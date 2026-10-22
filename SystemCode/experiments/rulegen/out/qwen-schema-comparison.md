# Qwen 3 14B — Schema Enforcement Experiment

## Objective

Evaluate whether enforcing the complete rule schema during generation improves the validity of candidate ESI triage rules extracted using Qwen 3 14B through LM Studio.

## Experimental Setup

- Model: `qwen/qwen3-14b`
- Runtime: LM Studio (local OpenAI-compatible API)
- Git branch: `JQ3`
- Source: ESI v5 handbook, printed page 12
- Validation: `rules/criteria.schema.json`
- Evaluation: schema validity, supporting-span verification, reviewed-rule matching, and new-candidate identification

## Results

| Metric | Baseline | Full schema | Full schema + shorter prompt |
|---|---:|---:|---:|
| Rules drafted | 15 | 16 | 14 |
| Schema-valid | 0/15 | 9/16 | 10/14 |
| Schema compliance | 0% | 56.3% | 71.4% |
| Strict spans | 0 | 9 | 10 |
| Fuzzy spans | 0 | 0 | 0 |
| Existing-rule matches | 0 | 9 | 8 |
| New candidates | 0 | 0 | 2 |

## Key Findings

**1. Full-schema enforcement improved validity.** Schema compliance increased from 0% in the selected baseline run to 56.3% with the full response schema.

**2. Removing schema text from the prompt produced a further improvement in this trial.** Compliance reached 71.4%, although this result requires repeated runs to establish reliability.

**3. Remaining failures involved malformed conditions.** Qwen sometimes generated both `equals` and `in` within the same leaf condition, violating the schema's two-property limit.

**4. Evidence verification remained strong among valid rules.** All 19 schema-valid rules across the two improved runs passed strict span verification. Invalid rules did not reach this stage.

**5. Two unmatched candidates emerged in the shorter-prompt run.** `B-95.new-onset-ams` and `B-97.psychological-distress` require human review to determine whether they are genuinely new criteria or missed matches.

## Limitations

- One run per configuration; results may reflect stochastic variation.
- Only one handbook page was used in this comparison.
- Schema validity does not establish clinical correctness.
- Existing-rule matching is heuristic.
- Strict structured-output configuration did not guarantee complete compliance with nested constraints in the observed LM Studio runs.

## Conclusion

The results support using full-schema enforcement when extracting ESI criteria with Qwen 3 14B. The shorter-prompt configuration produced the highest schema-valid rate in this trial.

A further step would be to evaluate this configuration across the previously tested handbook pages and compare results against the original baseline.

## Supporting Run Logs

- Baseline: `2026-10-06-2343-api-p12-13-14-15.md`
- Full schema: `2026-10-09-1814-api-p12.md`
- Full schema + shorter prompt: `2026-10-09-1826-api-p12.md`