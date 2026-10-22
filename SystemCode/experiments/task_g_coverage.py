"""Task G pre-registration: which criteria can the Yale dataset actually test?

For every antecedent field in rules/criteria.yaml, declare where it can come
from in the Yale data (see data/yale-schema.md), then evaluate each rule's
when-clause structure: a rule is ASSESSABLE if every leaf in some satisfiable
branch is available (all -> all children, any -> any child). Cited column
names are verified against the dataset's column list (workbook column_dictionary
sheet), so a typo in this table becomes 'absent' rather than a silent claim.

Output: experiments/out/task-g-coverage.md.   Run from the repo root:
    python3 experiments/task_g_coverage.py
"""
import os, yaml
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRITERIA = os.path.join(ROOT, "rules", "criteria.yaml")
WORKBOOK = os.path.join(ROOT, "data", "yale-explorer.xlsx")
OUT = os.path.join(ROOT, "experiments", "out", "task-g-coverage.md")

# tier: direct = a Yale column IS the fact | derivable = documented transformation
# of Yale columns | absent = nothing in Yale can supply it (eyes-on findings,
# judgment fields, detail the chief-complaint label doesn't carry).
# cols = Yale columns the claim rests on (verified to exist).
FIELD_SOURCES = {
    # -- patient
    "patient.age":        ("direct",    ["age"], "integer years"),
    "patient.age_group":  ("derivable", ["age"], "bands from age; infant band coarse (years only)"),
    "patient.age_days":   ("absent",    ["age"], "age is integer years - neonatal day counts impossible"),
    "patient.age_months": ("absent",    ["age"], "age is integer years"),
    # -- vitals (this triage)
    "vitals.heart_rate":        ("direct",    ["triage_vital_hr"], ""),
    "vitals.respiratory_rate":  ("direct",    ["triage_vital_rr"], ""),
    "vitals.spo2":              ("direct",    ["triage_vital_o2"], ""),
    "vitals.temp_c":            ("derivable", ["triage_vital_temp"], "recorded in Fahrenheit -> convert"),
    "vitals.hypotension":       ("derivable", ["triage_vital_sbp"], "needs a documented SBP threshold (handbook gives 'profound')"),
    "vitals.extreme_heart_rate":("derivable", ["triage_vital_hr"], "needs documented thresholds"),
    "vitals.spo2_is_patients_norm": ("absent", [], "no baseline SpO2 field"),
    "vitals.profound_hypoglycemia": ("absent", ["glucose_last"], "glucose columns are PRIOR-year history, not point-of-care"),
    # -- complaint
    "complaint.category":  ("derivable", ["cc_chestpain", "cc_abdominalpain", "cc_fall", "cc_fever", "cc_sorethroat", "cc_dizziness", "cc_epistaxis"], "cc_* label -> category mapping table (document every line)"),
    "complaint.fever":     ("derivable", ["cc_fever", "cc_feverimmunocompromised"], "chief complaint 'fever'"),
    "complaint.pain_rating": ("absent",  [], "no pain score column in Yale"),
    "complaint.acs_suspicion": ("absent", ["cc_chestpain"], "judgment field; cc_chestpain alone does not establish ACS features (pilot assumed it)"),
    "complaint.stroke_signs":  ("derivable", ["cc_strokealert"], "a stroke alert implies stroke signs were suspected - label, not exam"),
    "complaint.danger_to_self_or_others": ("derivable", ["cc_suicidal"], "complaint label; homicidal ideation not separable"),
    "complaint.vaginal_bleeding": ("derivable", ["cc_vaginalbleeding"], ""),
    "complaint.sexual_assault":  ("absent",    ["cc_assaultvictim"], "only a generic assault-victim label exists"),
    "complaint.known_toxic_ingestion": ("derivable", ["cc_overdose-intentional", "cc_overdose-accidental"], "intent labels; substance unknown"),
    "complaint.increasing_respiratory_effort": ("absent", ["cc_shortnessofbreath"], "trajectory ('increasing') not recorded"),
    "complaint.infection_signs": ("absent", [], "clinical signs not recorded"),
    "complaint.amputation_partial_or_complete": ("absent", [], ""),
    "complaint.atso_elements_count": ("absent", [], "ocular exam constellation"),
    "complaint.brisk_or_posterior_bleeding": ("absent", ["cc_epistaxis"], "severity/site not in label"),
    "complaint.button_battery_or_magnet_ingestion": ("absent", [], ""),
    "complaint.compartment_syndrome_symptoms": ("absent", [], ""),
    "complaint.extremity_neurovascular_compromise": ("absent", [], ""),
    "complaint.needle_stick_healthcare_worker": ("absent", [], ""),
    "complaint.pain_cause_class": ("absent", [], "judgment field"),
    "complaint.pain_refractory_constant_or_maximal_onset": ("absent", [], "pain character not recorded"),
    "complaint.possible_ectopic_pregnancy": ("absent", [], ""),
    "complaint.possible_pelvis_femur_fracture_or_dislocation": ("absent", [], "suspicion level not recorded"),
    "complaint.postpartum_hemorrhage": ("absent", [], ""),
    # -- events / mechanism
    "E.mechanism":  ("derivable", ["cc_fall", "cc_motorvehiclecrash", "cc_assaultvictim"], "from complaint labels; ecodes* columns are PRIOR history, do not use"),
    "E.fall_height_meters": ("absent", [], ""),
    "E.vehicle_ejection":   ("absent", [], ""),
    "E.mechanical_extrication": ("absent", [], ""),
    "E.abdominal_trauma":   ("absent", [], ""),
    "E.body_region":        ("absent", [], ""),
    # -- medications
    "M.anticoagulant.value":  ("direct",    ["meds_anticoagulants"], ">= 1 active anticoagulant"),
    "M.anticoagulant.status": ("derivable", ["meds_anticoagulants"], "EHR active-med list -> treat as confirmed (tier 2, document)"),
    "M.beta_blocker":         ("absent",    [], "no beta-blocker therapeutic subgroup among the 48 meds_* classes"),
    "M.immunosuppressant_or_steroid": ("derivable", ["meds_immunosuppressants"], "immunosuppressants only; no steroid subgroup"),
    # -- history
    "history.immunocompromised": ("derivable", ["cc_feverimmunocompromised", "hivinfectn", "maintchemr"], "complaint label or PMH flags (HIV, maintenance chemo)"),
    "history.pregnant": ("derivable", ["cc_abdominalpainpregnant"], "only via pregnancy-specific complaint labels; PMH has no current-pregnancy flag"),
    "history.thrombocytopenia_or_clotting_disorder": ("derivable", ["coaghemrdx"], "PMH CCS 'coagulation and hemorrhagic disorders'"),
    "history.transplant_recipient_or_listed": ("absent", [], "no transplant PMH category"),
    "history.baseline_mental_status": ("absent", [], ""),
}
# every obs.* field is an eyes-on finding: no consciousness / exam columns exist in Yale
OBS_NOTE = "eyes-on finding; Yale has no examination columns (verified: no AVPU/GCS/mental-status field)"

