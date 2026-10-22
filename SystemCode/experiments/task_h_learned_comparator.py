"""Task H - the learned comparator: gradient boosting on real visits, experiments only.

Trains on triage-time features (7 triage vitals, age, sex, the 200 chief-complaint
flags) and reports the rules' rival two ways, as the evaluation plan asks:
unweighted (accuracy-optimising) and class-balanced (a missed high-acuity case
weighted like a false alarm). Headline = under-triage of true ESI 1-2.
Visit-level 80/20 split (the public file has no patient id - disclosed).
Reads data/yale_ed_visits.parquet (data/convert-yale.py). ~3-6 min on CPU.
    python3 experiments/task_h_learned_comparator.py
"""
import json, os, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (cohen_kappa_score, confusion_matrix, roc_auc_score,
                             precision_recall_fscore_support)
from sklearn.inspection import permutation_importance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PQ = os.path.join(ROOT, "data", "yale_ed_visits.parquet")
OUT = os.path.join(ROOT, "experiments", "out", "task-h-learned-comparator")
SEED = 42
t0 = time.time()

cols = pd.read_parquet(PQ, columns=None).columns if False else None
import pyarrow.parquet as pq
schema = pq.read_schema(PQ).names
cc = [c for c in schema if c.startswith("cc_")]
vit = ["triage_vital_hr", "triage_vital_sbp", "triage_vital_dbp", "triage_vital_rr",
       "triage_vital_o2", "triage_vital_temp"]
df = pd.read_parquet(PQ, columns=["esi", "age", "gender", "arrivalmode", "disposition"] + vit + cc)
df = df[df["esi"].notna()].copy()
df["esi"] = df["esi"].astype(int)
print(f"rows with ESI: {len(df)}  ({time.time()-t0:.0f}s)")

X = pd.DataFrame(index=df.index)
for v in vit: X[v] = df[v].astype("float32")
X["age"] = pd.to_numeric(df["age"], errors="coerce").astype("float32")
X["male"] = (df["gender"] == "Male").astype("float32")
for c in cc: X[c] = df[c].astype("float32")
X_amb = X.copy(); X_amb["ambulance"] = df["arrivalmode"].astype(str).str.lower().eq("ambulance").astype("float32")
y_multi = df["esi"].values
y_bin = (df["esi"] <= 2).astype(int).values
admit = df["disposition"].eq("Admit").values

idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=SEED, stratify=y_multi)
print(f"split: train {len(idx_tr)}  test {len(idx_te)}")

def fit(Xm, y, balanced):
    clf = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.08, max_leaf_nodes=63,
                                         early_stopping=True, validation_fraction=0.1,
                                         class_weight="balanced" if balanced else None, random_state=SEED)
    clf.fit(Xm.iloc[idx_tr], y[idx_tr]); return clf

