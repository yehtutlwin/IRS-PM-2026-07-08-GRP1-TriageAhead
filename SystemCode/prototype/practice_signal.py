"""Practice signal - the learned model's second lane on the nurse report (design record,
"Two lanes"; TODO item 6). One feature vocabulary, defined here once, is built two ways:
from the Yale visit columns at training time (experiments/practice_signal_train.py) and
from the interview facts at run time (signal()). The lane is advisory and NEVER moves the
ESI floor: it says how similar past visits were triaged, by nurses, at one US site.

Pre-arrival features only - what a caregiver can tell us: age, the coarse complaint
groups the interview extracts, injury mechanism, fever, anticoagulation, immune status.
No vitals, no labs (the report is written before the patient is seen).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "models", "practice-signal.joblib")
META = os.path.join(HERE, "models", "practice-signal.json")

# interview complaint.category value -> Yale cc_* columns that mean the same coarse thing
GROUPS = {
    "chest_pain": ["chestpain", "chesttightness"],
    "abdominal_pain": ["abdominalpain", "abdominalcramping", "abdominaldistention", "abdominalpainpregnant", "epigastricpain", "flankpain"],
    "injury_fall": ["fall", "fall>65", "multiplefalls", "trauma", "fulltrauma", "modifiedtrauma", "headinjury", "motorvehiclecrash", "motorcyclecrash",   # the saved model's feature name (trained before the v2 rename of the category to `injury`); facts_vector maps the v2 categories to it
                    "assaultvictim", "ankleinjury", "arminjury", "facialinjury", "fingerinjury", "footinjury", "handinjury", "kneeinjury", "leginjury",
                    "ribinjury", "shoulderinjury", "thumbinjury", "toeinjury", "wristinjury", "eyeinjury", "laceration", "extremitylaceration",
                    "faciallaceration", "headlaceration", "burn"],
    "breathing": ["breathingdifficulty", "breathingproblem", "shortnessofbreath", "dyspnea", "respiratorydistress", "wheezing", "asthma"],
    "fever": ["fever", "fever-75yearsorolder", "fever-9weeksto74years", "feverimmunocompromised", "chills"],
    "sore_throat": ["sorethroat"],
    "dizziness": ["dizziness", "nearsyncope", "syncope"],
    "nosebleed": ["epistaxis"],
    "eye_problem": ["eyepain", "eyeproblem", "eyeredness", "foreignbodyineye", "blurredvision", "conjunctivitis"],
    "neuro_symptoms": ["strokealert", "weakness", "extremityweakness", "numbness", "neurologicproblem", "confusion", "alteredmentalstatus",
                       "headache-newonsetornewsymptoms", "seizure-newonset", "seizure-priorhxof", "seizures", "lossofconsciousness", "unresponsive"],
}
MECH = {"fall": ["fall", "fall>65", "multiplefalls"], "road_accident": ["motorvehiclecrash", "motorcyclecrash"], "assault": ["assaultvictim"]}
FEATURES = ["age"] + [f"cx_{g}" for g in GROUPS] + ["cx_other"] + [f"mech_{m}" for m in MECH] + ["anticoagulant", "immunocompromised"]


def yale_frame(df):
    """Feature frame from the Yale visit table (columns cc_*, meds_*, age). Same vocabulary as facts_vector."""
    import numpy as np, pandas as pd
    X = pd.DataFrame(index=df.index)
    X["age"] = pd.to_numeric(df["age"], errors="coerce").astype("float32")
    def flag(cols):
        cols = [f"cc_{c}" for c in cols if f"cc_{c}" in df.columns]
        return (pd.concat([pd.to_numeric(df[c], errors="coerce").fillna(0) for c in cols], axis=1).max(axis=1) > 0).astype("float32") if cols else 0.0
    grouped = set()
    for g, cols in GROUPS.items():
        X[f"cx_{g}"] = flag(cols); grouped.update(cols)
    other_cols = [c[3:] for c in df.columns if c.startswith("cc_") and c[3:] not in grouped]
    X["cx_other"] = flag(other_cols)
    for m, cols in MECH.items():
        X[f"mech_{m}"] = flag(cols)
    X["anticoagulant"] = (pd.to_numeric(df["meds_anticoagulants"], errors="coerce").fillna(0) > 0).astype("float32")
    X["immunocompromised"] = ((pd.to_numeric(df["meds_immunosuppressants"], errors="coerce").fillna(0) > 0)
                              | (pd.to_numeric(df["meds_antineoplastics"], errors="coerce").fillna(0) > 0)
                              | (pd.to_numeric(df["cc_feverimmunocompromised"], errors="coerce").fillna(0) > 0)).astype("float32")
    return X[FEATURES]


def facts_vector(facts):
    """The same features from the interview's fact store. Returns (row dict, basis list) or (None, []) if nothing to go on."""
    cats = facts.resolve("complaint.category") or []
    cats = cats if isinstance(cats, list) else [cats]
    row = {f: 0.0 for f in FEATURES}
    basis = []
    age = facts.resolve("patient.age")
    row["age"] = float(age) if isinstance(age, (int, float)) else float("nan")
    if isinstance(age, (int, float)): basis.append(f"age {int(age)}")
    for c in cats:
        name = "injury_fall" if c in ("injury", "head_injury", "wound", "burn", "limb_pain_or_swelling") else c   # the model was trained with the v1 category name
        key = f"cx_{name}" if f"cx_{name}" in row else "cx_other"
        row[key] = 1.0; basis.append("another complaint" if key == "cx_other" else str(c).replace("_", " "))
    if facts.resolve("complaint.fever") is True:
        row["cx_fever"] = 1.0; basis.append("fever")
    mech = facts.resolve("E.mechanism")
    if mech in MECH:
        row[f"mech_{mech}"] = 1.0; basis.append(str(mech).replace("_", " "))
    if facts.resolve("M.anticoagulant") is True:
        row["anticoagulant"] = 1.0; basis.append("anticoagulated")
    if facts.resolve("history.immunocompromised") is True:
        row["immunocompromised"] = 1.0; basis.append("immunocompromised")
    if not cats and not basis:
        return None, []
    return row, basis


