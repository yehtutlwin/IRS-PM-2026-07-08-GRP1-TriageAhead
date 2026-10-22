"""Practice-case review (issue #68): one page per test case with the handbook page, our transcription and the second
reading side by side, the rule engine's outcome on each, and a verdict stored in the same reviews database
(rule_set = 'case'). Imported by review/app.py; no state of its own beyond the files it reads."""
import hashlib, json, os, sys, urllib.parse, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "prototype")); import engine  # noqa: E402
E = None  # set by app.py (html.escape)
SECOND = os.path.join(ROOT, "experiments", "out", "second-reading-gemini-facts.json")
COMPARE = os.path.join(ROOT, "experiments", "out", "second-reading-gemini.json")
VERDICT_MEANING = {"accept": "facts and expected outcome correct", "edit": "a fact is wrong or missing (say which)",
                   "reject": "the expected outcome is wrong", "unsure": "cannot tell from the page"}
_cache = {}

def case_id(c):
    if c.get("set") == "appA": return f"appA-ch{c['chapter']}-q{c['case']}"
    return ("A-" if c.get("set") == "A" else "B-" if c.get("set") == "B" else "ch9-") + str(c["case"])

def load_cases():
    if "cases" in _cache: return _cache["cases"]
    out = {}
    for n in ("v4_cases.yaml", "v4_posttest_cases.yaml"):
        for c in yaml.safe_load(open(os.path.join(ROOT, "tests", n))):
            c = dict(c); c["_id"] = case_id(c); c["_file"] = n
            c["_snapshot"] = json.dumps({"facts": c["facts"], "expect": c.get("expect"), "expect_rules": c.get("expect_rules"), "xfail": c.get("xfail")}, sort_keys=True, ensure_ascii=False)
            c["_hash"] = hashlib.sha256(c["_snapshot"].encode()).hexdigest()[:12]
            out[c["_id"]] = c
    _cache["cases"] = out; return out

def second():
    if "second" not in _cache:
        _cache["second"] = json.load(open(SECOND)) if os.path.exists(SECOND) else {}
        cmp_ = json.load(open(COMPARE)) if os.path.exists(COMPARE) else {"rows": []}
        _cache["compare"] = {r["case"]: r for r in cmp_.get("rows", [])}
    return _cache["second"], _cache["compare"]

def outcome(facts):
    fx = engine.Facts()
    for f in facts:
        if isinstance(f, dict) and f.get("field"):
            fx.write(f["field"], f.get("value"), status=f.get("status") or "reported", turn=0)
    engine.derive(fx, 0); t = engine.evaluate_tree(fx, engine.load_criteria())
    cls = "esi1" if t["esi1_indicators"] else "floor2" if t["floor"] else "none"
    return cls, sorted(r["id"] for r in t["fired"] + t["esi1_indicators"]), sorted(r["id"] for r in t["consider"])

def book_label(c):
    if c.get("set") == "appA": return f"Appendix A, chapter {c['chapter']} question {c['case']}"
    if c.get("set"): return f"Chapter 10, set {c['set']}, case {c['case']}"
    return f"Chapter 9, case {c['case']}"

def status_of(c, verdicts):
    """What the list shows: outcome differs / facts differ / agree, and whether confirmed."""
    _, cmp_ = second(); r = cmp_.get(c["_id"], {})
    kind = "outcome differs" if r and r.get("outcome_ours") != r.get("outcome_theirs") else "facts differ" if r and (r.get("value_differs") or r.get("only_theirs")) else "agree" if r else "no second reading"
    latest = verdicts.get(c["_id"], [])
    confirmed = [v for v in latest if v["verdict"] == "accept" and v["rule_hash"] == c["_hash"]]
    return kind, latest, confirmed

