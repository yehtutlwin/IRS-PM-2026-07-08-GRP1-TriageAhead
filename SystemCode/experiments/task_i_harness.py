"""Task I harness: a persona-playing model drives the REAL interview through the web
API, then every session is scored against the persona's answer sheet.

The personas (prototype/personas.yaml) must be authored by a teammate who did not
build the interview - the independence rule; this harness only plays and scores.
    python3 experiments/task_i_harness.py [--runs 3] [--only P1-fall-anticoag] [--host http://localhost:8090]
    PERSONA_BACKEND=sheet ...   deterministic persona player: the sheet's `say` sentences, no model (number 2's consistency measure)
Outputs experiments/out/task-i-<timestamp>.md/.json (per persona x run: floor, rules,
extraction hits/misses, turns) - the language-layer results table.
"""
import argparse, json, os, sys, time, urllib.request
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
os.environ.setdefault("LLM_BACKEND", "ollama")
os.environ.setdefault("SESSIONS_DIR", "prototype/out/sessions-local")
import llm, engine, cli  # noqa: E402
# the persona player may run on a different backend and model from the interview (PERSONA_BACKEND, PERSONA_MODEL; #82):
# e.g. the interview on Claude Opus 5.5 (the server's LLM_BACKEND=claude) and the persona on Sonnet 5.5 or the local model
import importlib
_pb = os.environ.get("PERSONA_BACKEND", llm.BACKEND).strip().lower()
class _SheetPlayer:
    """PERSONA_BACKEND=sheet: the deterministic persona player of the evaluation plan (number 2). No model: each question is
    answered with the persona's `say` sentences for the fields the server reports as asked, or "I don't know." The same reply
    every time, so repeat runs measure fact extraction alone (16 Oct 2026)."""
    USAGE = {}
    @staticmethod
    def MODEL_NAME(): return "answer-sheet replay (no model)"
    @staticmethod
    def reply(p, asked):
        say = p.get("say") or {}; parts = []
        for f in asked or []:
            f = f[len("confirm."):] if f.startswith("confirm.") else f      # a confirmation question names its field as confirm.<field>
            if f in say and say[f] not in parts: parts.append(say[f])
        return " ".join(parts) if parts else "I don't know."
SHEET = _pb == "sheet"
persona_llm = _SheetPlayer if SHEET else (importlib.import_module("llm_" + _pb) if _pb != llm.BACKEND else llm)
if os.environ.get("PERSONA_MODEL"):
    os.environ[{"claude": "CLAUDE_MODEL", "ollama": "OLLAMA_MODEL"}.get(_pb, "PERSONA_MODEL")] = os.environ["PERSONA_MODEL"]

ap = argparse.ArgumentParser(); ap.add_argument("--runs", type=int, default=1); ap.add_argument("--only", default=None)
ap.add_argument("--host", default="http://localhost:8090"); ap.add_argument("--max-turns", type=int, default=16)
ap.add_argument("--tag", default="", help="label for the output file, e.g. dynamic-gemini")
args = ap.parse_args()

def post(path, body):
    r = urllib.request.Request(args.host + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(r, timeout=1800).read())   # a free-tier turn can wait on several back-offs
    except urllib.error.HTTPError as e:                  # the server answers 500 with {"error": ...}: show it, then stop
        raise RuntimeError(f"{path}: HTTP {e.code}: {e.read().decode(errors='replace')[:400]}") from None

PERSONA_SYSTEM = ("You are role-playing the person described below, texting an emergency-intake chatbot from a car "
                  "or ambulance. Answer ONLY the question just asked, in that person's voice, one or two short "
                  "sentences, using only facts from the description; if the description gives no answer, say you "
                  "don't know. Never add facts that are not in the description. Never break character.\n\n")

def get(path):
    return json.loads(urllib.request.urlopen(args.host + path, timeout=60).read())