def load_columns():
    cd = pd.read_excel(WORKBOOK, sheet_name="column_dictionary")
    return set(cd["column"].astype(str))

def field_tier(field, cols, problems):
    if field.startswith("obs."):
        return "absent", [], OBS_NOTE
    if field not in FIELD_SOURCES:
        problems.append(f"unclassified field {field} -> treated as absent")
        return "absent", [], "UNCLASSIFIED"
    tier, need, note = FIELD_SOURCES[field]
    missing = [c for c in need if c not in cols]
    if missing and tier != "absent":
        problems.append(f"{field}: cited column(s) not in dataset {missing} -> downgraded to absent")
        return "absent", need, f"cited column missing: {missing}"
    return tier, need, note

def available(cond, tiers):
    """True if the condition can be evaluated from Yale-available fields."""
    if not isinstance(cond, dict): return False
    if "all" in cond: return all(available(c, tiers) for c in cond["all"])
    if "any" in cond: return any(available(c, tiers) for c in cond["any"])
    return tiers.get(cond.get("field"), "absent") in ("direct", "derivable")

def leaf_fields(cond, acc):
    if not isinstance(cond, dict): return acc
    if "field" in cond: acc.append(cond["field"])
    for k in ("all", "any"):
        for c in cond.get(k, []): leaf_fields(c, acc)
    return acc

def main():
    crit = yaml.safe_load(open(CRITERIA))
    cols = load_columns()
    problems = []
    used = sorted({f for r in crit if "when" in r for f in leaf_fields(r["when"], [])})
    tiers = {}; meta = {}
    for f in used:
        t, need, note = field_tier(f, cols, problems)
        tiers[f] = t; meta[f] = (need, note)

    rows = []
    for r in crit:
        rid, dp = r["id"], r.get("decision_point", "?")
        if "when" not in r:
            rows.append((rid, dp, "not a firing rule", "definition / policy entry (no when-clause)")); continue
        fields = leaf_fields(r["when"], [])
        absent = sorted({f for f in fields if tiers[f] == "absent"})
        if available(r["when"], tiers):
            status = "ASSESSABLE" if not absent else "ASSESSABLE (via available branch)"
        else:
            status = "untestable on Yale"
        rows.append((rid, dp, status, ", ".join(absent) if absent else "-"))

    counts = {}
    for _, _, s, _ in rows: counts[s] = counts.get(s, 0) + 1
    L = ["# Task G coverage: which criteria can Yale test?", "",
         "Generated by `experiments/task_g_coverage.py` from `rules/criteria.yaml` and the",
         "Yale column list; field sourcing rules are in the script (tiers per data/yale-schema.md).", "",
         "## Summary", ""]
    for s, n in sorted(counts.items(), key=lambda x: -x[1]): L.append(f"- **{s}**: {n}")
    L += ["", f"Antecedent fields: {len(used)} - direct {sum(t=='direct' for t in tiers.values())}, "
          f"derivable {sum(t=='derivable' for t in tiers.values())}, absent {sum(t=='absent' for t in tiers.values())}.", ""]
    if problems:
        L += ["## Sourcing problems (fix the table or the data)", ""] + [f"- {p}" for p in problems] + [""]
    L += ["## Per criterion", "", "| criterion | DP | Task G status | fields Yale cannot supply |", "| --- | --- | --- | --- |"]
    for rid, dp, s, absent in rows: L.append(f"| {rid} | {dp} | {s} | {absent} |")
    L += ["", "## Per field", "", "| field | tier | Yale columns | note |", "| --- | --- | --- | --- |"]
    for f in used:
        need, note = meta[f]
        L.append(f"| {f} | {tiers[f]} | {', '.join(need) or '-'} | {note} |")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    if problems: print("\nPROBLEMS:", *problems, sep="\n  ")
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}")

if __name__ == "__main__":
    main()