def index(q, verdicts_by_case, page):
    cases = load_cases(); rows = []; counts = {"outcome differs": 0, "facts differ": 0, "agree": 0, "no second reading": 0}; confirmed_n = 0
    flt = q.get("show", "all")
    for cid, c in cases.items():
        kind, latest, confirmed = status_of(c, verdicts_by_case); counts[kind] += 1; confirmed_n += bool(confirmed)
        if flt == "differ" and kind == "agree": continue
        if flt == "outcome" and kind != "outcome differs": continue
        if flt == "unconfirmed" and confirmed: continue
        v = "".join(f'<span class="chip {E(x["verdict"])}">{E(x["verdict"])}</span> {E(x["reviewer"])} ' for x in latest[:3])
        chip = {"outcome differs": "reject", "facts differ": "edit", "agree": "accept"}.get(kind, "")
        rows.append(f'<tr><td><a href="/case/{urllib.parse.quote(cid)}">{E(cid)}</a></td><td>{E(book_label(c))}</td><td>{E(str(c.get("v4_answer")))}</td>'
                    f'<td>{E(c.get("expect",""))}{" <span class=muted>(expected failure)</span>" if c.get("xfail") else ""}</td><td><span class="chip {chip}">{E(kind)}</span></td><td>{v or "<span class=muted>none yet</span>"}</td></tr>')
    total = len(cases); pct = int(100 * confirmed_n / total) if total else 0
    f = lambda k, l: f'<a href="/cases?show={k}">{E(l)}</a>'
    body = f"""<div class="card"><h2 style="margin:0 0 6px">Practice cases: our transcription against a second reading</h2>
<p class="muted">Each case of the handbook's practice sets is written as a test case (facts in our field vocabulary, the book's level, our expected outcome). A second model read the printed cases without seeing our files.
A verdict here says whether the facts and the expected outcome are right; the rule engine's pass rate (evaluation number 1) is reported over confirmed cases. Read the <b>outcome differs</b> cases first.</p>
<div class="prog" style="margin:8px 0"><div style="width:{pct}%;background:var(--ok)"></div></div><span class="muted">{confirmed_n} of {total} confirmed at their current content · outcome differs {counts['outcome differs']} · facts differ {counts['facts differ']} · agree {counts['agree']}</span>
<p class="filters">Show: {f('all','all')} {f('outcome','outcome differs')} {f('differ','any difference')} {f('unconfirmed','not yet confirmed')}</p>
<p><button class="btn gray" onclick="bulkConfirm()">Confirm every case shown whose two readings agree and whose test passes</button> <span class="muted" id="bulkmsg"></span></p></div>
<div class="card"><table><tr><th>case</th><th>in the book</th><th>book level</th><th>our expectation</th><th>readings</th><th>latest verdicts</th></tr>{''.join(rows)}</table></div>
<script>
async function bulkConfirm(){{const who=localStorage.getItem('reviewer')||prompt('Your name');if(!who)return;localStorage.setItem('reviewer',who);
 const r=await fetch('/api/case-bulk-confirm',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{reviewer:who,show:'{E(flt)}'}})}});
 document.getElementById('bulkmsg').textContent=await r.text();setTimeout(()=>location.reload(),1200);}}
</script>"""
    return page("Practice cases", body)

