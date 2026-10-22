"""The web page: the same sections, checks and words as the terminal, served on the first
free port from 9095 on, on this machine only. The page polls /api/state every two seconds."""
import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import checks, files

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Setup guide</title>
<style>
:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--ok:#1b7f3b;--no:#b3261e;--wait:#8a6d00;--card:#f5f5f5;--line:#ddd;--acc:#2255aa}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mut:#aaa;--ok:#5ad27a;--no:#ff7b72;--wait:#e3b341;--card:#222;--line:#333;--acc:#79a6ff}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:24px 16px;display:grid;grid-template-columns:240px 1fr;gap:32px}
@media(max-width:720px){.wrap{grid-template-columns:1fr}}
h1{font-size:20px;margin:0 0 4px}h2{font-size:22px;margin:0 0 8px}
.mut{color:var(--mut);font-size:14px}
nav ol{list-style:none;padding:0;margin:16px 0}nav li{padding:6px 8px;border-left:3px solid var(--line);margin-bottom:4px}
nav li.current{border-color:var(--acc);font-weight:600}nav li.done{color:var(--ok)}nav li.skipped{color:var(--mut);text-decoration:line-through}
.check{display:grid;grid-template-columns:48px 1fr;gap:8px;padding:8px 0;border-top:1px solid var(--line)}
.mark{font-family:ui-monospace,monospace;font-weight:700}.ok{color:var(--ok)}.no{color:var(--no)}.wait{color:var(--wait)}
.fix{background:var(--card);border-radius:8px;padding:16px;margin:16px 0}
main{min-width:0}
pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px 64px 10px 12px;position:relative;margin:8px 0 0;white-space:pre-wrap;overflow-wrap:anywhere}
button{font:inherit;padding:8px 14px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer;margin-right:8px}
button.primary{background:var(--acc);color:#fff;border-color:var(--acc)}button:disabled{opacity:.5;cursor:default}
.copy{position:absolute;right:6px;top:6px;padding:2px 8px;font-size:12px}
ul.items{list-style:none;padding:0;margin:4px 0 12px}ul.items>li{padding:8px 0;border-top:1px solid var(--line)}
.label{font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--mut);margin-bottom:2px}
h3.grp{font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--mut);margin:20px 0 4px}
.tag{font-size:12px;color:var(--mut);border:1px solid var(--line);border-radius:10px;padding:0 8px;margin-left:6px}
.text p{margin:8px 0}.text ul{margin:8px 0;padding-left:22px}.text li{margin:4px 0}.text code{background:var(--card);padding:1px 4px;border-radius:4px;font-size:.92em}
.done{background:var(--card);border-left:4px solid var(--ok);padding:12px 16px;border-radius:0 8px 8px 0;margin:16px 0}
</style></head><body><div class="wrap">
<nav><h1>Setup guide</h1><div class="mut">ED triage pre-arrival intake assistant</div><ol id="nav"></ol>
<div class="mut" id="tick"></div></nav>
<main id="main">Loading…</main></div>
<script>
const $=s=>document.querySelector(s);const esc=t=>t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let last=null;
function render(st){
  $('#nav').innerHTML=st.sections.map(s=>`<li class="${s.status}">${esc(s.title)}</li>`).join('');
  $('#tick').textContent='re-checks every two seconds';
  if(st.finished){$('#main').innerHTML=`<h2>All sections done</h2><p>${st.sections.some(s=>s.status==='skipped')?'Some sections were skipped: '+esc(st.sections.filter(s=>s.status==='skipped').map(s=>s.title).join(', '))+'.':''}</p><p><button onclick="act('back')">Back</button></p>`;return}
  const s=st.section;let h=`<h2>${esc(s.title)}</h2><div class="text">${s.why_html}</div>`;
  let fix=null;
  for(const c of s.checks){const cls=c.ok?'ok':(c.ok===null?'wait':'no');const m=c.ok?'ok':(c.ok===null?'…':'no');
    h+=`<div class="check"><div class="mark ${cls}">${m}</div><div><div>${esc(c.title)}${c.optional&&!c.ok?' <span class="mut">(optional)</span>':''}</div><div class="mut">${esc(c.detail)}</div></div></div>`;
    if(c.ok===false&&!fix&&!c.optional)fix=c;}
  if(!fix)fix=s.checks.find(c=>c.ok===false)||null;
  if(s.passed){
    h+=`<div class="done text">${s.done_html}</div>`+list(s.items)+list(s.aside);
    h+=`<p><button class="primary" onclick="act('continue')">Continue</button>${st.index>0?'<button onclick="act(\'back\')">Back</button>':''}</p>`}
  else{ if(fix){h+=`<div class="fix"><div class="label">Still needed</div><strong>${esc(fix.title)}</strong><div class="text">${fix.fix_html}</div>`;
      if(fix.command)h+=pre(fix.command);
      h+=`<p class="mut">The command runs in a second terminal, in the repository folder. The guide notices when it has worked.</p></div>`}
    h+=`<p><button onclick="act('recheck')">Check again</button><button onclick="act('skip')">Skip this section</button>${st.index>0?'<button onclick="act(\'back\')">Back</button>':''}</p>`;
    h+=list(s.aside)}
  $('#main').innerHTML=h;
}
function list(items){let grp=null,h='<ul class="items">';
  for(const i of items){
    if(i.group&&i.group!==grp){grp=i.group;h+=`</ul><h3 class="grp">${esc(grp)}</h3><ul class="items">`}
    const note=i.note?`<div class="mut text">${i.note_html}</div>`:'';
    if(i.command){h+=`<li><strong>${esc(i.title)}</strong> <span class="tag">command</span>${note}${pre(i.command)}</li>`;continue}
    const href=i.url||('/file/'+i.path.split('/').map(encodeURIComponent).join('/'));
    const ext=(i.path.split('.').pop()||'').toLowerCase();
    const tag=(i.url?(i.url.startsWith('http://localhost')?'app':'site'):({mp4:'video',pdf:'PDF',yaml:'YAML',yml:'YAML',txt:'text',md:'page'}[ext]||'file'))+(i.meta?' · '+i.meta:'');
    if(i.ready===false){h+=`<li><span class="mut">${esc(i.title)}</span> <span class="tag">not yet</span>${note}</li>`;continue}
    h+=`<li><a href="${href}" target="_blank">${esc(i.title)}</a> <span class="tag">${esc(tag)}</span>${note}</li>`}
  return h+'</ul>'}
