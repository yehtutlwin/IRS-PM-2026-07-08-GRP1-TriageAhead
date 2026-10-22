"""Seam tests for the bridges (rules/bridges.yaml): facts are written exactly as the extraction step would write
them (everyday-sign fields), engine.derive() translates, the rules fire. This is the layer between the practice-case
tests (rule-level facts injected directly) and the persona runs (a language model in the loop).

Run:  .venv/bin/python -m pytest tests/ -v
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "prototype"))
import engine  # noqa: E402

CRITERIA = engine.load_criteria()


def evaluate(writes):
    facts = engine.Facts()
    for field, value in writes:
        facts.write(field, value, status="reported", turn=0)
    engine.derive(facts, 0)
    return facts, engine.evaluate_tree(facts, CRITERIA)


def fired(tree):
    return {r["id"] for r in tree["fired"]}


def considered(tree):
    return {r["id"] for r in tree["consider"]}


# ---- BR-05 stroke signs

def test_fast_bridge_fires_b05_even_resolved():
    """v4 case 44 at the extractor seam: resolved episode, FAST elements true."""
    facts, tree = evaluate([
        ("complaint.category", "neuro_symptoms"),
        ("stroke.speech_change", True),
        ("stroke.arm_weakness", True),
        ("stroke.face_droop", False),
        ("identity.dob", "15 Mar 1938"),
    ])
    assert facts.resolve("complaint.stroke_signs") is True
    assert tree["floor"] == "at least ESI-2"
    assert "B-05.stroke-signs" in fired(tree)


def test_fast_all_negative_no_floor():
    facts, tree = evaluate([
        ("complaint.category", "dizziness"),
        ("stroke.face_droop", False),
        ("stroke.arm_weakness", False),
        ("stroke.speech_change", False),
    ])
    assert facts.resolve("complaint.stroke_signs") is None
    assert tree["floor"] is None and not tree["esi1_indicators"]


# ---- BR-24 limb warning signs

def test_limb_bridge_fires_b24():
    """v4 case 50 at the extractor seam: cast too tight, digits impaired."""
    facts, tree = evaluate([
        ("complaint.category", "injury"),
        ("limb.cast_too_tight", True),
        ("limb.cannot_move_digits", True),
    ])
    assert facts.resolve("complaint.extremity_neurovascular_compromise") is True
    assert tree["floor"] == "at least ESI-2"
    assert "B-24.extremity-neurovascular-compromise" in fired(tree)


# ---- BR-01 / BR-29 / EN altered mental status

def test_ams_baseline_bridge_fires_b01():
    facts, tree = evaluate([("ams.changed_from_baseline", True)])
    assert "B-01.new-altered-mental-status" in fired(tree)
    assert tree["floor"] == "at least ESI-2"


def test_ams_bridge_pediatric_also_fires_b29():
    facts, tree = evaluate([
        ("ams.changed_from_baseline", True),
        ("patient.age", 5),
    ])
    assert {"B-01.new-altered-mental-status", "B-29.pediatric-subtle-ams"} <= fired(tree)


def test_changed_from_baseline_entails_altered_now_for_headache_rule():
    """B-34 reads the present-state fact; a change from baseline implies it (EN.changed-baseline-is-altered-now)."""
    facts, tree = evaluate([
        ("complaint.category", "headache"),
        ("ams.changed_from_baseline", True),
    ])
    assert facts.resolve("obs.confusion_lethargy_disorientation") is True
    assert "B-34.headache-red-flags" in fired(tree)


def test_not_responding_fires_b01_through_the_danger_screen():
    """BR-01.not-responding: 'no' to 'awake and responding normally' is altered mental status for the floor."""
    facts, tree = evaluate([("danger_signs.responsive", False)])
    assert facts.resolve("obs.new_confusion_lethargy_disorientation") is True
    assert "B-01.new-altered-mental-status" in fired(tree)
    assert tree["floor"] == "at least ESI-2"
    assert not tree["esi1_indicators"]          # the level-1 rule still needs a clinician's AVPU


def test_responsive_yes_feeds_nothing():
    facts, tree = evaluate([("danger_signs.responsive", True)])
    assert facts.resolve("obs.new_confusion_lethargy_disorientation") is None
    assert tree["floor"] is None


# ---- BR-13 / EN heavy vaginal bleeding

def test_heavy_bleeding_bridge_fires_b13():
    facts, tree = evaluate([
        ("complaint.heavy_vaginal_bleeding", True),
        ("history.postpartum", True),
    ])
    assert facts.resolve("complaint.postpartum_hemorrhage") is True
    assert "B-13.postpartum-hemorrhage" in fired(tree)


def test_heavy_bleeding_while_pregnant_is_not_postpartum_hemorrhage():
    """The handbook's pregnant sentence adds abnormal vital signs and infection (B-39); the bridge no longer fires for it."""
    facts, tree = evaluate([
        ("complaint.heavy_vaginal_bleeding", True),
        ("history.pregnant", True),
    ])
    assert facts.resolve("complaint.postpartum_hemorrhage") is None
    assert "B-13.postpartum-hemorrhage" not in fired(tree)


