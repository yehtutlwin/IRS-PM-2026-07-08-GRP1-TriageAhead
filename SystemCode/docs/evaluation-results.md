# Evaluation results

This document reports the six measurements defined in the team's evaluation plan, with results as of
15 October 2026, and for numbers 2 and 4 also the runs of 18 and 19 October 2026 on the sets of 25 and then 27 personas. Each measurement is presented in the same form: the question it answers, the method, the results, a
discussion, and the limitations. Every figure is produced by a script or test in the repository, and the file that holds
it is linked where the figure is first given.

## Terms used in this document

| Term | Meaning |
| --- | --- |
| The builder | The team member who wrote the system and the first persona answer sheets; "a teammate" is any other member. |
| Task G, H, I | The names of the experiment scripts and their outputs: `task_g_*` run the rules over the Yale record (number 6), `task_h_*` train the comparator classifier (number 5), `task_i_harness.py` plays the personas through the interview (numbers 2 and 4). |
| Rule engine | The deterministic component that applies the handbook rules in `rules/criteria.yaml` to the facts collected. It produces at most an urgency floor; it never assigns a triage level. |
| Urgency floor | The engine's output: "at least ESI-2" when a high-risk rule fires, an ESI-1 indicator when a life-threat rule fires, or no claim. ESI is the Emergency Severity Index, the five-level triage scale of the handbook. |
| Claim | Any run in which the engine produced a floor or an ESI-1 indicator. |
| Engine miss rate | The share of cases or visits rated level 1 or 2 by the reference for which the engine made no claim. The engine is silent in these cases; it does not give a wrong level. |
| Model under-triage | A language model, asked to assign a level directly, naming a level of lower acuity than the reference. |
| Fact extraction | The step in which a language model turns a caregiver's answer into values of the fields defined in `rules/fields.yaml`. |
| Persona | A scripted patient case used to test the interview. Each persona has an answer sheet, the list of facts the caregiver knows, and an expected floor. In the runs of 15 October a language model answered the interview's questions from the answer sheet (the persona player); since 16 October the answer-sheet player replies with the sheet's own sentence for each field asked, with no model. |
| Fact capture | The share of answer-sheet facts found in the fact store after an interview. |
| Re-ask | A question the interview had to ask a second time because the first answer did not yield the fact. |
| Danger-sign screen | The interview's opening questions on responsiveness, chest pain, breathing and bleeding. |
| Handbook | The ESI Implementation Handbook. The rules are built from the fifth edition (2023); the worked cases used as tests are from the fourth edition (2012). |
| Yale record | A public data set of 558,029 emergency department visits at one hospital system, with the triage nurse's ESI level recorded for each visit. |
| Classifier | A statistical model (here gradient-boosted decision trees) trained on past visits to estimate, from a visit's recorded features, how likely the visit was to be rated level 1 or 2. It is the report's advisory second lane and never changes the floor. |
| AUROC | Area under the receiver operating characteristic curve: the probability that the classifier ranks a randomly chosen level 1 or 2 visit above a randomly chosen level 3 to 5 visit. 0.5 is chance; 1.0 is perfect separation. |
| Calibration | Agreement between the probability the classifier states and the share of visits that were in fact level 1 or 2 among visits given that probability. |
| Weighted kappa | Agreement between two five-level ratings beyond chance, with disagreement by one level counted as less severe than by two or more. 0 is chance agreement; 1 is perfect. |

## Summary of results

