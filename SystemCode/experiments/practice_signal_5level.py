"""Five-level version of the practice signal, for one purpose: to show where the 17 pre-arrival
facts carry information and where they do not. Same features, same visit-level 80/20 split
(seed 42, stratified by level) as experiments/practice_signal_train.py; five classes instead of
two. Does not touch the model the app loads. Writes experiments/out/practice-signal-5level.{json,md}.
    .venv/bin/python experiments/practice_signal_5level.py     (a few minutes on CPU)
"""
import json, os, sys, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, cohen_kappa_score, roc_auc_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import practice_signal as ps   # noqa: E402
import pyarrow.parquet as pq

PQ = os.path.join(ROOT, "data", "yale_ed_visits.parquet")
OUT = os.path.join(ROOT, "experiments", "out", "practice-signal-5level")
SEED = 42; t0 = time.time()
names = pq.read_schema(PQ).names
need = ["esi", "age", "meds_anticoagulants", "meds_immunosuppressants", "meds_antineoplastics"] + [c for c in names if c.startswith("cc_")]
df = pd.read_parquet(PQ, columns=need)
df = df[df["esi"].notna()].copy(); df["esi"] = pd.to_numeric(df["esi"], errors="coerce").astype(int)
df = df[df["esi"].between(1, 5)]
X = ps.yale_frame(df); y = df["esi"].values
idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=SEED, stratify=y)
print(f"rows {len(df)}  features {len(ps.FEATURES)}  ({time.time()-t0:.0f}s)")

clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31, early_stopping=True,
                                     validation_fraction=0.1, random_state=SEED)
clf.fit(X.iloc[idx_tr], y[idx_tr])
P = clf.predict_proba(X.iloc[idx_te]); classes = list(clf.classes_); yt = y[idx_te]
pred = clf.predict(X.iloc[idx_te])
print(f"trained ({time.time()-t0:.0f}s)")

cm = confusion_matrix(yt, pred, labels=[1, 2, 3, 4, 5])
recall = [round(cm[i, i] / max(cm[i].sum(), 1), 3) for i in range(5)]
acc = float((pred == yt).mean()); majority = float(max(np.bincount(yt)) / len(yt))
kappa_q = cohen_kappa_score(yt, pred, weights="quadratic")
# where the facts carry information: one-vs-rest AUROC per level, and adjacent-pair AUROC
ovr = {int(c): round(float(roc_auc_score((yt == c).astype(int), P[:, classes.index(c)])), 3) for c in [1, 2, 3, 4, 5]}
adj = {}
for a, b in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    m = np.isin(yt, [a, b]); pa = P[m][:, classes.index(a)]; pb = P[m][:, classes.index(b)]
    adj[f"{a} vs {b}"] = round(float(roc_auc_score((yt[m] == a).astype(int), pa / (pa + pb))), 3)
# every two-way split of the scale, from the five-class probabilities summed up to the cut
cum = {}
for k in (1, 2, 3, 4):
    pk = P[:, [classes.index(c) for c in range(1, k + 1)]].sum(1); lab = (yt <= k).astype(int)
    cum[f"1-{k} vs {k+1}-5"] = {"auroc": round(float(roc_auc_score(lab, pk)), 3), "share_low_side": round(float(lab.mean()), 3)}
auroc_collapsed = cum["1-2 vs 3-5"]["auroc"]
under_triage = float(cm[:2, 2:].sum() / max(cm[:2].sum(), 1))   # classifier under-triage: true 1-2 predicted 3-5
print(f"acc {acc:.3f} (majority {majority:.3f})  kappa_q {kappa_q:.3f}  collapsed AUROC {auroc_collapsed:.3f}  ({time.time()-t0:.0f}s)")

res = {"trained_at": time.strftime("%Y-%m-%d"), "seed": SEED, "n_train": int(len(idx_tr)), "n_test": int(len(idx_te)),
       "features": ps.FEATURES, "confusion_rows_true_cols_pred": cm.tolist(), "per_class_recall": recall,
       "accuracy": round(acc, 4), "majority_class_share": round(majority, 4), "quadratic_weighted_kappa": round(float(kappa_q), 4),
       "one_vs_rest_auroc": ovr, "adjacent_pair_auroc": adj, "collapsed_1_2_vs_3_5_auroc": round(auroc_collapsed, 4), "cumulative_splits": cum,
       "classifier_under_triage_5level": round(under_triage, 4),
       "test_level_shares": {int(c): round(float((yt == c).mean()), 4) for c in [1, 2, 3, 4, 5]}}
json.dump(res, open(OUT + ".json", "w"), indent=1)
L = ["# Practice signal, five-level version (pre-arrival features only)", "",
     f"Same 17 features and the same split as the two-class practice signal (seed {SEED}, {len(idx_tr):,} train / {len(idx_te):,} test), trained on the recorded nurse level 1 to 5. Purpose: to show where the pre-arrival facts carry information. This model is not used by the app.", "",
     "## Confusion matrix on the test visits (recorded level on rows, predicted on columns)", "",
     "| true \\ predicted | 1 | 2 | 3 | 4 | 5 | recall |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
for i in range(5): L.append(f"| {i+1} | " + " | ".join(f"{cm[i, j]:,}" for j in range(5)) + f" | {recall[i]:.3f} |")
L += ["", f"- accuracy {acc:.3f}; predicting the commonest level for everyone would give {majority:.3f}",
      f"- quadratic weighted kappa {kappa_q:.3f}",
      f"- classifier under-triage (true 1-2 predicted 3-5) {under_triage:.3f}",
      "", "## Where the facts separate levels", "",
      "One-versus-rest AUROC per level (how well the model ranks that level against all others):", "",
      "| level | AUROC |", "| --- | ---: |"] + [f"| {k} | {v:.3f} |" for k, v in ovr.items()] + [
      "", "Adjacent-pair AUROC (only visits of the two levels, ranked by the model's relative probability):", "",
      "| pair | AUROC |", "| --- | ---: |"] + [f"| {k} | {v:.3f} |" for k, v in adj.items()] + [
      "", "Every two-way split of the scale (five-class probabilities summed up to the cut; a two-class model trained directly on each split gives the same figures to three decimals):", "",
      "| split | AUROC | share of visits on the low side |", "| --- | ---: | ---: |"] + [f"| {k} | {v['auroc']:.3f} | {v['share_low_side']:.3f} |" for k, v in cum.items()] + [
      "", f"The 1-2 versus 3-5 split, the one the report uses, is the weakest of the four at {auroc_collapsed:.3f}; the sharpest is 1-3 versus 4-5 at {cum['1-3 vs 4-5']['auroc']:.3f}. The report's split is chosen by the use (a floor is two-sided at the handbook's level-2 line) and not because the facts favour it.", "",
      "Reading: the facts carry a modest amount of order across the whole scale and do not single out the urgent line; as a level assigner the model is unsafe (see the matrix), so the report prints a two-sided share rather than a level."]
open(OUT + ".md", "w").write("\n".join(L) + "\n"); print("->", OUT + ".md")
