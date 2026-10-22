# Practice signal - the learned lane on the report (pre-arrival features only)

Trained 2026-09-19 on 446,423 Yale visits, tested on 111,606 (visit-level split, seed 42).
Label: recorded nurse ESI 1-2 vs 3-5 (prevalence 30.3%). Features (17): age, the interview's coarse complaint
groups (multi-hot; built from the Yale `cc_*` flags with the mapping in `prototype/practice_signal.py`), injury mechanism,
fever, anticoagulation (`meds_anticoagulants`), immune status (`meds_immunosuppressants` / `meds_antineoplastics` /
`cc_feverimmunocompromised`). No vitals, no labs - the report is produced before anyone examines the patient.

This lane is **advisory**: it describes how similar past visits were triaged at one site; it never moves the ESI floor.
The task H comparator (with vitals) is the data ceiling, not the rules' rival: a fair comparison needs equal inputs, so the rules are compared with this pre-arrival model (evaluation number 5).

## Discrimination and calibration

- AUROC **0.714** (with vitals, task H reaches ~0.85 - the gap is what arrival vitals add)
- Brier score 0.181; the report quotes the model's probability as 'an estimated N% were ESI 1-2', so calibration matters:

| decile | predicted share | actual share | n |
| --- | ---: | ---: | ---: |
| 1 | 8.7% | 8.2% | 11,161 |
| 2 | 14.1% | 14.1% | 11,288 |
| 3 | 20.4% | 20.0% | 11,773 |
| 4 | 23.4% | 23.6% | 11,231 |
| 5 | 25.8% | 26.0% | 10,480 |
| 6 | 28.4% | 29.1% | 11,915 |
| 7 | 29.3% | 29.7% | 10,405 |
| 8 | 32.6% | 32.2% | 11,079 |
| 9 | 50.3% | 50.0% | 11,253 |
| 10 | 70.5% | 70.4% | 11,021 |

## Bands used on the report (high ≥ 50%, low ≤ 20%)

- 'usually high acuity' band covers 14.7% of test visits; 65.6% of those were ESI 1-2;
  it catches 31.9% of all ESI 1-2 visits - most high-acuity visits are NOT in the band pre-arrival,
  which is exactly why the lane can only corroborate, never reassure.

## Each complaint group on its own (share of visits recorded ESI 1-2)

| interview group | n visits | ESI 1-2 share |
| --- | ---: | ---: |
| neuro_symptoms | 39,517 | 58.0% |
| breathing | 34,442 | 54.7% |
| chest_pain | 36,832 | 52.2% |
| dizziness | 19,214 | 40.8% |
| fever | 9,099 | 39.5% |
| nosebleed | 1,967 | 23.1% |
| injury_fall | 71,109 | 20.3% |
| abdominal_pain | 67,004 | 15.3% |
| eye_problem | 6,148 | 9.6% |
| sore_throat | 7,489 | 2.0% |

## Limitations

- The label is practice (nurse ESI at one US site, 2014-2017), including its errors and local habits; not truth.
- The interview's complaint groups are coarse; the model sees 'chest pain', not 'chest pain radiating to the jaw'.
- Immune status and anticoagulation are proxied from medication classes on the Yale side and from caregiver answers on ours.
- Visit-level split (no patient id); a patient-level check needs MIMIC-IV-ED.
