"""Validate rules/criteria.yaml mechanically: schema (rule entries), unique ids, and every quoted span found
verbatim on one of its cited PRINTED pages of the handbook (supplemented rules and non-rule entries skipped).
Run: .venv/bin/python rules/validate.py   (exit 1 on any failure)"""
import os, re, sys, json, difflib, yaml, jsonschema, pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OFFSET = 6
crit = yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml")))
schema = json.load(open(os.path.join(ROOT, "rules", "criteria.schema.json")))
doc = pymupdf.open(os.path.join(ROOT, "sources", "ESI-Handbook-5th-Edition-3-2023.pdf"))
def norm(s):
    s = str(s).lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"[\s\-]+", " ", s).strip()
pages = {i + 1 - OFFSET: norm(doc[i].get_text()) for i in range(len(doc)) if i + 1 - OFFSET >= 1}
vocab = yaml.safe_load(open(os.path.join(ROOT, "rules", "vocabulary.yaml")))
v = jsonschema.Draft202012Validator(schema); fails = 0; ids = set(); rows = []
# the schema's enumerations must be exactly the vocabulary's values, and every rule's tag value must be listed
for tag in ("decision_point", "assessed_via", "provenance", "effect_override", "level_from"):
    listed = sorted(vocab[tag]["values"]); enum = sorted(schema["properties"][tag]["enum"])
    if listed != enum: print(f"VOCAB {tag}: schema enum {enum} != vocabulary {listed}"); fails += 1
    for r in crit:
        if tag in r and r[tag] not in vocab[tag]["values"]: print(f"VOCAB {r['id']}: {tag}={r[tag]!r} not in rules/vocabulary.yaml"); fails += 1
for tag, body in vocab.items():
    for val, d in (body.get("values") or {}).items():
        for k in ("meaning", "program", "example"):
            if not d.get(k): print(f"VOCAB {tag}.{val}: missing {k}"); fails += 1
