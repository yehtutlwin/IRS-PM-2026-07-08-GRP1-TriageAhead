"""One-process web app for the pre-arrival intake demo (one-shot experiment branch).

Serves, on one port (default 8090), optionally behind a tunnel (webapp/run.sh):
  /            caregiver entry: the post-decision gate, then the chat
  /chat/<sid>  the chat page (same session resumes anywhere)
  /r/<sid>     nurse/doctor report page (first open switches the session to the
               waiting-room phase)
  /qr/<sid>    QR code (SVG) encoding the report link
  /rules       the rulebook inspector (same page as prototype/inspector.py)
  /api/...     JSON endpoints the chat page uses

Reuses the prototype modules: cli (interview steps + session store), engine (rules and the
derived agenda of what to ask), extraction (the extraction prompt), report, llm (Ollama/Gemini seam).
Run: python3 webapp/server.py   (see webapp/run.sh for server + tunnel together)
"""
import base64, json, os, random, re, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "prototype"))
# keep one-shot sessions out of the committed sessions dir unless caller overrides
os.environ.setdefault("SESSIONS_DIR", "prototype/out/sessions-local")

import cli, engine, report, llm            # noqa: E402
import practice_signal                     # noqa: E402
import inspector as rules_inspector        # noqa: E402

PORT = int(os.environ.get("WEBAPP_PORT", "8090"))
PUBLIC_BASE = os.environ.get("PUBLIC_BASE", f"http://localhost:{PORT}").rstrip("/")
CHECKIN_SECONDS = int(os.environ.get("CHECKIN_SECONDS", "900"))  # walkthrough: ~15 min

WORDS = ("LION TIGER EAGLE ORCHID LOTUS RAFFLES MERLION PANDA HERON OTTER "
         "BAOBAB DURIAN KOPI SAGA CANNA VANDA").split()
_locks, _locks_guard = {}, threading.Lock()


def _ts_epoch(ts):
    try: return time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))
    except (TypeError, ValueError): return 0


def lock_for(sid):
    with _locks_guard:
        return _locks.setdefault(sid, threading.Lock())


def new_ticket():
    while True:
        t = f"{random.choice(WORDS)}-{random.randint(1000, 9999)}"
        if not os.path.exists(cli._paths(t)[0]):
            return t


def valid_sid(sid):
    return bool(re.fullmatch(r"[A-Z]+-\d{4}", sid)) and os.path.exists(cli._paths(sid)[0])


# ---------------- interview steps (thin wrappers over cli) ----------------

# ---------------- interview quality fixes (webapp layer; prototype untouched) ----------------
BLANKET_NO = re.compile(
    r"^\s*(?:no|nope|nah|none|nothing|nil|nothing else|no thanks|not really|not at all|"
    r"no lah|no leh|no la|none that i know(?: of)?|not that i know(?: of)?|no[,.]? (?:none|nothing|nope)|"
    r"tiada|tak ada|takde|tidak|tidak ada|bukan|没有|没|无|不是|不|இல்லை)"
    r"[\s!.]*$", re.I)   # fullmatch only: "no wait, actually..." / "no fever. he was hot" are NOT blanket
# fields a blanket "no" can safely negate, by prefix or exact name
_NO_FALSE_PREFIX = ("danger_signs.", "stroke.", "limb.", "infection.")
_NO_FALSE_FIELDS = {"history.immunocompromised", "history.pregnant", "history.postpartum", "complaint.fever",
                    "E.head_strike", "E.loc"}
_NO_EMPTY_LIST = {"A.allergies", "history.conditions", "M.medications"}


INTERVIEW_MODE = os.environ.get("INTERVIEW_MODE", "dynamic").strip().lower()   # dynamic since interview design v2 (#63, 14 Oct 2026); static kept for comparison runs   # static: program bundles (asked_with) · dynamic: model bundles program-ranked fields
DYN_MAX_FIELDS = int(os.environ.get("DYN_MAX_FIELDS", "4"))


def _slot_by_id(slot_id):
    """The question a pending id names. 'dyn:a+b' is a bundle the model chose, 'fld:a+b' one the program chose,
    'confirm.<field>' a confirmation; all are read as a composite over their fields."""
    fields = engine.fields_of_question_id(slot_id)
    if not fields:
        return None
    hints = engine.load_agenda()
    return {"id": slot_id, "type": "composite", "fields": fields,
            "ask": " ".join(hints.get(f, {}).get("ask", f) for f in fields), "priority": 0, "rank": 0}


def blanket_no_fill(sid, st, facts, text):
    """A bare 'no' answers every remaining part of the compound question just asked.
    Deterministic, logged, and limited to fields where a negative is meaningful."""
    if not BLANKET_NO.fullmatch((text or "").strip()):
        return False
    slot = _slot_by_id(st.get("pending_slot", ""))
    if not slot:
        return False
    fields = slot["fields"] if slot["type"] == "composite" else [slot["id"]]
    turn = cli.turn_count(st)
    writes = []
    for f in fields:
        if facts.has(f):
            continue
        if f in _NO_EMPTY_LIST:
            facts.write(f, [], status="reported", who="blanket-no", turn=turn); writes.append((f, []))
        elif f in _NO_FALSE_FIELDS or f.startswith(_NO_FALSE_PREFIX):
            facts.write(f, False, status="reported", who="blanket-no", turn=turn); writes.append((f, False))
    if writes:
        cli.log_event(sid, "extract", writes=writes, via="blanket-no")
        engine.derive(facts, turn)
    return bool(writes)


def derive_mechanism_none(sid, st, facts):
    """TODO item 2: for a non-injury complaint there is no mechanism, and the
    extractor never writes 'none' unprompted, so complaint.main could never
    resolve. Derive it deterministically once a non-injury category is known."""
    if facts.has("E.mechanism"):
        return False
    cats = facts.resolve("complaint.category") or []
    cats = cats if isinstance(cats, list) else [cats]
    if cats and not any(c in ("injury", "head_injury", "wound", "burn", "limb_pain_or_swelling", "other") for c in cats):
        turn = cli.turn_count(st)
        facts.write("E.mechanism", "none", status="reported", who="derived", turn=turn)
        cli.log_event(sid, "extract", writes=[("E.mechanism", "none")], via="derived-non-injury")
        return True
    return False


