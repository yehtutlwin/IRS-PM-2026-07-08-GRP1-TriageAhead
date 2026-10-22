# Number 1: encoding fidelity, core and extended sets

187 handbook cases: 174 core (both editions give the same answer), 11 extended (`edition_differs`), 2 skipped (decided on vital signs). A case passes when the engine's output matches the book's level as the test expects it.

## Core set

| book's level | cases | pass | fail |
| --- | ---: | ---: | ---: |
| 1 | 29 | 29 | 0 |
| 2 | 51 | 33 | 18 |
| 3, 4 or 5 | 94 | 92 | 2 |
| all | 174 | 154 | 20 |

**Core result: 154 of 174 (89%) pass.** Failing cases:

- ch9-83 (book 3): 27F migraine 2 days, '20/10' pain, vomited twice. As case 20: the August entry carried no complaint category; with the book's facts (a migraine, vomiting) rule B-34 assigns level 2 where the book rates a known migraine as level 3. For the clinician read.
- ch9-20 (book 3): 37F migraine since morning, vomiting, pain 6/10. Found when the case was completed (10 Oct 2026): with the vomiting the book states, rule B-34 fires (the fifth edition's sentence assigns level 2 to 'headache plus fever, vomiting, lower back pain, altered mental status, and/or signs and symptoms of stroke'), while the book rates a known migraine with vomiting as level 3. A literal sentence against the book's own practice; for the clinician read.
- ch10A-22 (book 2): 14M snowboard vs tree, LUQ abdominal pain, femur appears broken. Since 5 Oct 2026 B-19 (abdominal pain after trauma) is a consider flag: the handbook lists it as a question for the nurse, not an assignment (four blind re-extractions agree). The engine shows consider flags B-19 and B-25 and no floor; the book's level 2 is the nurse's judgement on them.
- ch9-6 (book 2): 32F shortness of breath for hours, smoker on the pill, RR 32, SpO2 93%. The book's level 2 is a judgement: new shortness of breath in a smoker on the contraceptive pill, pulmonary embolus to be ruled out, with signs of respiratory distress. The fifth edition has no sentence for this picture; its signs of respiratory distress are a consider flag (B-54), not a floor.
- ch9-35 (book 2): 54F chronic renal failure, missed dialysis yesterday because too weak, normal vitals. The book's level 2 is a judgement: a dialysis patient who misses a treatment risks hyperkalaemia. No fifth-edition sentence covers it.
- ch9-41 (book 2): 19M tall thin smoker, coughing fit then short of breath; RR 36, SpO2 92%, HR 102. The book's level 2 is the picture of a spontaneous pneumothorax with a raised breathing rate and low oxygen. The fifth edition's signs of respiratory distress are a consider flag (B-54); SpO2 92% is decision point D.
- ch9-53 (book 2): 23F 5 weeks postpartum, exhausted, breathless on the stairs, swollen ankles. The book's level 2 is peripartum cardiomyopathy, a judgement. The fifth edition's sentence behind B-38 says 'pregnant patients with chest pain and/or shortness of breath' and does not name the postpartum weeks; since the pregnant/postpartum split (10 Oct 2026) B-38 reads history.pregnant alone, so this case no longer fires it. Recorded for the clinician read: whether postpartum breathlessness belongs under B-38.
- ch9-58 (book 2): man whose internal defibrillator shocked him at breakfast, cardiac history, medications changed days ago, normal vitals. The book's level 2 is a judgement: an implanted defibrillator that fired must be evaluated. No fifth-edition sentence covers it.
- ch9-74 (book 2): 19F throat on fire for days, can barely swallow, voice changed, swelling on one side of the throat; T 38.7, RR 24. The book's level 2 is a possible peritonsillar abscess with a threatened airway, a judgement. The fifth edition's airway sentence (B-14) needs drooling or inability to manage secretions, or stridor, which the case does not state.
- ch9-79 (book 2): young man shot, two wounds in the left leg, heard three shots, alert, normal vitals. The book's level 2 rests on a possible third wound and a possibly injured vessel. The fifth edition's penetrating-trauma sentence (B-23) covers the head, neck, chest and abdomen, not a limb.
- ch9-80 (book 2): 82F excruciating generalised abdominal pain 10/10 and vomiting for hours, previous heart attack; RR 28, HR 102. The book's level 2 is high risk plus severe pain in an elderly patient, a judgement. The fifth edition's severe-pain sentence is 'consider' (B-02); abdominal pain alone has no assigning sentence.
- ch9-88 (book 2): 73M dishevelled, drinking vodka on the kerb, 4 cm forehead laceration oozing, oriented, GCS 14. The book's level 2 is a judgement: an unclear mechanism (fall? assault?), age and alcohol. The fifth edition's trauma sentences need a known mechanism; none is stated.
- ch9-96 (book 2): 28M shellfish allergy, throat started to close, used his EpiPen, now feels okay; HR 108. The book's level 2 is an allergic reaction treated before arrival that may recur. The fifth edition names anaphylaxis itself (A-09, a clinician's finding) and nothing for a treated reaction. Same gap as Appendix A chapter 6 question 4.
- ch9-99 (book 2): 44F diabetic, vomiting 5 hours, no food or insulin, retching; HR 126, RR 24. The book's level 2 is the risk of diabetic ketoacidosis with a raised heart and breathing rate, a judgement; the vital signs are decision point D. No fifth-edition sentence covers it.
- ch10A-6 (book 2): boy with a cold and cough, new rash on face and chest with petechiae, sent in by his pediatrician. The book's level 2 is petechiae as a possible sign of meningococcal infection, a judgement the fifth edition does not state as a rule (it names petechial rash only in the isolation prompt). Recorded for the clinician read.
- ch10A-12 (book 2): 8M losing weight, cranky, up every hour to urinate, cannot drink enough; RR 30, HR 98, BP 92/78. The book's level 2 is the picture of diabetic ketoacidosis (polyuria, polydipsia, weight loss) with raised rates, a judgement; the vital signs are decision point D. No fifth-edition sentence covers it.
- ch10B-23 (book 2): 48M arrested for public intoxication, restless and tremulous after a night in jail; BP 172/124, HR 122. The book's level 2 is alcohol withdrawal (restless, tremulous, tachycardic, hypertensive), a judgement; the vital signs are decision point D. No fifth-edition sentence covers withdrawal.
- appA-ch3-q10 (book 2): 28M construction worker, concrete dust in the right eye, irrigated without relief, eye red, tearing, keeps rubbing it (alkaline burn). B-28 is a consider flag by our operationalisation (effect_override), so it never sets a floor; the book rates an alkaline eye exposure level 2. ATSO elements present: red eye and eye trauma (eye.red, eye.injury) -> count 2 by bridge BR-28, so the flag fires. The book's reason (alkaline chemistry) is not an ATSO element. Clinician review: chemical eye exposure as a floor.
- appA-ch5-q4 (book 2): 94M epigastric pain, vomiting, 'looks sick', HR 100, BP 130/80, SpO2 93%; book: 3 by resources, 2 because ill-appearing and 94. Gap: the book's level 2 rests on general appearance ('looks sick', probable dehydration) in a 94-year-old; no rule encodes ill appearance short of hypoperfusion or sepsis signs. The geriatric consider flag (B-52) is all the rulebook offers. Clinician review.
- appA-ch6-q4 (book 2): 10yo facial swelling and fine red rash after a cookie at school, peanut allergy, wheeze on auscultation, RR 16, HR 76, SpO2 97%. Gap or judgement: the book rates a stable allergic reaction with wheeze and facial swelling as high risk (2). The fifth edition names only anaphylaxis (level 1, A-09); there is no allergic-reaction criterion short of it. Whether this presentation already counts as anaphylaxis is a clinical judgement. Clinician review; the respiratory-signs consider flag (B-54) is what the rulebook shows.

