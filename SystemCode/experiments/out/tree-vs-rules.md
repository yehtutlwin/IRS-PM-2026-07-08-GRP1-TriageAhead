# Learned tree vs authored rulebook - structural comparison (demo)

Yale rows used: 558,029 · target: nurse ESI 1-2 vs 3-5 · tree: depth<=4, min_leaf=500, class-balanced

Test-set: high-acuity sensitivity 71.3% · under-triage (missed true 1-2) 28.7% · alarm rate 41.8%


## Feature pool offered to the tree (20 of 972 columns) - CURATED, disclosed

The candidate pool was hand-picked, not the full dataset: mapped clinical fields (so MATCHED has something to match on) plus a few triage-time features that no standard uses (arrival mode, sex, BP) so TREE-ONLY could exist. Consequence: the tree's *ranking* among these is data-driven, but the *pool* carries the analyst's presumptions - TREE-ONLY here means "data-discovered strength among presumption-selected candidates", not open discovery. Report-grade version: offer ALL columns (or all cc_/vitals/meds/history) and let the tree choose; only then is a TREE-ONLY entry a finding rather than a planted candidate.

| feature | source column | rulebook allowed to use it? |
| --- | --- | --- |
| `age` | `age` | yes - maps to `patient.age` |
| `triage_vital_o2` | `triage_vital_o2` | yes - maps to `vitals.spo2` |
| `triage_vital_hr` | `triage_vital_hr` | yes - maps to `vitals.heart_rate` |
| `triage_vital_rr` | `triage_vital_rr` | yes - maps to `vitals.respiratory_rate` |
| `triage_vital_temp` | `triage_vital_temp` | yes - maps to `vitals.temp` |
| `cc_fall` | `cc_fall` | yes - maps to `E.mechanism=fall` |
| `cc_fall>65` | `cc_fall>65` | yes - maps to `E.mechanism=fall` |
| `cc_headinjury` | `cc_headinjury` | yes - maps to `E.head_strike` |
| `cc_assaultvictim` | `cc_assaultvictim` | yes - maps to `E.mechanism=assault` |
| `cc_motorvehiclecrash` | `cc_motorvehiclecrash` | yes - maps to `E.mechanism=road_accident` |
| `cc_chestpain` | `cc_chestpain` | yes - maps to `complaint.category=chest_pain` |
| `cc_abdominalpain` | `cc_abdominalpain` | yes - maps to `complaint.category=abdominal_pain` |
| `cc_abdominalpainpregnant` | `cc_abdominalpainpregnant` | yes - maps to `B-17 combo (abdo pain + pregnant)` |
| `cc_feverimmunocompromised` | `cc_feverimmunocompromised` | yes - maps to `B-07 combo (fever + immunocompromised)` |
| `meds_anticoagulants` | `meds_anticoagulants` | yes - maps to `M.anticoagulant` |
| `meds_immunosuppressants` | `meds_immunosuppressants` | yes - maps to `M.immunosuppressant_or_steroid` |
| `triage_vital_sbp` | `triage_vital_sbp` | partly - hypotension is A-10 (with hypoperfusion), not in the D danger-zone table; not mapped in this demo |
| `triage_vital_dbp` | `triage_vital_dbp` | no rulebook use |
| `male` | `gender` | NO - not a criterion in any triage standard |
| `ambulance` | `arrivalmode` | NO - not a criterion in any triage standard |

## High-acuity paths the tree learned (top 8, as conjunctive rules)

- IF ambulance > 0.5 AND cc_motorvehiclecrash <= 0.5 AND cc_abdominalpain <= 0.5 AND male > 0.5  →  high acuity   (n=61,491, precision 79%)
- IF ambulance > 0.5 AND cc_motorvehiclecrash <= 0.5 AND cc_abdominalpain <= 0.5 AND male <= 0.5  →  high acuity   (n=64,839, precision 70%)
- IF ambulance <= 0.5 AND age > 49.5 AND cc_chestpain <= 0.5 AND triage_vital_hr > 103.25  →  high acuity   (n=33,118, precision 55%)
- IF ambulance <= 0.5 AND age > 49.5 AND cc_chestpain > 0.5 AND age > 56.5  →  high acuity   (n=5,749, precision 81%)
- IF ambulance <= 0.5 AND age <= 49.5 AND triage_vital_hr > 100.417 AND triage_vital_hr > 119.75  →  high acuity   (n=4,565, precision 62%)
- IF ambulance <= 0.5 AND age > 49.5 AND cc_chestpain > 0.5 AND age <= 56.5  →  high acuity   (n=2,819, precision 74%)
- IF ambulance > 0.5 AND cc_motorvehiclecrash > 0.5 AND triage_vital_hr > 102.75 AND male > 0.5  →  high acuity   (n=1,268, precision 53%)

