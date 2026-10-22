"""Serving repository files from the guide's page: PDFs and videos as they are (with byte
ranges, so a video can be seeked), Markdown through a small reader-only renderer.
Only files under the repository root with a listed extension are served; nothing that
starts with a dot (.env, .git) ever is."""
import html
import os
import re

TYPES = {
    ".pdf": "application/pdf", ".mp4": "video/mp4", ".m4a": "audio/mp4", ".srt": "text/plain; charset=utf-8",
    ".vtt": "text/vtt; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml", ".gif": "image/gif", ".html": "text/html; charset=utf-8",
    ".txt": "text/plain; charset=utf-8", ".md": "text/html; charset=utf-8",
    ".json": "text/plain; charset=utf-8", ".yaml": "text/html; charset=utf-8", ".yml": "text/html; charset=utf-8",
    ".jsonl": "text/plain; charset=utf-8", ".csv": "text/plain; charset=utf-8",
}


def resolve(root, relpath):
    """The absolute path for a request, or None when it must not be served."""
    rel = os.path.normpath(relpath.lstrip("/"))
    if rel.startswith("..") or any(part.startswith(".") for part in rel.split(os.sep)):
        return None
    ext = os.path.splitext(rel)[1].lower()
    if ext not in TYPES:
        return None
    full = os.path.realpath(os.path.join(root, rel))
    if not full.startswith(os.path.realpath(root) + os.sep) or not os.path.isfile(full):
        return None
    return full


def send(handler, root, relpath, head=False):
    full = resolve(root, relpath)
    if full is None:
        return _plain(handler, 404, "not found")
    if head:
        handler.send_response(200)
        handler.send_header("Content-Type", TYPES[os.path.splitext(full)[1].lower()])
        handler.send_header("Accept-Ranges", "bytes")
        handler.end_headers()
        return
    ext = os.path.splitext(full)[1].lower()
    if ext == ".md":
        _root[0] = root
        with open(full, encoding="utf-8", errors="replace") as f:
            body = page(os.path.relpath(full, root), markdown(f.read())).encode()
        return _bytes(handler, 200, body, TYPES[ext])
    if ext in (".yaml", ".yml"):
        with open(full, encoding="utf-8", errors="replace") as f:
            body = yaml_html(os.path.relpath(full, root), f.read()).encode()
        return _bytes(handler, 200, body, TYPES[ext])
    size = os.path.getsize(full)
    rng = handler.headers.get("Range")
    start, end = 0, size - 1
    m = re.match(r"bytes=(\d*)-(\d*)$", rng or "")
    if m and (m.group(1) or m.group(2)):
        if m.group(1):
            start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
        else:
            start = max(0, size - int(m.group(2)))
        end = min(end, size - 1)
        if start > end:
            handler.send_response(416); handler.send_header("Content-Range", f"bytes */{size}"); handler.end_headers()
            return
    code = 206 if m and (m.group(1) or m.group(2)) else 200
    handler.send_response(code)
    handler.send_header("Content-Type", TYPES[ext])
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Content-Length", str(end - start + 1))
    if code == 206:
        handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
    handler.end_headers()
    with open(full, "rb") as f:
        f.seek(start)
        left = end - start + 1
        while left > 0:
            chunk = f.read(min(1 << 16, left))
            if not chunk:
                break
            try:
                handler.wfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                return
            left -= len(chunk)


def _plain(handler, code, text):
    _bytes(handler, code, text.encode(), "text/plain; charset=utf-8")


def _bytes(handler, code, body, ctype):
    handler.send_response(code)
    handler.send_header("Content-Type", ctype)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


# ---- a small Markdown renderer: enough to read the project's documents -------------------------

SITE_LINKS = [  # links written for the team site: kept only when the target is in this repository
    (re.compile(r"^/docs/([\w-]+)/?(#.*)?$"), r"SystemCode/docs/\1.md"),
    (re.compile(r"^/experiments/([\w-]+)/?(#.*)?$"), r"SystemCode/experiments/out/\1.md"),
]
_root = [os.getcwd()]   # set by send(); where site links are resolved


def _href(h):
    """The address to link to, or None when the link points at something not in this repository."""
    if h.startswith("/"):
        for rx, to in SITE_LINKS:
            m = rx.match(h)
            if m:
                target = rx.sub(to, h.split("#")[0])
                if os.path.isfile(os.path.join(_root[0], target)):
                    return "/file/" + target + (m.group(2) or "")
                return None
        return None if not h.startswith("/file/") else h
    return h


def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", lambda m: f'<img alt="{m.group(1)}" src="{_href(m.group(2)) or ""}">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
               lambda m: f'<a href="{_href(m.group(2))}">{m.group(1)}</a>' if _href(m.group(2)) else m.group(1), t)
    t = re.sub(r"<(https?://[^>\s]+)>", r'<a href="\1">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def markdown(src):
    out, lines, i = [], src.splitlines(), 0
    para = []

    def flush():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush(); j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            code = html.escape("\n".join(lines[i + 1:j]))
            if ln.strip() == "```mermaid":       # drawn by the Mermaid library; stays readable as text without it
                out.append('<pre class="mermaid">' + code + "</pre>")
            else:
                out.append("<pre><code>" + code + "</code></pre>")
            i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            flush(); out.append(f"<h{len(m.group(1))}>{_inline(m.group(2))}</h{len(m.group(1))}>"); i += 1; continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{2,}", lines[i + 1]):
            flush(); rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            out.append("<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table>")
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", ln)
        if m:
            flush(); tag = "ol" if m.group(2)[0].isdigit() else "ul"; items = []
            while i < len(lines) and (re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]) or (lines[i].startswith("  ") and items)):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", lines[i])
                if mm:
                    items.append(mm.group(3))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if ln.startswith(">"):
            flush(); q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].strip()); i += 1
            out.append("<blockquote><p>" + _inline(" ".join(q)) + "</p></blockquote>"); continue
        if not ln.strip():
            flush(); i += 1; continue
        para.append(ln.strip()); i += 1
    flush()
    return "\n".join(out)


