# Rule review app (local)

Team members verify the LLM-drafted rulebook against the cited handbook pages and
record verdicts. Runs locally; its design decisions are in `adr/`.

```bash
bash sources/download.sh          # once - the copyrighted PDFs are per person
.venv/bin/python review/app.py    # -> http://localhost:8091
.venv/bin/python review/app.py export   # -> review/out/review-log.jsonl + .csv
```

What you do per rule: read the highlighted page on the right, decide whether the
rule says what the page says - the quote, the condition, and the impact (level and
assign-vs-consider) - pick **accept / edit / reject / unsure**, say what you checked,
optionally paste a corrected YAML. Each rule page draws the condition as a diagram:
fact boxes (coloured by whether the chat can produce them) → ALL/ANY gates → the rule
→ its impact → what the caregiver and the nurse see.

Covers `rules/criteria.yaml`, `rules/criteria-candidates.yaml` and
`rules/bridges.yaml` only (not the earlier rulebook versions or the rulegen experiment outputs). Verdicts live in `reviews.db` (append-only; in `review/` by
default, gitignored, or wherever `REVIEW_DATA_DIR` points). Each verdict stores the
reviewed fields and the rulebook commit; a rule edited after a review shows "changed
since review" with a diff of what changed (ADR 0008).

## Practice cases

`/cases` lists every practice case written as a test case (`tests/v4_cases.yaml`, `tests/v4_posttest_cases.yaml`) next to
a second reading of the printed case by another model (`experiments/out/second-reading-gemini-facts.json`); `/case/<id>`
shows the handbook page with the case highlighted, the two fact sets side by side, the rule engine's outcome on each, and
a verdict form. Verdicts go into the same `reviews` table with `rule_set = 'case'` and the case's content hash, so a case
changed after a verdict shows as such. "Confirm every case shown whose two readings agree and whose test passes" records
one accept per such case for the signed-in reviewer. Evaluation number 1 is reported over confirmed cases.
