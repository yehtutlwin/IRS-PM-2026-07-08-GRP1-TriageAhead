"""Number 3, handbook form (docs/evaluation-plan.md): the handbook's practice cases given to a model deciding the ESI level
directly, in two forms, k times each, beside the rule engine on the same facts; both judged against the book's answer.
  facts form: the case as the structured facts tests/v4_cases.yaml holds (what the engine sees)
  text form:  the case as printed (tests/v4_case_texts.json)
The cases are the fourth edition's (AHRQ 2012) with the book's answer as truth, as in number 1. The model is also asked to
cite the page of the fifth edition (the rule engine's source) that decides the case and a phrase from it; the citation counts
as verifiable only when the phrase is found on that printed page of the PDF (the check rules/validate.py applies to every rule span).
    LLM_BACKEND=ollama .venv/bin/python experiments/number3_handbook.py [--k 3] [--limit N] [--forms facts,text]
Resumable: experiments/out/number3-handbook.state.json. Writes number3-handbook.json and number3-handbook.md.
"""
import os, re, sys, json, time, argparse, collections, yaml, pymupdf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "prototype")); import engine, llm  # noqa: E402
OUT = os.path.join(ROOT, "experiments", "out"); STATE = os.path.join(OUT, "number3-handbook.state.json")
OFFSET = 6   # PDF page index -> printed page number, as in rules/validate.py
ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=3); ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--forms", default="facts,text"); args = ap.parse_args(); FORMS = args.forms.split(",")

def norm(s):
    s = str(s).lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"[\s\-]+", " ", s).strip()
doc = pymupdf.open(os.path.join(ROOT, "sources", "ESI-Handbook-5th-Edition-3-2023.pdf"))
PAGES = {i + 1 - OFFSET: norm(doc[i].get_text()) for i in range(len(doc)) if i + 1 - OFFSET >= 1}

def case_id(c):
    if c.get("set") == "appA": return f"appA-ch{c['chapter']}-q{c['case']}"
    return f"{('ch10' + c['set']) if c.get('set') else 'ch9'}-{c['case']}"
def text_id(c):   # tests/v4_case_texts.json names the chapter 10 sets without the 'ch10' prefix
    return case_id(c).replace("ch10", "", 1) if c.get("set") and c.get("set") != "appA" else case_id(c)
cases = yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_cases.yaml"))) + yaml.safe_load(open(os.path.join(ROOT, "tests", "v4_posttest_cases.yaml")))
texts = {t["id"]: t["text"] for t in json.load(open(os.path.join(ROOT, "tests", "v4_case_texts.json")))}
def book_levels(c):   # the book's answer; one case (set A, case 7) says "4 or 5"
    return sorted(int(x) for x in re.findall(r"\d", str(c["v4_answer"])))
missing = [case_id(c) for c in cases if text_id(c) not in texts]
assert not missing, f"no printed text for {missing}"
if args.limit: cases = cases[:args.limit]
FIELDS = engine.load_fields(); CRITERIA = engine.load_criteria()

SYSTEM = """You are an experienced emergency department triage nurse. Decide the Emergency Severity Index (ESI) level,
1 to 5, for one practice case from the ESI Implementation Handbook (the fourth edition's practice and competency cases,
AHRQ 2012), exactly as the handbook's own answer key would. Level 1: needs an immediate life-saving intervention. Level 2: high risk,
confused/lethargic/disoriented, severe pain or distress, or dangerous vital signs. Levels 3 to 5 by how many different
resources the patient is expected to need (two or more, one, none), moved up to 2 only when vital signs are in the danger
zone. If you can, cite the printed page of the current handbook (ESI Implementation Handbook, 5th edition, Emergency
Nurses Association, 2023) that decides this case and quote a short phrase printed on it.
Return ONLY JSON: {"level": <1-5>, "decision_point": "A"|"B"|"C"|"D", "reason": "<one sentence>",
"page": <printed page number or null>, "quote": "<phrase printed on that page, or null>"}"""

def facts_prompt(c):
    used = sorted({f["field"] for f in c["facts"] if f["field"] in FIELDS})
    legend = "\n".join(f"- {n}: {FIELDS[n].get('gloss', '')}" for n in used)
    rows = [{"field": f["field"], "value": f["value"], "status": f.get("status", "reported")} for f in c["facts"]]
    return ("The case, as structured facts (status 'observed' means a clinician saw or measured it; 'reported' means it was "
            "told to the nurse):\n" + json.dumps(rows, indent=1) + "\n\nWhat each field means:\n" + legend)
def text_prompt(c): return "The case, as printed in the handbook:\n\n" + texts[text_id(c)]