# the extractor's category enum (rules/fields.yaml, complaint.category); the local model invents others
CATEGORIES = set(engine.load_fields()["complaint.category"]["values"])
CATEGORY_SYNONYMS = {
    "breathing_difficulty": "breathing", "shortness_of_breath": "breathing", "breathless": "breathing", "asthma": "breathing",
    "stomach_ache": "abdominal_pain", "stomach_pain": "abdominal_pain", "belly_pain": "abdominal_pain",
    "fall": "injury", "fall_pain": "injury", "hip_injury": "injury", "injury_fall": "injury", "leg_injury": "limb_pain_or_swelling",
    "trauma": "injury", "head_bleeding": "head_injury", "laceration": "wound", "cut": "wound", "bite": "wound", "scald": "burn",
    "limb_pain": "limb_pain_or_swelling", "arm_pain": "limb_pain_or_swelling", "leg_pain": "limb_pain_or_swelling", "swelling": "limb_pain_or_swelling",
    "rash": "skin_problem", "skin_infection": "skin_problem", "abscess": "skin_problem", "earache": "ear_problem", "toothache": "dental",
    "vomiting": "vomiting_or_diarrhoea", "diarrhoea": "vomiting_or_diarrhoea", "diarrhea": "vomiting_or_diarrhoea", "gastro": "vomiting_or_diarrhoea",
    "uti": "urinary_problem", "urinary": "urinary_problem", "dysuria": "urinary_problem",
    "bleeding_pregnancy": "vaginal_bleeding", "pregnancy": "pregnancy_related", "labour": "pregnancy_related", "contractions": "pregnancy_related",
    "allergy": "allergic_reaction", "hives": "allergic_reaction",
    "anxiety": "mental_health", "self_harm": "mental_health", "overdose": "poisoning_or_overdose", "poisoning": "poisoning_or_overdose", "intoxication": "poisoning_or_overdose",
    "medication_refill": "request", "prescription": "request", "tetanus_request": "request", "administrative": "request", "emergency_contraception": "request",
    "fainting": "dizziness", "faint": "dizziness", "giddy": "dizziness", "lightheaded": "dizziness", "palpitations": "chest_pain",
    "stroke": "neuro_symptoms", "weakness": "neuro_symptoms", "seizure": "neuro_symptoms", "confusion": "neuro_symptoms",
    "current_complaint": "other", "general": "other", "pain": "other", "unknown": "other",
}


def normalise_categories(sid, st, facts):
    """Collapse invented categories onto the enum; unknown -> 'other'. The record's
    text is untouched, so nothing said is lost - only the label is disciplined."""
    recs = facts.complaints()
    if not recs:
        return
    changed = []
    merged = []
    for r in recs:
        cat = str(r["category"]).strip().lower().replace(" ", "_").replace("-", "_")
        norm = cat if cat in CATEGORIES else CATEGORY_SYNONYMS.get(cat, "other")
        if norm != r["category"]:
            changed.append((r["category"], norm))
        r["category"] = norm
        dup = next((m for m in merged if m["category"] == norm), None)
        if dup:   # same normalised category twice: keep the earlier record, fold details in
            for k, v in r.items():
                if k not in dup and k != "category":
                    dup[k] = v
        else:
            merged.append(r)
    facts.d["complaints"]["value"] = merged
    facts.d["complaint.category"]["value"] = [m["category"] for m in merged]
    if changed:
        cli.log_event(sid, "extract", writes=[("complaint.category", f"{a}->{b}") for a, b in changed],
                      via="normalised")


# safety-relevant facts: a later answer that would make one LESS urgent is not applied
# silently - the earlier value stands, the conflict is recorded for the nurse
SAFETY_BOOL = ("danger_signs.chest_pain_now", "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding",
               "E.head_strike", "E.loc", "history.pregnant", "history.postpartum", "history.immunocompromised",
               "stroke.face_droop", "stroke.arm_weakness", "stroke.speech_change")


def snapshot_safety(facts):
    snap = {f: dict(facts.d[f]) for f in SAFETY_BOOL if f in facts.d}
    for f in ("M.anticoagulant", "confirm.M.anticoagulant", "M.medications"):
        if f in facts.d:
            snap[f] = dict(facts.d[f])
    return snap


def contradiction_guard(sid, st, facts, before, text):
    found = []
    for f in SAFETY_BOOL:
        if f in before and before[f]["value"] is True and facts.resolve(f) is False:
            facts.d[f] = before[f]                      # keep the urgent value
            found.append(f"{f}: earlier YES, now says no")
    conf = facts.resolve("confirm.M.anticoagulant")
    if ("M.anticoagulant" in before and before["M.anticoagulant"].get("status") == "confirmed"
            and conf and conf != before.get("confirm.M.anticoagulant", {}).get("value")
            and not any(n in str(conf).lower() for n in engine.ANTICOAG_NAMES)):
        found.append(f"blood thinner: earlier '{before.get('confirm.M.anticoagulant', {}).get('value')}', "
                     f"now says '{conf}' - anticoagulant kept as CONFIRMED pending the box")
        facts.d["confirm.M.anticoagulant"] = before["confirm.M.anticoagulant"]
    if found:
        st.setdefault("contradictions", []).extend(
            {"ts": time.strftime("%H:%M"), "what": w, "said": text[:80]} for w in found)
        for w in found:
            cli.add_msg(st, "system", f"conflicting report kept the earlier value - {w}", kind="note")
        cli.log_event(sid, "contradiction", items=found, text=text[:80])
    return found


def restore_attempt_if_volunteered(st, facts, slot_id, writes_before, writes_after):
    """An answer that gave facts for OTHER slots is not a non-answer: don't burn
    the pending slot's attempt on it."""
    slot = _slot_by_id(slot_id)
    if not slot or writes_after <= writes_before:
        return
    fields = slot["fields"] if slot["type"] == "composite" else [slot["id"]]
    credit = st.setdefault("volunteer_credit", {})
    if (not any(facts.has(f) for f in fields) and st["attempts"].get(slot_id, 0) > 0
            and not credit.get(slot_id)):
        credit[slot_id] = True          # one free re-ask per slot, then the cap applies
        st["attempts"][slot_id] -= 1


PAIN_RE = re.compile(r"(?:pain|hurts?|sakit|疼|痛)[^\d]{0,25}(\d{1,2})\b|\b(\d{1,2})\s*(?:/|out of)\s*10", re.I)


def checkin_pain_fallback(sid, st, facts, text, n_before):
    """A check-in answer like 'pain is down to 5' must update the trend even when the
    extractor returns nothing (it has no slot context for check-ins)."""
    if st.get("pending_slot") != "checkin.status" or len(facts.d) != n_before:
        pass
    m = PAIN_RE.search(text or "")
    if not m:
        return False
    n = int(m.group(1) or m.group(2))
    if not 0 <= n <= 10:
        return False
    recs = facts.complaints()
    cat = recs[0]["category"] if recs else "other"
    if facts.resolve("complaint.pain_latest") == n:
        return False
    facts.write_complaint(cat, "complaint.pain_rating", n, status="reported", who="caregiver", turn=cli.turn_count(st))
    cli.log_event(sid, "extract", writes=[("complaint.pain_rating", n)], via="checkin-fallback")
    return True


