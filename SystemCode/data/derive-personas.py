"""Regenerate yale-persona-seeds.json from the raw Yale dataset.

The five prototype personas (prototype/personas.yaml) were seeded from these real
Yale rows; this script is the reproducible record of that selection. Run after
`bash data/download-yale.sh`; needs `pip install pyreadr pandas`.

Row numbers are 0-based positions (df.iloc) in the dataframe as loaded by pyreadr.
The `note` strings are our editorial labels for why each row was picked.
"""
import json, os, math
import pyreadr

HERE = os.path.dirname(os.path.abspath(__file__))
PICKS = [
    (1048, "elderly fall on anticoagulants"),
    (116,  "chest pain, ACS-suspect age"),
    (873,  "abdominal pain, pregnant"),
    (1339, "healthy young sore throat"),
    (744,  "fever, immunocompromised"),
]

def clean(v):
    if isinstance(v, float):
        return None if math.isnan(v) else v
    return v

df = next(iter(pyreadr.read_r(os.path.join(HERE, "yale_ed_visits.rdata")).values()))
seeds = []
for rownum, note in PICKS:
    row = df.iloc[rownum]
    seeds.append({
        "yale_row": rownum,
        "note": note,
        "age": int(row["age"]),
        "gender": clean(row["gender"]),
        "esi_label": clean(row["esi"]),
        "arrivalmode": clean(row["arrivalmode"]),
        "disposition": clean(row["disposition"]),
        "hr": clean(row["triage_vital_hr"]),
        "rr": clean(row["triage_vital_rr"]),
        "spo2": clean(row["triage_vital_o2"]),
        "on_anticoagulants": bool(row["meds_anticoagulants"]),
    })

out = os.path.join(HERE, "yale-persona-seeds.json")
with open(out, "w") as f:
    json.dump(seeds, f, indent=1)
print(f"wrote {out} ({len(seeds)} seeds)")
