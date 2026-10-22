"""The sheet check of the evaluation plan (issue #32): run the rule engine on each persona answer sheet's facts (`truth`) and
compare with the persona author's expected floor and rules, before any interview run. A disagreement is a rule gap, an author
error or a handbook ambiguity, and is settled here, not at run time; after this a run-time miss can only be a missing fact or
a model error.    .venv/bin/python experiments/sheet_check.py  -> experiments/out/sheet-check.md
"""
import os, sys, time, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, "prototype")); import engine  # noqa
personas = yaml.safe_load(open(os.path.join(ROOT, "prototype", "personas.yaml"))); CRIT = engine.load_criteria()
FIELDS = engine.load_fields(); rows = []; agree = 0
for p in personas:
    f = engine.Facts(); unknown = []
    for k, v in (p.get("truth") or {}).items():
        if k not in FIELDS: unknown.append(k); continue
        if v == "absent": continue
        f.write(k, v, status="confirmed" if k == "M.anticoagulant" else "reported", turn=0)
    engine.derive(f, 0); t = engine.evaluate_tree(f, CRIT)
    floor = "ESI-1" if t["esi1_indicators"] else t["floor"]; exp = p.get("expect_floor")
    fired = [r["id"] for r in t["fired"]] + [r["id"] for r in t["esi1_indicators"]]
    ok_floor = (floor == exp) or (exp == "at least ESI-2" and floor == "ESI-1")
    ok_rules = all(any(e == r for r in fired) for e in (p.get("expect_rules") or []) if not e.startswith("synthetic."))
    kind = "" if ok_floor and ok_rules else ("facts with no field (synthetic persona): a schema gap, recorded, not a rule gap" if unknown else "see note")
    agree += bool(ok_floor and ok_rules)
    rows.append((p["id"], exp or "none", floor or "none", ", ".join(p.get("expect_rules") or []) or "-", ", ".join(fired) or "-", "yes" if ok_floor and ok_rules else "NO", ", ".join(unknown) or "-", kind))
L = [f"# Sheet check: the rule engine on each persona answer sheet ({time.strftime('%Y-%m-%d %H:%M')})", "",
     "The engine is given the sheet's `truth` facts directly (the anticoagulant as confirmed, the rest as reported) and its floor and fired rules are compared with the author's expectation. "
     f"Agreement: {agree} of {len(personas)}.", "",
     "| persona | expected floor | engine floor | expected rules | fired | agree | truth fields with no schema field | kind |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
L += ["| " + " | ".join(r) + " |" for r in rows]
L += ["", "Notes. The two synthetic personas (heat stroke, liver disease) name rules that do not exist and facts no field holds; they were written to show the schema's edge and are kept as such, so their disagreement is a recorded schema gap, not a rule gap. "
      "The breathing persona's sheet states (since 16 Oct 2026) that the breathing is not getting worse, so no floor is expected and none fires."]
os.makedirs(os.path.join(ROOT, "experiments", "out"), exist_ok=True); open(os.path.join(ROOT, "experiments", "out", "sheet-check.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L[4:]))