def play(p):
    j = post("/api/start", {"coming_in": True}); sid, q = j["sid"], j["question"]
    asked = get(f"/api/state/{sid}").get("asked") or [] if SHEET else []
    turns = 0
    while q and turns < args.max_turns:
        if SHEET: a = _SheetPlayer.reply(p, asked)
        else: a = persona_llm.ask(f"Question from the chatbot: {q}\n\nYour answer:", system=PERSONA_SYSTEM + p["voice"]).strip().split("\n")[0]
        j = post(f"/api/answer/{sid}", {"text": a}); turns += 1; asked = j.get("asked") or []
        if j.get("complete"): break                      # interview design v2: `done` only means the report is ready (QR shown); the chat goes on
        q = next((r for r in j.get("replies", []) if r.endswith("?")), (j.get("replies") or [None])[-1])
    return sid, turns

import re as _re
SORRY = _re.compile(r"\b(sorry|apologi[sz]e)\b", _re.I)
YOU_EVENT = _re.compile(r"\b(you|your)\s+(fell|fall|hit your head|hurt yourself|were hit|collapsed|fainted|took|swallowed)\b", _re.I)


def wording_audit(sid, st):
    """What a human reader notices and the scores do not (added after Ye Htut Lwin's test session of 15 Oct 2026): apologies per
    session, the caregiver addressed as if they were the patient, questions after the report that are not for the nurse, and
    whether the nurse report renders at all."""
    qs = [m for m in st.get("messages", []) if m.get("role") == "bot" and m.get("kind") == "question"]
    sorry = sum(1 for m in qs if SORRY.search(m.get("text", "")))
    you_event = sum(1 for m in qs if YOU_EVENT.search(m.get("text", "")))
    ann = next((i for i, m in enumerate(st.get("messages", [])) if m.get("role") == "bot" and str(m.get("text", "")).startswith("That's enough for the hospital team")), None)
    keep = engine.after_report_fields(); after_bad = 0
    if ann is not None:
        for m in st["messages"][ann:]:
            if m.get("role") == "bot" and m.get("kind") == "question":
                fs = engine.fields_of_question_id(m.get("slot"))
                if fs and not any(f in keep for f in fs): after_bad += 1
    try:
        urllib.request.urlopen(args.host + f"/report-txt/{sid}", timeout=120).read(); report_ok = True
    except Exception as e:
        report_ok = False; print(f"  REPORT FAILED for {sid}: {str(e)[:120]}")
    return {"sorry": sorry, "you_event": you_event, "after_report_not_for_nurse": after_bad, "report_ok": report_ok}


def score(sid, p):
    st, facts = cli.load(sid)
    hits, misses = [], []
    for field, want in p["truth"].items():
        got = facts.resolve(field)
        if field == "M.anticoagulant" and want == "absent": ok = got in (None, False)
        elif isinstance(want, list): ok = bool(got)
        elif isinstance(want, (bool, int)): ok = got == want
        else: ok = got is not None
        (hits if ok else misses).append(f"{field}: want={want!r} got={got!r}")
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    qs = [m for m in st.get("messages", []) if m.get("role") == "bot" and m.get("kind") == "question"]
    seen, reasks = set(), 0
    for m in qs:                       # a re-ask: every field of this question was already asked before
        sl = m.get("slot") or ""; fs = tuple(sl[4:].split("+")) if sl.startswith("dyn:") else (sl,)
        if fs and all(f in seen for f in fs): reasks += 1
        seen.update(fs)
    msgs = st.get("messages", []); ann = next((i for i, m in enumerate(msgs) if m.get("role") == "bot" and str(m.get("text", "")).startswith("That's enough for the hospital team")), None)
    to_report = sum(1 for m in msgs[:ann] if m.get("role") == "bot" and m.get("kind") == "question") if ann is not None else None   # questions before the report was ready
    return wording_audit(sid, st) | {"questions": len(qs), "questions_to_report": to_report, "reasks": reasks, "floor": tree["floor"], "floor_ok": tree["floor"] == p["expect_floor"],
            "rules_ok": all(any(r["id"] == e for r in tree["fired"]) for e in p["expect_rules"]),
            "fired": [r["id"] for r in tree["fired"]], "hits": len(hits), "total": len(hits) + len(misses), "misses": misses,
            "danger_miss": any(m.split(":")[0] in p.get("must_catch", []) for m in misses)}

