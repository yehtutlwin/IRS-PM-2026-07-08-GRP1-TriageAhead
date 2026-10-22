"""Put several blind re-extractions next to the current rules file, one row per firing rule of ours.
    .venv/bin/python rules/extraction/compare_blind_re_extractions.py label=path/to/rules.yaml [label=path ...] [--out DIR]
Same matching as compare_blind.py: a blind re-extraction's entry is about one of our statements (rules/extraction/v5-complete-pass.yaml)
when both are on the same printed page and their quotes overlap. Through the statement we reach our rule. For each of our
firing rules the table shows what each blind re-extraction made of the same sentence: the effect it gave (assign, consider, reassess),
or that it filed the sentence as something that is not a rule (context, example, definition), or that it has no entry.
A second table lists sentences that two or more blind re-extractions made a rule of and that no statement of ours covers.
Writes <out>/blind-re-extractions-comparison.md and .json.
"""
import os, re, sys, json, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
args = [a for a in sys.argv[1:] if "=" in a]
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(ROOT, "rules", "extraction")
def norm(s):
    s = str(s).lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"[\s\-]+", " ", s).strip()
toks = lambda s: [t for t in re.findall(r"[a-z0-9<>%°]+", norm(s)) if len(t) > 1]
def overlap(a, b):
    na, nb = norm(a), norm(b)
    if na in nb or nb in na: return 1.0
    ta, tb = toks(a), toks(b)
    if not ta or not tb: return 0.0
    best = 0; prev = [0] * (len(tb) + 1)
    for x in ta:
        cur = [0] * (len(tb) + 1)
        for j, y in enumerate(tb, 1):
            if x == y: cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best / min(len(ta), len(tb))
TH = 0.6
def page(e):
    try: return int(e["page"])
    except Exception: return -1
SHORT = {"assign_level_1": "assign 1", "assign_level_2": "assign 2", "consider_level_2": "consider 2", "consider_level_1": "consider 1",
         "reassess_uptriage": "reassess", "resource_band": "resources", "none": "no effect"}
RANK = ["assign 1", "assign 2", "consider 1", "consider 2", "reassess", "resources"]
def our_effect(r):
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "consider": return "consider 2"
    if eo == "reassess_uptriage_consider" or dp == "D": return "reassess"
    return {"A": "assign 1", "B": "assign 2"}.get(dp, "no effect")

