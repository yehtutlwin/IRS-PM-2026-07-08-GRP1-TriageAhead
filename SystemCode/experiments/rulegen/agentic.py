"""agentic.py — the *agentic* extraction experiment: tools ON, inside an isolated temp workspace.

Contrast with rulegen.py (tool-less, one call per page): here the drafter is an agent (Antigravity
CLI) with file tools enabled, but it can only see a temp directory we populate. The directory holds
the handbook PDF, the page texts, the JSON schema, the field vocabulary and the instructions — and
NOT rules/criteria.yaml, so it cannot copy our reviewed answers. --sandbox is on; it writes its
drafts to out.yaml in that directory; we then apply the SAME gates (schema, span, diff) with the
rulegen functions. The agent's transcript is kept as the run log.

Run:  .venv/bin/python experiments/rulegen/agentic.py --model gemini-3.1-pro-high [--pages 9,11,12,...]
Output: out/criteria.draft.agentic.<model>.yaml + out/runs/<ts>-agentic-<model>.md (+ transcript)
"""
import os, sys, re, json, time, shutil, argparse, tempfile, subprocess
import yaml, jsonschema, pymupdf
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "prototype"))
import rulegen  # noqa: E402  — reuse SCHEMA, OFFSET, span_check, match_existing, fields_of

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--pages", default="9,10,11,12,13,14,15,23,24", help="printed pages to expose as text files")
    ap.add_argument("--timeout", default="40m")
    ap.add_argument("--no-sandbox", action="store_true", help="isolation by temp dir only (diagnostic)")
    ap.add_argument("--isolate", action="store_true",
                    help="optional: run agy inside a private mount namespace (empty /tmp, source trees hidden). Not needed for a clean-slate run; a fresh workspace suffices")
    args = ap.parse_args()
    pages = [int(p) for p in args.pages.split(",")]
    doc = pymupdf.open(rulegen.PDF)
    wsroot = os.path.expanduser("~/.cache/rulegen-agentic"); os.makedirs(wsroot, exist_ok=True)
    ws = tempfile.mkdtemp(prefix="ws-", dir=wsroot)   # outside /tmp so --isolate can replace /tmp with an empty tmpfs
    os.makedirs(os.path.join(ws, "pages")); os.makedirs(os.path.join(ws, "out"))
    shutil.copy(rulegen.PDF, os.path.join(ws, "handbook.pdf"))
    for pr in pages:
        open(os.path.join(ws, "pages", f"p{pr}.txt"), "w").write(doc[pr + rulegen.OFFSET - 1].get_text())
    json.dump(rulegen.SCHEMA, open(os.path.join(ws, "criteria.schema.json"), "w"), indent=1)
    open(os.path.join(ws, "INSTRUCTIONS.md"), "w").write(f"""# Task
Extract every triage criterion from the ESI v5 handbook into `out/out.yaml` as a YAML list of rule
entries, each conforming EXACTLY to `criteria.schema.json` (read it first). Work only inside this
directory. Do not use the network or any resource outside this directory.

Inputs: `handbook.pdf` (the whole handbook; printed page number = PDF index - {rulegen.OFFSET}) and
`pages/p<N>.txt` (extracted text of the printed pages of interest: {pages}). You may read any of
them, in any order, as many times as you like, and cross-check between pages and the PDF.

{rulegen.SYSTEM.split("Return ONLY JSON")[0]}

Rules for each entry (same as the tool-less run): id "<dp>-00.<kebab-slug>"; span COPIED VERBATIM from
the page (it is checked mechanically); source "ESI v5 p.<printed page> (<section>)"; provenance
verbatim or operationalized only; effect_override only when the handbook's verb is softer than
assign; assessed_via reported / observed / vitals. Prefer the field vocabulary in the schema's
x-known-fields. Be exhaustive: one entry per distinct criterion, example, and threshold.

When done, `out/out.yaml` must exist and parse as YAML. VERIFY it exists by reading it back. Then, in
your final reply, include the complete YAML list again inside a ```yaml fenced block (this is the
fallback if the file write did not persist), followed by a one-paragraph summary.
""")
    print(f"workspace: {ws}", flush=True)
    cmd = ["agy", "-p", "Read INSTRUCTIONS.md in this directory and carry out the task exactly. You may read files here; write only to out/out.yaml.",
           "--model", args.model, "--output-format", "stream-json", "--dangerously-skip-permissions",
           "--print-timeout", args.timeout] + ([] if args.no_sandbox else ["--sandbox"])
    # The agent's environment must carry no secrets: it may run `env` and the transcript is committed.
    env = {k: v for k, v in os.environ.items() if not re.search(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL", k, re.I)}
    env["PATH"] = os.pathsep.join([os.path.expanduser("~/.local/bin"), env.get("PATH", "")])
    if args.isolate:
        # private mount namespace: fresh tmpfs on /tmp with ONLY the workspace bind-mounted into it;
        # every source tree under $HOME hidden behind an empty tmpfs (credentials/config dirs stay visible).
        home = os.path.expanduser("~")
        hide = [d for d in (os.path.join(home, "source-code"), os.path.join(home, "repos"), os.path.join(home, "Documents")) if os.path.isdir(d)]
        inner = " && ".join(["mount -t tmpfs tmpfs /tmp", "mkdir -p /tmp/ws", f"mount --bind '{ws}' /tmp/ws"]
                            + [f"mount -t tmpfs tmpfs '{d}'" for d in hide + [wsroot]]   # wsroot last: sibling runs hidden, our bind survives
                            + ["cd /tmp/ws", "exec " + " ".join("'" + c.replace("'", "'\\''") + "'" for c in cmd)])
        cmd = ["unshare", "-Urm", "--propagation", "private", "sh", "-c", inner]
        ws_note = " · isolate: unshare mount ns (private /tmp, source trees hidden)"
    else:
        ws_note = ""
    t0 = time.time()
    r = subprocess.run(cmd, cwd=ws, env=env, text=True, capture_output=True, timeout=3600, stdin=subprocess.DEVNULL)
    elapsed = time.time() - t0
    # stream-json: one event per line; keep the whole transcript, derive the envelope from the final result
    events = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
    final = next((e for e in reversed(events) if e.get("status") or e.get("type") in ("result", "final")), {}) or {}
    env_ = {"status": final.get("status") or final.get("type"), "response": final.get("response") or final.get("result") or "",
            "num_turns": final.get("num_turns")}
    tool_events = [e for e in events if any(k in json.dumps(e).lower() for k in ("tool_use", "tool_call", "tool_result", "function"))]
    transcript_path = None
    outp = os.path.join(ws, "out", "out.yaml")
    drafts_raw = yaml.safe_load(open(outp)) if os.path.exists(outp) else None
    if isinstance(drafts_raw, dict): drafts_raw = drafts_raw.get("rules", [])
    source_of_drafts = "out/out.yaml"
    if not drafts_raw:   # fallback: YAML fenced block in the final response
        m = re.search(r"```ya?ml\s*(.*?)```", str(env_.get("response", "")), re.S)
        if m:
            try:
                fb = yaml.safe_load(m.group(1)); drafts_raw = fb.get("rules", fb) if isinstance(fb, dict) else fb
                source_of_drafts = "final response (fenced YAML) — file write did not persist"
            except yaml.YAMLError: pass
    drafts_raw = drafts_raw or []
    # gates — identical to rulegen
    validator = jsonschema.Draft202012Validator(rulegen.SCHEMA); known = set(rulegen.SCHEMA["x-known-fields"])
    text_by_page = {i + 1 - rulegen.OFFSET: doc[i].get_text() for i in range(len(doc)) if i + 1 - rulegen.OFFSET >= 1}
    drafts, rows, counter = [], [], {}
    for rr in drafts_raw:
        if not isinstance(rr, dict): continue
        dp = rr.get("decision_point", "X"); counter[dp] = counter.get(dp, 0) + 1
        slug = re.sub(r"^[ABCD]-\d+\.", "", str(rr.get("id", "unnamed")))
        rr["id"] = f"{dp}-{60 + counter[dp]:02d}.{slug}"
        m = re.search(r"(?:p\.?\s*|page\s+)(\d+)", str(rr.get("source", "")), re.I); cited = int(m.group(1)) if m else None
        g = rulegen._gate(rr, validator, known, text_by_page, cited)
        rows.append({"id": rr["id"], "cited": cited, **g, "provenance": rr.get("provenance")})
        if g["schema"] == "ok": drafts.append(rr)
    n = len(rows); valid = sum(r_["schema"] == "ok" for r_ in rows); strict = sum(r_["span"] == "strict" for r_ in rows)
    fail = sum(r_["span"] == "fail" for r_ in rows); matched = sum(1 for r_ in rows if r_["matches"])
    attributed = [r_ for r_ in rows if r_["found"] is not None]; page_ok = sum(1 for r_ in attributed if r_["found"] == r_["cited"])
    newf = sorted({f for r_ in rows for f in r_["new_fields"]})
    os.makedirs(os.path.join(HERE, "out", "runs"), exist_ok=True)
    yaml.safe_dump(drafts, open(os.path.join(HERE, "out", f"criteria.draft.agentic.{args.model}.yaml"), "w"), sort_keys=False, allow_unicode=True, width=100)
    tag = time.strftime("%Y-%m-%d-%H%M") + f"-agentic-{args.model}"
    L = [f"# rulegen run — mode AGENTIC (tools on, isolated temp workspace{ws_note}) · model {args.model} · {time.strftime('%Y-%m-%d %H:%M')} · {elapsed:.0f}s · agent status {env_.get('status')} · turns {env_.get('num_turns')}\n",
         "| metric | value | derivation |", "| --- | --- | --- |",
         f"| entries written by the agent | {n} | {source_of_drafts} |",
         f"| schema-valid | {valid}/{n} | jsonschema against rules/criteria.schema.json |",
         f"| span verified (strict) | {strict}/{valid} | quoted span found on some page (cited page first) |",
         f"| span FAILED | {fail}/{valid} | not found on any page — rejected |",
         f"| page attribution correct | {page_ok}/{len(attributed)} | cited printed page == page where the span was found |",
         f"| matched an existing reviewed rule | {matched}/{valid} | same matcher as the other modes |",
         f"| new candidates | {valid - matched}/{valid} | valid, not matched |",
         f"| new field names proposed | {len(newf)} | {newf} |",
         f"\n## Agent's closing summary\n\n{str(env_.get('response'))[:1500]}\n",
         "\n## Per-rule\n", "| id | cited | found | schema | span | matches | provenance |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r_ in rows: L.append(f"| {r_['id']} | {r_['cited']} | {r_['found']} | {r_['schema']} | {r_['span']} | {r_['matches'] or '—'} | {r_['provenance']} |")
    L += [f"\n## Transcript summary\n\n{len(events)} events, {len(tool_events)} tool-related; full transcript: out/runs/{tag}-transcript.jsonl\n"]
    for e in tool_events[:40]:
        L.append("- " + json.dumps(e)[:300].replace("|", "/"))
    rep = "\n".join(L); open(os.path.join(HERE, "out", "runs", f"{tag}.md"), "w").write(rep); print(rep[:1800])
    def redact(t):   # belt and braces: scrub anything key-shaped and the home path before it is saved
        t = re.sub(r"AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{20,}|ya29\.[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}", "***REDACTED***", t)
        return t.replace(os.path.expanduser("~"), "/home/user")
    with open(os.path.join(HERE, "out", "runs", f"{tag}-transcript.jsonl"), "w") as tf:
        for e in events: tf.write(redact(json.dumps(e)) + "\n")
    if r.stderr.strip(): open(os.path.join(HERE, "out", "runs", f"{tag}-stderr.txt"), "w").write(redact(r.stderr[-20000:]))
    shutil.copytree(ws, os.path.join(HERE, "out", "runs", f"{tag}-workspace"), dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("handbook.pdf"))   # copyrighted; never committed
    print(f"\n[workspace snapshot kept: out/runs/{tag}-workspace]")

if __name__ == "__main__":
    main()
