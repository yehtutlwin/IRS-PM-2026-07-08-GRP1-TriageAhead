# Yale ED dataset — schema guide for anyone mapping it to our rules

Read this before writing any label→fact mapping (Task G harnesses, persona
seeding, the tree experiment). Every claim below is either **quoted from the
source paper [1]**, **computed from the dataset** (reproducer given), or marked
**[unverified]**. A mapping assumption must be backed by one of these.

## What the dataset is (per [1], Materials and methods)

- "Retrospective data was obtained from three EDs covering the period of March
  2013 to July 2017" — a level I trauma center, a community hospital ED and a
  free-standing ED, "all three EDs are part of a single hospital system utilizing
  the Epic EHR ... and the Emergency Severity Index (ESI) for triage."
- "A total of 560,486 ED visits were included in the study", from "202,953
  unique patients"; "a total of 972 variables" per visit.
- Study outcome: "The primary response variable was the patient's disposition,
  encoded in a binary variable (1 = admission, 0 = discharge)"; visits with other
  dispositions (transfer, AMA, eloped) were excluded.
- The public file is "a de-identified, processed dataset" (Data Availability):
  it carries **no patient identifier column** (computed: none of the 972 columns
  is an ID), so rows are visits and the same person can recur.

## The 7 column groups

| Group | Columns | Construction, per [1] | Encoding in the file (computed) |
| --- | --- | --- | --- |
| Visit & demographics | 17 | Demographics, arrival info, `esi` (the ESI level recorded for the visit), `disposition`; `previousdispo` = disposition of the prior visit | `esi` is a *categorical* dtype → `pd.to_numeric`; 2,457 rows have no ESI |
| **Chief complaints** | 200, `cc_*` | "Given the high number of unique values (> 1000) for chief complaint, the top 200 most frequent values, which comprise >90% of all visits, were retained as unique categories and all other values binned into 'Other'" | one-hot, object dtype `'0'/'1'` → `to_numeric`; a visit can carry several |
| Past medical history | 281 | "ICD-9 codes for past medical history (PMH) were mapped onto 281 clinically meaningful categories using the AHRQ Clinical Classification Software (CCS), such that each CCS category became a binary variable" | 0/1 |
| Outpatient medications | 48, `meds_*` | "Outpatient medications listed in the EHR as active at the time of patient encounter were binned into 48 therapeutic subgroups ... with each corresponding variable representing the number of medications in that subgroup" | integer counts, not flags |
| Triage vitals | 7, `triage_vital_*` | "Triage vital signs included systolic and diastolic blood pressure, pulse, respiratory rate, oxygen saturation, presence of oxygen device, and temperature. Values beyond physiologic limits were replaced with missing values" | numeric; NaN where missing or out-of-range |
| Historical labs & imaging | 416 | "A time-frame of one year from the date of patient encounter was used" — numeric labs: "the minimum, maximum, median, and the last recorded value"; categorical labs: "the number of tests, the number of positives, and the last recorded value"; imaging counted by category | 95 numeric × `_last/_min/_max/_median`; 9 × `_count/_npos`; 9 imaging/EKG `_count` |
| Prior utilisation | 3 | Prior ED visits, admissions, surgeries | counts |

## Reading rules — what a column can and cannot tell you

1. **`cc_*` is the visit's recorded chief complaint — a category of "reason for
   visit" — not a bedside finding.** [1] defines these columns purely as the top-200
   values of the chief-complaint field. The file contains **no consciousness
   assessment column** (computed: no AVPU, GCS or mental-status field among the
   972; the only bedside measurements are the 7 triage vitals). So
   `cc_unresponsive`, `cc_alteredmentalstatus`, `cc_seizure*`, `cc_syncope`,
   `cc_strokealert` name what the patient presented *for*; whether that state is
   current at triage is **not recorded** — and the data shows it varies (next
   section). [1] does not state who enters the chief complaint or at what moment.
2. **Labs are history, not today's results.** Per [1] they summarise the year
   *before* the encounter ("one year from the date of patient encounter").
   `glucose_last` is the last prior value. Never feed them to a rule that means
   "now".