DYN_SYSTEM = (
    "You run the question flow of an emergency pre-arrival intake chat for a hospital. You are given the facts already "
    "known, the recent chat, and a RANKED list of facts still needed (most important first), each with a hint of how the "
    "hospital would ask about it. Decide which of the top-ranked facts to ask about in ONE natural question, then write it.\n"
    "Rules: you MUST include the first fact in the list. You may add up to the allowed number of further facts from the list, "
    "only if a caregiver can naturally answer them together (same topic, same moment: the stroke signs, the limb signs; never pain "
    "with medicines). At most TWO yes/no facts in one question. Never ask about a fact that is already known. "
    "A fact marked CONFIRMATION must be asked on its own. A fact marked ASKED BEFORE was not answered last time: ask it ALONE, in "
    "different, everyday words (no clinical terms), one short question. After a partial answer to a bundle, ask only what is still missing. "
    "Write one or two short, warm, plain sentences, in the language the person used last (default English). The person you are "
    "talking to is usually a family member, not the patient: say 'the patient' until the sex is known, then 'he' or 'she' (never "
    "'he/she'), and 'you' only for the person answering, unless they said they are the patient. Acknowledge what was just said in a few words at most, and only when it "
    "adds something; never apologise or express sorrow more than once in a conversation, never say sorry about a 'no' or about a fact "
    "that is good news, and never repeat the same opening. Then ask. "
    "You only collect information for the hospital team: never assess, reassure, advise or answer other questions; if the person "
    "asked something else, say the counter staff can help with that, then ask.\n"
    'Return ONLY JSON: {"fields": ["<field id>", ...], "question": "..."}')


def _open_fields(st, facts):
    """Program side of dynamic mode: the derived agenda's open fields (engine.open_fields), in rank order, as
    dicts with field, hint, confirm. Attempts are counted per field; a confirmation under 'confirm.<field>'."""
    return engine.open_fields(facts, st["attempts"])


def stage_candidates(sid, st, cands):
    """Interview design v2 (#63): in the pre-arrival stage only the questions that settle the floor are asked (engine.
    pre_arrival_fields); when none is open the report is ready, the QR code is shown, and the remaining questions continue
    in the same chat. Returns the candidates for the stage, flipping the stage when the floor is settled."""
    if st.get("stage", "floor") != "floor":
        if st.get("floor"):                                # the floor is set: only questions the nurse or doctor reads remain
            keep = engine.after_report_fields()
            return [c for c in cands if c["field"] in keep or c["confirm"]]
        return cands
    pre = engine.pre_arrival_fields(floor_set=bool(st.get("floor")))
    stage = [c for c in cands if c["field"] in pre]
    if stage:
        return stage
    st["stage"] = "rest"; st["qr_ready"] = True; st["qr_turn"] = cli.turn_count(st)
    msg = (f"That's enough for the hospital team to prepare. Show the code {sid} at the counter when you arrive. "
           "I'll ask a few more things while you're on the way; tell me straight away if anything changes.")
    cli.add_msg(st, "bot", msg, kind="ack"); st["announce"] = msg
    cli.log_event(sid, "engine", note="floor settled - report ready; remaining questions continue")
    return stage_candidates(sid, st, cands)           # the very first question after the report obeys the after-report filter too


def pick_and_ask_dynamic(sid, st, facts):
    cands = stage_candidates(sid, st, _open_fields(st, facts))
    if not cands:
        cli.log_event(sid, "engine", note="interview complete - no open fields")
        return None
    top = cands[0]
    asked_before = st["attempts"].get(("confirm." if top["confirm"] else "") + top["field"], 0) >= 1
    if top["confirm"] or asked_before:
        offered = [top]                                   # a confirmation, or a re-ask: alone, in different words
    else:
        offered = [c for c in cands[:6] if not c["confirm"]]
    known = [f"{f} = {rec['value']!r}" for f, rec in facts.d.items() if f != "complaints"][-12:]
    listing = "\n".join(f"{i + 1}. {c['field']}{' (CONFIRMATION - ask alone)' if c['confirm'] else (' (ASKED BEFORE - ask alone, differently)' if asked_before else '')}: {c['hint']}" for i, c in enumerate(offered))
    prompt = (f"Known facts:\n" + ("\n".join(known) or "(none yet)") + f"\n\nRecent chat:\n{cli.context_window(st)}\n\n"
              f"Facts still needed, ranked:\n{listing}\n\nAllowed number of facts in this question: {1 if (top['confirm'] or asked_before) else DYN_MAX_FIELDS}.")
    out = llm.ask_json(prompt, system=DYN_SYSTEM)
    chosen = [f for f in (out.get("fields") or []) if isinstance(f, str)] if isinstance(out, dict) else []
    allowed = {c["field"] for c in offered}
    chosen = [f for f in dict.fromkeys(chosen) if f in allowed]
    if top["field"] not in chosen:
        chosen.insert(0, top["field"])                    # guard rail: the top-priority fact is always asked
    chosen = chosen[:1] if (top["confirm"] or asked_before) else engine.cap_yes_no(chosen[:DYN_MAX_FIELDS], 2)
    q = (out.get("question") if isinstance(out, dict) else "") or ""
    q = str(q).strip()
    if not q:                                             # model gave no usable question: fall back to the top field's hint
        q = top["hint"]
    for f in chosen:
        k = ("confirm." + f) if top["confirm"] else f
        st["attempts"][k] = st["attempts"].get(k, 0) + 1
    slot_id = ("confirm." + chosen[0]) if top["confirm"] else "dyn:" + "+".join(chosen)
    st["pending_slot"] = slot_id
    cli.add_msg(st, "bot", q, kind="question", slot=slot_id)
    cli.log_event(sid, "question", slot=slot_id, text=q, fields=chosen, offered=[c["field"] for c in offered])
    return q


