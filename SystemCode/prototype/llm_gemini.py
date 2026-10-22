"""Gemini backend: key from the GEMINI_API_KEY env var (set directly or via .env at
the repo root; comma-separate multiple keys) or legacy gemini_api_key.txt (one key
per line); paced + retried. Import through llm.py, which picks the backend."""
import os, time, json, re

_REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

MODELS = [m.strip() for m in os.environ.get("GEMINI_MODELS",
    "gemini-3.6-flash,gemini-3.5-flash,gemini-3-flash-preview,gemini-flash-latest,"
    "gemini-2.5-flash-lite,gemini-2.5-flash").split(",")]
_model_idx = [0]
def MODEL_NAME(): return MODELS[_model_idx[0]]
def rotate_model():
    if _model_idx[0] + 1 < len(MODELS):
        _model_idx[0] += 1
        print(f"    [rotating model to {MODEL_NAME()}]", flush=True)
        return True
    return False
_PACE_SECONDS = float(os.environ.get("GEMINI_PACE", 15))
_last_call = [0.0]

def _real(keys):
    """Drop Doppler placeholders ("paste-..."), so a config whose key is not yet pasted does not shadow a real key elsewhere."""
    return [k.strip() for k in keys if k.strip() and not k.strip().startswith("paste-")]


def _keys():
    keys = _real(os.environ.get("GEMINI_API_KEY", "").split(","))
    if not keys:                                   # the shell or Doppler gave only placeholders: read the repo's .env directly
        env_path = os.path.join(_REPO_ROOT, ".env")
        if os.path.exists(env_path):
            for ln in open(env_path):
                if ln.strip().startswith("GEMINI_API_KEY="):
                    keys = _real(ln.split("=", 1)[1].strip().strip("'\"").split(","))
    if keys:
        return keys
    # legacy fallback: gemini_api_key.txt at the repo root, one key per line
    path = os.path.join(_REPO_ROOT, "gemini_api_key.txt")
    with open(path) as f:
        return _real([ln for ln in f])

_keys_list = None
_key_idx = [0]
_client = None
def client():
    global _client, _keys_list
    if _keys_list is None:
        _keys_list = _keys()
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=_keys_list[_key_idx[0]])
    return _client

def rotate_key():
    """Switch to the next key. Quotas are counted per Google Cloud project, not per key: a second key helps only when it
    was created in a second project (two keys of one project share one quota; Ye Htut Lwin, 15 Oct 2026)."""
    global _client
    if _key_idx[0] + 1 < len(_keys_list or []):
        _key_idx[0] += 1
        _client = None
        print(f"    [daily quota hit - rotating to key #{_key_idx[0]+1}]", flush=True)
        return True
    return False

def ask(prompt, system=None, json_mode=False, max_tries=8):
    from google.genai import types
    cfg = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json" if json_mode else None,
        temperature=float(os.environ.get("LLM_TEMPERATURE", 0.4)))
    for attempt in range(max_tries):
        wait = _PACE_SECONDS - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        try:
            r = client().models.generate_content(model=MODEL_NAME(), contents=prompt, config=cfg)
            _last_call[0] = time.time()
            _status("")
            return r.text or ""
        except Exception as e:
            _last_call[0] = time.time()
            msg = str(e)
            if "PerDay" in msg or "NOT_FOUND" in msg or "no longer available" in msg:
                if rotate_model() or rotate_key():
                    continue
                raise RuntimeError("Gemini daily quota exhausted on every listed model and key - it resets at midnight Pacific time (3 pm in Singapore)")
            if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg:
                # the model is overloaded, not our quota: move to the next model at once rather than wait on this one
                # (15 Oct 2026: gemini-3.6-flash and 3.5-flash answered 503 for ten minutes while 3-flash-preview worked;
                # at 00:50 SGT all six listed models answered 503 for a quarter of an hour: then start the list again and wait)
                if rotate_model():
                    print(f"    [model overloaded; switching to {MODEL_NAME()}]", flush=True)
                    _status(f"the model provider reports high demand; switching to {MODEL_NAME()}")
                    continue
                _model_idx[0] = 0
                backoff = 30 * (attempt + 1)
                print(f"    [every model overloaded; waiting {backoff:.0f}s, then from {MODEL_NAME()} again]", flush=True)
                _status(f"the model provider reports high demand on every model; waiting {backoff:.0f} seconds (attempt {attempt + 2} of {max_tries})")
                time.sleep(backoff)
                continue
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "503" in msg:
                if attempt >= 1 and rotate_model():       # a second limit in a row on the same model: try the next model
                    print(f"    [rate-limited twice; switching to {MODEL_NAME()}]", flush=True)
                    _status(f"the model provider is rate-limiting us; switching to {MODEL_NAME()}")
                    continue
                backoff = 30 * (attempt + 1)
                m = re.search(r"retry in ([0-9.]+)s", msg, re.I)
                if m: backoff = max(backoff, float(m.group(1)) + 1)
                print(f"    [rate-limited; waiting {backoff:.0f}s]", flush=True)
                _status(f"the model provider is rate-limiting us; retrying in {backoff:.0f} seconds (attempt {attempt + 2} of {max_tries})")
                time.sleep(backoff)
                continue
            raise
    raise RuntimeError("Gemini: retries exhausted")


def _status(text):
    try:
        import llm
        llm.STATUS["text"] = text
    except Exception:
        pass

def ask_image(image_path, prompt, system=None, max_tries=8):
    from google.genai import types
    with open(image_path, "rb") as f:
        data = f.read()
    mime = "image/png" if image_path.lower().endswith("png") else "image/jpeg"
    cfg = types.GenerateContentConfig(system_instruction=system,
                                      response_mime_type="application/json", temperature=0.2)
    for attempt in range(max_tries):
        wait = _PACE_SECONDS - (time.time() - _last_call[0])
        if wait > 0: time.sleep(wait)
        try:
            r = client().models.generate_content(model=MODEL_NAME(), config=cfg,
                contents=[types.Part.from_bytes(data=data, mime_type=mime), prompt])
            _last_call[0] = time.time()
            txt = re.sub(r"^```(json)?|```$", "", (r.text or "").strip(), flags=re.M).strip()
            try: return json.loads(txt)
            except json.JSONDecodeError:
                m = re.search(r"\{.*\}", txt, re.S)
                return json.loads(m.group(0)) if m else {}
        except Exception as e:
            _last_call[0] = time.time(); msg = str(e)
            if "PerDay" in msg or "NOT_FOUND" in msg or "no longer available" in msg:
                if rotate_model() or rotate_key(): continue
                raise RuntimeError("DAILY QUOTA EXHAUSTED on all models and keys")
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "503" in msg:
                backoff = 30 * (attempt + 1)
                m2 = re.search(r"retry in ([0-9.]+)s", msg, re.I)
                if m2: backoff = max(backoff, float(m2.group(1)) + 1)
                print(f"    [rate-limited; waiting {backoff:.0f}s]", flush=True)
                time.sleep(backoff); continue
            raise
    raise RuntimeError("Gemini: retries exhausted")

def ask_json(prompt, system=None):
    txt = ask(prompt, system=system, json_mode=True)
    txt = re.sub(r"^```(json)?|```$", "", txt.strip(), flags=re.M).strip()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0)) if m else {}
