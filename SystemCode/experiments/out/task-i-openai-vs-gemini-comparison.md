# OpenAI vs Gemini Task I comparison

Date: 2026-10-10

## Summary

This comparison uses the same Task I persona harness and the same interview flow, with a single run for each backend.

### OpenAI result

Report: task-i-20261010-2036-openai-full.md

- Floors: 6/9
- Expected rules: 6/9
- Extraction: 46/64 (72%)
- Danger-sign misses: 0
- Questions: 77
- Re-asks: 16

### Gemini result

Report: task-i-20261010-2028-gemini-topup-full.md

- Floors: 8/9
- Expected rules: 7/9
- Extraction: 46/64 (72%)
- Danger-sign misses: 0
- Questions: 116
- Re-asks: 54

## Side-by-side comparison

| Metric | OpenAI | Gemini |
| --- | ---: | ---: |
| Floors | 6/9 | 8/9 |
| Expected rules | 6/9 | 7/9 |
| Extraction | 46/64 (72%) | 46/64 (72%) |
| Danger-sign misses | 0 | 0 |
| Questions | 77 | 116 |
| Re-asks | 16 | 54 |

## Takeaway

The two backends are tied on extraction accuracy and danger-sign misses in this same interview task, but Gemini was stronger on floor and rule correctness. OpenAI was more concise, using fewer questions and re-asks than Gemini.

This is an apples-to-apples comparison because both runs used the same Task I persona harness and the same real interview flow.
