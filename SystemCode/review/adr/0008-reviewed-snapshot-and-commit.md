# ADR 0008: Each verdict stores the reviewed fields and the rulebook commit; changes are shown as a diff

**Status:** accepted (19 Sep 2026); refines ADR 0005

## Context
ADR 0005 hashed the whole YAML entry. That flags a verdict as "changed since review"
even when only the drafter's `notes` or an implementation flag moved, and it cannot
show *what* changed - the reviewer had to re-read the rule from scratch.

## Decision
- The hash covers only the fields a verdict is about (`REVIEWED_FIELDS` in
  `app.py`: decision point, provenance, source, span, condition, assessed-via,
  effect override and the definition / bridge fields). `id` and `notes` are excluded;
  a new implementation-only field is excluded unless it is added to that list.
- Every row stores `rule_snapshot` - those fields as JSON, as the reviewer saw them -
  and `rule_commit`, the served checkout's HEAD (`-dirty` if the rule files had
  uncommitted edits). The server fills both; the client only sends the hash.
- A verdict whose hash no longer matches shows a unified diff of reviewed vs current
  fields next to it. The snapshot, not git, is what the diff is built from, so it
  works after history rewrites or if the database outlives the repository; the
  commit is provenance for the report ("reviewed at rulebook commit X").
- Rows written before this decision were backfilled where the entry was unchanged
  (old whole-entry hash still matched): new hash, snapshot from the current YAML,
  commit = last commit that touched the rule files. Unchanged rows without a
  snapshot show "no diff available".

## Consequences
- A rulebook edit invalidates exactly the verdicts it should, and reviewers see the
  delta in one glance.
- The export carries snapshot and commit, so the report's draft-survival numbers can
  be tied to a rulebook version and recomputed later.
