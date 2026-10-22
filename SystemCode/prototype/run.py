"""Runner. Modes:
   python run.py dry            - engine-only proof, facts injected, no API calls
   python run.py live [P1 ...]  - full Gemini interviews for all (or named) personas
Outputs -> out/<persona>-transcript.txt and out/<persona>-report.txt"""
import sys, os, yaml, json, engine

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)


def load_personas():
    with open(os.path.join(HERE, "personas.yaml")) as f:
        return yaml.safe_load(f)


def score(persona, facts):
    hits, misses = [], []
    for field, want in persona["truth"].items():
        got = facts.resolve(field)
        if field == "M.anticoagulant" and want == "absent":
            ok = got is None or got is False
        elif isinstance(want, list):
            ok = got is not None and len(got or []) > 0
        elif isinstance(want, bool) or isinstance(want, int):
            ok = got == want
        else:
            ok = got is not None
        (hits if ok else misses).append(f"{field}: want={want!r} got={got!r}")
    return hits, misses


def dry():
    criteria = engine.load_criteria()
    print("== DRY RUN: rule engine only, facts injected at the seam ==\n")
    cases = {
        "P1-injected (anticoagulated fall)": [
            ("E.mechanism", "fall", "reported"), ("M.anticoagulant", True, "confirmed"),
            ("complaint.pain_rating", 7, "reported")],
        "P1-guard (anticoagulant only PROBABLE)": [
            ("E.mechanism", "fall", "reported"), ("M.anticoagulant", True, "probable")],
        "P4-injected (healthy sore throat)": [
            ("complaint.category", "sore_throat", "reported"),
            ("complaint.pain_rating", 3, "reported")],
        "P5-injected (chemo + fever)": [
            ("history.immunocompromised", True, "reported"), ("complaint.fever", True, "reported"),
            ("complaint.fever", True, "reported")],
    }
    for name, writes in cases.items():
        f = engine.Facts()
        for field, v, st in writes:
            f.write(field, v, status=st, who="test", turn=0)
        t = engine.evaluate_tree(f, criteria)
        print(f"{name}\n  floor: {t['floor']}   fired: {[r['id'] for r in t['fired']]}"
              f"   consider: {[r['id'] for r in t['consider']]}\n")


def live(only=None):
    import interview, report
    criteria = engine.load_criteria()
    personas = load_personas()
    results = {}
    for p in personas:
        if only and p["id"] not in only:
            continue
        if os.path.exists(os.path.join(OUT, f"{p['id']}-report.txt")):
            print(f"skip {p['id']} (report exists - delete out/ file to rerun)", flush=True)
            continue
        print(f"\n########  {p['id']}  (Yale row {p['yale_row']}, real ESI {p.get('expect_floor') or 'no floor expected'})")
        lines = []
        def log(s):
            print(s, flush=True)
            lines.append(s)
        try:
            facts, tree, transcript, turns = interview.run_interview(p, criteria, log)
        except Exception as e:
            log(f"  !! scenario aborted: {e}")
            open(os.path.join(OUT, f"{p['id']}-transcript.txt"), "w").write("\n".join(lines))
            results[p["id"]] = {"error": str(e)[:200]}
            continue
        try:
            rep = report.render(p["id"], facts, tree)
        except Exception as e:
            rep = f"(report generation failed: {e})" 
        open(os.path.join(OUT, f"{p['id']}-transcript.txt"), "w").write("\n".join(lines))
        open(os.path.join(OUT, f"{p['id']}-report.txt"), "w").write(rep)
        hits, misses = score(p, facts)
        ok_floor = tree["floor"] == p["expect_floor"]
        ok_rules = all(any(r["id"] == e for r in tree["fired"]) for e in p["expect_rules"])
        results[p["id"]] = {"turns": turns, "floor": tree["floor"], "floor_ok": ok_floor,
                            "rules_ok": ok_rules, "extraction": f"{len(hits)}/{len(hits)+len(misses)}",
                            "misses": misses}
        print(f"\n--- {p['id']}: floor={tree['floor']!r} (expected {p['expect_floor']!r}) "
              f"rules_ok={ok_rules} extraction={len(hits)}/{len(hits)+len(misses)}")
        for m in misses:
            print(f"    MISS {m}")
    json.dump(results, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    print("\n== SUMMARY ==")
    for k, v in results.items():
        print(f"  {k}: floor_ok={v['floor_ok']} rules_ok={v['rules_ok']} "
              f"extraction={v['extraction']} turns={v['turns']}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry"
    if mode == "dry":
        dry()
    else:
        live(set(sys.argv[2:]) or None)
