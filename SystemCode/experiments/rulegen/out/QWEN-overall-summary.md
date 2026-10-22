
# VANDA-9465 — Dynamic Questioning Session Evaluation

**Project:** ISS IRS 2026 Group 1 — Hospital Triage  
**Session ID:** VANDA-9465  
**Date:** 10 October 2026  
**AI Model:** Qwen 3 14B  
**Backend:** LM Studio (Local API)  
**Interface:** Hospital Triage Web Application  
**Evaluation:** Dynamic Questioning, Fact Extraction, and ESI Rule Evaluation

---

## 1. Executive Summary

The VANDA-9465 experiment evaluated Qwen 3 14B, running locally through LM Studio, for dynamic patient questioning in the hospital triage prototype.

The system completed eight patient-answer turns and demonstrated the ability to:

- Generate natural-language interview questions.
- Extract structured facts from conversational responses.
- Collect information across multiple clinical topics.
- Evaluate at least one relevant ESI criterion.
- Complete the interview and generate a session acknowledgement.

However, a potential safety-critical limitation was identified.

The patient reported chest pain, difficulty breathing, chest trauma following a fall, and pain severity of 8/10. Despite these findings, the system continued routine questioning without a visible urgent escalation event.

**Overall finding:** Dynamic questioning and fact extraction were operational, but clinical escalation and final triage correctness remain unverified.

---

## 2. Interview Overview

| Stage | Question Topic | Patient Response |
|---|---|---|
| 1 | Red-flag screening | Awake, chest pain, difficulty breathing, no heavy bleeding |
| 2 | Chief complaint | Fell and hit chest that morning; pain 8/10 |
| 3 | Limb assessment | No numbness or movement difficulties |
| 4 | Trauma details | No head strike or loss of consciousness; fall was not far |
| 5 | Medication history | No regular medications |
| 6 | Allergies and medical history | None reported |
| 7 | Infection screening | No fever, rash, travel, or infectious contacts |
| 8 | Final information | Last ate that morning; identifying information provided |

The interview ended at 23:29:39 with the following engine event:

```text
interview complete - no open slots
```

This indicates that the questioning engine had no remaining active information slots.

The interview lasted approximately 46 minutes from the first question to completion, including patient response time.

---

## 3. Dynamic Questioning Performance

### 3.1 Question Generation

Qwen generated natural-language questions based on the information slots selected by the interview engine.

After the patient reported falling and hitting their chest, the system asked:

> Did you hit your head or lose consciousness at any point, and roughly how far did you fall?

This question was relevant to the reported injury.

Other questions covered medications, allergies, medical history, infection exposure, and patient information.

**Finding:** Qwen successfully generated understandable and contextually relevant questions.

### 3.2 Adaptive Questioning

The existing architecture follows this process:

```text
Patient provides an answer
          |
          v
Qwen extracts structured facts
          |
          v
Fact store is updated
          |
          v
ESI rule engine evaluates facts
          |
          v
Engine selects next information slot
          |
          v
Qwen generates the next question
```

The system uses `engine.next_slot()` to select the next information topic, while Qwen phrases the question and extracts the answer.

This is best described as **rule-guided adaptive questioning**, rather than fully autonomous LLM-driven questioning.

The trauma follow-up was consistent with adaptive behavior, although the available transcript does not prove whether that slot was dynamically activated by the patient's answer.

### 3.3 Questioning Limitations

Several questions combined multiple topics into a single prompt.

For example, the allergies and medical history question asked about medication allergies, heart problems, diabetes, pregnancy, and immune-system conditions simultaneously.

The patient responded:

> nope

The extraction system interpreted this as negative responses across multiple fields.

This introduces potential ambiguity because the patient may have been responding to only part of the question.

**Recommendation:** Separate clinically important questions when individual confirmation is required.

---

## 4. Structured Fact Extraction

### 4.1 Initial Red-Flag Screening

Patient response:

> yes awake, yes chest pain, difficulty breathing, no bleeding

Extracted facts:

```json
{
  "red_flags.responsive": true,
  "red_flags.chest_pain_now": true,
  "red_flags.breathing_difficulty": true,
  "red_flags.heavy_bleeding": false
}
```

The extracted values were consistent with the supplied answer.

### 4.2 Chief Complaint

Patient response:

> he fell and hit his chest this morning, pain is 8

Extracted facts:

```json
{
  "complaint.category": "chest_pain",
  "complaint.text": "fell and hit his chest",
  "complaint.onset": "this morning",
  "complaint.pain_rating": 8,
  "E.mechanism": "fall"
}
```

This demonstrates successful extraction of categorical, free-text, temporal, numerical, and injury-mechanism information.

### 4.3 Trauma Information

Patient response:

> nope, didnt fall far

Extracted facts:

```json
{
  "E.head_strike": false,
  "E.loc": false
}
```

The response did not produce a numeric fall-height value.

**Finding:** Qwen handled the explicit negative findings, but did not obtain a precise fall height.

### 4.4 Medical History and Infection Screening

The system also extracted structured negative findings for:

- Regular medications.
- Medication allergies.
- Existing medical conditions.
- Immunocompromised status.
- Pregnancy or postpartum status.
- Fever and rash.
- Recent travel.
- Infectious contacts.

These extractions were generally consistent with the patient's responses, subject to the ambiguity of compound questions.

### 4.5 Extraction Assessment

| Capability | Result |
|---|---|
| Boolean extraction | Successful |
| Numerical extraction | Successful |
| Complaint classification | Successful |
| Symptom onset extraction | Successful |
| Injury mechanism extraction | Successful |
| Negative-response handling | Functioning, with ambiguity risks |
| Missing-information clarification | Needs improvement |
| Final fact-store persistence | Not independently verified |

**Finding:** Qwen successfully produced structured fact writes. However, the final saved session JSON was not independently inspected.

---

## 5. ESI Rule Engine Evaluation

The event log recorded the following event after the patient reported pain severity of 8/10:

```json
{
  "t": "22:48:33",
  "kind": "engine",
  "consider": [
    "B-02.severe-pain-consider"
  ]
}
```

This indicates that the engine recognized the severe-pain criterion for consideration.

The result demonstrates that at least part of the fact extraction and ESI rule evaluation pipeline was functioning.

However, the supplied log did not establish:

- The final ESI triage level.
- Whether all relevant ESI rules were evaluated.
- Whether chest pain and breathing difficulty triggered additional criteria.
- Whether an urgent alert appeared elsewhere in the web interface.

**Finding:** ESI rule consideration was demonstrated, but final triage correctness remains unverified.

---

## 6. Potential Safety Gap: Urgent Symptom Escalation

### 6.1 Urgent Symptoms Identified

| Symptom or Finding | Extracted Value |
|---|---|
| Current chest pain | `true` |
| Difficulty breathing | `true` |
| Chest trauma following a fall | Recorded |
| Pain severity | 8/10 |

These findings warrant prompt clinical attention and should be handled through a clinician-approved escalation pathway.

### 6.2 Observed Behavior

Despite extracting these findings, the system continued asking routine questions about:

- Limb symptoms.
- Trauma details.
- Medications.
- Allergies and medical history.
- Infection exposure.
- Final patient information.

No urgent escalation event was visible in the supplied event log.

The only explicit ESI-related event was consideration of the severe-pain rule.

### 6.3 Possible Causes

Three explanations remain possible:

1. The red-flag information was extracted but was not connected to escalation logic.
2. The rule engine evaluated the information, but the web interface did not interrupt the interview or visibly alert the user.
3. An escalation occurred through another component but was not recorded in the supplied log.

The available evidence cannot distinguish between these possibilities.

**Finding:** Urgent symptom detection was demonstrated, but appropriate escalation was not demonstrated.

