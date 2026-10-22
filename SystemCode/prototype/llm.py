"""LLM seam: every caller imports this module; LLM_BACKEND (.env or shell) picks
who answers - "gemini" (default, cloud), "ollama" (local server, no quota) or "claude" (Anthropic API, #82).
All backends expose the same surface: ask / ask_json / ask_image / MODEL_NAME; claude also USAGE and cost()."""
import os

_REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def _load_dotenv():
    """Load repo-root .env into os.environ (real env vars win). KEY=VALUE lines;
    supports comments, blank lines, `export ` prefixes and single/double quotes."""
    path = os.path.join(_REPO_ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            k = k.strip().removeprefix("export ").strip()
            v = v.strip().strip("'\"")
            if k:
                os.environ.setdefault(k, v)
_load_dotenv()

STATUS = {"text": ""}   # what the backend is doing while a call is slow (rate-limited, retrying); the web app shows it (#79)

BACKEND = os.environ.get("LLM_BACKEND", "gemini").strip().lower()
if BACKEND == "ollama":
    from llm_ollama import ask, ask_json, ask_image, MODEL_NAME
elif BACKEND == "gemini":
    from llm_gemini import ask, ask_json, ask_image, MODEL_NAME
elif BACKEND == "claude":
    from llm_claude import ask, ask_json, ask_image, MODEL_NAME, USAGE, cost
else:
    raise RuntimeError(f"unknown LLM_BACKEND {BACKEND!r} - use 'gemini', 'ollama' or 'claude'")