personas = yaml.safe_load(open(os.path.join(ROOT, "prototype", "personas.yaml")))
if args.only: personas = [p for p in personas if p["id"] in [x.strip() for x in args.only.split(",")]]   # one id, or several comma-separated
def server_usage():
    try: return json.loads(urllib.request.urlopen(args.host + "/api/info", timeout=10).read()).get("usage")
    except Exception: return None

t0 = time.time(); results = []
for p in personas:
    for run in range(args.runs):
        u0, pu0 = server_usage(), dict(getattr(persona_llm, "USAGE", {}) or {})
        sid, turns = play(p); s = score(sid, p); s.update({"persona": p["id"], "run": run + 1, "session": sid, "turns": turns})
        u1, pu1 = server_usage(), dict(getattr(persona_llm, "USAGE", {}) or {})
        if u0 and u1: s["interview_tokens"] = {k: u1[k] - u0[k] for k in u1}
        if pu0 and pu1: s["persona_tokens"] = {k: pu1[k] - pu0[k] for k in pu1}
        results.append(s); print(f"{p['id']} run {run+1}: floor_ok={s['floor_ok']} rules_ok={s['rules_ok']} extraction {s['hits']}/{s['total']} turns={turns} ({time.time()-t0:.0f}s)")

stamp = time.strftime("%Y%m%d-%H%M"); run_name = f"task-i-{stamp}" + (f"-{args.tag}" if args.tag else "")
out = os.path.join(ROOT, "experiments", "out", run_name)
# every persona session of this run is copied into the repository (the sessions folder itself is ignored by git because it
# also holds the live demo's sessions): facts, event log and transcript, under experiments/out/sessions-<run>/
import shutil
sess_dir = os.path.join(ROOT, "experiments", "out", "sessions-" + run_name); os.makedirs(sess_dir, exist_ok=True)
for r in results:
    for ext in (".json", ".log.jsonl", ".transcript.txt"):
        src = os.path.join(cli.SESS, r["session"] + ext)
        if os.path.exists(src): shutil.copy(src, sess_dir)
    r["transcript"] = f"sessions-{run_name}/{r['session']}.transcript.txt"
server_info = {}
try: server_info = json.loads(urllib.request.urlopen(args.host + "/api/info", timeout=10).read())
except Exception: pass
def _cost(tok, model):
    try:
        import llm_claude; return llm_claude.cost(tok, model)
    except Exception: return 0.0
interview_cost = sum(_cost(r["interview_tokens"], server_info.get("model")) for r in results if r.get("interview_tokens"))
persona_cost = sum(_cost(r["persona_tokens"], persona_llm.MODEL_NAME()) for r in results if r.get("persona_tokens"))
json.dump({"persona_backend": _pb, "persona_model": persona_llm.MODEL_NAME(), "interview": server_info, "tag": args.tag,
           "cost_usd": {"interview": round(interview_cost, 4), "persona": round(persona_cost, 4)}, "results": results}, open(out + ".json", "w"), indent=1)
