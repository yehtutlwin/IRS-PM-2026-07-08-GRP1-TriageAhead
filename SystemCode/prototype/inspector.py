"""Generate a human-readable rule inspector (self-contained HTML) from the YAML files.
Usage: python3 inspector.py   -> out/rules-inspector.html"""
import os, yaml, html

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- human vocabulary for fields ----------
LABEL = {
    "E.mechanism": "how the injury happened",
    "E.head_strike": "hit their head",
    "E.loc": "blacked out / lost consciousness",
    "E.fall_height_meters": "height of the fall (metres)",
    "E.body_region": "body region injured",
    "E.abdominal_trauma": "blow or wound to the abdomen",
    "E.vehicle_ejection": "thrown from a vehicle",
    "E.mechanical_extrication": "had to be cut out of a vehicle",
    "M.anticoagulant.value": "takes a blood thinner",
    "M.anticoagulant.status": "blood-thinner information",
    "M.medications": "regular medications",
    "M.beta_blocker": "takes a beta blocker",
    "M.immunosuppressant_or_steroid": "takes immune-suppressing medicine / steroids",
    "complaint.category": "main complaint",
    "complaint.pain_rating": "pain score (0–10)",
    "complaint.pain_cause_class": "cause of the severe pain",
    "complaint.fever": "has a fever",
    "complaint.infection_signs": "signs of infection",
    "complaint.stroke_signs": "signs of a stroke",
    "complaint.acs_suspicion": "chest pain has heart-attack features",
    "complaint.possible_ectopic_pregnancy": "possible ectopic pregnancy",
    "complaint.danger_to_self_or_others": "danger to self or others",
    "complaint.needle_stick_healthcare_worker": "needle-stick injury (healthcare worker)",
    "complaint.sexual_assault": "sexual assault",
    "complaint.increasing_respiratory_effort": "breathing getting harder",
    "complaint.postpartum_hemorrhage": "heavy bleeding after childbirth",
    "complaint.brisk_or_posterior_bleeding": "brisk / deep nosebleed",
    "complaint.button_battery_or_magnet_ingestion": "swallowed a button battery or magnets",
    "complaint.vaginal_bleeding": "vaginal bleeding",
    "complaint.pain_refractory_constant_or_maximal_onset": "pain constant, maximal at onset, or unrelieved by painkillers",
    "complaint.extremity_neurovascular_compromise": "limb losing pulse/feeling/colour",
    "complaint.compartment_syndrome_symptoms": "symptoms of compartment syndrome",
    "complaint.amputation_partial_or_complete": "partial or complete amputation",
    "complaint.possible_pelvis_femur_fracture_or_dislocation": "possible pelvis/thigh-bone fracture or dislocation",
    "complaint.known_toxic_ingestion": "known poisoning / toxic ingestion",
    "complaint.atso_elements_count": "number of eye danger signs (counted by bridge BR-28)",
    "eye.double_vision_pupil_or_bulge": "double vision, unequal pupils or a bulging eye",
    "eye.red": "red eye",
    "eye.intolerable_pain": "unbearable eye pain",
    "eye.injury": "eye injured or something in it",
    "eye.floaters_or_flashes": "floaters or flashes of light",
    "history.immunocompromised": "weakened immune system",
    "history.transplant_recipient_or_listed": "organ-transplant patient (or on the list)",
    "history.pregnant": "pregnant", "history.postpartum": "recently gave birth",
    "history.thrombocytopenia_or_clotting_disorder": "known bleeding/clotting disorder",
    "history.baseline_mental_status": "what their normal mental state is",
    "history.conditions": "known medical conditions",
    "complaint.fever": "fever", "infection.rash": "rash",
    "infection.travel_14d": "overseas travel in the last 2 weeks",
    "infection.contacts": "contact with someone infectious",
    "danger_signs.responsive": "awake and responding",
    "obs.nonverbal_acute": "suddenly not speaking",
    "obs.not_following_commands": "not following simple requests",
    "obs.avpu": "responsiveness level (AVPU)",
    "obs.cardiac_or_pulmonary_arrest": "heart or breathing has stopped (or about to)",
    "obs.apneic": "not breathing", "obs.intubated": "has a breathing tube",
    "obs.pulseless": "no pulse",
    "obs.severe_respiratory_distress": "severe struggle to breathe",
    "obs.airway_occluded_or_ineffective_clearance": "blocked airway",
    "obs.active_seizure": "seizing right now",
    "obs.anaphylaxis": "severe allergic reaction (anaphylaxis)",
    "obs.hypoperfusion_signs": "signs blood isn't circulating (pale, clammy, faint)",
    "obs.respiratory_compromise_signs": "other signs of breathing trouble",
    "obs.flaccid": "floppy, no muscle tone",
    "obs.requires_lifesaving_intervention": "needs a life-saving intervention now",
    "obs.hemodynamically_unstable": "circulation unstable",
    "obs.new_confusion_lethargy_disorientation": "NEW confusion, drowsiness or disorientation",
    "obs.confusion_lethargy_disorientation": "confusion, drowsiness or disorientation",
    "obs.stridor": "high-pitched noisy breathing (stridor)",
    "obs.cannot_manage_secretions": "cannot swallow own saliva",
    "obs.sepsis_signs": "signs of sepsis",
    "obs.subtle_mental_status_change": "subtle change in behaviour/alertness",
    "obs.unexplained_ams_breathing_or_rhythm_change": "unexplained confusion / breathing / heart-rhythm change",
    "vitals.spo2": "oxygen level (SpO2 %)",
    "vitals.spo2_is_patients_norm": "that oxygen level is normal for them",
    "vitals.hypotension": "blood pressure dangerously low",
    "vitals.profound_hypoglycemia": "blood sugar dangerously low",
    "vitals.extreme_heart_rate": "heart rate extremely fast or slow",
    "vitals.heart_rate": "heart rate", "vitals.respiratory_rate": "breathing rate",
    "vitals.temp_c": "temperature (°C)",
    "patient.age": "age", "patient.age_group": "age group",
    "patient.age_days": "age (days)", "patient.age_months": "age (months)",
}