def pick_and_ask(sid, st, facts):
    """cli._pick_and_ask with gap-aware re-phrasing: a partially answered compound
    slot re-asks ONLY its missing parts, acknowledging what is already known.
    INTERVIEW_MODE=dynamic hands the bundling to the model (pick_and_ask_dynamic)."""
    if INTERVIEW_MODE == "dynamic":
        return pick_and_ask_dynamic(sid, st, facts)
    bundle = engine.static_bundle(stage_candidates(sid, st, _open_fields(st, facts)))
    if not bundle:
        cli.log_event(sid, "engine", note="interview complete - no open fields")
        return None
    fields = [b["field"] for b in bundle]
    confirm = bundle[0]["confirm"]
    slot = {"id": ("confirm." + fields[0]) if confirm else "fld:" + "+".join(fields), "type": "composite",
            "fields": fields, "ask": " ".join(b["hint"] for b in bundle)}
    for f in fields:
        k = ("confirm." + f) if confirm else f
        st["attempts"][k] = st["attempts"].get(k, 0) + 1
    st["attempts"][slot["id"]] = max(st["attempts"].get(("confirm." if confirm else "") + f, 0) for f in fields)
    st["pending_slot"] = slot["id"]
    topic = slot["ask"]
    ctx = cli.context_window(st)
    retry = (" The person did not answer this last time - ask again, differently."
             if st["attempts"][slot["id"]] > 1 else "")
    q = llm.ask(f"Recent chat:\n{ctx}\n\nAsk this in one short, warm, plain-English sentence "
                f"(second person, no preamble):{retry}\nTopic: {topic}\n"
                f"Write in the same language the person used in their most recent message "
                f"(default English; Malay, Chinese, Tamil are all fine). "
                f"You only collect information for the hospital team. Never claim to prioritise, "
                f"assess, diagnose, reassure or decide anything, and do not answer other questions - "
                f"if the person asked something else, say the counter staff can help with that, "
                f"then ask the topic.").strip()
    cli.add_msg(st, "bot", q, kind="question", slot=slot["id"])
    cli.log_event(sid, "question", slot=slot["id"], text=q)
    return q



def esc_advice(st, tree, facts=None):
    """The bot's only permitted advice: escalate. Fires once, on ESI-1 indicators or when
    the caregiver reports the patient is not responding (danger_signs.responsive false).
    The latter is product behaviour, not a rulebook claim: A-01 needs the nurse's own
    observation (the floor comes from B-01 through a bridge), and the interview must never reassure."""
    unresponsive = facts is not None and facts.resolve("danger_signs.responsive") is False
    if (tree["esi1_indicators"] or unresponsive) and not st.get("advised995"):
        st["advised995"] = True
        msg = ("Based on what you just told me, please call 995 NOW if you are not "
               "already with paramedics. I have put this at the top of the hospital report.")
        cli.add_msg(st, "bot", msg, kind="advice")
        cli.log_event(st["sid"], "advice", text=msg)
        return msg
    return None


def worsening_check(st, facts):
    """After the report was first opened: pain above the baseline recorded at that
    open, or a floor/indicator change, marks the session worsening (report banner +
    the family is asked to alert the counter - the system has no line into staff)."""
    base = st.get("baseline")
    if not base:
        return None
    pain = facts.resolve("complaint.pain_latest") or facts.resolve("complaint.pain_rating")
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    worse = ((isinstance(pain, (int, float)) and isinstance(base.get("pain"), (int, float))
              and pain > base["pain"])
             or (tree["floor"] != base.get("floor"))
             or (bool(tree["esi1_indicators"]) and not base.get("esi1"))
             or (len(facts.complaints()) > base.get("n_complaints", len(facts.complaints()))))
    if worse and not st.get("worsening"):
        st["worsening"] = {"at_turn": cli.turn_count(st),
                           "ts": time.strftime("%H:%M")}
        msg = ("Thank you - please tell the counter staff now that the patient is feeling "
               "worse. I have also put this change at the top of the hospital report.")
        cli.add_msg(st, "bot", msg, kind="advice")
        cli.add_msg(st, "system", "worsening reported - family asked to alert the counter", kind="note")
        cli.log_event(st["sid"], "advice", text=msg, kind_note="worsening")
        return msg
    return None


def do_start():
    sid = new_ticket()
    sp, lp, tp = cli._paths(sid)
    st = {"sid": sid, "facts": {}, "attempts": {}, "messages": [], "stage": "floor",
          "floor": None, "phase": "enroute", "created": time.strftime("%Y-%m-%d %H:%M")}
    facts = engine.Facts()
    cli.log_event(sid, "engine", note=f"session {sid} started (web)")
    q = pick_and_ask(sid, st, facts)
    cli.save(sid, st, facts)
    return sid, q


DONT_KNOW_RE = re.compile(r"\b(don'?t|do not|dont|not) (know|sure|remember|aware)\b|\bno idea\b|\bunsure\b|\bnot that i know\b"
                          r"|\b(haven'?t|have not|didn'?t|did not) (taken|take|checked|check|measured|measure) (his|her|their|the) temp", re.I)   # an unmeasured temperature (18 Oct 2026)


def record_unknown(sid, st, facts, slot_id, text, n_before):
    """A caregiver's 'I don't know' is an answer. When the text says so, every asked field the extractor did not
    write is stored as unknown (value None, status 'unknown') so it closes, the report shows 'not known to the
    caregiver', and the answering-pattern note does not count it as a non-answer. Fields the answer did fill, and
    facts volunteered for other fields, are kept (v2: an answer can be partly 'I don't know')."""
    if not slot_id or slot_id == "checkin.status" or not DONT_KNOW_RE.search(text or ""):
        return False
    if len((text or "").split()) > 8 or n_before != len(facts.d):
        return False      # "just the bp pill, dont know the name. allergic to penicillin": the phrase is about one detail, not the question (15 Oct 2026)
    slot = _slot_by_id(slot_id)
    if not slot:
        return False
    fields = slot.get("fields") or ([slot["target"]] if slot.get("type") == "confirm" else [slot.get("field", slot_id)])
    turn = cli.turn_count(st)
    for f in fields:
        if facts.has(f) or f in engine.COMPLAINT_DETAILS or f == "complaint.category":
            continue                       # answered, or a complaint, which is never 'unknown' and is re-asked
        facts.write(f, None, status="unknown", who="caregiver", turn=turn)
    if not any(facts.has(f) and facts.resolve(f + ".status") == "unknown" and facts.d[f]["turn"] == turn for f in fields):
        return False
    cli.log_event(sid, "extract", writes=[(f, None) for f in fields if facts.has(f) and facts.resolve(f + ".status") == "unknown"], via="dont-know")
    return True


STATUS = {}   # sid -> what the server is doing with the caregiver's last message (shown on the chat page while a turn is slow, #79)


