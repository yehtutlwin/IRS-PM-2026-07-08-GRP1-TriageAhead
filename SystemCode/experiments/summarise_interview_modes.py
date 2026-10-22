#!/usr/bin/env python3
"""One table from the static-versus-dynamic runs: experiments/out/task-i-*-<tag>.json -> experiments/out/interview-modes.md

    .venv/bin/python experiments/summarise_interview_modes.py

Per configuration: floors reached, expected rules fired, facts captured, danger-sign misses, turns, questions,
re-asks (a question whose fields had all been asked before), and per-persona rows for the misses.
"""
import glob, json, os, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH = "https://github.com/yehtutlwin/iss-irs-2026-group1-hospital-triage/blob/main/"
TAGS = ["static-gemma4", "dynamic-gemma4", "static-qwen35", "dynamic-qwen35", "static-gemini", "dynamic-gemini"]
runs = {}
for tag in TAGS:
    files = sorted(glob.glob(os.path.join(ROOT, "experiments", "out", f"task-i-*-{tag}.json")))
    if files: runs[tag] = json.load(open(files[-1])) | {"file": os.path.basename(files[-1])}
L = ["# Static slots versus dynamic grouping - persona harness", "",
     "Same nine personas, same persona player, same rulebook and slot file. *Static*: the fixed slots, one question per slot. "
     "*Dynamic*: the program ranks the open fields; the model chooses which of the top-ranked ones to ask together (at most 4, top one always included, "
     "a confirmation alone) and writes the question. Re-ask = a question all of whose fields had already been asked.", "",
     "| configuration | interview model | floors ok | rules ok | facts captured | danger misses | turns / persona | questions / persona | re-asks total | source |",
     "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
for tag in TAGS:
    if tag not in runs: L.append(f"| {tag} | (not run) | | | | | | | | |"); continue
    r = runs[tag]; R = r["results"]; n = len(R); H = sum(x["hits"] for x in R); T = sum(x["total"] for x in R)
    info = r.get("interview", {})
    L.append(f"| {tag} | {info.get('model', '?')} ({info.get('backend', '?')}) | {sum(x['floor_ok'] for x in R)}/{n} | {sum(x['rules_ok'] for x in R)}/{n} | {H}/{T} ({H / max(T, 1):.0%}) | {sum(x['danger_miss'] for x in R)} | {sum(x['turns'] for x in R) / max(n, 1):.1f} | {sum(x.get('questions', 0) for x in R) / max(n, 1):.1f} | {sum(x.get('reasks', 0) for x in R)} | `{r['file'].replace('.json', '.md')}` |")
L += ["", "## Per persona, by configuration: the same persona, one session each", "", "Each cell links to the transcript of that session (ticket, floor, facts captured, questions asked, re-asks). Read a row across to compare the same persona under the four configurations; the persona's answers come from a fixed script, so only the questions differ.", ""]
personas = sorted({x["persona"] for r in runs.values() for x in r["results"]})
L.append("| persona | " + " | ".join(t for t in TAGS if t in runs) + " |"); L.append("| --- |" + " --- |" * len([t for t in TAGS if t in runs]))
for p in personas:
    cells = []
    for tag in TAGS:
        if tag not in runs: continue
        xs = [x for x in runs[tag]["results"] if x["persona"] == p]
        cells.append("; ".join(f"[{x['session']}]({GH}experiments/out/sessions-{tag}/{x['session']}.transcript.txt) · {'floor ok' if x['floor_ok'] else 'FLOOR ' + str(x['floor'])} · {x['hits']}/{x['total']} facts · {x.get('questions', x['turns'])} q · {x.get('reasks', 0)} re-asks" for x in xs) or "-")
    L.append(f"| {p} | " + " | ".join(cells) + " |")
L += ["", "## Misses by field (all configurations)", ""]
miss = collections.Counter()
for tag, r in runs.items():
    for x in r["results"]:
        for m in x["misses"]: miss[(tag, m.split(":")[0])] += 1
byfield = collections.defaultdict(dict)
for (tag, f), c in miss.items(): byfield[f][tag] = c
L.append("| field | " + " | ".join(t for t in TAGS if t in runs) + " |"); L.append("| --- |" + " ---: |" * len([t for t in TAGS if t in runs]))
for f in sorted(byfield, key=lambda k: -sum(byfield[k].values())):
    L.append(f"| {f} | " + " | ".join(str(byfield[f].get(t, "")) for t in TAGS if t in runs) + " |")
out = os.path.join(ROOT, "experiments", "out", "interview-modes.md"); open(out, "w").write("\n".join(L) + "\n"); print("wrote", out, "| configs:", list(runs))
