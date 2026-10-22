"""Compare a blind extraction run with the current rules file, sentence by sentence.
    .venv/bin/python rules/extraction/compare_blind.py <blind rules.yaml> <label> [--out DIR]
Matching key: the quoted handbook text. A blind entry and one of our statements (rules/extraction/v5-complete-pass.yaml)
are about the same sentence when they are on the same printed page and their quotes overlap. Through the statement we
reach the rule(s) of rules/criteria.yaml it supports. Then, for each matched pair of rules, compare what can be compared
without aligning fact names: decision point, effect, who can supply the facts, how many facts, how they are joined, and
the numbers. Fact names are listed side by side for a person to read. Writes <out>/blind-comparison-<label>.md and .json.
"""
import os, re, sys, json, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
blind_path, label = sys.argv[1], sys.argv[2]
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
    # longest common run of tokens, relative to the shorter quote
    best = 0; prev = [0] * (len(tb) + 1)
    for x in ta:
        cur = [0] * (len(tb) + 1)
        for j, y in enumerate(tb, 1):
            if x == y: cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best / min(len(ta), len(tb))

blind = yaml.safe_load(open(blind_path)); B = blind["entries"]; BF = {f["name"]: f for f in blind.get("facts", [])}
ours = yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml"))); R = {e["id"]: e for e in ours}
ST = yaml.safe_load(open(os.path.join(ROOT, "rules", "extraction", "v5-complete-pass.yaml")))["statements"]

def leaves(w, out, path="all"):
    if isinstance(w, dict):
        if "fact" in w or "field" in w: out.append((w, path))
        for k in ("all", "any", "not"):
            if k in w: leaves(w[k], out, k)
    elif isinstance(w, list):
        for x in w: leaves(x, out, path)
    return out
def shape(w):
    ls = leaves(w, [])
    facts = sorted({(l.get("fact") or l.get("field")).replace(".value", "").replace(".status", "") for l, _ in ls})
    nums = sorted({float(v) for l, _ in ls for k, v in l.items() if k in ("gte", "gt", "lt", "lte") and isinstance(v, (int, float))})
    top = "any" if isinstance(w, dict) and "any" in w and "all" not in w else ("all" if isinstance(w, dict) and "all" in w else "single")
    joins = sorted({p for _, p in ls}) if len(ls) > 1 else ["single"]
    return {"facts": facts, "n_facts": len(facts), "numbers": nums, "top": top, "has_any": "any" in json.dumps(w), "has_all": "all" in json.dumps(w)}
def our_effect(r):
    if not r.get("when"): return "none"
    eo, dp = r.get("effect_override"), r.get("decision_point")
    if eo == "consider": return "consider_level_2"
    if eo == "reassess_uptriage_consider" or dp == "D": return "reassess_uptriage"
    return {"A": "assign_level_1", "B": "assign_level_2"}.get(dp, "none")

# ---- 1. sentence matching
TH = 0.6
match_b = collections.defaultdict(list)          # blind id -> [(statement n, score)]
for b in B:
    for s in ST:
        if int(b["page"]) != int(s["page"]): continue
        sc = overlap(b["span"], s["span"])
        if sc >= TH: match_b[b["id"]].append((s["n"], round(sc, 2)))
st_by_n = {s["n"]: s for s in ST}
matched_st = {n for v in match_b.values() for n, _ in v}
only_blind = [b for b in B if b["id"] not in match_b]
only_ours = [s for s in ST if s["n"] not in matched_st]

# ---- 2. rule pairs through the matched statements
pairs = collections.OrderedDict()                # (blind id, our rule id) -> info
for b in B:
    for n, sc in match_b.get(b["id"], []):
        s = st_by_n[n]
        for rid in s.get("rules", []) + ([s["rule"]] if s.get("rule") else []) + ([s["proposal"]] if s.get("proposal") in R else []):
            pairs.setdefault((b["id"], rid), {"statements": []})["statements"].append(n)
bmap = {b["id"]: b for b in B}
rows = []
for (bid, rid), info in pairs.items():
    b, r = bmap[bid], R[rid]
    if b.get("kind") != "rule" or not r.get("when"):
        rows.append({"blind": bid, "ours": rid, "class": "non-rule on one side", "blind_kind": b.get("kind"), "ours_fires": bool(r.get("when")), "page": b["page"], "span": b["span"]}); continue
    sb, so = shape(b.get("when") or {}), shape(r["when"])
    diffs = []
    if str(b.get("decision_point")) != str(r.get("decision_point")): diffs.append(f"decision point {b.get('decision_point')} vs {r.get('decision_point')}")
    if b.get("effect") != our_effect(r): diffs.append(f"effect {b.get('effect')} vs {our_effect(r)}")
    if b.get("who_can_supply") != r.get("assessed_via"): diffs.append(f"who can supply {b.get('who_can_supply')} vs {r.get('assessed_via')}")
    if sb["n_facts"] != so["n_facts"]: diffs.append(f"facts {sb['n_facts']} vs {so['n_facts']}")
    if sb["numbers"] != so["numbers"]: diffs.append(f"numbers {sb['numbers']} vs {so['numbers']}")
    if (sb["has_any"], sb["has_all"]) != (so["has_any"], so["has_all"]) and max(sb["n_facts"], so["n_facts"]) > 1: diffs.append("joined differently (all/any)")
    rows.append({"blind": bid, "ours": rid, "class": "same" if not diffs else "differs", "diffs": diffs, "blind_facts": sb["facts"], "our_facts": so["facts"],
                 "page": b["page"], "span": b["span"], "blind_interpretation": b.get("interpretation"), "blind_note": b.get("note", "")})