## MATCHED - features both sides use (tree threshold vs rulebook)

- `age` ↔ `patient.age` — tree splits: <= 49.5, <= 56.5, > 49.5, > 56.5
    - rulebook A-13.flaccid-infant: `patient.age_group equals infant`
    - rulebook B-27.geriatric-trauma-caution: `patient.age gte 55`
    - rulebook B-29.pediatric-subtle-ams: `patient.age lt 18`
    - rulebook D-01.adult-danger-zone: `patient.age gt 18`
- `cc_abdominalpain` ↔ `complaint.category=abdominal_pain` — tree splits: <= 0.5
    - rulebook B-17.abdo-pain-pregnant-or-postpartum: `complaint.category equals abdominal_pain`
    - rulebook B-18.abdo-pain-sepsis-or-hypoperfusion: `complaint.category equals abdominal_pain`
    - rulebook B-19.abdo-pain-trauma: `complaint.category equals abdominal_pain`
    - rulebook B-20.abdo-pain-refractory-constant-maximal: `complaint.category equals abdominal_pain`
- `cc_chestpain` ↔ `complaint.category=chest_pain` — tree splits: <= 0.5, > 0.5
    - rulebook B-04.chest-pain-acs-suspect: `complaint.category equals chest_pain`
- `cc_motorvehiclecrash` ↔ `E.mechanism=road_accident` — tree splits: <= 0.5, > 0.5
    - rulebook B-27.geriatric-trauma-caution: `E.mechanism in ['fall', 'road_accident', 'assault', 'penetrating_trauma']`
    - rulebook B-30.anticoagulated-trauma: `E.mechanism in ['fall', 'road_accident', 'assault']`
- `triage_vital_hr` ↔ `vitals.heart_rate` — tree splits: > 100.417, > 102.75, > 103.25, > 119.75
    - rulebook D-01.adult-danger-zone: `vitals.heart_rate gt 100`

## TREE-ONLY - data splits with no rulebook counterpart (discovery candidates)

- `ambulance` — derived from `arrivalmode` (1 if 'ambulance'). Root split of the tree; ~52% of ambulance arrivals are nurse ESI 1-2 vs ~19% for car/walk-in. MUST NOT become a rule: it is a proxy for the dispatcher's/paramedics' prior acuity judgment (laundering an upstream decision), partly a consequence of the acuity we assess, and no triage scale uses arrival mode. Report as a practice pattern; keep it in the ML rival (legitimately known at triage) - the rival wins agreement partly by exploiting a proxy the rulebook is forbidden to use.
- `male` — derived from `gender`. A bias axis, not a criterion: keep in the ML rival only with an explicit fairness analysis (does nurse acuity differ by sex conditional on presentation?), otherwise drop. Never a rule.

## RULEBOOK-ONLY - 43 criteria the tree can never rediscover here

Fields absent from routine triage records (mechanism detail, LOC, responsiveness, confirmed-status gates) or events too rare for accuracy-driven splits:

A-01.unresponsive, A-02.arrest-or-imminent, A-03.apneic-or-intubated, A-04.pulseless, A-05.severe-respiratory-distress, A-06.occluded-airway, A-07.active-seizure, A-08.spo2-below-90-with-compromise, A-09.anaphylaxis, A-10.hypotension-with-hypoperfusion, A-11.hypoglycemia, A-12.severe-brady-or-tachycardia, A-13.flaccid-infant, A-14.penetrating-trauma-unstable, B-01.new-altered-mental-status, B-02.severe-pain-consider, B-03.severe-pain-systemic-cause, B-04.chest-pain-acs-suspect, B-05.stroke-signs, B-06.possible-ectopic-stable …


## Caveats

- Label = nurse decision (mimics practice, not truth); outcome arbitration would be a further experiment.
- Exploratory method only: a fuller version would need a patient-level split, threshold-sensitivity reruns, and the full column mapping table.
- B-30 note: fall+anticoagulant is 0.2% of rows - watch whether any tree path pairs them (rare-event blindness is the expected result and the floor's justification).
- Feature-selection leakage of the analyst's priors: a curated candidate pool bounds 'discoveries' to what the analyst already thought worth checking (same shape as synthetic-data circularity). Curation is acceptable for demonstrating the METHOD; the FINDING requires the open pool, with the curation disclosed - see the feature-pool table above.