"""Second reading of the practice cases (issue #68): a model from another provider reads each printed case and writes
the facts in our field vocabulary, without seeing our test files. Then the two fact sets are compared field by field.
    .venv/bin/python experiments/second_reading.py <case-texts.json> <out dir> [backend] [model]
case-texts.json: [{"id": ..., "text": <the case as printed>}]. Resumable: state.json in the out dir; stops itself after
SR_BUDGET_SECONDS (default 500) so it can run in slices. Writes second-reading.json (the model's facts per case).
"""
import os, sys, json, time, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "experiments", "rulegen")); import backends  # noqa: E402
texts_path, out_dir = sys.argv[1], sys.argv[2]
backend = sys.argv[3] if len(sys.argv) > 3 else "agy"; model = sys.argv[4] if len(sys.argv) > 4 else "gemini-3.1-pro-high"
os.makedirs(out_dir, exist_ok=True); STATE = os.path.join(out_dir, "state.json")
BUDGET = float(os.environ.get("SR_BUDGET_SECONDS", "500")); T0 = time.time(); BATCH = int(os.environ.get("SR_BATCH", "8"))
F = yaml.safe_load(open(os.path.join(ROOT, "rules", "fields.yaml")))["fields"]
def line(name, s):
    t = s["type"]; kind = ("one of: " + ", ".join(s["values"])) if t == "enum" else {"bool": "true/false", "number": "number", "text": "short text", "list": "list of short texts"}[t]
    return f"- {name} ({kind}): {s['gloss']}"      # the run of 11 Oct 2026 used the first sentence of `meaning`; gloss since 13 Oct
FIELDS = "\n".join(line(n, s) for n, s in F.items())
SYSTEM = f"""You transcribe emergency-department triage practice cases, printed in a textbook, into facts.
For each case, write every fact the printed text states that fits one of the allowed fields below. Use only the text:
never add what the text does not say, never infer a value (if the text does not give the sex, do not write it; a
pronoun does count as stating it). Numbers exactly as printed (temperature in Celsius to one decimal if printed in
Fahrenheit, with the conversion noted nowhere else). A yes/no field is true only when the text states the finding and
false only when the text denies it. A finding only a clinician could make (a measured vital sign, an examination
finding, 'unresponsive', 'intubated') carries "status": "observed". Put details that fit no field into complaint.text.
Do not write the triage level.

Return ONLY JSON: {{"rules": [{{"id": "<case id as given>", "facts": [{{"field": "...", "value": ..., "status": "observed"}}, ...]}}, ...]}}
(the key is named "rules" for the tool's sake; each item is one case).

Allowed fields:
{FIELDS}
"""
cases = json.load(open(texts_path)); cases = [c for c in cases if c.get("text")]
st = json.load(open(STATE)) if os.path.exists(STATE) else {"done": {}, "failed": []}
todo = [c for c in cases if c["id"] not in st["done"]]
print(f"{len(cases)} cases, {len(st['done'])} done, {len(todo)} to do", flush=True)
for i in range(0, len(todo), BATCH):
    if time.time() - T0 > BUDGET: print("budget reached; run again to continue", flush=True); break
    batch = todo[i:i + BATCH]
    prompt = "Cases:\n\n" + "\n\n".join(f"[case id: {c['id']}]\n{c['text']}" for c in batch)
    got = None
    for attempt in range(3):
        try:
            got, raw, used = backends.ask_json(backend, prompt, SYSTEM, model, ROOT)
        except Exception as e:
            raw, used, got = str(e), model, None
        if isinstance(got, dict) and isinstance(got.get("rules"), list) and got["rules"]: break
        print(f"  batch {i // BATCH}: attempt {attempt + 1} gave no usable JSON ({str(raw)[:160]!r})", flush=True); time.sleep(20 * (attempt + 1))
    if not (isinstance(got, dict) and isinstance(got.get("rules"), list) and got["rules"]):
        st["failed"].append([c["id"] for c in batch]); json.dump(st, open(STATE, "w")); continue
    for item in got["rules"]:
        if isinstance(item, dict) and item.get("id") and isinstance(item.get("facts"), list):
            st["done"][item["id"]] = {"facts": item["facts"], "model": used}
    json.dump(st, open(STATE, "w")); print(f"  batch {i // BATCH}: {len(got['rules'])} cases ({used})", flush=True)
json.dump(st["done"], open(os.path.join(out_dir, "second-reading.json"), "w"), indent=1)
print("done", len(st["done"]), "of", len(cases), "| failed batches:", len(st["failed"]), flush=True)
