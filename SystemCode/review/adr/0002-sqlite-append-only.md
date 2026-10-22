# ADR 0002: Verdicts are append-only rows in a local SQLite file

**Status:** accepted (19 Sep 2026)

## Context
The task-A pipeline needs a logged verdict per rule per reviewer (accepted /
edited / rejected, with the reason) - the "review log" the report's draft-survival
rate is computed from. Reviews must survive restarts and be exportable.

## Decision
`review/reviews.db` (gitignored) holds one table, `reviews`, and rows are never
updated or deleted: a reviewer who changes their mind adds a new row, and the UI
shows each reviewer's latest verdict per rule while keeping the history visible.
`review/app.py export` (or `/export`) writes `review-log.jsonl` and `.csv`.

## Consequences
- The full trail (including reversals) is the artefact; nothing is lost by a
  second look.
- Merging reviews from several machines is a concatenation of JSONL exports;
  a shared server later needs no schema change.
- Each row stores the rule's content hash at review time (ADR 0005), so a verdict
  given on an older wording is flagged, not silently trusted.