| No. | Question | Principal result | Status |
| --- | --- | --- | --- |
| 1 | Are the rules a faithful translation of the handbook? | 154 of 174 handbook cases pass (89%); no level-1 case is missed | complete |
| 2 | Does the interview capture what the caregiver said? | 94% of the facts the field schema can hold on the builder's ten personas, with a deterministic caregiver; 88% on the final set of 27 (148 of 169 facts outside the three personas tagged synthetic; 159 of 196, 81%, in all); repeat runs capture the identical facts and reach the identical floor | complete; graded wording and text-similarity scoring not built |
| 3 | What does a language model deciding the level directly cost? | model under-triage in 14% of runs from structured facts and 39% from printed text; the engine never names a lower level | complete |
| 4 | Does the whole interview reach the right floor? | our interview: 20 of 27 personas on the final set (22 of 25 on the set of 18 October, 9 of 10 on the builder's ten), the report ready after 12 questions; a language model running its own interview: 10 of 27 with the handbook, 13 of 27 with the handbook and our rules (a form that varies between runs: 11 to 14 of 25 over four runs on the earlier set) | complete; graded runs not done; the model's rules form varies between runs with identical inputs |
| 5 | How good is the learned signal? | AUROC 0.71 from pre-arrival facts, 0.89 once vital signs are known | complete; four refinements not run |
| 6 | How often is the floor stricter than the nurse's level? | 17% of claims, an upper bound | complete |

Three qualifications apply to every result and should accompany any quotation of it.

1. The final set of 27 personas mixes sources: 8 from Yale visits with the triage nurse's level and 6 from ESI handbook practice cases with the book's answer, both written by the builder; 9 written by teammates (invented cases with the handbook page cited, taken exactly as the teammates wrote them); and 4 synthetic cases of the builder's own judgement ([experiments/persona_selection.md](../experiments/persona_selection.md)). The builder's own sentences are spoken in 18 of the 27. Where a teammate's sheet tested the same rule as a builder sheet, the teammate's replaced it. Three of the four synthetic cases (acute gout, heat stroke, decompensated liver disease) are tagged synthetic in the persona file, and the figures "outside the synthetic personas" exclude exactly those three; the fourth, breathlessness without pain, carries no tag and is counted.
2. Variation between repeated runs of the same configuration is one or two facts, with the floor unchanged (number 2, consistency). A difference of one fact between two configurations is therefore not meaningful.
3. The nurse's level in the Yale record is a comparator, not a reference standard. The handbook is the reference for the rules; the record describes practice at one site.

## 1. Encoding fidelity

### Question

Do the rules in `rules/criteria.yaml` say what the handbook says?

### Method

All 187 worked cases of the fourth-edition handbook (the 100 practice cases of chapter 9, the two competency sets of
chapter 10, and the 37 cases of Appendix A) were transcribed as tests, each with the facts the book states and the level
given in the book's answer key ([tests/v4_cases.yaml](../tests/v4_cases.yaml), [tests/v4_posttest_cases.yaml](../tests/v4_posttest_cases.yaml)). A second, independent transcription of the printed
cases by another language model was reconciled with the first.

The book's answer is the reference. A case passes when the engine's output matches what that answer implies: an ESI-1
indicator for a level 1 case, a floor of at least 2 for a level 2 case decided on risk, and no claim for a case decided on
resources or vital signs. Two cases decided on vital signs are excluded, since the engine has no vital signs before arrival.

Because the cases are from the fourth edition and the rules from the fifth, the cases are reported in two sets. The
**core set** holds the 174 cases whose answer is the same under both editions; it is the measure of the rules. The
**extended set** holds the 11 cases, marked `edition_differs` in the test files, whose answer rests on a criterion the fifth
edition changed or removed. The full case lists are in [experiments/out/number1-encoding-fidelity.md](../experiments/out/number1-encoding-fidelity.md), produced by
[experiments/number1_report.py](../experiments/number1_report.py); the same cases run as part of the test suite.

### Results

Core set, by the level in the book's answer:

| Book's level | Cases | Pass | Fail |
| --- | ---: | ---: | ---: |
| 1 | 29 | 29 | 0 |
| 2 | 51 | 33 | 18 |
| 3, 4 or 5 | 94 | 92 | 2 |
| All | 174 | 154 | 20 |

Extended set: all 11 cases behave as the fifth edition prescribes. Five pass because the test expects the fifth edition's
reading; six fail the fourth edition's answer because the fifth edition has no corresponding criterion.

The 20 failures in the core set fall into two kinds:

| Kind | Cases | Example | Reason the rules are silent |
| --- | ---: | --- | --- |
| The book's clinical judgement, with no handbook sentence behind it | 16 | a dialysis patient who missed a treatment; an implanted defibrillator that discharged | a rule states only what a handbook sentence states (a design decision) |
| Our reading of a sentence's effect | 4 | a known migraine with vomiting, which the headache rule rates level 2 and the book rates 3 | the literal sentence conflicts with the book's own practice; referred to the clinician review |

### Discussion

The rules miss no level 1 case and over-call in two of 94 lower-level cases. Every failure is a case in which the book
reasons beyond its own text. The sixteen judgement cases are the material for a future class of rules derived from the
book's answers rather than its sentences (provenance `supplemented`; future work). Two conditions
attach to that plan: a rule derived from a case cannot be scored on that case, so such rules would need cases the
derivation never saw; and each is a clinical generalisation from a single example, which the clinician review must confirm.

### Limitations

The test feeds facts directly to the engine. The separate reachability check asks whether the interview could have asked
for each fact: 147 of 185 cases are fully reachable, and 30 facts are never opened by any trigger
([reachability.md](../experiments/out/reachability.md)).

## 2. Fact capture

### Question

Does the interview store what the caregiver said?

### Method

Twenty-seven personas are defined in [prototype/personas.yaml](../prototype/personas.yaml), each with an answer sheet: 8 from Yale visits with the nurse's level and 6 from handbook practice cases with the book's answer, written by the builder; 9 written by teammates on 19 October, exactly as posted; and 4 synthetic. The earlier sets were the builder's ten of 15 to 16 October and a set of 25 on 18 October ([experiments/persona_selection.md](../experiments/persona_selection.md)). The harness
[experiments/task_i_harness.py](../experiments/task_i_harness.py) conducts each interview through the web application with a persona player, then checks each
answer-sheet fact against the fact store. The index of all runs is [RUNS.md](../experiments/out/RUNS.md).

Three configurations were run: all ten personas with the local model (gemma4:12b) as interview model and persona player;
the five most demanding personas with the local model and with Claude Opus 5.5 as interview model, in both cases with the
local model as persona player at temperature 0, so that only the interview model differs
([comparison](../experiments/out/interview-v2-backends.md)); and the same five personas three times with the local model, to measure consistency. On 16 October the same runs were repeated with a
**deterministic persona player**: each persona carries one sentence per field (`say`), and the harness answers each question with the
sentences of the fields the server reports as asked, or "I don't know", with no model. Repeat runs with this player measure fact
extraction alone.

### Results

| Configuration | Facts captured | Run report |
| --- | ---: | --- |
| Ten personas, local model | 54 of 71 (76%) | [report](../experiments/out/task-i-20261015-0031-v2i-interview-v2-dynamic.md) |
| The eight personas whose facts the schema holds | 47 of 51 (92%) | same run |
| Five personas, local interview model | 30 of 35 | [report](../experiments/out/task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0.md) |
| Five personas, Claude Opus 5.5 interview model | 29 of 35 | [report](../experiments/out/task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0.md) |
| Five personas, three repeats, local model | 31, 30 and 30 of 35 | [report](../experiments/out/task-i-20261015-1817-v2o-consistency-3-runs-local.md) |
| Ten personas, deterministic persona player | 55 of 72 (76%); 49 of 52 (94%) on the eight the schema holds | [report](../experiments/out/task-i-20261016-0117-v2r-sheet-player-local-interview-t0.md) |
| Five personas, three repeats, deterministic persona player | 32 of 36 in each of the three runs, the same facts every time | [report](../experiments/out/task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0.md) |
| Twenty personas, three runs on 18 October (the first before two fixes the run itself found) | 106 of 129, 109 of 131, 108 of 131 | [first](../experiments/out/task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0.md), [second](../experiments/out/task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0.md), [third](../experiments/out/task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0.md) |
| Twenty-five personas, deterministic persona player, 18 October, the code as submitted | 133 of 163 (82%); 122 of 136 (90%) without the three synthetic personas | [report](../experiments/out/task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0.md) |
| **The final set of 27**, deterministic persona player, 19 October, the code as submitted | 159 of 196 (81%); 148 of 169 (88%) without the three synthetic personas | [report](../experiments/out/task-i-20261019-1452-v2z-27-personas-final-set-sheet-player-local-t0.md) |

The attainable maximum on the five demanding personas is 33 of 35 (34 of 36 with the deterministic player, whose breathing sheet carries
one fact more), because two facts on the gout persona's sheet have no field in the schema. Consistency by persona:

| Persona | Run 1 | Run 2 | Run 3 | Floor in all three runs |
| --- | ---: | ---: | ---: | --- |
| Fall on an anticoagulant | 9 of 9 | 9 of 9 | 9 of 9 | at least ESI-2 |
| Abdominal pain in pregnancy | 5 of 6 | 5 of 6 | 5 of 6 | at least ESI-2 |
| Resolved stroke symptoms | 6 of 6 | 4 of 6 | 5 of 6 | at least ESI-2 |
| Acute gout | 5 of 7 | 5 of 7 | 5 of 7 | none |
| Breathlessness without pain | 6 of 7 | 7 of 7 | 6 of 7 | at least ESI-2 |

### Discussion

The interview stores about nine in ten of the facts the schema can hold. With the deterministic caregiver the three repeat runs
captured the identical facts and reached the identical floors, so fact extraction itself is stable; the one-or-two-fact variation of
the model-played runs was the player's phrasing. The facts missed are the same in every run, which indicates a limit of the schema or
the interview design rather than random error: a denial of fever was never stored because the fever question was never asked once the floor had settled early (the field lacked a
handover purpose and the after-report filter dropped it; corrected on 16 October, after these runs); two gout
facts have no field; and a fact said inside a general answer is stored as the complaint flag or in a list, not as the field a
rule reads: stroke symptoms in the opening answer, a change in behaviour in the complaint answer, a clotting disorder in the
answer about conditions. On the 25-persona set the misses outside the synthetic personas are 14 of 136, of the
same kinds. The more capable model does not capture more facts; it requires fewer questions,
reported under number 4. Before the redesign of 15 October the ten-persona figure was 70 to 73%.

### Limitations

Two elements of the plan's specification were not implemented, and a third only in part:

- graded variants of each fact's wording (direct, lay, vague, buried in a longer answer, negative, noisy), scored as metamorphic tests; the five terse-answer sessions of 15 October are the available evidence of what terse answers cost: one was played by a team member, two were typed turn by turn by the AI coding agent acting as the caregiver, and two were scripted;
- text-similarity scoring; capture is judged by exact field and value;
- answer sheets written by a team member other than the builder: nine of the final 27 are teammates' sheets, used exactly as written; the earlier drafts posted by teammates could not be run because they lacked an expected floor, the per-field answer lines or the facts in the schema, and the builder did not alter them.

## 3. The rules against a language model deciding directly

### Question

What is lost and gained if a language model assigns the triage level directly, compared with rules that set only a floor?

### Method

Two forms. In the handbook form, the 187 cases of number 1 were given to the local model three times each in two
presentations: as the structured facts the engine receives, and as the printed text of the case. The model's level was
judged against the book's answer by the same criterion as the engine. The model was also asked to cite the handbook page and
a phrase from it; a citation is counted as verifiable only when the phrase is found on that page of the fifth-edition PDF,
the same check applied to every rule in the validator ([number3-handbook.md](../experiments/out/number3-handbook.md), produced by
[number3_handbook.py](../experiments/number3_handbook.py)).

In the Yale form, 200 recorded visits, 40 per level, were described as structured text and given to the same model three
times, with the engine run on the same facts ([task-g-llm-direct.md](../experiments/out/task-g-llm-direct.md)).

### Results

Handbook form, on the 90 cases the book rates level 1 or 2, where both the model and the engine make a claim:

| Measure | Model, structured facts | Model, printed text | Rule engine |
| --- | ---: | ---: | ---: |
| Names the book's level | 85% of runs | 61% of runs | a claim on 60 of 90 cases |
| Model under-triage | 14% of runs | 39% of runs | none |
| Level 1 cases given level 2 | 11 of 87 runs | 42 of 87 runs | 0 of 29 cases |
| Same answer in all three runs | 184 of 187 cases | 182 of 187 cases | all |
| Citation verifiable on the page named | 12% | 2% | every claim |

On the 97 cases the book rates level 3 to 5, the model gave level 1 or 2 in 11% of runs from structured facts and 4% from
printed text. The engine fired on five: three are cases the fifth edition moves to level 2, two are the migraine over-calls
of number 1. The model did not recognise a level 4 case from structured facts in any of 66 runs.

Yale form: the model agreed with the recorded level in 30.5% of runs and was within one level in 68%; it under-triaged 35%
of the visits recorded as level 1 or 2. The engine made a claim on 6.5% of the visits, of which 92.3% were recorded as
level 1 or 2.

### Discussion

Given the same facts, the model names the book's level more often than the engine on the level 1 and 2 cases (76 of 90
cases against 64, by majority of three runs), because it also reasons beyond the handbook's sentences where the engine is
silent. The cost is of a kind the engine never incurs: in one run in seven from structured facts, and two in five from
printed text, the model assigns a lower level than the book to a level 1 or 2 case, and its cited page can rarely be
verified. The engine's 65 claims fall on a level 1 or 2 case in 92% of cases, are identical on every run, and each carries
a page the validator has checked. This is the trade the design makes: coverage against a floor that is never a wrong level
and is always traceable.

