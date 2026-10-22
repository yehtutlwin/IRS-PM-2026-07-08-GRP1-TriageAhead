"""Deterministic core: condition evaluator, agenda controller, ESI-floor evaluator.
No LLM anywhere in this file. Rules are loaded from the spike's criteria.yaml."""
import yaml, os, re, time
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))

def load_terms():
    """rules/terms.yaml: the fuzzy terms (a word used without a number or list, and the number, band or list the system
    assigns to it); the engine reads the age bands and the blood-thinner names from it, so a review there changes behaviour."""
    if "terms" not in _KB:
        with open(os.path.join(HERE, "..", "rules", "terms.yaml")) as f:
            _KB["terms"] = {t["id"]: t for t in yaml.safe_load(f) if isinstance(t, dict)}
    return _KB["terms"]


def option_definitions(field):
    """{value: definition} for a choice field, from the option entries of rules/terms.yaml."""
    return {t["value"]: t["definition"] for t in load_terms().values() if t.get("field") == field and "value" in t}


_KB = {}
ANTICOAG_NAMES = set(load_terms()["blood_thinner"]["numbers"]["names"])
ANTICOAG_PHRASES = re.compile(load_terms()["blood_thinner"]["numbers"]["phrase_pattern"], re.I)


# fields that accumulate across turns instead of last-write-wins; first entry is
# the presenting complaint and is never displaced (TODO item 6, implemented 18 Aug)
ACCUMULATE = {"complaint.category"}

# complaint-scoped detail fields: grouped into per-complaint records (18 Aug).
# Patient-level facts (danger_signs, history, worst-pain semantics...) stay flat;
# rules keep reading flat views, so criteria.yaml is untouched.
COMPLAINT_DETAILS = {"complaint.text", "complaint.onset", "complaint.pain_rating"}


# ---------- facts store ----------
class Facts:
    def __init__(self):
        self.d = {}   # field -> {value, status, who, turn}

    def write(self, field, value, status="reported", who="caregiver", turn=None):
        if field in ACCUMULATE and field in self.d:
            old = self.d[field]["value"]
            merged = old if isinstance(old, list) else [old]
            for v in (value if isinstance(value, list) else [value]):
                if v not in merged:
                    merged.append(v)
            value = merged
        self.d[field] = {"value": value, "status": status, "who": who, "turn": turn,
                         "ts": time.strftime("%Y-%m-%d %H:%M")}

    # -- per-complaint records: d["complaints"] holds a list of
    #    {"category": str, "opened": rec, "<detail>": rec} dicts; first = presenting
    def complaints(self):
        rec = self.d.get("complaints")
        return rec["value"] if rec else []

    def _complaint_rec(self, category, status, who, turn):
        recs = self.complaints()
        for r in recs:
            if r["category"] == category:
                return r
        r = {"category": category,
             "opened": {"value": True, "status": status, "who": who, "turn": turn,
                        "ts": time.strftime("%Y-%m-%d %H:%M")}}
        recs.append(r)
        self.d["complaints"] = {"value": recs, "status": status, "who": who, "turn": turn}
        return r

    def write_complaint(self, category, field=None, value=None,
                        status="reported", who="caregiver", turn=None):
        """Open/extend the record for `category`; refresh the flat views rules read:
        complaint.category (membership list) and complaint.pain_rating (max = worst
        pain, ESI's patient-level severe-pain reading - errs conservative only)."""
        r = self._complaint_rec(category, status, who, turn)
        if field is not None:
            short = field.split(".", 1)[1]   # complaint.onset -> onset
            r[short] = {"value": value, "status": status, "who": who, "turn": turn,
                        "ts": time.strftime("%Y-%m-%d %H:%M")}
            # flat view (latest written) so slot resolution still sees text/onset;
            # without it complaint.main could only close via the attempt cap
            if field in ("complaint.text", "complaint.onset"):
                self.write(field, value, status=status, who=who, turn=turn)
        self.write("complaint.category", category, status=status, who=who, turn=turn)
        ratings = [r2["pain_rating"]["value"] for r2 in self.complaints()
                   if r2.get("pain_rating") and r2["pain_rating"]["value"] is not None]
        if ratings:
            self.write("complaint.pain_rating", max(ratings), status=status, who=who, turn=turn)
        if field == "complaint.pain_rating" and value is not None:
            # trend view for the report (rules keep the worst-pain flat view above)
            self.write("complaint.pain_latest", value, status=status, who=who, turn=turn)

    def resolve(self, path):
        """Supports trailing .value / .status; bare path -> value."""
        attr = "value"
        if path.endswith(".value"):
            path, attr = path[:-6], "value"
        elif path.endswith(".status"):
            path, attr = path[:-7], "status"
        rec = self.d.get(path)
        return None if rec is None else rec.get(attr)

    def has(self, field):
        return field in self.d


