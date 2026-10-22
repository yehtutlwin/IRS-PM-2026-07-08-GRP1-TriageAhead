"""Ablation: the rules replaced by "just ask the language model" - same cases.

A stratified sample of labelled Yale visits (N_PER_LEVEL per recorded ESI, seed
fixed) is described in plain structured text and the model is asked to assign
an ESI level, REPEATS times per case. Reported against the recorded ESI: exact
and within-one agreement, under-triage of recorded 1-2, and rerun consistency
(all repeats identical). The rulebook's floor on the same cases (task_g_full
mapping) is shown beside it. Runs on whichever LLM_BACKEND is configured; the
local model makes it quota-free (~600 calls).
    python3 experiments/task_g_llm_direct.py
"""
import json, os, re, sys, time
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype")); sys.path.insert(0, os.path.join(ROOT, "experiments"))
os.environ.setdefault("LLM_BACKEND", "ollama")
import llm, engine  # noqa: E402
import task_g_full as G  # noqa: E402  (imports run its module-level load; acceptable for the mapping helpers)

N_PER_LEVEL, REPEATS, SEED = 40, 3, 42
OUT = os.path.join(ROOT, "experiments", "out", "task-g-llm-direct")
t0 = time.time()

df = pd.read_parquet(os.path.join(ROOT, "data", "yale_ed_visits.parquet"), columns=G.NEED + ["gender"])
df = df[df["esi"].notna()].copy(); df["esi"] = df["esi"].astype(int)
rng = np.random.RandomState(SEED)
sample = pd.concat([df[df["esi"] == k].sample(N_PER_LEVEL, random_state=SEED) for k in (1, 2, 3, 4, 5)])
cc_cols = [c for c in G.NEED if c.startswith("cc_")]

def describe(row):
    cats = [c[3:] for c in cc_cols if row[c] == 1]
    vit = {"heart rate": row["triage_vital_hr"], "systolic BP": row["triage_vital_sbp"], "respiratory rate": row["triage_vital_rr"],
           "SpO2 %": row["triage_vital_o2"], "temperature F": row["triage_vital_temp"]}
    vit_s = ", ".join(f"{k} {v:g}" for k, v in vit.items() if pd.notna(v)) or "not recorded"
    meds = []
    if row["meds_anticoagulants"] >= 1: meds.append("on an anticoagulant")
    if row["meds_immunosuppressants"] >= 1: meds.append("on an immunosuppressant")
    hist = []
    if row["hivinfectn"] == 1: hist.append("HIV")
    if row["maintchemr"] == 1: hist.append("on maintenance chemotherapy")
    if row["coaghemrdx"] == 1: hist.append("coagulation/haemorrhagic disorder")
    return (f"Age {int(row['age']) if pd.notna(row['age']) else 'unknown'}, {str(row['gender']).lower()}. "
            f"Chief complaint(s): {', '.join(cats) or 'not recorded'}. Triage vitals: {vit_s}. "
            f"Medications: {', '.join(meds) or 'none noted'}. History: {', '.join(hist) or 'none noted'}.")

SYSTEM = ("You are an emergency triage nurse applying the Emergency Severity Index (ESI) v5. "
          "Given a structured triage record, answer with the single ESI level 1-5 you would assign, "
          "as one digit, then one short sentence of reasoning.")

def ask_level(text):
    out = llm.ask(f"{text}\n\nESI level (1-5)?", system=SYSTEM)
    m = re.search(r"\b([1-5])\b", out)
    return (int(m.group(1)) if m else None), out.strip()[:200]

rows = []
for i, (_, row) in enumerate(sample.iterrows()):
    text = describe(row)
    preds, rats = [], []
    for k in range(REPEATS):
        p, r = ask_level(text); preds.append(p); rats.append(r)
    rules = G.evaluate(tuple(sorted(G.facts_for(row, True).items())))
    rows.append({"esi": int(row["esi"]), "text": text, "preds": preds, "rationale": rats[0],
                 "rules_floor": rules["floor"], "rules_esi1": bool(rules["esi1"]), "rules_fired": rules["fired"] + rules["esi1"]})
    if (i + 1) % 25 == 0: print(f"{i+1}/{len(sample)} cases ({time.time()-t0:.0f}s)")

