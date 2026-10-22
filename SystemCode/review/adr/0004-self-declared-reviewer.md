# ADR 0004: Reviewer identity is self-declared for now

**Status:** accepted (19 Sep 2026); revisit when the app is exposed

## Context
The app runs locally for a four-person team; real authentication would need an identity
provider, which was not chosen.

## Decision
The reviewer types a name once; the browser remembers it (`localStorage`) and every
review row carries it. No accounts, no passwords, no sessions.

## Consequences
- Zero friction for the team; the review log's `reviewer` column still supports the
  independence rules (persona author vs app builder, second reviewer per rule).
- Names are trusted, not verified. Acceptable on a laptop or behind a login
  gate; a public deployment needs real auth (the row format will not
  change - only where `reviewer` comes from).