# ---------- condition DSL ----------
def holds(cond, facts: Facts):
    if cond is None:
        return False
    if "all" in cond:
        return all(holds(c, facts) for c in cond["all"])
    if "any" in cond:
        return any(holds(c, facts) for c in cond["any"])
    if "not" in cond:                      # true when the inner condition does not hold, including when its fact is unknown
        return not holds(cond["not"], facts)
    v = facts.resolve(cond["field"])
    if v is None:
        return False
    # accumulated fields hold a list: equals/in match on ANY element, so a rule
    # like category==chest_pain still fires after the conversation moved on
    if "equals" in cond:
        return cond["equals"] in v if isinstance(v, list) else v == cond["equals"]
    if "in" in cond:
        return any(x in cond["in"] for x in v) if isinstance(v, list) else v in cond["in"]
    try:
        fv = float(v)
    except (TypeError, ValueError):
        return False
    if "lt" in cond:  return fv <  float(cond["lt"])
    if "gt" in cond:  return fv >  float(cond["gt"])
    if "gte" in cond: return fv >= float(cond["gte"])
    if "lte" in cond: return fv <= float(cond["lte"])
    return False


# ---------- criteria / tree ----------
def load_criteria():
    with open(os.path.join(HERE, "..", "rules", "criteria.yaml")) as f:
        return [c for c in yaml.safe_load(f) if isinstance(c, dict)]


def evaluate_tree(facts: Facts, criteria):
    """Returns dict with floor, fired, consider, notes, esi1_indicators."""
    fired, consider, notes, esi1 = [], [], [], []
    for c in criteria:
        note = c.get("effect_override") == "context_note"   # background for the nurse; read at any decision point
        if "when" not in c or (not note and c.get("decision_point") not in ("A", "B")):
            continue
        if not holds(c["when"], facts):
            continue
        entry = {"id": c["id"], "source": c.get("source"), "span": c.get("span", "")}
        if note:
            notes.append(entry)
        elif c.get("effect_override") == "consider":
            consider.append(entry)
        elif c["decision_point"] == "A":
            esi1.append(entry)
        else:
            fired.append(entry)
    floor = "at least ESI-2" if fired else None
    return {"floor": floor, "fired": fired, "consider": consider, "notes": notes,
            "esi1_indicators": esi1, "pending": ["C (resources)", "D (vitals not available pre-arrival)"]}


# ---------- derivations (deterministic, run after every write) ----------
def _age_from_dob(dob):
    """Best-effort age in years from a free-text DOB ('02 Jan 1939', '1939-01-02'...)."""
    from datetime import datetime
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            b = datetime.strptime(dob.strip(), fmt).date()
            t = date.today()
            return t.year - b.year - ((t.month, t.day) < (b.month, b.day))
        except ValueError:
            pass
    m = re.search(r"\b(19\d\d|20\d\d)\b", dob)
    return date.today().year - int(m.group(1)) if m else None


def _try_parse(s, fmt):
    from datetime import datetime
    try:
        datetime.strptime(s.strip(), fmt); return True
    except ValueError:
        return False


# bridges: rules/bridges.yaml (cited, reviewable; same condition DSL as criteria.yaml). Loaded once; a `signs`
# or `entails` entry writes `target` when its `when` holds and the target is not already present; a `count`
# entry writes how many of its fields are true. Add-only, so derivations can only raise the floor.
_bridges_cache = None


def load_bridges():
    global _bridges_cache
    if _bridges_cache is None:
        with open(os.path.join(HERE, "..", "rules", "bridges.yaml")) as f:
            _bridges_cache = [b for b in yaml.safe_load(f) if isinstance(b, dict)]
    return _bridges_cache