def binary_report(clf, Xm, label):
    p = clf.predict(Xm.iloc[idx_te]); pr = clf.predict_proba(Xm.iloc[idx_te])[:, 1]; yt = y_bin[idx_te]
    tn, fp, fn, tp = confusion_matrix(yt, p, labels=[0, 1]).ravel()
    return {"model": label, "n_test": int(len(yt)), "high_acuity_prevalence": round(yt.mean(), 4),
            "sensitivity_high_acuity": round(tp / (tp + fn), 4), "under_triage_rate": round(fn / (tp + fn), 4),
            "specificity": round(tn / (tn + fp), 4), "ppv": round(tp / max(tp + fp, 1), 4),
            "alarm_rate": round(p.mean(), 4), "accuracy": round((tp + tn) / len(yt), 4),
            "auroc": round(roc_auc_score(yt, pr), 4),
            "admit_rate_among_missed_high_acuity": round(admit[idx_te][(yt == 1) & (p == 0)].mean(), 4),
            "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}}

def multi_report(clf, Xm, label):
    p = clf.predict(Xm.iloc[idx_te]); yt = y_multi[idx_te]
    prec, rec, f1, sup = precision_recall_fscore_support(yt, p, labels=[1, 2, 3, 4, 5], zero_division=0)
    cm = confusion_matrix(yt, p, labels=[1, 2, 3, 4, 5])
    true_hi = yt <= 2
    return {"model": label, "exact_accuracy": round((p == yt).mean(), 4),
            "within_one_level": round((np.abs(p - yt) <= 1).mean(), 4),
            "weighted_kappa_quadratic": round(cohen_kappa_score(yt, p, weights="quadratic"), 4),
            "under_triage_true_1_2_predicted_3_5": round(((p >= 3) & true_hi).sum() / true_hi.sum(), 4),
            "per_class": {str(k): {"precision": round(float(a), 4), "recall": round(float(b), 4),
                                   "f1": round(float(c), 4), "support": int(d)}
                          for k, a, b, c, d in zip([1, 2, 3, 4, 5], prec, rec, f1, sup)},
            "confusion_rows_true_cols_pred": cm.tolist()}

results = {"n_rows": int(len(df)), "seed": SEED, "split": "visit-level 80/20 stratified (no patient id in the public file)",
           "features": {"base": "6 triage vitals + age + sex + 200 cc_* flags", "with_ambulance": "base + arrival-by-ambulance"},
           "binary": [], "multiclass": []}
models = {}
for feats, Xm in (("base", X), ("with_ambulance", X_amb)):
    for balanced in (False, True):
        label = f"{feats} / {'class-balanced' if balanced else 'unweighted'}"
        clf = fit(Xm, y_bin, balanced); models[("bin", label)] = clf
        results["binary"].append(binary_report(clf, Xm, label)); print("binary done:", label, f"({time.time()-t0:.0f}s)")
for balanced in (False, True):
    label = f"base / {'class-balanced' if balanced else 'unweighted'}"
    clf = fit(X, y_multi, balanced); models[("multi", label)] = clf
    results["multiclass"].append(multi_report(clf, X, label)); print("multiclass done:", label, f"({time.time()-t0:.0f}s)")

# which features carry the binary base model (permutation importance on a 6k test sample)
clf = models[("bin", "base / class-balanced")]
sub = np.random.RandomState(SEED).choice(idx_te, 6000, replace=False)
pi = permutation_importance(clf, X.iloc[sub], y_bin[sub], n_repeats=3, random_state=SEED, scoring="roc_auc", n_jobs=-1)
order = np.argsort(pi.importances_mean)[::-1][:20]
results["top_features_binary_balanced"] = [{"feature": X.columns[i], "auroc_drop": round(float(pi.importances_mean[i]), 4)} for i in order]
print(f"importance done ({time.time()-t0:.0f}s)")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(results, open(OUT + ".json", "w"), indent=1)
L = ["# Task H - learned comparator (gradient boosting on Yale visits)", "",
     f"Rows with a recorded ESI: {results['n_rows']:,} - {results['split']} - seed {SEED}.",
     "Features: 6 triage vitals (NaN kept as missing), age, sex, 200 chief-complaint flags;",
     "a second variant adds arrival-by-ambulance (a practice proxy no criterion uses). Experiments only -",
     "this model never runs in the product; it is the rules' rival.", "",
     "## High acuity (ESI 1-2) vs not - the headline is under-triage", "",
     "| model | sensitivity (ESI 1-2 caught) | under-triage | specificity | PPV | alarm rate | accuracy | AUROC | admitted among missed |",
     "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
for r in results["binary"]:
    L.append(f"| {r['model']} | {r['sensitivity_high_acuity']:.1%} | **{r['under_triage_rate']:.1%}** | {r['specificity']:.1%} | {r['ppv']:.1%} | {r['alarm_rate']:.1%} | {r['accuracy']:.1%} | {r['auroc']:.3f} | {r['admit_rate_among_missed_high_acuity']:.1%} |")
L += ["", "Reading: the unweighted model optimises accuracy on a ~30/70 split and buys it by missing",
      "high-acuity visits; the class-balanced model trades false alarms for catches. The gap between the",
      "two rows is the accuracy-vs-safety finding; the 'admitted among missed' column is the outcome check",
      "on the visits the model would have under-triaged.", "",
      "## Five-level ESI", "",
      "| model | exact | within one level | weighted kappa | under-triage (true 1-2 -> predicted 3-5) |",
      "| --- | ---: | ---: | ---: | ---: |"]
for r in results["multiclass"]:
    L.append(f"| {r['model']} | {r['exact_accuracy']:.1%} | {r['within_one_level']:.1%} | {r['weighted_kappa_quadratic']:.3f} | **{r['under_triage_true_1_2_predicted_3_5']:.1%}** |")
for r in results["multiclass"]:
    L += ["", f"Per class - {r['model']}:", "", "| ESI | precision | recall | F1 | n |", "| --- | ---: | ---: | ---: | ---: |"]
    L += [f"| {k} | {v['precision']:.2f} | {v['recall']:.2f} | {v['f1']:.2f} | {v['support']:,} |" for k, v in r["per_class"].items()]
L += ["", "## What the model leans on (permutation importance, class-balanced binary, 6,000 test visits)", "",
      "| feature | AUROC drop when shuffled |", "| --- | ---: |"]
L += [f"| {f['feature']} | {f['auroc_drop']:.4f} |" for f in results["top_features_binary_balanced"]]
L += ["", "## Limitations", "",
      "- The label is the recorded nurse ESI - practice, not truth; the model learns practice including its errors.",
      "- Visit-level split: repeat visitors can appear on both sides (no patient id); a patient-level split needs MIMIC.",
      "- Chief-complaint flags are reasons for visit, not findings (data/yale-schema.md); rare dangerous",
      "  presentations are exactly where an accuracy-optimising model is blind - see the under-triage column.",
      "- Vitals missing for many of the sickest visits are kept as missing, which the model can exploit as a signal;",
      "  that is a practice artefact, not physiology.", ""]
open(OUT + ".md", "w").write("\n".join(L))
print(f"wrote {OUT}.md ({time.time()-t0:.0f}s)")
