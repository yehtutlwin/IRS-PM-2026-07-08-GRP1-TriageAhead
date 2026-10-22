"""Rule review app: teammates verify the LLM-drafted rulebook against the cited
handbook pages and record verdicts. Local-first, stdlib + sqlite3 + pymupdf.

  python3 review/app.py            -> http://localhost:8091
  python3 review/app.py export     -> <data dir>/out/review-log.jsonl + review-log.csv
  REVIEW_DATA_DIR=<dir>            -> where reviews.db, the page cache and exports live
                                      (default: this folder; a deployment points it outside the checkout)

Pages:  /                 progress + rule table (filters)
        /rule/<id>        the rule, its cited page rendered with the quoted span
                          highlighted, prior reviews, the review form
        /page/<doc>/<n>   rendered PDF page (PNG, cached); ?hl=<text> highlights
        /pdf/<doc>        the PDF itself (opens at #page=N in the browser)
        /export           the review log as JSONL
Decisions: review/adr/*.md.
"""
import csv, difflib, hashlib, html, io, json, os, re, sqlite3, subprocess, sys, time, urllib.parse
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Verdicts, the page cache and exports live in REVIEW_DATA_DIR (ADR 0007) - outside the
# checkout on a deployment, so the served branch can be replaced without touching data.
DATA = os.path.abspath(os.environ.get("REVIEW_DATA_DIR") or HERE)
DB = os.path.join(DATA, "reviews.db")
CACHE = os.path.join(DATA, "cache")
OUT = os.path.join(DATA, "out")
PORT = int(os.environ.get("REVIEW_PORT", "8091"))
RULE_FILES = [("criteria", os.path.join(ROOT, "rules", "criteria.yaml")),
              ("candidates", os.path.join(ROOT, "rules", "criteria-candidates.yaml")),
              ("bridges", os.path.join(ROOT, "rules", "bridges.yaml"))]
FIELDS_FILE = os.path.join(ROOT, "rules", "fields.yaml")   # the history and screening questions come from here (set "history")
TRIGGERS_FILE = os.path.join(ROOT, "rules", "triggers.yaml")   # the triggers (when a question is asked) come from here (set "triggers")
TERMS_FILE = os.path.join(ROOT, "rules", "terms.yaml")         # the fuzzy terms (a word and the number or list assigned to it) (set "terms")
DOCS = {   # citation key -> (file, label); printed page numbers are matched against the PDF by text
    "ESI v5": ("ESI-Handbook-5th-Edition-3-2023.pdf", "ESI Implementation Handbook, 5th ed. (ENA 2023)"),
    "ESI v4": ("ESI-Handbook-v4-2012-AHRQ.pdf", "ESI Implementation Handbook v4 (AHRQ 2012)"),
    "NICE": ("NICE-NG232-main-guideline.pdf", "NICE NG232 Head injury (2023)"),
    "CDC": ("CDC-Field-Triage-2011-MMWR.pdf", "CDC Field Triage Guidelines (MMWR 2012)"),
}
VERDICTS = ["accept", "edit", "reject", "unsure"]
# The fields a verdict is about (ADR 0008). Everything else in an entry - `notes`, ids,
# future implementation flags - can change without invalidating a review.
REVIEWED_FIELDS = ["decision_point", "provenance", "source", "span", "when", "assessed_via", "effect_override",
                   "mapping", "rule", "counts_as_resource", "does_not_count", "target", "value", "kind", "count", "ask", "purpose", "authored", "field", "why", "term", "definition", "numbers", "options"]


# ---------------- rules ----------------
def snapshot_of(r):
    return json.dumps({k: r[k] for k in REVIEWED_FIELDS if k in r}, sort_keys=True, ensure_ascii=False)


def load_rules():
    rules = []
    for setname, path in RULE_FILES:
        if not os.path.exists(path):
            continue
        for r in yaml.safe_load(open(path)) or []:
            if not isinstance(r, dict) or "id" not in r:
                continue
            r = dict(r); r["_set"] = setname
            r["_snapshot"] = snapshot_of(r)
            r["_hash"] = hashlib.sha256(r["_snapshot"].encode()).hexdigest()[:12]
            if setname == "bridges" and r.get("count") and not r.get("when"):   # a count bridge: drawn as "any of" its fields
                r["when"] = {"any": [{"field": f, "equals": True} for f in r["count"]]}
            r["_yaml"] = yaml.safe_dump({k: v for k, v in r.items() if not k.startswith("_")}, sort_keys=False, allow_unicode=True, width=100)
            rules.append(r)
    # the history and screening questions: every field in rules/fields.yaml with a `purpose` (asked for the nurse, not for
    # the level); reviewed like a rule: does the cited page name this item, or is the authored reason sound?
    if os.path.exists(FIELDS_FILE):
        for f, spec in (yaml.safe_load(open(FIELDS_FILE)).get("fields") or {}).items():
            if not isinstance(spec, dict) or not spec.get("purpose"): continue
            r = {"id": f, "purpose": spec["purpose"], "ask": spec.get("ask"), "gloss": spec.get("gloss"), "meaning": spec.get("meaning"), "ask_policy": spec.get("ask_policy"),
                 "provenance": spec.get("provenance") or ("transcribed" if spec.get("source") else "authored")}
            for k in ("source", "span", "authored", "notes", "asked_with"):
                if spec.get(k) is not None: r[k] = spec[k]
            r["_set"] = "history"; r["_snapshot"] = snapshot_of(r)
            r["_hash"] = hashlib.sha256(r["_snapshot"].encode()).hexdigest()[:12]
            r["_yaml"] = yaml.safe_dump({k: v for k, v in r.items() if not k.startswith("_")}, sort_keys=False, allow_unicode=True, width=100)
            rules.append(r)
    # the triggers: the authored condition under which a question is asked (rules/triggers.yaml); drawn like a rule whose
    # outcome is "the question is asked"; reviewed for plausibility (widen, narrow, strike)
    if os.path.exists(TRIGGERS_FILE):
        fields = (yaml.safe_load(open(FIELDS_FILE)).get("fields") or {}) if os.path.exists(FIELDS_FILE) else {}
        for t in yaml.safe_load(open(TRIGGERS_FILE)) or []:
            if not isinstance(t, dict) or not t.get("field"): continue
            spec = fields.get(t["field"], {})
            r = {"id": "trigger:" + t["field"], "field": t["field"], "when": t.get("trigger"), "why": t.get("why"), "provenance": "authored",
                 "ask": spec.get("ask"), "gloss": spec.get("gloss"), "meaning": spec.get("meaning"), "ask_policy": spec.get("ask_policy"), "feeds": spec.get("feeds")}
            r["_set"] = "triggers"; r["_snapshot"] = snapshot_of(r)
            r["_hash"] = hashlib.sha256(r["_snapshot"].encode()).hexdigest()[:12]
            r["_yaml"] = yaml.safe_dump({k: v for k, v in r.items() if not k.startswith("_")}, sort_keys=False, allow_unicode=True, width=100)
            rules.append(r)
    # the fuzzy terms: a word the handbook or the interview uses without a number or list, and the number, band or list the
    # system assigns to it; reviewed for the line drawn (move it, widen or shorten a list)
    if os.path.exists(TERMS_FILE):
        for t in yaml.safe_load(open(TERMS_FILE)) or []:
            if not isinstance(t, dict) or not t.get("id"): continue
            r = dict(t); r["id"] = "term:" + t["id"]
            r["_set"] = "terms"; r["_snapshot"] = snapshot_of(r)
            r["_hash"] = hashlib.sha256(r["_snapshot"].encode()).hexdigest()[:12]
            r["_yaml"] = yaml.safe_dump({k: v for k, v in r.items() if not k.startswith("_")}, sort_keys=False, allow_unicode=True, width=100)
            rules.append(r)
    return rules


def question_serves(r):
    """The rules a triggered question serves: those that read the field, plus those that read what it feeds through a bridge."""
    ids = list(rules_reading(r.get("field")))
    for t in [x.strip() for x in str(r.get("feeds") or "").split(",") if x.strip()]:
        ids += [x for x in rules_reading(t) if x not in ids]
    return ids


_commit_cache = {"t": 0, "v": ""}


def rules_commit():
    """The checkout's HEAD (short) that the served rulebook comes from, '-dirty' if the
    rule files have uncommitted edits, '' outside git. Cached for a few seconds."""
    if time.time() - _commit_cache["t"] < 5:
        return _commit_cache["v"]
    try:
        head = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--"] + [p for _, p in RULE_FILES] + [FIELDS_FILE, TRIGGERS_FILE, TERMS_FILE],
                               capture_output=True, text=True, timeout=5).stdout.strip()
        v = head + ("-dirty" if dirty else "") if head else ""
    except Exception:
        v = ""
    _commit_cache.update(t=time.time(), v=v)
    return v


