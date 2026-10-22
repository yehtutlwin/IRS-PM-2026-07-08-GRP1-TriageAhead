# Number 4, arm B: a language model runs its own interview (2026-10-19 16:35)

> The run of 19 Oct 2026 on the final set of 27 personas, kept under a dated name. `number4-second-arm.md` holds the 16 Oct 2026 run on 10 personas that the group report's earlier figures cite. The B-rules form does not repeat between runs (three repeats on the 25-persona set gave 11 to 14 of 25).

Interviewer and caregiver: gemma4:12b (backend ollama), temperature 0, seed 42, context window asked 49152 tokens. Caregiver answers only from the persona's answer-sheet sentences (`say` in prototype/personas.yaml). Personas: 27. Script: [experiments/number4_second_arm.py](../number4_second_arm.py); transcripts in [sessions-number4-second-arm-20261019-27-personas/](sessions-number4-second-arm-20261019-27-personas/).

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
| B-handbook | 10 of 27 (37%) | 0 of 27 (0%) | 0 of 27 (0%) | 11 of 27 (41%) | 13.8 | 0 |
| B-rules | 13 of 27 (48%) | 27 of 27 (100%) | 0 of 27 (0%) | 14 of 27 (52%) | 12.7 | 0 |

## Per run

| form | persona | expected | outcome | pass | miss label | turns | danger first | advice | citation |
| --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- |
| B-handbook | P1-fall-anticoag | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P2-chest-pain | at least ESI-2 | level 2 or floor | yes |  | 15 | no | 0 | page 12, 13, 14 |
| B-handbook | P4-sore-throat | none | level 5 | yes |  | 8 | no | 0 | page 20, Table 5-2 |
| B-handbook | P6-acute-gout | none | level 4 | yes |  | 14 | no | 0 | page 19, 20 |
| B-handbook | P7-heat-stroke | ESI-1 | level 2 or floor | NO | missing fact | 6 | no | 0 | page 12 |
| B-handbook | P8-decompensated-liver-disease | at least ESI-2 | level 2 or floor | yes |  | 12 | no | 0 | page 12 |
| B-handbook | P9-breathing-no-pain | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P10-infant-fever | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P12-elderly-confusion-uti | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P13-cast-too-tight | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P14-child-knee-cut | none | level 5 | yes |  | 8 | no | 0 | page 20, Table 5-2 |
| B-handbook | P15-suicidal-thoughts | at least ESI-2 | level 2 or floor | yes |  | 12 | no | 0 | page 12, 15 |
| B-handbook | P16-intentional-overdose | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P17-nosebleed-clotting | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P18-fall-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P19-headache-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | no | 0 |  |
| B-handbook | P20-cancer-pain | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | P21-child-shunt-not-right | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | ND-P20-infant-fever | at least ESI-2 | level 2 or floor | yes |  | 13 | no | 0 | page 30 |
| B-handbook | ND-P23-elderly-confusion | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | ND-P27-resolved-speech-change | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | ND-P28-postpartum-bleeding | at least ESI-2 | level 2 or floor | yes |  | 7 | no | 0 | page 14 |
| B-handbook | ND-P29-pregnant-headache | at least ESI-2 | level 2 or floor | yes |  | 12 | no | 0 | page 14 |
| B-handbook | CH-I29-03-possible-ectopic | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | CH-I29-04-fever-during-chemotherapy | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-handbook | CH-I29-08-sexual-assault | at least ESI-2 | level 2 or floor | yes |  | 9 | no | 0 | page 12 |
| B-handbook | CH-I29-09-child-increasing-work-of-breathing | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | no | 0 |  |
| B-rules | P1-fall-anticoag | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P2-chest-pain | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P4-sore-throat | none | no floor | yes |  | 9 | yes | 0 | ESI v5 p.19; p.20 (Table 5-2, item 2) |
| B-rules | P6-acute-gout | none | no floor | yes |  | 8 | yes | 0 | page 5 |
| B-rules | P7-heat-stroke | ESI-1 | level 2 or floor | NO | missing fact | 5 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P8-decompensated-liver-disease | at least ESI-2 | level 2 or floor | yes |  | 14 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P9-breathing-no-pain | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P10-infant-fever | at least ESI-2 | level 2 or floor | yes |  | 10 | yes | 0 | ESI v5 p.23 (Pediatric Vital Signs); p.6 |
| B-rules | P12-elderly-confusion-uti | at least ESI-2 | level 2 or floor | yes |  | 10 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | P13-cast-too-tight | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P14-child-knee-cut | none | no floor | yes |  | 9 | yes | 0 | ESI v5 p.20 (Table 5-2, ESI Level 5) |
| B-rules | P15-suicidal-thoughts | at least ESI-2 | level 2 or floor | yes |  | 15 | yes | 0 | ESI v5 p.15 (Mental and Behavioral Healt |
| B-rules | P16-intentional-overdose | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | P17-nosebleed-clotting | at least ESI-2 | level 1 | yes |  | 15 | yes | 0 | ESI v5 p.13 (epistasis); Rule B-15 |
| B-rules | P18-fall-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P19-headache-no-floor | none | no decision in 16 questions | NO | model error (over-call) | 16 | yes | 0 |  |
| B-rules | P20-cancer-pain | at least ESI-2 | level 2 or floor | yes |  | 8 | yes | 0 | ESI v5 p.12 (Severe Pain or Distress); r |
| B-rules | P21-child-shunt-not-right | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | ND-P20-infant-fever | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | ND-P23-elderly-confusion | at least ESI-2 | level 2 or floor | yes |  | 13 | yes | 0 | ESI v5 p.12 (New Onset Confusion, Lethar |
| B-rules | ND-P27-resolved-speech-change | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | ND-P28-postpartum-bleeding | at least ESI-2 | level 1 | yes |  | 4 | yes | 0 | ESI v5 p.14 (Obstetrical and Gynecologic |
| B-rules | ND-P29-pregnant-headache | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | CH-I29-03-possible-ectopic | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | CH-I29-04-fever-during-chemotherapy | at least ESI-2 | level 2 or floor | yes |  | 11 | yes | 0 | ESI v5 p.12 (chemotherapy example); p.15 |
| B-rules | CH-I29-08-sexual-assault | at least ESI-2 | no decision in 16 questions | NO | missing fact | 16 | yes | 0 |  |
| B-rules | CH-I29-09-child-increasing-work-of-breathing | at least ESI-2 | level 1 | yes |  | 4 | yes | 0 | ESI v5 p.6 (Fig 2-2 list); p.13 (Respira |

## Reading

Arm A (our interview with the same deterministic answer sheets) is reported in the persona run index (RUNS.md, tag v2r) and on the evaluation results page under number 4; the comparison is made there. A miss labelled *missing fact* means the interviewer never obtained the fact the expected rule needs; *model error* means the facts were stated and the judgement was still wrong; *no decision in 16 questions* means the model kept asking and never stated a level or floor within the turn limit, which counts as a miss. In B-handbook the model is judged against our reading of the handbook (the expected floors were reconciled with our rules), which the plan notes; B-rules holds the same knowledge as arm A, so its gap to arm A is the mechanism alone.
