"""Build data/yale-explorer.xlsx - a browsable Excel view of the Yale ED dataset
(560k rows x 972 cols is unusable raw). Sheets: README, a 2,000-row curated
sample, ESI/complaint/vitals summaries, and the full column dictionary.
Needs the raw download (data/download-yale.sh) + pip install pyreadr pandas openpyxl."""
import os, sys, json
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RDATA = os.path.join(HERE, "yale_ed_visits.rdata")
OUT = os.path.join(HERE, "yale-explorer.xlsx")
SAMPLE_N = 2000
SEED = 42  # fixed so the sample is reproducible

# allow a pre-pickled frame as argv[1] to skip the ~60s rdata parse
if len(sys.argv) > 1 and sys.argv[1].endswith(".pkl"):
    df = pd.read_pickle(sys.argv[1])
else:
    import pyreadr
    df = next(iter(pyreadr.read_r(RDATA).values()))

cc_cols = [c for c in df.columns if c.startswith("cc_")]
meds_cols = [c for c in df.columns if c.startswith("meds_")]
vital_cols = [c for c in df.columns if c.startswith("triage_")]

cc_num = df[cc_cols].apply(pd.to_numeric, errors="coerce")
esi_num = pd.to_numeric(df["esi"], errors="coerce")
admit = df["disposition"].eq("Admit")

def complaint_label(col):
    return col[3:]

# ---- Sample sheet: curated columns + readable complaint list ----
core = ["dep_name", "esi", "age", "gender", "race", "insurance_status",
        "arrivalmode", "arrivalmonth", "arrivalhour_bin", "previousdispo",
        "disposition"] + vital_cols
rng_sample = df.sample(n=SAMPLE_N, random_state=SEED).sort_index()
sample_cc = cc_num.loc[rng_sample.index]
sample = rng_sample[core].copy()
sample.insert(2, "chief_complaints",
              sample_cc.apply(lambda r: ", ".join(complaint_label(c) for c in cc_cols
                                                  if r[c] == 1) or "(none flagged)", axis=1))
sample.insert(0, "yale_row", rng_sample.index)
sample["n_med_classes"] = df[meds_cols].apply(pd.to_numeric, errors="coerce") \
                                       .loc[rng_sample.index].gt(0).sum(axis=1)

# ---- Persona seed rows: the real visits our five test personas were novelized
# from (prototype/personas.yaml); shown raw so the fiction can be checked ----
personas = yaml.safe_load(open(os.path.join(HERE, "..", "prototype", "personas.yaml")))
# only Yale-seeded personas have an integer yale_row; handbook-novelized or hand-written
# ones (yale_row null / "v4-case-44") are not dataset rows and are skipped here
personas = [p for p in personas if isinstance(p.get("yale_row"), int)]
seed_rows = [p["yale_row"] for p in personas]
seed_df = df.iloc[seed_rows]
seed_cc = cc_num.iloc[seed_rows]
seeds = seed_df[core].copy()
seeds.insert(0, "persona", [p["id"] for p in personas])
seeds.insert(1, "yale_row", seed_rows)
seeds.insert(2, "expect_floor", [p["expect_floor"] or "(none)" for p in personas])
seeds.insert(3, "expect_rules", [", ".join(p["expect_rules"]) or "-" for p in personas])
seeds.insert(6, "chief_complaints",
             seed_cc.apply(lambda r: ", ".join(complaint_label(c) for c in cc_cols
                                               if r[c] == 1) or "(none flagged)", axis=1).values)
seeds.insert(7, "meds_anticoagulants",
             pd.to_numeric(seed_df["meds_anticoagulants"], errors="coerce").values)

# the same five rows also appear inside the random sample, flagged by persona id
persona_by_row = dict(zip(seed_rows, (p["id"] for p in personas)))
seed_in_sample = seeds.drop(columns=["expect_floor", "expect_rules", "meds_anticoagulants"])
seed_in_sample["n_med_classes"] = df[meds_cols].apply(pd.to_numeric, errors="coerce") \
                                               .iloc[seed_rows].gt(0).sum(axis=1).values