# ---------------- what a rule does, and where its facts come from ----------------
def _label_dict():
    """Plain label for each field id: its `gloss` in rules/fields.yaml (the one-line definition written for the
    answer-to-facts step); the inspector's short labels fill any gap."""
    out = {}
    try:
        sys.path.insert(0, os.path.join(ROOT, "prototype"))
        import inspector
        out.update(inspector.LABEL)
    except Exception:
        pass
    try:
        for f, spec in (yaml.safe_load(open(os.path.join(ROOT, "rules", "fields.yaml"))) or {}).get("fields", {}).items():
            out[f] = str(spec.get("gloss") or spec.get("meaning", ""))
    except Exception:
        pass
    return out


LABEL = _label_dict()
ASSESSED = {"reported": "the caregiver can report it in the chat",
            "observed": "a finding the nurse sees at triage - never asked in the chat",
            "vitals": "a measured vital sign - not available before arrival"}
# Fields the engine derives itself (prototype/engine.py derive()); kept by hand.
DERIVED = {"patient.age": "stated by the caregiver, or derived from identity.dob",
           "M.anticoagulant": "confirmed from a named medicine in M.medications or the confirmation answer; probable from a description",
           "E.mechanism": "asked with the complaint; set to 'none' for a non-injury complaint"}


DP_MEANING = {"A": "decision point A - requires immediate life-saving intervention: <b>ESI-1</b>",
              "B": "decision point B - high-risk situation / should not wait: <b>ESI-2</b>",
              "C": "decision point C - expected resources (ESI-3 / 4 / 5)",
              "D": "decision point D - danger-zone vital signs (consider up-triage to ESI-2)"}
VERB_MEANING = {
    "context_note": "the book gives this as background for reading other findings; it assigns no level and asks for no consideration (a context note on the report)",None: "the book <b>assigns</b> the level (verbs like 'meets criteria', 'is ESI-2')",
                "consider": "the book only says <b>consider</b> - the rule must not assign",
                "reassess_uptriage_consider": "the book says <b>reassess / consider up-triage</b> - a prompt, not an assignment"}


def claim_text(r):
    """What the entry asserts the book prescribes - the part a reviewer checks against the page.
    Implied by decision_point + effect_override, never written out in the YAML."""
    if r["_set"] == "terms" and r.get("kind") == "option":
        return (f'the option <code>{E(str(r.get("value")))}</code> of the choice field <code>{E(str(r.get("field")))}</code> means: {E(str(r.get("definition")))}. '
                f'Fact extraction is given this definition with the value. Check: is the option rightly drawn and rightly defined, and is the list of options of this field complete?')
    if r["_set"] == "terms":
        users = ", ".join(f'<code>{E(u)}</code>' for u in (r.get("used_by") or [])) or "nothing yet"
        nums = f' Numbers or lists the programs read: <code>{E(json.dumps(r.get("numbers"), ensure_ascii=False))}</code>.' if r.get("numbers") else " No number assigned."
        return (f'the fuzzy term <b>{E(str(r.get("term")))}</b> means: {E(str(r.get("definition")))}.{nums} Used by {users}. '
                f'Check: is the line drawn where the cited page, or the reason, puts it? Say where to move it.')
    if r["_set"] == "triggers":
        serves = ", ".join(f'<a href="/rule/{urllib.parse.quote(x)}">{E(x)}</a>' for x in question_serves(r)) or "no rule (asked for the nurse)"
        return (f'the question <code>{E(str(r.get("field")))}</code> (&ldquo;{E(str(r.get("ask") or ""))}&rdquo;) is asked when this condition holds; it serves {serves}. '
                f'<b>Authored</b> by plausibility, no source. Check: is the question worth asking in these situations, and in no others? '
                f'Say where to widen or narrow it.')
    if r["_set"] == "history":
        readers = rules_reading(r["id"])
        rd = (" Read by " + ", ".join(f'<a href="/rule/{urllib.parse.quote(x)}">{E(x)}</a>' for x in readers) + ".") if readers else " No rule reads it."
        if r.get("source"):
            return (f'a question the interview asks for the nurse, not for the level: <b>{E(str(r.get("purpose")))}</b>.{rd} '
                    f'Check: does the cited source name this item, and is the wording right for a caregiver?')
        return (f'a question the interview asks for the nurse, not for the level: <b>{E(str(r.get("purpose")))}</b>.{rd} '
                f'<b>Authored</b>, no outside source. Check: is the reason given sound, and is the wording right for a caregiver?')
    if r["_set"] == "bridges":
        rules = ", ".join(f'<a href="/rule/{urllib.parse.quote(x)}">{E(x)}</a>' for x in rules_reading(r.get("target"))) or "no rule"
        kind = r.get("kind")
        if kind == "count":
            return (f'the number of these everyday signs that are true is written as <code>{E(str(r.get("target")))}</code>, read by {rules}. '
                    f'Check: are these the findings the cited page counts?')
        if kind == "entails":
            return (f'one of our own facts implies another: when the condition holds, <code>{E(str(r.get("target")))}</code> = '
                    f'<code>{E(json.dumps(r.get("value", True)))}</code>, read by {rules}. No outside source: check the two meanings in rules/fields.yaml against the reason given.')
        return (f'everyday signs a caregiver can report translate to the book\'s term <code>{E(str(r.get("target")))}</code> = '
                f'<code>{E(json.dumps(r.get("value", True)))}</code>, read by {rules}. Check: is that translation what the cited page supports?')
    if "when" not in r:
        return f'{DP_MEANING.get(str(r.get("decision_point")), "")} - a definition / counting policy, no level of its own.'
    eo = r.get("effect_override")
    return f'{DP_MEANING.get(str(r.get("decision_point")), "unknown decision point")}; {VERB_MEANING.get(eo, E(str(eo)))}.'


def short_effect(r):
    """One-word effect for the index table."""
    if r["_set"] == "bridges": return "bridge"
    if r["_set"] == "history": return "question"
    if r["_set"] == "triggers": return "trigger"
    if r["_set"] == "terms": return "option" if r.get("kind") == "option" else "fuzzy term"
    if "when" not in r: return "definition"
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "consider": return "consider"
    if eo == "context_note": return "context note"
    if eo == "reassess_uptriage_consider": return "reassess"
    return {"A": "ESI-1", "B": "≥ ESI-2"}.get(dp, f"DP {dp}")


def engine_text(r):
    """What the prototype does when the rule fires (mirrors prototype/engine.py evaluate_tree)."""
    if r["_set"] == "terms":
        return "the engine reads the age bands and the blood-thinner names from the term; rules and triggers carry its numbers in their conditions (the validator keeps them equal); the fact-extraction glosses repeat its definition."
    if r["_set"] == "triggers":
        return "when the condition holds on the facts so far, the question joins the open questions the interview may ask next; it is never asked otherwise (a volunteered answer is still written)."
    if r["_set"] == "history":
        return f'asked in the interview ({E(str(r.get("ask_policy") or "when applicable"))}); stored and shown in the nurse\'s report; no floor of its own.'
    if r["_set"] == "bridges":
        if r.get("kind") == "count": return "writes the count of true signs as the target fact, updating it as answers arrive; no floor of its own."
        return "writes the target fact once, unless the caregiver already stated it; no floor of its own."
    if "when" not in r:
        return "nothing fires."
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "consider":
        return "shown to the nurse as a CONSIDER flag; the floor does not change."
    if eo == "context_note":
        return "shown to the nurse under CONTEXT NOTES (background for reading other findings); neither a flag nor a floor."
    if eo == "reassess_uptriage_consider":
        return ("<span style=\"color:#b07a00\">the engine currently treats it like a floor rule (fires &rarr; 'at least ESI-2') - "
                "stronger than the book's verb; inert pre-arrival since vitals are unavailable. Engine issue, not a fault of this entry.</span>")
    if dp == "A":
        return "ESI-1 indicator: the caregiver gets the one permitted advice (call 995) once; listed at the top of the nurse report. ESI-1 itself is the nurse's call."
    if dp == "B":
        return "floor becomes 'at least ESI-2'; the report shows the rule, its source and the quoted span."
    return f"fires &rarr; floor 'at least ESI-2' (engine default for decision point {E(str(dp))})."


def when_fields(c, out=None):
    out = [] if out is None else out
    if isinstance(c, dict):
        if "all" in c or "any" in c:
            for x in c.get("all", []) + c.get("any", []): when_fields(x, out)
        elif c.get("field") and c["field"] not in out:
            out.append(c["field"])
    return out


def rules_reading(target):
    """The rules whose condition reads this field (a bridge's target)."""
    if not target: return []
    return [r["id"] for r in load_rules() if r["_set"] == "criteria" and r.get("when")
            and target in [re.sub(r"\.(value|status)$", "", f) for f in when_fields(r["when"])]]


_reach_cache = {}