### Limitations

Only one model, the local one, was tested. The engine's misses in this comparison are the 20 cases of number 1.

## 4. End-to-end floor

### Question

Does the complete interview, questions, fact extraction and rule engine together, reach the floor the case warrants?

### Method

**Arm A, our interview.** The persona runs of number 2 are judged on the floor and the rule: a run passes when the floor the answer
sheet expects is reached and the expected rule fires. Questions are counted up to the point where the report is ready (the floor is
settled and the QR code shown) and in total, since the interview continues afterwards with questions the nurse reads.

**Arm B, a language model that runs its own interview** ([number4-second-arm.md](../experiments/out/number4-second-arm.md), script
[number4_second_arm.py](../experiments/number4_second_arm.py)). The local model (gemma4:12b, temperature 0, seed 42, a
49,152-token window) asks what it likes, one question a turn, and states its decision, in two forms. *B-handbook*: the model has the
fifth-edition handbook as text and nothing else, and states a level 1 to 5. *B-rules*: the handbook, our rules file rendered as text,
the meaning of each fact name, and our interview constraints (danger signs first, no care advice, no vital signs), and states a floor
as our engine does. The caregiver is the same local model at temperature 0, told to answer only from the persona's answer-sheet
sentences. A run passes when the expected floor is reached (an expected "at least ESI-2" by level 1 or 2 or a floor; an expected no
floor by no floor or level 3 to 5); a run that reaches sixteen questions without a decision is a miss. Before B-rules a retrieval probe
checked that the model could use the 44,000-token prompt: it quoted the conditions of rules from the start, middle and end of the file
and named the right rule for a fall on warfarin, but listed only part of the rules that mention pregnancy; no run's prompt exceeded
the window.

