"""Session-based interview CLI. Gemini plays the SYSTEM (phrase + extract);
the persona seat is a human at a terminal - or any agent driving these commands.

  python cli.py start  <session>              new session, prints question 1
  python cli.py answer <session> "free text"  process an answer, print events + next question
  python cli.py chat   <session>              interactive loop (humans) - same code path
  python cli.py report <session>             render the nurse report (1 Gemini call for summary)
  python cli.py score  <session> <persona>   compare facts vs personas.yaml answer sheet
  python cli.py log    <session>             dump the unified event log

State + logs: out/sessions/<session>.json (state) and <session>.log.jsonl (events).
Every event is also mirrored to <session>.transcript.txt for human reading.
Set SESSIONS_DIR (.env or shell) to write sessions somewhere else - e.g. the
gitignored prototype/out/sessions-local/ for tests you don't want to commit."""
import sys, os, json, time, yaml
import engine, llm, extraction

HERE = os.path.dirname(os.path.abspath(__file__))
# SESSIONS_DIR (.env or shell) redirects all session artifacts - absolute path,
# or relative to the repo root. Default stays in the committed out/sessions/;
# prototype/out/sessions-local/ is gitignored for throwaway test runs.
_sess_dir = os.environ.get("SESSIONS_DIR", "")
SESS = (os.path.join(HERE, "..", _sess_dir) if _sess_dir and not os.path.isabs(_sess_dir)
        else _sess_dir) or os.path.join(HERE, "out", "sessions")
SESS = os.path.abspath(SESS)
os.makedirs(SESS, exist_ok=True)



# ---------------- chat history: structured messages ----------------
# st["messages"]: list of {"role": bot|caregiver|system, "text", "ts": "YYYY-MM-DD HH:MM:SS",
#   "kind": question|answer|photo|advice|ack|checkin|note, "slot": <slot id> (questions/answers)}
# The transcript file is generated from this list; the LLM sees a rendered window of it.
ROLE_TAG = {"bot": "BOT", "caregiver": "THEM", "system": "SYS"}


