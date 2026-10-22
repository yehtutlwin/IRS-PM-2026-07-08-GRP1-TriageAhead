# Task G - rulebook vs practice on the whole Yale dataset (two arms)

560,486 visits, 558,029 with a recorded ESI. Engine: rules/criteria.yaml as committed;
mapping table and deliberately unmapped fields listed at the end. The recorded ESI is a comparator,
not truth (data/yale-schema.md); a floor is a lower-bound claim, so 'consistent' means the floor did not
exceed the recorded level. Denominators as the script defines them.

## Arm: history only

- Claims made (floor or ESI-1 indicator): **16,056** of 558,029 rows = reach **2.88%** (6,291 unique fact signatures)
- Consistent with recorded ESI 1-2: **82.7%** of claims (13,274)
- Overshoot (floor claimed, recorded ESI 3-5): **2,782** = 17.3% of floors; those visits were admitted at **25.7%** vs 18.3% for recorded-3-5 visits with no claim
- Recorded ESI 1-2 caught by a claim: 13,274 of 168,805; silent misses (recorded 1-2, no claim, at least one rule evaluable): **155,521** (92.1% of recorded 1-2)
- Rows where no rule had its inputs at all: 11

| rule | fires | recorded ESI 1 / 2 / 3 / 4 / 5 | below floor | admitted |
| --- | ---: | --- | ---: | ---: |
| B-09.suicidal-or-homicidal | 8,286 | 13 / 8019 / 235 / 13 / 6 | 3.1% | 38.3% |
| D-05.context-immunosuppression-consider | 2,522 | 23 / 1544 / 836 / 88 / 31 | 37.9% | 90.7% |
| B-05.stroke-signs | 2,187 | 805 / 1372 / 10 / 0 / 0 | 0.5% | 89.8% |
| B-17.abdo-pain-pregnant-or-postpartum | 2,051 | 0 / 647 / 1388 / 14 / 2 | 68.5% | 7.4% |
| B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | 2,051 | 0 / 647 / 1388 / 14 / 2 | 68.5% | 7.4% |
| B-30.anticoagulated-trauma | 1,298 | 17 / 718 / 513 / 45 / 5 | 43.4% | 83.8% |
| B-26.suspected-toxic-ingestion | 1,259 | 63 / 1059 / 130 / 7 / 0 | 10.9% | 47.7% |
| B-07.immunocompromised-fever | 625 | 2 / 530 / 91 / 1 / 1 | 14.9% | 81.6% |
| B-21.abdo-pain-vaginal-bleeding | 383 | 0 / 83 / 297 / 2 / 1 | 78.3% | 8.1% |
| B-15.high-risk-epistaxis | 173 | 0 / 67 / 79 / 24 / 3 | 61.3% | 46.2% |

Coverage by presenting complaint (top 15):

| complaint | rows | claims | claim % | recorded 1-2 |
| --- | ---: | ---: | ---: | ---: |
| (no mapped complaint) | 369,908 | 9,225 | 2.5% | 107,464 |
| abdominal_pain | 55,533 | 2,369 | 4.3% | 8,554 |
| injury_fall | 43,899 | 1,348 | 3.1% | 10,379 |
| chest_pain | 35,694 | 111 | 0.3% | 18,893 |
| breathing | 28,665 | 23 | 0.1% | 16,500 |
| dizziness | 11,825 | 12 | 0.1% | 3,628 |
| sore_throat | 7,291 | 1 | 0.0% | 136 |
| neuro_symptoms | 2,179 | 2,179 | 100.0% | 2,170 |
| nosebleed | 1,934 | 172 | 8.9% | 448 |
| fever | 1,101 | 616 | 55.9% | 633 |

## Arm: with vitals

- Claims made (floor or ESI-1 indicator): **16,726** of 558,029 rows = reach **3.0%** (357,777 unique fact signatures)
- Consistent with recorded ESI 1-2: **82.8%** of claims (13,850)
- Overshoot (floor claimed, recorded ESI 3-5): **2,782** = 17.3% of floors; those visits were admitted at **25.7%** vs 18.3% for recorded-3-5 visits with no claim
- Recorded ESI 1-2 caught by a claim: 13,850 of 168,805; silent misses (recorded 1-2, no claim, at least one rule evaluable): **154,949** (91.8% of recorded 1-2)
- Rows where no rule had its inputs at all: 7

| rule | fires | recorded ESI 1 / 2 / 3 / 4 / 5 | below floor | admitted |
| --- | ---: | --- | ---: | ---: |
| D-01.adult-danger-zone | 75,100 | 371 / 28439 / 33420 / 11517 / 1353 | 61.6% | 37.9% |
| B-09.suicidal-or-homicidal | 8,286 | 13 / 8019 / 235 / 13 / 6 | 3.1% | 38.3% |
| D-11.spo2-below-92-any-age | 3,566 | 79 / 2503 / 843 / 121 / 20 | 27.6% | 75.4% |
| D-05.context-immunosuppression-consider | 2,522 | 23 / 1544 / 836 / 88 / 31 | 37.9% | 90.7% |
| B-05.stroke-signs | 2,187 | 805 / 1372 / 10 / 0 / 0 | 0.5% | 89.8% |
| B-17.abdo-pain-pregnant-or-postpartum | 2,051 | 0 / 647 / 1388 / 14 / 2 | 68.5% | 7.4% |
| B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | 2,051 | 0 / 647 / 1388 / 14 / 2 | 68.5% | 7.4% |
| B-30.anticoagulated-trauma | 1,298 | 17 / 718 / 513 / 45 / 5 | 43.4% | 83.8% |
| B-26.suspected-toxic-ingestion | 1,259 | 63 / 1059 / 130 / 7 / 0 | 10.9% | 47.7% |
| A-12.severe-brady-or-tachycardia | 682 | 41 / 547 / 85 / 9 / 0 | 13.8% | 65.8% |
| B-07.immunocompromised-fever | 625 | 2 / 530 / 91 / 1 / 1 | 14.9% | 81.6% |
| B-21.abdo-pain-vaginal-bleeding | 383 | 0 / 83 / 297 / 2 / 1 | 78.3% | 8.1% |
| B-15.high-risk-epistaxis | 173 | 0 / 67 / 79 / 24 / 3 | 61.3% | 46.2% |