def test_heavy_bleeding_entails_vaginal_bleeding_for_b21():
    facts, tree = evaluate([
        ("complaint.category", "abdominal_pain"),
        ("complaint.heavy_vaginal_bleeding", True),
    ])
    assert facts.resolve("complaint.vaginal_bleeding") is True
    assert "B-21.abdo-pain-vaginal-bleeding" in considered(tree)   # B-21 is a consider flag


# ---- BR-28 eye findings count

def test_eye_findings_are_counted_and_two_raise_the_consider_flag():
    facts, tree = evaluate([
        ("complaint.category", "eye_problem"),
        ("eye.red", True),
        ("eye.injury", True),
        ("eye.floaters_or_flashes", False),
    ])
    assert facts.resolve("complaint.atso_elements_count") == 2
    assert "B-28.ocular-high-risk-constellation" in considered(tree)
    assert tree["floor"] is None                   # a consider flag, not a floor


def test_eye_count_updates_as_answers_arrive_but_never_overwrites_a_stated_count():
    facts = engine.Facts()
    facts.write("complaint.category", "eye_problem", status="reported", turn=0)
    facts.write("eye.red", True, status="reported", turn=0)
    engine.derive(facts, 0)
    assert facts.resolve("complaint.atso_elements_count") == 1
    facts.write("stroke.vision_change", True, status="reported", turn=1)
    engine.derive(facts, 1)
    assert facts.resolve("complaint.atso_elements_count") == 2
    stated = engine.Facts()
    stated.write("complaint.atso_elements_count", 3, status="reported", turn=0)
    stated.write("eye.red", True, status="reported", turn=0)
    engine.derive(stated, 0)
    assert stated.resolve("complaint.atso_elements_count") == 3


def test_vision_change_feeds_both_stroke_and_eye_bridges():
    facts, tree = evaluate([
        ("complaint.category", "eye_problem"),
        ("stroke.vision_change", True),
    ])
    assert facts.resolve("complaint.stroke_signs") is True
    assert facts.resolve("complaint.atso_elements_count") == 1


# ---- EN breathing

def test_breathing_difficulty_now_entails_shortness_of_breath_for_b38():
    facts, tree = evaluate([
        ("danger_signs.breathing_difficulty", True),
        ("history.pregnant", True),
    ])
    assert facts.resolve("complaint.shortness_of_breath") is True
    assert "B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache" in fired(tree)


# ---- derivations in code and the add-only rule

def test_age_derivation_unblocks_b27():
    """B-27 was 'partially reachable: missing patient.age' - DOB from wrap-up closes it."""
    facts, tree = evaluate([
        ("E.mechanism", "fall"),
        ("identity.dob", "02 Jan 1939"),
    ])
    assert facts.resolve("patient.age") >= 55
    assert "B-27.geriatric-trauma-caution" in {r["id"] for r in tree["notes"]}
    assert tree["floor"] is None   # context note only, floor unchanged


def test_age_derivation_never_overwrites_reported_age():
    facts, tree = evaluate([
        ("patient.age", 30),
        ("identity.dob", "02 Jan 1939"),
    ])
    assert facts.resolve("patient.age") == 30


def test_bridges_do_not_downgrade():
    """A bridge target already written is left alone (add-only discipline)."""
    facts = engine.Facts()
    facts.write("complaint.stroke_signs", False, status="reported", turn=0)
    facts.write("stroke.face_droop", True, status="reported", turn=0)
    engine.derive(facts, 0)
    # existing explicit value wins; bridge must not overwrite in either direction
    assert facts.resolve("complaint.stroke_signs") is False


