"""Reachability of the practice cases through the interview (knowledge base v2, issue #57; model-free).
For every practice case in tests/, feed its facts to the interview's own selection (engine.open_fields) one at a time,
in the order the interview would ask for them, answering "not known" to every question the case says nothing about.
A fact is REACHED when the interview asked for it. A fact not reached is one of: clinician-only (no caregiver could give
it; expected for level-1 cases), fed through a bridge (the interview asks the everyday-sign fields instead and derives
it; counted as reachable when all its sources are askable), volunteered only (by policy), or NEVER OPENED (a gate kept
the question shut: the finding this check exists for). No model is involved; the result is deterministic.
    .venv/bin/python experiments/reachability.py            writes experiments/out/reachability.md and .json
"""
import os, sys, json, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import engine  # noqa: E402

A = engine.load_agenda()
IDX = yaml.safe_load(open(os.path.join(ROOT, "rules", "derived", "fields-index.yaml")))["fields"]
BR = {b["id"]: b for b in yaml.safe_load(open(os.path.join(ROOT, "rules", "bridges.yaml")))}

def leaves(w, out):
    if isinstance(w, dict):
        if "field" in w: out.append(w["field"].replace(".value", "").replace(".status", ""))
        for k in ("all", "any", "not"):
            if k in w: leaves(w[k], out)
    elif isinstance(w, list):
        for x in w: leaves(x, out)
    return out

def reach(pairs):
    want = dict(pairs); fx = engine.Facts(); got = set(); progress = True
    while progress:
        progress = False
        for o in engine.open_fields(fx, {}):
            f = o["field"]
            if fx.has(f): continue
            if f in want:
                fx.write(f, want[f], status="reported", turn=0); engine.derive(fx, 0); got.add(f); progress = True; break
            fx.write(f, None, status="unknown", turn=0)      # the case says nothing: the caregiver does not know
    out = []
    for f in want:
        if f in got: continue
        if fx.has(f) and (fx.d.get(f) or {}).get("who") == "derived": out.append((f, "derived", "")); continue   # the engine derived it from another fact
        e = A.get(f)
        srcs = sorted({s for b in IDX.get(f, {}).get("fed_by_bridge", []) for s in leaves(BR[b].get("when"), [])})
        if srcs and all(A.get(s, {}).get("ask_policy") in ("always", "when_applicable") for s in srcs): out.append((f, "through a bridge", ", ".join(srcs))); continue
        if f.startswith("vitals."): out.append((f, "measurement", "")); continue   # given by the case; the interview asks for it only when a complaint calls for it
        if e is None: out.append((f, "clinician-only", ""))
        elif e["ask_policy"] == "volunteered_only": out.append((f, "volunteered only", ""))
        else: out.append((f, "never opened", "trigger" if e.get("trigger") is not None else "rule gate: " + ", ".join(e.get("rule_gates", []))))
    return out

def load_cases():
    cases = []
    for n in ("v4_cases.yaml", "v4_posttest_cases.yaml"):
        for c in yaml.safe_load(open(os.path.join(ROOT, "tests", n))):
            if c.get("skip"): continue
            cid = f"appA ch{c['chapter']} q{c['case']}" if c.get("set") == "appA" else f"ch10 {c['set']} {c['case']}" if c.get("set") else f"ch9 {c['case']}"
            cases.append((cid, [(f["field"], f["value"]) for f in c["facts"]], [f for f in c["facts"] if f["field"] == "complaint.category"]))
    return cases

def run():
    cases = load_cases(); rows = []; cnt = collections.Counter(); per = collections.Counter(); examples = {}
    full = clean = 0
    for cid, pairs, cats in cases:
        u = reach(pairs); kinds = {k for _, k, _ in u}
        full += not u; clean += not ({"never opened", "volunteered only"} & kinds)
        for f, k, d in u:
            cnt[k] += 1; per[(f, k)] += 1; examples.setdefault((f, k), (cid, [c["value"] for c in cats]))
        rows.append({"case": cid, "facts": len(pairs), "not_reached": [{"field": f, "why": k, "detail": d} for f, k, d in u]})
    return cases, rows, cnt, per, examples, full, clean

if __name__ == "__main__":
    cases, rows, cnt, per, examples, full, clean = run()
    out = os.path.join(ROOT, "experiments", "out"); os.makedirs(out, exist_ok=True)
    json.dump({"cases": len(cases), "every_fact_askable": full, "only_clinician_or_bridge_missing": clean, "by_kind": dict(cnt), "rows": rows}, open(os.path.join(out, "reachability.json"), "w"), indent=1)
    L = ["# Reachability of the practice cases through the interview (model-free)", "",
         "For each practice case the interview's own selection (`engine.open_fields` on the derived agenda) is fed the case's facts one at a time, "
         "in the order it would ask for them; every question the case says nothing about is answered \"not known\". Generated by `experiments/reachability.py`.", "",
         f"Cases: {len(cases)}. Every fact askable: {full}. Nothing missing except clinician-only or bridge-fed facts: {clean}.", "",
         "| Not reached because | Facts |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in cnt.most_common()]
    L += ["", "## Never opened: a gate kept the question shut", "", "| times | field | gate | example case (its complaint categories) |", "| ---: | --- | --- | --- |"]
    L += [f"| {n} | {f} | {next(d for r in rows for x in r['not_reached'] if x['field']==f and x['why']==k for d in [x['detail']])} | {examples[(f,k)][0]} ({', '.join(map(str, examples[(f,k)][1])) or 'no category given'}) |"
          for (f, k), n in sorted(per.items(), key=lambda x: -x[1]) if k == "never opened"]
    L += ["", "## Volunteered only (by policy)", "", "| times | field |", "| ---: | --- |"] + [f"| {n} | {f} |" for (f, k), n in sorted(per.items(), key=lambda x: -x[1]) if k == "volunteered only"]
    L += ["", "## Reading it", "", "- *Measurement*: a vital sign the case states; before arrival the interview asks for one only when a complaint calls for it (a temperature with fever), so these are not counted against the gates.",
          "- *Clinician-only* facts are expected: level-1 cases rest on what a clinician sees or measures; the interview was never meant to collect them.",
          "- *Through a bridge*: the case states the clinical fact; the interview asks the everyday-sign fields and derives it. Counted as reachable.",
          "- *Never opened* is the finding: either the gate is too narrow, or the case's facts lack what the gate needs (many practice cases carry no complaint category, or a category outside the field file's list), which is a test-case problem (#67, #68), not a gate problem. The example column tells the two apart."]
    open(os.path.join(out, "reachability.md"), "w").write("\n".join(L) + "\n")
    print(f"cases {len(cases)} | every fact askable {full} | clean {clean} | {dict(cnt)}")
