"""Claude backend (Anthropic Messages API): the same surface as llm_gemini and llm_ollama (ask / ask_json / ask_image /
MODEL_NAME), plus USAGE and cost() so a run report can state what it cost (#82). Key: ANTHROPIC_API_KEY from the shell or
.env (Doppler: `doppler run --project hospital-triage --config dev_personal -- ...`); model: CLAUDE_MODEL (default
claude-opus-5-5). No prompt caching: the system prompt changes with the open fields every turn."""
import os, json, re, time, base64

USAGE = {"calls": 0, "input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
# $ per million tokens: input, output, cache read, cache write (5 min). platform.claude.com/docs/en/about-claude/pricing, read 14 Oct 2026.
PRICES = {"claude-opus-5-5": (4.0, 20.0, 0.20, 5.0), "claude-sonnet-5-5": (2.0, 10.0, 0.10, 2.5), "claude-haiku-4-5-20251001": (1.0, 5.0, 0.10, 1.25)}


def MODEL_NAME():
    return os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")


_client = None


def client():
    global _client
    if _client is None:
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key or key.startswith("paste-"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set: paste it into Doppler (hospital-triage, dev_personal) or .env")
        _client = anthropic.Anthropic(api_key=key)
    return _client


def _status(text):
    try:
        import llm
        llm.STATUS["text"] = text
    except Exception:
        pass


def _record(u):
    USAGE["calls"] += 1
    USAGE["input"] += getattr(u, "input_tokens", 0) or 0
    USAGE["output"] += getattr(u, "output_tokens", 0) or 0
    USAGE["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
    USAGE["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0


def cost(usage=None, model=None):
    """Dollars for a usage dict at the listed prices (0 when the model is not listed)."""
    u = usage or USAGE; p = PRICES.get(model or MODEL_NAME())
    if not p: return 0.0
    return (u["input"] * p[0] + u["output"] * p[1] + u["cache_read"] * p[2] + u["cache_write"] * p[3]) / 1e6


def _call(content, system, json_mode, max_tries, model):
    kw = {"model": model or MODEL_NAME(), "max_tokens": 1024, "messages": [{"role": "user", "content": content}]}
    if system:
        kw["system"] = system      # no prompt caching: the system prompt carries the open fields and changes every turn (a cache write each call, 14 Oct 2026 run)
    if json_mode:
        if isinstance(kw["messages"][0]["content"], str):
            kw["messages"][0]["content"] += "\n\nReturn ONLY the JSON object, nothing else."
    for attempt in range(max_tries):
        try:
            r = client().messages.create(**kw)
            _record(r.usage); _status("")
            return "".join(getattr(b, "text", "") for b in r.content if getattr(b, "type", "") == "text")
        except Exception as e:
            msg = str(e).lower()
            if any(x in msg for x in ("rate", "429", "overloaded", "529", "timeout")) and attempt + 1 < max_tries:
                backoff = 10 * (attempt + 1)
                _status(f"the model provider is rate-limiting us; retrying in {backoff} seconds (attempt {attempt + 2} of {max_tries})")
                time.sleep(backoff); continue
            raise
    raise RuntimeError("Claude: retries exhausted")


def _parse_json(txt):
    txt = re.sub(r"^```(json)?|```$", "", txt.strip(), flags=re.M).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else {}


def ask(prompt, system=None, json_mode=False, max_tries=6, model=None):
    return _call(prompt, system, json_mode, max_tries, model)


def ask_json(prompt, system=None, model=None):
    return _parse_json(ask(prompt, system=system, json_mode=True, model=model))


def ask_image(image_path, prompt, system=None, max_tries=6, model=None):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    media = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    content = [{"type": "image", "source": {"type": "base64", "media_type": media, "data": b64}}, {"type": "text", "text": prompt}]
    return _parse_json(_call(content, system, True, max_tries, model))