def do_answer(sid, text):
    st, facts = cli.load(sid)
    st["sid"] = sid
    was_pending = st.get("pending_slot")
    before, n_before = snapshot_safety(facts), len(facts.d)
    STATUS[sid] = "reading your answer"
    tree = cli._process_answer(sid, st, facts, text)
    st["checkins_unanswered"] = 0
    if record_unknown(sid, st, facts, was_pending, text, n_before):
        tree = engine.evaluate_tree(facts, engine.load_criteria())
    normalise_categories(sid, st, facts)
    conflicts = contradiction_guard(sid, st, facts, before, text)
    if was_pending == "checkin.status":
        checkin_pain_fallback(sid, st, facts, text, n_before)
    restore_attempt_if_volunteered(st, facts, was_pending, n_before, len(facts.d))
    if blanket_no_fill(sid, st, facts, text) | derive_mechanism_none(sid, st, facts) | bool(conflicts):
        tree = engine.evaluate_tree(facts, engine.load_criteria())
    replies = []
    adv = esc_advice(st, tree, facts)
    if adv: replies.append(adv)
    w = worsening_check(st, facts)
    if w: replies.append(w)
    STATUS[sid] = "choosing the next question"
    q = pick_and_ask(sid, st, facts)
    STATUS.pop(sid, None)
    if st.pop("announce", None):                           # the floor was settled this turn: say so before the next question
        replies.append(st["messages"][-2]["text"] if q else st["messages"][-1]["text"])
    complete = q is None
    if complete and not st.get("said_done"):
        st["said_done"] = True
        closing = ("Thank you - that's everything. Show the code "
                   f"{sid} at the counter when you arrive.")
        cli.add_msg(st, "bot", closing, kind="ack")
        replies.append(closing)
    elif q:
        replies.append(q)
    if not replies:
        # nothing to ask and nothing to escalate: never leave an answer unacknowledged
        now = time.strftime("%H:%M")
        ack = (f"Thank you - noted at {now}. I will check in again in a while; if anything "
               f"changes for the worse before then, tell the counter staff straight away."
               if was_pending == "checkin.status" else
               f"Noted at {now} - I have added that to the hospital report.")
        cli.add_msg(st, "bot", ack, kind="ack")
        cli.log_event(sid, "engine", note=f"acknowledged (no open slots): {ack[:40]}")
        replies.append(ack)
    cli.save(sid, st, facts)
    return replies, bool(st.get("qr_ready")), complete


def do_arrived(sid):
    """The family presses 'we've arrived': the waiting-room phase begins (periodic check-ins), and the baseline for the
    worsening check is recorded now. Idempotent."""
    st, facts = cli.load(sid)
    st["sid"] = sid
    if st.get("phase") == "waiting":
        return "already"
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    st["phase"] = "waiting"
    st["baseline"] = {"pain": facts.resolve("complaint.pain_latest") or facts.resolve("complaint.pain_rating"),
                      "floor": tree["floor"], "esi1": bool(tree["esi1_indicators"]), "n_complaints": len(facts.complaints())}
    cli.log_event(sid, "engine", note="family reports arrival - waiting-room phase begins")
    cli.add_msg(st, "system", "family reports arrival - waiting-room phase begins", kind="note")
    msg = ("Welcome. Show the code at the counter if you have not yet. I will check in with you now and then; "
           "if anything gets worse before then, tell the counter staff straight away.")
    cli.add_msg(st, "bot", msg, kind="ack")
    cli.save(sid, st, facts)
    return msg


def do_checkin(sid):
    """Waiting-room phase: the periodic 'how are they now?' question (fixed text, no LLM)."""
    st, facts = cli.load(sid)
    st["sid"] = sid
    if st.get("phase") != "waiting":
        return None
    if st.get("checkins_unanswered", 0) >= 3:
        return None                        # three check-ins with no reply: stop asking until the family writes again
    st["checkins_unanswered"] = st.get("checkins_unanswered", 0) + 1
    q = "How is the patient doing right now compared to when you arrived?"
    st["pending_slot"] = "checkin.status"
    cli.add_msg(st, "bot", q, kind="checkin", slot="checkin.status")
    st["last_checkin_ts"] = time.time()
    cli.log_event(sid, "question", slot="checkin.status", text=q)
    cli.save(sid, st, facts)
    return q


# ---------------- report page ----------------
def summary_grounded(para, facts):
    """Deterministic check on the AI paragraph: every number it contains must appear in a stored
    fact value or timestamp. Anything else is withheld rather than shown (design record:
    'one AI paragraph checked against the stored facts')."""
    pool = set()
    def collect(v):
        if isinstance(v, dict):
            for x in v.values(): collect(x)
        elif isinstance(v, list):
            for x in v: collect(x)
        elif v is not None:
            pool.update(re.findall(r"\d+(?:\.\d+)?", str(v)))
    collect(facts.d)
    nums = re.findall(r"\d+(?:\.\d+)?", para)
    return all(n in pool or n.lstrip("0") in pool for n in nums)


def open_report(sid):
    """Nurse/doctor view. Opening it changes nothing in the family's chat (until 15 Oct 2026 the first open started the
    waiting-room phase; now the family's own 'we've arrived' button does, do_arrived). Staff-only: the caregiver gets the
    ticket and the QR, never this page (team decision 19 Sep 2026). A 'changed since last opened' list was removed the
    same day: any page load by anyone counted as a read, and it compared arrival turns, not values."""
    st, facts = cli.load(sid)
    st["sid"] = sid
    turn = cli.turn_count(st)
    tree = engine.evaluate_tree(facts, engine.load_criteria())
    # cached AI summary, regenerated only when new material arrived
    if st.get("summary_turn") != turn:
        try:
            body = report.render(sid, facts, tree, with_summary=True)
            m = re.search(r"SUMMARY \(AI-written[^\n]*\n((?:  .*\n)+)", body)
            para = m.group(1).strip() if m else ""
            if para and not summary_grounded(para, facts):
                cli.log_event(sid, "engine", note="AI summary withheld: a number in it is not in the stored facts")
                para = ""
            st["summary"] = para
        except Exception:
            body = report.render(sid, facts, tree, with_summary=False)
            st["summary"] = "(summary unavailable)"
        st["summary_turn"] = turn
    text = report.render(sid, facts, tree, with_summary=False)
    cli.log_event(sid, "engine", note="report rendered (web)")
    cli.save(sid, st, facts)
    return st, tree, text


