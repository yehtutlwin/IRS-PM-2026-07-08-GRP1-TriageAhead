"""Task G - rulebook vs practice on the WHOLE Yale dataset, two arms, per docs/task-g-guide.md.

Reads data/yale_ed_visits.parquet, maps raw columns to engine facts through the
documented table below (every line names its source columns and provenance tier;
see data/yale-schema.md - chief-complaint labels are reasons for visit, never
findings, so judgment fields like acs_suspicion are NOT mapped), runs the
deterministic engine over every visit in two information states:
  arm 1  history/complaint only   - the product's en-route floor
  arm 2  + triage vitals          - the at-arrival state; exercises A-08/A-10/A-12/D-01
and reports agreement / overshoot / reach / silent-miss with their own denominators.
Rows are grouped by identical mapped facts, so the engine runs once per signature.
    python3 experiments/task_g_full.py
"""
import json, os, sys, time
from collections import Counter, defaultdict
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import engine  # noqa: E402

PQ = os.path.join(ROOT, "data", "yale_ed_visits.parquet")
OUT = os.path.join(ROOT, "experiments", "out", "task-g-full")
t0 = time.time()

# ---------------- the mapping table (tier: direct | derived) ----------------
CC_TO_CATEGORY = {   # cc_* label -> complaint.category (enum of the interview schema)
    "cc_chestpain": "chest_pain", "cc_abdominalpain": "abdominal_pain", "cc_abdominalpainpregnant": "abdominal_pain",
    "cc_fall": "injury", "cc_fall>65": "injury", "cc_fever": "fever", "cc_feverimmunocompromised": "fever",
    "cc_sorethroat": "sore_throat", "cc_dizziness": "dizziness", "cc_epistaxis": "nosebleed",
    "cc_shortnessofbreath": "breathing", "cc_breathingdifficulty": "breathing", "cc_dyspnea": "breathing",
    "cc_strokealert": "neuro_symptoms", "cc_motorvehiclecrash": "injury", "cc_assaultvictim": "injury",
}
MECHANISM = {"cc_fall": "fall", "cc_fall>65": "fall", "cc_motorvehiclecrash": "road_accident", "cc_assaultvictim": "assault"}
FLAG_FACTS = {   # cc_* label -> a positive fact the label directly states (derived tier)
    "cc_strokealert": ("complaint.stroke_signs", True),
    "cc_suicidal": ("complaint.danger_to_self_or_others", True),
    "cc_vaginalbleeding": ("complaint.vaginal_bleeding", True),
    "cc_overdose-intentional": ("complaint.known_toxic_ingestion", True),
    "cc_overdose-accidental": ("complaint.known_toxic_ingestion", True),
    "cc_abdominalpainpregnant": ("history.pregnant", True),
    "cc_fever": ("complaint.fever", True), "cc_feverimmunocompromised": ("complaint.fever", True),
}
NOT_MAPPED = {   # deliberately unmapped, with the reason (goes in the report)
    "complaint.acs_suspicion": "judgment field - cc_chestpain does not establish ACS features",
    "obs.*": "eyes-on findings - no examination columns in Yale (cc_unresponsive is a reason for visit)",
    "complaint.pain_rating": "no pain score column",
    "E.head_strike / E.loc / fall height": "not recorded",
}
VITALS = ["triage_vital_hr", "triage_vital_sbp", "triage_vital_rr", "triage_vital_o2", "triage_vital_temp"]
NEED = ["esi", "age", "disposition", "meds_anticoagulants", "meds_immunosuppressants", "hivinfectn", "maintchemr",
        "coaghemrdx"] + VITALS + sorted(set(list(CC_TO_CATEGORY) + list(MECHANISM) + list(FLAG_FACTS)))

