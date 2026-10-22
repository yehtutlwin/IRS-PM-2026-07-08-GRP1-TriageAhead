# Gemini free-tier interview results

**Date:** 15 October 2026

**Interview model:** `gemini-3.6-flash`

**Persona model:** `gemma-4-26b-a4b-it` through the Gemini API

**Interview mode:** dynamic

**Configured spacing:** 15 seconds between Gemini API calls

## Results

Each of the five required personas was run once. Runs were sequential; the persona model and interview model both used the Gemini API.

| Persona | Floor check | Expected rules | Facts captured | Questions to report | Session duration | Answer turns | Gemini API calls | Re-asks | Harness complete |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag | Pass | Pass | 7/9 | 14 | 695 s | 16 | 49 | 2 | No |
| P3-abdo-pregnant | Pass | Pass | 4/6 | 9 | 834 s | 16 | 48 | 4 | Yes |
| P6-stroke-resolved | Pass | Pass | 3/6 | 5 | 453 s | 10 | 30 | 0 | Yes |
| P6-acute-gout | Pass | Pass | 5/7 | 13 | 631 s | 15 | 45 | 2 | Yes |
| P9-breathing-no-pain | **Fail** | Pass | 7/7 | 10 | 510 s | 12 | 36 | 1 | No |
| **Total / overall** | **4/5** | **5/5** | **26/35 (74%)** | **10.2 mean** | **3,124 s total** | **69** | **208** | **9** | **3/5** |

All five persona runs returned a scored result. The harness's formal `complete` flag was true for three sessions and false for P1 and P9; those two are therefore not counted as completed sessions in the harness. P9's expected floor check failed even though its expected rule passed and all seven scored facts were captured.

Across all runs, mean session duration was approximately **625 seconds (10.4 minutes)**, or **45 seconds per answer turn** when pooled across the 69 turns. Times include the persona-player API calls and are from sequential runs, not a concurrency test.

## Gemini limits and recommendation

- The first configured model, `gemini-3.6-flash`, handled the interviews; no model rotation was observed.
- The runs recorded **208 successful Gemini API calls across both model roles**. This is a call count, **not a token count**.
- No per-minute rate-limit, overload, or daily-quota waits were recorded. Daily-quota exhaustion was not exercised, so the post-exhaustion behavior was not verified by these runs.
- The configured 15-second spacing produced the session times above. This is evidence for these sequential persona runs only; it does not establish capacity for concurrent demo sessions or remaining free-tier quota.
- Whether multiple Google Cloud projects may be used for one application was not checked against Google's terms.

These runs cover the Gemini/Gemma persona setup only. The planned Claude and local-model comparison runs were not completed, so this report does not compare interview quality across those backends.

## Run details

| Persona | Run ID | Calls by interview / persona role |
| --- | --- | ---: |
| P9-breathing-no-pain | `20261015-184016` | Not separated in the saved summary; 36 total |
| P1-fall-anticoag | `20261015-185153` | Not separated in the saved summary; 49 total |
| P3-abdo-pregnant | `20261015-190348` | Not separated in the saved summary; 48 total |
| P6-stroke-resolved | `20261015-191756` | Not separated in the saved summary; 30 total |
| P6-acute-gout | `20261015-192544` | Not separated in the saved summary; 45 total |

