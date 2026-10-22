"""relate.py — relation graph over every drafted rule (spike rulebook + all rulegen outputs).
Nodes = rules; typed edges = how two rules relate; connected components = concepts.
  IDENTICAL   same span AND same condition           -> duplicates
  SAME-SPAN   same source sentence, different `when`  -> mixed representations of one concept
  SAME-LOGIC  same condition, different span/page     -> one encoding, several textual anchors
  SPLIT       fields of one are a strict subset of the other (merged `any` vs its pieces)
  RELATED     partial span/field overlap
Per concept: members by origin, representation variants, and label disagreements
(provenance / effect_override / decision_point).
Run: .venv/bin/python experiments/rulegen/relate.py -> out/concepts.md + out/concept-graph.html"""
import os, re, json, glob, yaml, itertools
import networkx as nx
sys_path_note = None
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))

def norm(s): return re.sub(r"[\s\-–—]+", " ", str(s).lower().replace("’", "'").replace("“", '"').replace("”", '"')).strip()
def leaves(c, acc=None):
    acc = [] if acc is None else acc
    if isinstance(c, dict):
        if "field" in c:
            op = next(k for k in ("equals", "in", "lt", "gt", "gte", "lte") if k in c)
            acc.append((c["field"], op, json.dumps(c[op], sort_keys=True)))
        for k in ("all", "any"):
            for x in c.get(k, []): leaves(x, acc)
    return acc
def fields(r): return {l[0] for l in leaves(r["when"])}
def logic(r): return frozenset(leaves(r["when"]))
def page(r):
    m = re.search(r"(?:p\.?\s*|page\s+)(\d+)", str(r.get("source", "")), re.I); return int(m.group(1)) if m else None

