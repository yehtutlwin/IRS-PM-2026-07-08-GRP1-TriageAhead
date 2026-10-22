# Second reading of the practice cases (gemini) against our test cases

Cases compared: 187 of 187. A second model read each printed case with the field list and no sight of our files (`experiments/second_reading.py`); this compares the two fact sets (`experiments/second_reading_compare.py`).

| Facts | Count |
| --- | ---: |
| agree | 1431 |
| only ours | 294 |
| only theirs | 146 |
| value differs | 76 |
| theirs, no such field | 0 |

## Cases where the outcome under the rule engine differs (30)

| case | ours | theirs | our expectation | rules (ours) | rules (theirs) |
| --- | --- | --- | --- | --- | --- |
| ch9-42 | esi1 | floor2 | esi1 | A-01.unresponsive, B-32.thunderclap-headache, B-34.headache-red-flags, B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | B-34.headache-red-flags, B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache |
| ch9-95 | none | esi1 | none |  | A-01.unresponsive |
| A-8 | floor2 | none | floor2 | B-12.increasing-respiratory-effort |  |
| A-10 | esi1 | none | esi1 | A-05.severe-respiratory-distress, A-14.penetrating-trauma-unstable, A-22.requires-lifesaving-intervention |  |
| A-18 | esi1 | floor2 | esi1 | A-10.hypotension-with-hypoperfusion, B-04.chest-pain-acs-suspect, B-36.abnormal-ecg-chest-pain | B-04.chest-pain-acs-suspect, B-36.abnormal-ecg-chest-pain |
| A-24 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion |  |
| B-20 | esi1 | none | esi1 | A-14.penetrating-trauma-unstable, A-22.requires-lifesaving-intervention |  |
| B-25 | esi1 | floor2 | esi1 | A-05.severe-respiratory-distress, B-12.increasing-respiratory-effort | B-12.increasing-respiratory-effort |
| ch9-2 | esi1 | floor2 | esi1 | A-08.spo2-below-90-with-compromise, A-22.requires-lifesaving-intervention, B-01.new-altered-mental-status, B-26.suspected-toxic-ingestion | B-01.new-altered-mental-status, B-09.suicidal-or-homicidal, B-26.suspected-toxic-ingestion |
| ch9-8 | none | floor2 | none |  | B-29.pediatric-subtle-ams |
| ch9-16 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion, A-22.requires-lifesaving-intervention |  |
| ch9-22 | esi1 | none | esi1 | A-05.severe-respiratory-distress, A-22.requires-lifesaving-intervention, B-12.increasing-respiratory-effort |  |
| ch9-37 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion, A-12.severe-brady-or-tachycardia, A-17.chest-pain-unstable-lifesaving, A-22.requires-lifesaving-intervention |  |
| ch9-45 | none | floor2 | none |  | B-06.possible-ectopic-stable |
| ch9-48 | esi1 | floor2 | esi1 | A-10.hypotension-with-hypoperfusion, A-18.pregnancy-hemodynamic-instability-lifesaving, A-22.requires-lifesaving-intervention, B-13.postpartum-hemorrhage, B-37.pregnant-postpartum-sbp-out-of-range | B-13.postpartum-hemorrhage, B-37.pregnant-postpartum-sbp-out-of-range |
| ch9-59 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion, A-17.chest-pain-unstable-lifesaving, A-22.requires-lifesaving-intervention, B-04.chest-pain-acs-suspect |  |
| ch9-60 | floor2 | none | floor2 | B-12.increasing-respiratory-effort |  |
| ch9-66 | esi1 | none | esi1 | A-12.severe-brady-or-tachycardia, A-16.profound-hypotension, A-22.requires-lifesaving-intervention |  |
| ch9-69 | esi1 | none | esi1 | A-14.penetrating-trauma-unstable, A-22.requires-lifesaving-intervention |  |
| ch9-71 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion, A-22.requires-lifesaving-intervention |  |
| ch9-92 | esi1 | none | esi1 | A-05.severe-respiratory-distress, A-08.spo2-below-90-with-compromise, A-22.requires-lifesaving-intervention, B-12.increasing-respiratory-effort |  |
| ch9-100 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion, A-16.profound-hypotension, A-22.requires-lifesaving-intervention |  |
| A-3 | esi1 | none | esi1 | A-22.requires-lifesaving-intervention, B-01.new-altered-mental-status, B-29.pediatric-subtle-ams |  |
| appA-ch3-q1 | floor2 | none | floor2 | B-04.chest-pain-acs-suspect |  |
| appA-ch3-q7 | floor2 | none | floor2 | B-29.pediatric-subtle-ams |  |
| appA-ch3-q12 | floor2 | none | floor2 | B-01.new-altered-mental-status |  |
| appA-ch3-q13 | floor2 | none | floor2 | B-12.increasing-respiratory-effort |  |
| appA-ch3-q14 | esi1 | none | esi1 | A-10.hypotension-with-hypoperfusion |  |
| appA-ch3-q15 | esi1 | floor2 | esi1 | A-18.pregnancy-hemodynamic-instability-lifesaving, A-22.requires-lifesaving-intervention, B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache |
| appA-ch6-q2 | esi1 | none | esi1 | A-19.ineffective-tissue-perfusion, A-20.ineffective-respiratory-pattern, A-22.requires-lifesaving-intervention |  |