Coverage by presenting complaint (top 15):

| complaint | rows | claims | claim % | recorded 1-2 |
| --- | ---: | ---: | ---: | ---: |
| (no mapped complaint) | 369,908 | 9,693 | 2.6% | 107,464 |
| abdominal_pain | 55,533 | 2,412 | 4.3% | 8,554 |
| injury_fall | 43,899 | 1,364 | 3.1% | 10,379 |
| chest_pain | 35,694 | 180 | 0.5% | 18,893 |
| breathing | 28,665 | 81 | 0.3% | 16,500 |
| dizziness | 11,825 | 25 | 0.2% | 3,628 |
| sore_throat | 7,291 | 4 | 0.1% | 136 |
| neuro_symptoms | 2,179 | 2,179 | 100.0% | 2,170 |
| nosebleed | 1,934 | 172 | 8.9% | 448 |
| fever | 1,101 | 616 | 55.9% | 633 |

## Delta between arms - the nurse-vitals-entry decision gate

- Rows that gain a claim only when vitals are known: **670** (576 recorded ESI 1-2, 94 recorded 3-5)
- DP-D 'reconsider up-triage' fires on 77,149 rows; their recorded ESI: {1: 391, 2: 29667, 3: 34111, 4: 11597, 5: 1383} (D is a modifier on the 3/4/5 side, reported separately from the floor)

## Mapping table (source columns -> facts)

```json
{
 "cc_to_category": {
  "cc_chestpain": "chest_pain",
  "cc_abdominalpain": "abdominal_pain",
  "cc_abdominalpainpregnant": "abdominal_pain",
  "cc_fall": "injury_fall",
  "cc_fall>65": "injury_fall",
  "cc_fever": "fever",
  "cc_feverimmunocompromised": "fever",
  "cc_sorethroat": "sore_throat",
  "cc_dizziness": "dizziness",
  "cc_epistaxis": "nosebleed",
  "cc_shortnessofbreath": "breathing",
  "cc_breathingdifficulty": "breathing",
  "cc_dyspnea": "breathing",
  "cc_strokealert": "neuro_symptoms",
  "cc_motorvehiclecrash": "injury_fall",
  "cc_assaultvictim": "injury_fall"
 },
 "mechanism": {
  "cc_fall": "fall",
  "cc_fall>65": "fall",
  "cc_motorvehiclecrash": "road_accident",
  "cc_assaultvictim": "assault"
 },
 "flag_facts": {
  "cc_strokealert": [
   "complaint.stroke_signs",
   true
  ],
  "cc_suicidal": [
   "complaint.danger_to_self_or_others",
   true
  ],
  "cc_vaginalbleeding": [
   "complaint.vaginal_bleeding",
   true
  ],
  "cc_overdose-intentional": [
   "complaint.known_toxic_ingestion",
   true
  ],
  "cc_overdose-accidental": [
   "complaint.known_toxic_ingestion",
   true
  ],
  "cc_abdominalpainpregnant": [
   "history.pregnant_or_postpartum",
   true
  ],
  "cc_fever": [
   "complaint.fever",
   true
  ],
  "cc_feverimmunocompromised": [
   "complaint.fever",
   true
  ]
 },
 "other": [
  "meds_anticoagulants>=1 -> M.anticoagulant confirmed",
  "meds_immunosuppressants>=1 -> M.immunosuppressant_or_steroid",
  "cc_feverimmunocompromised|hivinfectn|maintchemr -> history.immunocompromised",
  "coaghemrdx -> history.thrombocytopenia_or_clotting_disorder",
  "age -> patient.age",
  "arm 2: hr/rr/o2/sbp/temp -> vitals.*; extreme HR = >150 or <40; hypotension = SBP<90 (documented assumptions)"
 ]
}
```

Deliberately not mapped:

- `complaint.acs_suspicion`: judgment field - cc_chestpain does not establish ACS features
- `obs.*`: eyes-on findings - no examination columns in Yale (cc_unresponsive is a reason for visit)
- `complaint.pain_rating`: no pain score column
- `E.head_strike / E.loc / fall height`: not recorded

## How to read the disagreements

Every overshoot or silent miss belongs to one of: nurse deviated from the standard / standard silent /
data lacks the deciding detail / mapping error. This run cannot attribute automatically; the per-rule
tables above are the starting point (a rule whose fires sit mostly at recorded 3-5 with a LOW admit rate
points at a mapping or standard problem; a HIGH admit rate points at practice under-triage of a real risk).
