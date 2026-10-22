# Task H - learned comparator (gradient boosting on Yale visits)

Rows with a recorded ESI: 558,029 - visit-level 80/20 stratified (no patient id in the public file) - seed 42.
Features: 6 triage vitals (NaN kept as missing), age, sex, 200 chief-complaint flags;
a second variant adds arrival-by-ambulance (a practice proxy no criterion uses). Experiments only -
this model never runs in the product; it is the rules' rival.

## High acuity (ESI 1-2) vs not - the headline is under-triage

| model | sensitivity (ESI 1-2 caught) | under-triage | specificity | PPV | alarm rate | accuracy | AUROC | admitted among missed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base / unweighted | 63.1% | **36.9%** | 91.4% | 76.0% | 25.1% | 82.8% | 0.885 | 50.6% |
| base / class-balanced | 79.6% | **20.4%** | 80.5% | 63.9% | 37.7% | 80.2% | 0.885 | 44.8% |
| with_ambulance / unweighted | 64.9% | **35.1%** | 91.0% | 75.7% | 25.9% | 83.1% | 0.889 | 49.7% |
| with_ambulance / class-balanced | 80.7% | **19.3%** | 80.6% | 64.3% | 38.0% | 80.6% | 0.889 | 44.0% |

Reading: the unweighted model optimises accuracy on a ~30/70 split and buys it by missing
high-acuity visits; the class-balanced model trades false alarms for catches. The gap between the
two rows is the accuracy-vs-safety finding; the 'admitted among missed' column is the outcome check
on the visits the model would have under-triaged.

## Five-level ESI

| model | exact | within one level | weighted kappa | under-triage (true 1-2 -> predicted 3-5) |
| --- | ---: | ---: | ---: | ---: |
| base / unweighted | 66.3% | 96.6% | 0.667 | **33.6%** |
| base / class-balanced | 58.2% | 90.3% | 0.596 | **25.1%** |

Per class - base / unweighted:

| ESI | precision | recall | F1 | n |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.62 | 0.26 | 0.36 | 1,054 |
| 2 | 0.71 | 0.65 | 0.68 | 32,707 |
| 3 | 0.66 | 0.72 | 0.69 | 47,246 |
| 4 | 0.64 | 0.69 | 0.66 | 25,001 |
| 5 | 0.52 | 0.22 | 0.31 | 5,598 |

Per class - base / class-balanced:

| ESI | precision | recall | F1 | n |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.09 | 0.81 | 0.17 | 1,054 |
| 2 | 0.68 | 0.59 | 0.63 | 32,707 |
| 3 | 0.74 | 0.55 | 0.63 | 47,246 |
| 4 | 0.62 | 0.61 | 0.61 | 25,001 |
| 5 | 0.25 | 0.64 | 0.36 | 5,598 |

## What the model leans on (permutation importance, class-balanced binary, 6,000 test visits)

| feature | AUROC drop when shuffled |
| --- | ---: |
| cc_alcoholintoxication | 0.0393 |
| age | 0.0375 |
| cc_suicidal | 0.0216 |
| cc_psychiatricevaluation | 0.0154 |
| cc_chestpain | 0.0148 |
| triage_vital_hr | 0.0123 |
| cc_alteredmentalstatus | 0.0103 |
| cc_shortnessofbreath | 0.0075 |
| triage_vital_temp | 0.0064 |
| cc_syncope | 0.0061 |
| cc_strokealert | 0.0052 |
| cc_drugproblem | 0.0051 |
| cc_backpain | 0.0051 |
| triage_vital_rr | 0.0039 |
| cc_rash | 0.0037 |
| cc_alcoholproblem | 0.0036 |
| cc_neurologicproblem | 0.0034 |
| cc_dentalpain | 0.0034 |
| cc_sorethroat | 0.0033 |
| triage_vital_sbp | 0.0031 |

## Limitations

- The label is the recorded nurse ESI - practice, not truth; the model learns practice including its errors.
- Visit-level split: repeat visitors can appear on both sides (no patient id); a patient-level split needs MIMIC.
- Chief-complaint flags are reasons for visit, not findings (data/yale-schema.md); rare dangerous
  presentations are exactly where an accuracy-optimising model is blind - see the under-triage column.
- Vitals missing for many of the sickest visits are kept as missing, which the model can exploit as a signal;
  that is a practice artefact, not physiology.
