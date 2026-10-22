"""Demo: learned-tree vs authored-rulebook structural comparison (design record,
evaluation layer: ML comparator). Trains a shallow decision tree on the Yale ED
dataset to predict HIGH ACUITY (nurse ESI 1-2 vs 3-5 — the floor's actual job),
unrolls every high-acuity leaf into a conjunctive rule, and lines those up against
the thresholds in rules/criteria.yaml in three buckets:

  MATCHED       tree splits on a feature the rulebook also uses (thresholds side by side)
  TREE-ONLY     data-driven splits with no rulebook counterpart (discovery candidates -
                need the source-first treatment before they could ever become rules)
  RULEBOOK-ONLY criteria the tree never grew (rare events / fields absent from the data -
                expected, and the safety argument for the deterministic floor)

Run:  .venv/bin/python experiments/tree_vs_rules.py   (needs data/download-yale.sh first)
Output: printed summary + experiments/out/tree-vs-rules.md

Caveats (also stamped into the report): the label is the NURSE'S decision, not ground
truth; missing vitals are kept as NaN (sklearn handles them); this is a demo of the
comparison METHOD - the report-grade version adds patient-level splits, sensitivity
perturbations, and outcome arbitration.
"""
import os, json
import numpy as np
import pandas as pd
import pyreadr, yaml
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# dataset feature -> our fact-schema field (the bridge between the two vocabularies)
FEATURE_TO_FIELD = {
    "age": "patient.age",
    "triage_vital_o2": "vitals.spo2",
    "triage_vital_hr": "vitals.heart_rate",
    "triage_vital_rr": "vitals.respiratory_rate",
    "triage_vital_temp": "vitals.temp",
    "cc_fall": "E.mechanism=fall",
    "cc_fall>65": "E.mechanism=fall",
    "cc_headinjury": "E.head_strike",
    "cc_assaultvictim": "E.mechanism=assault",
    "cc_motorvehiclecrash": "E.mechanism=road_accident",
    "cc_chestpain": "complaint.category=chest_pain",
    "cc_abdominalpain": "complaint.category=abdominal_pain",
    "cc_abdominalpainpregnant": "B-17 combo (abdo pain + pregnant)",
    "cc_feverimmunocompromised": "B-07 combo (fever + immunocompromised)",
    "meds_anticoagulants": "M.anticoagulant",
    "meds_immunosuppressants": "M.immunosuppressant_or_steroid",
}
# candidate features; the vitals ESI's danger zone actually uses, plus mechanism/context
CANDIDATES = list(FEATURE_TO_FIELD) + [
    "triage_vital_sbp", "triage_vital_dbp",   # NOT in ESI's adult danger-zone table -> tree-only if used
    "gender", "arrivalmode",
]

def load():
    df = next(iter(pyreadr.read_r(os.path.join(ROOT, "data", "yale_ed_visits.rdata")).values()))
    esi = pd.to_numeric(df["esi"], errors="coerce")
    keep = esi.notna()
    df, esi = df[keep], esi[keep]
    y = (esi <= 2).astype(int)                # high acuity = ESI 1-2
    global n_cols_total; n_cols_total = df.shape[1]
    feats = [c for c in CANDIDATES if c in df.columns]
    X = pd.DataFrame(index=df.index)
    for c in feats:
        if c == "gender":
            X["male"] = (df[c] == "Male").astype(float)
        elif c == "arrivalmode":
            X["ambulance"] = df[c].astype(str).str.lower().eq("ambulance").astype(float)
        else:
            X[c] = pd.to_numeric(df[c], errors="coerce")
    return X, y

def unroll(tree, names):
    """Every root->leaf path as a list of (feature, '<=' or '>', threshold)."""
    t = tree.tree_
    paths = []
    def walk(node, conds):
        if t.children_left[node] == -1:
            n = int(t.n_node_samples[node]); neg, pos = t.value[node][0] * t.n_node_samples[node]
            paths.append({"conds": conds, "n": n, "p_high": float(pos / max(n, 1)),
                          "pred_high": bool(pos >= neg)})
            return
        f, thr = names[t.feature[node]], float(t.threshold[node])
        walk(t.children_left[node],  conds + [(f, "<=", thr)])
        walk(t.children_right[node], conds + [(f, ">", thr)])
    walk(0, [])
    return paths

