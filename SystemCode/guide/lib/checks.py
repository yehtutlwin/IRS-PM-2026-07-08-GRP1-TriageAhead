"""Read-only checks. Each returns (ok, detail). Nothing here changes the machine."""
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request


def tool(name):
    path = shutil.which(name)
    return (True, f"found at {path}") if path else (False, f"{name} is not on the PATH")


def file_present(path, what=None):
    what = what or os.path.relpath(path)
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return True, f"{what} is present"
    return False, f"{what} is missing"


def dir_present(path, what=None):
    what = what or os.path.relpath(path)
    return (True, f"{what} is present") if os.path.isdir(path) else (False, f"{what} is missing")


def system_python_has(module):
    """The Python running the guide can import `module` ("a, b" for several)."""
    r = subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True, text=True)
    names = [m.strip() for m in module.split(",")]
    if r.returncode == 0:
        return True, f"the {' and '.join(names)} module{'s are' if len(names) > 1 else ' is'} available"
    missing = (r.stderr.strip().splitlines() or ["?"])[-1].split("'")[1::2] or [module]
    return False, f"the {missing[0]} module is missing from {sys.executable}"


def guide_python():
    """The Python that started the guide, as the reader can type it: its short name when that name on the
    PATH is this same interpreter (python3.12), else its full path."""
    exe = os.path.realpath(sys.executable)
    name = os.path.basename(sys.executable)
    found = shutil.which(name)
    if found and os.path.realpath(found) == exe:
        return name
    return sys.executable


def venv_python(root):
    for p in (os.path.join(root, ".venv", "bin", "python"), os.path.join(root, ".venv", "Scripts", "python.exe")):
        if os.path.exists(p):
            return p
    return None


def venv_present(root):
    """The venv exists, runs, and was made with the same Python as the guide (same major.minor)."""
    py = venv_python(root)
    if not py:
        return False, "no .venv folder in SystemCode yet"
    r = subprocess.run([py, "-c", "import sys; print(sys.version.split()[0])"], capture_output=True, text=True)
    if r.returncode != 0:
        return False, ".venv exists but its Python does not run"
    v = r.stdout.strip()
    mine = "%d.%d" % sys.version_info[:2]
    if ".".join(v.split(".")[:2]) != mine:
        return False, f".venv was made with Python {v}; the guide runs on Python {mine} ({guide_python()})"
    return True, f".venv is present (Python {v}, the same as the guide's)"


def venv_mismatch(root):
    ok, detail = venv_present(root)
    return (not ok) and "was made with" in detail


_imported = set()   # (venv, module) pairs that imported once; re-checked only if .venv is made again


def venv_imports(root, modules):
    """Every module in `modules` imports inside .venv. Names those that do not."""
    py = venv_python(root)
    if not py:
        return False, "no .venv yet"
    try:
        made = os.path.getmtime(os.path.join(root, ".venv", "pyvenv.cfg"))
    except OSError:
        made = 0
    todo = [m for m in modules if (made, m) not in _imported]
    if not todo:
        return True, "installed in .venv: " + ", ".join(modules)
    code = ("import importlib, sys\n"
            "bad = []\n"
            "for m in sys.argv[1:]:\n"
            "    try: importlib.import_module(m)\n"
            "    except Exception: bad.append(m)\n"
            "print(' '.join(bad))\n")
    r = subprocess.run([py, "-c", code, *todo], capture_output=True, text=True)
    bad = r.stdout.split()
    if r.returncode != 0:
        return False, "could not run .venv's Python"
    _imported.update((made, m) for m in todo if m not in bad)
    if bad:
        return False, "not installed in .venv: " + ", ".join(bad)
    return True, "installed in .venv: " + ", ".join(modules)


def not_under_windows_mount():
    cwd = os.getcwd()
    if cwd.startswith("/mnt/") and os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        return False, f"the repository is under {cwd[:7]}..., the Windows file system"
    return True, "the repository is on a Linux or macOS file system"


def port_free(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex((host, port)) != 0


def first_free_port(start, count=20):
    for p in range(start, start + count):
        if port_free(p):
            return p
    raise OSError(f"no free port between {start} and {start + count - 1}")


_recognised = {}   # signature -> ports where that app answered; those are not fetched again, only tested


def _get(port, path, limit=200000):
    # a cold app can take a few seconds to build its first page; giving up early leaves it
    # writing into a closed connection and printing a trace for every retry
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=20) as r:
            return r.status, r.read(limit).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def app_answering(ports, signature, path="/", probe=None, probe_what=""):
    """One of `ports` serves a page containing `signature` (the app we are waiting for, not whatever
    else listens there) and, when `probe` is given, answers that read-only path with 200.
    Returns (ok, detail, port)."""
    seen = _recognised.setdefault(signature, set())
    other, lacking = [], []
    for port in ports:
        if port_free(port):
            seen.discard(port)
            continue
        if port not in seen:
            try:
                code, body = _get(port, path)
            except Exception:
                code, body = None, ""
            if code != 200 or signature not in body:
                other.append(port)
                continue
            seen.add(port)
        if probe:
            try:
                code, _ = _get(port, probe, 2000)
            except Exception:
                code = None
            if code != 200:
                lacking.append(port)
                continue
        return True, f"answering on port {port}", port
    if lacking:
        return False, f"the app on port {lacking[0]} has no {probe_what}. It may be another copy of the app.", None
    if other:
        return False, f"port {other[0]} is in use by something else", None
    return False, f"nothing answers on port {ports[0]}", None


def dotenv(path):
    """The KEY=VALUE lines of a .env file, as the apps read them (comments and blank lines skipped)."""
    out = {}
    try:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith("#") or "=" not in ln:
                    continue
                k, v = ln.split("=", 1)
                out[k.strip().removeprefix("export ").strip()] = v.strip().strip("'\"")
    except OSError:
        pass
    return out


def ollama_models(host="http://localhost:11434"):
    """The models an Ollama server lists, or None when no server answers."""
    import json
    try:
        with urllib.request.urlopen(host.rstrip("/") + "/api/tags", timeout=3) as r:
            return [m.get("name", "") for m in json.load(r).get("models", [])]
    except Exception:
        return None
