"""The derived agenda and the engine's open-field selection (knowledge base v2, issue #57).
The agenda is derived from the rules and the field file by rules/derive.py; these tests pin what the interview may
ask on a few fact patterns, so a change in the rules or the field file that changes the questions shows up here.
Run:  .venv/bin/python -m pytest tests/ -v
"""
import os, subprocess, sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import engine  # noqa: E402


def facts_of(pairs):
    f = engine.Facts()
    for k, v in pairs:
        f.write(k, v, status="reported", turn=0)
    engine.derive(f, 0)
    return f


def opened(pairs, attempts=None):
    return [o["field"] for o in engine.open_fields(facts_of(pairs), attempts or {})]


def test_derived_files_are_current():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "rules", "derive.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_first_questions_are_the_danger_screen_then_the_complaint():
    first = opened([])[:6]
    assert first[:4] == ["danger_signs.responsive", "danger_signs.chest_pain_now", "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding"]
    assert first[4] == "complaint.category"


def test_no_injury_means_no_injury_questions():
    o = opened([("complaint.category", "fever"), ("patient.age", 30), ("patient.sex", "male")])
    assert not any(f.startswith(("E.fall", "limb.", "E.head", "E.loc")) for f in o)


def test_a_fall_opens_fall_height_head_strike_and_limb_signs_and_blood_thinner():
    o = opened([("complaint.category", "injury"), ("E.mechanism", "fall"), ("patient.age", 70), ("patient.sex", "female")])
    for f in ("E.fall_height_meters", "E.head_strike", "E.loc", "limb.numb_tingling", "M.anticoagulant", "history.thrombocytopenia_or_clotting_disorder"):
        assert f in o, f
    assert "E.vehicle_ejection" not in o


def test_pregnancy_is_not_asked_of_a_man_or_a_woman_of_sixty():
    assert "history.pregnant" not in opened([("patient.sex", "male"), ("patient.age", 30)])
    assert "history.pregnant" not in opened([("patient.sex", "female"), ("patient.age", 60)])
    assert "history.pregnant" in opened([("patient.sex", "female"), ("patient.age", 30)])


def test_abdominal_pain_in_a_woman_opens_the_handbook_questions():
    o = opened([("complaint.category", "abdominal_pain"), ("patient.sex", "female"), ("patient.age", 28)])
    for f in ("history.pregnant", "complaint.vaginal_bleeding", "complaint.pain_refractory_constant_or_maximal_onset",
              "E.abdominal_trauma", "complaint.unilateral_lower_quadrant_pain", "complaint.possible_ectopic_pregnancy"):
        assert f in o, f
    assert "complaint.testicular_or_scrotal_pain" not in o


def test_sensitive_single_fact_rules_are_never_asked_unprompted():
    o = opened([("complaint.category", "other"), ("patient.age", 40), ("patient.sex", "female")])
    for f in ("complaint.sexual_assault", "complaint.needle_stick_healthcare_worker", "complaint.severe_psychological_distress", "complaint.psychotic_or_violent"):
        assert f not in o, f


def test_fever_opens_the_immune_and_transplant_questions():
    o = opened([("complaint.category", "fever"), ("complaint.fever", True), ("patient.age", 45), ("patient.sex", "male")])
    for f in ("history.immunocompromised", "history.transplant_recipient_or_listed", "complaint.infection_signs", "vitals.temp_c"):
        assert f in o, f


def test_a_probable_blood_thinner_is_confirmed_alone():
    f = facts_of([("complaint.category", "injury"), ("E.mechanism", "fall"), ("M.medications", ["a small pill to thin his blood"])])
    assert f.resolve("M.anticoagulant.status") == "probable"
    o = engine.open_fields(f, {})
    conf = [x for x in o if x["confirm"]]
    assert conf and conf[0]["field"] == "M.anticoagulant"


def test_stored_and_exhausted_fields_drop_out():
    pairs = [("danger_signs.responsive", True), ("danger_signs.chest_pain_now", False), ("danger_signs.breathing_difficulty", False), ("danger_signs.heavy_bleeding", False)]
    o = opened(pairs, attempts={"complaint.category": 3})
    assert not any(f.startswith("danger_signs.") for f in o)
    assert "complaint.category" not in o


def test_every_offered_field_has_everyday_wording():
    fields = engine.load_fields()
    for e in engine.open_fields(engine.Facts(), {}):
        assert fields[e["field"]].get("ask"), e["field"]


def test_reachability_of_the_practice_cases_does_not_regress():
    """Model-free reachability (experiments/reachability.py): how many practice-case facts a gate keeps the interview from
    ever asking for. The number is frozen here so that a change to a gate or a policy that shuts a question shows up."""
    sys.path.insert(0, os.path.join(ROOT, "experiments"))
    import reachability
    cases, rows, cnt, per, examples, full, clean = reachability.run()
    assert cnt["never opened"] <= 30, dict(cnt)      # 13 Oct 2026, 185 cases: bridges v2 (eye findings asked one by one, heavy bleeding one field, the danger screen feeds B-01); see experiments/out/reachability.md
    assert clean >= 147, clean


def test_stated_only_guard_drops_deductions_and_keeps_statements():
    import extraction
    kept, dropped = extraction.guard([{"field": "history.pregnant", "value": False}, {"field": "patient.age", "value": 60}], "She's an old lady, 60 years old.")
    assert [w["field"] for w in dropped] == ["history.pregnant"] and [w["field"] for w in kept] == ["patient.age"]
    kept, dropped = extraction.guard([{"field": "history.pregnant", "value": False}], "No, she is not pregnant.")
    assert not dropped
    kept, dropped = extraction.guard([{"field": "patient.has_ovaries", "value": True}], "She is a 40-year-old woman.")
    assert dropped and not kept


def test_a_limb_complaint_opens_the_limb_warning_signs_without_a_known_mechanism():
    # persona run of 18 Oct 2026 (P13, a cast too tight, handbook case 50): the family did not know how the wrist broke, so
    # only the complaint says it is a limb; the warning signs that let B-24 fire must still be asked
    o = opened([("complaint.category", "limb_pain_or_swelling"), ("patient.age", 35), ("patient.sex", "female")])
    for f in ("limb.numb_tingling", "limb.cold_pale_blue", "limb.cannot_move_digits", "limb.cast_too_tight"):
        assert f in o, f