## Extended set (the fifth edition differs)

Judged by the fourth edition's answer the engine passes where the test expects the fifth edition's reading; judged by the fifth edition every case behaves as its note says.

| case | book (4th) | 5th edition | test expects | passes |
| --- | ---: | --- | --- | --- |
| ch9-11 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |
| ch9-27 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |
| ch9-31 | 3 | 2 | floor2 | yes |
| ch9-32 | 3 | 2 | floor2 | yes |
| ch9-57 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |
| appA-ch2-q2 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |
| appA-ch2-q5 | 2 | see note | none | yes |
| appA-ch3-q9 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |
| appA-ch3-q11 | 2 | see note | none | yes |
| appA-ch4-q7 | 3 | see note | floor2 | yes |
| appA-ch5-q6 | 2 | no such criterion | floor2 | no (fourth-edition answer only) |

Extended cases, in words:

- ch9-11: 4F fell 4 feet off the jungle gym, hit her head, unconscious a couple of minutes, now crying; HR 162, RR 38. The book's level 2 rests on a witnessed fall with loss of consciousness in a child. The fifth edition has no head-injury or loss-of-consciousness criterion; the vital signs are decision point D.
- ch9-27: 17M restrained driver, high-speed crash, abdominal pain, arm lacerations; BP 102/60, HR 86, RR 28. The book's level 2 is the mechanism of injury (high-speed crash). The fifth edition's mechanism list is numeric (a fall of 6 metres or more, ejection, mechanical extrication) and names no speed; abdominal pain after trauma is a consider flag (B-19). Set 2 case (trauma mechanism changed between editions).
- ch9-31: middle-aged man, table saw, lost a couple of fingertips, bleeding controlled, pain 6/10. Set 2: the fifth edition lists partial or complete amputation as high risk (p.15, rule B-47), so the level re-derived under v5 is 2; the fourth edition's answer (3, two resources) stands for v4.
- ch9-32: 27F low abdominal pain 4 days, spotting today, last period 7 weeks ago, previous ectopic, stable. Set 2: the fifth edition's high-risk examples include 'a possible ectopic pregnancy, hemodynamically stable' (p.12, rule B-06); the fourth edition rated this 3 with ectopic on the differential. Re-derived under v5: 2.
- ch9-57: restrained SUV driver in a high-speed multicar crash, right thigh pain, hand laceration, knee abrasion, stable. The book's level 2 is the mechanism of injury alone. The fifth edition's mechanism list is numeric and names no speed (Set 2, as case 27).
- appA-ch2-q2: 53yo with 30% body-surface-area burn. v4-only: the fifth edition never mentions burns (0 occurrences), and criteria.yaml has no burn rule. Clinician review: whether a major burn should be a supplemented high-risk rule.
- appA-ch2-q5: 45yo in a high-speed motor vehicle collision, BP 120/60 HR 72 RR 18. v4's answer rests on its qualitative mechanism rule (high-speed MVC). The fifth edition (p.21) lists numeric mechanisms only: falls >= 6 m, ejection, mechanical extrication, sexual assault. None is stated here, so under v5 no A/B rule fires; age 45 is below the geriatric consider. Re-derived expectation: no floor. Flagged for clinician review with cases 27 and 57 of chapter 9.
- appA-ch3-q9: 28M struck on the head with a baseball bat, passed out for a couple of minutes, headache, neck pain, vomited once, now alert (epidural haematoma). v4-only: the fifth edition has no head-injury or loss-of-consciousness criterion (0 occurrences) and criteria.yaml has none. The interview does record E.loc. Clinician review: blunt head injury with loss of consciousness as a supplemented rule (the anticoagulant rule B-30 covers only anticoagulated patients).
- appA-ch3-q11: 40M fell about 10 feet (3 m) from a ladder onto both feet, foot and back pain 6/10, pale and slightly diaphoretic, no LOC. v4's answer rests on mechanism (lumbar and calcaneus fractures). The fifth edition's numeric threshold is 6 m (p.21); 3 m does not reach it, and pale/diaphoretic without hypotension is not A-10. Re-derived expectation under v5: no floor. Flagged for clinician review with chapter 2 case 5.
- appA-ch4-q7: 30F sexually active, no contraception, vaginal bleeding and cramping, dizzy and pale; book: 'at least two resources, level 3'. The question is about resources and the v4 answer is 3. The fifth edition (p.12) lists 'a possible ectopic pregnancy, hemodynamically stable' as level 2 (B-06), and the diff log tags the OB/GYN framing CHANGED. Re-derived under v5: floor at least 2. possible_ectopic_pregnancy is a judgement field, set on: sexually active, no contraception, bleeding with cramping, dizzy.
- appA-ch5-q6: 9yo collided with another player at lacrosse, loss of consciousness about 5 minutes witnessed by the coach, now awake with headache and nausea. v4-only: as chapter 3 case 9, no head-injury or loss-of-consciousness criterion in the fifth edition or in criteria.yaml. Clinician review.

## Skipped

- appA-ch5-q3: Decided at decision point D: the book up-triages from 3 to 2 on danger-zone vitals (SpO2 91%, RR 30). The engine's D point is pending.
- appA-ch5-q5: Decided at decision point D: the book up-triages from 3 to 2 on danger-zone vitals (HR 112, RR 28, SpO2 91%). The engine's D point is pending. Steroid dependence is the D-05 context flag.
