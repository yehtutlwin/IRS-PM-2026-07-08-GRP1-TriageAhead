# ADR 0001: The review app is a separate, dependency-free local process

**Status:** accepted (19 Sep 2026)

## Context
Teammates need to verify ~100 LLM-drafted rules against the cited handbook pages
and record verdicts. The intake web app (`webapp/`) exists, but it is the product
demo; the review tool is team tooling with a different audience and lifetime.

## Decision
`review/app.py` is its own process on port 8091, built on the Python standard
library (`http.server`, `sqlite3`) plus `pymupdf` (already a project dependency)
and `PyYAML`. No framework, no JavaScript build, no external services.

## Consequences
- Anyone on the team runs it with one command after the normal repo setup.
- Exposing it later is a sub-path on the same tunnel or a second tunnel; nothing in
  the app assumes a host (links are relative).
- Server-rendered HTML with a few lines of inline JS keeps the whole app in one file
  a teammate can read in ten minutes; the cost is no live reactivity, which review
  work does not need.
