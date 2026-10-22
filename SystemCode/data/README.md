# Datasets

The data set itself is not in the repository; each person fetches their own copy. In the repository are the scripts,
the persona-seeds file, the report-case file and the explorer workbook.

## Yale ED visits (public) — used for persona seeding

~560k real ED visits with triage vitals, chief-complaint flags, medications, and the
nurse-assigned ESI level. Public dataset from the Yale admission-prediction study
([source paper](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0201016) ·
[authors' GitHub](https://github.com/yaleemmlc/admissionprediction) ·
[Kaggle mirror](https://www.kaggle.com/datasets/maalona/hospital-triage-and-patient-history-data)).

```bash
bash data/download-yale.sh     # ~99 MB -> data/yale_ed_visits.rdata
```

Load in Python (`pip install pyreadr pandas`):

```python
import pyreadr
df = next(iter(pyreadr.read_r("data/yale_ed_visits.rdata").values()))
# gotchas: esi comes as a categorical; cc_* columns are object dtype with '0'/'1'
# values -> use pd.to_numeric(..., errors="coerce") before filtering
```

`yale-persona-seeds.json` (committed) records the real Yale rows the first five Yale-seeded
personas were taken from (row number, age, ESI label, key flags) — e.g. persona P1
comes from row 1048, an 87-year-old man, fall, on anticoagulants, nurse ESI 2.
`derive-personas.py` regenerates that file from the raw download — the reproducible
record of how the rows were picked.

**Before mapping any Yale column to a rule fact, read [yale-schema.md](yale-schema.md)** — what each of the 972 columns can and cannot tell you (chief complaints are not observations; labs are history; missing vitals carry signal), with the `cc_unresponsive` mapping as the worked example.

`yale-report-case.json` (committed) is one visit — row 466081 — extracted by `extract-report-case.py` as the seed for the
nurse's report mock-ups in the proposal; the script's docstring says why that row.

## Others (references)

- **NHAMCS** (US national ED survey, instant download): <https://www.cdc.gov/nchs/nhamcs/about/index.html>
- **KTAS mistriage set** (small Korean set with expert-corrected labels; methodology
  reference for the under-triage analysis): <https://plos.figshare.com/articles/dataset/Triage_accuracy_and_causes_of_mistriage_using_the_Korean_Triage_and_Acuity_Scale/9779267>

## Browsing the Yale data without the download: `yale-explorer.xlsx`

Committed (public, de-identified, ~234 KB) so nobody needs the 560k-row raw file just to look.
Sheets: `README`, a reproducible 2,000-row random `sample` with a readable chief-complaint
column, `persona_seeds` (the five real visits the Yale-seeded personas P1–P5 were novelized
from — shown raw so the fiction can be checked; those rows are also flagged inside the sample),
`esi_overview`, `top_complaints`, `vitals_by_esi`, and the full 972-column `column_dictionary`.
Regenerate after the raw download with `python data/make-yale-explorer.py` (fixed seed 42 —
same sample every time). Personas not seeded from Yale (handbook-novelized or hand-written,
`yale_row` non-integer) are deliberately absent: this workbook is a dataset view, not a persona inventory.