for r in crit:
    rid = r["id"]
    if rid in ids: print("DUPLICATE id", rid); fails += 1
    ids.add(rid)
    if r.get("when"):
        errs = [e.message for e in v.iter_errors(r)]
        if errs: print("SCHEMA", rid, "-", errs[0][:100]); fails += 1
    if r.get("provenance") == "supplemented" or not r.get("when"): rows.append((rid, "skipped")); continue
    cited = [int(p) for p in re.findall(r"p\.(\d+)", str(r["source"]))]
    ns = norm(r["span"]); found = None
    for p in cited:
        if p in pages and ns in pages[p]: found = p; break
    if found is None:
        best = 0
        for p in cited:
            t = pages.get(p, ""); L = len(ns)
            for i in range(0, max(1, len(t) - L + 1), max(1, L // 4)):
                best = max(best, difflib.SequenceMatcher(None, ns, t[i:i + L]).ratio())
        elsewhere = [p for p, t in pages.items() if ns in t]
        print(f"SPAN {rid}: not on cited {cited} (best fuzzy {best:.2f}); found on {elsewhere or 'no page'}"); fails += 1
        rows.append((rid, "FAIL"))
    else: rows.append((rid, f"ok p.{found}"))
# v2: every field used anywhere is defined in rules/fields.yaml, none is defined and unused, and the derived index is current
import subprocess
dv = subprocess.run([sys.executable, os.path.join(ROOT, "rules", "derive.py"), "--check"], capture_output=True, text=True)
if dv.returncode: print("FIELDS", dv.stdout.strip()); fails += 1
# v2: every entry names the statements of the complete reading pass that support it; each number exists and names the entry back
pass_st = {s["n"]: s for s in yaml.safe_load(open(os.path.join(ROOT, "rules", "extraction", "v5-complete-pass.yaml")))["statements"]}
for r in crit:
    nums = r.get("statements")
    if nums is None: print("STATEMENTS", r["id"], "- no statements list"); fails += 1; continue
    if not nums and r.get("provenance") != "supplemented": print("STATEMENTS", r["id"], "- empty but not supplemented"); fails += 1
    for n in nums:
        s = pass_st.get(n)
        named = s and (r["id"] in s.get("rules", []) or s.get("rule") == r["id"] or s.get("proposal") == r["id"])
        if not named: print("STATEMENTS", r["id"], f"- statement {n} missing or does not name this entry"); fails += 1
# v2: bridges name only defined fields, carry a source for anything clinical, and agree with the fields' `feeds`
fields = yaml.safe_load(open(os.path.join(ROOT, "rules", "fields.yaml")))["fields"]
terms = {t["id"]: t for t in yaml.safe_load(open(os.path.join(ROOT, "rules", "terms.yaml"))) if isinstance(t, dict)}
bridges = [b for b in yaml.safe_load(open(os.path.join(ROOT, "rules", "bridges.yaml"))) if isinstance(b, dict)]
def _leaves(w, out):
    if isinstance(w, dict):
        if "field" in w: out.append(w["field"])
        for k in ("all", "any", "not"):
            if k in w: _leaves(w[k], out)
    elif isinstance(w, list):
        for x in w: _leaves(x, out)
    return out
_seen, _reads = set(), {}                                  # field -> the targets of the bridges that read it
for b in bridges:
    bid = b.get("id", "?")
    if bid in _seen: print("BRIDGE", bid, "- duplicate id"); fails += 1
    _seen.add(bid)
    if b.get("kind") not in ("signs", "count", "entails"): print("BRIDGE", bid, "- kind must be signs, count or entails"); fails += 1
    if b.get("target") not in fields: print("BRIDGE", bid, "- target not in fields.yaml:", b.get("target")); fails += 1
    srcs = _leaves(b.get("when"), []) + list(b.get("count") or [])
    if not srcs: print("BRIDGE", bid, "- neither when nor count"); fails += 1
    for f in srcs:
        if f.replace(".value", "").replace(".status", "") not in fields: print("BRIDGE", bid, "- reads an undefined field", f); fails += 1
        _reads.setdefault(f, set()).add(b.get("target"))
    if b.get("kind") in ("signs", "count") and not (b.get("source") and b.get("span")): print("BRIDGE", bid, "- a signs or count bridge needs source and span"); fails += 1
    if not b.get("why"): print("BRIDGE", bid, "- no why"); fails += 1
    for f in (b.get("sign_sources") or {}):
        if f not in srcs: print("BRIDGE", bid, "- sign_sources names a field the bridge does not read:", f); fails += 1
for f, spec in fields.items():
    for t in [x.strip() for x in str(spec.get("feeds") or "").split(",") if x.strip()]:
        if t not in _reads.get(f, set()): print("FEEDS", f, "- says it feeds", t, "but no bridge reads it into that target"); fails += 1
for f, ts in _reads.items():
    if f.startswith(("stroke.", "limb.", "eye.", "ams.")):
        declared = {x.strip() for x in str(fields.get(f, {}).get("feeds") or "").split(",") if x.strip()}
        for t in sorted(ts - declared): print("FEEDS", f, "- a bridge reads it into", t, "but the field's feeds does not say so"); fails += 1
# v2: triggers (rules/triggers.yaml) name defined when_applicable fields with a reason; every when_applicable field has a
# trigger or a rule gate; no trigger is left on a field
triggers = [t for t in yaml.safe_load(open(os.path.join(ROOT, "rules", "triggers.yaml"))) if isinstance(t, dict)]
agenda = yaml.safe_load(open(os.path.join(ROOT, "rules", "derived", "agenda.yaml")))["fields"]
_tf = set()
for t in triggers:
    f = t.get("field")
    if f in _tf: print("TRIGGER", f, "- two triggers for one field"); fails += 1
    _tf.add(f)
    if f not in fields: print("TRIGGER", f, "- not in fields.yaml"); fails += 1; continue
    if fields[f].get("ask_policy") != "when_applicable": print("TRIGGER", f, "- the field is not asked when applicable"); fails += 1
    if not t.get("trigger"): print("TRIGGER", f, "- no condition"); fails += 1
    if not t.get("why"): print("TRIGGER", f, "- no reason"); fails += 1
    for lf in _leaves(t.get("trigger"), []):
        if lf.replace(".value", "").replace(".status", "") not in fields: print("TRIGGER", f, "- condition reads an undefined field", lf); fails += 1
for f, spec in fields.items():
    if "applies_when" in spec: print("TRIGGER", f, "- applies_when left on the field; triggers live in rules/triggers.yaml"); fails += 1
    if spec.get("ask_policy") == "when_applicable" and f not in _tf and not agenda.get(f, {}).get("rule_gates"):
        print("TRIGGER", f, "- asked when applicable but has neither a trigger nor a rule gate"); fails += 1
_opts = {(t.get("field"), t.get("value")): t for t in terms.values() if "value" in t}
for f, spec in fields.items():
    if "value_meanings" in spec: print("VALUES", f, "- value_meanings left on the field; options live in rules/terms.yaml"); fails += 1
    if spec.get("type") == "enum":
        for v in spec.get("values") or []:
            t = _opts.get((f, v))
            if not t: print("VALUES", f, "- value", v, "has no option entry in terms.yaml"); fails += 1
            elif not t.get("definition"): print("VALUES", f, "- option", v, "has no definition"); fails += 1
for (f, v), t in _opts.items():
    if f not in fields or v not in (fields[f].get("values") or []): print("TERM", t["id"], "- an option of a value that no field allows"); fails += 1
for tid, t in terms.items():
    if t.get("kind") not in ("fuzzy", "option"): print("TERM", tid, "- kind must be fuzzy or option"); fails += 1
for f, spec in fields.items():
    g = str(spec.get("gloss") or "").strip()
    if not g: print("GLOSS", f, "- every field needs a gloss (the one-line definition given to fact extraction)"); fails += 1
    elif len(g) > 260 or "issue #" in g or "bridge" in g.lower() or ".yaml" in g: print("GLOSS", f, "- too long or carries file talk"); fails += 1
# v2: terms (rules/terms.yaml): every pointer names a term, every fuzzy term lists its pointers, and the numbers agree
pointers = {}
for f, spec in fields.items():
    for t in spec.get("terms") or []: pointers.setdefault(t, set()).add("field:" + f)
for t in triggers:
    for x in t.get("terms") or []: pointers.setdefault(x, set()).add("trigger:" + t["field"])
for r in crit:
    for x in r.get("terms") or []: pointers.setdefault(x, set()).add("rule:" + r["id"])
for t, ptrs in pointers.items():
    if t not in terms: print("TERM", t, "- pointed at but not in terms.yaml:", sorted(ptrs)); fails += 1
for tid, t in terms.items():
    if t.get("kind") != "fuzzy": continue
    listed = {u for u in (t.get("used_by") or []) if not u.startswith("engine:")}
    if listed != pointers.get(tid, set()): print("TERM", tid, "- used_by disagrees with the pointers:", sorted(listed ^ pointers.get(tid, set()))); fails += 1
    if not (t.get("why") and (t.get("provenance") == "authored" or (t.get("source") and t.get("span")))): print("TERM", tid, "- needs a reason, and a source + span unless authored"); fails += 1
def _age_leaves(w): return [l for l in _leaves_full(w, []) if l.get("field") == "patient.age"]
def _leaves_full(w, out):
    if isinstance(w, dict):
        if "field" in w: out.append(w)
        for k in ("all", "any", "not"):
            if k in w: _leaves_full(w[k], out)
    elif isinstance(w, list):
        for x in w: _leaves_full(x, out)
    return out
def _check_numbers(owner, cond, tids):
    for tid in tids:
        num = terms.get(tid, {}).get("numbers") or {}
        ages = _age_leaves(cond)
        if "age_years_min" in num and tid in ("could_be_pregnant", "elderly") and not any(l.get("gte") == num["age_years_min"] for l in ages):
            print("TERM", tid, "-", owner, "does not carry its lower age", num["age_years_min"]); fails += 1
        if "age_years_max" in num and tid in ("could_be_pregnant", "pediatric") and not any(l.get("lt") == num["age_years_max"] for l in ages):
            print("TERM", tid, "-", owner, "does not carry its upper age", num["age_years_max"]); fails += 1
        if "min_count" in num and not any(l.get("gte") == num["min_count"] for l in _leaves_full(cond, []) if l.get("field") == "complaint.atso_elements_count"):
            print("TERM", tid, "-", owner, "does not carry its count", num["min_count"]); fails += 1
for t in triggers:
    if t.get("terms"): _check_numbers("trigger " + t["field"], t.get("trigger"), t["terms"])
for r in crit:
    if r.get("terms"): _check_numbers("rule " + r["id"], r.get("when"), r["terms"])
bands = [terms[b]["numbers"] for b in ("infant", "child", "adult", "older_adult")]
for a, b in zip(bands, bands[1:]):
    if a.get("age_years_max") != b.get("age_years_min"): print("TERM age bands - not contiguous:", a, b); fails += 1
print(f"terms: {sum(1 for t in terms.values() if t.get('kind') == 'fuzzy')} fuzzy terms and {sum(1 for t in terms.values() if t.get('kind') == 'option')} options checked")
for f, spec in fields.items():
    if spec.get("purpose") and not ((spec.get("source") and spec.get("span")) or spec.get("authored")):
        print("HISTORY", f, "- a field with a purpose needs source and span, or an authored reason"); fails += 1
print(f"bridges: {len(bridges)} entries checked; triggers: {len(triggers)}; history and screening fields with a source or an authored reason: {sum(1 for v in fields.values() if v.get('purpose'))}")
n_rules = sum(1 for r in crit if r.get("when"))
print(f"\n{len(crit)} entries, {n_rules} rule entries; span-verified {sum(1 for _, s in rows if s.startswith('ok'))}; failures {fails}")
sys.exit(1 if fails else 0)