sample.insert(1, "persona", sample["yale_row"].map(persona_by_row).fillna(""))
sample = pd.concat([sample[~sample.yale_row.isin(seed_rows)], seed_in_sample]) \
           .sort_values("yale_row")

# ---- ESI overview ----
esi_overview = pd.DataFrame({
    "visits": esi_num.value_counts(dropna=False).sort_index(),
})
esi_overview["share_%"] = (esi_overview.visits / len(df) * 100).round(1)
esi_overview["admit_rate_%"] = df.groupby(esi_num, dropna=False)["disposition"] \
                                 .apply(lambda s: s.eq("Admit").mean() * 100).round(1)
esi_overview.index.name = "esi (1=most urgent)"

# ---- Top complaints ----
rows = []
for c in cc_cols:
    mask = cc_num[c] == 1
    n = int(mask.sum())
    if n == 0:
        continue
    rows.append({"complaint": complaint_label(c), "visits": n,
                 "mean_esi": round(esi_num[mask].mean(), 2),
                 "admit_rate_%": round(admit[mask].mean() * 100, 1)})
complaints = pd.DataFrame(rows).sort_values("visits", ascending=False).head(60)

# ---- Vitals by ESI ----
vit = df[vital_cols].apply(pd.to_numeric, errors="coerce")
vitals_by_esi = vit.groupby(esi_num).median().round(1)
vitals_by_esi.index.name = "esi"

# ---- Column dictionary ----
def group(c):
    if c.startswith("cc_"): return "chief complaint flag (0/1)"
    if c.startswith("meds_"): return "outpatient med class count"
    if c.startswith("triage_"): return "triage vital"
    if c in core or c in ("esi", "ethnicity", "lang", "religion", "maritalstatus",
                          "employstatus", "arrivalday"): return "demographics/visit"
    return "prior labs/history"
coldict = pd.DataFrame({
    "column": df.columns,
    "group": [group(c) for c in df.columns],
    "dtype": [str(t) for t in df.dtypes],
    "non_null": df.notna().sum().values,
    "unique": [df[c].nunique() for c in df.columns],
})

readme = pd.DataFrame({"Yale ED visits - explorer workbook": [
    f"Source: {os.path.basename(RDATA)} - 560,486 ED visits, 972 columns (Yale admission-prediction study).",
    "This workbook is a browsable view; the full data stays in the .rdata file.",
    "",
    f"sample: {SAMPLE_N} random visits (seed {SEED}), curated columns; 'yale_row' matches "
    "the row numbers used in yale-persona-seeds.json; 'chief_complaints' condenses the 200 cc_* flags.",
    "persona_seeds: the five REAL rows our test personas were novelized from, raw - "
    "richer than yale-persona-seeds.json (all complaint flags, full vitals) so the "
    "fiction in prototype/personas.yaml can be checked against the data.",
    "NOTE: chief_complaints strips the cc_ prefix for readability - these are the triage "
    "CHIEF COMPLAINT flags (reason for visit), never bedside observations; see data/yale-schema.md "
    "before mapping any label to a rule fact.",
    "esi_overview: visit count, share and admission rate per nurse-assigned ESI level.",
    "top_complaints: the 60 most common complaint flags with mean ESI and admit rate.",
    "vitals_by_esi: median triage vitals per ESI level.",
    "column_dictionary: all 972 raw columns with type, fill and cardinality.",
    "",
    "Regenerate: python data/make-yale-explorer.py",
]})

with pd.ExcelWriter(OUT, engine="openpyxl") as xl:
    readme.to_excel(xl, sheet_name="README", index=False)
    sample.to_excel(xl, sheet_name="sample", index=False)
    seeds.to_excel(xl, sheet_name="persona_seeds", index=False)
    esi_overview.to_excel(xl, sheet_name="esi_overview")
    complaints.to_excel(xl, sheet_name="top_complaints", index=False)
    vitals_by_esi.to_excel(xl, sheet_name="vitals_by_esi")
    coldict.to_excel(xl, sheet_name="column_dictionary", index=False)
print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB)")
