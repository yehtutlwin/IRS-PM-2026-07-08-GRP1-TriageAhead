# The current rules file next to the blind re-extractions, rule by rule

Blind re-extractions: opus (415 entries), fable (335 entries), gpt (282 entries), gemini (318 entries).
Matching: same printed page and overlapping quote (longest common run of words at least 60% of the shorter quote).
A cell shows what that blind re-extraction made of the sentence(s) our rule rests on. "(inferred)" means the model marked the level as its own inference, not the handbook's words.

Firing rules of ours: 92. Every blind re-extraction that has an entry agrees with our effect: 69. At least one blind re-extraction gives a different effect or files the sentence as not a rule: 22. No blind re-extraction has an entry: 1.

## Rules where at least one blind re-extraction differs

| rule | ours | opus | fable | gpt | gemini | re-extractions differing |
| --- | --- | --- | --- | --- | --- | ---: |
| B-27.geriatric-trauma-caution | assign 2 | not a rule (usage) | consider 2 (inferred) | no entry | not a rule (context) | 3 of 3 |
| B-29.pediatric-subtle-ams | assign 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | assign 2 (inferred) | 3 of 4 |
| B-48.unexplained-changes-possible-ingestion-consider | consider 2 | assign 2 (inferred) | assign 2 / consider 2 (inferred) | not a rule (context) | assign 2 (inferred) | 3 of 4 |
| B-52.geriatric-vitals-medication-context-consider | assign 2 | not a rule (usage) | not a rule (context) | no entry | not a rule (context) | 3 of 3 |
| B-53.pediatric-respiratory-distress-signs-consider | assign 2 | not a rule (definition) | not a rule (definition) | no entry | not a rule (definition) | 3 of 3 |
| B-25.pelvis-femur-fracture-consider | consider 2 | consider 2 (inferred) | consider 2 (inferred) | not a rule (context) | no effect | 2 of 4 |
| B-35.severe-psychological-distress-consider | consider 2 | assign 2 | consider 2 (inferred) | assign 2 / consider 2 | assign 2 (inferred) | 2 of 4 |
| B-55.recent-covid-cardiac-risk-consider | assign 2 | no entry | not a rule (context) | no entry | not a rule (context) | 2 of 2 |
| D-04.context-beta-blockers-consider | reassess | not a rule (usage) | not a rule (context) | no entry | no entry | 2 of 2 |
| D-05.context-immunosuppression-consider | reassess | not a rule (usage) | not a rule (context) | no entry | no entry | 2 of 2 |
| A-03.apneic | assign 1 | assign 1 | assign 1 (inferred) | not a rule (definition) | no entry | 1 of 3 |
| A-04.pulseless | assign 1 | assign 1 | assign 1 (inferred) | not a rule (definition) | no entry | 1 of 3 |
| A-15.intubated | assign 1 | assign 1 | assign 1 (inferred) | not a rule (definition) | no entry | 1 of 3 |
| A-16.profound-hypotension | assign 1 | assign 1 | assign 1 (inferred) | not a rule (definition) | no entry | 1 of 3 |
| B-16.button-battery-or-magnet-ingestion | assign 2 | assign 2 (inferred) | assign 2 (inferred) | consider 2 (inferred) | assign 2 (inferred) | 1 of 4 |
| B-21.abdo-pain-vaginal-bleeding | consider 2 | consider 2 (inferred) | not a rule (context) | no entry | consider 2 (inferred) | 1 of 3 |
| B-24.extremity-neurovascular-compromise | assign 2 | assign 2 (inferred) | assign 2 (inferred) | not a rule (context) | assign 2 (inferred) | 1 of 4 |
| B-26.suspected-toxic-ingestion | assign 2 | assign 2 (inferred) | assign 2 (inferred) | not a rule (context) | assign 2 (inferred) | 1 of 4 |
| B-28.ocular-high-risk-constellation | consider 2 | no entry | no entry | no entry | not a rule (context) | 1 of 1 |
| B-46.compartment-syndrome-symptoms | assign 2 | assign 2 (inferred) | assign 2 (inferred) | not a rule (context) | assign 2 (inferred) | 1 of 4 |
| B-47.partial-or-complete-amputation | assign 2 | assign 2 (inferred) | assign 2 (inferred) | not a rule (context) | assign 2 (inferred) | 1 of 4 |
| B-50.transplant-list-consider | consider 2 | consider 2 | consider 2 (inferred) | not a rule (context) | consider 2 (inferred) | 1 of 4 |

