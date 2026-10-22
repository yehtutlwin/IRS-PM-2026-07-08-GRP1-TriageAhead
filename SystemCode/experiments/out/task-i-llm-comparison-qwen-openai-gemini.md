# Task I model comparison: Qwen vs OpenAI vs Gemini

This comparison uses the same real interview persona harness and the same 9-persona evaluation set.

## Results

### Qwen (dynamic)

Source: [task-i-20260926-0351-dynamic-qwen35.md](task-i-20260926-0351-dynamic-qwen35.md)

- Floors: 8/9
- Expected rules: 7/9
- Extraction: 47/64 (73%)
- Danger-sign misses: 0
- Questions: 66
- Re-asks: 6

### OpenAI

Source: task-i-20261010-2036-openai-full.md

- Floors: 6/9
- Expected rules: 6/9
- Extraction: 46/64 (72%)
- Danger-sign misses: 0
- Questions: 77
- Re-asks: 16

### Gemini

Source: task-i-20261010-2028-gemini-topup-full.md

- Floors: 8/9
- Expected rules: 7/9
- Extraction: 46/64 (72%)
- Danger-sign misses: 0
- Questions: 116
- Re-asks: 54

## Side-by-side summary

| Model | Floors | Expected rules | Extraction | Danger-sign misses | Questions | Re-asks |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen (dynamic) | 8/9 | 7/9 | 47/64 (73%) | 0 | 66 | 6 |
| OpenAI | 6/9 | 6/9 | 46/64 (72%) | 0 | 77 | 16 |
| Gemini | 8/9 | 7/9 | 46/64 (72%) | 0 | 116 | 54 |

## Interpretation

- Qwen dynamic is the strongest overall on this task: it had the best extraction rate and the lowest question count and re-ask count.
- Gemini matched Qwen on floor and rule correctness, but it required far more questioning and had many more re-asks.
- OpenAI matched the extraction rate of Gemini but was weaker on floor and rule correctness and required more questions than Qwen.
- All three models had zero danger-sign misses, which suggests they were similarly good at not missing the key red-flag conditions.

## Conclusion

For this interview task, the best overall performer was Qwen dynamic, combining the strongest extraction score with the best efficiency. Gemini was competitive on correctness but much more verbose. OpenAI was competitive on extraction but weaker on floor/rule decisions.