n = len(results); H = sum(r["hits"] for r in results); T = sum(r["total"] for r in results)
L = [f"# Task I - persona runs through the real interview ({stamp})", "",
     f"Interview: mode {server_info.get('interview_mode', '?')}, backend {server_info.get('backend', '?')} ({server_info.get('model', '?')}). Persona played by {_pb} ({persona_llm.MODEL_NAME()}). Temperature: interview {server_info.get('temperature', '?')}, persona {os.environ.get('LLM_TEMPERATURE', 'backend default')} (the Claude API takes no temperature; its own default applies). {len(personas)} personas x {args.runs} run(s). Tag: {args.tag or '-'}"
     + (f" Tokens: interview {sum(r['interview_tokens']['input'] + r['interview_tokens']['cache_read'] for r in results if r.get('interview_tokens')):,} in / {sum(r['interview_tokens']['output'] for r in results if r.get('interview_tokens')):,} out, about ${interview_cost:.2f}; persona about ${persona_cost:.2f} (prices of 14 Oct 2026)." if interview_cost or persona_cost else ""), "",
     f"Floors {sum(r['floor_ok'] for r in results)}/{n} · expected rules {sum(r['rules_ok'] for r in results)}/{n} · extraction {H}/{T} ({H/max(T,1):.0%}) · danger-sign misses {sum(r['danger_miss'] for r in results)} · questions {sum(r['questions'] for r in results)} · re-asks {sum(r['reasks'] for r in results)}", "",
     f"Wording audit: apologies {sum(r.get('sorry', 0) for r in results)} · caregiver addressed as the patient {sum(r.get('you_event', 0) for r in results)} · questions after the report not for the nurse {sum(r.get('after_report_not_for_nurse', 0) for r in results)} · reports that failed to render {sum(1 for r in results if not r.get('report_ok', True))}", "",
     "| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |", "| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
for r in results:
    L.append(f"| {r['persona']} ([{r['session']}]({r['transcript']})) | {r['run']} | {r['floor'] or '-'} | {'yes' if r['floor_ok'] else 'NO'} | {'yes' if r['rules_ok'] else 'NO'} | {r['hits']}/{r['total']} | {r['turns']} | {r['questions']} | {r.get('questions_to_report') if r.get('questions_to_report') is not None else '-'} | {r['reasks']} | {r.get('sorry', 0)} | {'; '.join(r['misses'])[:160]} |")
if args.runs > 1:
    L += ["", "Rerun consistency (same persona, identical floor across runs):", ""]
    for pid in {r["persona"] for r in results}:
        fl = [r["floor"] for r in results if r["persona"] == pid]; L.append(f"- {pid}: {'consistent' if len(set(fl)) == 1 else 'VARIES ' + str(fl)}")
open(out + ".md", "w").write("\n".join(L) + "\n"); print(f"wrote {out}.md")

# the index of every persona run, regenerated from the run files on disk (experiments/out/task-i-*.json); never edited
import glob
rows = []
for jf in sorted(glob.glob(os.path.join(ROOT, "experiments", "out", "task-i-*.json"))):
    try: d = json.load(open(jf))
    except Exception: continue
    rs = d.get("results") or []
    if not rs: continue
    name = os.path.basename(jf)[:-5]; info = d.get("interview") or {}
    Hh, Tt = sum(x.get("hits", 0) for x in rs), sum(x.get("total", 0) for x in rs)
    tr = [x.get("questions_to_report") for x in rs if x.get("questions_to_report") is not None]
    to_report = f"{sum(tr) / len(tr):.1f}" if tr else "-"
    rows.append(f"| {name[7:20]} | {d.get('tag') or '-'} | {info.get('interview_mode', '?')} | {info.get('backend', '?')} {info.get('model', '')} | "
                f"{d.get('persona_backend', '?')} {d.get('persona_model', '')} | {len(rs)} | {sum(bool(x.get('floor_ok')) for x in rs)}/{len(rs)} | "
                f"{sum(bool(x.get('rules_ok')) for x in rs)}/{len(rs)} | {Hh}/{Tt} | {sum(x.get('questions', 0) for x in rs) / len(rs):.1f} | {to_report} | "
                f"{sum(x.get('reasks', 0) for x in rs)} | [report]({name}.md) |")
idx = ["# Persona runs: the index", "",
       "Every run of the persona harness (`experiments/task_i_harness.py`), one row each, regenerated by the harness from the run files",
       "`task-i-*.json` in this folder. Never edited by hand. A run = every persona in `prototype/personas.yaml` (or one, with `--only`) played",
       "through the real web interview; the report links each persona's session transcript (copied into `sessions-<run>/` since 15 Oct 2026;",
       "earlier runs' transcripts are in the `sessions-*` folders named after the configuration, or were not kept).",
       "Columns: floors and rules = evaluation number 4 (the expected floor reached, the expected rule fired); extraction = number 2",
       "(facts on the persona's sheet found in the fact store); questions = per persona; to report = questions before the report was ready",
       "(interview design v2, 14 Oct 2026); re-asks = questions all of whose fields had been asked before.", "",
       "| run | tag | mode | interview model | persona model | personas | floors | rules | extraction | questions | to report | re-asks | report |",
       "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"] + rows
open(os.path.join(ROOT, "experiments", "out", "RUNS.md"), "w").write("\n".join(idx) + "\n"); print("index: experiments/out/RUNS.md")