def lab(f):
    return LABEL.get(f, f.replace("_", " ").replace(".", " › "))

def val_h(v):
    if v is True: return "yes"
    if v is False: return "no"
    return f"“{v}”" if isinstance(v, str) else str(v)

def cond_h(c, depth=0):
    if c is None: return "—"
    if "all" in c:
        parts = [cond_h(x, depth+1) for x in c["all"]]
        s = " <b>AND</b> ".join(parts)
        return f"({s})" if depth else s
    if "any" in c:
        parts = [cond_h(x, depth+1) for x in c["any"]]
        s = " <b>OR</b> ".join(parts)
        return f"({s})" if depth else s
    if "not" in c:                      # as engine.holds reads it: true when the inner condition does not hold
        return f"<b>NOT</b> ({cond_h(c['not'], depth+1)})"
    f = lab(c["field"])
    if "equals" in c: return f"{f} is {val_h(c['equals'])}"
    if "in" in c: return f"{f} is one of: {', '.join(val_h(x) for x in c['in'])}"
    if "gte" in c: return f"{f} is at least {c['gte']}"
    if "gt" in c: return f"{f} is above {c['gt']}"
    if "lte" in c: return f"{f} is at most {c['lte']}"
    if "lt" in c: return f"{f} is below {c['lt']}"
    return html.escape(str(c))

PROV = {"verbatim": ("VERBATIM", "#1e6e34", "stated numerically/explicitly in the source"),
        "operationalized": ("OPERATIONALIZED", "#8a6d00", "our concrete interpretation of vague source wording — priority for expert review"),
        "supplemented": ("SUPPLEMENTED", "#7b2d8b", "fills a gap the primary source leaves open, using another authoritative document")}

EFFECT = {"A": ("→ possible ESI-1 — needs immediate life-saving intervention", "#b3261e"),
          "B": ("→ at least ESI-2 — high-risk, should not wait", "#b3261e"),
          "consider": ("→ CONSIDER flag — nurse judgment, not automatic", "#8a6d00"),
          "context_note": ("→ context note — background for reading other findings, not a flag", "#555"),
          "reassess": ("→ re-check the urgency level (vital signs)", "#1a4a7a")}

def title_of(rid):
    part = rid.split(".", 1)[-1].replace("-", " ")
    return part[0].upper() + part[1:]

def src_h(s):
    if isinstance(s, list): return " · ".join(html.escape(x) for x in s)
    return html.escape(str(s or ""))