_cache = {}


def load():
    if "m" in _cache:
        return _cache["m"], _cache["meta"]
    if not (os.path.exists(MODEL) and os.path.exists(META)):
        return None, None
    import joblib
    _cache["m"] = joblib.load(MODEL); _cache["meta"] = json.load(open(META))
    return _cache["m"], _cache["meta"]


def signal(facts):
    """Advisory lane: {'share': p, 'band': 'high'|'mixed'|'low', 'basis': [...], 'meta': {...}} or None."""
    model, meta = load()
    if model is None:
        return None
    row, basis = facts_vector(facts)
    if row is None:
        return None
    import pandas as pd
    p = float(model.predict_proba(pd.DataFrame([row], columns=FEATURES))[0, 1])
    hi, lo = meta.get("band_high", 0.5), meta.get("band_low", 0.2)
    band = "high" if p >= hi else ("low" if p <= lo else "mixed")
    return {"share": round(p, 3), "band": band, "basis": basis, "meta": meta}


def wording(sig):
    """The one sentence the nurse reads: the band only. The share, the base rate and the model's
    figures belong on the "about this signal" page and in the evaluation, not on the report
    (team decision 19 Sep 2026: one sentence per lane, no numbers that read as a level)."""
    basis = ", ".join(sig["basis"]).replace("injury fall", "fall injury").replace("another complaint", "other complaint")
    return {"high": f"Most similar past visits ({basis}) were ESI 1 or 2.",
            "mixed": f"About half of similar past visits ({basis}) were ESI 1 or 2.",
            "low": f"Most similar past visits ({basis}) were ESI 3, 4 or 5."}[sig["band"]]