def engine_verdict(c):
    facts = engine.Facts()
    for f in c["facts"]: facts.write(f["field"], f["value"], status=f.get("status", "reported"), turn=0)
    engine.derive(facts, 0); r = engine.evaluate_tree(facts, CRITERIA)
    ids = lambda es: {e["id"] for e in es}
    claim = "1" if r["esi1_indicators"] else ("at least 2" if r["floor"] else None)
    exp = c["expect"]
    if exp == "esi1": ok = not (set(c["expect_rules"]) - ids(r["esi1_indicators"]))
    elif exp == "floor2": ok = r["floor"] == "at least ESI-2" and not (set(c["expect_rules"]) - ids(r["fired"]))
    else: ok = r["floor"] is None and not r["esi1_indicators"]
    pages = sorted({int(p) for e in r["esi1_indicators"] + r["fired"] for p in re.findall(r"p\.(\d+)", str(e.get("source")))})
    return {"claim": claim, "pass": bool(ok), "pages": pages, "skip": c.get("skip"), "xfail": c.get("xfail")}

def ask(prompt):
    for attempt in range(3):
        try:
            got = llm.ask_json(prompt, system=SYSTEM)
            if isinstance(got, dict) and got.get("level") is not None: return got
        except Exception as e: got = {"error": str(e)[:200]}
        time.sleep(3)
    return got if isinstance(got, dict) else {"error": "no JSON"}

def judge(c, got):
    try: lvl = int(got.get("level"))
    except (TypeError, ValueError): lvl = None
    bl = book_levels(c); book = min(bl); page = got.get("page"); quote = got.get("quote")
    try: page = int(page) if page is not None else None
    except (TypeError, ValueError): page = None
    cited = page is not None and bool(quote); verified = cited and page in PAGES and norm(quote) in PAGES[page]
    return {"level": lvl, "book": book, "book_levels": bl, "exact": lvl in bl, "within1": lvl is not None and min(abs(lvl - b) for b in bl) <= 1,
            "model_under_triage": book <= 2 and lvl is not None and lvl > max(bl), "cited": cited, "verified": bool(verified),
            "page": page, "quote": quote, "decision_point": got.get("decision_point"), "reason": got.get("reason"), "error": got.get("error")}

st = json.load(open(STATE)) if os.path.exists(STATE) else {}
t0 = time.time(); n_calls = 0
for i, c in enumerate(cases):
    cid = case_id(c); rec = st.setdefault(cid, {"book": min(book_levels(c)), "book_levels": book_levels(c), "synopsis": c.get("synopsis"), "engine": engine_verdict(c)})
    rec["engine"] = engine_verdict(c)   # always current
    for form in FORMS:
        runs = rec.setdefault(form, [])
        while len(runs) < args.k:
            got = ask(facts_prompt(c) if form == "facts" else text_prompt(c)); runs.append(judge(c, got)); n_calls += 1
            json.dump(st, open(STATE, "w"), indent=1)
    if i % 10 == 0: print(f"{i + 1}/{len(cases)} cases, {n_calls} calls, {time.time() - t0:.0f}s", flush=True)
json.dump(st, open(STATE, "w"), indent=1)

# ---------- scoring ----------
def rate(n, d): return f"{n}/{d} ({100.0 * n / d:.1f}%)" if d else "-"
by_level = collections.defaultdict(lambda: collections.Counter())
S = {form: collections.Counter() for form in FORMS}; E = collections.Counter()
for cid, rec in st.items():
    book = rec["book"]; bl = rec.get("book_levels", [book]); bkey = " or ".join(map(str, bl)); e = rec["engine"]
    E["cases"] += 1; E["pass"] += e["pass"]; E["claim"] += e["claim"] is not None
    if book <= 2: E["high_cases"] += 1; E["high_claimed"] += e["claim"] is not None; E["high_pass"] += e["pass"]; E["high_silent_pass"] += e["pass"] and e["claim"] is None
    else: E["low_cases"] += 1; E["low_pass"] += e["pass"]; E["low_claimed"] += e["claim"] is not None
    by_level[bkey]["cases"] += 1; by_level[bkey]["engine_pass"] += e["pass"]
    for form in FORMS:
        runs = rec.get(form, [])[:args.k]; s = S[form]
        s["runs"] += len(runs); s["cases"] += 1
        for r in runs:
            for key in ("exact", "within1", "cited", "verified", "model_under_triage"): s[key] += bool(r[key])
            s["no_answer"] += r["level"] is None
            by_level[bkey][f"{form}_exact"] += bool(r["exact"]); by_level[bkey][f"{form}_runs"] += 1
        levels = [r["level"] for r in runs]
        if len(runs) == args.k: s["identical"] += len(set(levels)) == 1; s["identical_and_right"] += len(set(levels)) == 1 and levels[0] in bl
        if book <= 2: s["high_runs"] += len(runs); s["high_under"] += sum(bool(r["model_under_triage"]) for r in runs)
        if book >= 3: s["low_runs"] += len(runs); s["low_over"] += sum(1 for r in runs if r["level"] is not None and r["level"] <= 2)
        if not all(r["within1"] for r in runs): s["cases_with_gross_miss"] += 1