def test_every_bridge_has_a_kind_and_reads_defined_fields():
    import yaml
    fields = yaml.safe_load(open(os.path.join(HERE, "..", "rules", "fields.yaml")))["fields"]
    for b in engine.load_bridges():
        assert b["kind"] in ("signs", "count", "entails"), b["id"]
        assert b["target"] in fields, b["id"]
        for f in b.get("count", []):
            assert f in fields, (b["id"], f)


def test_prompt_gives_each_enum_value_with_its_meaning():
    """The answer-to-facts step is given value_meanings, not bare value names (13 Oct 2026)."""
    import extraction
    line = extraction._line("E.mechanism", engine.load_fields()["E.mechanism"])
    assert "fall = a fall, slip or trip, from any height" in line
    assert "penetrating_trauma = stabbed, shot or impaled" in line


def test_age_group_is_derived_from_the_age_with_the_handbook_bands():
    """patient.age_group is never asked: derived from days, months or years (ESI v5 p.24, Table 6-1); A-13 reads it."""
    facts, tree = evaluate([("patient.age_months", 3), ("obs.flaccid", True)])
    assert facts.resolve("patient.age_group") == "infant"
    assert "A-13.flaccid-infant" in {r["id"] for r in tree["esi1_indicators"]}
    assert facts.resolve("patient.age") == 0
    for age, band in ((0.5, "infant"), (6, "child"), (40, "adult"), (70, "older_adult")):
        f, _ = evaluate([("patient.age", age)])
        assert f.resolve("patient.age_group") == band, (age, band)
    stated, _ = evaluate([("patient.age", 2), ("patient.age_group", "child")])
    assert stated.resolve("patient.age_group") == "child"     # a stated band is never overwritten
    assert stated.resolve("patient.age_months") == 24          # months from whole years, marked probable



# ---- interview design v2 (#63, 14 Oct 2026): the pre-arrival stage, the bundling cap, the denial guard

def test_pre_arrival_stage_holds_the_floor_setting_questions_and_identity():
    pre = engine.pre_arrival_fields()
    for f in ("danger_signs.responsive", "complaint.category", "patient.age", "M.anticoagulant", "complaint.pain_rating",
              "M.medications", "A.allergies", "history.conditions", "history.immunocompromised", "identity.name", "identity.dob"):
        assert f in pre, f
    after = engine.pre_arrival_fields(floor_set=True)     # the floor is at least ESI-2: only the essentials remain
    assert "M.anticoagulant" not in after and "complaint.pain_rating" not in after and "M.medications" in after and "identity.dob" in after
    for f in ("L.last_intake", "E.head_strike", "complaint.atso_elements_count", "eye.red", "M.beta_blocker"):
        assert f not in pre, f          # flags, notes and the rest of the history continue after the report is ready


def test_a_bundle_holds_at_most_two_yes_no_questions():
    four = ["danger_signs.responsive", "danger_signs.chest_pain_now", "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding"]
    assert engine.cap_yes_no(four, 2) == four[:2]
    mixed = ["complaint.category", "danger_signs.chest_pain_now", "patient.age", "danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding"]
    assert engine.cap_yes_no(mixed, 2) == ["complaint.category", "danger_signs.chest_pain_now", "patient.age", "danger_signs.breathing_difficulty"]