## Rules where every blind re-extraction with an entry agrees

| rule | ours | opus | fable | gpt | gemini |
| --- | --- | --- | --- | --- | --- |
| A-01.unresponsive | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-02.arrest-or-imminent | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-05.severe-respiratory-distress | assign 1 | assign 1 | assign 1 | assign 1 | assign 1 |
| A-06.occluded-airway | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-07.active-seizure | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | no entry |
| A-08.spo2-below-90-with-compromise | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-09.anaphylaxis | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-10.hypotension-with-hypoperfusion | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-11.hypoglycemia | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-12.severe-brady-or-tachycardia | assign 1 | assign 1 (inferred) | assign 1 (inferred) | assign 1 (inferred) | assign 1 |
| A-13.flaccid-infant | assign 1 | assign 1 (inferred) | assign 1 | assign 1 (inferred) | assign 1 |
| A-14.penetrating-trauma-unstable | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-17.chest-pain-unstable-lifesaving | assign 1 | assign 1 | assign 1 | assign 1 | assign 1 |
| A-18.pregnancy-hemodynamic-instability-lifesaving | assign 1 | assign 1 | assign 1 (inferred) | no entry | assign 1 |
| A-19.ineffective-tissue-perfusion | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-20.ineffective-respiratory-pattern | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| A-21.impaired-gas-exchange | assign 1 | assign 1 | assign 1 | assign 1 (inferred) | assign 1 |
| B-01.new-altered-mental-status | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-02.severe-pain-consider | consider 2 | assign 2 / consider 2 | consider 2 | assign 2 / consider 2 | consider 2 |
| B-03.severe-pain-systemic-cause | assign 2 | assign 2 | assign 2 (inferred) | no entry | assign 2 |
| B-04.chest-pain-acs-suspect | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-05.stroke-signs | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-06.possible-ectopic-stable | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-07.immunocompromised-fever | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-08.transplant-fever-or-infection | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 (inferred) |
| B-09.suicidal-or-homicidal | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-10.needle-stick-hcw | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-11.sexual-assault | assign 2 | assign 2 | assign 2 / consider 2 | assign 2 | assign 2 |
| B-12.increasing-respiratory-effort | assign 2 | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-13.postpartum-hemorrhage | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-14.stridor-or-secretions | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-15.high-risk-epistaxis | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 | assign 2 |
| B-17.abdo-pain-pregnant-or-postpartum | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | consider 2 |
| B-18.abdo-pain-sepsis-or-hypoperfusion | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | consider 2 |
| B-19.abdo-pain-trauma | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | consider 2 |
| B-20.abdo-pain-refractory-constant-maximal | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | consider 2 |
| B-22.fall-from-6-metres-or-more | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-23.penetrating-trauma-stable | consider 2 | consider 2 (inferred) | consider 2 (inferred) | no entry | consider 2 |
| B-30.anticoagulated-trauma | assign 2 | no entry | no entry | no entry | no entry |
| B-31.post-ictal | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-32.thunderclap-headache | assign 2 | no entry | assign 2 (inferred) | no entry | assign 2 (inferred) |
| B-33.headache-with-neck-pain-or-nuchal-rigidity | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) | assign 2 (inferred) |
| B-34.headache-red-flags | assign 2 | no entry | assign 2 (inferred) | assign 2 | assign 2 |
| B-36.abnormal-ecg-chest-pain | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-37.pregnant-postpartum-sbp-out-of-range | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | assign 2 | no entry | assign 2 | no entry | no entry |
| B-39.pregnant-heavy-bleeding-abnormal-vitals-infection | assign 2 | assign 2 (inferred) | assign 2 (inferred) | assign 2 | assign 2 |
| B-41.testicular-or-scrotal-pain-torsion-consider | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | no entry |
| B-42.unilateral-lower-quadrant-pain-torsion-or-ectopic-consider | consider 2 | consider 2 (inferred) | consider 2 (inferred) | consider 2 (inferred) | no entry |
| B-43.uti-elderly-or-urosepsis-signs | assign 2 | assign 2 | assign 2 (inferred) | no entry | no entry |
| B-44.vehicle-ejection | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-45.mechanical-extrication | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-49.severe-flank-pain | assign 2 | assign 2 | assign 2 | assign 2 | no entry |
| B-51.psychotic-or-violent | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-54.respiratory-distress-signs-consider | consider 2 | consider 2 | consider 2 | consider 2 | consider 2 |
| B-56.infant-under-28-days-fever | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-57.infant-under-90-days-temperature-over-38 | assign 2 | assign 2 | assign 2 | assign 2 | assign 2 |
| B-58.infant-1-to-3-months-fever-consider | consider 2 | consider 2 | consider 2 (inferred) | consider 2 | consider 2 |
| B-59.child-over-3-months-fever-consider | consider 2 | no entry | consider 2 | consider 2 | consider 2 |
| B-60.child-hypothermia-under-36-consider | consider 2 | consider 2 (inferred) | consider 2 (inferred) | no entry | consider 2 (inferred) |
| B-61.child-over-3-months-temperature-red-flag-consider | consider 2 | consider 2 (inferred) | consider 2 (inferred) | no entry | consider 2 (inferred) |
| D-01.adult-danger-zone | reassess | assign 2 / reassess | reassess | reassess | reassess |
| D-02.pediatric-danger-zone-under-1-month | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-06.pediatric-danger-zone-1-to-12-months | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-07.pediatric-danger-zone-1-to-3-years | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-08.pediatric-danger-zone-3-to-5-years | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-09.pediatric-danger-zone-5-to-12-years | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-10.pediatric-danger-zone-12-to-18-years | reassess | reassess | reassess (inferred) | reassess | reassess |
| D-11.spo2-below-92-any-age | reassess | reassess | reassess | no entry | reassess |
| A-22.requires-lifesaving-intervention | assign 1 | assign 1 | assign 1 | assign 1 | assign 1 |

