"""Train the practice-signal model (the report's learned second lane) on pre-arrival
features only - the vocabulary in prototype/practice_signal.py, built from Yale columns
here and from interview facts at run time. Class-balanced gradient boosting, high acuity
(ESI 1-2) vs not, visit-level 80/20 split. Writes the model + metadata for the app and a
report for the write-up.
    python3 experiments/practice_signal_train.py        (~1-2 min on CPU)
"""
import json, os, sys, time
import numpy as np, pandas as pd, joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, confusion_matrix, brier_score_loss

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import practice_signal as ps   # noqa: E402

PQ = os.path.join(ROOT, "data", "yale_ed_visits.parquet")
OUT = os.path.join(ROOT, "experiments", "out", "practice-signal")
SEED = 42; t0 = time.time()

import pyarrow.parquet as pq
names = pq.read_schema(PQ).names
need = ["esi", "age", "meds_anticoagulants", "meds_immunosuppressants", "meds_antineoplastics"] + [c for c in names if c.startswith("cc_")]
df = pd.read_parquet(PQ, columns=need)
df = df[df["esi"].notna()].copy(); df["esi"] = pd.to_numeric(df["esi"], errors="coerce").astype(int)
X = ps.yale_frame(df); y = (df["esi"] <= 2).astype(int).values
print(f"rows {len(df)}  features {len(ps.FEATURES)}  ({time.time()-t0:.0f}s)")

idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=SEED, stratify=df["esi"].values)
clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, max_leaf_nodes=31, early_stopping=True,
                                     validation_fraction=0.1, random_state=SEED)   # unweighted: probabilities stay calibrated shares
clf.fit(X.iloc[idx_tr], y[idx_tr])
pr = clf.predict_proba(X.iloc[idx_te])[:, 1]; yt = y[idx_te]
auroc = roc_auc_score(yt, pr); prev = float(yt.mean()); brier = brier_score_loss(yt, pr)
band_high, band_low = 0.5, 0.2
p_hi = clf.predict_proba(X.iloc[idx_te])[:, 1] >= band_high
tn, fp, fn, tp = confusion_matrix(yt, p_hi, labels=[0, 1]).ravel()
# calibration by decile: does "an estimated 60% were ESI 1-2" mean 60%?
dec = pd.qcut(pr, 10, labels=False, duplicates="drop")
calib = pd.DataFrame({"p": pr, "y": yt, "d": dec}).groupby("d").agg(pred=("p", "mean"), actual=("y", "mean"), n=("y", "size")).reset_index(drop=True)
# what each coarse complaint group looks like on its own (sanity for the wording)
per_group = {}
for g in ps.GROUPS:
    m = X[f"cx_{g}"].values == 1
    if m.sum(): per_group[g] = {"n": int(m.sum()), "esi12_share": round(float(y[m].mean()), 3)}
print(f"AUROC {auroc:.3f}  prevalence {prev:.3f}  brier {brier:.3f}  ({time.time()-t0:.0f}s)")

os.makedirs(os.path.join(ROOT, "prototype", "models"), exist_ok=True)
meta = {"trained_at": time.strftime("%Y-%m-%d"), "seed": SEED, "n_train": int(len(idx_tr)), "n_test": int(len(idx_te)),
        "features": ps.FEATURES, "prevalence": round(prev, 4), "auroc": round(float(auroc), 4), "brier": round(float(brier), 4),
        "band_high": band_high, "band_low": band_low,
        "band_high_share_of_visits": round(float(p_hi.mean()), 4), "band_high_precision": round(tp / max(tp + fp, 1), 4),
        "sensitivity_at_high_band": round(tp / max(tp + fn, 1), 4),
        "data": "Yale ED visits 2014-2017 (Hong et al. 2018), one US health system, recorded nurse ESI as label",
        "model": "HistGradientBoostingClassifier, unweighted (calibrated shares), pre-arrival features only"}
joblib.dump(clf, ps.MODEL); json.dump(meta, open(ps.META, "w"), indent=1)
res = dict(meta, calibration=calib.round(3).to_dict("records"), per_group=per_group)
os.makedirs(os.path.dirname(OUT), exist_ok=True); json.dump(res, open(OUT + ".json", "w"), indent=1)
L = ["# Practice signal - the learned lane on the report (pre-arrival features only)", "",
     f"Trained {meta['trained_at']} on {meta['n_train']:,} Yale visits, tested on {meta['n_test']:,} (visit-level split, seed {SEED}).",
     f"Label: recorded nurse ESI 1-2 vs 3-5 (prevalence {prev:.1%}). Features ({len(ps.FEATURES)}): age, the interview's coarse complaint",
     "groups (multi-hot; built from the Yale `cc_*` flags with the mapping in `prototype/practice_signal.py`), injury mechanism,",
     "fever, anticoagulation (`meds_anticoagulants`), immune status (`meds_immunosuppressants` / `meds_antineoplastics` /",
     "`cc_feverimmunocompromised`). No vitals, no labs - the report is produced before anyone examines the patient.", "",
     "This lane is **advisory**: it describes how similar past visits were triaged at one site; it never moves the ESI floor.",
     "The task H comparator (with vitals) is the data ceiling, not the rules' rival: a fair comparison needs equal inputs, so the rules are compared with this pre-arrival model (see docs/evaluation-plan.md, number 5).", "",
     "## Discrimination and calibration", "",
     f"- AUROC **{auroc:.3f}** (with vitals, task H reaches ~0.85 - the gap is what arrival vitals add)",
     f"- Brier score {brier:.3f}; the report quotes the model's probability as 'an estimated N% were ESI 1-2', so calibration matters:", "",
     "| decile | predicted share | actual share | n |", "| --- | ---: | ---: | ---: |"]
L += [f"| {i+1} | {r['pred']:.1%} | {r['actual']:.1%} | {int(r['n']):,} |" for i, r in enumerate(calib.to_dict('records'))]
L += ["", f"## Bands used on the report (high ≥ {band_high:.0%}, low ≤ {band_low:.0%})", "",
      f"- 'usually high acuity' band covers {meta['band_high_share_of_visits']:.1%} of test visits; {meta['band_high_precision']:.1%} of those were ESI 1-2;",
      f"  it catches {meta['sensitivity_at_high_band']:.1%} of all ESI 1-2 visits - most high-acuity visits are NOT in the band pre-arrival,",
      "  which is exactly why the lane can only corroborate, never reassure.", "",
      "## Each complaint group on its own (share of visits recorded ESI 1-2)", "",
      "| interview group | n visits | ESI 1-2 share |", "| --- | ---: | ---: |"]
L += [f"| {g} | {v['n']:,} | {v['esi12_share']:.1%} |" for g, v in sorted(per_group.items(), key=lambda kv: -kv[1]['esi12_share'])]
L += ["", "## Limitations", "",
      "- The label is practice (nurse ESI at one US site, 2014-2017), including its errors and local habits; not truth.",
      "- The interview's complaint groups are coarse; the model sees 'chest pain', not 'chest pain radiating to the jaw'.",
      "- Immune status and anticoagulation are proxied from medication classes on the Yale side and from caregiver answers on ours.",
      "- Visit-level split (no patient id); a patient-level check needs MIMIC-IV-ED.", ""]
open(OUT + ".md", "w").write("\n".join(L))
print(f"wrote {ps.MODEL} ({os.path.getsize(ps.MODEL)//1024} KB), {OUT}.md  ({time.time()-t0:.0f}s)")
