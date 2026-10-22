"""The extraction step's instructions, knowledge base v2 (issue #57): the instruction part is an authored text
(extract_instructions.txt); the field part is rendered from rules/fields.yaml and the derived agenda at call time,
so the model sees the fields that are asked, open or always allowed, each with its meaning and allowed values."""
import os, re
import engine

HERE = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS = open(os.path.join(HERE, "extract_instructions.txt")).read()
TYPE_WORD = {"bool": "true/false", "number": "number", "text": "short string", "list": "list of strings", "enum": "one of"}


def _line(name, spec):
    t = spec["type"]
    if t == "enum":   # each allowed value with its definition (an option entry in rules/terms.yaml), so the model does not guess from the name
        vm = engine.option_definitions(name)
        vals = "; ".join(f"{v} = {vm[v]}" if v in vm else str(v) for v in spec.get("values", []))
        kind = f"one of: {vals}"
    else:
        kind = TYPE_WORD.get(t, t)
    return f"- {name} ({kind}): {spec['gloss']}"      # gloss: the one-line definition written for this step (rules/fields.yaml)


def allowed_fields(asked=(), open_fields=()):
    """The fields the extractor may write this turn: the ones just asked, every field asked of everyone, every field
    that is open now, every field that may only be volunteered, and the complaint detail fields."""
    agenda, fields = engine.load_agenda(), engine.load_fields()
    names = []
    def add(f):
        if f in fields and f not in names: names.append(f)
    for f in asked: add(f)
    for f, e in agenda.items():
        if e["ask_policy"] in ("always", "volunteered_only"): add(f)
    for f in open_fields: add(f)
    for f in ("complaint.category", "complaint.text", "complaint.onset", "complaint.pain_rating"): add(f)
    return names


def system_prompt(asked=(), open_fields=()):
    fields = engine.load_fields()
    names = allowed_fields(asked, open_fields)
    asked = [f for f in asked if f in fields]
    head = ""
    if asked:
        head = ("\n\nFIELDS ASKED IN THIS QUESTION - decide each one: either a write (true, false, or the value) or its name in "
                "\"not_addressed\" when the answer says nothing about it. Every asked field appears in one of the two.\n"
                + "\n".join(_line(f, fields[f]) for f in asked) + "\n")
    section = "\n".join(_line(f, fields[f]) for f in names)
    return INSTRUCTIONS.rstrip() + head + "\n\nAllowed fields and values (the asked ones again, and everything else the caregiver may volunteer):\n" + section + "\n"


def _norm(t):
    return re.sub(r"[^a-z0-9 ]+", " ", str(t or "").lower()).strip()


def guard(writes, answer_text, asked_fields=()):
    """Three checks on what fact extraction wrote, all from the caregiver's own words (returns (kept, dropped)):
    1. stated-only fields: kept only when one of the field's words is in the answer (a deduced value never enters); a 'no' to
       the field the question asked is kept, since it answers the question rather than deducing anything;
    2. a denial (a yes/no field written false) to a field the answer does not address is dropped when the answer did
       address something else that was asked. Issue #80: to 'awake and responding, chest pain, trouble breathing, heavy
       bleeding?' the answer 'he is awake and has no pain' addressed two items, so the 'no's to breathing and bleeding are
       dropped. A bare 'no' that addresses nothing by name answers the question as asked and is kept. Addressing = one of
       the field's keywords (engine.field_keywords: name, gloss, everyday wording, stated-only words) is in the answer.
       A dropped denial costs one re-ask; a false denial hides a danger sign, so the guard errs this way on purpose;
    3. a write that carries a `quote` must quote the answer: if the quote is not in the answer, the write is dropped."""
    fields = engine.load_fields(); text = _norm(answer_text); raw = (answer_text or "").lower()
    writes = [w for w in writes if isinstance(w, dict)]
    quotes = {}                                            # normalised quote -> how many writes rest on it
    for w in writes:
        q = _norm(w.get("quote"))
        if q: quotes[q] = quotes.get(q, 0) + 1
    def own_quote(w):                                      # a quote that is in the answer and shared with no other write
        q = _norm(w.get("quote")); return bool(q) and q in text and quotes.get(q, 0) == 1
    addressed = {f for f in (asked_fields or ()) if any(k in text for k in engine.field_keywords(f))}
    addressed |= {w["field"] for w in writes if own_quote(w)}
    kept, dropped = [], []
    for w in writes:
        spec = fields.get(w.get("field"), {})
        words = spec.get("stated_only")
        answered_no = w.get("value") is False and w.get("field") in set(asked_fields or ())   # a 'no' to the question asked is an answer, not a deduction (16 Oct 2026: 'No, I don't have any conditions' to the immune-status question was dropped and the question asked again)
        if words and not answered_no and not any(str(k).lower() in raw for k in words):
            dropped.append(dict(w, why="not stated")); continue
        if (spec.get("type") == "bool" and w.get("value") is False and addressed and w["field"] not in addressed
                and not any(k in text for k in engine.field_keywords(w["field"]))):
            dropped.append(dict(w, why="denial of something the answer does not address")); continue
        q = _norm(w.get("quote"))
        if q and q not in text and spec.get("type") != "list":    # a list carries earlier items forward: not held to this answer's words
            dropped.append(dict(w, why="quote not in the answer")); continue
        kept.append(w)
    return kept, dropped