## Fields most often different

| field | kind | cases |
| --- | --- | ---: |
| complaint.category | value differs | 37 |
| obs.requires_lifesaving_intervention | only ours | 19 |
| complaint.category | only ours | 17 |
| A.allergies | only ours | 16 |
| history.conditions | value differs | 16 |
| history.conditions | only ours | 15 |
| patient.has_ovaries | only theirs | 15 |
| M.medications | only ours | 14 |
| history.conditions | only theirs | 14 |
| patient.age_months | only ours | 13 |
| patient.age | only ours | 12 |
| vitals.hypotension | only ours | 11 |
| obs.hemodynamically_unstable | only ours | 11 |
| E.mechanism | only ours | 10 |
| obs.avpu | only theirs | 10 |
| red_flags.responsive | only theirs | 10 |
| complaint.fever | only ours | 10 |
| E.fall_height_meters | only ours | 9 |
| history.pregnant | only ours | 8 |
| complaint.onset | value differs | 8 |
| M.medications | value differs | 7 |
| patient.sex | only ours | 6 |
| complaint.atso_elements_count | only ours | 6 |
| obs.subtle_mental_status_change | only ours | 6 |
| complaint.respiratory_distress_signs | only ours | 6 |
| infection.rash | only theirs | 6 |
| vitals.abnormal_for_patient | only theirs | 5 |
| complaint.increasing_respiratory_effort | only ours | 5 |
| complaint.shortness_of_breath | only theirs | 5 |
| obs.confusion_lethargy_disorientation | only theirs | 5 |
| vitals.sbp | only theirs | 5 |
| complaint.rash | only ours | 5 |
| M.anticoagulant | only theirs | 4 |
| red_flags.heavy_bleeding | only ours | 4 |
| history.postpartum | only ours | 4 |
| M.medications | only theirs | 4 |
| complaint.extremity_neurovascular_compromise | only ours | 4 |
| obs.new_confusion_lethargy_disorientation | only ours | 4 |
| obs.severe_respiratory_distress | only ours | 4 |
| obs.hypoperfusion_signs | only ours | 4 |

## Reading it

- *agree*: same field, same value. *value differs*: both wrote the field with different values; the per-case JSON lists both.
- *only ours* / *only theirs*: a fact one reading wrote and the other did not; a person decides which reading the book supports.
- *theirs, no such field*: the model used a name outside the field file; ignored for the outcome, listed per case.
- An outcome change is where the two fact sets lead the rule engine to a different class (ESI-1 indicator, floor, none); these are read first.