def case_page(cid, ident, page, locate, render_hint, verdicts_for, rules_commit):
    c = load_cases().get(cid)
    if not c: return None
    sec, cmp_ = second(); theirs = sec.get(cid, {}).get("facts", []); r = cmp_.get(cid, {})
    o_mine = outcome(c["facts"]); o_theirs = outcome(theirs) if theirs else ("none", [], [])
    ids = list(load_cases()); i = ids.index(cid); prev_id = ids[i-1] if i else None; next_id = ids[i+1] if i+1 < len(ids) else None
    # the handbook page: chapter 9/10 cases carry the printed page; Appendix A pages are found by the quoted span
    span = c.get("book_span", ""); printed = c.get("book_page"); panel = ""
    idx, how, printed_here = (None, None, None)
    if c.get("set") == "appA" and span:          # Appendix A pages carry no plain page number: search the appendix's own pages first
        try:
            import pymupdf
            d = pymupdf.open(os.path.join(ROOT, "sources", "ESI-Handbook-v4-2012-AHRQ.pdf"))
            for i in range(97, min(108, len(d))):
                if d[i].search_for(span[:60]): idx, how, printed_here = i, "span", None; break
        except Exception:
            pass
    if idx is None and (printed or span):
        idx, how, printed_here = locate("ESI v4", printed, span)
    if idx is not None:
        hl = urllib.parse.quote(span[:200]); cap = {"span": "quoted opening of the case found on this page", "pagemap": "printed page located; the quoted opening was not found on it", "guess": "page is a guess"}[how]
        panel = f"""<div class="card page"><b>ESI Implementation Handbook v4 (AHRQ 2012)</b> · {E(book_label(c))} · <span class="muted">{E(cap)} (PDF page {idx+1}{(', printed page ' + str(printed_here)) if printed_here else ''})</span>
 <p><a href="/pdf/ESI v4#page={idx+1}" target="_blank">open in PDF viewer at this page</a>{(' · answer on printed page ' + str(c['answer_page'])) if c.get('answer_page') else ''}</p>
 <a href="/page/ESI v4/{idx}?hl={hl}" target="_blank"><img loading="lazy" src="/page/ESI v4/{idx}?hl={hl}" alt="handbook page"></a></div>"""
    else:
        panel = '<div class="card"><p class="muted">The handbook PDF is not present locally, or the case could not be located on a page.</p></div>'
    mine = {f["field"]: f for f in c["facts"]}; other = {f["field"]: f for f in theirs if isinstance(f, dict) and f.get("field")}
    vd = r.get("value_differs", {}) or {}; only_theirs = r.get("only_theirs", {}) or {}
    def cell(v): return E(json.dumps(v, ensure_ascii=False)) if not isinstance(v, str) else E(v)
    trs = []
    for f in sorted(set(mine) | set(other)):
        m, o = mine.get(f), other.get(f)
        if m and o and f in vd: kind, style = "value differs", "background:#fff3e6"
        elif m and o: kind, style = "agree", ""
        elif m: kind, style = "only ours", "background:#eef3ff"
        else: kind, style = "only second reading", "background:#f3eaff"
        src = (" <span class=chip>from " + E(m["from"]) + "</span>") if m and m.get("from") else ""
        trs.append(f'<tr style="{style}"><td><code>{E(f)}</code></td><td>{cell(m.get("value")) if m else ""}{(" <span class=muted>(" + E(m["status"]) + ")</span>") if m and m.get("status") else ""}{src}</td><td>{cell(o.get("value")) if o else ""}</td><td class="muted">{kind}</td></tr>')
    def oc(o): return f'<b>{E(o[0])}</b>' + (f' · rules {E(", ".join(o[1]))}' if o[1] else "") + (f' · consider {E(", ".join(o[2]))}' if o[2] else "")
    xf = f'<p><b>Expected failure:</b> {E(str(c["xfail"]))}</p>' if c.get("xfail") else ""
    note = f'<p><b>Note:</b> {E(str(c["note"]))}</p>' if c.get("note") else ""
    hist = "".join(f'<tr><td><span class="chip {E(x["verdict"])}">{E(x["verdict"])}</span></td><td>{E(x["reviewer"])}</td><td class="muted">{E(x["created_at"])}{" · <span class=chip>case changed since</span>" if x["rule_hash"] != c["_hash"] else ""}</td><td>{E(x["comment"] or "")}</td></tr>' for x in verdicts_for(cid))
    nav = (f'<a href="/case/{urllib.parse.quote(prev_id)}">&larr; {E(prev_id)}</a>' if prev_id else "") + " &nbsp; " + (f'<a href="/case/{urllib.parse.quote(next_id)}">{E(next_id)} &rarr;</a>' if next_id else "")
    body = f"""<p class="muted"><a href="/cases">&larr; all cases</a> &nbsp; {nav}</p>
<div class="two"><div>
<div class="card"><h2 style="margin:0 0 6px">{E(cid)}</h2><span class="chip">{E(book_label(c))}</span> <span class="chip">book level {E(str(c.get('v4_answer')))}</span> <span class="chip">we expect {E(c.get('expect',''))}</span> <span class="muted">{E(c['_hash'])}{(' @ ' + E(rules_commit())) if rules_commit() else ''}</span>
 <p><b>{E(c.get('synopsis',''))}</b></p>{note}{xf}
 <p><b>Rule engine on our facts:</b> {oc(o_mine)}<br><b>Rule engine on the second reading's facts:</b> {oc(o_theirs) if theirs else '<span class=muted>no second reading for this case</span>'}</p>
 <table><tr><th>field</th><th>our transcription</th><th>second reading (Gemini 3.1 Pro)</th><th></th></tr>{''.join(trs)}</table>
 <p class="muted">"from answer": the book states it in its answer, not in the case. "from second-reading": found by the second reader, kept after a glance at the page.</p></div>
<div class="card"><h3 style="margin:0 0 6px">Your verdict</h3>
 <p class="muted">Read the case on the right. Is every fact in our column something the printed case (or, where marked, its answer) states, with nothing missing that a field exists for? Is the expected outcome what the book's level implies (level 1 → an ESI-1 indicator; level 2 by a high-risk finding → floor; else no floor)?</p>
 <form onsubmit="return submitCase(event)">
 <label>{'Signed in as' if ident else 'Your name (remembered on this device)'}</label><input type="text" id="reviewer" required {f'value="{E(ident)}" readonly' if ident else ''}>
 <div class="radio" style="margin-top:8px">{''.join(f'<label><input type="radio" name="verdict" value="{v}" required> <b>{v}</b> <span class="muted">{E(m)}</span></label><br>' for v, m in VERDICT_MEANING.items())}</div>
 <label>Comment (which fact, what the page says)</label><textarea id="comment"></textarea>
 <input type="hidden" id="case_id" value="{E(cid)}"><input type="hidden" id="case_hash" value="{E(c['_hash'])}">
 <p><button class="btn">Save verdict</button> <span class="muted" id="msg"></span></p></form>
 <h3>Verdicts so far</h3><table>{hist or '<tr><td class=muted>none yet</td></tr>'}</table></div>
</div><div>{panel}</div></div>
<script>
const rv=document.getElementById('reviewer');if(rv&&!rv.readOnly){{rv.value=localStorage.getItem('reviewer')||'';}}
async function submitCase(ev){{ev.preventDefault();const f=new FormData(ev.target);const d={{case_id:document.getElementById('case_id').value,case_hash:document.getElementById('case_hash').value,reviewer:document.getElementById('reviewer').value,verdict:f.get('verdict'),comment:document.getElementById('comment').value}};
 localStorage.setItem('reviewer',d.reviewer);const r=await fetch('/api/case-review',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});const t=await r.text();
 if(!r.ok){{document.getElementById('msg').textContent=t;return false;}}const j=JSON.parse(t);document.getElementById('msg').textContent='saved';if(j.next)location.href='/case/'+encodeURIComponent(j.next);else location.reload();return false;}}
</script>"""
    return page(f"Case {cid}", body)