### Results

| Configuration | Expected floor reached | Expected rule fired | Questions to the report (mean) | Questions in total (mean) | Re-asks per interview |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ten personas, local model | 9 of 10 | 8 of 10 | 14 | 22 | 6.4 |
| Five personas, local interview model | 4 of 5 | 5 of 5 | 14.4 | 18 | 5.0 |
| Five personas, Claude Opus 5.5 interview model | 4 of 5 | 5 of 5 | 10.8 | 15.8 | 2.4 |
| Five personas, three repeats, local model | 12 of 15 | 15 of 15 | 14.6 | 18 | 4.9 |
| Ten personas, deterministic persona player | 9 of 10 | 8 of 10 | 11.8 | 15.7 | 2.0 |
| Five personas, three repeats, deterministic persona player | 15 of 15 | 15 of 15 | 12.0 | 15.5 | 2.3 |
| Twenty personas, three runs on 18 October | 18, 18 and 17 of 20 | 16, 17 and 16 of 20 | 11.7 to 12.3 | 15.8 to 16.0 | 2.8 to 3.1 |
| Twenty-five personas, deterministic persona player, 18 October, the code as submitted | 22 of 25 | 21 of 25 | 12.0 | 16.2 | 3.4 |
| **The final set of 27**, deterministic persona player, 19 October, the code as submitted | 20 of 27 | 17 of 27 | 12.2 | 16.5 | 4.2 |