model = llm.MODEL_NAME(); stamp = time.strftime("%Y-%m-%d %H:%M")
L = [f"# Number 3, handbook form: the rules against a model deciding directly ({stamp})", "",
     f"Model: {model} (backend {llm.BACKEND}), {args.k} runs per case per form. Cases: {E['cases']} handbook practice cases "
     f"([tests/v4_cases.yaml](../../tests/v4_cases.yaml), [tests/v4_posttest_cases.yaml](../../tests/v4_posttest_cases.yaml)); "
     f"printed form from [tests/v4_case_texts.json](../../tests/v4_case_texts.json). Truth: the handbook's own answer. "
     f"Script: [experiments/number3_handbook.py](../number3_handbook.py); per-run detail in number3-handbook.json.", "",
     "## The model, per run", "", "| measure | " + " | ".join(f"{f} form" for f in FORMS) + " |", "|---|" + "---|" * len(FORMS)]
rows = [("runs", lambda s: str(s["runs"])), ("agrees with the book exactly", lambda s: rate(s["exact"], s["runs"])),
        ("within one level of the book", lambda s: rate(s["within1"], s["runs"])),
        ("model under-triage: book level 1 or 2, model lower acuity", lambda s: rate(s["high_under"], s["high_runs"])),
        ("book level 3 to 5, model said 1 or 2", lambda s: rate(s["low_over"], s["low_runs"])),
        ("no usable answer", lambda s: rate(s["no_answer"], s["runs"])),
        ("cited a page and a phrase", lambda s: rate(s["cited"], s["runs"])),
        ("citation verifiable (phrase found on that printed page)", lambda s: rate(s["verified"], s["runs"]))]
for name, fn in rows: L.append(f"| {name} | " + " | ".join(fn(S[f]) for f in FORMS) + " |")
L += ["", "## The model, per case (consistency)", "", "| measure | " + " | ".join(f"{f} form" for f in FORMS) + " |", "|---|" + "---|" * len(FORMS),
      "| same level in all runs | " + " | ".join(rate(S[f]["identical"], S[f]["cases"]) for f in FORMS) + " |",
      "| same level in all runs and it is the book's | " + " | ".join(rate(S[f]["identical_and_right"], S[f]["cases"]) for f in FORMS) + " |",
      "| cases with at least one run two or more levels off | " + " | ".join(rate(S[f]["cases_with_gross_miss"], S[f]["cases"]) for f in FORMS) + " |", "",
      "## The rule engine on the same facts", "",
      "The engine claims level 1 (an ESI-1 indicator fired), 'at least 2' (a floor rule fired) or nothing. A case passes when the "
      "claim matches the book: the book's rule fired for a level 1 or 2 case, and nothing fired for a level 3 to 5 case (the same "
      "judgement as the fixed tests of number 1). The engine gives the same answer every run and every claim names its handbook page.", "",
      "| measure | engine |", "|---|---|",
      f"| cases passing | {rate(E['pass'], E['cases'])} |",
      f"| book level 1 or 2: a claim made (the engine miss rate is the rest) | {rate(E['high_claimed'], E['high_cases'])} |",
      f"| book level 1 or 2: pass, counting the {E['high_silent_pass']} cases the book decides on vital signs, where silence is right | {rate(E['high_pass'], E['high_cases'])} |",
      f"| book level 3 to 5: nothing fired | {rate(E['low_pass'], E['low_cases'])} |",
      f"| claims in all, and how many are on a book level 1 or 2 case | {E['claim']}, {rate(E['high_claimed'], E['claim'])} (the others: see the test file's note on each) |",
      "| same answer every run | all |", "| claims with a verifiable handbook page | all (checked by rules/validate.py) |", "",
      "## By book level", "", "| book level | cases | engine pass | " + " | ".join(f"model exact, {f} form" for f in FORMS) + " |", "|---|---|---|" + "---|" * len(FORMS)]
for lv in sorted(by_level):
    b = by_level[lv]
    L.append(f"| {lv} | {b['cases']} | {rate(b['engine_pass'], b['cases'])} | " + " | ".join(rate(b[f"{f}_exact"], b[f"{f}_runs"]) for f in FORMS) + " |")
L += ["", "## Reading", "",
      "Exact agreement counts a run right only when it names the book's level; the engine's pass counts a level 3 to 5 case "
      "right when it stays silent, which is the engine's job pre-arrival. The two are therefore compared where both make a "
      "claim: book level 1 and 2. Model under-triage is the model naming a lower acuity than the book on those cases; the "
      "engine's counterpart is its miss rate (the book's rule not firing), a silence the nurse sees as 'no claim', not a wrong level."]
open(os.path.join(OUT, "number3-handbook.md"), "w").write("\n".join(L) + "\n")
json.dump({"model": model, "k": args.k, "stamp": stamp, "summary": {f: dict(S[f]) for f in FORMS}, "engine": dict(E), "cases": st},
          open(os.path.join(OUT, "number3-handbook.json"), "w"), indent=1)
print("\n".join(L[:30]))
