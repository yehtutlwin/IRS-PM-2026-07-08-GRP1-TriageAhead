# Number 4, arm B: a language model runs its own interview (2026-10-18 19:17)

> This is the run of 18 Oct 2026 on 20 personas, kept under a dated name. `number4-second-arm.md` holds the 16 Oct 2026 run on 10 personas that the evaluation results page and the group report cite. Its B-rules form does not repeat between runs.

Interviewer and caregiver: gemma4:12b (backend ollama), temperature 0, seed 42, context window asked 49152 tokens. Caregiver answers only from the persona's answer-sheet sentences (`say` in prototype/personas.yaml). Personas: 20. Script: [experiments/number4_second_arm.py](../number4_second_arm.py); transcripts in [sessions-number4-second-arm-20261018-20-personas/](sessions-number4-second-arm-20261018-20-personas/).

## Retrieval probe (before B-rules)

| probe | result | prompt tokens |
| --- | --- | ---: |
| quote condition of A-01.unresponsive | pass: {'when': '{"any": [{"all": [{"field": "obs.nonverbal_acute", "equals": true}, {" | 43628 |
| quote condition of B-26.suspected-toxic-ingestion | pass: {'when': '{"field": "complaint.known_toxic_ingestion", "equals": true}'} | 43633 |
| quote condition of A-22.requires-lifesaving-intervention | pass: {'when': '{"field": "obs.requires_lifesaving_intervention", "equals": true}'} | 43633 |
| rules that mention pregnancy | FAIL: ['A-18', 'B-13', 'B-17', 'B-38', 'B-39', 'B-6'] | 43619 |
| name the rule for fall + warfarin | pass: {'id': 'B-30'} | 43632 |

## Pass rate per form

| form | expected floor reached | danger signs asked first | runs with care advice | decision with a citation | mean turns | void (prompt exceeded window) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B-handbook | 8 of 20 (40%) | 0 of 20 (0%) | 0 of 20 (0%) | 9 of 20 (45%) | 13.7 | 0 |
| B-rules | 9 of 20 (45%) | 20 of 20 (100%) | 0 of 20 (0%) | 10 of 20 (50%) | 12.9 | 0 |

## Per run

| form | persona | expected | outcome | pass | miss label | turns | danger first | advice | citation |
| --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- |
| B-handbook | P1-fall-anticoag | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P2-chest-pain | at least ESI-2 | level 2 or floor | yes |  | 15 | no | 0 | page 12, 13, 14 |
| B-handbook | P3-abdo-pregnant | at least ESI-2 | level 2 or floor | yes |  | 10 | no | 0 | page 14 |
| B-handbook | P4-sore-throat | none | level 5 | yes |  | 10 | no | 0 | page 20, Table 5-2 |
| B-handbook | P6-stroke-resolved | at least ESI-2 | level 2 or floor | yes |  | 14 | no | 0 | page 12, 'Signs of a stroke but does not |
| B-handbook | P5-fever-chemo | at least ESI-2 | level 2 or floor | yes |  | 10 | no | 0 | page 15, 'Transplant' section (referring |
| B-handbook | P6-acute-gout | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P7-heat-stroke | ESI-1 | level 2 or floor | NO | missing fact | 6 | no | 0 | page 12 |
| B-handbook | P8-decompensated-liver-disease | at least ESI-2 | level 2 or floor | yes |  | 12 | no | 0 | page 12 |
| B-handbook | P9-breathing-no-pain | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P10-infant-fever | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P11-asthma-worsening | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P12-elderly-confusion-uti | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P13-cast-too-tight | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P14-child-knee-cut | none | level 5 | yes |  | 8 | no | 0 | page 20, Table 5-2 |
| B-handbook | P15-suicidal-thoughts | at least ESI-2 | level 2 or floor | yes |  | 12 | no | 0 | page 12, 15 |
| B-handbook | P16-intentional-overdose | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P17-nosebleed-clotting | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P18-fall-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P19-headache-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-rules | P1-fall-anticoag | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P2-chest-pain | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P3-abdo-pregnant | at least ESI-2 | level 2 or floor | yes |  | 15 | yes | 0 | ESI v5 p.14 (Obstetrical and Gynecologic |
| B-rules | P4-sore-throat | none | no floor | yes |  | 9 | yes | 0 | ESI v5 p.19; p.20 (Table 5-2, item 2) |
| B-rules | P6-stroke-resolved | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P5-fever-chemo | at least ESI-2 | level 2 or floor | yes |  | 12 | yes | 0 | ESI v5 p.12 (chemotherapy example); p.15 |
| B-rules | P6-acute-gout | none | no floor | yes |  | 10 | yes | 0 | ESI v5 p.5 |
| B-rules | P7-heat-stroke | ESI-1 | level 2 or floor | NO | missing fact | 10 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P8-decompensated-liver-disease | at least ESI-2 | level 2 or floor | yes |  | 10 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P9-breathing-no-pain | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P10-infant-fever | at least ESI-2 | level 2 or floor | yes |  | 9 | yes | 0 | ESI v5 p.23 (Pediatric Vital Signs); p.6 |
| B-rules | P11-asthma-worsening | at least ESI-2 | level 1 | yes |  | 5 | yes | 0 | ESI v5 p.6 (Fig 2-2 list of presentation |
| B-rules | P12-elderly-confusion-uti | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P13-cast-too-tight | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P14-child-knee-cut | none | no floor | yes |  | 9 | yes | 0 | ESI v5 p.5 (Decision Point C) |
| B-rules | P15-suicidal-thoughts | at least ESI-2 | level 2 or floor | yes |  | 9 | yes | 0 | ESI v5 p.15 (Mental and Behavioral Healt |
| B-rules | P16-intentional-overdose | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P17-nosebleed-clotting | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P18-fall-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P19-headache-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |

## Reading

Arm A (our interview with the same deterministic answer sheets) is reported in the persona run index (RUNS.md, tag v2r) and on the evaluation results page under number 4; the comparison is made there. A miss labelled *missing fact* means the interviewer never obtained the fact the expected rule needs; *model error* means the facts were stated and the judgement was still wrong; *no decision in 16 questions* means the model kept asking and never stated a level or floor within the turn limit, which counts as a miss. In B-handbook the model is judged against our reading of the handbook (the expected floors were reconciled with our rules), which the plan notes; B-rules holds the same knowledge as arm A, so its gap to arm A is the mechanism alone.
