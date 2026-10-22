#!/usr/bin/env python3
"""Extract one real Yale visit as the seed for the report mock-ups (docs/img/make-report-mockups.py).

    python3 data/extract-report-case.py [row]      # default 466081 -> data/yale-report-case.json

Why this row: a non-ambulance (walk-in) visit with several complaints (chest pain, cough, fever),
an immunosuppressant on the active medication list, a rich past-medical-history vector, no triage
vitals recorded, nurse-assigned ESI 2 and admission — the richest case our rulebook can read
end to end (B-07 immunocompromised + fever fires verbatim from ESI v5 p.12). Found by ranking
non-ambulance ESI 1-2 visits by count of positive complaint, medication-class and PMH flags.

Everything written here is public, de-identified data (Hong et al. 2018). Column semantics per
data/yale-schema.md: meds_* are counts of active outpatient medications per therapeutic class;
PMH columns are AHRQ CCS categories from ICD-9 history; cc_* are chief-complaint labels.
"""
import json, os, sys
import pandas as pd, pyreadr

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = int(sys.argv[1]) if len(sys.argv) > 1 else 466081

MEDS_LABEL = {   # therapeutic subgroup -> plain label for the report
    "meds_immunosuppressants": "immunosuppressant", "meds_antibiotics": "antibiotic",
    "meds_antiasthmatics": "asthma/COPD inhaler or tablet", "meds_cardiacdrugs": "cardiac drug",
    "meds_cardiovascular": "cardiovascular drug", "meds_antihyperglycemics": "blood-sugar-lowering drug",
    "meds_cnsdrugs": "CNS drug", "meds_psychotherapeuticdrugs": "psychiatric drug",
    "meds_sedative/hypnotics": "sedative / sleeping tablet", "meds_musclerelaxants": "muscle relaxant",
    "meds_hormones": "hormone", "meds_gastrointestinal": "gastrointestinal drug", "meds_analgesics": "painkiller",
    "meds_antihistamines": "antihistamine", "meds_elect/caloric/h2o": "electrolyte / supplement",
    "meds_smokingdeterrents": "smoking-cessation aid", "meds_vitamins": "vitamin",
}
PMH_LABEL = {
    "asthma": "asthma", "copd": "COPD", "htn": "hypertension", "esophgealdx": "oesophageal disorder",
    "gastroent": "gastroenteritis (past)", "othergidx": "other GI disorder", "backproblem": "back problem",
    "pleurisy": "pleurisy / pleural effusion (past)", "othlowresp": "other lower-respiratory disease",
    "poisnotmed": "poisoning, non-medicinal (past)", "othnervdx": "other nervous-system disorder",
    "othskindx": "skin disorder", "otjointdx": "joint disorder", "unclassified": "(unclassified category)",
}

df = next(iter(pyreadr.read_r(os.path.join(HERE, "yale_ed_visits.rdata")).values()))
r = df.loc[ROW]
num = lambda c: pd.to_numeric(pd.Series([r[c]]), errors="coerce").iloc[0]
cc = [c for c in df.columns if c.startswith("cc_") and num(c) > 0]
meds = {c: int(num(c)) for c in df.columns if c.startswith("meds_") and num(c) > 0}
pmh = [c for c in PMH_LABEL if c in df.columns and num(c) > 0]
vit = {c: (None if pd.isna(num(c)) else float(num(c))) for c in df.columns if c.startswith("triage_vital_")}
case = {
    "yale_row": ROW, "source": "Hong WS, Haimovich AD, Taylor RA (2018) PLoS ONE 13(7): e0201016 - public, de-identified",
    "age": int(r["age"]), "gender": str(r["gender"]), "arrivalmode": str(r["arrivalmode"]), "lang": str(r["lang"]),
    "maritalstatus": str(r["maritalstatus"]), "employstatus": str(r["employstatus"]),
    "esi_recorded": str(r["esi"]), "disposition": str(r["disposition"]), "previousdispo": str(r["previousdispo"]),
    "n_edvisits": int(num("n_edvisits")) if "n_edvisits" in df.columns else None,
    "n_admissions": int(num("n_admissions")) if "n_admissions" in df.columns else None,
    "chief_complaints": cc,
    "med_classes": {c: {"count": n, "label": MEDS_LABEL.get(c, c[5:])} for c, n in meds.items()},
    "pmh": {c: PMH_LABEL[c] for c in pmh},
    "triage_vitals": vit,
}
out = os.path.join(HERE, "yale-report-case.json")
json.dump(case, open(out, "w"), indent=1)
print("wrote", out, "| cc", cc, "| meds", len(meds), "| pmh", len(pmh), "| vitals recorded:", any(v is not None for v in vit.values()))
