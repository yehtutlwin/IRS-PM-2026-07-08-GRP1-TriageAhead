"""The interview loop: the engine picks the open fields from the derived agenda, the model phrases them, a second model
role-plays the persona, Gemini extracts schema-bound facts, engine re-evaluates."""
import engine, llm, extraction


def phrase(bundle, transcript, attempt):
    ctx = "\n".join(transcript[-4:])
    retry = " The person did not answer this last time - gently ask again differently." if attempt > 0 else ""
    return llm.ask(
        f"Recent chat:\n{ctx}\n\nAsk this, in one short natural sentence (warm, plain English, "
        f"second person, no preamble):{retry}\nTopic: {' '.join(b['hint'] for b in bundle)}").strip()


def persona_answer(voice, question, transcript):
    ctx = "\n".join(transcript[-6:])
    return llm.ask(
        f"Recent chat:\n{ctx}\n\nThe intake assistant asks: \"{question}\"\n"
        f"Reply in character, 1-2 short sentences. Answer what was asked; you may "
        f"volunteer one extra detail if natural. Do not list everything you know.",
        system=voice).strip()


def extract(question, answer, asked, open_now):
    out = llm.ask_json(
        f"Question asked (about {', '.join(asked)}): {question}\nAnswer given: {answer}",
        system=extraction.system_prompt(asked, open_now))
    return out.get("writes", []) if isinstance(out, dict) else []


def run_interview(persona, criteria, log, max_turns=16):
    facts = engine.Facts()
    attempts = {}
    transcript = []
    turn = 0
    tree = engine.evaluate_tree(facts, criteria)
    while turn < max_turns:
        open_now = engine.open_fields(facts, attempts)
        bundle = engine.static_bundle(open_now)
        if not bundle:
            break
        turn += 1
        asked = [b["field"] for b in bundle]
        for f in asked:
            attempts[f] = attempts.get(f, 0) + 1
        q = phrase(bundle, transcript, max(attempts[f] for f in asked) - 1)
        a = persona_answer(persona["voice"], q, transcript)
        transcript += [f"BOT: {q}", f"THEM: {a}"]
        log(f"  BOT : {q}")
        log(f"  THEM: {a}")
        for w in extraction.guard(extract(q, a, asked, [o["field"] for o in open_now]), a)[0]:
            f, v = w.get("field"), w.get("value")
            if f:
                facts.write(f, v, status="probable" if w.get("status") == "probable" else "reported", who=persona.get("who", "caregiver"), turn=turn)
        engine.derive(facts, turn)
        prev_floor = tree["floor"]
        tree = engine.evaluate_tree(facts, criteria)
        if tree["floor"] != prev_floor:
            log(f"  >>> FLOOR CHANGED: {tree['floor']}  (rules: {[r['id'] for r in tree['fired']]})")
    return facts, tree, transcript, turn