R = {e["id"]: e for e in yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml")))}
ST = yaml.safe_load(open(os.path.join(ROOT, "rules", "extraction", "v5-complete-pass.yaml")))["statements"]
st_rules = lambda s: [x for x in (s.get("rules") or []) + [s.get("rule"), s.get("proposal")] if x in R]
readers = collections.OrderedDict()
for a in args:
    label, path = a.split("=", 1)
    readers[label] = [e for e in yaml.safe_load(open(path))["entries"] if e.get("span")]

verdict = {}                                     # (rule id, label) -> {"effects": [...], "kinds": [...], "ids": [...], "interp": [...]}
unmatched = {}                                   # label -> rule entries with no statement of ours
for label, B in readers.items():
    unmatched[label] = []
    for b in B:
        hit = [s for s in ST if page(b) == int(s["page"]) and overlap(b["span"], s["span"]) >= TH]
        if not hit and b.get("kind") == "rule": unmatched[label].append(b)
        for s in hit:
            for rid in st_rules(s):
                v = verdict.setdefault((rid, label), {"effects": [], "kinds": [], "ids": [], "interp": []})
                v["ids"].append(b["id"])
                if b.get("kind") == "rule" or b.get("effect") in ("assign_level_1", "assign_level_2", "consider_level_1", "consider_level_2", "reassess_uptriage"):  # an example that carries a level counts as that level
                    v["effects"].append(SHORT.get(b.get("effect"), str(b.get("effect")))); v["interp"].append(b.get("interpretation"))
                else: v["kinds"].append(str(b.get("kind")))
def cell(v):
    if not v: return "no entry"
    if v["effects"]:
        effs = sorted(set(v["effects"]), key=lambda x: RANK.index(x) if x in RANK else 99)
        s = " / ".join(effs)
        if any(i in ("effect_inferred", "interpreted") for i in v["interp"]) and not any(i == "verbatim" for i in v["interp"]): s += " (inferred)"
        return s
    return "not a rule (" + ", ".join(sorted(set(v["kinds"]))) + ")"
def agrees(ours, c):
    if c == "no entry": return None
    return ours in c.replace(" (inferred)", "").split(" / ")
rows = []
for rid, r in R.items():
    if not r.get("when"): continue
    ours = our_effect(r); cells = {l: cell(verdict.get((rid, l))) for l in readers}
    ag = {l: agrees(ours, c) for l, c in cells.items()}
    rows.append({"rule": rid, "ours": ours, "readers": cells, "agree": sum(1 for x in ag.values() if x), "weaker_or_different": [l for l, x in ag.items() if x is False],
                 "silent": [l for l, x in ag.items() if x is None], "title": r.get("title") or r.get("name") or ""})

# sentences several readers made a rule of, that we have no statement for
cl = []                                          # clusters of unmatched rule entries across readers
for label, es in unmatched.items():
    for b in es:
        for c in cl:
            if c["page"] == page(b) and overlap(c["span"], b["span"]) >= TH: c["by"].setdefault(label, []).append(b); break
        else: cl.append({"page": page(b), "span": b["span"], "by": {label: [b]}})
shared = sorted([c for c in cl if len(c["by"]) >= 2], key=lambda c: (-len(c["by"]), c["page"]))

json.dump({"readers": {l: len(b) for l, b in readers.items()}, "rows": rows,
           "unmatched_rule_entries": {l: len(v) for l, v in unmatched.items()},
           "shared_only_in_readers": [{"page": c["page"], "span": c["span"], "by": {l: [{"id": b["id"], "effect": b.get("effect"), "interpretation": b.get("interpretation")} for b in bs] for l, bs in c["by"].items()}} for c in shared]},
          open(os.path.join(OUT, "blind-re-extractions-comparison.json"), "w"), indent=1)
labels = list(readers)
contested = [r for r in rows if r["weaker_or_different"]]
L = ["# The current rules file next to the blind re-extractions, rule by rule", "",
     "Blind re-extractions: " + ", ".join(f"{l} ({n} entries)" for l, n in ((l, len(b)) for l, b in readers.items())) + ".",
     f"Matching: same printed page and overlapping quote (longest common run of words at least {int(TH*100)}% of the shorter quote).",
     "A cell shows what that blind re-extraction made of the sentence(s) our rule rests on. \"(inferred)\" means the model marked the level as its own inference, not the handbook's words.", "",
     f"Firing rules of ours: {len(rows)}. Every blind re-extraction that has an entry agrees with our effect: {sum(1 for r in rows if not r['weaker_or_different'] and r['agree'])}. "
     f"At least one blind re-extraction gives a different effect or files the sentence as not a rule: {len(contested)}. No blind re-extraction has an entry: {sum(1 for r in rows if not r['agree'] and not r['weaker_or_different'])}.", "",
     "## Rules where at least one blind re-extraction differs", "", "| rule | ours | " + " | ".join(labels) + " | re-extractions differing |", "| --- | --- | " + " | ".join("---" for _ in labels) + " | ---: |"]
L += [f"| {r['rule']} | {r['ours']} | " + " | ".join(r["readers"][l] for l in labels) + f" | {len(r['weaker_or_different'])} of {len(labels) - len(r['silent'])} |" for r in sorted(contested, key=lambda r: -len(r["weaker_or_different"]))]
L += ["", "## Rules where every blind re-extraction with an entry agrees", "", "| rule | ours | " + " | ".join(labels) + " |", "| --- | --- | " + " | ".join("---" for _ in labels) + " |"]
L += [f"| {r['rule']} | {r['ours']} | " + " | ".join(r["readers"][l] for l in labels) + " |" for r in rows if not r["weaker_or_different"]]
L += ["", "## Sentences two or more blind re-extractions made a rule of, with no statement of ours", "", "| page | re-extractions | effects | quote |", "| ---: | --- | --- | --- |"]
L += [f"| {c['page']} | {', '.join(c['by'])} | " + "; ".join(f"{l}: {SHORT.get(bs[0].get('effect'), bs[0].get('effect'))}" for l, bs in c["by"].items()) + f" | {str(c['span'])[:150]} |" for c in shared]
open(os.path.join(OUT, "blind-re-extractions-comparison.md"), "w").write("\n".join(L) + "\n")
print("rules", len(rows), "contested", len(contested), "shared only-in-readers", len(shared), {l: len(v) for l, v in unmatched.items()})
