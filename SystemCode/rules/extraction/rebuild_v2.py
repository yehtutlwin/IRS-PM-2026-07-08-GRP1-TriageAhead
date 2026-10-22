"""One-time rebuild of rules/criteria.yaml into its version-2 form (issue #50, decision #55). Applied 4 Oct 2026.
Reads the version-1 rulebook (kept as rules/criteria.v1-2026-08-29.yaml) and the complete reading pass, and writes
rules/criteria.yaml so that:
  - every entry lists the statements of the pass that support it (`statements`) and where it came from (`origin`);
  - the entries the pass found missing and that the handbook states outright are added;
  - the refinements the pass asked for are applied where they change a condition;
  - statements about how levels are used are no longer filed under decision point D.
Conditions of existing rules are otherwise unchanged, and their ids are kept, so the handbook case tests show whether
anything was lost. The text of the file is edited in place, not re-dumped, so comments and layout survive.
    .venv/bin/python rules/extraction/rebuild_v2.py
"""
import os, re, collections, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V1 = os.path.join(ROOT, "rules", "criteria.v1-2026-08-29.yaml"); OUT = os.path.join(ROOT, "rules", "criteria.yaml")
st = yaml.safe_load(open(os.path.join(ROOT, "rules", "extraction", "v5-complete-pass.yaml")))["statements"]
sup = collections.defaultdict(list)
for s in st:
    for r in s.get("rules", []) + ([s["rule"]] if s.get("rule") else []) + ([s["proposal"]] if s.get("proposal") else []):
        sup[r].append(s["n"])
text = open(V1).read()
text = text.replace("# criteria.yaml — ESI v5 criteria, version 2 (29 Aug 2026; replaces the feasibility-spike draft, kept as criteria.v1-spike.yaml)",
 "# criteria.yaml — the rulebook, knowledge base and extraction design v2 (rebuilt 4 Oct 2026 by rules/extraction/rebuild_v2.py;\n"
 "# the 29 Aug 2026 rulebook is kept as criteria.v1-2026-08-29.yaml, the August spike as criteria.v1-spike.yaml).\n"
 "# PROCESS: extracted from sources. Each entry lists `statements`: the numbers of the sentences in\n"
 "# rules/extraction/v5-complete-pass.yaml that support it, and `origin`: where the entry came from (meanings in rules/vocabulary.yaml).")
# --- refinements that change a condition or a tag
old = """  when: { all: [ { field: history.transplant_recipient_or_listed, equals: true },
                 { any: [ { field: complaint.fever, equals: true },
                          { field: complaint.infection_signs, equals: true } ] } ] }"""
new = """  when: { all: [ { field: history.transplant_recipient_or_listed, equals: true },
                 { any: [ { field: complaint.fever, equals: true },
                          { field: complaint.infection_signs, equals: true },
                          { field: complaint.transplant_rejection_signs, equals: true } ] } ] }"""
assert old in text; text = text.replace(old, new)
for gid in ("GOV-01.acuity-changes-up-only", "GOV-02.environment-independence"):
    a = text.index(f"- id: {gid}"); b = text.index("\n", text.index("decision_point:", a))
    text = text[:text.index("decision_point:", a)] + "decision_point: none" + text[b:]
old = '  span: "(v1 entry retained; span to be verified at review)"'
if old in text: text = text.replace(old, '  span: "The only change that should be made is to increase acuity"', 1)
# --- attach statements and origin to every existing entry
blocks = re.split(r"(?m)^(?=- id: )", text); head, blocks = blocks[0], blocks[1:]
out = [head]
for b in blocks:
    rid = re.match(r"- id: (\S+)", b).group(1)
    lines = b.split("\n"); last = max(i for i, l in enumerate(lines) if l.startswith("  ") or i == 0)
    supplemented = "provenance: supplemented" in b
    origin = "[supplemented-2026-08]" if supplemented else "[consolidation-2026-08-29, complete-pass-2026-10-04]"
    extra = [f"  statements: {sorted(sup.get(rid, []))}", f"  origin: {origin}"]
    if rid == "B-16.button-battery-or-magnet-ingestion":
        extra.insert(0, '  refinement_pending: "The handbook singles out children under 6 years and batteries over 20 mm (p.13); the rule fires on any ingestion. Not narrowed: the wider reading is the safer one. For clinician review."')
    lines[last + 1:last + 1] = extra
    out.append("\n".join(lines))