def card(c):
    rid = c["id"]
    prov = c.get("provenance", "")
    pv = PROV.get(prov)
    dp = c.get("decision_point", "")
    if c.get("effect_override") == "consider": eff = EFFECT["consider"]
    elif c.get("effect_override") == "context_note": eff = EFFECT["context_note"]
    elif str(c.get("effect_override", "")).startswith("reassess"): eff = EFFECT["reassess"]
    elif dp in EFFECT: eff = EFFECT[dp]
    else: eff = ("", "#555")
    rows = []
    if "when" in c:
        rows.append(f"<div class='cond'><span class='k'>WHEN</span> {cond_h(c['when'])}</div>")
    if eff[0]:
        rows.append(f"<div class='eff' style='color:{eff[1]}'>{eff[0]}</div>")
    if c.get("assessed_via"):
        via = {"reported": "askable over the phone", "observed": "needs eyes on the patient",
               "vitals": "needs measured vital signs"}.get(c["assessed_via"], c["assessed_via"])
        rows.append(f"<div class='meta'>How it's known: {via}</div>")
    if c.get("span"):
        rows.append(f"<div class='span'>“{html.escape(str(c['span']))}”</div>")
    if c.get("source"):
        rows.append(f"<div class='meta'>Source: {src_h(c['source'])}</div>")
    if c.get("notes"):
        rows.append(f"<div class='notes'>Note: {html.escape(' '.join(str(c['notes']).split()))}</div>")
    badge = (f"<span class='badge' style='background:{pv[1]}' title='{pv[2]}'>{pv[0]}</span>"
             if pv else "")
    return (f"<div class='card' data-prov='{prov}' data-dp='{dp}'>"
            f"<div class='head'><span class='rid'>{rid}</span> <b>{title_of(rid)}</b> {badge}</div>"
            + "".join(rows) +
            "<div class='review'>Expert review: &#9744; keep &nbsp; &#9744; reword &nbsp; "
            "&#9744; drop &nbsp; comment: ______________________________________</div></div>")

def table_entry(c):
    """C/D special entries rendered as simple lists."""
    bits = [f"<div class='head'><span class='rid'>{c['id']}</span> <b>{title_of(c['id'])}</b></div>"]
    for key in ("rule",):
        if c.get(key): bits.append(f"<div class='cond'>{html.escape(' '.join(str(c[key]).split()))}</div>")
    if c.get("mapping"):
        bits.append("<div class='cond'>" + " · ".join(
            f"{k.replace('_',' ')} → <b>{v}</b>" for k, v in c["mapping"].items()) + "</div>")
    for key, label in (("counts_as_resource", "Counts as a resource"),
                       ("does_not_count", "Does NOT count")):
        if c.get(key):
            bits.append(f"<div class='cond'><b>{label}:</b> " +
                        ", ".join(x.replace("_", " ") for x in c[key]) + "</div>")
    if c.get("bands"):
        rows = "".join(f"<tr><td>{b['age']}</td><td>HR &gt; {b['hr_gt']}</td>"
                       f"<td>RR &gt; {b['rr_gt']}</td></tr>" for b in c["bands"])
        bits.append(f"<table class='bands'><tr><th>Age</th><th>Heart rate</th>"
                    f"<th>Breathing rate</th></tr>{rows}</table>"
                    "<div class='meta'>Plus SpO2 &lt; 92% at any age.</div>")
    if c.get("when"):
        bits.append(f"<div class='cond'><span class='k'>WHEN</span> {cond_h(c['when'])}</div>")
    if c.get("span"): bits.append(f"<div class='span'>“{html.escape(str(c['span']))}”</div>")
    if c.get("source"): bits.append(f"<div class='meta'>Source: {src_h(c.get('source'))}</div>")
    if c.get("notes"): bits.append(f"<div class='notes'>Note: {html.escape(' '.join(str(c['notes']).split()))}</div>")
    return "<div class='card'>" + "".join(bits) + "</div>"

def agenda_card(f, e):
    """One entry of the derived agenda (rules/derived/agenda.yaml)."""
    pol = {"always": "asked of everyone", "when_applicable": "asked when it applies", "volunteered_only": "never asked unprompted; written if volunteered"}[e["ask_policy"]]
    gate = ""
    if e.get("trigger") is not None:
        gate = f"<div class='meta'>Trigger: {cond_h(e['trigger'])}</div>"
    elif e.get("rule_gates"):
        gate = "<div class='meta'>Opens when one of these rules is still possible and another of its facts is known: " + ", ".join(e["rule_gates"]) + "</div>"
    wanted = ", ".join(e.get("wanted_by") or []) or "no rule reads it (history or identity)"
    conf = f"<div class='meta'>Confirmation asked while probable, for: {', '.join(e['confirm_for'])}</div>" if e.get("confirm_for") else ""
    return (f"<div class='card'><div class='head'><span class='rid'>{e['position']}</span> <b>{html.escape(e['ask'])}</b></div>"
            f"<div class='meta'>Field: <code>{html.escape(f)}</code> · priority {e['priority']} · {pol}</div>{gate}{conf}"
            f"<div class='meta'>Wanted by: {html.escape(wanted)}</div></div>")

