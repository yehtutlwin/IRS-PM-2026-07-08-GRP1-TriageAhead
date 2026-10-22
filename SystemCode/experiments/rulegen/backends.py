"""LLM backends for rulegen — one function, three routes, identical prompt and gates.

  api         the project's prototype seam (Gemini API key / Ollama; see prototype/llm.py)
  gemini-cli  Google's Gemini CLI, headless (`gemini -p ... -o json --approval-mode plan`);
              auth via GEMINI_API_KEY or a Google login (GOOGLE_GENAI_USE_GCA) where permitted
  codex-cli   OpenAI's Codex CLI, headless (`codex exec -m ... -s read-only`), signed in with a
              ChatGPT account — a design-time drafting tool, never part of the runtime chatbot
  agy         Google's Antigravity CLI (successor to Gemini CLI for Google AI Pro/Ultra accounts),
              headless (`agy -p ... --mode plan --output-format json`); sign in once interactively

Every call returns (parsed_json_or_None, raw_text, model_reported). Read-only / no-tool modes are
forced so the run is a pure model call over the text we supply — reproducible from the log.
"""
import os, re, json, subprocess, tempfile, shutil

def _parse(txt):
    txt = re.sub(r"^```(json)?|```$", "", (txt or "").strip(), flags=re.M).strip()
    try: return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        try: return json.loads(m.group(0)) if m else None
        except json.JSONDecodeError: return None

def _node_path():
    extra = [p for p in (os.path.expanduser("~/.nvm/versions/node/v22.23.1/bin"), os.path.expanduser("~/.local/bin")) if os.path.isdir(p)]
    return os.pathsep.join(extra + [os.environ.get("PATH", "")])

def ask_json(backend, prompt, system, model, cwd):
    if backend == "api":
        import llm
        out = llm.ask_json(prompt, system=system)
        return (out if isinstance(out, dict) else None), json.dumps(out) if out else "", llm.MODEL_NAME()
    env = dict(os.environ, PATH=_node_path())
    full = f"{system}\n\n=====\n\n{prompt}"
    if backend == "gemini-cli":
        cmd = ["gemini", "-p", "", "-o", "json", "--approval-mode", "plan"] + (["-m", model] if model else [])
        r = subprocess.run(cmd, input=full, text=True, capture_output=True, cwd=cwd, env=env, timeout=900)
        d = _parse(r.stdout) or {}
        if d.get("error"): raise RuntimeError(f"gemini-cli: {d['error'].get('message', '')[:300]}")
        resp = d.get("response", "") if isinstance(d, dict) else r.stdout
        used = ",".join((d.get("stats", {}) or {}).get("models", {}).keys()) if isinstance(d, dict) else model
        return _parse(resp), resp, used or model
    if backend == "codex-cli":
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f: last = f.name
        cmd = ["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "-o", last, "-C", cwd] + (["-m", model] if model else []) + ["-"]
        r = subprocess.run(cmd, input=full, text=True, capture_output=True, cwd=cwd, env=env, timeout=900)
        resp = open(last).read() if os.path.exists(last) else r.stdout
        if r.returncode != 0 and not resp.strip():
            raise RuntimeError(f"codex-cli: {(r.stderr or r.stdout)[-400:]}")
        return _parse(resp), resp, model or "codex-default"
    if backend == "agy":
        # agy is an agent: without this it reaches for tools, which headless mode auto-denies (-> empty / CANCELED)
        full_cli = ("IMPORTANT: Do NOT use any tools, run any commands, read or write any files. All the text you "
                    "need is in this message. Answer directly, in one turn, with the JSON object only.\n\n" + full)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"type": "object", "properties": {"rules": {"type": "array", "items": {"type": "object"}}},
                       "required": ["rules"]}, f); wrapper = f.name
        cmd = ["agy", "-p", full_cli, "--output-format", "json", "--mode", "plan", "--disable-slash-commands",
               "--print-timeout", "15m", "--json-schema", wrapper] + (["--model", model] if model else [])
        r = subprocess.run(cmd, text=True, capture_output=True, cwd=cwd, env=env, timeout=1000, stdin=subprocess.DEVNULL)
        d = _parse(r.stdout)
        if not isinstance(d, dict):
            raise RuntimeError(f"agy: non-JSON output: {(r.stdout or r.stderr)[-400:]}")
        if not (d.get("response") or "").strip():
            raise RuntimeError(f"agy: empty response (tool denied?) stderr: {r.stderr[-300:]}")
        if d.get("error") or d.get("is_error") or (d.get("status") and d.get("status") != "SUCCESS"):
            raise RuntimeError(f"agy: status={d.get('status')} {str(d.get('error') or d.get('response'))[:300]}")
        resp = d.get("response") or d.get("result") or d.get("content") or ""
        used = model or "agy-default (envelope does not report the model - always pass --model)"
        so = d.get("structured_output")   # schema-enforced, already parsed - prefer it
        return (so if isinstance(so, dict) and "rules" in so else _parse(resp)), resp, used
    raise ValueError(backend)