# split / merge: one of ours matched by several blind rules, or the reverse
by_ours = collections.defaultdict(set); by_blind = collections.defaultdict(set)
for r_ in rows:
    if r_["class"] in ("same", "differs"): by_ours[r_["ours"]].add(r_["blind"]); by_blind[r_["blind"]].add(r_["ours"])
split_ours = {k: sorted(v) for k, v in by_ours.items() if len(v) > 1}      # we have one rule, the blind re-extraction has several
split_blind = {k: sorted(v) for k, v in by_blind.items() if len(v) > 1}    # the blind re-extraction has one, we have several
our_rules_unmatched = [rid for rid, r in R.items() if r.get("when") and rid not in by_ours]
blind_rules_unmatched = [b for b in only_blind if b.get("kind") == "rule"]

res = {"label": label, "blind_entries": len(B), "blind_by_kind": dict(collections.Counter(b.get("kind") for b in B)), "blind_facts": len(BF),
       "our_entries": len(R), "our_firing_rules": sum(1 for r in R.values() if r.get("when")), "our_statements": len(ST),
       "blind_entries_matched_to_a_statement": len(match_b), "only_in_blind": [{"id": b["id"], "page": b["page"], "kind": b.get("kind"), "effect": b.get("effect"), "span": b["span"], "note": b.get("note", "")} for b in only_blind],
       "only_in_ours_statements": [{"n": s["n"], "page": s["page"], "kind": s["kind"], "disposition": s["disposition"], "rules": s.get("rules") or s.get("rule") or s.get("proposal") or "", "span": s["span"]} for s in only_ours],
       "pairs": rows, "we_one_blind_several": split_ours, "blind_one_we_several": split_blind,
       "our_firing_rules_with_no_blind_rule": our_rules_unmatched}
json.dump(res, open(os.path.join(OUT, f"blind-comparison-{label}.json"), "w"), indent=1)
same = [r for r in rows if r["class"] == "same"]; diff = [r for r in rows if r["class"] == "differs"]; nonr = [r for r in rows if r["class"] == "non-rule on one side"]
L = [f"# Blind re-extraction ({label}) compared with the current rules file", "",
     f"Blind re-extraction: {len(B)} entries ({res['blind_by_kind']}), {len(BF)} facts. Current: {len(R)} entries, {res['our_firing_rules']} firing rules, supported by {len(ST)} statements of the complete reading pass.",
     f"Matching: same printed page and overlapping quote (longest common run of words at least {int(TH*100)}% of the shorter quote).", "",
     "| Outcome | Count |", "| --- | ---: |",
     f"| blind entries that match one of our statements | {len(match_b)} of {len(B)} |",
     f"| rule pairs compared | {len(same) + len(diff)} |", f"| of which the comparable parts agree | {len(same)} |", f"| of which something differs | {len(diff)} |",
     f"| blind entries with no statement of ours (only in the blind re-extraction) | {len(only_blind)} (of which rules: {len(blind_rules_unmatched)}) |",
     f"| our statements with no blind entry (only in ours) | {len(only_ours)} |",
     f"| our firing rules reached by no blind rule | {len(our_rules_unmatched)} |",
     f"| one rule of ours matched by several blind rules | {len(split_ours)} |", f"| one blind rule matching several of ours | {len(split_blind)} |", "",
     "## Same sentence, something differs", "", "| ours | blind | page | what differs | our facts | blind facts |", "| --- | --- | ---: | --- | --- | --- |"]
L += [f"| {r['ours']} | {r['blind']} | {r['page']} | {'; '.join(r['diffs'])} | {', '.join(r['our_facts'])} | {', '.join(r['blind_facts'])} |" for r in diff]
L += ["", "## Only in the blind re-extraction", "", "| blind | page | kind | effect | quote |", "| --- | ---: | --- | --- | --- |"]
L += [f"| {b['id']} | {b['page']} | {b.get('kind')} | {b.get('effect')} | {str(b['span'])[:140]} |" for b in only_blind]
L += ["", "## Only in ours", "", "| statement | page | kind | supports | quote |", "| ---: | ---: | --- | --- | --- |"]
L += [f"| {s['n']} | {s['page']} | {s['kind']} / {s['disposition']} | {s.get('rules') or s.get('rule') or s.get('proposal') or ''} | {s['span'][:140]} |" for s in only_ours]
L += ["", "## Our firing rules that no blind rule reached", "", ", ".join(our_rules_unmatched) or "none",
      "", "## Cut differently", "", "One rule of ours, several in the blind re-extraction:", ""] + [f"- {k}: {', '.join(v)}" for k, v in split_ours.items()]
L += ["", "One blind rule, several of ours:", ""] + [f"- {k}: {', '.join(v)}" for k, v in split_blind.items()]
L += ["", "## Same sentence, comparable parts agree (fact names side by side)", "", "| ours | blind | our facts | blind facts |", "| --- | --- | --- | --- |"]
L += [f"| {r['ours']} | {r['blind']} | {', '.join(r['our_facts'])} | {', '.join(r['blind_facts'])} |" for r in same]
open(os.path.join(OUT, f"blind-comparison-{label}.md"), "w").write("\n".join(L) + "\n")
print({k: v for k, v in res.items() if isinstance(v, (int, str, dict)) and k not in ("we_one_blind_several", "blind_one_we_several")})
print("same", len(same), "differs", len(diff), "non-rule pairs", len(nonr), "only blind", len(only_blind), "only ours", len(only_ours))