CSS = """
body{font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;margin:0;background:#eef1f4;color:#1c1c1e;font-size:14px;line-height:1.45}
.wrap{max-width:900px;margin:0 auto;padding:18px}
h1{font-size:21px;margin:8px 0 2px} h2{font-size:16px;margin:26px 0 8px;border-bottom:2px solid #4a6fa5;padding-bottom:3px}
.sub{color:#555;font-size:12.5px;margin-bottom:10px}
.legend{background:#fff;border:1px solid #d8dde3;border-radius:8px;padding:10px 14px;font-size:12.5px;margin:10px 0}
.card{background:#fff;border:1px solid #d8dde3;border-radius:8px;padding:10px 14px;margin:8px 0;break-inside:avoid}
.head{margin-bottom:4px} .rid{font-family:monospace;font-size:11.5px;color:#666;background:#f1f3f5;border-radius:4px;padding:0 5px}
.badge{color:#fff;font-size:10px;border-radius:4px;padding:1px 7px;letter-spacing:.5px;vertical-align:middle}
.cond{margin:4px 0} .k{font-size:10.5px;color:#fff;background:#4a6fa5;border-radius:4px;padding:0 5px;letter-spacing:.5px}
.eff{font-weight:600;margin:3px 0}
.span{color:#555;font-style:italic;font-size:12.5px;margin:4px 0;border-left:3px solid #d8dde3;padding-left:8px}
.meta{color:#666;font-size:12px;margin:2px 0} .notes{font-size:12.5px;background:#fff7df;border-radius:6px;padding:4px 8px;margin:4px 0}
.review{font-size:11.5px;color:#888;border-top:1px dashed #d8dde3;margin-top:7px;padding-top:5px}
.bands{border-collapse:collapse;font-size:12.5px;margin:6px 0} .bands td,.bands th{border:1px solid #c9ced4;padding:2px 9px}
.filters{position:sticky;top:0;background:#eef1f4;padding:8px 0;z-index:5;font-size:13px}
.filters label{margin-right:14px;cursor:pointer}
nav{position:fixed;left:0;top:0;bottom:0;width:215px;background:#1a2b45;padding:18px 0;overflow-y:auto}
nav a{display:block;color:#dbe6f5;text-decoration:none;padding:8px 16px;font-size:13px;border-left:3px solid transparent}
nav a:hover{background:#24385a;border-left-color:#7aa2d6}
.cnt{background:#4a6fa5;color:#fff;border-radius:9px;font-size:10.5px;padding:0 7px;margin-left:4px}
.wrap{margin-left:230px}
h3{font-size:13.5px;margin:16px 0 4px;color:#1a4a7a}
@media (max-width:800px){nav{display:none}.wrap{margin-left:0}}
@media print{.filters{display:none}.card{page-break-inside:avoid}}
"""

JS = """
function apply(){
  const provs=[...document.querySelectorAll('.pf:checked')].map(x=>x.value);
  document.querySelectorAll('.card[data-prov]').forEach(c=>{
    c.style.display = provs.includes(c.dataset.prov)||!c.dataset.prov ? '' : 'none';});
}
document.querySelectorAll('.pf').forEach(x=>x.addEventListener('change',apply));
document.getElementById('q').addEventListener('input',e=>{
  const t=e.target.value.toLowerCase();
  document.querySelectorAll('.card').forEach(c=>{
    c.style.display = c.textContent.toLowerCase().includes(t) ? '' : 'none';});
});
"""

THEME = {  # simple clinical grouping for decision point B (start simple; refine with the team)
    "B-01": "Mental state & behaviour", "B-09": "Mental state & behaviour", "B-29": "Children & special cases",
    "B-02": "Severe pain", "B-03": "Severe pain",
    "B-04": "Chest & stroke", "B-05": "Chest & stroke",
    "B-06": "Pregnancy & women's health", "B-13": "Pregnancy & women's health", "B-21": "Pregnancy & women's health",
    "B-07": "Infection & immune", "B-08": "Infection & immune",
    "B-10": "Exposures & assault", "B-11": "Exposures & assault", "B-26": "Exposures & assault",
    "B-12": "Breathing & airway", "B-14": "Breathing & airway",
    "B-15": "Bleeding", "B-16": "Children & special cases",
    "B-17": "Abdominal", "B-18": "Abdominal", "B-19": "Abdominal", "B-20": "Abdominal",
    "B-22": "Trauma & injuries", "B-23": "Trauma & injuries", "B-24": "Trauma & injuries",
    "B-25": "Trauma & injuries", "B-27": "Trauma & injuries", "B-30": "Trauma & injuries",
    "B-28": "Eye",
}
THEME_ORDER = ["Trauma & injuries", "Chest & stroke", "Abdominal", "Pregnancy & women's health",
               "Infection & immune", "Mental state & behaviour", "Breathing & airway", "Bleeding",
               "Severe pain", "Children & special cases", "Exposures & assault", "Eye", "Other"]