text = "".join(out).rstrip("\n") + "\n"
# --- entries the pass found missing and the handbook states outright
S = lambda rid: sorted(sup.get(rid, []))
text += f"""
# ============ ADDED BY THE COMPLETE READING PASS (4 Oct 2026) — stated outright by the handbook ============

- id: A-22.requires-lifesaving-intervention
  decision_point: A
  when: {{ field: obs.requires_lifesaving_intervention, equals: true }}
  assessed_via: observed
  provenance: verbatim
  source: "ESI v5 p.5 (Conceptual Overview); p.9 (Table 3-1, the interventions)"
  span: "Decision point A is the only one needed for ESI level-1 patients, who are defined as in need of immediate lifesaving intervention"
  notes: "The generic level-1 criterion. Until now this fact was read only together with other facts (A-14, A-17, A-18).
          What counts as a lifesaving intervention is listed in A-LIST.lifesaving-interventions."
  statements: {S('A-22.requires-lifesaving-intervention')}
  origin: [complete-pass-2026-10-04]

- id: A-LIST.lifesaving-interventions
  decision_point: A
  list:
    airway_breathing: [assisted ventilation, intubation, surgical airway, emergent non-invasive positive pressure ventilation]
    electrical_therapy: [defibrillation, emergent cardioversion, external pacing]
    procedures: [chest needle decompression, pericardiocentesis, open thoracotomy]
    hemodynamics: [significant intravenous fluid resuscitation, blood administration, control of external hemorrhage]
    medications: [adenosine, atropine, dextrose, dopamine, epinephrine (including intramuscular for anaphylaxis), naloxone]
  not_interventions: "Diagnostics: a CT scan for a stroke, or the catheterization lab for a hemodynamically stable patient."
  provenance: verbatim
  source: "ESI v5 p.9 (Table 3-1)"
  span: "Note that diagnostics are not interventions"
  notes: "Defines obs.requires_lifesaving_intervention. 'Control of external hemorrhage' is the handbook sentence behind the
          caregiver's heavy-bleeding danger-sign answer, which no rule reads yet."
  statements: {S('A-LIST.lifesaving-interventions')}
  origin: [complete-pass-2026-10-04]

- id: C-NOTE.resource-count-independent-of-hospital
  decision_point: C
  rule: "The number of resources a presentation needs is the same in any emergency department; it does not depend on the type or location of the hospital."
  provenance: verbatim
  source: "ESI v5 p.19"
  span: "Resource determination is independent of type of hospital"
  statements: {S('C-NOTE.resource-count-independent-of-hospital')}
  origin: [complete-pass-2026-10-04]

- id: C-NOTE.institution-policy
  decision_point: C
  rule: "What counts as a resource follows the institution's policy where the handbook's list leaves room (the handbook's example: throat cultures)."
  provenance: verbatim
  source: "ESI v5 p.20 (footnote to Table 5-2)"
  span: "Follow the institution’s policy on what constitutes a resource"
  statements: {S('C-NOTE.institution-policy')}
  origin: [complete-pass-2026-10-04]

- id: ISO-01.fever-rash-incomplete-immunizations-isolation-consider
  decision_point: none
  rule: "A fever with a non-petechial rash and incomplete immunizations should prompt the nurse to consider isolation. Not a level."
  condition_proposed: {{ all: [ {{ field: complaint.fever, equals: true }}, {{ field: infection.rash, equals: true }}, {{ field: patient.immunizations_incomplete, equals: true }} ] }}
  assessed_via: reported
  provenance: verbatim
  source: "ESI v5 p.23 (Pediatric Vital Signs)"
  span: "non-petechial rash, and incomplete immunizations should prompt the triage nurse to consider isolation"
  notes: "Not executed: the program has no isolation flag yet (issue #57). The handbook source for asking about a rash in the infection screen (issue #58)."
  statements: {S('ISO-01.fever-rash-incomplete-immunizations-isolation-consider')}
  origin: [complete-pass-2026-10-04]

- id: GOV-03.decision-points-in-order
  decision_point: none
  rule: "The four decision points are taken in order, A first. The basis for asking about immediate danger before anything else."
  provenance: verbatim
  source: "ESI v5 p.5"
  span: "The decision points must be performed in order"
  statements: {S('GOV-03.decision-points-in-order')}
  origin: [complete-pass-2026-10-04]

- id: GOV-04.arrival-mode-independence
  decision_point: none
  rule: "How the patient arrives (ambulance, car, carried in) must not change the level."
  provenance: verbatim
  source: "ESI v5 p.10 (The problem of geography)"
  span: "The triage nurse should not consider the method of arrival as a barrier to assigning the appropriate ESI level"
  statements: {S('GOV-04.arrival-mode-independence')}
  origin: [complete-pass-2026-10-04]

- id: GOV-05.disposition-independence
  decision_point: none
  rule: "Whether the patient is likely to be discharged does not lower a level-1 assignment."
  provenance: verbatim
  source: "ESI v5 p.10"
  span: "The likelihood of discharge does not have an impact on assigning ESI 1"
  statements: {S('GOV-05.disposition-independence')}
  origin: [complete-pass-2026-10-04]

- id: GOV-06.no-vitals-if-they-delay-care
  decision_point: none
  rule: "A patient recognised as level 1 or 2 does not need vital signs taken first if that would delay care. Levels 1 and 2 can be recognised without them."
  provenance: verbatim
  source: "ESI v5 p.23"
  span: "1 or 2 do not need vitals taken if it is going to delay initiation of care"
  statements: {S('GOV-06.no-vitals-if-they-delay-care')}
  origin: [complete-pass-2026-10-04]

- id: GOV-07.no-level-without-assessment
  decision_point: none
  rule: "No ESI level is assigned without an assessment that includes a full set of vital signs, unless the patient is in extremis. The handbook's own reason why a system working before arrival reports a floor and never a level."
  provenance: verbatim
  source: "ESI v5 p.27 (Appendix A, 'Can a preliminary ESI level be assigned prior to assessment?')"
  span: "Assigning an ESI level without an assessment may result in significant undertriage"
  statements: {S('GOV-07.no-level-without-assessment')}
  origin: [complete-pass-2026-10-04]

- id: GOV-08.levels-are-ordinal
  decision_point: none
  rule: "ESI levels are ordered categories. They can be counted and compared; they cannot be averaged."
  provenance: verbatim
  source: "ESI v5 p.27 (Appendix A)"
  span: "ESI levels are ordinal data, not interval data, and so cannot be meaningfully averaged"
  statements: {S('GOV-08.levels-are-ordinal')}
  origin: [complete-pass-2026-10-04]

- id: GOV-09.no-time-targets
  decision_point: none
  rule: "ESI defines no expected time to be seen for any level, unlike the Australasian, Canadian and Manchester scales."
  provenance: verbatim
  source: "ESI v5 p.1"
  span: "The ESI does not define expected time intervals to physician evaluation"
  statements: {S('GOV-09.no-time-targets')}
  origin: [complete-pass-2026-10-04]
"""
open(OUT, "w").write(text)
print("rebuilt:", OUT)