def facts_for(row, with_vitals):
    f = {}
    cats = []
    for c, cat in CC_TO_CATEGORY.items():
        if row[c] == 1 and cat not in cats: cats.append(cat)
    if cats: f["complaint.category"] = tuple(cats)
    for c, mech in MECHANISM.items():
        if row[c] == 1: f["E.mechanism"] = mech; break
    for c, (field, val) in FLAG_FACTS.items():
        if row[c] == 1: f[field] = val
    if row["meds_anticoagulants"] >= 1: f["M.anticoagulant"] = ("confirmed", True)   # EHR active list -> confirmed (tier 2)
    if row["meds_immunosuppressants"] >= 1: f["M.immunosuppressant_or_steroid"] = True
    if row["cc_feverimmunocompromised"] == 1 or row["hivinfectn"] == 1 or row["maintchemr"] == 1:
        f["history.immunocompromised"] = True
    if row["coaghemrdx"] == 1: f["history.thrombocytopenia_or_clotting_disorder"] = True
    if pd.notna(row["age"]): f["patient.age"] = int(row["age"])
    if with_vitals:
        hr, sbp, rr, o2, temp = (row[v] for v in VITALS)
        if pd.notna(hr): f["vitals.heart_rate"] = float(hr); f["vitals.extreme_heart_rate"] = bool(hr > 150 or hr < 40)   # documented thresholds (tier 2)
        if pd.notna(rr): f["vitals.respiratory_rate"] = float(rr)
        if pd.notna(o2): f["vitals.spo2"] = float(o2)
        if pd.notna(sbp): f["vitals.hypotension"] = bool(sbp < 90)   # documented threshold (tier 2)
        if pd.notna(temp): f["vitals.temp_c"] = round((float(temp) - 32) * 5 / 9, 1) if temp > 50 else float(temp)
    return f

def to_facts(sig):
    F = engine.Facts()
    for k, v in sig:
        if k == "complaint.category":
            for cat in v: F.write_complaint(cat, who="dataset")
        elif k == "M.anticoagulant":
            F.write(k, v[1], status=v[0], who="dataset")
        else:
            F.write(k, v, status="reported", who="dataset")
    return F

CRIT = engine.load_criteria()
D_RULES = [c for c in CRIT if "when" in c and c.get("decision_point") == "D"]

def leaf_fields(cond, acc):
    if not isinstance(cond, dict): return acc
    if "field" in cond: acc.append(cond["field"].replace(".value", "").replace(".status", ""))
    for k in ("all", "any"):
        for c in cond.get(k, []): leaf_fields(c, acc)
    return acc
def inputs_present(cond, F):
    if not isinstance(cond, dict): return False
    if "all" in cond: return all(inputs_present(c, F) for c in cond["all"])
    if "any" in cond: return any(inputs_present(c, F) for c in cond["any"])
    return F.has(cond["field"].replace(".value", "").replace(".status", ""))
AB_RULES = [c for c in CRIT if "when" in c and c.get("decision_point") in ("A", "B")]

def evaluate(sig):
    F = to_facts(sig)
    tree = engine.evaluate_tree(F, CRIT)
    d_fired = [c["id"] for c in D_RULES if engine.holds(c["when"], F)]
    evaluable = [c["id"] for c in AB_RULES if inputs_present(c["when"], F)]
    return {"floor": tree["floor"], "fired": [r["id"] for r in tree["fired"]], "esi1": [r["id"] for r in tree["esi1_indicators"]],
            "consider": [r["id"] for r in tree["consider"]], "d": d_fired, "evaluable": evaluable}