def build_html():
    crit = yaml.safe_load(open(os.path.join(HERE, "..", "rules", "criteria.yaml")))
    agenda = yaml.safe_load(open(os.path.join(HERE, "..", "rules", "derived", "agenda.yaml")))["fields"]
    by_dp = lambda dp: [c for c in crit if c.get("decision_point") == dp and "when" in c]
    special = [c for c in crit if "when" not in c or c.get("decision_point") not in ("A", "B")]
    n_prov = {}
    for c in crit:
        p = c.get("provenance")
        if p: n_prov[p] = n_prov.get(p, 0) + 1

    nav = [("interview", "What the interview may ask", len(agenda)),
           ("dpa", "A — life-saving intervention", len(by_dp("A"))),
           ("dpb", "B — high-risk (ESI 2)", len(by_dp("B"))),
           ("special", "C, D & governance", len(special))]
    navhtml = "".join(f"<a href='#{a}'>{t} <span class='cnt'>{n}</span></a>" for a, t, n in nav)
    H = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Rule Inspector — ED Triage Intake</title><style>{CSS}</style></head><body>"
         f"<nav>{navhtml}</nav><div class='wrap'>"]
    H.append("<h1>Rule Inspector — ED Triage Intake prototype</h1>")
    H.append("<div class='sub'>Generated from rules/criteria.yaml and rules/derived/agenda.yaml (itself derived from the rules and rules/fields.yaml) — do not edit this file; edit the YAML and regenerate (python3 inspector.py). "
             "Every rule shows its condition in plain language, its source, and the exact quoted passage it came from.</div>")
    H.append("<div class='legend'><b>Provenance legend:</b> ")
    for k, (name, color, desc) in PROV.items():
        H.append(f"<span class='badge' style='background:{color}'>{name}</span> {desc} ({n_prov.get(k,0)}) &nbsp; ")
    H.append("</div>")
    H.append("<div class='filters'><b>Show:</b> " + "".join(
        f"<label><input type='checkbox' class='pf' value='{k}' checked> {v[0].title()}</label>"
        for k, v in PROV.items()) +
        " &nbsp; <input id='q' placeholder='search rules...' style='padding:3px 8px;width:200px'></div>")

    H.append("<h2 id='interview'>What the interview may ask — the derived agenda, in order</h2>")
    H.append("<div class='sub'>One entry per field a caregiver can answer, derived by rules/derive.py from the rules and the field file. "
             "The model words each question; the text shown is the field's everyday wording (reference, not a script).</div>")
    H += [agenda_card(f, e) for f, e in agenda.items()]

    H.append("<h2 id='dpa'>Decision point A — needs immediate life-saving intervention (ESI 1)</h2>")
    H += [card(c) for c in by_dp("A")]
    H.append("<h2 id='dpb'>Decision point B — high-risk, should not wait (at least ESI 2)</h2>")
    groups = {}
    for c in by_dp("B"):
        key = THEME.get(c["id"].split(".")[0], "Other")
        groups.setdefault(key, []).append(c)
    for theme in THEME_ORDER:
        if theme in groups:
            H.append(f"<h3>{theme} <span class='cnt'>{len(groups[theme])}</span></h3>")
            H += [card(c) for c in groups[theme]]
    H.append("<h2 id='special'>Decision points C &amp; D, and governance</h2>")
    H += [table_entry(c) for c in special]

    H.append(f"</div><script>{JS}</script></body></html>")
    return "\n".join(H), (len(crit), len(agenda), 0)


def export():
    html_text, counts = build_html()
    out = os.path.join(HERE, "out", "rules-inspector.html")
    open(out, "w").write(html_text)
    print(f"written: {out}  ({counts[0]} criteria, {counts[1]} agenda rules, {counts[2]} questions)")


def serve(port=8077):
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            body, _ = build_html()          # re-reads the YAML every refresh
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def log_message(self, *a): pass

    print(f"Rule inspector: http://localhost:{port}  (edit the YAML, refresh the page; Ctrl-C stops)")
    HTTPServer(("0.0.0.0", port), H).serve_forever()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8077)
    else:
        export()
