"""Standard-vs-practice divergence, one rule: B-30 anticoagulated trauma (design record,
evaluation layers "standard vs practice" + "under-triage safety net", in miniature).

Question: when B-30's condition holds on real visits (trauma mechanism + anticoagulant),
what did nurses actually assign - and where they assigned BELOW our floor (ESI 3-5),
did the outcome (admission) side with the nurse or the rule?

Method: Yale rows where a mapped trauma flag is set AND meds_anticoagulants > 0.
Control: same trauma flags, NOT anticoagulated, same nurse level bands - isolates the
anticoagulant's contribution to the admission gap.

Run:  .venv/bin/python experiments/divergence_b30.py   (needs data/download-yale.sh)
Output: printed + experiments/out/divergence-b30.md

CAVEATS (stamped in the report - read them before quoting any number):
- Admission is a treatment-paradox outcome: anticoagulated head-injury patients are often
  admitted for observation BECAUSE of the anticoagulant, so admission partly encodes the
  risk factor itself, not proof of mistriage.
- cc_fall etc. don't confirm a head strike or the mechanism detail the sources describe;
  the mapping is coarse (disclosed as a confound).
- B-30 is supplemented-class: this is a claim about the CDC/NICE criterion vs practice,
  not about ESI.
- Pattern-level only. Never "these nurses were wrong" - the nurse saw the patient; we saw
  a row.
"""
import os
import pandas as pd
import pyreadr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TRAUMA_FLAGS = {           # Yale cc_ flag -> our E.mechanism value
    "cc_fall": "fall", "cc_fall>65": "fall", "cc_multiplefalls": "fall",
    "cc_motorvehiclecrash": "road_accident", "cc_motorcyclecrash": "road_accident",
    "cc_assaultvictim": "assault",
}

def main():
    df = next(iter(pyreadr.read_r(os.path.join(ROOT, "data", "yale_ed_visits.rdata")).values()))
    esi = pd.to_numeric(df["esi"], errors="coerce")
    ok = esi.notna(); df, esi = df[ok], esi[ok]
    num = lambda c: pd.to_numeric(df[c], errors="coerce").fillna(0)
    trauma = pd.Series(False, index=df.index)
    per_mech = {}
    for flag, mech in TRAUMA_FLAGS.items():
        if flag in df.columns:
            m = num(flag) > 0
            trauma |= m
            per_mech[mech] = per_mech.get(mech, pd.Series(False, index=df.index)) | m
    ac = num("meds_anticoagulants") > 0
    admit = df["disposition"].astype(str).eq("Admit")

    fires = trauma & ac                       # B-30 condition (coarse mapping)
    below = fires & (esi >= 3)                # nurse below our floor
    ctrl_below = trauma & ~ac & (esi >= 3)    # control: same trauma, no anticoagulant

    L = ["# B-30 anticoagulated-trauma: standard vs practice on Yale (one-rule divergence analysis)\n",
         f"Rows with a nurse ESI: {len(df):,} · trauma-flagged: {trauma.sum():,} · "
         f"anticoagulated among them: {fires.sum():,} (**B-30 condition holds, coarse mapping**)\n",
         "\n## Nurse ESI where B-30 fires (our floor: at least ESI-2)\n",
         "| nurse ESI | n | share |", "| --- | --- | --- |"]
    vc = esi[fires].value_counts().sort_index()
    for lvl, n in vc.items():
        L.append(f"| {int(lvl)} | {n:,} | {n/fires.sum():.1%} |")
    L.append(f"\n**Below our floor (ESI 3-5): {below.sum():,} = {below.sum()/fires.sum():.1%}** of B-30 cases.\n")

    L.append("\n## Outcome arbitration: admission rate among nurse-ESI 3-5 trauma patients\n")
    L.append("| group | n | admitted |")
    L.append("| --- | --- | --- |")
    L.append(f"| trauma + anticoagulated (B-30 fired, nurse below floor) | {below.sum():,} | {admit[below].mean():.1%} |")
    L.append(f"| trauma, NOT anticoagulated, same nurse levels (control) | {ctrl_below.sum():,} | {admit[ctrl_below].mean():.1%} |")
    ratio = admit[below].mean() / max(admit[ctrl_below].mean(), 1e-9)
    L.append(f"\nAdmission ratio (B-30 group / control): **{ratio:.1f}×**\n")
    # age confound: anticoagulated patients are old; compare within age bands
    age = pd.to_numeric(df["age"], errors="coerce")
    L.append("\n### Age-banded control (is it the anticoagulant, or just age?)\n")
    L.append("| age band | B-30 below-floor: n / admitted | control below-floor: n / admitted | ratio |")
    L.append("| --- | --- | --- | --- |")
    for lo, hi in ((0, 64), (65, 74), (75, 84), (85, 200)):
        band = (age >= lo) & (age <= hi)
        b, c = below & band, ctrl_below & band
        if b.sum() >= 20:
            r = admit[b].mean() / max(admit[c].mean(), 1e-9)
            L.append(f"| {lo}-{hi if hi < 200 else '+'} | {b.sum():,} / {admit[b].mean():.1%} | "
                     f"{c.sum():,} / {admit[c].mean():.1%} | {r:.1f}× |")

    L.append("\n## By mechanism (B-30 fired)\n")
    L.append("| mechanism | n fired | nurse below floor | admitted among below-floor |")
    L.append("| --- | --- | --- | --- |")
    for mech, m in per_mech.items():
        f = m & ac; b = f & (esi >= 3)
        if f.sum():
            L.append(f"| {mech} | {f.sum():,} | {b.sum()/f.sum():.1%} | "
                     f"{admit[b].mean():.1%} (n={b.sum():,}) |")

    L.append("\n## Reading it\n")
    L.append("- The rule's condition is common on real data (not an exotic textbook case).\n"
             "- A large share of those patients were triaged below the floor the CDC/NICE-derived "
             "criterion implies - a real *divergence* between the encoded criterion and practice.\n"
             "- Outcome arbitration points in the floor's direction, with the treatment-paradox "
             "caveat: admission-for-observation is partly *caused by* the anticoagulant, so this "
             "supports 'the criterion identifies a group clinicians take seriously', not "
             "'nurses under-triaged'.\n"
             "- This is the under-triage safety-net analysis in miniature; the report-grade version "
             "uses a critical-outcome composite (ICU/death/immediate intervention - MIMIC), "
             "sensitivity vs alarm-rate curves, and rule-class attribution.")
    L.append("\n## Caveats\n")
    L.append("- Treatment paradox on admission (see above).\n- Coarse mapping: cc_fall etc. don't "
             "confirm head strike / mechanism detail; head-injury-specific rows would be a tighter "
             "test.\n- Supplemented-class rule: a claim about the external criterion vs practice, "
             "not about ESI.\n- Pattern-level only; never individual adjudication.")
    report = "\n".join(L)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = os.path.join(HERE, "out", "divergence-b30.md")
    open(out, "w").write(report)
    print(report); print(f"\n[saved: {out}]")

if __name__ == "__main__":
    main()