MERMAID = """<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/11.4.1/mermaid.min.js"></script>
<script>if(window.mermaid){mermaid.initialize({startOnLoad:true,theme:matchMedia('(prefers-color-scheme:dark)').matches?'dark':'default'})}</script>"""


def page(title, body):
    extra = MERMAID if 'class="mermaid"' in body else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f5f5f5;--line:#ddd;--acc:#2255aa}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161616;--fg:#eee;--mut:#aaa;--card:#222;--line:#333;--acc:#79a6ff}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:24px 16px}}a{{color:var(--acc)}}img{{max-width:100%}}
code{{background:var(--card);padding:1px 4px;border-radius:4px;font-size:.92em}}pre{{background:var(--card);padding:12px;border-radius:8px;overflow:auto}}pre code{{background:none;padding:0}}
table{{border-collapse:collapse;margin:12px 0;font-size:.95em}}th,td{{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}}
blockquote{{border-left:4px solid var(--line);margin:12px 0;padding:4px 16px;color:var(--mut)}}
.top{{font-size:14px;color:var(--mut);margin-bottom:16px}}pre.mermaid{{background:none;text-align:center}}
</style></head><body><main><div class="top"><a href="/">Setup guide</a> &rsaquo; {html.escape(title)}</div>
{body}</main>{extra}</body></html>"""


# ---- the YAML viewer: two small libraries do the work ------------------------------------------
# js-yaml parses the file in the browser, json-formatter-js shows it as a collapsible tree, highlight.js
# colours the source view. Offline, the page still shows the plain source.

HLJS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0"


def yaml_html(relpath, text):
    src = html.escape(text)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(relpath)}</title>
<link rel="stylesheet" href="{HLJS}/styles/github.min.css" media="(prefers-color-scheme: light)">
<link rel="stylesheet" href="{HLJS}/styles/github-dark.min.css" media="(prefers-color-scheme: dark)">
<style>
:root{{--bg:#fff;--fg:#1a1a1a;--mut:#666;--card:#f5f5f5;--line:#ddd;--acc:#2255aa}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161616;--fg:#eee;--mut:#aaa;--card:#222;--line:#333;--acc:#79a6ff}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:16px 24px}}.top{{font-size:14px;color:var(--mut);margin-bottom:8px}}a{{color:var(--acc)}}
button{{font:inherit;padding:6px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer;margin:0 8px 12px 0}}
button.on{{background:var(--acc);color:#fff;border-color:var(--acc)}}
pre{{margin:0;font:13.5px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-word}}
pre code.hljs{{background:none;padding:0}}#tree{{font:13.5px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.hide{{display:none}}
#tree .json-formatter-string{{white-space:pre-wrap;word-break:break-word}}
</style></head><body><main>
<div class="top"><a href="/">Setup guide</a> &rsaquo; {html.escape(relpath)}</div>
<button id="bt" class="on" onclick="show('tree')">Tree</button><button id="bs" onclick="show('src')">Source</button>
<div id="tree"></div><pre id="src" class="hide"><code class="language-yaml">{src}</code></pre>
<script src="https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/json-formatter-js@2.5.23/dist/json-formatter.umd.js"></script>
<script src="{HLJS}/highlight.min.js"></script>
<script src="{HLJS}/languages/yaml.min.js"></script>
<script>
function show(w){{document.getElementById('tree').classList.toggle('hide',w!=='tree');document.getElementById('src').classList.toggle('hide',w!=='src');
  document.getElementById('bt').classList.toggle('on',w==='tree');document.getElementById('bs').classList.toggle('on',w==='src')}}
// Open the tree one level below the file's main list: the collection holding the most entries that are
// objects (the rules, the fields, the test cases). Each entry then shows its own fields, nested ones folded.
function openDepth(d){{let best={{n:0,depth:1}};
  (function walk(x,depth){{if(!x||typeof x!=='object'||depth>3)return;const kids=Array.isArray(x)?x:Object.values(x);
    const n=kids.filter(k=>k&&typeof k==='object'&&!Array.isArray(k)).length;if(n>best.n)best={{n:n,depth:depth}};
    kids.forEach(k=>walk(k,depth+1))}})(d,1);
  return best.depth+1}}
try{{const data=jsyaml.load(document.querySelector('#src code').textContent);
  const dark=matchMedia('(prefers-color-scheme: dark)').matches;
  // maxArrayItems: show a long list whole; the library's default splits it into groups of 100, one more level
  document.getElementById('tree').appendChild(new JSONFormatter(data,openDepth(data),
    {{hoverPreviewEnabled:true,maxArrayItems:1000000,animateOpen:false,animateClose:false,theme:dark?'dark':''}}).render());
  hljs.highlightAll()}}catch(e){{show('src')}}
</script></main></body></html>"""
