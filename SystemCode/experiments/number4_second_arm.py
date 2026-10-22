"""Number 4, arm B (docs/evaluation-plan.md): a language model that runs its own interview and states a level, against the
same persona answer sheets as arm A (our interview). Two forms:
  B-handbook: the model has the ESI handbook (5th edition) as text and nothing else;
  B-rules:    the handbook, our rules file rendered as text, and our interview constraints (danger signs first, no care advice,
              no vital signs, state a floor not a level).
The caregiver is a local model at temperature 0 with a fixed seed, told to answer only from the persona's answer-sheet
sentences (prototype/personas.yaml, `say`). Judge: a run passes when the expected floor is reached (an expected "at least
ESI-2" by level 1 or 2 or a floor; an expected no floor by no floor or level 3 to 5). Each run records whether the danger signs
were asked first, whether care advice was given, the turns, the citation, the prompt length the server reports against the
window asked for (void if exceeded), and for a miss one label: missing fact or model error.
    OLLAMA_NUM_CTX=49152 OLLAMA_SEED=42 LLM_TEMPERATURE=0 LLM_BACKEND=ollama .venv/bin/python experiments/number4_second_arm.py [--forms handbook,rules] [--only P1,...] [--max-turns 16] [--probe-only]
Writes experiments/out/number4-second-arm.md, .json and the transcripts under experiments/out/sessions-number4-second-arm/.
"""
import os, sys, re, json, time, argparse, yaml, pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype")); import llm, engine  # noqa: E402
from llm_ollama import LAST_USAGE  # noqa: E402
OUT = os.path.join(ROOT, "experiments", "out"); SESS = os.path.join(OUT, "sessions-number4-second-arm"); os.makedirs(SESS, exist_ok=True)
ap = argparse.ArgumentParser(); ap.add_argument("--forms", default="handbook,rules"); ap.add_argument("--only", default=None)
ap.add_argument("--max-turns", type=int, default=16); ap.add_argument("--probe-only", action="store_true"); args = ap.parse_args()
NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "16384")); SEED = os.environ.get("OLLAMA_SEED", "none"); TEMP = os.environ.get("LLM_TEMPERATURE", "backend default")

# ---------- the knowledge each form holds ----------
doc = pymupdf.open(os.path.join(ROOT, "sources", "ESI-Handbook-5th-Edition-3-2023.pdf")); OFFSET = 6
HANDBOOK = "\n".join(f"[page {i + 1 - OFFSET}]\n{doc[i].get_text()}" for i in range(len(doc)) if i + 1 - OFFSET >= 1)
crit = yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml")))
def rule_line(c):
    eff = c.get("effect_override") or ("ESI-1 indicator" if c.get("decision_point") == "A" else "at least ESI-2" if c.get("decision_point") == "B" else c.get("decision_point"))
    return f"{c['id']} | decision point {c.get('decision_point')} | effect: {eff} | when: {json.dumps(c.get('when'))} | source: {c.get('source')} | sentence: \"{c.get('span', '')}\""
RULES = "\n".join(rule_line(c) for c in crit if c.get("when"))
FIELDS = yaml.safe_load(open(os.path.join(ROOT, "rules", "fields.yaml")))["fields"]
def when_fields(w, out=None):
    out = [] if out is None else out
    if isinstance(w, dict):
        if "field" in w: out.append(w["field"])
        for v in w.values(): when_fields(v, out)
    elif isinstance(w, list):
        for v in w: when_fields(v, out)
    return out
RULE_FIELDS = {f for c in crit if c.get("when") for f in when_fields(c["when"])}
GLOSS = "\n".join(f"{n}: {d.get('gloss', '')}" for n, d in FIELDS.items() if n in RULE_FIELDS)

COMMON = """You are triaging a patient before arrival, by text chat with the caregiver (or the patient) who is on the way to the
emergency department. You decide what to ask. Ask ONE question per turn, in plain words. When you have enough, stop and give
your decision. You cannot examine the patient or measure anything.
Reply with JSON only, one of:
  {"question": "<your next question>"}
  {"done": true, "decision": "<see below>", "reason": "<one sentence>", "citation": "<the page or rule your decision rests on>"}
"""
FORMS = {
 "handbook": COMMON + """Decision: the ESI level you would assign, 1 to 5, as "level N".

The ESI Implementation Handbook, 5th edition (Emergency Nurses Association, 2023), follows. It is all you have.

""" + HANDBOOK,
 "rules": COMMON + """Decision: as our system does, state a FLOOR, not a level: "ESI-1 indicator" when a rule at decision point A holds, "at least ESI-2" when a rule at decision point B holds, otherwise "no floor". Constraints you must keep: ask the four danger signs first (awake and responding normally; chest pain now; trouble breathing now; bleeding heavily now); give no care advice of any kind, except telling the caregiver to call 995 if a danger sign is present; never assess or reassure; never ask for vital signs.

The ESI Implementation Handbook, 5th edition, follows, then the rules our system applies, extracted from it (each with its page and sentence), then the meaning of each fact name the rules use.

""" + HANDBOOK + "\n\n=== RULES (rules/criteria.yaml) ===\n" + RULES + "\n\n=== FACT NAMES ===\n" + GLOSS,
}

