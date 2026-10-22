"""Encoding-fidelity unit tests: v4 practice cases (Set 1) and the Appendix A post-test
questions vs the v5 rulebook via the deterministic engine. Case data + expectation
semantics: tests/v4_cases.yaml and tests/v4_posttest_cases.yaml.
Partition rationale: rules/v4-v5-diff-log.md.
Entries with `skip:` are not run (decided at C or D); entries with `xfail:` must fail
(strict) - they record v4-only content, gaps and threshold choices for review.
`expect_consider` and `expect_notes` list consider flags and context notes that must appear.

Run:  .venv/bin/python -m pytest tests/ -v
"""
import os
import sys

import pytest
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prototype"))
import engine  # noqa: E402


def load_cases():
    cases = []
    for name in ("v4_cases.yaml", "v4_posttest_cases.yaml"):
        with open(os.path.join(HERE, name)) as f:
            cases += yaml.safe_load(f)
    return cases


def case_id(c):
    if c.get("set") == "appA":
        return f"appA-ch{c['chapter']}-q{c['case']}-exp{c['v4_answer']}"
    return f"{('ch10' + c['set']) if c.get('set') else 'ch9'}-{c['case']}-exp{c['v4_answer']}"


def as_param(c):
    marks = []
    if c.get("skip"):
        marks.append(pytest.mark.skip(reason=c["skip"]))
    if c.get("xfail"):
        marks.append(pytest.mark.xfail(reason=c["xfail"], strict=True))
    return pytest.param(c, id=case_id(c), marks=marks)


CASES = load_cases()
CRITERIA = engine.load_criteria()


def run_case(case):
    facts = engine.Facts()
    for fact in case["facts"]:
        facts.write(fact["field"], fact["value"],
                    status=fact.get("status", "reported"), turn=0)
    engine.derive(facts, 0)   # runtime parity: meds -> M.anticoagulant etc.
    return engine.evaluate_tree(facts, CRITERIA)


def ids_of(entries):
    return {e["id"] for e in entries}


@pytest.mark.parametrize("case", [as_param(c) for c in CASES])
def test_v4_case(case):
    result = run_case(case)
    fired, esi1, consider = ids_of(result["fired"]), ids_of(result["esi1_indicators"]), ids_of(result["consider"])
    expect = case["expect"]

    if expect == "esi1":
        missing = set(case["expect_rules"]) - esi1
        assert not missing, f"expected ESI-1 indicators {missing} did not fire (got {esi1 or 'none'})"
    elif expect == "floor2":
        assert result["floor"] == "at least ESI-2", \
            f"expected floor 'at least ESI-2', got {result['floor']!r} (fired: {fired or 'none'})"
        missing = set(case["expect_rules"]) - fired
        assert not missing, f"expected rules {missing} did not fire (fired: {fired or 'none'})"
    elif expect == "none":
        assert result["floor"] is None, \
            f"no floor expected (v4 answer {case['v4_answer']}), but {fired} fired -> {result['floor']!r}"
        assert not esi1, f"no ESI-1 indicators expected, but {esi1} fired"
    else:
        pytest.fail(f"unknown expect class {expect!r}")

    for rule in case.get("expect_consider", []):
        assert rule in consider, f"expected consider-flag {rule}, got {consider or 'none'}"
    notes = ids_of(result["notes"])
    for rule in case.get("expect_notes", []):
        assert rule in notes, f"expected context note {rule}, got {notes or 'none'}"


def test_no_supplemented_rule_credits_esi_encoding():
    """Guard: every case that fires B-30 must be explicitly marked supplemented,
    so supplemented-rule behavior is never silently scored as ESI fidelity."""
    for case in CASES:
        if case.get("skip"):
            continue
        result = run_case(case)
        if "B-30.anticoagulated-trauma" in ids_of(result["fired"]):
            assert case.get("supplemented"), \
                f"case {case['case']} fires B-30 but is not marked supplemented"