No danger sign was missed in any run. Each persona reached the same floor in all three repeat runs, with either caregiver. The
runs stop each interview after sixteen answers; the real interview continues, so a miss below means the floor was not reached
within sixteen answers. No run raised a floor for a persona that expected none. The only floor other than the expected one, in
every run, is the synthetic heat-stroke persona's: the sheet expects an ESI-1 indicator and the engine states at least ESI-2.

The floors not reached:

| Persona | Configuration | Explanation |
| --- | --- | --- |
| Heat stroke (synthetic) | ten personas | the sheet names facts no field holds and a rule that does not exist |
| Breathlessness without pain | local model runs | the sheet does not state whether the breathing is still worsening; the persona player answered yes, the increasing-effort rule fired, and the sheet expects no floor |
| Acute gout | Claude run | the answer "not feeling like myself because of this pain" was stored as altered mental status and the corresponding rule fired; the field's definition and question were corrected the same day |
| Cast too tight (P13) | first run of 18 October | the limb warning signs were not asked for a limb complaint when the mechanism was unknown (fixed the same day); reached in the later runs except one in which the question fell past the sixteen-answer limit |
| Nosebleed with a clotting disorder (P17) | three of the four runs of 18 October | "He has a blood clotting disorder" was stored in the condition list, not as the field the rule reads; the direct follow-up came as question 17 after the onset and the pain score had each been asked three times |
| Cancer pain (P20) | 25-persona run | the question on the cause of the pain came as question 17, after the danger signs were asked one at a time and the stroke signs first |
| Heat stroke (synthetic) | every run | as above |
| Bleeding eight days after childbirth (ND-P28, a teammate's sheet) | final set | the question on how heavy the bleeding is never came within sixteen answers; the danger-sign "heavy bleeding" does not feed the postpartum bridge |
| Pregnant with a severe headache (ND-P29, a teammate's sheet) | final set | the complaint was filed as "pregnancy related" rather than "headache", and the rule reads the category; every fact was captured |
| Fever on chemotherapy (CH-I29-04, a teammate's sheet) | final set | the sheet's answers of the form "I do not know whether …" exceed the don't-know rule's eight words, so each was asked three times and the immune question never came |
| Sexual assault (CH-I29-08, a teammate's sheet) | final set | the statement in the complaint answer was not stored as the field the rule reads, then re-asks of the same kind as in the fever-on-chemotherapy case used the remaining answers; the same sheet passed on 18 October |

**Arm B results.** Ten personas, one run per form:

| Form | Expected floor reached | Danger signs asked first | Runs with care advice | Decision with a citation | Questions (mean) | No decision within 16 questions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B-handbook: the handbook only | 6 of 10 | 0 of 10 | 0 of 10 | 7 of 10 | 12.5 | 3 |
| B-rules: the handbook, our rules, our constraints | 5 of 10 | 10 of 10 | 0 of 10 | 6 of 10 | 13.0 | 4 |
| Arm A, our interview, same sheets | 9 of 10 | 10 of 10 by construction | 0 of 10 by construction | every claim, with the page verified | 11.8 to the report | 0 |

Of the nine arm B misses, seven ended at the sixteen-question limit with no decision: the model went on asking, most often for vital
signs and oxygen readings the caregiver cannot have, or repeated one question five times (B-rules on the fall persona asked about a
bone sticking out five times and never about medicines, so the anticoagulant was never learned). The other two are the synthetic
heat-stroke persona, which arm A also cannot reach. Where arm B did decide, its decisions carried a page or a rule id, unverified.

**Arm B on the final set of 27** (19 October, one run per form, [dated result file](../experiments/out/number4-second-arm-20261019-27-personas.md)): B-handbook reached the expected floor in 10 of 27 (danger signs first in none, 16 runs with no decision), B-rules in 13 of 27 (danger signs first in all, 13 with no decision), against 20 of 27 for arm A on the same sheets. The 25-persona run that preceded it:

**Arm B on the 25 personas** (18 October, one run per form, [dated result file](../experiments/out/number4-second-arm-20261018-25-personas.md)):

| Form | Expected floor reached | Danger signs asked first | Runs with care advice | Decision with a citation | Questions (mean) | No decision within 16 questions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B-handbook: the handbook only | 10 of 25 | 0 of 25 | 0 of 25 | 11 of 25 | 14.0 | 14 |
| B-rules: the handbook, our rules, our constraints | 11 of 25 | 25 of 25 | 0 of 25 | 12 of 25 | 13.3 | 13 |
| Arm A, our interview, same sheets | 22 of 25 | 25 of 25 by construction | 0 of 25 by construction | every claim, with the page verified | 12.0 to the report | 0 |

Of arm B's 29 misses on the 25, 27 ended at the sixteen-question limit with no decision, 18 of them labelled a missing fact (the
model never collected the fact its own rule needed) and 9 an over-call (it went on asking of a patient who warranted no floor); the
other two are the synthetic heat-stroke persona. **The B-rules form does not repeat.** On the ten personas both runs cover, B-handbook
gave the identical interview on 16 and 18 October, question for question; B-rules gave a different interview in seven of ten with the
same inputs, seed and temperature, and two outcomes changed, one each way. A direct repeat on the same code confirmed it. Three further runs of the B-rules form on the 25 personas with identical inputs, made overnight on 18 to 19 October
([repeat 1](../experiments/out/number4-second-arm-20261018-25-personas-rules-repeat1.md), [2](../experiments/out/number4-second-arm-20261018-25-personas-rules-repeat2.md), [3](../experiments/out/number4-second-arm-20261018-25-personas-rules-repeat3.md)), reached the expected floor in 11, 11 and 14 of 25 against 11 in the first run: **11 to 14 of 25 over four runs**. Eight
personas passed in all four runs, eight failed in all four, and nine changed outcome between runs. The B-handbook figure is a single
run that repeated exactly on the ten personas; the prompt of the B-rules form is about 44,000 tokens against 30,000 for B-handbook.

### Discussion

Our interview reaches the expected floor in every case the schema covers on the builder's ten, in 22 of 25 on the set of 18 October, and
in 20 of 27 on the final set, where the seven misses are the synthetic heat-stroke persona, two personas whose deciding question came
one past the sixteen-answer limit of the run, and four teammate sheets that each exposed a gap in the interview, described in the table above; none of the seven is a wrong floor. The floor does not change between repeat runs of the same persona, whether the caregiver is a model or the answer
sheet itself, except where a run ends at that limit: the twenty personas gave 18, 18 and 17 of 20 in three runs of 18 October. The choice of language model changes the number of questions, not the
destination: Claude Opus 5.5 reaches the report in eleven questions against fourteen for the local model, with half as many re-asks.

The second arm measures what the knowledge engineering and the mechanism are worth. The same model that extracts facts for our
interview, given the whole handbook and left to run the interview itself, reached the expected floor in six cases of ten, never asked
the danger signs first, and in three cases never stopped asking. Given our rules as text and our constraints as instructions, it kept
the constraints (danger signs first in every run, no care advice) but reached the floor in five of ten, because it did not reliably
collect the facts its own rules needed and could not stop. Holding the same knowledge, the deterministic engine applied to extracted
facts reached nine of ten with the report ready after twelve questions. On the 25 personas the same pattern holds: 10 and 11 of 25
for the model's two forms against 22 of 25 for our interview, and on the final 27, 10 and 13 of 27 against 20 of 27, with the model again
unable to stop in about half the runs. The gap
between B-rules and arm A is the mechanism alone; the gap between B-handbook and arm A also includes the knowledge engineering.

### Limitations

One run per persona and form in arm B, with one local model, and the B-rules form gives a different interview on each run with
identical inputs, so its figure can move by a persona or two between runs; a stronger model would likely stop and decide
more often, and the comparison should be read as one model against itself in two roles. The sixteen-answer limit of the harness is a
run setting, not a property of the interview; two of the three arm A misses on the 25 would have been reached on the next question. The plan's graded runs (direct, lay and vague wordings through
both arms) were not made. Arm B's caregiver is a model, since no field list exists to key a deterministic reply to; arm A's is the
answer sheet itself. The terse-answer sessions of 15 October remain the evidence closest to a real caregiver, and only one of them was played by a team member.

## 5. The learned signal

### Question

How well can a classifier trained on past visits estimate, from the facts known before arrival, whether a visit will be
rated level 1 or 2?

### Method

Three classifiers were trained on the same 446,423 Yale visits and tested on the same 111,606 held-out visits. They differ
in their inputs and in what they predict, as the table states. The first is the one the nurse's report uses; the other two
exist only to interpret it.

| Classifier | Inputs | Predicts | Purpose | Report |
| --- | --- | --- | --- | --- |
| A. Pre-arrival classifier | 17 pre-arrival features: age, complaint group, injury mechanism, fever, anticoagulation, immune status | level 1 or 2 against 3 to 5 | the advisory lane shown on the nurse's report | [practice-signal.md](../experiments/out/practice-signal.md) |
| B. Five-level variant of A | the same 17 features | the level, 1 to 5 | to test whether pre-arrival facts can support a level rather than a band | [practice-signal-5level.md](../experiments/out/practice-signal-5level.md) |
| C. Comparator with vital signs | the six triage vital signs, age, sex and 200 complaint flags, as recorded at the triage desk | level 1 or 2 against 3 to 5 | the ceiling the data allows once the patient has been examined; never used in the product | [task-h-learned-comparator.md](../experiments/out/task-h-learned-comparator.md) |

### Results

| Classifier | Result |
| --- | --- |
| A. Pre-arrival classifier | AUROC 0.714. Calibrated within one percentage point in every decile of predicted probability. |
| A, the "high" band the report shows (predicted probability of level 1 or 2 at least 50%) | covers 15% of visits; 66% of those were level 1 or 2; contains 32% of all level 1 and 2 visits |
| B. Five-level variant | weighted kappa 0.39; 66% of the visits recorded as level 1 or 2 were predicted as level 3 to 5 (classifier under-triage) |
| C. Comparator with vital signs | AUROC 0.885 |

### Discussion

Calibration, not discrimination, is what the report relies on: it allows the sentence "an estimated N% of similar past
visits were level 1 or 2" to be true as stated. The high band can corroborate a floor but cannot reassure, since it
contains only a third of the high-acuity visits. The five-level variant shows why the report presents bands and not a level:
two thirds of the high-acuity visits would be placed at level 3 to 5. The difference between 0.714 and 0.885 is the
contribution of vital signs, and the reason no system acting before arrival should claim a level.

### Limitations

One site's record, with the nurse's level as the label. Four refinements in the plan were not run and are future work:
same-profile lookup against gradient boosting, presence-only baselines, and training with realistic gaps
in the facts.

## 6. Floor soundness

### Question

When the rules set a floor on a real visit, how often is it stricter than the level the nurse gave?

### Method

The rule engine was run over 558,029 Yale visits with facts mapped from the record's columns. A claim is a visit where a
floor or an ESI-1 indicator was produced. A claim is consistent when the recorded level is 1 or 2 and stricter when it is
3 to 5 ([task-g-full.md](../experiments/out/task-g-full.md); coverage of the rules by the record's columns in [task-g-coverage.md](../experiments/out/task-g-coverage.md)).

### Results

| Measure | Value |
| --- | ---: |
| Visits with a claim | 2.9% |
| Claims consistent with a recorded level 1 or 2 | 82.7% |
| Claims stricter than the nurse's level | 17.3% |
| Admission rate of the visits with a stricter claim | 25.7% |
| Admission rate of visits at the same levels with no claim | 18.3% |
| Engine miss rate: recorded level 1 and 2 visits with no claim | 92.1% |
| Rules that cannot be evaluated from the record's columns | 74 of 92 |

For the anticoagulant-and-injury rule alone, the nurse gave level 1 or 2 in 57% of the visits where it fired and level 3
in 39% ([divergence-b30.md](../experiments/out/divergence-b30.md)).

### Discussion

Visits with a stricter claim were admitted more often than comparable visits without one, which indicates that part of
the 17.3% reflects under-triage in the record rather than over-calling by the rules; 17.3% is therefore an upper bound.
The engine miss rate reflects the coverage of the record rather than a failure of the rules, since most rules require
facts the record does not contain. A floor built from caregiver facts before arrival identifies a small, well-founded share
of high-acuity visits and must not be read as a screening test.

### Limitations

One site; coarse complaint flags stand in for caregiver answers; the nurse's level is a comparator.

## Parts of the plan not run

| No. | Element of the plan | Status |
| --- | --- | --- |
| 2 | graded wording variants (direct, lay, vague, buried, negative, noisy) scored as metamorphic tests; text-similarity scoring | not built; answer sheets by team members other than the builder are in the final set (9 of 27) |
| 4 | graded runs of both arms (direct, lay, vague) | not done |
| 5 | lookup against boosting; presence-only baselines; training with gaps | not run; future work |

## Changes during the final week

- Completing all 187 handbook cases and reconciling the second transcription raised number 1 from 120 passing cases to 159 of 185 without changing the meaning of any rule; the bridges and triggers raised reachability from 144 to 147 cases.
- The second version of the interview design (14 October) brought the report forward from the end of the interview (17 questions) to between 11 and 14 questions, with the same floors and the same facts captured.
- The free tier of Gemini was unusable during the Singapore night and worked in the afternoon on its oldest model.
- On 18 October the persona set grew from 10 to 25 with labels from outside the team. The first run on the new personas found two defects, which were fixed and kept (the limb warning signs now open for a limb complaint without a known mechanism; an unmeasured temperature counts as "I don't know"); a third change was reverted the same day after it altered how another answer was read. The code was then frozen: findings from later runs are recorded, not fixed. For P12 and P13 the later runs are therefore not a clean test; the first run's 18 of 20 is. On 19 October nine teammate sheets replaced builder sheets testing the same rules, making the final set of 27 (20 of 27 floors); the code was not changed for them.

## Further runs (outside the six numbers)

Runs the team made on other models during the project, each committed as a summary. They are not part of the six numbers: each is a single run, and three of them used the first versions of the knowledge base and the interview. They are recorded here with their dates so that their results can be read against the six numbers above.

### Rule extraction with a small local model

**Question.** Can a small model on one machine do rule extraction, and what makes its output usable?

**Method.** Qwen 3 14B through LM Studio drafted rules from nine pages of the fifth-edition handbook (9 to 15, 23 and 24) in two configurations: a baseline with the schema given only in the prompt, and an improved one with the full response schema enforced and a shorter prompt. Every draft went through the same gates as our own rules: the schema, then the quote-on-page check, then a heuristic match against the existing rules. One run per configuration ([qwen-baseline-vs-improved.md](../experiments/rulegen/out/qwen-baseline-vs-improved.md), run logs in [experiments/rulegen/out/runs/](../experiments/rulegen/out/runs)).

**Results.**

| Configuration | Rules drafted | Passed the schema | Quote found on the page | Quote not found | Matched an existing rule | New candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 59 | 22 (37%) | 22 | 0 | 16 | 6 |
| Full schema, shorter prompt | 76 | 69 (91%) | 63 | 6 | 54 | 15 |

**Discussion.** Enforcing the schema during generation, together with a shorter prompt, raised the share of usable drafts from about a third to nine in ten. Six drafts that passed the schema still quoted a sentence that is not on the cited page: the quote-on-page check, not the schema, is what catches them. The match against existing rules is a text heuristic and says nothing about clinical equivalence; the new candidates would need the same reading on the review site as any rule.

**Limitations.** One run per configuration, so the effect of the schema and of the shorter prompt cannot be separated and run-to-run variation is unknown.

### One interview on Qwen 3 14B (10 October, the first interview design)

**What was done.** One caregiver session was played through the web application with Qwen 3 14B as the interview model: a patient who fell and hit his chest, with chest pain and trouble breathing ([QWEN-overall-summary.md](../experiments/rulegen/out/QWEN-overall-summary.md)). The session files themselves are not in the repository; the summary is the record.

**Results.** Questions and fact extraction worked: the danger signs, the complaint, the onset, the pain rating and the mechanism were stored correctly. Two defects were found.

- One question asked about five conditions at once, and the answer "nope" was stored as a denial of all five. The second version of the interview design (14 October) allows at most two yes/no items in one question, and the guard keeps a denial only for an item the answer addresses.
- Chest pain and trouble breathing were reported on the danger-sign screen, yet the interview went on with its fixed questions and set no floor; only the severe-pain consider flag fired. Replayed through the current engine (17 October), the same answers open the question whether the breathing is getting harder in the stage before the report, and a yes sets the floor at least ESI-2 through rule B-12. Chest pain alone sets no floor by design: the handbook's level-2 criterion is the nurse's suspicion of an acute coronary syndrome, which the system never asks of a caregiver and lists on the report as not collected.

### Three other interview models on nine personas (26 September to 10 October)

**What was done.** The nine personas of the time were run once each on the first versions of the knowledge base and the interview, with three interview models ([task-i-llm-comparison-qwen-openai-gemini.md](../experiments/out/task-i-llm-comparison-qwen-openai-gemini.md)).

| Interview model | Date | Floors | Expected rules | Facts captured | Questions | Re-asks | Danger signs missed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.5 9B, local ([run](../experiments/out/task-i-20260926-0351-dynamic-qwen35.md)) | 26 Sep | 8 of 9 | 7 of 9 | 47 of 64 (73%) | 66 | 6 | 0 |
| GPT-4.1 mini (OpenAI) | 10 Oct | 6 of 9 | 6 of 9 | 46 of 64 (72%) | 77 | 16 | 0 |
| Gemini | 10 Oct | 8 of 9 | 7 of 9 | 46 of 64 (72%) | 116 | 54 | 0 |

**Discussion.** No model missed a danger sign, and all three stored about the same share of facts. They differed in the number of questions and re-asks, and GPT-4.1 mini reached two floors fewer.

**Limitations.** One run each, on code that changed between 26 September and 10 October, before both version-2 designs. The OpenAI and Gemini run files the summary cites are not in the repository, so those two rows rest on the summary alone.

### Gemini on the second interview design (15 October)

**What was done.** The five demanding personas of number 2 were run once each with Gemini 3.6 Flash as the interview model and Gemma 4 (26B) as the caregiver, both through the Gemini API, with 15 seconds between calls ([gemini-gemma-results-20261015.md](../experiments/out/gemini-gemma-results-20261015.md)).

**Results.** Floors 4 of 5, expected rules 5 of 5, facts 26 of 35 (74%), 10.2 questions to the report on average, about ten minutes a session, and no quota or rate-limit waits. The floor not reached is the breathlessness persona, for the reason given under number 4 (its sheet did not yet say whether the breathing was worsening).

**Limitations.** One run each, with a different caregiver model from the runs of number 2, so the fact counts are not directly comparable with the 30 of 35 (local model) and 29 of 35 (Claude) above. Whether the run used the free or the paid tier was not recorded.