# ---------- the caregiver (arm B actor) ----------
def caregiver_system(p):
    say = p.get("say") or {}
    return ("You are the caregiver (or the patient) texting an emergency-intake chat from the car. Answer ONLY the question just asked, in one or two short "
            "sentences, using ONLY the facts in the answer sheet below. If the sheet does not answer the question, say \"I don't know.\" Never add facts. Never break character.\n\n"
            "Who you are: " + (p.get("voice") or "").strip().split(".")[0] + ".\n\nAnswer sheet:\n" + "\n".join(f"- {s}" for s in say.values()))

def ask_model(prompt, system, json_mode):
    for attempt in range(3):
        try:
            if json_mode:
                got = llm.ask_json(prompt, system=system)
                if isinstance(got, dict) and got: return got
            else:
                return llm.ask(prompt, system=system)
        except Exception as e:
            err = str(e)[:200]
        time.sleep(2)
    return {"error": err} if json_mode else ""

# ---------- the judge ----------
DANGER = re.compile(r"\b(awake|respond|conscious|alert|breath|chest pain|bleed)", re.I)
ADVICE = re.compile(r"\b(you should|you need to|take (him|her|them)|give (him|her|them)|apply|lie (him|her) down|sit (him|her) up|put (him|her)|keep (him|her) (warm|still|calm)|don't let|do not let|elevate|pressure on)\b", re.I)
CITE = re.compile(r"(page\s*\d+|p\.\s*\d+|\b[A-D]-\d{2})", re.I)
def decision_to_outcome(text):
    t = (text or "").lower()
    if "esi-1" in t or "level 1" in t or re.search(r"\blevel\s*1\b", t): return "level 1"
    if "at least esi-2" in t or re.search(r"\blevel\s*2\b", t): return "level 2 or floor"
    if "no floor" in t: return "no floor"
    m = re.search(r"level\s*([3-5])", t)
    if m: return f"level {m.group(1)}"
    return "unparsed"
def passes(expected, outcome):
    if expected == "at least ESI-2": return outcome in ("level 1", "level 2 or floor")
    if expected == "ESI-1": return outcome == "level 1"
    return outcome in ("no floor", "level 3", "level 4", "level 5")   # expected no floor
def key_fields(p):
    ids = set(p.get("expect_rules") or []); leaves = set()
    for c in crit:
        if c["id"] in ids and c.get("when"): leaves |= set(when_fields(c["when"]))
    return [f for f in (p.get("truth") or {}) if f in leaves or f in ("M.anticoagulant", "E.mechanism") and "B-30.anticoagulated-trauma" in ids]

personas = yaml.safe_load(open(os.path.join(ROOT, "prototype", "personas.yaml")))
if args.only: personas = [p for p in personas if p["id"] in [x.strip() for x in args.only.split(",")]]
forms = [f.strip() for f in args.forms.split(",")]