def reach_map():
    """field -> (how, detail): where a fact can come from - the interview (rules/derived/agenda.yaml, derived from the
    rules and rules/fields.yaml), a bridge, a derivation - or nowhere (a finding or measurement only a clinician gives)."""
    if _reach_cache:
        return _reach_cache
    m = {}
    try:
        agenda = (yaml.safe_load(open(os.path.join(ROOT, "rules", "derived", "agenda.yaml"))) or {}).get("fields", {})
        for f, e in agenda.items():
            pol = e.get("ask_policy")
            ask = E(str(e.get("ask", ""))[:110])
            if pol == "always":
                m[f] = ("asked", f'asked of every patient: &ldquo;{ask}&rdquo;')
            elif pol == "when_applicable":
                gate = "when its trigger holds (authored, rules/triggers.yaml)" if e.get("trigger") is not None else "when a rule that reads it is still possible"
                m[f] = ("asked", f'asked {gate}: &ldquo;{ask}&rdquo;')
            elif pol == "volunteered_only":
                m[f] = ("extractable", "never asked unprompted; the extraction step writes it when the caregiver volunteers it")
    except Exception:
        pass
    for f, d in DERIVED.items():
        m.setdefault(f, ("derived", d))
    for b in load_rules():
        if b["_set"] == "bridges" and b.get("target"):
            src = ", ".join(f"<code>{E(x)}</code>" for x in when_fields(b.get("when")))
            m.setdefault(b["target"], ("bridged", f'derived by bridge <a href="/rule/{urllib.parse.quote(b["id"])}">{E(b["id"])}</a> from {src}'))
    _reach_cache.update(m)
    return m


def fields_table(r):
    fields = when_fields(r.get("when"))
    if not fields:
        return ""
    reach = reach_map(); rows = []
    for f in fields:
        how, detail = reach.get(f, ("none", "<span style=\"color:#b3261e\">not produced by the interview</span> - nurse-observed or entered at triage only"))
        gloss = LABEL.get(f)
        rows.append(f'<tr><td><code>{E(f)}</code></td><td>{E(gloss) if gloss else "<span class=muted>no gloss yet</span>"}</td><td class="muted">{detail}</td></tr>')
    return ('<p><b>Facts in this condition</b> <span class="muted">- ids are the engine\'s controlled vocabulary (rules/criteria.schema.json); '
            'each is defined once in rules/fields.yaml; the extraction step writes them from the caregiver\'s words and bridges translate everyday signs</span></p>'
            f'<table><tr><th>field</th><th>meaning (rules/fields.yaml)</th><th>where it can come from</th></tr>{"".join(rows)}</table>')


# ---------------- diagram: facts -> gates -> rule -> impact -> what each audience sees ----------------
ROW, LEAF_W, GATE_W, GATE_STEP = 44, 340, 64, 118
REACH_STYLE = {"asked": ("#1b7f3b", "asked in the chat"), "extractable": ("#1b7f3b", "chat, if volunteered"),
               "bridged": ("#1a4a7a", "via a bridge"), "derived": ("#1a4a7a", "derived"), "none": ("#8a8f98", "nurse only")}


def _op_text(c):
    for k, sym in (("equals", "="), ("in", "in"), ("gte", "≥"), ("gt", ">"), ("lte", "≤"), ("lt", "<")):
        if k in c:
            v = c[k]
            if v is True: return "= yes"
            if v is False: return "= no"
            if isinstance(v, list): return f"{sym} {', '.join(str(x) for x in v)}"
            return f"{sym} {v}"
    return "?"


def _tree(c):
    if isinstance(c, dict) and ("all" in c or "any" in c):
        kind = "all" if "all" in c else "any"
        return {"kind": kind, "children": [_tree(x) for x in c[kind]]}
    return {"kind": "leaf", "field": str(c.get("field", "?")) if isinstance(c, dict) else str(c), "op": _op_text(c) if isinstance(c, dict) else ""}


def _layout(n, row=0):
    """Leaves take one row each; a gate sits at its children's mean y, one column right of the deepest child."""
    if n["kind"] == "leaf":
        n["depth"], n["y"] = 0, row * ROW + ROW / 2
        return row + 1
    for ch in n["children"]:
        row = _layout(ch, row)
    n["depth"] = max(ch["depth"] for ch in n["children"]) + 1
    n["y"] = sum(ch["y"] for ch in n["children"]) / len(n["children"])
    return row


def _x(depth):
    return 0 if depth == 0 else LEAF_W + 40 + (depth - 1) * GATE_STEP


