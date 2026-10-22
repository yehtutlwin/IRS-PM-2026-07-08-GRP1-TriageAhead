"""Build out/review.html — the review site — from out/concepts.json (written by relate.py).
Run: .venv/bin/python experiments/rulegen/build_review.py"""
import os, json, html
from drafters import LABEL, EXPLAIN
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "out", "concepts.json")))
DATA = json.dumps(data).replace("</", "<\\/")
EXPL_HTML = "".join(f"<dt>{html.escape(t)}</dt><dd>{html.escape(d).replace('`','')}</dd>" for t, d in EXPLAIN)
PAGE = open(os.path.join(HERE, "review.template.html")).read()
page = PAGE.replace("__DATA__", DATA).replace("__OL__", json.dumps(LABEL)).replace("__EXPLAIN__", EXPL_HTML)
open(os.path.join(HERE, "out", "review.html"), "w").write(page)
print("review.html:", os.path.getsize(os.path.join(HERE, "out", "review.html")), "bytes")