sources = {"spike": [r for r in yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml"))) if r.get("when")]}
for f in sorted(glob.glob(os.path.join(HERE, "out", "criteria.draft.*.yaml"))):
    sources[os.path.basename(f).replace("criteria.draft.", "").replace(".yaml", "")] = yaml.safe_load(open(f)) or []
nodes = []
for origin, rs in sources.items():
    for r in rs: nodes.append({"key": f"{origin}:{r['id']}", "origin": origin, "r": r})
G = nx.Graph()
for n in nodes: G.add_node(n["key"], **{k: v for k, v in n.items() if k != "r"}, dp=n["r"]["decision_point"], page=page(n["r"]))
def relate(a, b):
    ra, rb = a["r"], b["r"]
    if ra["decision_point"] != rb["decision_point"] and not (norm(ra["span"]) == norm(rb["span"])): pass
    sa, sb = set(norm(ra["span"]).split()), set(norm(rb["span"]).split())
    jac = len(sa & sb) / max(1, len(sa | sb))
    same_span = norm(ra["span"]) == norm(rb["span"]) or jac >= 0.8
    fa, fb = fields(ra), fields(rb)
    if same_span and logic(ra) == logic(rb): return "IDENTICAL", jac
    if same_span: return "SAME-SPAN", jac
    if fa and logic(ra) == logic(rb): return "SAME-LOGIC", jac
    if fa and fb and (fa < fb or fb < fa) and (jac >= 0.15 or ra["decision_point"] == rb["decision_point"]): return "SPLIT", jac
    if ra["decision_point"] == rb["decision_point"] and (jac >= 0.35 or (fa and fb and fa == fb)): return "RELATED", jac
    if ra["decision_point"] == rb["decision_point"] and fa and fb and len(fa & fb) >= 1 and jac >= 0.2: return "RELATED", jac
    return None, jac
counts = {}
for a, b in itertools.combinations(nodes, 2):
    t, jac = relate(a, b)
    if t:
        G.add_edge(a["key"], b["key"], type=t, jac=round(jac, 2)); counts[t] = counts.get(t, 0) + 1
STRONG = {"IDENTICAL", "SAME-SPAN", "SAME-LOGIC"}
Gs = nx.Graph(); Gs.add_nodes_from(G.nodes)
Gs.add_edges_from((a, b) for a, b, d in G.edges(data=True) if d["type"] in STRONG)
comps = sorted(nx.connected_components(Gs), key=lambda c: -len(c))
cid = {k: i for i, c in enumerate(comps, 1) for k in c}
# cross-concept links (SPLIT / RELATED) summarised per concept
xlinks = {}
for a, b, d in G.edges(data=True):
    if d["type"] in STRONG or cid[a] == cid[b]: continue
    xlinks.setdefault(cid[a], set()).add((cid[b], d["type"])); xlinks.setdefault(cid[b], set()).add((cid[a], d["type"]))
byk = {n["key"]: n for n in nodes}
L = ["# Concept inventory — relation graph over all drafted rules\n",
     f"Nodes: {len(nodes)} rules from {len(sources)} origins ({', '.join(f'{k}={len(v)}' for k, v in sources.items())}) · "
     f"edges: {sum(counts.values())} ({', '.join(f'{k} {v}' for k, v in sorted(counts.items()))}) · "
     f"concepts (connected components): {len(comps)}, of which singletons {sum(1 for c in comps if len(c)==1)}\n",
     "SUMMARY_PLACEHOLDER",
     "| # | size | origins | decision pt(s) | representation variants | label disagreements | split/related to | anchor |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
multi = 0; mixed = 0; disagree = 0
for i, comp in enumerate(comps, 1):
    if len(comp) == 1: continue
    multi += 1
    mem = [byk[k]["r"] for k in comp]; origins = sorted({byk[k]["origin"] for k in comp})
    dps = sorted({m["decision_point"] for m in mem})
    etypes = sorted({G.edges[e]["type"] for e in G.subgraph(comp).edges if G.edges[e]["type"] in STRONG})
    variants = []
    if "SAME-SPAN" in etypes: variants.append("same text, different encoding")
    if "SPLIT" in etypes: variants.append("merged vs split")
    if "SAME-LOGIC" in etypes: variants.append("same logic, different text")
    if "IDENTICAL" in etypes: variants.append("exact duplicates")
    if len({frozenset(fields(m)) for m in mem}) > 1 and not variants: variants.append("different field vocabulary")
    dis = []
    if len({m.get("provenance") for m in mem}) > 1: dis.append("provenance " + "/".join(sorted({str(m.get('provenance')) for m in mem})))
    if len({m.get("effect_override") for m in mem}) > 1: dis.append("effect " + "/".join(sorted({str(m.get('effect_override')) for m in mem})))
    if len(dps) > 1: dis.append("decision point " + "/".join(dps))
    if variants: mixed += 1
    if dis: disagree += 1
    anchor = min(mem, key=lambda m: (0 if m in sources["spike"] else 1, m["id"]))
    xl = ", ".join(f"#{c} ({t.lower()})" for c, t in sorted(xlinks.get(i, set()))[:6])
    L.append(f"| {i} | {len(comp)} | {', '.join(origins)} | {'/'.join(dps)} | {'; '.join(variants) or 'consistent'} | {'; '.join(dis) or '—'} | {xl or '—'} | {anchor['id']}: {str(anchor['span'])[:60]} |")
L[L.index("SUMMARY_PLACEHOLDER")] = f"Concepts formed by strong identity only (identical / same-span / same-logic); split-merge and related links are shown between concepts. Multi-member concepts: {multi} · with representation variants: {mixed} · with label disagreements: {disagree} · singletons: {sum(1 for c in comps if len(c)==1)}\n"
singles = [byk[next(iter(c))] for c in comps if len(c) == 1]
L.append("\n## Singletons (found by one origin only)\n")
for n in sorted(singles, key=lambda n: (n['origin'], n['r']['id'])):
    L.append(f"- {n['origin']} · {n['r']['id']} (p.{page(n['r'])}) — {str(n['r']['span'])[:90]}")
L.append("\n## Reading it\n- A concept with one member per origin and 'consistent' = the drafters agree; safe to promote after one page-check.\n- 'same text, different encoding' = the sentence is agreed, the `when` is not — the review question is which encoding is faithful.\n- 'merged vs split' = the same criteria as one `any` rule or several rules; a representation policy decision, not a knowledge disagreement.\n- Label disagreements (provenance / effect / decision point) are the review list.\n- Singletons are criteria only one origin found — coverage gaps of the others, or invention to check.")
open(os.path.join(HERE, "out", "concepts.md"), "w").write("\n".join(L)); print("\n".join(L[:6]))
# ---- concepts.json: the review page's data (build_review.py) ----
def _when_str(c):
    if not isinstance(c, dict): return ""
    if "field" in c:
        op = next(k for k in ("equals","in","lt","gt","gte","lte") if k in c); return f"{c['field']} {op} {json.dumps(c[op])}"
    for k in ("all","any"):
        if k in c: return "(" + f" {k.upper()} ".join(_when_str(x) for x in c[k]) + ")"
    return ""
_export = []
for i, comp in enumerate(comps, 1):
    mem = []
    for k in sorted(comp):
        n = byk[k]; r = n["r"]
        mem.append({"origin": n["origin"], "id": r["id"], "dp": r["decision_point"], "page": page(r), "provenance": r.get("provenance"),
                    "effect": r.get("effect_override"), "via": r.get("assessed_via"), "span": str(r.get("span","")),
                    "fields": sorted(fields(r)), "when": _when_str(r.get("when")), "source": str(r.get("source","")), "notes": r.get("notes")})
    etypes = sorted({G.edges[e]["type"] for e in G.subgraph(comp).edges if G.edges[e]["type"] in STRONG})
    dps = sorted({m["dp"] for m in mem}); origins = sorted({m["origin"] for m in mem})
    dis = [d for d, ok in (("provenance", len({m["provenance"] for m in mem})>1), ("effect", len({m["effect"] for m in mem})>1), ("decision point", len(dps)>1)) if ok]
    variants = [v for v, t in (("same text, different encoding","SAME-SPAN"),("same logic, different text","SAME-LOGIC"),("exact duplicates","IDENTICAL")) if t in etypes]
    anchor = min(mem, key=lambda m: (0 if m["origin"]=="spike" else 1, m["id"]))
    _export.append({"n": i, "size": len(comp), "origins": origins, "dps": dps, "variants": variants, "dis": dis,
                    "links": sorted({f"#{c} {t.lower()}" for c, t in xlinks.get(i, set())}), "anchor": anchor["id"], "aspan": anchor["span"],
                    "members": mem, "reviewed": any(m["origin"]=="spike" for m in mem)})
json.dump({"concepts": _export, "origins": {k: len(v) for k, v in sources.items()}}, open(os.path.join(HERE, "out", "concepts.json"), "w"))

# interactive graph
from pyvis.network import Network
net = Network(height="900px", width="100%", bgcolor="#ffffff", font_color="#222", notebook=False, cdn_resources="in_line")
col = {"spike": "#1f4e9c", "perpage": "#3e8e4f", "perpage.agy.gemini-3.6-flash-medium": "#7bc47f", "perpage.agy.gemini-3.1-pro-high": "#d9a300",
       "agentic.gemini-3.6-flash-medium": "#e07b39", "agentic.gemini-3.1-pro-high": "#b8322f", "whole": "#8e5fb5", "whole-exhaustive": "#c7a0e0"}
ecol = {"IDENTICAL": "#222", "SAME-SPAN": "#e08a00", "SAME-LOGIC": "#0a7", "SPLIT": "#c33", "RELATED": "#bbb"}
for k in G.nodes:
    n = byk[k]; r = n["r"]
    net.add_node(k, label=r["id"], color=col.get(n["origin"], "#999"), title=f"{n['origin']} · {r['decision_point']} · {r.get('provenance')} · p.{page(r)}<br>{str(r['span'])[:160]}<br>{sorted(fields(r))}", size=9,
                 origin=n["origin"], dp=r["decision_point"], concept=cid[k], hay=(r["id"] + " " + str(r["span"]) + " " + " ".join(sorted(fields(r)))).lower())
for a, b, d in G.edges(data=True):
    net.add_edge(a, b, color=ecol[d["type"]], title=f"{d['type']} (jac {d['jac']})", width=2 if d["type"] != "RELATED" else 1, rtype=d["type"])
net.set_options('{"physics": {"solver": "forceAtlas2Based", "stabilization": {"iterations": 200}}}')
gp = os.path.join(HERE, "out", "concept-graph.html"); net.save_graph(gp)
# ---- inject legend + filters (pyvis exposes `nodes`, `edges`, `network` globals) ----
origins_js = json.dumps([(o, col.get(o, "#999"), n_) for o, n_ in ((o, len(v)) for o, v in sources.items())])
etypes_js = json.dumps([(t, c, t != "RELATED") for t, c in ecol.items()])
panel = """
<style>#cg-panel{position:fixed;top:10px;left:10px;z-index:9;background:rgba(255,255,255,.96);border:1px solid #ccd;border-radius:6px;padding:10px 12px;font:13px/1.4 system-ui,sans-serif;max-width:330px;max-height:92vh;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.12)}
#cg-panel h4{margin:8px 0 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#556}#cg-panel h4 a{text-transform:none;letter-spacing:0;font-weight:400;color:#1f6f8b;margin-left:4px}#cg-panel label{display:flex;align-items:center;gap:6px;margin:2px 0;cursor:pointer}
#cg-panel .sw{width:12px;height:12px;border-radius:50%;display:inline-block;border:1px solid #888}#cg-panel .ln{width:22px;height:0;border-top:3px solid;display:inline-block}
#cg-panel input[type=search],#cg-panel select{width:100%;padding:5px;margin:3px 0;font:inherit}#cg-panel .cnt{color:#667;font-size:12px;margin-top:6px}#cg-panel .help{font-size:12px;color:#556;margin:0 0 6px}
#cg-toggle{position:fixed;top:10px;left:10px;z-index:10;display:none;font:13px system-ui;padding:6px 10px}</style>
<div id="cg-panel">
<b>Concept graph — how to read it</b>
<p class="help">Each dot is one drafted rule; colour = which drafter produced it. A line joins two rules that encode the same criterion: black = identical, orange = same quoted sentence but different encoding, teal = same condition from different text, red = one is a split/merged version of the other, grey = loosely related. Clusters are concepts. Hover a dot for its span and fields; drag to rearrange.</p>
<h4>Search</h4><input type="search" id="cg-q" placeholder="rule id, words in span, field name…">
<h4>Decision point</h4><select id="cg-dp"><option value="">All</option><option>A</option><option>B</option><option>C</option><option>D</option></select>
<h4>Drafters (nodes) <a href="#" class="cg-all" data-for="cg-orig" data-on="1">all</a> · <a href="#" class="cg-all" data-for="cg-orig" data-on="0">none</a></h4><div id="cg-orig"></div>
<h4>Relations (edges) <a href="#" class="cg-all" data-for="cg-et" data-on="1">all</a> · <a href="#" class="cg-all" data-for="cg-et" data-on="0">none</a></h4><div id="cg-et"></div>
<label><input type="checkbox" id="cg-iso"> hide rules with no visible connection</label>
<div class="cnt" id="cg-cnt"></div>
</div>
<script>
(function(){
const ORIG=__ORIG__, ET=__ET__;
const OL=__OL__;
const og=document.getElementById('cg-orig'), eg=document.getElementById('cg-et');
ORIG.forEach(([o,c,n])=>{og.insertAdjacentHTML('beforeend',`<label><input type="checkbox" data-o="${o}" checked><span class="sw" style="background:${c}"></span>${OL[o]||o} <span style="color:#889">(${n})</span></label>`)});
ET.forEach(([t,c,on])=>{eg.insertAdjacentHTML('beforeend',`<label><input type="checkbox" data-t="${t}" ${on?'checked':''}><span class="ln" style="border-color:${c}"></span>${t.toLowerCase()}</label>`)});
const allN=nodes.get(), allE=edges.get();
function apply(){
  const q=document.getElementById('cg-q').value.toLowerCase(), dp=document.getElementById('cg-dp').value;
  const oks=new Set([...og.querySelectorAll('input:checked')].map(i=>i.dataset.o)), ets=new Set([...eg.querySelectorAll('input:checked')].map(i=>i.dataset.t));
  const iso=document.getElementById('cg-iso').checked;
  let vis=new Set(allN.filter(n=>oks.has(n.origin)&&(!dp||n.dp===dp)&&(!q||n.hay.includes(q))).map(n=>n.id));
  if(q){ // also show the concept-mates of matches so context stays visible
    const cs=new Set(allN.filter(n=>vis.has(n.id)).map(n=>n.concept)); allN.forEach(n=>{if(cs.has(n.concept)&&oks.has(n.origin)&&(!dp||n.dp===dp))vis.add(n.id)});
  }
  const visE=allE.filter(e=>ets.has(e.rtype)&&vis.has(e.from)&&vis.has(e.to));
  if(iso){const conn=new Set(); visE.forEach(e=>{conn.add(e.from);conn.add(e.to)}); vis=new Set([...vis].filter(id=>conn.has(id)))}
  nodes.update(allN.map(n=>({id:n.id,hidden:!vis.has(n.id)}))); edges.update(allE.map(e=>({id:e.id,hidden:!(ets.has(e.rtype)&&vis.has(e.from)&&vis.has(e.to))})));
  document.getElementById('cg-cnt').textContent=`${vis.size} of ${allN.length} rules · ${visE.filter(e=>vis.has(e.from)&&vis.has(e.to)).length} edges shown`;
}
document.getElementById('cg-panel').addEventListener('input',apply); document.getElementById('cg-panel').addEventListener('change',apply);
document.querySelectorAll('.cg-all').forEach(a=>a.addEventListener('click',e=>{e.preventDefault(); document.querySelectorAll('#'+a.dataset.for+' input').forEach(i=>i.checked=a.dataset.on==='1'); apply();}));
apply();
})();
</script>"""
from drafters import LABEL as _OL
h = open(gp).read().replace("</body>", panel.replace("__ORIG__", origins_js).replace("__ET__", etypes_js).replace("__OL__", json.dumps(_OL)) + "\n</body>")
open(gp, "w").write(h)
print("graph -> out/concept-graph.html  (node colour = origin: blue spike, green per-page, red whole, purple whole-exhaustive; edge colour = relation)")
