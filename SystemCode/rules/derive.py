"""Derive, from the extracted rules and the field file, what is known about each field and what the interview may ask.
No judgement, no model: run it twice, get the same files. Knowledge base and extraction design v2 (issues #55, #57).
Writes two files that must never be edited by hand:
  rules/derived/fields-index.yaml   for each field: which rules read it, who can supply it, bridges, comparisons
  rules/derived/agenda.yaml         for each field a caregiver can answer: priority, how it may be asked, its gates
    .venv/bin/python rules/derive.py            regenerate both
    .venv/bin/python rules/derive.py --check    exit 1 if a file on disk is out of date or a field is undefined or unused
"""
import os, sys, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_INDEX = os.path.join(ROOT, "rules", "derived", "fields-index.yaml")
OUT_AGENDA = os.path.join(ROOT, "rules", "derived", "agenda.yaml")
load = lambda *p: yaml.safe_load(open(os.path.join(ROOT, *p)))
base = lambda f: f.replace(".value", "").replace(".status", "")

def leaves(w, out):
    if isinstance(w, dict):
        if "field" in w: out.append(w)
        for k in ("all", "any", "not"):
            if k in w: leaves(w[k], out)
    elif isinstance(w, list):
        for x in w: leaves(x, out)
    return out

def effect_of(r):
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "context_note": return "context_note"
    if eo == "consider": return "consider"
    if eo == "reassess_uptriage_consider" or dp == "D": return "reassess"
    return {"A": "assign_1", "B": "assign_2"}.get(dp, "none")