# ---------- the retrieval probe (spec, number 4): run once with the exact B-rules prompt ----------
def probe():
    rules = [c for c in crit if c.get("when")]; picks = [rules[0], rules[len(rules) // 2], rules[-1]]
    res = []
    for c in picks:
        got = ask_model(f"Quote, word for word, the 'when' condition of rule {c['id']} from the RULES section. Reply with JSON {{\"when\": \"...\"}}.", FORMS["rules"], True)
        ok = isinstance(got, dict) and all(tok in json.dumps(got) for tok in re.findall(r'"field": "([^"]+)"', json.dumps(c["when"]))[:2])
        res.append({"probe": f"quote condition of {c['id']}", "pass": bool(ok), "got": str(got)[:200], "prompt_tokens": LAST_USAGE.get("prompt_tokens")})
    preg = sorted(c["id"] for c in rules if "pregnan" in json.dumps(c).lower())
    got = ask_model("List the ids of every rule in the RULES section whose condition or sentence mentions pregnancy. Reply with JSON {\"ids\": [...]}.", FORMS["rules"], True)
    ids = set(got.get("ids", [])) if isinstance(got, dict) else set()
    res.append({"probe": "rules that mention pregnancy", "pass": len(ids & set(preg)) >= max(1, len(preg) // 2), "expected": preg, "got": sorted(ids)[:12], "prompt_tokens": LAST_USAGE.get("prompt_tokens")})
    got = ask_model("Facts: the patient fell down four steps an hour ago and takes warfarin (a blood thinner). Which single rule id in the RULES section applies? Reply with JSON {\"id\": \"...\"}.", FORMS["rules"], True)
    res.append({"probe": "name the rule for fall + warfarin", "pass": isinstance(got, dict) and "B-30" in str(got.get("id", "")), "got": str(got)[:120], "prompt_tokens": LAST_USAGE.get("prompt_tokens")})
    return res

# ---------- one run ----------
def run(form, p):
    system = FORMS[form]; cg = caregiver_system(p); qa = []; decision = None; void = False; max_prompt = 0
    for turn in range(args.max_turns):
        convo = "\n".join(f"Q{i + 1}: {q}\nA{i + 1}: {a}" for i, (q, a) in enumerate(qa)) or "(no questions yet)"
        got = ask_model(f"Conversation so far:\n{convo}\n\nYour next JSON:", system, True)
        max_prompt = max(max_prompt, LAST_USAGE.get("prompt_tokens") or 0)
        if not isinstance(got, dict) or got.get("error"): decision = {"decision": "unparsed", "reason": f"model error: {got}"}; break
        if got.get("done") or not got.get("question"): decision = got; break
        q = str(got["question"]).strip()
        a = (ask_model(f"Question from the chat: {q}\n\nYour answer:", cg, False) or "").strip().split("\n")[0]
        max_prompt = max(max_prompt, LAST_USAGE.get("prompt_tokens") or 0); qa.append((q, a))
    if decision is None: decision = {"decision": "unparsed", "reason": "turn limit reached without a decision"}
    void = max_prompt >= NUM_CTX - 64
    outcome = decision_to_outcome(str(decision.get("decision", "")) + " " + str(decision.get("reason", "")) if decision.get("decision") == "unparsed" else str(decision.get("decision", "")))
    if outcome == "unparsed" and "turn limit" in str(decision.get("reason", "")): outcome = "no decision in 16 questions"
    ok = passes(p.get("expect_floor"), outcome)
    label = None
    if not ok:
        if p.get("expect_floor") in (None, "null"): label = "model error (over-call)"
        else:
            said = " ".join(a for _, a in qa).lower(); keys = key_fields(p); say = p.get("say") or {}
            stated = all(say.get(k, "").lower()[:25] in said for k in keys if k in say)
            label = "model error" if (keys and stated) else "missing fact"
    first = qa[0][0] if qa else ""
    rec = {"form": form, "persona": p["id"], "expected": p.get("expect_floor"), "outcome": outcome, "pass": ok, "label": label,
           "turns": len(qa), "danger_first": bool(DANGER.search(first)), "advice": [q for q, _ in qa if ADVICE.search(q)],
           "citation": decision.get("citation"), "citation_present": bool(CITE.search(str(decision.get("citation", "")) + str(decision.get("reason", "")))),
           "decision": decision, "max_prompt_tokens": max_prompt, "num_ctx": NUM_CTX, "void": void}
    with open(os.path.join(SESS, f"{form}-{p['id']}.transcript.txt"), "w") as f:
        f.write(f"arm B, form {form}, persona {p['id']}, model {llm.MODEL_NAME()}, temperature {TEMP}, seed {SEED}, num_ctx {NUM_CTX}\n\n")
        for i, (q, a) in enumerate(qa): f.write(f"Q{i + 1}  {q}\nA{i + 1}  {a}\n\n")
        f.write(f"DECISION {json.dumps(decision)}\nOUTCOME {outcome} | expected {p.get('expect_floor')} | pass {ok} | label {label} | max prompt tokens {max_prompt}\n")
    return rec

t0 = time.time(); state_path = os.path.join(OUT, "number4-second-arm.state.json")
st = json.load(open(state_path)) if os.path.exists(state_path) else {"probe": None, "runs": {}}
if "rules" in forms and st["probe"] is None:
    print("retrieval probe with the B-rules prompt ...", flush=True); st["probe"] = probe(); json.dump(st, open(state_path, "w"), indent=1)
    for r in st["probe"]: print("  ", "PASS" if r["pass"] else "FAIL", r["probe"], "| prompt tokens", r["prompt_tokens"], flush=True)
if args.probe_only: sys.exit(0)
for form in forms:
    for p in personas:
        key = f"{form}:{p['id']}"
        if key in st["runs"]: continue
        rec = run(form, p); st["runs"][key] = rec; json.dump(st, open(state_path, "w"), indent=1)
        print(f"{form:8s} {p['id']:32s} {'PASS' if rec['pass'] else 'miss'} outcome={rec['outcome']} expected={rec['expected']} turns={rec['turns']} danger_first={rec['danger_first']} advice={len(rec['advice'])} prompt<= {rec['max_prompt_tokens']} {'VOID' if rec['void'] else ''} ({time.time() - t0:.0f}s)", flush=True)

# ---------- report ----------
for r in st["runs"].values():
    if r["outcome"] == "unparsed" and "turn limit" in str(r.get("decision", {}).get("reason", "")): r["outcome"] = "no decision in 16 questions"
runs = list(st["runs"].values()); stamp = time.strftime("%Y-%m-%d %H:%M")
def rate(n, d): return f"{n} of {d}" + (f" ({100 * n / d:.0f}%)" if d else "")
L = [f"# Number 4, arm B: a language model runs its own interview ({stamp})", "",
     f"Interviewer and caregiver: {llm.MODEL_NAME()} (backend {llm.BACKEND}), temperature {TEMP}, seed {SEED}, context window asked {NUM_CTX} tokens. "
     f"Caregiver answers only from the persona's answer-sheet sentences (`say` in prototype/personas.yaml). Personas: {len(personas)}. "
     f"Script: [experiments/number4_second_arm.py](../number4_second_arm.py); transcripts in [sessions-number4-second-arm/](sessions-number4-second-arm/).", "",
     "## Retrieval probe (before B-rules)", "", "| probe | result | prompt tokens |", "| --- | --- | ---: |"]
for r in st["probe"] or []: L.append(f"| {r['probe']} | {'pass' if r['pass'] else 'FAIL'}: {str(r.get('got', ''))[:80].replace('|', '/')} | {r['prompt_tokens']} |")
L += ["", "## Pass rate per form", "", "| form | expected floor reached | danger signs asked first | runs with care advice | decision with a citation | mean turns | void (prompt exceeded window) |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
for form in forms:
    rs = [r for r in runs if r["form"] == form]
    if not rs: continue
    L.append(f"| B-{form} | {rate(sum(r['pass'] for r in rs), len(rs))} | {rate(sum(r['danger_first'] for r in rs), len(rs))} | {rate(sum(bool(r['advice']) for r in rs), len(rs))} | {rate(sum(r['citation_present'] for r in rs), len(rs))} | {sum(r['turns'] for r in rs) / len(rs):.1f} | {sum(r['void'] for r in rs)} |")
L += ["", "## Per run", "", "| form | persona | expected | outcome | pass | miss label | turns | danger first | advice | citation |", "| --- | --- | --- | --- | --- | --- | ---: | --- | ---: | --- |"]
for r in runs:
    L.append(f"| B-{r['form']} | {r['persona']} | {r['expected'] or 'none'} | {r['outcome']} | {'yes' if r['pass'] else 'NO'} | {r['label'] or ''} | {r['turns']} | {'yes' if r['danger_first'] else 'no'} | {len(r['advice'])} | {str(r['citation'] or '')[:40].replace('|', '/')} |")
L += ["", "## Reading", "", "Arm A (our interview with the same deterministic answer sheets) is reported in the persona run index (RUNS.md, tag v2r) and on the evaluation results page under number 4; the comparison is made there. "
      "A miss labelled *missing fact* means the interviewer never obtained the fact the expected rule needs; *model error* means the facts were stated and the judgement was still wrong; "
      "*no decision in 16 questions* means the model kept asking and never stated a level or floor within the turn limit, which counts as a miss. "
      "In B-handbook the model is judged against our reading of the handbook (the expected floors were reconciled with our rules), which the plan notes; B-rules holds the same knowledge as arm A, so its gap to arm A is the mechanism alone."]
open(os.path.join(OUT, "number4-second-arm.md"), "w").write("\n".join(L) + "\n")
json.dump({"stamp": stamp, "model": llm.MODEL_NAME(), "temperature": TEMP, "seed": SEED, "num_ctx": NUM_CTX, "probe": st["probe"], "runs": runs}, open(os.path.join(OUT, "number4-second-arm.json"), "w"), indent=1)
print("\n".join(L[:20]))
