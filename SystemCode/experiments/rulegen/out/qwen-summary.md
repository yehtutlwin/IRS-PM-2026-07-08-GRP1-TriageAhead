# Qwen 3 14B Rulegen Experiment Summary

Backend: LM Studio local API  
Model: `qwen/qwen3-14b`  
Pages evaluated: 9–15, 23–24

## Run comparison

| Pages | Drafted | Schema-valid | Strict | Fuzzy | Span failed | Matched | New candidates | New fields |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9–11 | 23 | 13/23 | 10/13 | 3/13 | 0/13 | 11/13 | 2/13 | 0 |
| 12–15 | 34 | 9/34 | 6/9 | 3/9 | 0/9 | 5/9 | 4/9 | 2 |
| 23–24 | 2 | 0/2 | 0/0 | 0/0 | 0/0 | 0/0 | 0/0 | 0 |

## Overall

- Rules drafted: **59**
- Schema-valid: **22/59**
- Schema compliance rate: **37.3%**
- Strict span verification: **16**
- Fuzzy span verification: **6**
- Span failures: **0**
- Evidence verification rate: **22/22 (100.0%)**
- Existing reviewed rules matched: **16/22 (72.7%)**
- New candidates: **6/22 (27.3%)**

## Observations

- Schema compliance varied substantially between handbook pages.
- When Qwen produced schema-valid rules, supporting spans were generally recoverable from the handbook.
- A recurring failure mode was reproducing JSON Schema constructs such as `$defs` inside generated rule conditions.
- Some generated rules omitted required fields such as `decision_point` or `assessed_via`.
- New candidates should remain candidates until manually reviewed against the cited handbook page.