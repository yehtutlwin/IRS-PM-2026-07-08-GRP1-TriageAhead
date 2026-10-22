"""Ollama backend: same surface as llm_gemini, served by a local model over
Ollama's native API (stdlib-only, JSON mode and images included). Model must be
pulled once (`ollama pull <model>`) and the server running (`ollama serve`, or
the systemd service the installer sets up). No pacing or quota locally."""
import os, json, re, base64, urllib.request, urllib.error

_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
LAST_USAGE = {"prompt_tokens": None, "output_tokens": None}

def MODEL_NAME():
    return os.environ.get("OLLAMA_MODEL", "gemma4:12b")

def _chat(messages, json_mode=False, temperature=0.4):
    # think=false: thinking models (e.g. gemma4) otherwise burn 100s-1000s of
    # tokens per call and can return an EMPTY content field; OLLAMA_THINK=true
    # re-enables it for experiments
    # num_ctx: Ollama's default window is 4,096 tokens and it silently drops the START of a prompt that overflows it, which is
    # where the fact-extraction instructions and the asked fields are (15 Oct 2026: a date of birth given with the name was
    # lost late in interviews, when the open-field list made the prompt about that long). 16k covers the longest prompt
    # several times over; OLLAMA_NUM_CTX overrides. LAST_USAGE keeps the token counts of the last call for checks.
    body = {"model": MODEL_NAME(), "messages": messages, "stream": False,
            "think": os.environ.get("OLLAMA_THINK", "").lower() == "true",
            "options": {"temperature": float(os.environ.get("LLM_TEMPERATURE", temperature)), "num_ctx": int(os.environ.get("OLLAMA_NUM_CTX", "16384")),
                        **({"seed": int(os.environ["OLLAMA_SEED"])} if os.environ.get("OLLAMA_SEED") else {})}}   # OLLAMA_SEED: a fixed seed for repeatable runs (number 4, arm B)
    if json_mode:
        body["format"] = "json"
    req = urllib.request.Request(f"{_HOST}/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        # first call after idle can block while the model loads into VRAM
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read())
            LAST_USAGE.update(prompt_tokens=data.get("prompt_eval_count"), output_tokens=data.get("eval_count"))
            return data["message"]["content"] or ""
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        if e.code == 404 and "not found" in detail:
            raise RuntimeError(f"model {MODEL_NAME()!r} not pulled - run: "
                               f"ollama pull {MODEL_NAME()}") from e
        raise RuntimeError(f"Ollama error {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama not reachable at {_HOST} - is the server "
                           f"running? (`ollama serve`)") from e

def _messages(prompt, system, images=None):
    user = {"role": "user", "content": prompt}
    if images:
        user["images"] = images
    return ([{"role": "system", "content": system}] if system else []) + [user]

def _parse_json(txt):
    txt = re.sub(r"^```(json)?|```$", "", txt.strip(), flags=re.M).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else {}

def ask(prompt, system=None, json_mode=False, max_tries=8):
    return _chat(_messages(prompt, system), json_mode=json_mode)

def ask_json(prompt, system=None):
    return _parse_json(ask(prompt, system=system, json_mode=True))

def ask_image(image_path, prompt, system=None, max_tries=8):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return _parse_json(_chat(_messages(prompt, system, images=[b64]),
                             json_mode=True, temperature=0.2))
