"""Check rules/extraction/v5-complete-pass.yaml mechanically: every span is on its printed page of the handbook, every
rule id it names exists, and report which existing rules no statement supports. Exit 1 on a span or id failure.
    .venv/bin/python rules/extraction/check_pass.py"""
import os, re, sys, collections, yaml, pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); OFFSET = 6
def norm(s):
    s = str(s).lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"[\s\-]+", " ", s).strip()
doc = pymupdf.open(os.path.join(ROOT, "sources", "ESI-Handbook-5th-Edition-3-2023.pdf"))
pages = {i + 1 - OFFSET: norm(doc[i].get_text()) for i in range(len(doc)) if i + 1 - OFFSET >= 1}
crit = yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml"))); ids = {e["id"]: e for e in crit}
st = yaml.safe_load(open(os.path.join(ROOT, "rules", "extraction", "v5-complete-pass.yaml")))["statements"]
fails = 0; supported = collections.Counter()
for s in st:
    if norm(s["span"]) not in pages.get(s["page"], ""):
        where = [p for p, t in pages.items() if norm(s["span"]) in t]
        print(f"SPAN #{s['n']} not on p.{s['page']} (found on {where or 'no page'}): {s['span'][:70]}"); fails += 1
    for r in s.get("rules", []) + ([s["rule"]] if s.get("rule") else []):
        if r not in ids: print(f"ID #{s['n']}: unknown rule {r}"); fails += 1
        else: supported[r] += 1
    if s.get("proposal") in ids: supported[s["proposal"]] += 1      # a proposal that has since been added to the rulebook
unsupported = [i for i, e in ids.items() if i not in supported]
disp = collections.Counter(s["disposition"] for s in st)
print(f"\n{len(st)} statements; by disposition: {dict(disp)}")
print(f"existing entries supported by at least one statement: {len(ids) - len(unsupported)} of {len(ids)}")
print("existing entries with no supporting statement:", [(i, ids[i].get('provenance')) for i in unsupported])
props = sorted({s["proposal"] for s in st if s["disposition"] == "new"})
print("proposals now in the rulebook:", [p for p in props if p in ids])
print("proposals not in the rulebook (candidates awaiting review):", [p for p in props if p not in ids])
print("failures:", fails); sys.exit(1 if fails else 0)
