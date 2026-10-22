# Number 4, arm B: a language model runs its own interview (2026-10-19 02:32)

> Repeat 3 of 3 of the B-rules form on the 25 personas with identical inputs, 19 Oct 2026. The first run is in number4-second-arm-20261018-25-personas.md; the cited 16 Oct run on 10 personas is number4-second-arm.md.

Interviewer and caregiver: gemma4:12b (backend ollama), temperature 0, seed 42, context window asked 49152 tokens. Caregiver answers only from the persona's answer-sheet sentences (`say` in prototype/personas.yaml). Personas: 25. Script: [experiments/number4_second_arm.py](../number4_second_arm.py); transcripts in [sessions-number4-second-arm-20261018-25-personas-rules-repeat3/](sessions-number4-second-arm-20261018-25-personas-rules-repeat3/).

## Retrieval probe (before B-rules)

| probe | result | prompt tokens |
| --- | --- | ---: |
| quote condition of A-01.unresponsive | pass: {'when': '{"any": [{"all": [{"field": "obs.nonverbal_acute", "equals": true}, {" | 43628 |
| quote condition of B-26.suspected-toxic-ingestion | pass: {'when': '{"field": "complaint.known_toxic_ingestion", "equals": true}'} | 43633 |
| quote condition of A-22.requires-lifesaving-intervention | pass: {'when': '{"field": "obs.requires_lifesaving_intervention", "equals": true}'} | 43633 |
| rules that mention pregnancy | FAIL: ['A-18', 'B-13', 'B-17', 'B-38', 'B-39'] | 43619 |
| name the rule for fall + warfarin | pass: {'id': 'B-30'} | 43632 |

## Pass rate per form

| form | expected floor reached | danger signs asked first | runs with care advice | decision with a citation | mean turns | void (prompt exceeded window) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B-rules | 14 of 25 (56%) | 25 of 25 (100%) | 0 of 25 (0%) | 14 of 25 (56%) | 13.5 | 0 |

## Per run

| form | persona | expected | outcome | pass | miss label | turns | danger first | advice | citation |
| --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- |
| B-rules | P1-fall-anticoag | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P2-chest-pain | at least ESI-2 | level 2 or floor | yes |  | 9 | yes | 0 | ESI v5 p.13 (Cardiovascular); rule B-04. |
| B-rules | P3-abdo-pregnant | at least ESI-2 | level 2 or floor | yes |  | 15 | yes | 0 | ESI v5 p.14 (Obstetrical and Gynecologic |
| B-rules | P4-sore-throat | none | no floor | yes |  | 15 | yes | 0 | N/A |
| B-rules | P6-stroke-resolved | at least ESI-2 | level 2 or floor | yes |  | 15 | yes | 0 | ESI v5 p.12 (Stroke signs: ...sudden los |
| B-rules | P5-fever-chemo | at least ESI-2 | level 2 or floor | yes |  | 11 | yes | 0 | ESI v5 p.12 (chemotherapy example); p.15 |
| B-rules | P6-acute-gout | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P7-heat-stroke | ESI-1 | level 2 or floor | NO | missing fact | 10 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P8-decompensated-liver-disease | at least ESI-2 | level 2 or floor | yes |  | 10 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P9-breathing-no-pain | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P10-infant-fever | at least ESI-2 | level 2 or floor | yes |  | 9 | yes | 0 | ESI v5 p.23 (Pediatric Vital Signs); p.6 |
| B-rules | P11-asthma-worsening | at least ESI-2 | no decision in 16 questions | NO | model error | 16 | yes | 0 |  |
| B-rules | P12-elderly-confusion-uti | at least ESI-2 | level 2 or floor | yes |  | 13 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P13-cast-too-tight | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P14-child-knee-cut | none | no floor | yes |  | 8 | yes | 0 | page 5 |
| B-rules | P15-suicidal-thoughts | at least ESI-2 | level 2 or floor | yes |  | 8 | yes | 0 | ESI v5 p.15 (Mental and Behavioral Healt |
| B-rules | P16-intentional-overdose | at least ESI-2 | no decision in 16 questions | NO | model error | 16 | yes | 0 |  |
| B-rules | P17-nosebleed-clotting | at least ESI-2 | level 1 | yes |  | 14 | yes | 0 | ESI v5 p.13 (epistasis); Rule B-15 |
| B-rules | P18-fall-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P19-headache-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P20-cancer-pain | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P21-child-shunt-not-right | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P22-teen-threatening-family | at least ESI-2 | level 2 or floor | yes |  | 14 | yes | 0 | ESI v5 p.15 (Mental and Behavioral Healt |
| B-rules | P23-sawdust-in-eye | none | no floor | yes |  | 12 | yes | 0 | ESI v5 p.5 (Conceptual Overview) |
| B-rules | P24-bug-in-ear | none | no floor | yes |  | 15 | yes | 0 | page 5 |

## Reading

Arm A (our interview with the same deterministic answer sheets) is reported in the persona run index (RUNS.md, tag v2r) and on the evaluation results page under number 4; the comparison is made there. A miss labelled *missing fact* means the interviewer never obtained the fact the expected rule needs; *model error* means the facts were stated and the judgement was still wrong; *no decision in 16 questions* means the model kept asking and never stated a level or floor within the turn limit, which counts as a miss. In B-handbook the model is judged against our reading of the handbook (the expected floors were reconciled with our rules), which the plan notes; B-rules holds the same knowledge as arm A, so its gap to arm A is the mechanism alone.