def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>
:root {{ --ink:#1a2b45; --accent:#3e8e4f; --warn:#b3261e; }}
body {{ font-family: system-ui, sans-serif; margin:0; background:#f4f6f9; color:var(--ink); }}
.wrap {{ max-width: 760px; margin: 0 auto; padding: 16px; }}
.card {{ background:#fff; border-radius:10px; padding:16px; margin:12px 0; box-shadow:0 1px 4px rgba(0,0,0,.08); }}
.banner {{ border:2px solid var(--warn); background:#fff4f2; border-radius:10px; padding:12px 16px; margin:12px 0; }}
pre {{ white-space: pre-wrap; font: 12px/1.5 ui-monospace, monospace; overflow-x:auto; }}
.btn {{ background:var(--accent); color:#fff; border:0; border-radius:8px; padding:12px 18px; font-size:16px; cursor:pointer; }}
.muted {{ color:#5a6a82; font-size: 13px; }}
h1 {{ font-size:20px; }} h2 {{ font-size:16px; }}
</style></head><body><div class="wrap">{body}</div></body></html>"""


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _chip(rec):
    colors = {"confirmed": "#1b7f3b", "probable": "#b07a00", "reported": "#5a6a82", "unknown": "#8a94a6"}
    c = colors.get(rec.get("status"), "#5a6a82")
    who = _esc({"persona": "caregiver", "persona-photo": "photo"}.get(rec.get("who"), rec.get("who", "?"))); turn = rec.get("turn")
    when = rec.get("ts", "")[-5:] if rec.get("ts") else (f"t{turn}" if turn is not None else "")
    return (f'<span style="background:{c};color:#fff;border-radius:10px;padding:1px 8px;'
            f'font-size:11px;white-space:nowrap">{rec.get("status","?")} - {who}'
            + (f' - {when}' if when else "") + "</span>")


def _val(v, status=None):
    if status == "unknown": return "not known to the caregiver"
    if v is True: return "YES"
    if v is False: return "no"
    if v in (None, "", []): return "-"
    if isinstance(v, list): return ", ".join(str(x) for x in v)
    return str(v)


def _row(label, rec, abs_rec=None):
    warn = rec.get("value") is True and not label.startswith("responsive")
    style = 'style="color:#b3261e;font-weight:700"' if warn else ""
    shown = _esc(_val(rec.get("value"), rec.get("status")))
    if abs_rec:
        shown += f' <span class="muted">{_esc(_val(abs_rec.get("value")))}</span>'
    return (f'<tr><td class="lbl">{_esc(label)}</td><td {style}>{shown}</td>'
            f'<td class="chipcol">{_chip(rec)}</td></tr>')


def render_html_report(sid, st, facts, tree):
    esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;")
    name = esc(facts.resolve("identity.name") or "(not collected)")
    dob = esc(facts.resolve("identity.dob") or "(not collected)")
    B = []
    add = B.append
    add(f'<div class="rephead"><div><b>PRE-ARRIVAL INTAKE REPORT</b> - session {sid} '
        f'<span class="muted">- prototype output, advisory only</span></div></div>')
    add(f'<div class="card idcard"><div><span class="muted">Patient AS DECLARED by caregiver</span><br>'
        f'<b style="font-size:19px">{name}</b> &nbsp; DOB {dob}</div>'
        f'<div class="unver">NOT VERIFIED<br><span>confirm against the patient</span></div></div>')
    if st.get("worsening"):
        add(f'<div class="banner"><b>CHANGED FOR THE WORSE</b> (reported {st["worsening"]["ts"]}) - '
            f'family was asked to alert the counter staff.</div>')
    if st.get("contradictions"):
        add('<div class="banner"><b>CONFLICTING REPORTS - confirm these directly:</b><ul>'
            + "".join(f'<li>{c["ts"]} - {esc(c["what"])} <span class="muted">(said: &ldquo;{esc(c["said"])}&rdquo;)</span></li>'
                      for c in st["contradictions"]) + "</ul></div>")
    capped = [k for k, v in st.get("attempts", {}).items() if v >= 3]
    if st.get("contradictions") or capped:
        add(f'<div class="banner amber"><b>Answering-pattern note:</b> {len(st.get("contradictions", []))} '
            f'conflicting answer(s), {len(capped)} question(s) without a usable answer after three attempts'
            + (f' ({", ".join(capped)})' if capped else "") + '. Answers of "don\'t know" are recorded as such and not counted here.</div>')
    if facts.resolve("danger_signs.responsive") is False:
        add('<div class="banner"><b>CAREGIVER REPORTS THE PATIENT IS NOT RESPONDING NORMALLY</b> - 995 escalation was advised in the chat. '
            '<span class="muted">Counted as altered mental status for rule B-01 (floor at least ESI-2, bridge BR-01.not-responding); the level-1 rule A-01 needs the nurse\'s own observation - confirm responsiveness on arrival.</span></div>')
    if tree["esi1_indicators"]:
        add('<div class="banner"><b>POSSIBLE ESI-1 INDICATORS (reported)</b> - advise 995 escalation:<ul>'
            + "".join(f'<li><b>{r["id"]}</b> <span class="muted">{esc(r.get("source"))}</span></li>'
                      for r in tree["esi1_indicators"]) + "</ul></div>")
    if tree["floor"]:
        def src_text(v):   # a source may be one string or a list; drop the local file paths
            items = v if isinstance(v, list) else [v]
            return " · ".join(re.sub(r"\s*\(sources/[^)]*\)", "", str(x)).strip() for x in items if x)
        rules_html = "".join(
            f'<div class="rule"><b>{r["id"]}</b><br><span class="muted">source: {esc(src_text(r.get("source")))}</span>'
            + (f'<br><span class="muted">&ldquo;{esc(r["span"])}&rdquo;</span>' if r.get("span") and not str(r["span"]).lstrip().startswith("(") else "")
            + "</div>" for r in tree["fired"])
        add(f'<div class="card floorcard"><div class="floorbadge">{tree["floor"].upper()}</div>'
            f'<div class="muted">computed WITHOUT vitals - a floor, not a final level; '
            f'nurse assessment prevails</div>{rules_html}'
            f'<div class="muted">Pending: {", ".join(tree["pending"])}</div></div>')
    else:
        add('<div class="card floorcard"><div class="floorbadge gray">NO FLOOR ESTABLISHED SO FAR</div>'
            '<div class="muted">no rule has fired on the facts collected so far; pending: '
            + ", ".join(tree["pending"]) + "</div></div>")
    sig = practice_signal.signal(facts)   # second lane: learned, advisory, never moves the floor (design record, "two lanes")
    if sig:
        add('<div class="card" style="border-left:4px solid #1a4a7a"><b>Practice signal</b> <span class="muted">(learned from past visits)</span>'
            f'<div style="margin:6px 0">{esc(practice_signal.wording(sig))}</div>'
            '<div class="muted">Does not change the floor above. <a href="/about-signal">About this signal</a></div></div>')
    if tree["consider"]:
        add('<div class="card"><b>Consider flags</b> <span class="muted">(handbook: judgment, not automatic)</span><ul>'
            + "".join(f'<li>{r["id"]} <span class="muted">{esc(r.get("source"))}</span></li>'
                      for r in tree["consider"]) + "</ul></div>")
    if tree.get("notes"):
        add('<div class="card"><b>Context notes</b> <span class="muted">(handbook background for reading other findings; not a flag)</span><ul>'
            + "".join(f'<li>{esc(r.get("span"))} <span class="muted">{r["id"]} · {esc(r.get("source"))}</span></li>'
                      for r in tree["notes"]) + "</ul></div>")
    recs = facts.complaints()
    if recs:
        cards = []
        for i, r in enumerate(recs):
            dets = "".join(f'<tr><td class="lbl">{k}</td><td>{esc(_val(r[k]["value"]))}'
                           + (f' <span class="muted">{esc(r["onset_abs"]["value"])}</span>'
                              if k == "onset" and "onset_abs" in r else "") + '</td>'
                           f'<td class="chipcol">{_chip(r[k])}</td></tr>'
                           for k in ("text", "onset", "pain_rating") if k in r)
            cards.append(f'<div class="complaint"><b>{i + 1}. {esc(r["category"])}</b>'
                         + (' <span class="pres">presenting</span>' if i == 0 else "")
                         + f' {_chip(r["opened"])}<table>{dets}</table></div>')
        add('<div class="card"><h2>Complaints <span class="muted">(in order reported)</span></h2>'
            + "".join(cards) + "</div>")
    worst, latest = facts.d.get("complaint.pain_rating"), facts.d.get("complaint.pain_latest")
    if worst:
        trend = ""
        if latest and latest["value"] != worst["value"]:
            trend = f' &rarr; latest <b>{_esc(latest["value"])}</b> <span class="muted">({latest.get("ts","")[-5:]})</span>'
        add(f'<div class="card"><h2>Pain (0-10)</h2><table><tr><td class="lbl">worst reported</td>'
            f'<td><b>{_esc(worst["value"])}</b>{trend}</td><td class="chipcol">{_chip(latest or worst)}</td></tr></table></div>')
    for title, fields in report.SECTIONS:
        rows = [(f, facts.d[f]) for f in fields if f in facts.d]
        if not rows:
            continue
        add(f'<div class="card"><h2>{title}</h2><table>'
            + "".join(_row(f.split(".")[-1].replace("_", " "), rec, facts.d.get(f + "_abs"))
                      for f, rec in rows)
            + "</table></div>")
    # a gap is a report field the interview would still ask of THIS patient (asked of everyone, or applicable on the facts
    # so far, by engine.open_fields' test): a field that does not apply, such as a pregnancy question for a man, is not a gap (#112)
    applies = {o["field"] for o in engine.open_fields(facts, {}) if not o["confirm"]}
    missing = [f for _, fs in report.SECTIONS for f in fs if f in applies]
    if missing:
        add('<div class="card"><h2>Not collected <span class="muted">(not asked, or not answered)</span></h2>'
            '<p class="muted">' + ", ".join(f.split(".")[-1].replace("_", " ") for f in missing) + "</p></div>")
    if st.get("summary"):
        add(f'<div class="card"><h2>AI summary</h2><p>{esc(st["summary"])}</p>'
            f'<p class="muted">written from the stored facts above; every number in it was checked against them</p></div>')
    add('<p class="muted">Advisory only. All items caregiver/patient-reported unless marked confirmed. '
        'This report never assigns a final triage level; only the nurse does. '
        f'<a href="/rules">Rulebook</a> - <a href="/report-txt/{sid}">plain text</a></p>')
    css = """
.rephead { margin: 4px 0 10px; } .muted { color:#5a6a82; font-size:13px; }
.idcard { display:flex; justify-content:space-between; align-items:center; gap:12px; }
.unver { background:#fff4f2; border:2px solid #b3261e; color:#b3261e; font-weight:800;
         padding:8px 12px; border-radius:8px; text-align:center; font-size:14px; }
.unver span { font-weight:400; font-size:11px; }
.floorbadge { display:inline-block; background:#b3261e; color:#fff; font-weight:800;
              font-size:18px; padding:6px 14px; border-radius:8px; margin-bottom:6px; }
.floorbadge.gray { background:#5a6a82; }
.rule { margin:8px 0; padding:8px 10px; background:#f4f6f9; border-radius:8px; }
.banner.amber { border-color:#b07a00; background:#fff9ec; }
table { width:100%; border-collapse:collapse; }
td { padding:5px 6px; border-top:1px solid #eef1f6; vertical-align:top; font-size:14px; }
td.lbl { color:#5a6a82; width:38%; } td.chipcol { text-align:right; width:26%; }
.complaint { border:1px solid #e3e8f0; border-radius:8px; padding:10px; margin:8px 0; }
.pres { background:#3e8e4f; color:#fff; border-radius:10px; padding:1px 8px; font-size:11px; }
h2 { margin: 2px 0 8px; }"""
    return page(f"Report {sid}", f"<style>{css}</style>" + "".join(B))



def report_page(sid):
    st, tree, text = open_report(sid)
    return render_html_report(sid, st, cli.load(sid)[1], tree)


# ---------------- HTTP plumbing ----------------
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # noqa: E402

CHAT_HTML = open(os.path.join(HERE, "chat.html")).read()
LANDING_HTML = open(os.path.join(HERE, "landing.html")).read()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _base(self):
        """Public base URL as the browser saw it: a tunnel/proxy (Cloudflare, ngrok)
        passes Host and X-Forwarded-Proto, so the QR and report links match whatever
        host served the page. Falls back to PUBLIC_BASE when a client sends no Host."""
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host")
        if not host:
            return PUBLIC_BASE
        local = host.split(":")[0] in ("localhost", "127.0.0.1") or host.startswith("[::1]")
        proto = self.headers.get("X-Forwarded-Proto") or ("http" if local else "https")
        return f"{proto}://{host}"

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj), "application/json")

    def do_GET(self):
        p = self.path.split("?")[0]
        try:
            if p == "/" :
                return self._send(200, LANDING_HTML)
            if p.startswith("/chat/"):
                sid = p.split("/")[2]
                if not valid_sid(sid): return self._send(404, page("Not found", "<p>No such session.</p>"))
                return self._send(200, CHAT_HTML.replace("__SID__", sid)
                                  .replace("__CHECKIN__", str(CHECKIN_SECONDS)))
            if p == "/api/info":
                info = {"interview_mode": INTERVIEW_MODE, "backend": llm.BACKEND, "model": llm.MODEL_NAME(), "dyn_max_fields": DYN_MAX_FIELDS,
                        "temperature": os.environ.get("LLM_TEMPERATURE", "backend default")}
                if hasattr(llm, "USAGE"): info["usage"] = dict(llm.USAGE); info["cost_usd"] = round(llm.cost(), 4)   # the Claude backend counts tokens (#82)
                return self._json(info)
            if p.startswith("/api/state/"):
                sid = p.split("/")[3]
                if not valid_sid(sid): return self._json({"error": "no such session"}, 404)
                st, facts = cli.load(sid)
                msgs = [{"role": m["role"], "text": m["text"], "ts": m.get("ts", "")[-8:-3],
                         "kind": m.get("kind", "")}
                        for m in st.get("messages", []) if m["role"] != "system"]
                status = STATUS.get(sid, "")
                if status and llm.STATUS["text"]: status += f" ({llm.STATUS['text']})"
                return self._json({"sid": sid, "messages": msgs,
                                   "started": st.get("created", ""),
                                   "phase": st.get("phase", "enroute"), "stage": st.get("stage", "floor"),
                                   "done": bool(st.get("qr_ready") or st.get("said_done")),      # the report is ready: show the QR code
                                   "complete": bool(st.get("said_done")),                           # nothing more to ask
                                   "asked": engine.fields_of_question_id(st.get("pending_slot")),   # #17: the fields the open question asks
                                   "status": status,
                                   "report_url": f"{self._base()}/r/{sid}"})
            if p.startswith("/r/"):
                sid = p.split("/")[2]
                if not valid_sid(sid): return self._send(404, page("Not found", "<p>No such session.</p>"))
                with lock_for(sid):
                    return self._send(200, report_page(sid))
            if p.startswith("/report-txt/"):
                sid = p.split("/")[2]
                if not valid_sid(sid): return self._send(404, "no such session", "text/plain")
                st, facts = cli.load(sid)
                tree = engine.evaluate_tree(facts, engine.load_criteria())
                return self._send(200, report.render(sid, facts, tree, with_summary=False), "text/plain; charset=utf-8")
            if p.startswith("/qr/"):
                sid = p.split("/")[2].removesuffix(".svg")
                if not valid_sid(sid): return self._send(404, "no such session", "text/plain")
                import segno, io
                buf = io.BytesIO()
                segno.make(f"{self._base()}/r/{sid}").save(buf, kind="svg", scale=5, border=1)
                return self._send(200, buf.getvalue(), "image/svg+xml")
            if p == "/about-signal":
                _, meta = practice_signal.load()
                if not meta: return self._send(404, page("Not found", "<p>No model file.</p>"))
                body = (f"<h1>About the practice signal</h1>"
                        f"<p>The practice signal is the report's second lane. It is learned from {meta['n_train']:,} {_esc(meta['data'])}, "
                        f"using only what a caregiver can report before arrival: age, complaint group, injury mechanism, fever, "
                        f"anticoagulation and immune status. No vital signs.</p>"
                        f"<p>For a visit it estimates the share of similar past visits that nurses triaged ESI 1-2, and the report shows "
                        f"one of three sentences: <b>most were ESI 1 or 2</b> (estimated share at or above {meta.get('band_high', 0.5):.0%}), "
                        f"<b>about half were ESI 1 or 2</b>, or <b>most were ESI 3, 4 or 5</b> (share at or below {meta.get('band_low', 0.2):.0%}). "
                        f"The base rate in the training data is {meta['prevalence']:.0%}.</p>"
                        f"<p>Model: gradient boosting, unweighted so that the share is calibrated (checked by decile). "
                        f"Discrimination on held-out visits: AUROC {meta['auroc']:.2f}. The training site is one US health system; "
                        f"the label is the recorded nurse level, so the signal describes past practice there, not outcomes.</p>"
                        f"<p>The signal is computed from the stored facts at render time and writes nothing to the rule engine: the ESI floor "
                        f"above it on the report is unchanged by it.</p>"
                        f"<p class=\"muted\">Details: <code>prototype/practice_signal.py</code>, <code>experiments/out/practice-signal.md</code>.</p>")
                return self._send(200, page("About the practice signal", body))
            if p == "/rules" or p.startswith("/rules"):
                body, _ = rules_inspector.build_html()
                return self._send(200, body)
            return self._send(404, page("Not found", "<p>Unknown path.</p>"))
        except Exception as e:
            return self._send(500, page("Error", f"<p>Server error: {str(e)[:300]}</p>"))

    def do_POST(self):
        p = self.path.split("?")[0]
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            if p == "/api/start":
                if not body.get("coming_in"):
                    return self._json({"refused": True,
                        "message": "This service is only for people already coming to the "
                                   "emergency department. If this is an emergency, call 995."})
                sid, q = do_start()
                return self._json({"sid": sid, "question": q})
            if p.startswith("/api/answer/"):
                sid = p.split("/")[3]
                if not valid_sid(sid): return self._json({"error": "no such session"}, 404)
                text = (body.get("text") or "").strip()
                if not text: return self._json({"error": "empty"}, 400)
                if len(text) > 2000:
                    return self._json({"replies": ["That message is very long - could you tell me the most "
                                                   "important part in a sentence or two?"], "error": "too_long"}, 400)
                with lock_for(sid):
                    # a double-tap on Send re-sends the same text within seconds: answer
                    # once, return the same replies, never burn a second turn on it
                    st_peek, _ = cli.load(sid)
                    msgs = st_peek.get("messages", [])
                    last = [m for m in msgs if m["role"] == "caregiver"]
                    bot_since = bool(last) and any(m["role"] == "bot" for m in msgs[msgs.index(last[-1]) + 1:])
                    # a duplicate only while the previous identical answer is still unanswered: once the bot has replied, the
                    # same short text again ("no fever no rash") is a new answer (15 Oct 2026: it had looped a question for ever)
                    if last and last[-1]["text"] == text and not bot_since and (time.time() - _ts_epoch(last[-1].get("ts"))) < 8:
                        after = st_peek["messages"][st_peek["messages"].index(last[-1]) + 1:]
                        return self._json({"replies": [m["text"] for m in after if m["role"] == "bot"],
                                           "done": bool(st_peek.get("qr_ready") or st_peek.get("said_done")),
                                           "complete": bool(st_peek.get("said_done")),
                                           "asked": engine.fields_of_question_id(st_peek.get("pending_slot")), "duplicate": True})
                    replies, done, complete = do_answer(sid, text)
                    st_after, _ = cli.load(sid)
                return self._json({"replies": replies, "done": done, "complete": complete,
                                   "asked": engine.fields_of_question_id(st_after.get("pending_slot"))})
            if p.startswith("/api/arrived/"):
                sid = p.split("/")[3]
                if not valid_sid(sid): return self._json({"error": "no such session"}, 404)
                with lock_for(sid):
                    msg = do_arrived(sid)
                return self._json({"message": None if msg == "already" else msg, "phase": "waiting"})
            if p.startswith("/api/checkin/"):
                sid = p.split("/")[3]
                if not valid_sid(sid): return self._json({"error": "no such session"}, 404)
                with lock_for(sid):
                    q = do_checkin(sid)
                return self._json({"question": q})
            return self._json({"error": "unknown endpoint"}, 404)
        except Exception as e:
            return self._json({"error": str(e)[:300]}, 500)


if __name__ == "__main__":
    print(f"webapp: http://localhost:{PORT}   public base: {PUBLIC_BASE}")
    print(f"sessions dir: {cli.SESS}   llm backend: {llm.BACKEND}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
