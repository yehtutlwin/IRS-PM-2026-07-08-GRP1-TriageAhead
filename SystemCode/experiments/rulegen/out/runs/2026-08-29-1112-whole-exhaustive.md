# rulegen run — mode WHOLE (PDF sent in one call) · model gemini-3.6-flash · 2026-08-29 11:12 · 156s

| metric | value | derivation |
| --- | --- | --- |
| rules drafted | 38 | one call over the whole handbook |
| schema-valid | 37/38 | jsonschema against rules/criteria.schema.json |
| span verified (strict) | 37/37 | quoted span found verbatim on some page (cited page tried first) |
| span verified (fuzzy ≥0.85) | 0/37 | best-window ratio |
| span FAILED | 0/37 | not found on any page — rejected |
| page attribution correct | 37/37 | model's cited printed page == page where the span was found |
| matched an existing reviewed rule | 22/37 | same matcher as per-page mode |
| new candidates | 15/37 | valid, not matched |
| new field names proposed | 0 | [] |

## Per-rule

| id | cited p. | found p. | schema | span | matches | provenance | override | new fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-61.intubated | 6 | 6 | ok | strict | — | verbatim |  |  |
| A-62.unresponsive-avpu | 6 | 6 | ok | strict | — | verbatim |  |  |
| A-63.pulselessness | 6 | 6 | ok | strict | A-04.pulseless | verbatim |  |  |
| A-64.apneic | 6 | None | INVALID: 'apneic' is too short | n/a | — | verbatim |  |  |
| A-65.severe-respiratory-distress | 6 | 6 | ok | strict | A-05.severe-respiratory-distress | verbatim |  |  |
| A-66.profound-hypotension | 6 | 6 | ok | strict | A-11.hypoglycemia | verbatim |  |  |
| A-67.profound-hypoglycemia | 6 | 6 | ok | strict | A-11.hypoglycemia | verbatim |  |  |
| A-68.spo2-below-90-respiratory-compromise | 9 | 9 | ok | strict | A-08.spo2-below-90-with-compromise | verbatim |  |  |
| A-69.anaphylaxis | 9 | 9 | ok | strict | A-09.anaphylaxis | verbatim |  |  |
| A-70.flaccid-infant | 9 | 9 | ok | strict | A-13.flaccid-infant | verbatim |  |  |
| A-71.cardiac-pulmonary-arrest | 9 | 9 | ok | strict | A-02.arrest-or-imminent | verbatim |  |  |
| B-61.active-chest-pain-acs | 12 | 12 | ok | strict | B-04.chest-pain-acs-suspect | verbatim |  |  |
| B-62.stroke-signs | 12 | 12 | ok | strict | B-05.stroke-signs | verbatim |  |  |
| B-63.ectopic-pregnancy | 12 | 12 | ok | strict | B-06.possible-ectopic-stable | verbatim |  |  |
| B-64.immunocompromised-fever | 12 | 12 | ok | strict | B-07.immunocompromised-fever | verbatim |  |  |
| B-65.transplant-fever | 12 | 12 | ok | strict | B-08.transplant-fever-or-infection | verbatim |  |  |
| B-66.suicidal-homicidal | 12 | 12 | ok | strict | B-09.suicidal-or-homicidal | verbatim |  |  |
| B-67.needlestick | 12 | 12 | ok | strict | B-10.needle-stick-hcw | verbatim |  |  |
| B-68.sexual-assault | 12 | 12 | ok | strict | B-11.sexual-assault | verbatim |  |  |
| B-69.increasing-respiratory-effort | 12 | 12 | ok | strict | B-12.increasing-respiratory-effort | verbatim |  |  |
| B-70.postpartum-hemorrhage | 12 | 12 | ok | strict | B-13.postpartum-hemorrhage | verbatim |  |  |
| B-71.new-confusion-lethargy | 12 | 12 | ok | strict | — | verbatim |  |  |
| B-72.severe-pain | 12 | 12 | ok | strict | B-02.severe-pain-consider | verbatim | consider |  |
| B-73.thunderclap-headache | 12 | 12 | ok | strict | — | verbatim |  |  |
| B-74.post-ictal | 12 | 12 | ok | strict | — | verbatim |  |  |
| B-75.secretions-stridor | 13 | 13 | ok | strict | B-14.stridor-or-secretions | verbatim |  |  |
| B-76.epistaxis-anticoagulated | 13 | 13 | ok | strict | — | verbatim |  |  |
| B-77.pregnant-sbp-extreme | 14 | 14 | ok | strict | — | verbatim |  |  |
| B-78.pregnant-high-risk-symptoms | 14 | 14 | ok | strict | — | verbatim |  |  |
| B-79.postpartum-heavy-bleeding | 14 | 14 | ok | strict | — | verbatim |  |  |
| B-80.high-fall | 15 | 15 | ok | strict | — | verbatim |  |  |
| B-81.vehicle-ejection | 15 | 15 | ok | strict | — | verbatim |  |  |
| B-82.mechanical-extrication | 15 | 15 | ok | strict | — | verbatim |  |  |
| B-83.high-risk-ortho-injury | 15 | 15 | ok | strict | B-24.extremity-neurovascular-compromise | verbatim |  |  |
| B-84.toxic-ingestion | 15 | 15 | ok | strict | B-26.suspected-toxic-ingestion | verbatim |  |  |
| D-61.fever-neonate | 6 | 6 | ok | strict | — | verbatim |  |  |
| D-62.fever-1-3-months | 6 | 6 | ok | strict | — | verbatim | consider |  |
| D-63.fever-3-months-plus-temp | 6 | 6 | ok | strict | — | verbatim | consider |  |