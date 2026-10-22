"""An answer that the caregiver does not know closes the question (webapp/server.py, record_unknown): the phrases it
recognises, including a temperature nobody measured (#115, persona run of 18 Oct 2026, P12), and an answer it must not take for
one (a medicines answer).    Run:  .venv/bin/python -m pytest tests/ -v
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("LLM_BACKEND", "ollama")   # importing the web app loads a model backend; this test calls no model
sys.path.insert(0, os.path.join(ROOT, "webapp"))
import server  # noqa: E402


def test_dont_know_phrases():
    for text in ("I don't know.", "not sure", "no idea", "I haven't taken her temperature.", "We didn't check his temperature"):
        assert server.DONT_KNOW_RE.search(text), text


def test_answers_that_are_not_dont_know():
    for text in ("I haven't taken any medicine.", "No fever.", "He takes warfarin."):
        assert not server.DONT_KNOW_RE.search(text), text