## Sentences two or more blind re-extractions made a rule of, with no statement of ours

| page | re-extractions | effects | quote |
| ---: | --- | --- | --- |
| 6 | opus, fable, gpt, gemini | opus: assign 2; fable: assign 2; gpt: assign 2; gemini: assign 2 | High-risk situation? |
| 5 | opus, fable, gemini | opus: assign 2; fable: assign 2; gemini: assign 2 | Decision point B is used to determine whether the patient is likely to deteriorate and/or require more immediate care |
| 5 | opus, gpt, gemini | opus: resources; gpt: resources; gemini: resources | None One Many |
| 6 | opus, gpt, gemini | opus: assign 1; gpt: assign 1; gemini: assign 1 | Requires immediate lifesaving intervention? |
| 6 | opus, fable, gemini | opus: reassess; fable: reassess; gemini: reassess | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| 9 | fable, gpt, gemini | fable: assign 1; gpt: assign 1; gemini: assign 1 | When these signs are present, the patient is assigned an ESI level of 1 |
| 11 | opus, fable, gpt | opus: assign 2; fable: consider 2; gpt: assign 2 | Severe pain/distress? |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Behavioral outbursts at triage |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Combativeness |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Survivor of sexual violence |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Acute grief reaction |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Suicidal ideation, plan, or attempt |
| 12 | opus, fable, gemini | opus: assign 2; fable: consider 2; gemini: assign 2 | Prenatal loss |
| 14 | opus, gpt, gemini | opus: assign 2; gpt: assign 2; gemini: assign 2 | Pregnant patients with chest pain and/or shortness of breath, abdominal pain, or headache |
| 19 | opus, gpt, gemini | opus: resources; gpt: resources; gemini: assign_level_3 | Patients who require two or more resources are assigned level 3 |
| 5 | opus, gemini | opus: assign 2; gemini: assign 2 | High risk-confused/distress? |
| 5 | opus, gemini | opus: reassess; gemini: reassess | High-risk vital signs? |
| 5 | gpt, gemini | gpt: resources; gemini: resources | ESI levels 3, 4, and 5 are based on how many resources the nurse anticipates will be used |
| 5 | gpt, gemini | gpt: reassess; gemini: reassess | reassess the acuity decision, potentially resulting in assignment of a higher acuity level as appropriate |
| 6 | opus, gpt | opus: assign 2; gpt: assign 2 | Confused/lethargic/disoriented? |
| 6 | opus, gemini | opus: reassess; gemini: reassess | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| 6 | opus, fable | opus: consider 2; fable: consider 2 | Incomplete immunizations |
| 6 | opus, fable | opus: consider 2; fable: consider 2 | No obvious source of fever |
| 6 | gpt, gemini | gpt: resources; gemini: resources | How many different resources are needed? |
| 11 | opus, gpt | opus: assign 2; gpt: assign 2 | Confused/lethargic/disoriented? |
| 11 | opus, fable | opus: assign 2; fable: consider 2 | Is the situation high-risk? |
| 11 | opus, fable | opus: assign 2; fable: consider 2 | Is the patient likely to deteriorate? |
| 11 | opus, fable | opus: assign 2; fable: consider 2 | Does the patient have an acute change in mental status? |
| 12 | opus, fable | opus: assign 2; fable: assign 2 | AMS is a high-risk complaint |
| 13 | opus, fable | opus: assign 2; fable: assign 2 | The high-risk patient is one who is currently ventilating and oxygenating adequately but is in respiratory distress and has the potential to rapidly d |
| 15 | gpt, gemini | gpt: assign 2; gemini: assign 2 | Mechanisms of injury that warrant an ESI 2 designation include falls of 20 feet (6 meters) or more |
| 20 | gpt, gemini | gpt: resources; gemini: assign_level_5 | If that is the case the patient would be an ESI level 5 |
| 23 | opus, gemini | opus: reassess; gemini: reassess | SpO2 < 92% |
| 24 | opus, fable | opus: assign 2; fable: consider 2 | < 90 days > 38°C (100.4°F) or < 36°C (96.8°F) |
| 29 | opus, gemini | opus: assign 1; gemini: assign 1 | Requires immediate lifesaving intervention? |
| 29 | opus, gemini | opus: assign 2; gemini: assign 2 | High-risk situation? |
| 29 | opus, gemini | opus: reassess; gemini: reassess | SpO2 < 92% |
| 30 | opus, gemini | opus: assign 1; gemini: assign 1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe respiratory di |
| 30 | opus, gemini | opus: reassess; gemini: reassess | Reassess to determine whether the patient warrants a higher acuity level if a patient has one or more vital signs outside the normal parameters for th |
| 30 | opus, gemini | opus: assign 2; gemini: assign 2 | 1-28 days of age: Assign at least ESI 2 if T > 38° C |
| 30 | opus, gemini | opus: consider 2; gemini: consider 2 | 1-3 months: Consider assigning ESI 2 if T > 38 ° C |
| 30 | opus, gemini | opus: consider 2; gemini: consider 2 | T > 39°C (102.2°F) or < 36°C (96.8°F) |