3. **PMH flags are history too** — CCS categories of the patient's ICD-9 PMH [1].
4. **`meds_*` are counts per therapeutic subgroup [1]** — `meds_anticoagulants
   >= 1` is a legitimate "on an anticoagulant" fact; no drug names exist.
5. **Missing vitals are "not measured or out-of-range" [1], never "normal".**
   Computed: only 271 of 1,020 `cc_unresponsive` visits have a heart rate.
   *Why* they are missing is **[unverified]** — [1] says nothing about triage
   bypass; treat NaN as unknown and don't infer acuity from absence.
6. **The ESI label is a comparator, not ground truth.** [1] records it as the
   triage ESI at EDs that "utilize ... the Emergency Severity Index"; it is a
   practice label. Disagreement with our engine means one of: nurse deviated /
   standard silent / data lacks the deciding detail / *our mapping was wrong* —
   attribute before counting.

## Worked example: `cc_unresponsive` vs decision point A

The ESI handbook defines the decision-point-A criterion precisely [2, p.12]:

> "Unresponsiveness is defined as a patient who either: 1. Is nonverbal and not
> following commands (acutely) OR 2. Requires noxious stimulus (P or U on AVPU
> scale)"

AVPU is an examiner-applied consciousness scale [3]: **P** = "responds only to
painful stimuli applied by the examiner"; **U** = "does not ... respond to verbal
or painful stimuli". It is a bedside test; nothing in the dataset records it
(rule 1), and a caregiver cannot perform it.

The natural first mapping — `cc_unresponsive` → `obs.avpu = "U"` — asserts
criterion A-01 from the complaint label. Computed over all 1,020 `cc_unresponsive` visits, the recorded
ESI is **1: 429 · 2: 555 · 3: 33** (73% admitted). The label therefore covers
both patients meeting A-01 at the door and patients triaged ESI-2; the AVPU
mapping contradicts the recorded ESI in 58% of cases.

The floor-consistent mapping is weaker and better: `cc_unresponsive` → *reported
episode of unresponsiveness* → `B-01.new-altered-mental-status` (decision point B:
"exhibit newly altered mental status" [2, p.12]) → floor "at least ESI-2". That
agrees with 984/1,020 recorded labels (96%) and never asserts ESI-1. `obs.avpu`
must only be written from an eyes-on assessment (`assessed_via: observed` in
`rules/criteria.yaml`); no dataset label and no interview answer licenses it.

Reproduce the numbers:

```python
import pyreadr, pandas as pd
df = next(iter(pyreadr.read_r("data/yale_ed_visits.rdata").values()))
m = pd.to_numeric(df["cc_unresponsive"], errors="coerce") == 1
print(pd.to_numeric(df.loc[m, "esi"], errors="coerce").value_counts().sort_index())
print(pd.to_numeric(df.loc[m, "triage_vital_hr"], errors="coerce").notna().sum(), "of", m.sum())
```

**Method to reuse for every mapping line:** for each complaint label, tabulate
its recorded-ESI distribution and ask "which rule's *floor* agrees with the bulk
without overshooting?"; cite the handbook page for the rule; record which
provenance tier each fact came from (present in data / derived by documented
transformation / unavailable / persona-supplied).

## Where to read the data from

Task G and H should read the raw download (`yale_ed_visits.rdata`; convert once
to Parquet per Task F) — never the explorer workbook. `data/yale-explorer.xlsx`
is a 2,000-row, 22-column *browsing* view; its `chief_complaints` column strips
the `cc_` prefix for readability, which is exactly the hint a mapping author
needs. Raw columns keep it.

## References

1. Hong WS, Haimovich AD, Taylor RA. *Predicting hospital admission at emergency
   department triage using machine learning.* PLoS ONE 13(7): e0201016 (2018).
   https://doi.org/10.1371/journal.pone.0201016 — Materials and methods.
2. Emergency Nurses Association. *Emergency Severity Index (ESI) Implementation Handbook,
   5th ed.* 2023 — p.12 (decision points A/B
   definitions; repeated p.36). Local copy: `sources/ESI-Handbook-5th-Edition-3-2023.pdf`.
3. Crist C, Farrell MW. *AVPU Scale.* StatPearls, NCBI Bookshelf (NIH), updated 31 Jul 2026.
   https://www.ncbi.nlm.nih.gov/books/NBK538431/
