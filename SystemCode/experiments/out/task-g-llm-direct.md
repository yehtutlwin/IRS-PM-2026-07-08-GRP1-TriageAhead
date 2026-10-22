# Ablation - LLM-direct triage vs the rulebook on the same cases

200 labelled Yale visits (40 per recorded ESI level, seed 42), each described as structured text and
given to the model (ollama: gemma4:12b) 3 times. The rulebook's claim on the same case uses the
task_g_full mapping (with vitals). Recorded ESI is a comparator, not truth.

| | LLM-direct | rulebook |
| --- | ---: | ---: |
| exact agreement with recorded ESI | 30.5% | n/a (floor, not a level) |
| within one level | 68.0% | n/a |
| under-triage of recorded ESI 1-2 | **35.0%** | silent-miss semantics, see task-g-full |
| over-triage of recorded ESI 3-5 (called 1-2) | 19.2% | overshoot on claimed cases only |
| makes a claim at all | 100% (always answers) | 6.5% |
| claims consistent with recorded 1-2 | - | 92.3% |
| **rerun consistency** (3 identical answers) | **88.0%** (max spread 3 levels) | 100% by construction |
| explanation | one free-text sentence, unverifiable | rule id + handbook page + quoted span |
| parse failures (no digit in reply) | 0 | - |

Confusion (rows recorded ESI, columns model's first answer; 0 = no parseable answer):

```
preds  1   2  3   5
esi                
1      4  27  3   6
2      0  21  7  12
3      0   9  8  23
4      0   8  5  27
5      0   6  6  28
```

Reading: the model always produces a level - including for the majority of cases where the rulebook
honestly declines because the record lacks the deciding details - and its answers vary between identical
runs. The rulebook never overshoots on repeat, never invents a level, and every claim is traceable; its
cost is reach. Which property matters more is the product argument, made in the report's findings.