def main():
    df = pd.read_parquet(PQ, columns=NEED)
    n_all = len(df)
    df = df[df["esi"].notna()].copy(); df["esi"] = df["esi"].astype(int)
    print(f"{n_all:,} rows, {len(df):,} with ESI ({time.time()-t0:.0f}s)")
    report = {"n_rows": int(n_all), "n_with_esi": int(len(df)), "arms": {}}
    rows_by_arm = {}
    for arm, with_vitals in (("history_only", False), ("with_vitals", True)):
        sigs = df.apply(lambda r: tuple(sorted(facts_for(r, with_vitals).items())), axis=1)
        uniq = sigs.unique()
        print(f"arm {arm}: {len(uniq):,} unique fact signatures ({time.time()-t0:.0f}s)")
        ev = {s: evaluate(s) for s in uniq}
        print(f"arm {arm}: evaluated ({time.time()-t0:.0f}s)")
        r = pd.DataFrame({"esi": df["esi"].values, "admit": df["disposition"].eq("Admit").values,
                          "sig": sigs.values})
        r["floor"] = r["sig"].map(lambda s: ev[s]["floor"]); r["esi1"] = r["sig"].map(lambda s: bool(ev[s]["esi1"]))
        r["claim"] = r["floor"].notna() | r["esi1"]
        r["fired"] = r["sig"].map(lambda s: tuple(ev[s]["fired"] + ev[s]["esi1"])); r["d"] = r["sig"].map(lambda s: tuple(ev[s]["d"]))
        r["n_eval"] = r["sig"].map(lambda s: len(ev[s]["evaluable"]))
        r["cats"] = r["sig"].map(lambda s: next((v for k, v in s if k == "complaint.category"), ()))
        hi = r["esi"] <= 2
        claim = r["claim"]
        consistent = claim & hi
        overshoot = r["floor"].notna() & ~hi
        silent = ~claim & hi & (r["n_eval"] > 0)
        A = {"rows": int(len(r)), "claims_made": int(claim.sum()), "reach_pct": round(claim.mean() * 100, 2),
             "consistent_with_recorded_1_2": int(consistent.sum()), "consistent_pct_of_claims": round(consistent.sum() / max(claim.sum(), 1) * 100, 1),
             "overshoot_floor_vs_recorded_3_5": int(overshoot.sum()), "overshoot_pct_of_floors": round(overshoot.sum() / max(r["floor"].notna().sum(), 1) * 100, 1),
             "overshoot_admit_rate": round(r.loc[overshoot, "admit"].mean() * 100, 1) if overshoot.any() else None,
             "control_admit_rate_recorded_3_5_no_claim": round(r.loc[~claim & ~hi, "admit"].mean() * 100, 1),
             "recorded_1_2_total": int(hi.sum()), "recorded_1_2_caught": int(consistent.sum()),
             "silent_miss": int(silent.sum()), "silent_miss_pct_of_recorded_1_2": round(silent.sum() / hi.sum() * 100, 1),
             "rows_with_no_evaluable_rule": int((r["n_eval"] == 0).sum()),
             "unique_signatures": int(len(uniq)),
             "d_reconsider_rows": int((r["d"].map(len) > 0).sum())}
        # per rule: fires, recorded-ESI distribution, admit rate, overshoot share
        per_rule = {}
        for rid in sorted({x for t in r["fired"] for x in t} | {x for t in r["d"] for x in t}):
            m = r["fired"].map(lambda t: rid in t) | r["d"].map(lambda t: rid in t)
            dist = r.loc[m, "esi"].value_counts().sort_index()
            per_rule[rid] = {"fires": int(m.sum()), "recorded_esi": {int(k): int(v) for k, v in dist.items()},
                             "below_floor_pct": round((r.loc[m, "esi"] >= 3).mean() * 100, 1),
                             "admit_rate": round(r.loc[m, "admit"].mean() * 100, 1)}
        A["per_rule"] = per_rule
        # coverage by presenting complaint family
        fam = r["cats"].map(lambda c: c[0] if c else "(no mapped complaint)")
        cov = r.groupby(fam).agg(rows=("esi", "size"), claims=("claim", "sum"), rec_1_2=("esi", lambda s: int((s <= 2).sum())))
        cov["claim_pct"] = (cov["claims"] / cov["rows"] * 100).round(1)
        A["coverage_by_presenting_complaint"] = {k: {kk: int(vv) if kk != "claim_pct" else float(vv) for kk, vv in v.items()} for k, v in cov.sort_values("rows", ascending=False).iterrows()}
        report["arms"][arm] = A
        rows_by_arm[arm] = r
        print(f"arm {arm}: metrics done ({time.time()-t0:.0f}s)")

    # the delta between arms - the nurse-vitals-entry decision gate
    h, v = rows_by_arm["history_only"], rows_by_arm["with_vitals"]
    newly = (~h["claim"]) & v["claim"]
    report["delta"] = {"rows_newly_claimed_with_vitals": int(newly.sum()),
                       "of_which_recorded_1_2": int((newly & (v["esi"] <= 2)).sum()),
                       "of_which_recorded_3_5": int((newly & (v["esi"] >= 3)).sum()),
                       "d_reconsider_rows": int((v["d"].map(len) > 0).sum()),
                       "d_reconsider_recorded_esi": {int(k): int(c) for k, c in v.loc[v["d"].map(len) > 0, "esi"].value_counts().sort_index().items()}}
    report["not_mapped"] = NOT_MAPPED
    report["mapping"] = {"cc_to_category": CC_TO_CATEGORY, "mechanism": MECHANISM, "flag_facts": {k: list(v) for k, v in FLAG_FACTS.items()},
                         "other": ["meds_anticoagulants>=1 -> M.anticoagulant confirmed", "meds_immunosuppressants>=1 -> M.immunosuppressant_or_steroid",
                                   "cc_feverimmunocompromised|hivinfectn|maintchemr -> history.immunocompromised", "coaghemrdx -> history.thrombocytopenia_or_clotting_disorder",
                                   "age -> patient.age", "arm 2: hr/rr/o2/sbp/temp -> vitals.*; extreme HR = >150 or <40; hypotension = SBP<90 (documented assumptions)"]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(report, open(OUT + ".json", "w"), indent=1)

    L = ["# Task G - rulebook vs practice on the whole Yale dataset (two arms)", "",
         f"{report['n_rows']:,} visits, {report['n_with_esi']:,} with a recorded ESI. Engine: rules/criteria.yaml as committed;",
         "mapping table and deliberately unmapped fields listed at the end. The recorded ESI is a comparator,",
         "not truth (data/yale-schema.md); a floor is a lower-bound claim, so 'consistent' means the floor did not",
         "exceed the recorded level. Denominators per docs/task-g-guide.md section 5.", ""]
    for arm, A in report["arms"].items():
        L += [f"## Arm: {arm.replace('_', ' ')}", "",
              f"- Claims made (floor or ESI-1 indicator): **{A['claims_made']:,}** of {A['rows']:,} rows = reach **{A['reach_pct']}%** ({A['unique_signatures']:,} unique fact signatures)",
              f"- Consistent with recorded ESI 1-2: **{A['consistent_pct_of_claims']}%** of claims ({A['consistent_with_recorded_1_2']:,})",
              f"- Overshoot (floor claimed, recorded ESI 3-5): **{A['overshoot_floor_vs_recorded_3_5']:,}** = {A['overshoot_pct_of_floors']}% of floors; those visits were admitted at **{A['overshoot_admit_rate']}%** vs {A['control_admit_rate_recorded_3_5_no_claim']}% for recorded-3-5 visits with no claim",
              f"- Recorded ESI 1-2 caught by a claim: {A['recorded_1_2_caught']:,} of {A['recorded_1_2_total']:,}; silent misses (recorded 1-2, no claim, at least one rule evaluable): **{A['silent_miss']:,}** ({A['silent_miss_pct_of_recorded_1_2']}% of recorded 1-2)",
              f"- Rows where no rule had its inputs at all: {A['rows_with_no_evaluable_rule']:,}", "",
              "| rule | fires | recorded ESI 1 / 2 / 3 / 4 / 5 | below floor | admitted |", "| --- | ---: | --- | ---: | ---: |"]
        for rid, p in sorted(A["per_rule"].items(), key=lambda x: -x[1]["fires"]):
            d = p["recorded_esi"]; L.append(f"| {rid} | {p['fires']:,} | {' / '.join(str(d.get(k, 0)) for k in (1,2,3,4,5))} | {p['below_floor_pct']}% | {p['admit_rate']}% |")
        L += ["", "Coverage by presenting complaint (top 15):", "", "| complaint | rows | claims | claim % | recorded 1-2 |", "| --- | ---: | ---: | ---: | ---: |"]
        for k, c in list(A["coverage_by_presenting_complaint"].items())[:15]:
            L.append(f"| {k} | {c['rows']:,} | {c['claims']:,} | {c['claim_pct']}% | {c['rec_1_2']:,} |")
        L.append("")
    dl = report["delta"]
    L += ["## Delta between arms - the nurse-vitals-entry decision gate", "",
          f"- Rows that gain a claim only when vitals are known: **{dl['rows_newly_claimed_with_vitals']:,}** ({dl['of_which_recorded_1_2']:,} recorded ESI 1-2, {dl['of_which_recorded_3_5']:,} recorded 3-5)",
          f"- DP-D 'reconsider up-triage' fires on {dl['d_reconsider_rows']:,} rows; their recorded ESI: {dl['d_reconsider_recorded_esi']} (D is a modifier on the 3/4/5 side, reported separately from the floor)", "",
          "## Mapping table (source columns -> facts)", "", "```json", json.dumps(report["mapping"], indent=1), "```", "",
          "Deliberately not mapped:", ""] + [f"- `{k}`: {v}" for k, v in NOT_MAPPED.items()] + ["",
          "## How to read the disagreements", "",
          "Every overshoot or silent miss belongs to one of: nurse deviated from the standard / standard silent /",
          "data lacks the deciding detail / mapping error. This run cannot attribute automatically; the per-rule",
          "tables above are the starting point (a rule whose fires sit mostly at recorded 3-5 with a LOW admit rate",
          "points at a mapping or standard problem; a HIGH admit rate points at practice under-triage of a real risk).", ""]
    open(OUT + ".md", "w").write("\n".join(L))
    print(f"wrote {OUT}.md ({time.time()-t0:.0f}s)")

if __name__ == "__main__":
    main()
