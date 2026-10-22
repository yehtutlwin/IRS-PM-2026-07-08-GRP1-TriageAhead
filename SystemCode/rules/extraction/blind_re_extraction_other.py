"""Blind extraction by a model from another provider (OpenAI through the Codex CLI, Google through the Gemini CLI or
Antigravity CLI), with the same brief as the Claude blind re-extractions. The model is given the handbook text and nothing else:
the call runs in an empty working directory, read-only, with no tools. The whole handbook is in every call so that
cross-page contradictions can be seen; each call asks for the entries of a few pages.
    .venv/bin/python rules/extraction/blind_re_extraction_other.py <backend> <label> <handbook-pages.txt> <out-dir> [model]
backend: codex-cli | gemini-cli | agy      (experiments/rulegen/backends.py)
"""
import os, re, sys, json, tempfile, time, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "experiments", "rulegen")); sys.path.insert(0, os.path.join(ROOT, "prototype"))
import backends
backend, label, pages_path, out_dir = sys.argv[1:5]; model = sys.argv[5] if len(sys.argv) > 5 else None
text = open(pages_path).read()
CHUNKS = [[1, 2, 5], [6, 7], [9, 10], [11, 12], [13], [14], [15], [19, 20], [23], [24, 25], [27, 29, 30]]
SYSTEM = """You are doing an independent, from-scratch extraction of triage rules from one document, the Emergency Severity Index (ESI) Implementation Handbook, 5th edition (2023). Your reading will be compared with other independent readings to find where readers differ. Accuracy and completeness matter more than brevity. Use only the handbook text given below. Do not use any tool, file or outside knowledge of this handbook.

Background: ESI has five levels (1 most urgent). Four decision points: A (does the patient need an immediate lifesaving intervention? yes means level 1), B (is this a high-risk situation, or new confusion/lethargy/disorientation, or severe pain or distress? yes means level 2), C (how many resources will be needed? none means 5, one means 4, two or more means 3), D (are the vital signs in the danger zone? if so reassess, possibly up to level 2).

TASK. For the printed pages named in the request, produce every statement that assigns a triage level, conditions a level, tells the nurse to consider or reassess a level, defines what counts toward a level (for example what counts as a resource or as a lifesaving intervention), or states a rule about how levels may be used or changed. Miss nothing. Add nothing the text does not say.

THE HARDEST PART: HOW STRONG IS THE HANDBOOK'S VERB. Record what the sentence itself licenses, not what a clinician would probably do.
- "should be assigned / triaged as / designated ESI level 2", "is assigned", "meets level-1 criteria", "warrants an ESI 2 designation": an assignment.
- "should be considered", "consider assigning", "may", "may include", "can help the nurse determine whether", "should be evaluated for", "should be carefully evaluated": NOT an assignment. Use effect consider_level_2 (or none if no level is in view) and copy the soft verb into `verb`.
- A statement that only says something is "high risk", "time sensitive", "concerning" or "a red flag" without naming a level: record what you think follows, set interpretation to "interpreted", and say why in `note`.
- A list of questions to ask, or of examples of a category: say in `note` whether the text makes each item sufficient alone.
- Where two places in the handbook give different strengths for the same thing (a figure and the running text, for example), record both and say so in `note`.

OUTPUT. Reply with ONE JSON object and nothing else: {"rules": [entry, ...], "facts": [fact, ...]}.
Each entry:
{"id": "B-012",                      // your own running id: A-, B-, C-, D- by decision point, N- for none
 "page": 12,                         // printed page number of the quote
 "also_on": [6, 30],                 // other printed pages where the SAME criterion is printed again; write a criterion once, not once per page; omit if none
 "span": "exact contiguous words copied from that page, at most about 25 words",
 "verb": "the handbook's own words that carry the strength, copied exactly",
 "decision_point": "B",              // A | B | C | D | none
 "kind": "rule",                     // rule | definition | usage | negative (says explicitly that NO higher level follows) | context (something to bear in mind; no level assigned or asked to be considered) | example (a worked case with its level)
 "effect": "assign_level_2",         // assign_level_1 | assign_level_2 | consider_level_2 | reassess_uptriage | resource_band | consider_isolation | none
 "who_can_supply": "reported_directly",  // kind rule only: reported_directly (a family member with no clinical training could state this fact as worded) | reported_as_everyday_signs (they could not state the clinical finding but could describe everyday signs of it; say which in note) | observed (needs a clinician) | vitals (needs a measurement)
 "when": {"all": [{"fact": "is_immunocompromised", "is": true}, {"fact": "has_fever", "is": true}]},   // kind rule only; all / any, nested as needed; leaves use is, in, gte, gt, lt, lte
 "interpretation": "verbatim",       // verbatim (condition AND effect are what the sentence says) | effect_inferred (facts as stated, level is your inference) | interpreted (you chose a reading of vague or ambiguous wording; say which and what the other reading is, in note)
 "note": "optional"}
Each fact: {"name": "has_fever", "meaning": "one plain sentence a non-clinician would understand", "type": "bool"}   // type: bool | number | enum | text ; add "values" for enum

RULES FOR CONDITIONS. One entry per distinct criterion; if a sentence lists several independently sufficient criteria, one entry each. Two things needed together go under "all". Keep distinct things as distinct facts: do not bundle "pregnant" with "postpartum" or "suicidal" with "homicidal" unless the sentence treats them as one; for "pregnant or postpartum" use "any" over two facts. Use numbers exactly as given, with the unit in the fact name (fall_height_meters, temperature_celsius, age_days, age_months, age_years). Do not invent thresholds: for vague words ("elderly", "constellation", "severe") keep one yes/no fact naming the vague thing and set interpretation to "interpreted". Do not generalise an example into a category or narrow a category to its example. Fact names are lower_snake_case, named for the finding being present; one fact, one name: reuse the names in the list of facts already defined that the request gives you.

Before answering, re-read the pages named in the request paragraph by paragraph and check: every level-conditioning statement, every soft verb, every qualifier and exception is captured; every entry with an assign effect has an assignment verb."""
os.makedirs(out_dir, exist_ok=True); cwd = tempfile.mkdtemp(prefix="blind-empty-")
# Resumable: progress is saved after every page group, and a run stops by itself after BUDGET seconds so that it can be
# invoked again to continue (each invocation stays inside the caller's time limit).
STATE = os.path.join(out_dir, "state.json"); BUDGET = float(os.environ.get("BLIND_BUDGET_SECONDS", "400")); T0 = time.time()
st = json.load(open(STATE)) if os.path.exists(STATE) else {"entries": [], "facts": {}, "log": []}
entries, facts, log = st["entries"], st["facts"], st["log"]
done = {tuple(l["pages"]) for l in log if l.get("ok")}
def save(): json.dump({"entries": entries, "facts": facts, "log": log}, open(STATE, "w"))
for chunk in CHUNKS:
    if tuple(chunk) in done: continue
    if time.time() - T0 > BUDGET: print("budget reached; run again to continue", flush=True); break
    known = "\n".join(f"- {n}: {f.get('meaning','')}" for n, f in facts.items()) or "(none yet)"
    prompt = (f"Extract the entries for printed page(s) {', '.join(map(str, chunk))} ONLY (skip reference lists). The whole handbook is given for context.\n\n"
              f"Facts already defined (reuse these names; add new facts only for new things):\n{known}\n\n===== HANDBOOK TEXT =====\n{text}")
    got = None
    for attempt in range(3):
        try:
            got, raw, used = backends.ask_json(backend, prompt, SYSTEM, model, cwd)
        except Exception as e:
            raw, used, got = str(e), model, None
        if isinstance(got, dict) and isinstance(got.get("rules"), list) and got["rules"]: break
        print(f"  pages {chunk}: attempt {attempt + 1} gave no usable JSON ({str(raw)[:160]!r})", flush=True); time.sleep(20 * (attempt + 1))
    if not (isinstance(got, dict) and isinstance(got.get("rules"), list) and got["rules"]):
        log.append({"pages": chunk, "ok": False}); save(); continue
    for e in got["rules"]:
        if isinstance(e, dict) and e.get("span") and e.get("page"): e["id"] = f"{label}-{len(entries) + 1:03d}"; entries.append(e)
    got_facts = got.get("facts", []) or []
    if isinstance(got_facts, dict):  # some models key the facts by name instead of listing them
        got_facts = [{"name": n, **(f if isinstance(f, dict) else {"meaning": str(f)})} for n, f in got_facts.items()]
    for f in got_facts:
        if isinstance(f, dict) and f.get("name") and f["name"] not in facts: facts[f["name"]] = f
    log.append({"pages": chunk, "ok": True, "entries": len(got["rules"]), "model": used}); print(f"  pages {chunk}: {len(got['rules'])} entries ({used})", flush=True); save()
yaml.safe_dump({"entries": entries, "facts": list(facts.values())}, open(os.path.join(out_dir, "rules.yaml"), "w"), sort_keys=False, allow_unicode=True, width=160)
json.dump({"backend": backend, "label": label, "model": model, "chunks": log}, open(os.path.join(out_dir, "run.json"), "w"), indent=1)
remaining = [c for c in CHUNKS if tuple(c) not in {tuple(l["pages"]) for l in log if l.get("ok")}]
print("entries", len(entries), "facts", len(facts), "page groups still to do:", remaining)