function pre(c){return `<pre><code>${esc(c)}</code><button class="copy" onclick="copyCmd(this)">copy</button></pre>`}
function copyCmd(b){navigator.clipboard&&navigator.clipboard.writeText(b.previousElementSibling.textContent).then(()=>{b.textContent='copied'})}
async function act(a){await fetch('/api/action',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action:a})});poll(true)}
async function poll(force){try{const st=await (await fetch('/api/state')).json();const k=st.version+':'+st.index+':'+st.finished;if(force||k!==last){last=k;render(st)}}catch(e){$('#tick').textContent='the guide has stopped; restart it with python3 SystemCode/guide/start.py'}}
poll(true);setInterval(poll,2000);
</script></body></html>"""


def serve(state, start_port=9095):
    port = checks.first_free_port(start_port)

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/api/state":
                self._send(200, json.dumps(state.snapshot()).encode(), "application/json")
            elif self.path in ("/", "/index.html"):
                self._send(200, PAGE.encode(), "text/html; charset=utf-8")
            elif self.path.startswith("/file/"):
                files.send(self, state.root, urllib.parse.unquote(self.path[6:].split("?")[0]))
            else:
                self._send(404, b"not found", "text/plain")

        def do_HEAD(self):
            if self.path.startswith("/file/"):
                files.send(self, state.root, urllib.parse.unquote(self.path[6:].split("?")[0]), head=True)
            else:
                self.send_response(200); self.end_headers()

        def do_POST(self):
            if self.path != "/api/action":
                return self._send(404, b"not found", "text/plain")
            n = int(self.headers.get("Content-Length") or 0)
            try:
                action = json.loads(self.rfile.read(n) or b"{}").get("action", "")
            except ValueError:
                action = ""
            ok = state.action(action) if action in ("continue", "skip", "back", "recheck") else False
            self._send(200, json.dumps({"ok": ok}).encode(), "application/json")

    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://localhost:{port}"