def rulebook_conditions():
    """(rule id, field, op, value) leaves from criteria.yaml."""
    crit = yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml")))
    out = []
    def leaves(c):
        if not isinstance(c, dict): return
        if "field" in c:
            for op in ("equals", "in", "lt", "gt", "gte", "lte"):
                if op in c: out.append((rid, c["field"], op, c[op]))
        for k in ("all", "any"):
            for s in c.get(k, []): leaves(s)
    for r in crit:
        if r.get("when"):
            rid = r["id"]
            leaves(r["when"])
    return out

def main():
    X, y = load()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)
    clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=500,
                                 class_weight="balanced", random_state=7).fit(Xtr, ytr)
    pred = clf.predict(Xte)
    sens = ((pred == 1) & (yte == 1)).sum() / (yte == 1).sum()   # high-acuity recall
    alarm = (pred == 1).mean()
    under = ((pred == 0) & (yte == 1)).sum() / (yte == 1).sum()  # missed true 1-2s

    paths = [p for p in unroll(clf, list(X.columns)) if p["pred_high"]]
    paths.sort(key=lambda p: -p["n"] * p["p_high"])

    used = {c[0] for p in paths for c in p["conds"]}
    rb = rulebook_conditions()
    rb_fields = {f for _, f, _, _ in rb}
    inv = {}
    for feat, field in FEATURE_TO_FIELD.items():
        inv.setdefault(feat, field)

    matched, tree_only = [], []
    for feat in sorted(used):
        field = inv.get(feat) or {"male": None, "ambulance": None}.get(feat)
        base, _, want = (field or "").partition("=")
        def rel(f, op, v):
            if not base or not f.startswith(base): return False
            if not want: return True
            if op == "equals": return v == want
            if op == "in": return want in v
            return True
        hits = [(rid, f, op, v) for rid, f, op, v in rb if rel(f, op, v)]
        (matched if hits else tree_only).append((feat, field, hits))
    mappable_fields = {v.split("=")[0] for v in FEATURE_TO_FIELD.values()}
    rulebook_only = sorted({rid for rid, f, _, _ in rb
                            if not any(f.startswith(m) for m in mappable_fields)})

    L = []
    L.append("# Learned tree vs authored rulebook - structural comparison (demo)\n")
    L.append(f"Yale rows used: {len(X):,} · target: nurse ESI 1-2 vs 3-5 · "
             f"tree: depth<=4, min_leaf=500, class-balanced\n")
    L.append(f"Test-set: high-acuity sensitivity {sens:.1%} · under-triage (missed true 1-2) "
             f"{under:.1%} · alarm rate {alarm:.1%}\n")
    L.append(f"\n## Feature pool offered to the tree ({len(X.columns)} of {n_cols_total:,} columns) - CURATED, disclosed\n")
    L.append("The candidate pool was hand-picked, not the full dataset: mapped clinical fields "
             "(so MATCHED has something to match on) plus a few triage-time features that no "
             "standard uses (arrival mode, sex, BP) so TREE-ONLY could exist. Consequence: the "
             "tree's *ranking* among these is data-driven, but the *pool* carries the analyst's "
             "presumptions - TREE-ONLY here means \"data-discovered strength among presumption-"
             "selected candidates\", not open discovery. Report-grade version: offer ALL "
             "columns (or all cc_/vitals/meds/history) and let the tree choose; only then is a "
             "TREE-ONLY entry a finding rather than a planted candidate.\n")
    L.append("| feature | source column | rulebook allowed to use it? |")
    L.append("| --- | --- | --- |")
    for feat in X.columns:
        src = {"male": "gender", "ambulance": "arrivalmode"}.get(feat, feat)
        field = FEATURE_TO_FIELD.get(feat)
        SPECIAL = {"triage_vital_sbp": "partly - hypotension is A-10 (with hypoperfusion), not in the D danger-zone table; not mapped in this demo",
                   "triage_vital_dbp": "no rulebook use",
                   "male": "NO - not a criterion in any triage standard",
                   "ambulance": "NO - not a criterion in any triage standard"}
        allowed = ("yes - maps to `%s`" % field) if field else SPECIAL.get(feat, "no rulebook use")
        L.append(f"| `{feat}` | `{src}` | {allowed} |")
    L.append("\n## High-acuity paths the tree learned (top 8, as conjunctive rules)\n")
    for p in paths[:8]:
        cond = " AND ".join(f"{f} {op} {thr:.6g}" for f, op, thr in p["conds"])
        L.append(f"- IF {cond}  →  high acuity   (n={p['n']:,}, precision {p['p_high']:.0%})")
    L.append("\n## MATCHED - features both sides use (tree threshold vs rulebook)\n")
    for feat, field, hits in matched:
        thrs = sorted({f"{op} {thr:.6g}" for p in paths for f2, op, thr in p["conds"] if f2 == feat})
        L.append(f"- `{feat}` ↔ `{field}` — tree splits: {', '.join(thrs)}")
        for rid, f, op, v in hits[:4]:
            L.append(f"    - rulebook {rid}: `{f} {op} {v}`")
    L.append("\n## TREE-ONLY - data splits with no rulebook counterpart (discovery candidates)\n")
    NOTES = {
        "ambulance": "derived from `arrivalmode` (1 if 'ambulance'). Root split of the tree; "
                     "~52% of ambulance arrivals are nurse ESI 1-2 vs ~19% for car/walk-in. "
                     "MUST NOT become a rule: it is a proxy for the dispatcher's/paramedics' prior "
                     "acuity judgment (laundering an upstream decision), partly a consequence of the "
                     "acuity we assess, and no triage scale uses arrival mode. Report as a practice "
                     "pattern; keep it in the ML rival (legitimately known at triage) - the rival "
                     "wins agreement partly by exploiting a proxy the rulebook is forbidden to use.",
        "male": "derived from `gender`. A bias axis, not a criterion: keep in the ML rival only "
                "with an explicit fairness analysis (does nurse acuity differ by sex conditional "
                "on presentation?), otherwise drop. Never a rule.",
    }
    for feat, _, _ in tree_only:
        L.append(f"- `{feat}` — {NOTES.get(feat, 'no criterion uses this; source-first check required before it could become a rule (or report as practice-pattern only)')}")
    L.append(f"\n## RULEBOOK-ONLY - {len(rulebook_only)} criteria the tree can never rediscover here\n")
    L.append("Fields absent from routine triage records (mechanism detail, LOC, responsiveness, "
             "confirmed-status gates) or events too rare for accuracy-driven splits:\n")
    L.append(", ".join(rulebook_only[:20]) + (" …" if len(rulebook_only) > 20 else ""))
    L.append("\n\n## Caveats\n")
    L.append("- Label = nurse decision (mimics practice, not truth); outcome arbitration is the "
             "follow-up experiment.\n- Demo method only: report-grade version needs patient-level "
             "split, threshold-sensitivity reruns, and the full column mapping table.\n- B-30 note: "
             "fall+anticoagulant is 0.2% of rows - watch whether any tree path pairs them (rare-event "
             "blindness is the expected result and the floor's justification).\n- Feature-selection "
             "leakage of the analyst's priors: a curated candidate pool bounds 'discoveries' to what "
             "the analyst already thought worth checking (same shape as synthetic-data circularity). "
             "Curation is acceptable for demonstrating the METHOD; the FINDING requires the open pool, "
             "with the curation disclosed - see the feature-pool table above.")
    report = "\n".join(L)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = os.path.join(HERE, "out", "tree-vs-rules.md")
    open(out, "w").write(report)
    print(report)
    print(f"\n[saved: {out}]")

if __name__ == "__main__":
    main()
