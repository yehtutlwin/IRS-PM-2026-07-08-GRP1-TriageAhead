"""The nurse page's card of facts not collected (issue #112): it lists a report field only when the interview would still
ask it of this patient, so a question that does not apply, such as a pregnancy question for a man, is never shown as a gap.
Run:  .venv/bin/python -m pytest tests/ -v
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.environ.setdefault("LLM_BACKEND", "ollama")   # importing the web app loads a model backend; rendering the page calls no model
sys.path.insert(0, os.path.join(ROOT, "webapp"))
import server  # noqa: E402

SESSION = os.path.join(ROOT, "experiments", "out", "sessions-hand-played-2026-10-15", "OTTER-8193.json")


def not_collected_card(sid, tmp_path, monkeypatch):
    """Render the nurse page of a recorded session from a copy, and return the items of its not-collected card."""
    shutil.copy(SESSION, tmp_path / f"{sid}.json")
    monkeypatch.setattr(server.cli, "SESS", str(tmp_path))
    html = server.report_page(sid)
    m = re.search(r"<h2>Not collected.*?<p class=\"muted\">(.*?)</p>", html, re.S)
    return m.group(1).split(", ") if m else []


def test_not_collected_lists_only_fields_that_apply(tmp_path, monkeypatch):
    # OTTER-8193: an 87-year-old man who fell. The fall height and the immune status apply to him and were not collected;
    # pregnancy, postpartum and vaginal bleeding cannot apply to a man, and the suspicion of acute coronary syndrome
    # needs chest pain, which was denied.
    assert not_collected_card("OTTER-8193", tmp_path, monkeypatch) == ["fall height meters", "immunocompromised"]