def build():
    rules = [e for e in load("rules", "criteria.yaml") if isinstance(e, dict) and e.get("when")]
    bridges = load("rules", "bridges.yaml")
    fields = load("rules", "fields.yaml")["fields"]
    triggers = {t["field"]: t["trigger"] for t in load("rules", "triggers.yaml") if isinstance(t, dict)}   # authored, with reasons
    blank = lambda: {"read_by": [], "assessed_via": [], "compared": [], "fed_by_bridge": [], "feeds_through_bridge": []}
    idx = collections.OrderedDict((f, blank()) for f in fields)
    used = set(); rule_by_id = {r["id"]: r for r in rules}
    for r in rules:
        for lf in leaves(r["when"], []):
            f = base(lf["field"]); used.add(f); e = idx.setdefault(f, blank())
            if r["id"] not in e["read_by"]: e["read_by"].append(r["id"])
            if r["assessed_via"] not in e["assessed_via"]: e["assessed_via"].append(r["assessed_via"])
            for k, v in lf.items():
                if k == "field": continue
                c = f"{k} {v}" + (f" ({lf['field'].split('.')[-1]})" if lf["field"] != f else "")
                if c not in e["compared"]: e["compared"].append(c)
    bridge_target = {}                                   # lay field -> clinical fields it feeds
    for b in bridges:
        t = base(b["target"]); used.add(t)
        if t in idx and b["id"] not in idx[t]["fed_by_bridge"]: idx[t]["fed_by_bridge"].append(b["id"])
        for lf in leaves(b.get("when"), []) + [{"field": f} for f in b.get("count", [])]:   # a count bridge lists its fields
            f = base(lf["field"]); used.add(f)
            if f in idx and b["id"] not in idx[f]["feeds_through_bridge"]: idx[f]["feeds_through_bridge"].append(b["id"])
            bridge_target.setdefault(f, set()).add(t)
    gate_refs = collections.Counter()                    # field -> how many other fields' triggers mention it
    for f, spec in fields.items():
        for lf in leaves(triggers.get(f), []):
            g = base(lf["field"]); used.add(g)
            if g != f: gate_refs[g] += 1
    out = collections.OrderedDict()
    for f, e in idx.items():
        e["assessed_via"] = sorted(e["assessed_via"])
        e["askable"] = "reported" in e["assessed_via"]   # some rule tagged reported reads it
        e["rule_fed"] = bool(e["read_by"])
        out[f] = {k: v for k, v in e.items() if v not in ([], None)} | {"askable": e["askable"], "rule_fed": e["rule_fed"]}
    missing = sorted(used - set(fields)); unused = sorted(set(fields) - used - {f for f, s in fields.items() if s.get("purpose")})

    # ---- the agenda: one entry per field the interview may raise
    agenda = collections.OrderedDict(); order = 0
    for f, spec in fields.items():
        order += 1
        e = out.get(f, {})
        wanting = list(e.get("read_by", []))
        for t in sorted(bridge_target.get(f, ())):       # a lay field wants what its clinical target's rules want
            for rid in out.get(t, {}).get("read_by", []):
                if rid not in wanting: wanting.append(rid)
        effects = {effect_of(rule_by_id[rid]) for rid in wanting}
        caregiver = e.get("askable") or bool(spec.get("ask")) or bool(spec.get("purpose")) or f in bridge_target
        if not caregiver or spec.get("alias_of"): continue   # clinician-only finding or measurement, or an alias: not in the agenda
        # priority: 0 danger screen · 1 gate (3+ other fields wait on it) · 2 feeds a rule that assigns a level ·
        # 3 feeds only consider flags or context notes · 4 history and identity, no rule
        if f.startswith("danger_signs."): prio = 0
        elif gate_refs[f] >= 3: prio = 1
        elif effects & {"assign_1", "assign_2"}: prio = 2
        elif effects: prio = 3
        else: prio = 4
        # gates: a rule reading this field whose other leaves exist gives a derived gate (the field opens when that
        # rule is still possible and one of its other facts is known); an authored trigger (rules/triggers.yaml) overrides it
        rule_gated = [rid for rid in wanting if len({base(l["field"]) for l in leaves(rule_by_id[rid]["when"], [])} - {f}) > 0]
        policy = spec.get("ask_policy") or ("when_applicable" if (triggers.get(f) or rule_gated) else "volunteered_only")
        if not spec.get("ask") and policy != "volunteered_only": policy, no_ask = "volunteered_only", True   # no everyday wording: never asked unprompted
        else: no_ask = False
        confirm = [rid for rid in wanting if any(l["field"] == f + ".status" and l.get("equals") == "confirmed" for l in leaves(rule_by_id[rid]["when"], []))]
        entry = {"priority": prio, "rank": (len(wanting) and -len(wanting) or 0) if prio else 0, "order": order, "ask_policy": policy,   # the danger screen keeps its authored (ESI) order
                 "wanted_by": wanting, "effects": sorted(effects), "ask": spec.get("ask") or spec["gloss"]}
        if triggers.get(f): entry["trigger"] = triggers[f]
        elif policy == "when_applicable": entry["rule_gates"] = rule_gated
        if confirm: entry["confirm_for"] = confirm
        if not spec.get("ask_policy") or no_ask: entry["policy_default"] = True
        if spec.get("asked_with"): entry["asked_with"] = spec["asked_with"]
        agenda[f] = entry
    for f, e in agenda.items():                          # asked_with: the group goes where its most important member goes
        anc = agenda.get(e.get("asked_with"))
        if anc and e["priority"] < anc["priority"]: anc["priority"], anc["rank"] = e["priority"], min(anc["rank"], e["rank"])
    for f, e in agenda.items():                          # ... and each follower takes the anchor's place, just after it
        anc = agenda.get(e.get("asked_with"))
        if anc: e["priority"], e["rank"], e["order"] = anc["priority"], anc["rank"], anc["order"] + 0.5
    ranked = sorted(agenda.items(), key=lambda kv: (kv[1]["priority"], kv[1]["rank"], kv[1]["order"]))
    agenda = collections.OrderedDict((f, {k: v for k, v in e.items() if k not in ("rank", "order")} | {"position": i + 1}) for i, (f, e) in enumerate(ranked))
    pol = collections.Counter(e["ask_policy"] for e in agenda.values())
    counts = {"fields": len(out), "read_by_a_rule": sum(1 for e in out.values() if e["rule_fed"]), "askable": sum(1 for e in out.values() if e["askable"]),
              "in_agenda": len(agenda), "asked_of_everyone": pol["always"], "asked_when_applicable": pol["when_applicable"], "volunteered_only": pol["volunteered_only"],
              "gated_by_a_rule_only": sum(1 for e in agenda.values() if e.get("rule_gates")), "with_an_authored_trigger": sum(1 for e in agenda.values() if e.get("trigger")),
              "confirmations": sum(1 for e in agenda.values() if e.get("confirm_for"))}
    return out, agenda, counts, missing, unused

