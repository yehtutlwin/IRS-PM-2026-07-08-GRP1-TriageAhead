"""Number 1 (encoding fidelity) as two sets: the core set, where the fourth edition's answer also holds under the fifth
edition the rules are built from, and the extended set, the cases marked `edition_differs` in the test files, where the
book's answer rests on a criterion the fifth edition changed or dropped (each case's note or xfail says how).
    .venv/bin/python experiments/number1_report.py     -> experiments/out/number1-encoding-fidelity.md
"""
import os, sys, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, "prototype")); import engine  # noqa
cases = yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_cases.yaml"))) + yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_posttest_cases.yaml")))
CRIT = engine.load_criteria()
def cid(c): return f"appA-ch{c['chapter']}-q{c['case']}" if c.get("set")=="appA" else f"{('ch10'+c['set']) if c.get('set') else 'ch9'}-{c['case']}"
def passes(c):
    f = engine.Facts()
    for x in c["facts"]: f.write(x["field"], x["value"], status=x.get("status", "reported"), turn=0)
    engine.derive(f, 0); r = engine.evaluate_tree(f, CRIT); ids = lambda es: {e["id"] for e in es}
    if c["expect"] == "esi1": return not (set(c["expect_rules"]) - ids(r["esi1_indicators"]))
    if c["expect"] == "floor2": return r["floor"] == "at least ESI-2" and not (set(c["expect_rules"]) - ids(r["fired"]))
    return r["floor"] is None and not r["esi1_indicators"]
def level_band(c): v = str(c["v4_answer"]); return v if v in ("1", "2") else "3, 4 or 5"
core, ext, skipped = [], [], []
for c in cases:
    (skipped if c.get("skip") else ext if c.get("edition_differs") else core).append(c)
def rate(n, d): return f"{n} of {d} ({100*n/d:.0f}%)"
L = ["# Number 1: encoding fidelity, core and extended sets", "",
     f"{len(cases)} handbook cases: {len(core)} core (both editions give the same answer), {len(ext)} extended (`edition_differs`), "
     f"{len(skipped)} skipped (decided on vital signs). A case passes when the engine's output matches the book's level as the test expects it.", "",
     "## Core set", "", "| book's level | cases | pass | fail |", "| --- | ---: | ---: | ---: |"]
tot = collections.Counter()
for band in ("1", "2", "3, 4 or 5"):
    cs = [c for c in core if level_band(c) == band]; p = sum(passes(c) for c in cs)
    L.append(f"| {band} | {len(cs)} | {p} | {len(cs) - p} |"); tot["n"] += len(cs); tot["p"] += p
L += [f"| all | {tot['n']} | {tot['p']} | {tot['n'] - tot['p']} |", "", f"**Core result: {rate(tot['p'], tot['n'])} pass.** Failing cases:", ""]
for c in core:
    if not passes(c): L.append(f"- {cid(c)} (book {c['v4_answer']}): {c['synopsis']}. {c.get('xfail') or c.get('note') or ''}")
L += ["", "## Extended set (the fifth edition differs)", "",
      "Judged by the fourth edition's answer the engine passes where the test expects the fifth edition's reading; judged by the fifth edition every case behaves as its note says.", "",
      "| case | book (4th) | 5th edition | test expects | passes |", "| --- | ---: | --- | --- | --- |"]
for c in ext:
    L.append(f"| {cid(c)} | {c['v4_answer']} | {(c.get('v5_answer') or ('no such criterion' if c.get('xfail') else 'see note'))} | {c['expect']} | {'yes' if passes(c) else 'no (fourth-edition answer only)'} |")
L += ["", "Extended cases, in words:", ""] + [f"- {cid(c)}: {c['synopsis']}. {c.get('xfail') or c.get('note')}" for c in ext]
L += ["", "## Skipped", ""] + [f"- {cid(c)}: {c['skip']}" for c in skipped]
os.makedirs(os.path.join(ROOT, "experiments", "out"), exist_ok=True)
open(os.path.join(ROOT, "experiments", "out", "number1-encoding-fidelity.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L[:16]))
