# ADR 0005: Every review records the rule's content hash; changed rules show "changed since review"

**Status:** accepted (19 Sep 2026)

## Context
The rulebook is edited while reviews happen (task A edits, candidate promotions).
A verdict on last week's wording must not read as a verdict on today's.

## Decision
Each rule's YAML entry is hashed (sha256 of its sorted dump, 12 hex chars) on load;
every review row stores the hash it was given against. The index and the rule page
flag a review whose hash no longer matches as "changed since review".

## Consequences
- Reviewers see which verdicts need a fresh look after a rulebook edit; nothing is
  silently invalidated or auto-expired.
- The export carries the hash, so the report's draft-survival numbers can be
  computed against a specific rulebook version.
