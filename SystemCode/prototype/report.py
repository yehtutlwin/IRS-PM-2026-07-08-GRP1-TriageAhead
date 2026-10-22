"""Text nurse report: deterministic layout; one optional Gemini summary paragraph."""
import re
import engine
import llm

SECTIONS = [
    ("PATIENT", ["patient.age", "patient.sex"]),
    ("EVENTS & CONTEXT", ["E.mechanism", "E.fall_height_meters", "E.head_strike", "E.loc",
                          "complaint.vaginal_bleeding", "complaint.acs_suspicion"]),
    ("A - ALLERGIES", ["A.allergies"]),
    ("M - MEDICATIONS", ["M.medications", "M.anticoagulant"]),
    ("P - PAST HISTORY", ["history.conditions", "history.immunocompromised",
                          "history.pregnant", "history.postpartum"]),
    ("L - LAST INTAKE", ["L.last_intake"]),
    ("INFECTION SCREEN", ["complaint.fever", "infection.rash", "infection.travel_14d",
                          "infection.contacts"]),
    ("DANGER SIGNS (asked first)", ["danger_signs.responsive", "danger_signs.chest_pain_now",
                                 "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding"]),
]

def chip(rec):
    return f"[{rec['who']} - turn {rec['turn']} - {rec['status']}]"

def render(session_id, facts, tree, with_summary=True):
    L = []
    add = L.append
    add("=" * 72)
    add(f"PRE-ARRIVAL INTAKE REPORT       session {session_id}   (prototype output)")
    add("=" * 72)
    name = facts.resolve("identity.name") or "(not collected)"
    dob = facts.resolve("identity.dob") or "(not collected)"
    add(f"Patient AS DECLARED by caregiver: {name}, DOB {dob}")
    add(">> NOT verified by the system - confirm name/DOB against the patient. <<")
    add("-" * 72)
    if tree["esi1_indicators"]:
        add("!!! POSSIBLE ESI-1 INDICATORS (reported) - advise call 995 escalation:")
        for r in tree["esi1_indicators"]:
            add(f"    {r['id']}  [{r['source']}]")
    if tree["floor"]:
        add(f"FLOOR: {tree['floor'].upper()} - computed WITHOUT vitals")
        for r in tree["fired"]:
            add(f"    rule {r['id']}")
            srcs = r["source"] if isinstance(r["source"], list) else [r["source"]]
            add("      source: " + " · ".join(re.sub(r"\s*\(sources/[^)]*\)", "", str(x)).strip() for x in srcs))
    else:
        add("FLOOR: none established so far (no rule has fired on the facts collected so far)")
    if tree["consider"]:
        add("CONSIDER FLAGS (handbook: judgment, not automatic):")
        for r in tree["consider"]:
            add(f"    {r['id']}  [{r['source']}]")
    if tree.get("notes"):
        add("CONTEXT NOTES (handbook background for reading other findings; not a flag):")
        for r in tree["notes"]:
            add(f"    {r['id']}  \"{r['span']}\"  [{r['source']}]")
    add(f"Pending decision points: {', '.join(tree['pending'])}")
    add("This is a floor, not a final level. Nurse assessment prevails.")
    try:
        import practice_signal
        sig = practice_signal.signal(facts)
    except Exception:
        sig = None
    if sig:   # second lane: learned, advisory; never changes the floor above
        add("PRACTICE SIGNAL (learned from past visits; does not change the floor above):")
        add("    " + practice_signal.wording(sig))
    add("-" * 72)
    recs = facts.complaints() if hasattr(facts, "complaints") else []
    if recs:
        add("COMPLAINTS (in order reported; first = presenting)")
        for i, r in enumerate(recs):
            head = f"  {i+1}. {r['category']}" + ("  (presenting)" if i == 0 else "")
            add(f"{head:<40} {chip(r['opened'])}")
            for det in ("text", "onset", "pain_rating"):
                if det in r:
                    add(f"       {det:<17} = {r[det]['value']!r:<33} {chip(r[det])}")
        add("")
    elif any(f in facts.d for f in ("complaint.category", "complaint.text")):
        add("CHIEF COMPLAINT (legacy flat session)")
        for f in ("complaint.category", "complaint.text", "complaint.onset", "complaint.pain_rating"):
            if f in facts.d:
                rec = facts.d[f]
                add(f"  {f.split('.')[-1]:<22} = {('not known to the caregiver' if rec.get('status') == 'unknown' else repr(rec['value'])):<38} {chip(rec)}")
        add("")
    for title, fields in SECTIONS:
        rows = [(f, facts.d[f]) for f in fields if f in facts.d]
        if not rows:
            continue
        add(title)
        for f, rec in rows:
            add(f"  {f.split('.')[-1]:<22} = {('not known to the caregiver' if rec.get('status') == 'unknown' else repr(rec['value'])):<38} {chip(rec)}")
        add("")
    # not collected = what the interview asks of everyone (derived agenda, policy always) and did not get
    agenda = engine.load_agenda()
    missing = [f"  {f}" for f, e in agenda.items() if e["ask_policy"] == "always" and f not in facts.d]
    if missing:
        add("NOT COLLECTED (not asked, or not answered):")
        L += missing
        add("")
    if with_summary:
        def _plain(f, r):
            if f == "complaints":
                return "complaints: " + "; ".join(
                    f"{c['category']} (" + ", ".join(f"{k}={c[k]['value']}" for k in
                    ("text", "onset", "pain_rating") if k in c) + ")" for c in r["value"])
            return f"{f}: {r['value']}"
        facts_txt = "\n".join(_plain(f, r) for f, r in facts.d.items())
        para = llm.ask(
            "Write a 3-4 sentence clinical hand-over paragraph using ONLY these facts. "
            "Plain prose, no new information, no advice:\n" + facts_txt)
        add("SUMMARY (AI-written from the facts above only - not independently checked):")
        add("  " + para.strip().replace("\n", "\n  "))
        add("")
    add("Advisory only. All items caregiver/patient-reported unless marked confirmed.")
    add("This report never assigns a final triage level; only the nurse does.")
    add("=" * 72)
    return "\n".join(L)