def _clip(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def outcomes(r):
    """(impact label, colour, caregiver sees, nurse report shows) for the right-hand side."""
    if r["_set"] == "terms":
        return ("a line is drawn", "#555", "nothing said", "the rules and derivations that use the term")
    if r["_set"] == "triggers":
        return ("question is asked", "#1a4a7a", f'asked: {r.get("ask")}', "nothing of its own; the answer feeds the rules it serves")
    if r["_set"] == "history":
        return ("question for the nurse", "#555", f'asked: {r.get("ask")}', "shown in the report's history section")
    if r["_set"] == "bridges":
        return ("writes the book's term", "#1a4a7a", "nothing said", f'feeds {", ".join(rules_reading(r.get("target"))) or "no rule"}')
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "consider":
        return ("CONSIDER flag", "#b07a00", "nothing said (never reassure)", "CONSIDER flag with citation; floor unchanged")
    if eo == "context_note":
        return ("context note", "#555", "nothing said", "a context note with the quote; neither flag nor floor")
    if eo == "reassess_uptriage_consider":
        return ("reassess / consider", "#1a4a7a", "nothing (vitals unavailable pre-arrival)", "engine: floor 'at least ESI-2' (stronger than the book)")
    if dp == "A":
        return ("ESI-1 indicator", "#b3261e", "bot says: call 995 now (once)", "top banner: possible ESI-1 indicator + citation")
    if dp == "B":
        return ("floor: at least ESI-2", "#c2410c", "nothing said (never reassure)", "floor 'at least ESI-2' + rule, source, quote")
    return (f"fires (DP {dp})", "#c2410c", "nothing said", "floor 'at least ESI-2' (engine default)")


def svg_rule(r):
    """Inline SVG: leaf facts (coloured by where they can come from) -> ALL/ANY gates -> rule ->
    impact -> the two audiences. Pure server-side layout; no script."""
    if "when" not in r:
        return ""
    t = _tree(r["when"]); rows = _layout(t); reach = reach_map()
    leaves, gates, edges = [], [], []

    def walk(n, parent=None):
        if parent is not None:
            x1 = (_x(n["depth"]) + (LEAF_W if n["depth"] == 0 else GATE_W)); x2 = _x(parent["depth"]); xm = (x1 + x2) / 2
            edges.append(f'<path d="M{x1:.0f},{n["y"]:.0f} H{xm:.0f} V{parent["y"]:.0f} H{x2:.0f}" fill="none" stroke="#9aa5b5" stroke-width="1.5"/>')
        if n["kind"] == "leaf":
            base = re.sub(r"\.(value|status)$", "", n["field"])   # conditions may read a record's .value / .status
            how = reach.get(base, ("none", ""))[0]; col, tag = REACH_STYLE[how]
            gloss = LABEL.get(n["field"]) or LABEL.get(base, n["field"])
            if n["field"].endswith(".status"): gloss += " (status)"
            leaves.append(f'<g><title>{E(n["field"])} {E(n["op"])} - {E(tag)}</title>'
                          f'<rect x="0" y="{n["y"] - 17:.0f}" width="{LEAF_W}" height="34" rx="6" fill="#fff" stroke="{col}" stroke-width="{2 if how != "none" else 1.2}"{" stroke-dasharray=\"4,3\"" if how == "extractable" else ""}/>'
                          f'<text x="10" y="{n["y"] - 3:.0f}" font-size="12" fill="#1a2b45">{E(_clip(f"{gloss} {n['op']}", 50))}</text>'
                          f'<text x="10" y="{n["y"] + 11:.0f}" font-size="10" fill="{col}">{E(tag)} · {E(_clip(n["field"], 34))}</text></g>')
        else:
            x = _x(n["depth"])
            gates.append(f'<rect x="{x}" y="{n["y"] - 14:.0f}" width="{GATE_W}" height="28" rx="14" fill="#eef2f8" stroke="#6b7a90"/>'
                         f'<text x="{x + GATE_W / 2:.0f}" y="{n["y"] + 4:.0f}" font-size="12" font-weight="700" text-anchor="middle" fill="#1a2b45">{"ALL of" if n["kind"] == "all" else "ANY of"}</text>')
            for ch in n["children"]:
                walk(ch, n)
    walk(t)
    height = max(rows * ROW, 3 * ROW)
    yc = t["y"]
    rx = _x(t["depth"]) + (LEAF_W if t["depth"] == 0 else GATE_W) + 36           # rule node
    label, col, care, nurse = outcomes(r)
    ex = rx + 176                                                                 # impact node
    ox = ex + 206                                                                 # outcomes
    oy1, oy2 = min(yc - 26, height - ROW - 4), min(yc + 26, height - 4)
    if rows < 3: oy1, oy2 = ROW * 0.6 + 4, ROW * 1.9 + 4
    parts = edges + gates + leaves
    parts.append(f'<path d="M{rx - 36},{yc:.0f} H{rx}" stroke="#9aa5b5" stroke-width="1.5" marker-end="url(#arr)"/>')
    parts.append(f'<rect x="{rx}" y="{yc - 18:.0f}" width="160" height="36" rx="6" fill="#1a2b45"/>'
                 f'<text x="{rx + 80}" y="{yc - 3:.0f}" font-size="11" text-anchor="middle" fill="#fff">{"question is asked" if r["_set"] == "triggers" else "rule fires"}</text>'
                 f'<text x="{rx + 80}" y="{yc + 11:.0f}" font-size="11" font-weight="700" text-anchor="middle" fill="#fff">{E(_clip(r["id"], 26))}</text>')
    parts.append(f'<path d="M{rx + 160},{yc:.0f} H{ex}" stroke="#9aa5b5" stroke-width="1.5" marker-end="url(#arr)"/>')
    sub = f'{r.get("target")} = {json.dumps(r.get("value", True))}' if r["_set"] == "bridges" else ""
    parts.append(f'<g><title>{E(label)}{(" - " + E(sub)) if sub else ""}</title><rect x="{ex}" y="{yc - 18:.0f}" width="190" height="36" rx="6" fill="{col}"/>'
                 f'<text x="{ex + 95}" y="{yc + (-1 if sub else 4):.0f}" font-size="12" font-weight="700" text-anchor="middle" fill="#fff">{E(label)}</text>'
                 + (f'<text x="{ex + 95}" y="{yc + 12:.0f}" font-size="9.5" text-anchor="middle" fill="#fff">{E(_clip(sub, 34))}</text>' if sub else "") + '</g>')
    for oy, who, what in ((oy1, "caregiver in the chat", care), (oy2, "nurse report", nurse)):
        parts.append(f'<path d="M{ex + 190},{yc:.0f} H{ex + 198} V{oy:.0f} H{ox}" fill="none" stroke="#9aa5b5" stroke-width="1.5" marker-end="url(#arr)"/>')
        parts.append(f'<g><title>{E(what)}</title><rect x="{ox}" y="{oy - 17:.0f}" width="370" height="34" rx="6" fill="#fff" stroke="{col}"/>'
                     f'<text x="{ox + 10}" y="{oy - 3:.0f}" font-size="10" fill="#5a6a82">{E(who)}</text>'
                     f'<text x="{ox + 10}" y="{oy + 11:.0f}" font-size="12" fill="#1a2b45">{E(_clip(what, 56))}</text></g>')
    width = ox + 380
    legend = ('<p class="muted" style="margin:6px 0 0">Fact boxes: <span style="color:#1b7f3b">green = the chat can produce it</span> (dashed: only if volunteered) &middot; '
              '<span style="color:#1a4a7a">blue = derived / via a bridge</span> &middot; <span style="color:#8a8f98">grey = nurse-only, never from the chat</span>. '
              'Hover a box for the full text.</p>')
    return (f'<div style="overflow-x:auto"><svg viewBox="0 0 {width} {height + 8}" width="{width}" height="{height + 8}" font-family="system-ui,sans-serif" style="max-width:100%;height:auto">'
            f'<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#9aa5b5"/></marker></defs>'
            f'<g transform="translate(4,4)">{"".join(parts)}</g></svg></div>{legend}')


def snapshot_diff(old, new):
    """Unified diff of two snapshots (JSON strings), rendered as YAML for reading."""
    def lines(s):
        try: return yaml.safe_dump(json.loads(s), sort_keys=True, allow_unicode=True, width=100).splitlines()
        except Exception: return [str(s)]
    return "\n".join(difflib.unified_diff(lines(old or ""), lines(new or ""), "reviewed", "current", lineterm="", n=2))


def source_lines(source):
    """A source may be one string or a list of strings (dual citations)."""
    return [str(x) for x in source] if isinstance(source, list) else [str(source or "")]


def citations(source):
    """Each source line -> (doc_key, [printed pages], line). Lines naming a document
    without a page number are kept (page located by text search later)."""
    out = []
    for src in source_lines(source):
        for key in DOCS:
            if key in src or (key == "NICE" and "NG232" in src) or (key == "CDC" and ("MMWR" in src or "Field Triage" in src)):
                pages = sorted({int(p) for p in re.findall(r"p\.\s*(\d+)", src)})
                out.append((key, pages, src))
    return out


def is_quotation(span):
    """The span field should be a quote from the page; drafters sometimes left a note."""
    t = str(span or "").strip()
    return bool(t) and not t.startswith("(") and "to be verified" not in t.lower() and "not stated" not in t.lower()


def locate_by_text(doc_key, probes):
    """No page number in the citation: search the whole PDF for the quoted span, then for a
    recommendation / step id mentioned in the citation ('1.5.9', 'Step Four'). Returns
    (pdf index, what matched) or (None, None)."""
    import pymupdf
    path = pdf_path(doc_key)
    if not path or not os.path.exists(path):
        return None, None
    d = pymupdf.open(path)
    for probe in [p for p in probes if p and len(p.strip()) >= 4]:
        for i in range(len(d)):
            if d[i].search_for(probe):
                return i, probe
    return None, None


# ---------------- handbook rendering ----------------
def pdf_path(doc_key):
    f = DOCS.get(doc_key)
    return os.path.join(ROOT, "sources", f[0]) if f else None


_page_maps = {}


def page_map(doc_key):
    """printed page number -> PDF index, read from the number printed on each page
    (first/last short lines). Cached per document; front matter is thus handled."""
    import pymupdf
    if doc_key in _page_maps:
        return _page_maps[doc_key]
    d = pymupdf.open(pdf_path(doc_key)); m = {}
    last = 0   # printed numbers must increase with the PDF index; stray digits are rejected
    for i in range(1, len(d)):   # index 0 is the cover - never a numbered page
        lines = [l.strip() for l in d[i].get_text().splitlines() if l.strip()]
        for l in lines[:3] + lines[-4:]:
            if re.fullmatch(r"\d{1,3}", l) and last < int(l) <= last + 3 and int(l) not in m:
                m[int(l)] = i; last = int(l); break
    _page_maps[doc_key] = m
    return m


def _probes(span):
    t = re.sub(r"\s+", " ", str(span or "")).strip().strip("\"'\u201c\u201d")
    if not t:
        return []
    out = [t[:70], t[:45]]
    first = re.split(r"[.;:]", t)[0].strip()
    if len(first) > 12: out.append(first[:70])
    words = t.split(" ")
    if len(words) > 6: out.append(" ".join(words[:6]))
    return [p for p in dict.fromkeys(out) if len(p) >= 8]


def locate(doc_key, printed_page, span):
    """Where to show the citation. Returns (pdf_index, how, printed_no_on_that_page):
    how = 'span' (quoted text found - authoritative), 'pagemap' (the printed page
    number, span not found on it), or 'guess' (nothing verified)."""
    import pymupdf
    path = pdf_path(doc_key)
    if not path or not os.path.exists(path):
        return None, None, None
    d = pymupdf.open(path); pm = page_map(doc_key); inv = {v: k for k, v in pm.items()}
    expected = pm.get(printed_page)
    for probe in _probes(span):
        hits = [i for i in range(len(d)) if d[i].search_for(probe)]
        if hits:
            i = min(hits, key=lambda x: abs(x - expected) if expected is not None else x)
            return i, "span", inv.get(i)
    if expected is not None:
        return expected, "pagemap", printed_page
    g = max(0, min((printed_page or 1) - 1, len(d) - 1))
    return g, "guess", inv.get(g)


def page_is_blank(doc_key, index):
    import pymupdf
    return len(pymupdf.open(pdf_path(doc_key))[index].get_text().strip()) < 40


def render_page(doc_key, index, highlight):
    import pymupdf
    key = hashlib.sha256(f"{doc_key}|{index}|{highlight}".encode()).hexdigest()[:16]
    out = os.path.join(CACHE, key + ".png")
    if os.path.exists(out):
        return open(out, "rb").read()
    d = pymupdf.open(pdf_path(doc_key)); p = d[index]
    if highlight:
        for probe in _probes(highlight):
            rects = p.search_for(probe)
            if rects:
                for r in rects: p.add_highlight_annot(r)
                break
    png = p.get_pixmap(dpi=110).tobytes("png")
    os.makedirs(CACHE, exist_ok=True); open(out, "wb").write(png)
    return png


# ---------------- Cloudflare Access identity (optional; ADR 0006) ----------------
# When the app is published through a Cloudflare Tunnel behind Access, every request
# carries Cf-Access-Jwt-Assertion. With CF_ACCESS_TEAM (the <team> in
# <team>.cloudflareaccess.com) and CF_ACCESS_AUD (the application's audience tag) set,
# the token is verified against the team's public keys and its email becomes the
# reviewer identity. Unset -> self-declared names as before (local use).
CF_TEAM = os.environ.get("CF_ACCESS_TEAM", "").strip()
CF_AUD = os.environ.get("CF_ACCESS_AUD", "").strip()
_jwks_cache = {"t": 0, "keys": {}}


def _b64url(s):
    import base64
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _jwks():
    import urllib.request
    if time.time() - _jwks_cache["t"] > 3600 or not _jwks_cache["keys"]:
        data = json.loads(urllib.request.urlopen(f"https://{CF_TEAM}.cloudflareaccess.com/cdn-cgi/access/certs", timeout=10).read())
        _jwks_cache.update(t=time.time(), keys={k["kid"]: k for k in data.get("keys", []) if k.get("kty") == "RSA"})
    return _jwks_cache["keys"]


def access_identity(headers):
    """Verified email from the Access JWT, or None. Fails closed: any problem -> None."""
    if not (CF_TEAM and CF_AUD):
        return None
    tok = headers.get("Cf-Access-Jwt-Assertion")
    if not tok:
        return None
    try:
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        from cryptography.hazmat.primitives import hashes
        h64, p64, s64 = tok.split(".")
        hdr, payload = json.loads(_b64url(h64)), json.loads(_b64url(p64))
        if hdr.get("alg") != "RS256":
            return None
        k = _jwks().get(hdr.get("kid"))
        if not k:
            _jwks_cache["t"] = 0; k = _jwks().get(hdr.get("kid"))
            if not k: return None
        n = int.from_bytes(_b64url(k["n"]), "big"); e = int.from_bytes(_b64url(k["e"]), "big")
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        pub.verify(_b64url(s64), f"{h64}.{p64}".encode(), padding.PKCS1v15(), hashes.SHA256())
        aud = payload.get("aud"); aud = aud if isinstance(aud, list) else [aud]
        if CF_AUD not in aud or payload.get("exp", 0) < time.time():
            return None
        if payload.get("iss") != f"https://{CF_TEAM}.cloudflareaccess.com":
            return None
        return (payload.get("email") or "").strip().lower() or None
    except Exception:
        return None


# ---------------- storage ----------------
def db():
    os.makedirs(DATA, exist_ok=True)
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, rule_id TEXT NOT NULL, rule_set TEXT, rule_hash TEXT,
        reviewer TEXT NOT NULL, verdict TEXT NOT NULL, page_checked INTEGER DEFAULT 0,
        comment TEXT, suggested_change TEXT, created_at TEXT NOT NULL,
        rule_snapshot TEXT, rule_commit TEXT)""")
    have = {r["name"] for r in c.execute("PRAGMA table_info(reviews)")}
    for col in ("rule_snapshot", "rule_commit"):   # databases created before ADR 0008
        if col not in have:
            c.execute(f"ALTER TABLE reviews ADD COLUMN {col} TEXT")
    c.execute("CREATE INDEX IF NOT EXISTS ix_rule ON reviews(rule_id, created_at)")
    return c


def reviews_for(rule_id):
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reviews WHERE rule_id=? ORDER BY created_at DESC", (rule_id,))]


def latest_by_reviewer(rule_id):
    seen, out = set(), []
    for r in reviews_for(rule_id):
        if r["reviewer"] not in seen:
            seen.add(r["reviewer"]); out.append(r)
    return out


def add_review(d):
    with db() as c:
        c.execute("INSERT INTO reviews (rule_id, rule_set, rule_hash, reviewer, verdict, page_checked, comment, suggested_change, created_at, rule_snapshot, rule_commit) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                  (d["rule_id"], d.get("rule_set"), d.get("rule_hash"), d["reviewer"].strip()[:60], d["verdict"],
                   1 if d.get("page_checked") else 0, (d.get("comment") or "").strip()[:4000],
                   (d.get("suggested_change") or "").strip()[:8000], time.strftime("%Y-%m-%d %H:%M:%S"),
                   d.get("rule_snapshot"), d.get("rule_commit")))


def case_verdicts_by_case():
    with db() as c:
        rows = [dict(r) for r in c.execute("SELECT * FROM reviews WHERE rule_set='case' ORDER BY created_at DESC")]
    out = {}
    for r in rows:
        out.setdefault(r["rule_id"], []).append(r)
    return out


def next_unreviewed_case(after_id, reviewer):
    ids = list(case_review.load_cases()); start = ids.index(after_id) + 1 if after_id in ids else 0
    with db() as c:
        done = {r["rule_id"] for r in c.execute("SELECT DISTINCT rule_id FROM reviews WHERE rule_set='case' AND reviewer=?", (reviewer,))}
    for cid in ids[start:] + ids[:start]:
        if cid not in done and cid != after_id:
            return cid
    return None


def next_unreviewed(rules, after_id, reviewer):
    """The next rule (in file order, wrapping) this reviewer has not reviewed yet."""
    ids = list(rules); start = ids.index(after_id) + 1 if after_id in ids else 0
    with db() as c:
        done = {r["rule_id"] for r in c.execute("SELECT DISTINCT rule_id FROM reviews WHERE reviewer=?", (reviewer,))}
    for rid in ids[start:] + ids[:start]:
        if rid not in done and rid != after_id:
            return rid
    return None


def export(fmt_dir=None):
    fmt_dir = fmt_dir or OUT
    os.makedirs(fmt_dir, exist_ok=True)
    with db() as c:
        rows = [dict(r) for r in c.execute("SELECT * FROM reviews ORDER BY created_at")]
    with open(os.path.join(fmt_dir, "review-log.jsonl"), "w") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(fmt_dir, "review-log.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["rule_id"]); w.writeheader(); w.writerows(rows)
    return len(rows)


# ---------------- HTML ----------------
E = html.escape
sys.path.insert(0, HERE); import cases as case_review  # noqa: E402  (practice-case review, issue #68)
case_review.E = E
CSS = """
:root{--ink:#1a2b45;--muted:#5a6a82;--ok:#1b7f3b;--warn:#b07a00;--bad:#b3261e;--line:#dbe2ec}
body{font-family:system-ui,sans-serif;margin:0;background:#f4f6f9;color:var(--ink)}
.wrap{max-width:1280px;margin:0 auto;padding:14px 18px}
header{display:flex;gap:16px;align-items:baseline;border-bottom:1px solid var(--line);padding:10px 0;margin-bottom:12px}
header a{color:var(--ink);text-decoration:none;font-weight:700} .muted{color:var(--muted);font-size:13px}
.card{background:#fff;border-radius:10px;padding:14px 16px;margin:10px 0;box-shadow:0 1px 4px rgba(0,0,0,.08)}
table{width:100%;border-collapse:collapse} td,th{padding:6px 8px;border-top:1px solid #eef1f6;text-align:left;font-size:14px;vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase}
.chip{display:inline-block;border-radius:10px;padding:1px 8px;font-size:11px;color:#fff;background:var(--muted);white-space:nowrap}
.chip.accept{background:var(--ok)} .chip.edit{background:var(--warn)} .chip.reject{background:var(--bad)} .chip.unsure{background:#6c5ce7}
.chip.verbatim{background:#1b7f3b}.chip.transcribed{background:#1b7f3b}.chip.authored{background:#555}.chip.logical{background:#1a4a7a}.chip.operationalized{background:#b07a00}.chip.supplemented{background:#6c5ce7}.chip.stale{background:#b3261e}
pre{background:#f7f9fc;border:1px solid var(--line);border-radius:8px;padding:10px;font:12.5px/1.45 ui-monospace,monospace;white-space:pre-wrap;overflow-x:auto}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px} @media(max-width:900px){.two{grid-template-columns:1fr}}
.page img{width:100%;border:1px solid var(--line);border-radius:6px;background:#fff}
.btn{background:#3e8e4f;color:#fff;border:0;border-radius:8px;padding:9px 14px;font-size:14px;cursor:pointer} .btn.gray{background:var(--muted)}
input[type=text],textarea,select{width:100%;font:14px system-ui;padding:8px;border:1px solid #c6d0de;border-radius:8px;box-sizing:border-box}
textarea{min-height:90px} label{font-size:13px;color:var(--muted);display:block;margin:8px 0 3px}
.radio label{display:inline-block;margin-right:14px;color:var(--ink)} .span{border-left:4px solid #3e8e4f;padding:6px 10px;background:#f2f8f3;border-radius:0 8px 8px 0}
.prog{height:10px;background:#e6ebf3;border-radius:5px;overflow:hidden;display:flex} .prog div{height:100%}
.filters a{margin-right:10px;font-size:13px}
"""

def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><style>{CSS}</style></head><body><div class="wrap">
<header><a href="/">Rulebook review</a><a href="/?set=bridges" style="font-weight:500">Bridges</a><a href="/?set=history" style="font-weight:500">History questions</a><a href="/?set=triggers" style="font-weight:500">Triggers</a><a href="/?set=terms" style="font-weight:500">Terms and options</a><a href="/cases" style="font-weight:500">Practice cases</a><span class="muted">verify each LLM-drafted rule, and each transcribed practice case, against the cited page; verdicts are kept locally</span>
<span style="margin-left:auto" class="muted" id="who"></span></header>{body}
<script>const who=localStorage.getItem('reviewer')||'';document.getElementById('who').textContent=who?('reviewing as '+who):'no reviewer name yet';</script>
</div></body></html>"""


def cond_text(c, depth=0):
    pad = "  " * depth
    if not isinstance(c, dict): return pad + str(c)
    if "all" in c: return pad + "ALL of:\n" + "\n".join(cond_text(x, depth + 1) for x in c["all"])
    if "any" in c: return pad + "ANY of:\n" + "\n".join(cond_text(x, depth + 1) for x in c["any"])
    f = c.get("field", "?"); op = next((k for k in ("equals", "in", "lt", "gt", "gte", "lte") if k in c), None)
    return pad + f"{f} {op} {c.get(op)!r}" if op else pad + str(c)


def index_page(q):
    rules = load_rules()
    dp, prov, status, rset = q.get("dp", ""), q.get("prov", ""), q.get("status", ""), q.get("set", "")
    with db() as c:
        counts = {r["rule_id"]: r for r in c.execute("SELECT rule_id, COUNT(*) n, MAX(created_at) last FROM reviews GROUP BY rule_id")}
        reviewers = [dict(r) for r in c.execute("SELECT reviewer, COUNT(DISTINCT rule_id) rules, COUNT(*) n FROM reviews GROUP BY reviewer ORDER BY rules DESC")]
        verdicts = {r["verdict"]: r["n"] for r in c.execute("""SELECT verdict, COUNT(*) n FROM reviews r WHERE id IN
            (SELECT MAX(id) FROM reviews GROUP BY rule_id, reviewer) GROUP BY verdict""")}
    rows = []
    for r in rules:
        if dp and r.get("decision_point") != dp: continue
        if prov and r.get("provenance") != prov: continue
        if rset and r["_set"] != rset: continue
        lat = latest_by_reviewer(r["id"])
        if status == "unreviewed" and lat: continue
        if status == "reviewed" and not lat: continue
        if status == "disputed" and len({x["verdict"] for x in lat}) < 2: continue
        stale = any(x["rule_hash"] != r["_hash"] for x in lat)
        chips = " ".join(f'<span class="chip {E(x["verdict"])}" title="{E(x["reviewer"])}">{E(x["verdict"])} · {E(x["reviewer"])}</span>' for x in lat)
        if stale: chips += ' <span class="chip stale" title="rule text changed after this review">changed since review</span>'
        rows.append(f'<tr><td><a href="/rule/{urllib.parse.quote(r["id"])}">{E(r["id"])}</a><br><span class="muted">{E(r["_set"])}</span></td>'
                    f'<td>{E(str(r.get("decision_point") or ("bridge" if r["_set"] == "bridges" else "")))}</td><td>{E(short_effect(r))}</td><td><span class="chip {E(str(r.get("provenance","")))}">{E(str(r.get("provenance","")))}</span></td>'
                    f'<td class="muted">{"<br>".join(E(x) for x in source_lines(r.get("source")))}{"" if is_quotation(r.get("span")) else " <span class=chip style=background:#b3261e>no quote</span>"}</td><td>{chips or "<span class=muted>—</span>"}</td></tr>')
    if not rows:
        rows.append('<tr><td colspan=6 class="muted">No rules match these filters.</td></tr>')
    total = len(rules); reviewed = sum(1 for r in rules if latest_by_reviewer(r["id"]))
    pct = lambda k: (verdicts.get(k, 0) / max(sum(verdicts.values()), 1)) * 100
    prog = "".join(f'<div style="width:{pct(k)}%;background:var(--{ {"accept":"ok","edit":"warn","reject":"bad","unsure":"muted"}[k] })" title="{k} {verdicts.get(k,0)}"></div>' for k in VERDICTS)
    rv = ", ".join(f'{E(x["reviewer"])} ({x["rules"]} rules)' for x in reviewers) or "nobody yet"
    def flt(name, val, label): return f'<a href="?{urllib.parse.urlencode({**q, name: val})}">{E(label)}</a>'
    body = f"""
<div class="card"><b>{reviewed} of {total} rules have at least one review</b> · latest verdicts:
 accept {verdicts.get('accept',0)} · edit {verdicts.get('edit',0)} · reject {verdicts.get('reject',0)} · unsure {verdicts.get('unsure',0)}
<div class="prog" style="margin:8px 0">{prog}</div><span class="muted">Reviewers: {rv}. Export: <a href="/export">review-log.jsonl</a></span></div>
<div class="card filters"><b>Filter</b> &nbsp; set: {flt('set','', 'all')} {flt('set','criteria','criteria')} {flt('set','candidates','candidates')} {flt('set','bridges','bridges')} {flt('set','history','history questions')} {flt('set','triggers','triggers')} {flt('set','terms','terms and options')}
 &nbsp;|&nbsp; DP: {flt('dp','','all')} {' '.join(flt('dp', d, d) for d in ('A','B','C','D'))}
 &nbsp;|&nbsp; provenance: {flt('prov','','all')} {flt('prov','verbatim','verbatim')} {flt('prov','operationalized','operationalized')} {flt('prov','supplemented','supplemented')}
 &nbsp;|&nbsp; status: {flt('status','','all')} {flt('status','unreviewed','unreviewed')} {flt('status','reviewed','reviewed')} {flt('status','disputed','disputed')}
 &nbsp; <a href="/">reset</a></div>
<div class="card"><table><tr><th>rule</th><th>DP</th><th>impact</th><th>provenance</th><th>source</th><th>latest verdicts</th></tr>{''.join(rows)}</table></div>"""
    return page("Rulebook review", body)


def rule_page(rule_id, ident=None):
    rules = {r["id"]: r for r in load_rules()}
    r = rules.get(rule_id)
    if not r: return None
    ids = list(rules); i = ids.index(rule_id)
    prev_id, next_id = ids[i - 1] if i else None, ids[i + 1] if i + 1 < len(ids) else None
    cites = citations(r.get("source"))
    span = str(r.get("span", ""))
    quoted = is_quotation(span)
    panels = []
    for key, pages, src in cites:
        label = DOCS[key][1]
        if not os.path.exists(pdf_path(key) or ""):
            panels.append(f'<div class="card"><b>{E(label)}</b><p class="muted">PDF not present locally - run <code>bash sources/download.sh</code>.</p></div>')
            continue
        if not pages:
            ids = re.findall(r"\b\d+\.\d+(?:\.\d+)?\b|Step \w+", src)
            idx, hit = locate_by_text(key, ([span[:60]] if quoted else []) + ids)
            if idx is None:
                panels.append(f'<div class="card"><b>{E(label)}</b> <a href="/pdf/{key}" target="_blank">open PDF</a><p class="muted">No page number in the citation and neither the quoted span nor a recommendation id was found by text search - open the PDF and search yourself. <b>That is a finding: the citation is not locatable.</b></p></div>')
                continue
            pages = [idx + 1]; located = f'located by searching for &ldquo;{E(hit)}&rdquo; (the citation gives no page number)'
        else:
            located = ""
        for pg in pages[:2]:
            if located:
                idx, how, printed_here = pg - 1, "span", None
            else:
                idx, how, printed_here = locate(key, pg, span if quoted else "")
            hl = urllib.parse.quote(span[:200]) if quoted else ""
            if how == "span":
                caption = f'<span style="color:#1b7f3b"><b>quoted span found on this page</b></span> (PDF page {idx+1}{f", printed page {printed_here}" if printed_here else ""})'
            elif how == "pagemap":
                caption = (f'<span style="color:#b07a00"><b>printed page {pg} located (PDF page {idx+1}) but the quoted span was NOT found on it</b></span> - '
                           f'the quote may be paraphrased, hyphenated, or on another page; judge from the page text')
            else:
                caption = (f'<span style="color:#b3261e"><b>could not verify this page</b></span> - showing PDF page {idx+1} as a guess for printed page {pg}; '
                           f'use the PDF viewer link')
            blank = ' <span class="chip stale">this PDF page has no text (blank or figure-only)</span>' if page_is_blank(key, idx) else ""
            panels.append(f"""<div class="card page"><b>{E(label)}</b> - cited as: <i>{E(src)}</i>
 <br><span class="muted">repo: <code>sources/{E(DOCS[key][0])}</code> · provenance and licence in <code>sources/README.md</code> · fetch: <code>bash sources/download.sh</code></span>
 {f'<p class="muted">{located}</p>' if located else ''}
 <p>{caption}{blank}</p>
 <p><a href="/pdf/{key}#page={idx+1}" target="_blank">open in PDF viewer at this page</a>
 &nbsp; <a href="/page/{key}/{max(idx-1,0)}?hl={hl}" target="_blank">&larr; prev</a> <a href="/page/{key}/{idx+1}?hl={hl}" target="_blank">next &rarr;</a></p>
 <a href="/page/{key}/{idx}?hl={hl}" target="_blank"><img loading="lazy" src="/page/{key}/{idx}?hl={hl}" alt="handbook page"></a></div>""")
    if not cites:
        panels.append('<div class="card"><b>Source</b><p class="muted">No recognised document in the citation - read the source text below.</p></div>')
    def stale_cell(x):
        if x["rule_hash"] == r["_hash"]:
            return ""
        diff = snapshot_diff(x.get("rule_snapshot"), r["_snapshot"]) if x.get("rule_snapshot") else ""
        body = f"<pre>{E(diff)}</pre>" if diff else '<p class="muted">reviewed before snapshots were kept (ADR 0008) - no diff available; the whole entry was hashed then.</p>'
        return f' <span class="chip stale">rule changed since</span><details><summary class="muted">what changed</summary>{body}</details>'
    hist = "".join(f"""<tr><td><span class="chip {E(x['verdict'])}">{E(x['verdict'])}</span></td><td>{E(x['reviewer'])}</td>
        <td class="muted">{E(x['created_at'])}{(' · at ' + E(x['rule_commit'])) if x.get('rule_commit') else ''}{' · <span class=chip>page checked</span>' if x['page_checked'] else ''}{stale_cell(x)}</td>
        <td>{E(x['comment'] or '')}{('<pre>' + E(x['suggested_change']) + '</pre>') if x['suggested_change'] else ''}</td></tr>""" for x in reviews_for(rule_id))
    notes = f'<p><b>Notes from the drafter:</b> {E(str(r["notes"]))}</p>' if r.get("notes") else ""
    v2 = []
    if r.get("why"):
        v2.append(f'<b>Why this bridge exists:</b> {E(str(r["why"]))}')
    if r["_set"] == "terms" and r.get("kind") == "option":
        sibs = [x for x in load_rules() if x["_set"] == "terms" and x.get("field") == r.get("field") and x.get("value")]
        v2.append(f'<b>Option of:</b> <code>{E(str(r.get("field")))}</code>; the other options: ' + ", ".join(f'<a href="/rule/{urllib.parse.quote(x["id"])}">{E(str(x.get("value")))}</a>' for x in sibs if x["id"] != r["id"]))
    if r["_set"] == "terms":
        v2.append(f'<b>Definition:</b> {E(str(r.get("definition")))}')
        if r.get("numbers"): v2.append(f'<b>Numbers or lists the programs read:</b> <code>{E(json.dumps(r.get("numbers"), ensure_ascii=False))}</code>')
        v2.append(f'<b>Why this line:</b> {E(str(r.get("why")))}')
        v2.append('<b>Used by:</b> ' + ", ".join(f'<a href="/rule/{urllib.parse.quote(u.split(":", 1)[1] if u.startswith("rule:") else ("trigger:" + u.split(":", 1)[1] if u.startswith("trigger:") else u.split(":", 1)[1]))}">{E(u)}</a>' if not u.startswith("engine:") else f'<code>{E(u)}</code>' for u in (r.get("used_by") or [])))
    if r["_set"] == "triggers":
        v2.append(f'<b>Why this trigger:</b> {E(str(r.get("why")))}')
        v2.append(f'<b>The question it opens:</b> &ldquo;{E(str(r.get("ask") or ""))}&rdquo; <span class="muted">({E(str(r.get("gloss") or ""))})</span>')
    if r["_set"] == "history":
        v2.append(f'<b>Purpose:</b> {E(str(r.get("purpose")))}')
        if r.get("authored"): v2.append(f'<b>Authored, with reason:</b> {E(str(r["authored"]))}')
        if r.get("asked_with"): v2.append(f'<b>Asked together with:</b> <code>{E(str(r["asked_with"]))}</code>')
        if r.get("notes"): v2.append(f'<b>Notes:</b> {E(str(r["notes"]))}')
    if r.get("sign_sources"):
        v2.append('<b>Where each sign comes from:</b><ul style="margin:4px 0">' + "".join(f'<li><code>{E(f)}</code>: {E(str(q))}</li>' for f, q in r["sign_sources"].items()) + '</ul>')
    if r.get("statements"):
        v2.append(f'<b>Supporting statements:</b> {E(", ".join(map(str, r["statements"])))} in <code>rules/extraction/v5-complete-pass.yaml</code> (the complete reading pass of the handbook; each statement carries its page and quote)')
    if r.get("origin"):
        v2.append(f'<b>Origin:</b> {E(", ".join(map(str, r["origin"])))} (meanings in <code>rules/vocabulary.yaml</code>)')
    if r.get("level_from") == "section":
        v2.append('<b>Level inferred from the section:</b> the quoted sentence names no level; the level comes from the section or list it sits in (every blind re-extraction but at most one marked it so). A first candidate for the clinician read.')
    if r.get("refinement_pending"):
        v2.append(f'<b>Refinement pending:</b> {E(str(r["refinement_pending"]))}')
    notes += ("<p>" + "<br>".join(v2) + "</p>") if v2 else ""
    eff = f'<p><b>Effect override:</b> {E(str(r["effect_override"]))}</p>' if r.get("effect_override") else ""
    when = f'<pre>{E(cond_text(r["when"]))}</pre>' if r.get("when") else (
        f'<p><b>Question wording</b> (<code>ask</code> in rules/fields.yaml; the interview model writes its own words from it): &ldquo;{E(str(r.get("ask") or ""))}&rdquo;<br>'
        f'<b>Definition (gloss):</b> {E(str(r.get("gloss") or ""))}' + (f'<br><b>Also:</b> {E(str(r["meaning"]))}' if r.get("meaning") else "") + '</p>' if r["_set"] == "history" else
        f'<p><b>Term:</b> {E(str(r.get("term")))}</p>' if r["_set"] == "terms" else '<p class="muted">Definition / policy entry - no firing condition.</p>')
    nav = (f'<a href="/rule/{urllib.parse.quote(prev_id)}">&larr; {E(prev_id)}</a>' if prev_id else "") + " &nbsp; " + (f'<a href="/rule/{urllib.parse.quote(next_id)}">{E(next_id)} &rarr;</a>' if next_id else "")
    body = f"""
<p class="muted"><a href="/">&larr; all rules</a> &nbsp; {nav}</p>
<div class="two"><div>
<div class="card"><h2 style="margin:0 0 6px">{E(r['id'])}</h2>
 <span class="chip">{E(r['_set'])}</span> <span class="chip">DP {E(str(r.get('decision_point','')))}</span>
 <span class="chip {E(str(r.get('provenance','')))}">{E(str(r.get('provenance','')))}</span>
 {f'<span class="chip" title="{E(ASSESSED.get(str(r["assessed_via"]), ""))}">assessed via {E(str(r["assessed_via"]))}</span>' if r.get('assessed_via') else ''}
 <span class="muted" title="rule content hash · git commit of the served rulebook">{E(r['_hash'])}{(' @ ' + E(rules_commit())) if rules_commit() else ''}</span>
 <p><b>Source{'s' if len(source_lines(r.get('source'))) > 1 else ''}:</b></p><ul style="margin-top:0">{''.join(f'<li>{E(x)}</li>' for x in source_lines(r.get('source')))}</ul>
 <p><b>Quoted span:</b></p>{f'<div class="span">&ldquo;{E(span)}&rdquo;</div>' if quoted else f'<div class="span" style="border-color:#b3261e;background:#fff4f2"><b>No quotation recorded</b> - the span field holds a drafter note: <i>{E(span)}</i>. A verbatim/operationalized rule without a quote cannot be verified from the page; the citation still needs a quoted sentence.</div>'}
 <div class="span" style="border-color:#1a4a7a;background:#f0f4fa"><b>What this entry claims the book prescribes:</b> {claim_text(r)}
 {f'<br><span class="muted">Assessed via <b>{E(str(r["assessed_via"]))}</b>: {E(ASSESSED.get(str(r["assessed_via"]), ""))}.</span>' if r.get('assessed_via') else ''}
 <br><span class="muted"><b>What the prototype does when it fires:</b> {engine_text(r)}</span></div>
 <p><b>How it fires and what happens:</b></p>{svg_rule(r) or when}
 {f'<details><summary class="muted">condition as text, and each fact\'s meaning and origin</summary>{when}{fields_table(r)}</details>' if svg_rule(r) else ''}{eff}{notes}
 <details><summary class="muted">raw YAML</summary><pre>{E(r['_yaml'])}</pre></details></div>
<div class="card"><h3 style="margin:0 0 6px">Your review</h3>
 <p class="muted">Read the highlighted page on the right and check three things: <b>(1) the quote</b> is on the page and means this; <b>(2) the condition</b> encodes it - no more, no less; <b>(3) the impact</b> - the level (decision point) and the strength of the verb (assign vs consider) are what the page prescribes, not stronger and not weaker. Verbatim rules must match the text; operationalized ones must state a defensible reading of vague wording; supplemented ones must be justified by the second source.</p>
 <form onsubmit="return submitReview(event)">
 <label>{'Signed in as (verified by Cloudflare Access)' if ident else 'Your name (remembered on this device)'}</label><input type="text" id="reviewer" required {f'value="{E(ident)}" readonly' if ident else ''}>
 <div class="radio"><label>Verdict</label>
  <label><input type="radio" name="verdict" value="accept" required> accept - matches the page</label>
  <label><input type="radio" name="verdict" value="edit"> edit - right idea, wrong detail (say what)</label>
  <label><input type="radio" name="verdict" value="reject"> reject - not what the page says</label>
  <label><input type="radio" name="verdict" value="unsure"> unsure - needs a clinician</label></div>
 <label><input type="checkbox" id="page_checked"> I read the cited page (not just the quoted span)</label>
 <label>Comment - what you checked, what is off</label><textarea id="comment"></textarea>
 <label>Suggested change (optional; edit the YAML)</label><textarea id="suggested" style="font-family:ui-monospace,monospace"></textarea>
 <p><button class="btn">Save review</button> <button class="btn gray" type="button" onclick="submitReview(null, true)">Save &amp; next unreviewed</button> <span class="muted" id="msg"></span></p></form></div>
<div class="card"><h3 style="margin:0 0 6px">Reviews so far</h3><table>{hist or '<tr><td class=muted>none yet</td></tr>'}</table></div>
</div><div>{''.join(panels)}</div></div>
<script>
const rv=document.getElementById('reviewer'); if(!rv.readOnly) rv.value=localStorage.getItem('reviewer')||'';
async function submitReview(e, advance){{ if(e) e.preventDefault(); localStorage.setItem('reviewer', rv.value.trim());
 const v=document.querySelector('input[name=verdict]:checked'); if(!v){{ document.getElementById('msg').textContent='pick a verdict first'; return false; }}
 if(!rv.value.trim()){{ document.getElementById('msg').textContent='your name is required'; return false; }}
 const body={{rule_id:{json.dumps(rule_id)}, rule_set:{json.dumps(r['_set'])}, rule_hash:{json.dumps(r['_hash'])}, reviewer:rv.value.trim(), verdict:v.value,
   page_checked:document.getElementById('page_checked').checked, comment:document.getElementById('comment').value, suggested_change:document.getElementById('suggested').value}};
 const res=await fetch('/api/review',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
 if(!res.ok){{ document.getElementById('msg').textContent='error: '+(await res.text()); return false; }}
 const j=await res.json(); document.getElementById('msg').textContent='saved';
 setTimeout(()=>{{ if(advance && j.next) location.href='/rule/'+encodeURIComponent(j.next); else location.reload(); }}, 300); return false; }}
</script>"""
    return page(f"Review {rule_id}", body)


# ---------------- HTTP ----------------
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # noqa: E402


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(data)))
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        p, _, qs = self.path.partition("?"); q = {k: v[0] for k, v in urllib.parse.parse_qs(qs).items()}
        try:
            if p == "/": return self._send(200, index_page(q))
            if p.startswith("/rule/"):
                body = rule_page(urllib.parse.unquote(p[6:]), ident=access_identity(self.headers))
                return self._send(200, body) if body else self._send(404, page("Not found", "<p>No such rule.</p>"))
            if p.startswith("/page/"):
                _, _, key, idx = p.split("/", 3)
                key = urllib.parse.unquote(key)
                if key not in DOCS or not os.path.exists(pdf_path(key) or ""): return self._send(404, "unknown document or PDF not present", "text/plain")
                import pymupdf
                n = len(pymupdf.open(pdf_path(key)))
                if not idx.isdigit() or not 0 <= int(idx) < n: return self._send(404, f"page index must be 0..{n-1}", "text/plain")
                return self._send(200, render_page(key, int(idx), q.get("hl", "")[:200]), "image/png", {"Cache-Control": "max-age=3600"})
            if p.startswith("/pdf/"):
                key = urllib.parse.unquote(p[5:])
                path = pdf_path(key)
                if not path or not os.path.exists(path): return self._send(404, "PDF not present locally", "text/plain")
                return self._send(200, open(path, "rb").read(), "application/pdf")
            if p == "/cases":
                return self._send(200, case_review.index(q, case_verdicts_by_case(), page))
            if p.startswith("/case/"):
                body = case_review.case_page(urllib.parse.unquote(p[6:]), access_identity(self.headers), page, locate, None, lambda cid: reviews_for(cid), rules_commit)
                return self._send(200, body) if body else self._send(404, page("Not found", "<p>No such case.</p>"))
            if p == "/export":
                export()
                return self._send(200, open(os.path.join(OUT, "review-log.jsonl"), "rb").read(), "application/x-ndjson",
                                  {"Content-Disposition": "attachment; filename=review-log.jsonl"})
            if p == "/api/stats":
                with db() as c:
                    return self._send(200, json.dumps([dict(r) for r in c.execute("SELECT rule_id, reviewer, verdict, created_at FROM reviews")]), "application/json")
            return self._send(404, page("Not found", "<p>Unknown path.</p>"))
        except Exception as e:
            return self._send(500, page("Error", f"<p>Server error: {E(str(e)[:300])}</p>"))

    def do_POST(self):
        if self.path in ("/api/case-review", "/api/case-bulk-confirm"): return self._case_post()
        if self.path != "/api/review": return self._send(404, "no", "text/plain")
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 20000: return self._send(413, "review too large", "text/plain")
            try: d = json.loads(self.rfile.read(n) or b"{}")
            except ValueError: return self._send(400, "body must be JSON", "text/plain")
            ident = access_identity(self.headers)
            if ident: d["reviewer"] = ident
            elif CF_TEAM and CF_AUD: return self._send(401, "not authenticated through Cloudflare Access", "text/plain")
            if not str(d.get("reviewer", "")).strip(): return self._send(400, "reviewer name required", "text/plain")
            if len(str(d.get("reviewer"))) > 60: return self._send(400, "reviewer name too long (60)", "text/plain")
            if d.get("verdict") not in VERDICTS: return self._send(400, "verdict must be one of " + ", ".join(VERDICTS), "text/plain")
            rules = {r["id"]: r for r in load_rules()}
            r = rules.get(d.get("rule_id"))
            if not r: return self._send(400, "unknown rule", "text/plain")
            if d.get("rule_hash") != r["_hash"]:
                return self._send(409, "the rule changed since this page was loaded - reload and review the current text", "text/plain")
            if len(str(d.get("comment") or "")) > 4000 or len(str(d.get("suggested_change") or "")) > 8000:
                return self._send(400, "comment (4000) or suggested change (8000) too long", "text/plain")
            d["rule_set"] = r["_set"]; d["rule_snapshot"] = r["_snapshot"]; d["rule_commit"] = rules_commit()
            add_review(d); return self._send(200, json.dumps({"ok": True, "next": next_unreviewed(rules, d["rule_id"], d["reviewer"])}), "application/json")
        except Exception as e:
            return self._send(500, str(e)[:300], "text/plain")


def _case_post_impl(self):
    try:
        n = int(self.headers.get("Content-Length", 0))
        if n > 20000: return self._send(413, "too large", "text/plain")
        try: d = json.loads(self.rfile.read(n) or b"{}")
        except ValueError: return self._send(400, "body must be JSON", "text/plain")
        ident = access_identity(self.headers)
        if ident: d["reviewer"] = ident
        elif CF_TEAM and CF_AUD: return self._send(401, "not authenticated through Cloudflare Access", "text/plain")
        if not str(d.get("reviewer", "")).strip() or len(str(d.get("reviewer"))) > 60: return self._send(400, "reviewer name required (max 60)", "text/plain")
        cases = case_review.load_cases()
        if self.path == "/api/case-bulk-confirm":
            # confirm every case whose two readings agree and whose test passes (its outcome matches its expectation, or it is a recorded expected failure)
            _, cmp_ = case_review.second(); n_done = 0
            for cid, c in cases.items():
                r = cmp_.get(cid)
                if not r or r.get("outcome_ours") != r.get("outcome_theirs") or r.get("value_differs") or r.get("only_theirs"): continue
                add_review({"rule_id": cid, "rule_set": "case", "rule_hash": c["_hash"], "reviewer": d["reviewer"], "verdict": "accept", "page_checked": 0,
                            "comment": "bulk: both readings agree and the test passes", "rule_snapshot": c["_snapshot"], "rule_commit": rules_commit()}); n_done += 1
            return self._send(200, f"confirmed {n_done} cases", "text/plain")
        c = cases.get(d.get("case_id"))
        if not c: return self._send(400, "unknown case", "text/plain")
        if d.get("verdict") not in VERDICTS: return self._send(400, "verdict must be one of " + ", ".join(VERDICTS), "text/plain")
        if d.get("case_hash") != c["_hash"]: return self._send(409, "the case changed since this page was loaded - reload", "text/plain")
        add_review({"rule_id": c["_id"], "rule_set": "case", "rule_hash": c["_hash"], "reviewer": d["reviewer"], "verdict": d["verdict"], "page_checked": 1,
                    "comment": d.get("comment"), "rule_snapshot": c["_snapshot"], "rule_commit": rules_commit()})
        return self._send(200, json.dumps({"ok": True, "next": next_unreviewed_case(c["_id"], d["reviewer"])}), "application/json")
    except Exception as e:
        return self._send(500, str(e)[:300], "text/plain")
H._case_post = _case_post_impl


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        print(f"exported {export()} reviews to {OUT}/")
    else:
        db().close()
        print(f"rule review: http://localhost:{PORT}   data: {DATA}   rulebook at {rules_commit() or '(not a git checkout)'}")
        ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