R = pd.DataFrame(rows)
first = R["preds"].map(lambda p: p[0])
valid = first.notna()
hi = R["esi"] <= 2
res = {"n_cases": int(len(R)), "repeats": REPEATS, "model": llm.MODEL_NAME(), "backend": llm.BACKEND,
       "parse_failures_first_run": int((~valid).sum()),
       "llm_exact_agreement": round((first == R["esi"]).mean(), 3),
       "llm_within_one": round(((first - R["esi"]).abs() <= 1).mean(), 3),
       "llm_under_triage_recorded_1_2": round(((first >= 3) & hi).sum() / hi.sum(), 3),
       "llm_over_triage_recorded_3_5": round(((first <= 2) & ~hi).sum() / (~hi).sum(), 3),
       "llm_rerun_all_identical": round(R["preds"].map(lambda p: len(set(p)) == 1).mean(), 3),
       "llm_rerun_max_spread": int(R["preds"].map(lambda p: max(x for x in p if x) - min(x for x in p if x) if any(p) else 0).max()),
       "rules_claim_rate": round((R["rules_floor"].notna() | R["rules_esi1"]).mean(), 3),
       "rules_claims_consistent_with_recorded_1_2": round(((R["rules_floor"].notna() | R["rules_esi1"]) & hi).sum() / max((R["rules_floor"].notna() | R["rules_esi1"]).sum(), 1), 3),
       "rules_rerun_all_identical": 1.0,
       "confusion_llm_first_run": pd.crosstab(R["esi"], first.fillna(0).astype(int)).to_dict()}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"summary": res, "cases": rows}, open(OUT + ".json", "w"), indent=1, default=str)
L = [f"# Ablation - LLM-direct triage vs the rulebook on the same cases", "",
     f"{res['n_cases']} labelled Yale visits ({N_PER_LEVEL} per recorded ESI level, seed {SEED}), each described as structured text and",
     f"given to the model ({res['backend']}: {res['model']}) {REPEATS} times. The rulebook's claim on the same case uses the",
     "task_g_full mapping (with vitals). Recorded ESI is a comparator, not truth.", "",
     "| | LLM-direct | rulebook |", "| --- | ---: | ---: |",
     f"| exact agreement with recorded ESI | {res['llm_exact_agreement']:.1%} | n/a (floor, not a level) |",
     f"| within one level | {res['llm_within_one']:.1%} | n/a |",
     f"| under-triage of recorded ESI 1-2 | **{res['llm_under_triage_recorded_1_2']:.1%}** | silent-miss semantics, see task-g-full |",
     f"| over-triage of recorded ESI 3-5 (called 1-2) | {res['llm_over_triage_recorded_3_5']:.1%} | overshoot on claimed cases only |",
     f"| makes a claim at all | 100% (always answers) | {res['rules_claim_rate']:.1%} |",
     f"| claims consistent with recorded 1-2 | - | {res['rules_claims_consistent_with_recorded_1_2']:.1%} |",
     f"| **rerun consistency** (3 identical answers) | **{res['llm_rerun_all_identical']:.1%}** (max spread {res['llm_rerun_max_spread']} levels) | 100% by construction |",
     "| explanation | one free-text sentence, unverifiable | rule id + handbook page + quoted span |",
     f"| parse failures (no digit in reply) | {res['parse_failures_first_run']} | - |", "",
     "Confusion (rows recorded ESI, columns model's first answer; 0 = no parseable answer):", "",
     "```", pd.crosstab(R["esi"], first.fillna(0).astype(int)).to_string(), "```", "",
     "Reading: the model always produces a level - including for the majority of cases where the rulebook",
     "honestly declines because the record lacks the deciding details - and its answers vary between identical",
     "runs. The rulebook never overshoots on repeat, never invents a level, and every claim is traceable; its",
     "cost is reach. Which property matters more is the product argument, made in the report's findings.", ""]
open(OUT + ".md", "w").write("\n".join(L)); print(f"wrote {OUT}.md ({time.time()-t0:.0f}s)"); print(json.dumps(res, indent=1)[:600])