def test_guard_drops_a_denial_of_something_the_answer_does_not_address():
    """Issue #80: 'he has no pain' must not become 'no' to trouble breathing or heavy bleeding."""
    import extraction
    writes = [{"field": "danger_signs.responsive", "value": True, "quote": "He is awake and talking normally"},
              {"field": "danger_signs.chest_pain_now", "value": False, "quote": "He has no pain"},
              {"field": "danger_signs.breathing_difficulty", "value": False, "quote": "He has no pain"},
              {"field": "danger_signs.heavy_bleeding", "value": False, "quote": "He has no pain"}]
    asked = [w["field"] for w in writes]
    kept, dropped = extraction.guard(writes, "He is awake and talking normally. He has no pain.", asked)
    assert [w["field"] for w in kept] == ["danger_signs.responsive", "danger_signs.chest_pain_now"]
    assert {w["field"] for w in dropped} == {"danger_signs.breathing_difficulty", "danger_signs.heavy_bleeding"}
    kept, dropped = extraction.guard([{"field": "danger_signs.breathing_difficulty", "value": False}], "No, his breathing is fine, no trouble at all.", ["danger_signs.breathing_difficulty"])
    assert kept and not dropped          # a denial that addresses the field passes
    two = [{"field": "infection.rash", "value": False}, {"field": "infection.travel_14d", "value": False}]
    kept, dropped = extraction.guard(two, "No.", ["infection.rash", "infection.travel_14d"])
    assert len(kept) == 2 and not dropped   # a bare 'no' answers the question as asked
    kept, dropped = extraction.guard([{"field": "complaint.fever", "value": True, "quote": "burning hot"}], "She feels a bit warm.")
    assert dropped and dropped[0]["why"] == "quote not in the answer"


def test_a_confirmed_blood_thinner_is_added_to_the_medicine_list():
    facts, tree = evaluate([("E.mechanism", "fall"), ("M.medications", []), ("confirm.M.anticoagulant", "warfarin")])
    assert "warfarin" in facts.resolve("M.medications")
    f2, _ = evaluate([("M.medications", ["blood thinner", "bp pill"]), ("confirm.M.anticoagulant", "warfarin")])
    assert f2.resolve("M.medications") == ["blood thinner (warfarin)", "bp pill"]     # named on the vague item, not a second item
    assert facts.resolve("M.anticoagulant.status") == "confirmed" and "B-30.anticoagulated-trauma" in fired(tree)


def test_after_the_report_only_questions_the_nurse_reads_remain():
    keep = engine.after_report_fields()
    for f in ("L.last_intake", "E.head_strike", "E.loc", "infection.travel_14d", "M.beta_blocker", "history.recent_covid_infection", "eye.red"):
        assert f in keep, f
    for f in ("E.fall_height_meters", "limb.numb_tingling", "complaint.compartment_syndrome_symptoms", "complaint.transplant_rejection_signs"):
        assert f not in keep, f          # their only consumers set a level, which the floor already is


def test_same_as_usual_is_a_denial_of_a_change_from_baseline():
    import extraction
    kept, dropped = extraction.guard([{"field": "complaint.pain_rating", "value": 7}, {"field": "ams.changed_from_baseline", "value": False}],
                                     "pain 7. no, same as usual", ["ams.changed_from_baseline", "complaint.pain_rating"])
    assert {w["field"] for w in kept} == {"complaint.pain_rating", "ams.changed_from_baseline"} and not dropped


def test_a_bp_pill_is_not_a_beta_blocker():
    import extraction
    kept, dropped = extraction.guard([{"field": "M.beta_blocker", "value": True}], "warfarin and a bp pill, dont know the name", ["M.anticoagulant"])
    assert dropped and not kept
    kept, dropped = extraction.guard([{"field": "M.beta_blocker", "value": True}], "he takes bisoprolol", ["M.medications"])
    assert kept


def test_a_quote_of_its_own_counts_as_addressing_and_a_shared_quote_does_not():
    import extraction
    kept, dropped = extraction.guard([{"field": "ams.changed_from_baseline", "value": False, "quote": "he's himself"},
                                      {"field": "complaint.pain_rating", "value": 7, "quote": "maybe 7"}],
                                     "he's himself, just in pain. maybe 7", ["ams.changed_from_baseline", "complaint.pain_rating"])
    assert len(kept) == 2 and not dropped
    kept, dropped = extraction.guard([{"field": "danger_signs.chest_pain_now", "value": False, "quote": "he has no pain"},
                                      {"field": "danger_signs.breathing_difficulty", "value": False, "quote": "he has no pain"}],
                                     "he is awake. he has no pain", ["danger_signs.responsive", "danger_signs.chest_pain_now", "danger_signs.breathing_difficulty"])
    assert [w["field"] for w in dropped] == ["danger_signs.breathing_difficulty"]
    kept, dropped = extraction.guard([{"field": "M.medications", "value": ["warfarin", "bp pill"], "quote": "warfarin"}], "just the bp pill, dont know the name", ["M.medications"])
    assert kept and not dropped          # a list carries earlier items forward

