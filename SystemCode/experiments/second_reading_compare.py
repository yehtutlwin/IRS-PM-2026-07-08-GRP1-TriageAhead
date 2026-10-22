"""Compare the second reading of the practice cases (experiments/second_reading.py) with our test cases, field by field,
and say where the difference changes the rule engine's outcome. Writes experiments/out/second-reading-<label>.md/.json.
    .venv/bin/python experiments/second_reading_compare.py <second-reading.json> <label>
"""
import os, sys, json, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype")); import engine  # noqa: E402
theirs = json.load(open(sys.argv[1])); label = sys.argv[2]
F = yaml.safe_load(open(os.path.join(ROOT, "rules", "fields.yaml")))["fields"]
ours = {}
for c in yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_cases.yaml"))):
    ours[("A-" if c.get("set") == "A" else "B-" if c.get("set") == "B" else "ch9-") + str(c["case"])] = c
for c in yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_posttest_cases.yaml"))):
    ours[f"appA-ch{c['chapter']}-q{c['case']}"] = c
CRIT = engine.load_criteria()
def outcome(facts):
    fx = engine.Facts()
    for f in facts:
        if f.get("field") in F or f.get("field", "").startswith("complaint."):
            fx.write(f["field"], f.get("value"), status=f.get("status") or "reported", turn=0)
    engine.derive(fx, 0); t = engine.evaluate_tree(fx, CRIT)
    return "esi1" if t["esi1_indicators"] else "floor2" if t["floor"] else "none", sorted(r["id"] for r in t["fired"] + t["esi1_indicators"])
SYN = {"htn": "hypertension", "high blood pressure": "hypertension", "dm": "diabetes", "type 2 diabetes": "diabetes", "diabetes mellitus": "diabetes",
       "copd": "chronic obstructive pulmonary disease", "afib": "atrial fibrillation", "a-fib": "atrial fibrillation", "mi": "myocardial infarction",
       "heart attack": "myocardial infarction", "ckd": "chronic renal failure", "chronic kidney disease": "chronic renal failure", "asa": "aspirin"}
def _word(s):
    s = str(s).strip().lower().rstrip(".")
    return SYN.get(s, s)
def norm(v):
    """Values compared loosely: case and spacing ignored; list items reduced to common clinical synonyms and order ignored;
    an empty list and a 'none' statement are the same."""
    if isinstance(v, str): return SYN.get(v.strip().lower(), v.strip().lower())
    if isinstance(v, list): return sorted(set(_word(x) for x in v if str(x).strip().lower() not in ("none", "nil", "no")))
    return v
rows = []; agg = collections.Counter(); per_field = collections.Counter(); outcome_changes = []
for cid, c in ours.items():
    if cid not in theirs: continue
    mine = {f["field"]: f for f in c["facts"]}; other = {f["field"]: f for f in theirs[cid]["facts"] if isinstance(f, dict) and f.get("field")}
    unknown_fields = sorted(f for f in other if f not in F)
    both = sorted(set(mine) & set(other)); only_mine = sorted(set(mine) - set(other)); only_theirs = sorted(f for f in set(other) - set(mine) if f in F)
    agree = [f for f in both if norm(mine[f].get("value")) == norm(other[f].get("value")) or (f == "complaint.text")]
    differ = [f for f in both if f not in agree]
    for f in only_mine: per_field[(f, "only ours")] += 1
    for f in only_theirs: per_field[(f, "only theirs")] += 1
    for f in differ: per_field[(f, "value differs")] += 1
    agg["agree"] += len(agree); agg["value differs"] += len(differ); agg["only ours"] += len(only_mine); agg["only theirs"] += len(only_theirs); agg["theirs, no such field"] += len(unknown_fields)
    o_mine, r_mine = outcome(c["facts"]); o_theirs, r_theirs = outcome(theirs[cid]["facts"])
    if o_mine != o_theirs: outcome_changes.append((cid, o_mine, o_theirs, c.get("expect"), r_mine, r_theirs))
    rows.append({"case": cid, "agree": agree, "value_differs": {f: [mine[f].get("value"), other[f].get("value")] for f in differ}, "only_ours": only_mine, "only_theirs": {f: other[f].get("value") for f in only_theirs},
                 "no_such_field": unknown_fields, "outcome_ours": o_mine, "outcome_theirs": o_theirs})
json.dump({"label": label, "cases": len(rows), "totals": dict(agg), "outcome_changes": outcome_changes, "rows": rows}, open(os.path.join(ROOT, "experiments", "out", f"second-reading-{label}.json"), "w"), indent=1)
L = [f"# Second reading of the practice cases ({label}) against our test cases", "",
     f"Cases compared: {len(rows)} of {len(ours)}. A second model read each printed case with the field list and no sight of our files (`experiments/second_reading.py`); this compares the two fact sets (`experiments/second_reading_compare.py`).", "",
     "| Facts | Count |", "| --- | ---: |"] + [f"| {k} | {v} |" for k, v in agg.most_common()]
L += ["", f"## Cases where the outcome under the rule engine differs ({len(outcome_changes)})", "", "| case | ours | theirs | our expectation | rules (ours) | rules (theirs) |", "| --- | --- | --- | --- | --- | --- |"]
L += [f"| {cid} | {a} | {b} | {e} | {', '.join(r1)} | {', '.join(r2)} |" for cid, a, b, e, r1, r2 in outcome_changes]
L += ["", "## Fields most often different", "", "| field | kind | cases |", "| --- | --- | ---: |"] + [f"| {f} | {k} | {n} |" for (f, k), n in per_field.most_common(40)]
L += ["", "## Reading it", "", "- *agree*: same field, same value. *value differs*: both wrote the field with different values; the per-case JSON lists both.",
      "- *only ours* / *only theirs*: a fact one reading wrote and the other did not; a person decides which reading the book supports.",
      "- *theirs, no such field*: the model used a name outside the field file; ignored for the outcome, listed per case.",
      "- An outcome change is where the two fact sets lead the rule engine to a different class (ESI-1 indicator, floor, none); these are read first."]
open(os.path.join(ROOT, "experiments", "out", f"second-reading-{label}.md"), "w").write("\n".join(L) + "\n")
print(dict(agg), "outcome changes:", len(outcome_changes))