# ---------- relative time -> absolute estimate (anchored on when it was said) ----------
_REL_NUM = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "ten": 10, "fifteen": 15, "twenty": 20, "thirty": 30, "half an": 0.5, "half": 0.5}


def resolve_relative_time(text, said_at):
    """'10 mins ago', 'half an hour ago', 'about 2 hours ago', 'around 1pm', 'yesterday'
    -> 'YYYY-MM-DD HH:MM' estimate, or None. said_at: the record's ts string."""
    if not text:
        return None
    t = str(text).lower().strip()
    try:
        anchor = datetime.strptime(said_at, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        anchor = datetime.now()
    m = re.search(r"(\d+(?:\.\d+)?|half an|a|an|one|two|three|four|five|six|ten|fifteen|twenty|thirty)\s*"
                  r"(min(?:ute)?s?|hours?|hrs?|h|days?)\s*(?:ago|before|earlier|back)", t)
    if m:
        n = float(m.group(1)) if m.group(1)[0].isdigit() else _REL_NUM.get(m.group(1), 1)
        unit = m.group(2)
        delta = timedelta(minutes=n) if unit.startswith("m") else \
                timedelta(hours=n) if unit.startswith("h") else timedelta(days=n)
        return (anchor - delta).strftime("%Y-%m-%d %H:%M")
    if "just now" in t or t in ("now", "right now"):
        return anchor.strftime("%Y-%m-%d %H:%M")
    if "yesterday" in t:
        return (anchor - timedelta(days=1)).strftime("%Y-%m-%d") + " (time unknown)"
    if "this morning" in t:
        return anchor.strftime("%Y-%m-%d") + " morning"
    if "last night" in t:
        return (anchor - timedelta(days=1)).strftime("%Y-%m-%d") + " night"
    m = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", t)
    if m:
        h, mi = int(m.group(1)) % 12, int(m.group(2) or 0)
        if m.group(3) == "pm": h += 12
        return anchor.strftime("%Y-%m-%d") + f" {h:02d}:{mi:02d}"
    return None


def derive_absolute_times(facts, turn):
    """For the free-text time fields, add a sibling *_abs estimate anchored on the
    record's own timestamp. The original phrase stays as the evidence."""
    for f in ("complaint.onset", "L.last_intake"):
        rec = facts.d.get(f)
        if rec and not facts.has(f + "_abs"):
            est = resolve_relative_time(rec.get("value"), rec.get("ts"))
            if est:
                facts.write(f + "_abs", f"~{est} (from '{rec['value']}' said {rec.get('ts', '?')[-5:]})",
                            status="reported", who="derived", turn=turn)
    for r in facts.complaints():
        if "onset" in r and "onset_abs" not in r:
            est = resolve_relative_time(r["onset"].get("value"), r["onset"].get("ts"))
            if est:
                r["onset_abs"] = {"value": f"~{est}", "status": "reported", "who": "derived",
                                  "turn": turn, "ts": r["onset"].get("ts")}


def derive(facts: Facts, turn):
    derive_absolute_times(facts, turn)
    for b in load_bridges():
        if b.get("count"):
            # a `count` bridge: the target is how many of the listed everyday signs are true; it may overwrite only
            # a value it wrote itself, never one the caregiver stated
            n = sum(1 for f in b["count"] if facts.resolve(f) is True)
            cur = facts.d.get(b["target"])
            if n and (cur is None or cur.get("who") == "derived") and (cur is None or cur.get("value") != n):
                facts.write(b["target"], n, status="reported", who="derived", turn=turn)
        elif not facts.has(b["target"]) and holds(b.get("when"), facts):
            facts.write(b["target"], b.get("value", True), status="reported", who="derived", turn=turn)
    # age from the DOB we already collect at wrap-up (unblocks B-27)
    if not facts.has("patient.age") and facts.resolve("identity.dob"):
        dob = str(facts.resolve("identity.dob"))
        age = _age_from_dob(dob)
        if age is not None:
            # a full date -> reported; a bare year ("1950 something") -> probable, so the
            # report chip says so and a reviewer knows the age is +-1 year at best
            exact = any(_try_parse(dob, fmt) for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"))
            facts.write("patient.age", age, status="reported" if exact else "probable", who="derived", turn=turn)
    # age units and band: months from whole years and years from months when only one is known; the age group (read by the
    # flaccid-infant rule A-13) from whichever age is known, with the handbook's bands (ESI v5 p.24, Table 6-1; see
    # patient.age_group in rules/fields.yaml). Never overwrites a stated value.
    def _num(f):
        try: return float(facts.resolve(f)) if facts.resolve(f) is not None else None
        except (TypeError, ValueError): return None
    years, months, days = _num("patient.age"), _num("patient.age_months"), _num("patient.age_days")
    if years is None and months is not None:
        facts.write("patient.age", int(months // 12), status="reported", who="derived", turn=turn); years = months // 12
    if months is None and years is not None and years < 3:
        facts.write("patient.age_months", int(years * 12), status="probable", who="derived", turn=turn); months = years * 12
    if not facts.has("patient.age_group"):
        band, T = None, load_terms()
        yrs = years if years is not None else (months / 12 if months is not None else (days / 365 if days is not None else None))
        if yrs is not None:
            for b in ("infant", "child", "adult", "older_adult"):          # the bands come from rules/terms.yaml
                lo, hi = T[b]["numbers"].get("age_years_min", 0), T[b]["numbers"].get("age_years_max")
                if yrs >= lo and (hi is None or yrs < hi): band = b; break
        if band: facts.write("patient.age_group", band, status="reported", who="derived", turn=turn)
    # aliases (rules/fields.yaml alias_of): one fact under two names; whichever was written fills the other
    for f, spec in load_fields().items():
        other = spec.get("alias_of")
        if other and facts.has(f) != facts.has(other):
            src, dst = (f, other) if facts.has(f) else (other, f)
            rec = facts.d[src]
            facts.write(dst, rec["value"], status=rec["status"], who="derived", turn=turn)
    # blood thinner: a named anticoagulant anywhere (medicine list, the confirmation answer) confirms it; a description
    # ("a pill that thins the blood") makes it probable. Runs whatever the extractor wrote, so a direct "yes, warfarin"
    # (status reported) is upgraded too; B-30 needs confirmed.
    # a blood thinner named in the confirmation answer belongs on the medicine list too (the report's M line was empty
    # although warfarin had been named, 15 Oct 2026): added, never removed; the caregiver's own list is kept as written
    conf = facts.resolve("confirm.M.anticoagulant")
    if conf and facts.has("M.medications") and isinstance(facts.resolve("M.medications"), list) \
            and not any(str(conf).lower() in str(m).lower() for m in facts.resolve("M.medications")):
        meds = list(facts.resolve("M.medications"))
        vague = [m for m in meds if any(w in str(m).lower() for w in ("thin", "clot", "anticoag"))]
        if vague:   # "blood thinner" becomes "blood thinner (warfarin)" rather than a second item
            meds = [f"{m} ({conf})" if m in vague[:1] else m for m in meds]
        else:
            meds.append(str(conf))
        facts.write("M.medications", meds, status="reported", who="derived", turn=turn)
    names = [str(m) for m in (facts.resolve("M.medications") or [])] + ([str(facts.resolve("confirm.M.anticoagulant"))] if facts.resolve("confirm.M.anticoagulant") else [])
    status = facts.resolve("M.anticoagulant.status")
    if status != "confirmed":
        if any(n in name.lower() for name in names for n in ANTICOAG_NAMES):
            facts.write("M.anticoagulant", True, status="confirmed", who="caregiver", turn=turn)
        elif not facts.has("M.anticoagulant") and any(ANTICOAG_PHRASES.search(name) for name in names):
            facts.write("M.anticoagulant", True, status="probable", who="caregiver", turn=turn)


# ---------- agenda (knowledge base v2: derived from the rules, rules/derived/agenda.yaml) ----------

def load_fields():
    if "fields" not in _KB:
        with open(os.path.join(HERE, "..", "rules", "fields.yaml")) as f:
            _KB["fields"] = yaml.safe_load(f)["fields"]
    return _KB["fields"]


def load_agenda():
    if "agenda" not in _KB:
        with open(os.path.join(HERE, "..", "rules", "derived", "agenda.yaml")) as f:
            _KB["agenda"] = yaml.safe_load(f)["fields"]
    return _KB["agenda"]


def possible(cond, facts: Facts):
    """Three-valued reading of a rule condition: could it still hold once the unknown facts are known?
    A leaf on a stored fact is evaluated; a leaf on an unknown fact counts as possible."""
    if cond is None:
        return True
    if "all" in cond:
        return all(possible(c, facts) for c in cond["all"])
    if "any" in cond:
        return any(possible(c, facts) for c in cond["any"])
    if "not" in cond:
        inner = cond["not"]
        return True if not _known(inner, facts) else not holds(inner, facts)
    return holds(cond, facts) if facts.has(_base(cond.get("field", ""))) else True


def _known(cond, facts: Facts):
    if cond is None:
        return True
    for k in ("all", "any"):
        if k in cond:
            return all(_known(c, facts) for c in cond[k])
    if "not" in cond:
        return _known(cond["not"], facts)
    return facts.has(_base(cond.get("field", "")))


def _base(field):
    return field[:-6] if field.endswith(".value") else field[:-7] if field.endswith(".status") else field


def _rule_gate_open(rids, criteria_by_id, field, facts: Facts):
    """A field with rule gates only opens when one of those rules is still possible and another of its facts is known."""
    for rid in rids:
        r = criteria_by_id.get(rid)
        if not r or not possible(r["when"], facts):
            continue
        others = {_base(l["field"]) for l in _leaves(r["when"], [])} - {field}
        if any(facts.has(o) for o in others):
            return True
    return False


def _leaves(w, out):
    if isinstance(w, dict):
        if "field" in w:
            out.append(w)
        for k in ("all", "any", "not"):
            if k in w:
                _leaves(w[k], out)
    elif isinstance(w, list):
        for x in w:
            _leaves(x, out)
    return out


def open_fields(facts: Facts, attempts, criteria=None, max_attempts=3):
    """What the interview may ask now, in order: every agenda field that is not stored, has been asked fewer than
    max_attempts times, and whose policy and gates allow it. A confirmation entry (a rule needs the fact confirmed)
    is due while the fact's status is probable, and is asked alone. Returns dicts: field, hint, confirm, why."""
    agenda = load_agenda()
    if criteria is None:
        if "criteria_by_id" not in _KB:
            _KB["criteria_by_id"] = {c["id"]: c for c in load_criteria() if c.get("when")}
        crit = _KB["criteria_by_id"]
    else:
        crit = {c["id"]: c for c in criteria if c.get("when")}
    out = []
    for f, e in agenda.items():
        if attempts.get(f, 0) >= max_attempts:
            continue
        if e.get("confirm_for") and facts.has(f) and facts.resolve(f) and facts.resolve(f + ".status") in ("probable", "reported") and attempts.get("confirm." + f, 0) < max_attempts:   # a rule needs it confirmed: ask for the exact name while it is only reported or probable
            out.append({"field": f, "hint": e["ask"], "confirm": True, "why": "confirmation for " + ", ".join(e["confirm_for"])})
            continue
        if facts.has(f):
            continue
        pol = e["ask_policy"]
        if pol == "always":
            out.append({"field": f, "hint": e["ask"], "confirm": False, "why": "asked of everyone"})
        elif pol == "when_applicable":
            if e.get("trigger") is not None:          # an authored trigger (rules/triggers.yaml)
                if holds(e["trigger"], facts):
                    out.append({"field": f, "hint": e["ask"], "confirm": False, "why": "applies on the facts so far"})
            elif _rule_gate_open(e.get("rule_gates", []), crit, f, facts):
                out.append({"field": f, "hint": e["ask"], "confirm": False, "why": "a rule that reads it is still possible: " + ", ".join(e["rule_gates"])})
        # volunteered_only: never offered
    return out

def fields_of_question_id(qid):
    """The fields a question id names: 'dyn:a+b' (the model's bundle) or 'fld:a+b' (the program's bundle)."""
    if not qid or qid == "checkin.status":
        return []
    return qid.split(":", 1)[1].split("+") if ":" in qid else [qid]


def static_bundle(open_list, limit=4):
    """Without a model choosing the grouping: the top open field plus the open fields asked with it (asked_with) or of
    the same topic (same area prefix, same priority: the four danger signs, the infection screen, the limb signs),
    up to limit. A confirmation is always alone."""
    if not open_list:
        return []
    top = open_list[0]
    if top["confirm"]:
        return [top]
    agenda = load_agenda()
    anchor = agenda.get(top["field"], {}).get("asked_with") or top["field"]
    area, prio = top["field"].split(".")[0], agenda.get(top["field"], {}).get("priority")
    group = [top]
    for o in open_list[1:]:
        if len(group) >= limit or o["confirm"]:
            continue
        e = agenda.get(o["field"], {})
        same_anchor = (e.get("asked_with") or o["field"]) == anchor
        same_topic = o["field"].split(".")[0] == area and e.get("priority") == prio
        if same_anchor or same_topic:
            group.append(o)
    return group


# ---------- interview design v2 (#63, decided 14 Oct 2026) ----------
ESSENTIALS = {"danger_signs.responsive", "danger_signs.chest_pain_now", "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding",
              "complaint.category", "complaint.text", "complaint.onset", "patient.age", "patient.sex",
              "M.medications", "A.allergies", "history.conditions", "identity.name", "identity.dob"}


def pre_arrival_fields(floor_set=False):
    """The questions the pre-arrival part of the interview may ask (interview design v2, #63). While no floor is set: the
    agenda's bands 0 to 2 (the danger signs, the facts other questions wait on, every question that can set a level, the
    handover history asked with them) plus the two identity fields. Once the floor is 'at least ESI-2' no further question
    can raise it (level 1 is the nurse's), so only the essentials remain: the danger signs, the complaint, age and sex,
    medicines, allergies, conditions, identity. When none is open, the report is ready and the QR code is shown; the
    remaining questions (flags, notes, the rest of the history) continue in the same chat."""
    if floor_set:
        return set(ESSENTIALS)
    return {f for f, e in load_agenda().items() if e["priority"] <= 2} | {"identity.name", "identity.dob"}


def after_report_fields():
    """The questions still worth asking once the report is ready and the floor is set: those that serve something other than a
    rule that sets a level, which can no longer change anything. Kept: fields with a purpose (the handover history, the
    infection screen, identity), fields that feed only consider flags or context notes, and the everyday signs that feed them.
    Dropped: fields whose only consumers are rules that assign a level (fall height, the limb warning signs). Decided after
    Ye Htut Lwin's test session of 15 Oct 2026, in which the chat asked the fall height after the QR code."""
    agenda, specs = load_agenda(), load_fields()
    keep = set()
    for f, e in agenda.items():
        effects = set(e.get("effects") or [])
        if specs.get(f, {}).get("purpose") or not effects or not (effects <= {"assign_1", "assign_2"}):
            keep.add(f)
    return keep


def cap_yes_no(fields, limit=2):
    """A bundle holds at most `limit` yes/no questions (the four-in-one danger-sign question produced the wrong 'no's of
    #80): the first ones stay, in order; other kinds of question are not counted."""
    specs = load_fields(); out, n = [], 0
    for f in fields:
        if specs.get(f, {}).get("type") == "bool":
            if n >= limit:
                continue
            n += 1
        out.append(f)
    return out


_STOP = {"patient", "caregiver", "person", "sees", "says", "said", "states", "stated", "right", "normally", "symptom", "symptoms", "finding", "findings",
         "today", "since", "started", "problem", "with", "without", "that", "this", "than", "their", "they", "have", "been", "does",
         "when", "what", "which", "also", "only", "other", "some", "more", "most", "less", "after", "before", "about", "from",
         "into", "over", "under", "each", "every", "where", "there", "then", "them", "being", "even", "ever", "much", "many",
         "complaint", "history", "signs", "danger", "status", "class", "count", "elements", "cause", "written", "write", "field",
         "fields", "value", "rule", "rules", "read", "reads", "asked", "question", "answer", "caregiver's", "patient's", "known",
         "anyone", "anything", "something", "someone", "whether", "because", "though", "still", "just", "very", "such", "like"}


def field_keywords(field):
    """Word stems that show an answer addresses this field: from its name, its gloss and its everyday wording (four letters
    or more, cut to five, common words removed) and its stated_only words. The fact-extraction guard requires one of them in
    the answer before it keeps a denial (value false), so a 'no' said about one thing cannot become a 'no' about another."""
    spec = load_fields().get(field, {})
    text = " ".join([field.split(".", 1)[-1].replace("_", " "), str(spec.get("gloss") or ""), str(spec.get("ask") or "")])
    words = [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 4 and w not in _STOP]
    return {w[:5] for w in words} | {str(k).lower() for k in spec.get("stated_only") or []}