### 6.4 Recommendation

Implement or verify a deterministic, clinician-approved urgent-symptom pathway that can interrupt routine questioning and request immediate clinical assessment when appropriate.

Escalation should not depend solely on Qwen generating a suitable conversational response.

---

## 7. Interview Completion

At the end of the interview, the system generated an acknowledgement directing the patient to present the session code at the hospital counter.

The final engine event was:

```json
{
  "t": "23:29:39",
  "kind": "engine",
  "note": "interview complete - no open slots"
}
```

This indicates that the engine considered the interview agenda complete.

However, **completion of the interview does not necessarily mean the patient has been safely triaged**.

The application should clearly distinguish between interview completion and clinical triage disposition.

---

## 8. Key Findings Summary

| Evaluation Area | Result | Interpretation |
|---|---|---|
| Web interview execution | Successful | Session ran to logged completion |
| Question generation | Successful | Qwen generated understandable questions |
| Adaptive questioning | Partially demonstrated | Rule-guided selection; adaptation not fully verified |
| Structured fact extraction | Successful in event log | Important patient information extracted |
| ESI rule consideration | Demonstrated | Severe-pain rule considered |
| Final ESI classification | Not verified | Final triage level not shown |
| Urgent symptom escalation | Not visibly demonstrated | Potential safety-critical gap |
| Interview completion | Successful | No remaining open slots |
| Clinical readiness | Not established | Further validation required |

---

## 9. Recommendations

### Priority 1 — Verify Urgent Escalation

Investigate how the system handles:

```python
red_flags.chest_pain_now
red_flags.breathing_difficulty
```

Confirm that these fields are consumed by the rule engine and trigger appropriate clinician-approved escalation behavior.

### Priority 2 — Verify Final Triage Evaluation

Inspect the saved session state to determine whether the engine produced a final ESI classification and which rules contributed to it.

### Priority 3 — Improve Follow-Up Questioning

Introduce clarification questions for incomplete or ambiguous responses.

Examples include:

- Vague injury height.
- Incomplete date of birth.
- Compound questions answered with a single negative response.

### Priority 4 — Validate Fact Persistence

Compare the extraction events against the final saved fact store to ensure information was correctly retained.

### Priority 5 — Introduce Regression Testing

Use synthetic scenarios covering:

- Chest pain with breathing difficulty.
- Severe pain following trauma.
- Routine low-risk presentations.
- Missing or incomplete answers.
- Contradictory patient responses.

### Priority 6 — Preserve LLM and Rule Engine Separation

Continue using Qwen for question phrasing and structured information extraction, while retaining deterministic, clinician-reviewed rules for triage decisions and escalation.

---

## 10. Evaluation Limitations

This evaluation is based on a single synthetic patient interview.

The available evidence consisted of:

- `VANDA-9465.transcript.txt`
- `VANDA-9465.log.jsonl`
- Selected excerpts from `prototype/cli.py`
- Selected excerpts from `prototype/interview.py`

The complete session JSON, full rule engine implementation, web interface logic, and final clinical report were not independently inspected.

The findings therefore do not establish clinical accuracy, patient safety, general model reliability, or production readiness.

---

## 11. Overall Conclusion

The VANDA-9465 experiment demonstrated that **Qwen 3 14B, operating through LM Studio, can support a rule-guided dynamic questioning workflow** in the hospital triage prototype.

The system successfully:

- Generated conversational questions.
- Extracted structured patient information.
- Considered at least one relevant ESI criterion.
- Completed the interview.

However, the most significant unresolved issue is the absence of visible urgent escalation despite the patient reporting chest pain, difficulty breathing, and severe pain following trauma.

Future development should prioritize red-flag handling, clinician escalation, final triage evaluation, and fact-store integrity.

**Overall assessment:** Dynamic questioning and information extraction were operational in this test, but clinical safety and triage correctness remain unverified.
