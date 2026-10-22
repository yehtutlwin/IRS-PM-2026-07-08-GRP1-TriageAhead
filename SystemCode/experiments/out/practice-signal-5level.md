# Practice signal, five-level version (pre-arrival features only)

Same 17 features and the same split as the two-class practice signal (seed 42, 446,423 train / 111,606 test), trained on the recorded nurse level 1 to 5. Purpose: to show where the pre-arrival facts carry information. This model is not used by the app.

## Confusion matrix on the test visits (recorded level on rows, predicted on columns)

| true \ predicted | 1 | 2 | 3 | 4 | 5 | recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 510 | 314 | 230 | 0 | 0.000 |
| 2 | 0 | 11,049 | 14,367 | 7,291 | 0 | 0.338 |
| 3 | 1 | 6,160 | 30,582 | 10,503 | 0 | 0.647 |
| 4 | 0 | 380 | 8,557 | 16,064 | 0 | 0.643 |
| 5 | 0 | 61 | 1,888 | 3,649 | 0 | 0.000 |

- accuracy 0.517; predicting the commonest level for everyone would give 0.423
- quadratic weighted kappa 0.386
- classifier under-triage (true 1-2 predicted 3-5) 0.658

## Where the facts separate levels

One-versus-rest AUROC per level (how well the model ranks that level against all others):

| level | AUROC |
| --- | ---: |
| 1 | 0.799 |
| 2 | 0.709 |
| 3 | 0.704 |
| 4 | 0.795 |
| 5 | 0.764 |

Adjacent-pair AUROC (only visits of the two levels, ranked by the model's relative probability):

| pair | AUROC |
| --- | ---: |
| 1 vs 2 | 0.753 |
| 2 vs 3 | 0.694 |
| 3 vs 4 | 0.811 |
| 4 vs 5 | 0.615 |

Every two-way split of the scale (five-class probabilities summed up to the cut; a two-class model trained directly on each split gives the same figures to three decimals):

| split | AUROC | share of visits on the low side |
| --- | ---: | ---: |
| 1-1 vs 2-5 | 0.799 | 0.009 |
| 1-2 vs 3-5 | 0.714 | 0.303 |
| 1-3 vs 4-5 | 0.813 | 0.726 |
| 1-4 vs 5-5 | 0.764 | 0.950 |

The 1-2 versus 3-5 split, the one the report uses, is the weakest of the four at 0.714; the sharpest is 1-3 versus 4-5 at 0.813. The report's split is chosen by the use (a floor is two-sided at the handbook's level-2 line) and not because the facts favour it.

Reading: the facts carry a modest amount of order across the whole scale and do not single out the urgent line; as a level assigner the model is unsafe (see the matrix), so the report prints a two-sided share rather than a level.
