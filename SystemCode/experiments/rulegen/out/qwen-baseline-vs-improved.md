# Qwen 3 14B: Baseline vs Improved Rule Extraction

## Experimental setup

- Model: `qwen/qwen3-14b`
- Runtime: LM Studio
- Git branch: `JQ3`
- Pages: 9, 10, 11, 12, 13, 14, 15, 23, 24
- Baseline: weak JSON schema enforcement, full schema in prompt
- Improved: full response schema, shorter prompt

## Overall comparison

| Configuration | Drafted | Valid | Compliance | Verified spans | Span failed | Matched | New candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 59 | 22 | 37.3% | 22 | 0 | 16 | 6 |
| Improved | 76 | 69 | 90.8% | 63 | 6 | 54 | 15 |

## Detailed rates

| Metric | Baseline | Improved |
| --- | ---: | ---: |
| Schema compliance | 37.3% | 90.8% |
| Evidence verification among valid rules | 100.0% | 91.3% |
| Existing matches among valid rules | 72.7% | 78.3% |

## Improved run breakdown

| Pages | Drafted | Valid | Strict | Fuzzy | Failed | Matched | New |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 12 | 14 | 10 | 10 | 0 | 0 | 8 | 2 |
| 9,10,14,23,24 | 29 | 26 | 21 | 4 | 1 | 21 | 5 |
| 11,13,15 | 33 | 33 | 22 | 6 | 5 | 25 | 8 |

## Findings

1. Full-schema enforcement combined with a shorter prompt substantially increased schema compliance in these selected runs.
2. Span verification remains necessary: some schema-valid rules still fail to quote supporting handbook text.
3. Existing-rule matching is heuristic and does not establish clinical equivalence.
4. Unmatched candidates require span verification and human review before possible promotion.
5. The comparison uses one selected run per configuration and does not establish statistical reliability or isolate the individual effect of enforcement versus prompt shortening.

## Source run logs

### Baseline

- `2026-10-06-2315-api-p9-10-11.md`
- `2026-10-06-2343-api-p12-13-14-15.md`
- `2026-10-07-1639-api-p23-24.md`

### Improved

- `2026-10-09-1826-api-p12.md`
- `2026-10-10-1055-api-p9-10-14-23-24.md`
- `2026-10-10-1024-api-p11-13-15.md`

## Limitations

- The models are stochastic; repeated runs may differ.
- Span verification is conditional on schema validity.
- A schema-valid rule is not necessarily clinically correct.
- The number of new candidates includes unmatched rules that may have failed span verification.
- These results are experimental drafts, not approved clinical triage rules.