def render_index(out, counts):
    head = ("# rules/derived/fields-index.yaml - DERIVED DETERMINISTICALLY by rules/derive.py. DO NOT EDIT: regenerate.\n"
            "# For each field in rules/fields.yaml: which rules read it, who can supply it (from the rules' assessed_via tag),\n"
            "# the comparisons the rules make, and the bridges that feed it or that it feeds.\n"
            "# askable = at least one rule tagged 'reported' reads the field.  rule_fed = at least one rule reads it.\n")
    return head + yaml.safe_dump({"counts": {k: v for k, v in counts.items() if k in ("fields", "read_by_a_rule", "askable")}, "fields": dict(out)}, sort_keys=False, allow_unicode=True, width=140)

def render_agenda(agenda, counts):
    head = ("# rules/derived/agenda.yaml - DERIVED DETERMINISTICALLY by rules/derive.py. DO NOT EDIT: regenerate.\n"
            "# What the interview may ask, in order. One entry per field a caregiver can answer (a rule tagged reported reads it,\n"
            "# it feeds such a rule through a bridge, or the field file gives it a purpose). Replaces the control part of the v1\n"
            "# question file and the v1 agenda-rules file. The program (prototype/engine.py, open_fields) reads this at run time.\n"
            "# priority: 0 danger screen (danger_signs) · 1 gate, three or more other fields wait on it · 2 feeds a rule that assigns a\n"
            "#   level · 3 feeds only consider flags or context notes · 4 history and identity, no rule reads it.\n"
            "# position: the order within and across priorities (more wanting rules first, then field-file order).\n"
            "# ask_policy: always = asked of every patient · when_applicable = asked when its trigger holds (authored, in rules/triggers.yaml\n"
            "#   file) or, with rule_gates only, when one of those rules is still possible and another of its facts is already known ·\n"
            "#   volunteered_only = never asked unprompted; the extraction step may still write it. policy_default: true means the\n"
            "#   field file set no policy and the default applied.\n"
            "# confirm_for: a rule needs this fact confirmed; a confirmation question is due while its status is probable.\n")
    return head + yaml.safe_dump({"counts": {k: v for k, v in counts.items() if k not in ("fields", "read_by_a_rule", "askable")}, "fields": dict(agenda)}, sort_keys=False, allow_unicode=True, width=140)

if __name__ == "__main__":
    out, agenda, counts, missing, unused = build(); ti, ta = render_index(out, counts), render_agenda(agenda, counts)
    if "--check" in sys.argv:
        stale = [p for p, t in ((OUT_INDEX, ti), (OUT_AGENDA, ta)) if not os.path.exists(p) or open(p).read() != t]
        if missing: print("fields used but not defined in rules/fields.yaml:", missing)
        if unused: print("fields defined in rules/fields.yaml but used nowhere:", unused)
        for p in stale: print(os.path.relpath(p, ROOT), "is out of date: run rules/derive.py")
        sys.exit(0 if not (stale or missing or unused) else 1)
    os.makedirs(os.path.dirname(OUT_INDEX), exist_ok=True); open(OUT_INDEX, "w").write(ti); open(OUT_AGENDA, "w").write(ta)
    print(counts); print("missing from fields.yaml:", missing); print("defined but unused:", unused)
