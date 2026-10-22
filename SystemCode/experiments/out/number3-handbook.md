# Number 3, handbook form: the rules against a model deciding directly (2026-10-15 19:16)

Model: gemma4:12b (backend ollama), 3 runs per case per form. Cases: 187 handbook practice cases ([tests/v4_cases.yaml](../../tests/v4_cases.yaml), [tests/v4_posttest_cases.yaml](../../tests/v4_posttest_cases.yaml)); printed form from [tests/v4_case_texts.json](../../tests/v4_case_texts.json). Truth: the handbook's own answer. Script: [experiments/number3_handbook.py](../number3_handbook.py); per-run detail in number3-handbook.json.

## The model, per run

| measure | facts form | text form |
|---|---|---|
| runs | 561 | 561 |
| agrees with the book exactly | 390/561 (69.5%) | 338/561 (60.2%) |
| within one level of the book | 529/561 (94.3%) | 532/561 (94.8%) |
| model under-triage: book level 1 or 2, model lower acuity | 38/270 (14.1%) | 106/270 (39.3%) |
| book level 3 to 5, model said 1 or 2 | 33/291 (11.3%) | 12/291 (4.1%) |
| no usable answer | 0/561 (0.0%) | 0/561 (0.0%) |
| cited a page and a phrase | 560/561 (99.8%) | 561/561 (100.0%) |
| citation verifiable (phrase found on that printed page) | 65/561 (11.6%) | 12/561 (2.1%) |

## The model, per case (consistency)

| measure | facts form | text form |
|---|---|---|
| same level in all runs | 184/187 (98.4%) | 182/187 (97.3%) |
| same level in all runs and it is the book's | 129/187 (69.0%) | 111/187 (59.4%) |
| cases with at least one run two or more levels off | 11/187 (5.9%) | 10/187 (5.3%) |

## The rule engine on the same facts

The engine claims level 1 (an ESI-1 indicator fired), 'at least 2' (a floor rule fired) or nothing. A case passes when the claim matches the book: the book's rule fired for a level 1 or 2 case, and nothing fired for a level 3 to 5 case (the same judgement as the fixed tests of number 1). The engine gives the same answer every run and every claim names its handbook page.

| measure | engine |
|---|---|
| cases passing | 159/187 (85.0%) |
| book level 1 or 2: a claim made (the engine miss rate is the rest) | 60/90 (66.7%) |
| book level 1 or 2: pass, counting the 4 cases the book decides on vital signs, where silence is right | 64/90 (71.1%) |
| book level 3 to 5: nothing fired | 95/97 (97.9%) |
| claims in all, and how many are on a book level 1 or 2 case | 65, 60/65 (92.3%) (the others: see the test file's note on each) |
| same answer every run | all |
| claims with a verifiable handbook page | all (checked by rules/validate.py) |

## By book level

| book level | cases | engine pass | model exact, facts form | model exact, text form |
|---|---|---|---|---|
| 1 | 29 | 29/29 (100.0%) | 76/87 (87.4%) | 45/87 (51.7%) |
| 2 | 61 | 35/61 (57.4%) | 153/183 (83.6%) | 119/183 (65.0%) |
| 3 | 45 | 43/45 (95.6%) | 86/135 (63.7%) | 93/135 (68.9%) |
| 4 | 22 | 22/22 (100.0%) | 0/66 (0.0%) | 3/66 (4.5%) |
| 4 or 5 | 1 | 1/1 (100.0%) | 0/3 (0.0%) | 0/3 (0.0%) |
| 5 | 29 | 29/29 (100.0%) | 75/87 (86.2%) | 78/87 (89.7%) |

## Reading

Exact agreement counts a run right only when it names the book's level; the engine's pass counts a level 3 to 5 case right when it stays silent, which is the engine's job pre-arrival. The two are therefore compared where both make a claim: book level 1 and 2. Model under-triage is the model naming a lower acuity than the book on those cases; the engine's counterpart is its miss rate (the book's rule not firing), a silence the nurse sees as 'no claim', not a wrong level.