def add_msg(st, role, text, kind=None, slot=None):
    m = {"role": role, "text": text, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    if kind: m["kind"] = kind
    if slot: m["slot"] = slot
    st.setdefault("messages", []).append(m)
    return m


def turn_count(st):
    """Turn = number of caregiver messages so far (answers and photos)."""
    return sum(1 for m in st.get("messages", []) if m["role"] == "caregiver")


def last_question(st):
    for m in reversed(st.get("messages", [])):
        if m["role"] == "bot" and m.get("kind") in ("question", "checkin"):
            return m["text"]
    return ""


def context_window(st, n=4):
    """Rendered recent conversation for the phrasing model (system notes excluded)."""
    conv = [m for m in st.get("messages", []) if m["role"] != "system"]
    return "\n".join(f"{ROLE_TAG[m['role']]}: {m['text']}" for m in conv[-n:])


def migrate_chat(st):
    """Legacy sessions stored st['chat'] as 'BOT: ..'/'THEM: ..' strings (+ optional
    parallel st['chat_ts']). Convert once; the old keys are dropped."""
    if "messages" in st or "chat" not in st:
        return st
    ts = st.get("chat_ts", [])
    st["messages"] = []
    for i, line in enumerate(st["chat"]):
        role = "bot" if line.startswith("BOT: ") else "caregiver" if line.startswith("THEM: ") else "system"
        text = line[5:] if role == "bot" else line[6:] if role == "caregiver" else line
        st["messages"].append({"role": role, "text": text,
                               "ts": (ts[i] if i < len(ts) and ts[i] else ""),
                               "kind": "question" if role == "bot" else "answer"})
    st.pop("chat", None); st.pop("chat_ts", None)
    return st


def write_transcript(name, st):
    """The human-readable transcript, regenerated from the messages on every save."""
    _, _, tp = _paths(name)
    lines = [f"session {name}   started {st.get('created', '?')}   (generated from messages)", ""]
    for m in st.get("messages", []):
        tag = ROLE_TAG.get(m["role"], "?")
        slot = f"   [slot {m['slot']}]" if m.get("slot") else ""
        kind = f" ({m['kind']})" if m.get("kind") not in (None, "question", "answer") else ""
        lines.append(f"{m.get('ts', '')[-8:]:>8}  {tag:<4} {m['text']}{slot}{kind}")
    with open(tp, "w") as f:
        f.write("\n".join(lines) + "\n")


# ---------------- state ----------------
def _paths(name):
    return (os.path.join(SESS, f"{name}.json"),
            os.path.join(SESS, f"{name}.log.jsonl"),
            os.path.join(SESS, f"{name}.transcript.txt"))

def load(name):
    sp, _, _ = _paths(name)
    with open(sp) as f:
        st = json.load(f)
    migrate_chat(st)
    facts = engine.Facts(); facts.d = st["facts"]
    return st, facts

def save(name, st, facts):
    sp, _, _ = _paths(name)
    st["facts"] = facts.d
    with open(sp, "w") as f:
        json.dump(st, f, indent=1)
    write_transcript(name, st)

def log_event(name, kind, **data):
    _, lp, tp = _paths(name)
    evt = {"t": time.strftime("%H:%M:%S"), "kind": kind, **data}
    with open(lp, "a") as f:
        f.write(json.dumps(evt) + "\n")


# ---------------- core steps (shared by every mode) ----------------
def _pick_and_ask(name, st, facts):
    """Static mode without a model choosing the grouping: the program takes the top open field of the derived
    agenda and the fields asked with it, and the model only words the question."""
    bundle = engine.static_bundle(engine.open_fields(facts, st["attempts"]))
    if not bundle:
        log_event(name, "engine", note="interview complete - no open fields")
        return None
    fields = [b["field"] for b in bundle]
    qid = ("confirm." if bundle[0]["confirm"] else "fld:") + "+".join(fields) if not bundle[0]["confirm"] else "confirm." + fields[0]
    for f in fields:
        st["attempts"][("confirm." if bundle[0]["confirm"] else "") + f] = st["attempts"].get(("confirm." if bundle[0]["confirm"] else "") + f, 0) + 1
    st["pending_slot"] = qid
    ctx = context_window(st)
    n = max(st["attempts"].get(f, 0) for f in fields)
    retry = (" The person did not answer this last time - ask again, in different, simpler words." if n > 1 else "")
    topic = " ".join(b["hint"] for b in bundle)
    q = llm.ask(f"Recent chat:\n{ctx}\n\nAsk this in one short, warm, plain-English sentence "
                f"(second person, no preamble):{retry}\nTopic: {topic}").strip()
    add_msg(st, "bot", q, kind="question", slot=qid)
    log_event(name, "question", slot=qid, text=q, fields=fields)
    return q

def _process_answer(name, st, facts, text):
    slot_id = st.get("pending_slot", "?")
    asked = last_question(st)
    add_msg(st, "caregiver", text, kind="answer", slot=slot_id)
    log_event(name, "answer", slot=slot_id, text=text)
    turn = turn_count(st)
    asked_fields = engine.fields_of_question_id(slot_id)
    open_now = [o["field"] for o in engine.open_fields(facts, st.get("attempts", {}))]
    out = llm.ask_json(f"Question asked (about {', '.join(asked_fields) or slot_id}): {asked}\n"
                       f"Answer given: {text}", system=extraction.system_prompt(asked_fields, open_now))
    writes = out.get("writes", []) if isinstance(out, dict) else []
    writes, dropped = extraction.guard(writes, text, asked_fields)   # stated-only fields; denials of unaddressed items; quotes
    if dropped:
        log_event(name, "extract", writes=[(w.get("field"), w.get("value"), w.get("why")) for w in dropped], via="guard-dropped")   # the reason per write (not stated / denial of an unaddressed item / quote not in the answer)
    current_cat = None   # last category seen in THIS turn; fallback detail target
    for w in writes:
        field = w.get("field")
        if not field:
            continue
        status = "probable" if w.get("status") == "probable" else "reported"   # a deduced value keeps its lower certainty
        if field == "complaint.category":
            facts.write_complaint(w.get("value"), status=status, who="caregiver", turn=turn)
            current_cat = w.get("value")
        elif field in engine.COMPLAINT_DETAILS:
            recs = facts.complaints()
            known = {r["category"] for r in recs} | set(engine.load_fields()["complaint.category"]["values"])
            about = w.get("about") if w.get("about") in known else None   # an invented category never opens a complaint
            target = about or current_cat or (recs[-1]["category"] if recs else None)
            if target:
                facts.write_complaint(target, field, w.get("value"),
                                      status=status, who="caregiver", turn=turn)
            else:   # detail before any complaint exists - legacy flat write
                facts.write(field, w.get("value"), status=status, who="caregiver", turn=turn)
        else:
            facts.write(field, w.get("value"), status=status, who="caregiver", turn=turn)
    log_event(name, "extract",
              writes=[(w.get("field"), w.get("value")) + ((w["about"],) if w.get("about") else ())
                      for w in writes])
    engine.derive(facts, turn)
    prev = st.get("floor")
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    if tree["floor"] != prev:
        st["floor"] = tree["floor"]
        log_event(name, "floor", floor=tree["floor"],
                  fired=[r["id"] for r in tree["fired"]],
                  sources=[r["source"] for r in tree["fired"]])
        add_msg(st, "system", f"floor: {tree['floor']}  rules: {[r['id'] for r in tree['fired']]}", kind="floor")
        print(f"  >>> FLOOR: {tree['floor']}  rules: {[r['id'] for r in tree['fired']]}")
    if tree["consider"]:
        newc = [r["id"] for r in tree["consider"] if r["id"] not in st.get("considered", [])]
        if newc:
            st.setdefault("considered", []).extend(newc)
            log_event(name, "engine", consider=newc)
            print(f"  >>> CONSIDER flags: {newc}")
    return tree


# ---------------- commands ----------------
def cmd_start(name):
    sp, lp, tp = _paths(name)
    for p in (sp, lp, tp):
        if os.path.exists(p): os.remove(p)
    st = {"facts": {}, "attempts": {}, "messages": [], "floor": None,
          "created": time.strftime("%Y-%m-%d %H:%M")}
    facts = engine.Facts()
    log_event(name, "engine", note=f"session {name} started")
    q = _pick_and_ask(name, st, facts)
    save(name, st, facts)
    print(f"[session {name}]")
    print(f"BOT: {q}")

def cmd_answer(name, text):
    st, facts = load(name)
    _process_answer(name, st, facts, text)
    q = _pick_and_ask(name, st, facts)
    save(name, st, facts)
    if q is None:
        print("BOT: Thank you - that's everything. Show the code at the counter when you arrive.")
        print(f"[interview complete - run: python cli.py report {name}]")
    else:
        print(f"BOT: {q}")

def cmd_chat(name):
    sp, _, _ = _paths(name)
    if not os.path.exists(sp):
        cmd_start(name)
    else:
        print(f"[resuming session {name}]")
    while True:
        try:
            text = input("YOU: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[paused - resume anytime with the same session name]")
            return
        if not text:
            continue
        st, facts = load(name)
        _process_answer(name, st, facts, text)
        q = _pick_and_ask(name, st, facts)
        save(name, st, facts)
        if q is None:
            print("BOT: Thank you - that's everything.")
            return
        print(f"BOT: {q}")

PHOTO_SYSTEM = """You read a photo supplied during an emergency-intake chat (typically a
medicine box or label). Return ONLY JSON:
{"writes":[{"field":"confirm.M.anticoagulant","value":"<drug name>"}]} if a medication
name is readable (use the generic or brand name exactly as printed, lowercase), plus
{"field":"M.medications","value":["<name printed>"]} for any medication identified.
If nothing medication-related is readable, return {"writes":[]}."""

def cmd_photo(name, image_path, note=""):
    st, facts = load(name)
    add_msg(st, "caregiver", f"[sent a photo{': ' + note if note else ''}]", kind="photo", slot=st.get("pending_slot"))
    log_event(name, "answer", slot=st.get("pending_slot"), text=f"[PHOTO {os.path.basename(image_path)}] {note}")
    out = llm.ask_image(image_path, "Read this photo per your instructions.", system=PHOTO_SYSTEM)
    writes = out.get("writes", []) if isinstance(out, dict) else []
    turn = turn_count(st)
    for w in writes:
        if w.get("field"):
            facts.write(w["field"], w.get("value"), status="reported", who="persona-photo", turn=turn)
    log_event(name, "extract", writes=[(w.get("field"), w.get("value")) for w in writes], via="photo")
    print(f"  ~ photo read: {[(w.get('field'), w.get('value')) for w in writes]}")
    engine.derive(facts, turn)
    prev = st.get("floor")
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    if tree["floor"] != prev:
        st["floor"] = tree["floor"]
        log_event(name, "floor", floor=tree["floor"], fired=[r["id"] for r in tree["fired"]])
        print(f"  >>> FLOOR: {tree['floor']}  rules: {[r['id'] for r in tree['fired']]}")
    q = _pick_and_ask(name, st, facts)
    save(name, st, facts)
    print(f"BOT: {q}" if q else "BOT: Thank you - that's everything.")

def cmd_report(name):
    import report
    st, facts = load(name)
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    rep = report.render(name, facts, tree)
    out = os.path.join(SESS, f"{name}.report.txt")
    open(out, "w").write(rep)
    log_event(name, "engine", note="report rendered")
    print(rep)
    print(f"\n[saved: {out}]")

def cmd_score(name, persona_id):
    st, facts = load(name)
    personas = yaml.safe_load(open(os.path.join(HERE, "personas.yaml")))
    p = next(x for x in personas if x["id"] == persona_id)
    hits, misses = [], []
    for field, want in p["truth"].items():
        got = facts.resolve(field)
        if field == "M.anticoagulant" and want == "absent":
            ok = got in (None, False)
        elif isinstance(want, list):
            ok = bool(got)
        elif isinstance(want, (bool, int)):
            ok = got == want
        else:
            ok = got is not None
        (hits if ok else misses).append(f"{field}: want={want!r} got={got!r}")
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    print(f"floor: {tree['floor']!r}  expected: {p['expect_floor']!r}  "
          f"match: {tree['floor'] == p['expect_floor']}")
    print(f"expected rules fired: "
          f"{all(any(r['id'] == e for r in tree['fired']) for e in p['expect_rules'])}")
    print(f"extraction: {len(hits)}/{len(hits) + len(misses)}")
    for m in misses:
        print(f"  MISS {m}")

def cmd_log(name):
    _, lp, _ = _paths(name)
    print(open(lp).read())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "start":    cmd_start(sys.argv[2])
    elif cmd == "answer": cmd_answer(sys.argv[2], sys.argv[3])
    elif cmd == "chat":   cmd_chat(sys.argv[2])
    elif cmd == "photo":  cmd_photo(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "report": cmd_report(sys.argv[2])
    elif cmd == "score":  cmd_score(sys.argv[2], sys.argv[3])
    elif cmd == "log":    cmd_log(sys.argv[2])
    else: print(__doc__)
