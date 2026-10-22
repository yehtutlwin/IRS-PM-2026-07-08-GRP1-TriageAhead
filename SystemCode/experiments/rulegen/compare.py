"""Three-way comparison: reviewed rulebook (spike) vs rulegen per-page vs rulegen whole-document.
Same schema, same gates, same model (gemini-3.6-flash) for the two rulegen modes.
Run: .venv/bin/python experiments/rulegen/compare.py   -> prints + out/comparison.md"""
import os, re, yaml, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
def norm(s): return re.sub(r"[\s\-]+", " ", str(s).lower().replace("’", "'")).strip()
def fields_of(c, acc=None):
    acc = set() if acc is None else acc
    if isinstance(c, dict):
        if "field" in c: acc.add(c["field"])
        for k in ("all", "any"):
            for x in c.get(k, []): fields_of(x, acc)
    return acc
def page(r):
    m = re.search(r"(?:p\.?\s*|page\s+)(\d+)", str(r.get("source", "")), re.I); return int(m.group(1)) if m else None
def same(a, b, jac_min=0.35):
    """loose criterion identity: same decision point and (span overlap or shared distinctive fields)"""
    if a["decision_point"] != b["decision_point"]: return False
    sa, sb = set(norm(a["span"]).split()), set(norm(b["span"]).split())
    jac = len(sa & sb) / max(1, len(sa | sb))
    fa, fb = fields_of(a["when"]), fields_of(b["when"])
    return jac >= jac_min or (fa and fa == fb) or (fa and fb and len(fa & fb) >= 1 and jac >= 0.2)
spike = [r for r in yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml"))) if r.get("when")]
per = yaml.safe_load(open(os.path.join(HERE, "out", "criteria.draft.perpage.yaml"))) or []
# other per-page drafters (CLI backends), keyed backend.model
pers = {os.path.basename(f).replace("criteria.draft.perpage.", "").replace(".yaml", ""): (yaml.safe_load(open(f)) or [])
        for f in sorted(glob.glob(os.path.join(HERE, "out", "criteria.draft.perpage.*.yaml")))}
wholes = {os.path.basename(f).replace("criteria.draft.", "").replace(".yaml", ""): (yaml.safe_load(open(f)) or [])
          for f in sorted(glob.glob(os.path.join(HERE, "out", "criteria.draft.whole*.yaml")))}
agentics = {os.path.basename(f).replace("criteria.draft.agentic.", "").replace(".yaml", ""): (yaml.safe_load(open(f)) or [])
            for f in sorted(glob.glob(os.path.join(HERE, "out", "criteria.draft.agentic.*.yaml")))}
whole = wholes.get("whole-exhaustive") or wholes.get("whole") or []   # the fuller whole-mode run for the pairwise section
pages_per = sorted({page(r) for r in per if page(r)})
spike_in_scope = [r for r in spike if page(r) in pages_per]
def refound(drafts, base): return [b for b in base if any(same(b, d) for d in drafts)]
def novel(drafts, base): return [d for d in drafts if not any(same(d, b) for b in base)]
rows = []
for name, drafts in ([("per-page (api gemini-3.6-flash)", per)] + [(f"per-page ({k})", v) for k, v in pers.items()]
                     + [(f"whole ({k})", v) for k, v in wholes.items()] + [(f"agentic ({k})", v) for k, v in agentics.items()]):
    if not drafts: rows.append((name, "— not run —", "", "", "", "")); continue
    rf_all = refound(drafts, spike); rf_scope = refound(drafts, spike_in_scope)
    nv = novel(drafts, spike)
    prov = {}
    for d in drafts: prov[d.get("provenance")] = prov.get(d.get("provenance"), 0) + 1
    rows.append((name, len(drafts), f"{len(rf_all)}/{len(spike)}", f"{len(rf_scope)}/{len(spike_in_scope)}", len(nv), prov))
both = [d for d in per if any(same(d, w) for w in whole)] if whole else []
only_per = [d for d in per if not any(same(d, w) for w in whole)] if whole else per
only_whole = [w for w in whole if not any(same(w, d) for d in per)] if whole else []
L = ["# Reviewed rulebook vs rulegen per-page vs rulegen whole-document\n",
     f"Reviewed (spike) rule entries: {len(spike)} ({len(spike_in_scope)} on the pages the per-page mode covered: {pages_per}).",
     "Same schema and gates for both rulegen modes; same model. 'Re-found' uses a loose criterion-identity matcher (same decision point + span overlap ≥0.35 or shared fields) — still an undercount.\n",
     "| mode | drafts | re-found of all reviewed rules | re-found of in-scope reviewed rules | novel (not in reviewed) | provenance labels |",
     "| --- | --- | --- | --- | --- | --- |"]
for r in rows: L.append("| " + " | ".join(str(x) for x in r) + " |")
if whole:
    L += [f"\n## Agreement between per-page and the fuller whole-document run (same model, different context)\n",
          f"- criteria found by **both**: {len(both)}", f"- **per-page only**: {len(only_per)}", f"- **whole-document only**: {len(only_whole)}",
          "\nPer-page only (first 12):"] + [f"  - {d['id']} (p.{page(d)}) — {str(d['span'])[:80]}" for d in only_per[:12]] + \
         ["\nWhole-document only (first 12):"] + [f"  - {d['id']} (p.{page(d)}) — {str(d['span'])[:80]}" for d in only_whole[:12]]
    for k, v in pers.items():
        if not v: continue
        b2 = [d for d in per if any(same(d, w) for w in v)]
        L += [f"\n## per-page API flash vs per-page {k}: found by both {len(b2)} · api-only {len(per)-len(b2)} · {k}-only {len([w for w in v if not any(same(w, d) for d in per)])}"]
    for k, v in agentics.items():
        if not v: continue
        b3 = [d for d in per if any(same(d, w) for w in v)]
        L += [f"\n## per-page API flash vs agentic {k}: found by both {len(b3)} · api-only {len(per)-len(b3)} · agentic-only {len([w for w in v if not any(same(w, d) for d in per)])}"]
    everything = per + whole + [d for v in pers.values() for d in v] + [d for v in agentics.values() for d in v]
    missed_both = [b for b in spike_in_scope if not any(same(b, d) for d in everything)]
    L += [f"\n## Reviewed rules no drafter re-found ({len(missed_both)})\n"] + [f"  - {b['id']} (p.{page(b)}) — {str(b['span'])[:80]}" for b in missed_both]
rep = "\n".join(L); open(os.path.join(HERE, "out", "comparison.md"), "w").write(rep); print(rep)
