# ADR 0003: The cited page is rendered inline with the quoted span highlighted

**Status:** accepted (19 Sep 2026)

## Context
A review is only as good as the reviewer's look at the source. Asking people to
open a 36-page PDF, find "p.12", and locate a sentence is the step everyone skips.

## Decision
For each citation the app locates the page in the local PDF and renders it as a
PNG (110 dpi, cached in `review/cache/`) with the rule's quoted span highlighted
via a text search. Printed page numbers and PDF indices differ per document, so
the page is located by searching for the span around the expected index rather
than trusting the number; the PDF viewer link and prev/next page links are there
for context. Copyrighted PDFs are never committed - the app reads each person's
own copy from `sources/` (fetched by `sources/download.sh`) and says so when a
file is missing.

## Consequences
- A reviewer sees the sentence in its context without leaving the page.
- **No highlight is itself a finding**: the span is not on the cited page as
  quoted (wrong page, paraphrased "quote", or invented text). The UI says this
  explicitly rather than hiding the failure.
- Long spans are matched by their first 60 characters / first clause; a miss can
  still be a quoting-format difference - the reviewer decides, which is the point.
