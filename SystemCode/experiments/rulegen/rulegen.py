"""rulegen — programmatic rule extraction from the ESI v5 handbook, schema-constrained.

The knowledge-engineering pipeline (task A) as a runnable script:
  page text  ->  LLM drafts rules that MUST conform to rules/criteria.schema.json
             ->  schema validation (jsonschema)          -> number: schema-valid rate
             ->  span check (quoted span must occur on the cited page) -> number: span-verified rate
             ->  diff against the reviewed rules/criteria.yaml -> numbers: matched-existing vs new
Two modes, same schema, same gates, SAME MODEL (pinned; no rotation in whole mode):
  --mode perpage (default): one LLM call per page, page text extracted by PyMuPDF, neighbour overlap
                            -> out/criteria.draft.perpage.yaml (re-running a page replaces its entries)
  --mode whole:             the PDF itself sent to Gemini in ONE call; the model reads and cites pages
                            -> out/criteria.draft.whole.yaml
Every run writes a log to out/runs/. Compare the modes with compare.py.

Run (forces the Gemini backend regardless of .env):
  LLM_BACKEND=gemini .venv/bin/python experiments/rulegen/rulegen.py --pages 12,13
Printed page numbers are the handbook's own (as cited in criteria.yaml); PDF index = printed + 6.

The LLM never decides the shape: the schema is embedded in the prompt AND enforced afterwards;
anything non-conforming is rejected and counted. Provenance for a single-page run can only be
verbatim or operationalized (supplemented needs an external source).
"""
import os, sys, re, json, time, argparse, difflib
import yaml, jsonschema, pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "prototype"))
import llm  # noqa: E402  (prototype seam: ask_json, MODEL_NAME; backend from LLM_BACKEND)

PDF = os.path.join(ROOT, "sources", "ESI-Handbook-5th-Edition-3-2023.pdf")
SCHEMA = json.load(open(os.path.join(ROOT, "rules", "criteria.schema.json")))
EXISTING = [r for r in yaml.safe_load(open(os.path.join(ROOT, "rules", "criteria.yaml"))) if r.get("when")]
OFFSET = 6

SYSTEM = f"""You extract triage criteria from ONE page of the Emergency Severity Index (ESI) v5 handbook
into a strict machine schema. You are a drafting assistant, not an authority: use ONLY the page text
provided. Never use outside medical knowledge to add criteria.

Return ONLY JSON: {{"rules": [ <rule>, ... ]}} where every <rule> conforms EXACTLY to this JSON Schema
(no extra keys, exactly one operator per leaf, nesting only via all/any):
{json.dumps({k: v for k, v in SCHEMA.items() if not k.startswith("x-")})}

Field vocabulary — prefer these existing dotted field names; invent a new one only if no existing
field fits, following the same prefix conventions (obs. = clinician-observed, vitals., complaint.,
history., patient., E. = event/mechanism, M. = medications):
{json.dumps(SCHEMA["x-known-fields"])}

Rules for each entry:
- id: use "<decision_point>-00.<kebab-slug>" (the number is assigned later).
- decision_point: A = requires immediate life-saving intervention (ESI 1); B = high-risk situation /
  severe pain-distress / new confusion (ESI 2); C = resource prediction; D = vital-sign danger zone.
- span: COPY the supporting sentence or phrase VERBATIM from the page text — no paraphrase; it will
  be checked mechanically against the page.
- source: "ESI v5 p.{{printed_page}} (<short section name>)".
- provenance: "verbatim" if the page states the condition directly (including any number it gives);
  "operationalized" if you had to pin a number/count/threshold to fuzzy wording — then say what you
  chose and why in notes. Never "supplemented" (single-page run).
- effect_override: only when the page's verb is softer than assign — "should be considered" ->
  "consider"; "reassess" -> "reassess_uptriage_consider". Otherwise omit.
- assessed_via: "reported" if a caregiver can answer it by phone, "observed" if it needs a
  clinician's eyes on the patient, "vitals" if it needs measurement.
- One rule per distinct criterion on the page. If the page has no criteria, return {{"rules": []}}."""

def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    s = re.sub(r"[\s\-]+", " ", s)
    return s.strip()

def span_check(span, page_text):
    ns, nt = norm(span), norm(page_text)
    if ns in nt: return "strict"
    # fuzzy: best-matching window of similar length
    L = len(ns); best = 0.0
    step = max(1, L // 4)
    for i in range(0, max(1, len(nt) - L + 1), step):
        r = difflib.SequenceMatcher(None, ns, nt[i:i + L]).ratio()
        if r > best: best = r
        if best >= 0.92: break
    return "fuzzy" if best >= 0.85 else "fail"

def fields_of(c, acc=None):
    acc = set() if acc is None else acc
    if isinstance(c, dict):
        if "field" in c: acc.add(c["field"])
        for k in ("all", "any"):
            for s in c.get(k, []): fields_of(s, acc)
    return acc

def match_existing(draft):
    ds = set(norm(draft.get("span", "")).split()); df = fields_of(draft.get("when"))
    best, why = None, None
    for r in EXISTING:
        if r["decision_point"] != draft.get("decision_point"): continue
        rs = set(norm(str(r["span"])).split())
        jac = len(ds & rs) / max(1, len(ds | rs))
        if jac >= 0.5: best, why = r["id"], f"span-jaccard {jac:.2f}"; break
        if df and df == fields_of(r["when"]): best, why = r["id"], "same fields"; break
    return best, why

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="", help="printed page numbers, comma-separated (e.g. 12,13)")
    ap.add_argument("--mode", choices=["perpage", "whole"], default="perpage")
    ap.add_argument("--backend", choices=["api", "gemini-cli", "codex-cli", "agy"], default="api",
                    help="api = prototype seam (Gemini API/Ollama); gemini-cli / codex-cli / agy = headless CLIs (design-time drafting only)")
    ap.add_argument("--model", default="gemini-3.6-flash", help="pinned model for comparability (for CLIs: the CLI's model name)")
    ap.add_argument("--exhaustive", action="store_true",
                    help="whole mode: add an explicit enumerate-everything instruction (logged as a separate run)")
    ap.add_argument("--overlap", type=int, default=600,
                    help="chars of the previous page's tail and next page's head shown as context (0 = none)")
    args = ap.parse_args()
    pages = [int(p) for p in args.pages.split(",")] if args.pages else []
    doc = pymupdf.open(PDF)
    if args.backend == "api" and llm.MODEL_NAME() != args.model:
        sys.exit(f"model mismatch: backend would use {llm.MODEL_NAME()}; set GEMINI_MODELS={args.model} so runs are comparable")
    if args.backend != "api" and args.mode == "whole":
        sys.exit("whole mode (PDF bytes) is API-only; CLIs receive text — use --mode perpage with a CLI backend")
    if args.mode == "whole":
        return run_whole(args, doc)
    validator = jsonschema.Draft202012Validator(SCHEMA)
    known = set(SCHEMA["x-known-fields"])
    tag = time.strftime("%Y-%m-%d-%H%M") + f"-{args.backend}" + ("" if args.backend == "api" else f"-{args.model}") + "-p" + "-".join(map(str, pages))
    drafts_path = os.path.join(HERE, "out", "criteria.draft.perpage" + ("" if args.backend == "api" else f".{args.backend}.{args.model}") + ".yaml")
    kept = []
    if os.path.exists(drafts_path):   # merge: drop earlier entries from the pages being re-run
        for r in yaml.safe_load(open(drafts_path)) or []:
            m = re.search(r"(?:p\.?\s*|page\s+)(\d+)", str(r.get("source", "")), re.I)
            if not (m and int(m.group(1)) in pages): kept.append(r)
    drafts, rows, counter = [], [], {}; model_used = args.model
    for r in kept:   # continue numbering after what is kept
        dp, n = r["id"][0], int(r["id"][2:4]); counter[dp] = max(counter.get(dp, 0), n - 60)
    t0 = time.time()
    def page_text(pr):
        i = pr + OFFSET - 1
        return doc[i].get_text() if 0 <= i < len(doc) else ""
    for printed in pages:
        text = page_text(printed)
        prev_tail = page_text(printed - 1)[-args.overlap:] if args.overlap else ""
        next_head = page_text(printed + 1)[:args.overlap] if args.overlap else ""
        prompt = (f"Printed page number: {printed}\n\n"
                  f"=== CONTEXT: end of page {printed-1} (for sentences that continue onto this page) ===\n{prev_tail}\n"
                  f"=== PAGE {printed} TEXT — extract criteria from here ===\n{text}\n"
                  f"=== CONTEXT: start of page {printed+1} (for sentences that continue past this page) ===\n{next_head}\n=== END ===\n"
                  f"Use the context only to complete criteria that cross the page break. Quote spans exactly as printed; "
                  f"if a span starts on page {printed-1} or {printed+1}, cite that page in source.")
        window = {printed - 1: prev_tail, printed: text, printed + 1: next_head}
        import backends
        out, _raw, used_model = backends.ask_json(args.backend, prompt, SYSTEM, args.model, ROOT)
        if not isinstance(out, dict) or "rules" not in out:
            out, _raw, used_model = backends.ask_json(args.backend, prompt + "\n\nYour previous reply was not a JSON object with a 'rules' list. Return exactly {\"rules\": [...]}.", SYSTEM, args.model, ROOT)
        model_used = used_model
        rules = out.get("rules", []) if isinstance(out, dict) else []
        print(f"p.{printed}: {len(rules)} drafted", flush=True)
        for r in rules:
            if not isinstance(r, dict): continue
            dp = r.get("decision_point", "X")
            counter[dp] = counter.get(dp, 0) + 1
            slug = re.sub(r"^[ABCD]-\d\d\.", "", str(r.get("id", "unnamed")))
            r["id"] = f"{dp}-{60 + counter[dp]:02d}.{slug}"
            errs = [e.message for e in validator.iter_errors(r)]
            sc, found_on = "n/a", printed
            if not errs:   # search the page first, then the overlap context; cite where the span was found
                for pg in (printed, printed - 1, printed + 1):
                    sc = span_check(str(r.get("span", "")), window[pg]) if window[pg] else "fail"
                    if sc != "fail": found_on = pg; break
                if found_on != printed:
                    r["source"] = re.sub(r"p\.\d+", f"p.{found_on}", str(r.get("source", "")), count=1)
            newf = sorted(fields_of(r.get("when")) - known) if not errs else []
            m, why = match_existing(r) if not errs else (None, None)
            rows.append({"id": r["id"], "page": printed, "schema": "ok" if not errs else "INVALID: " + errs[0][:80],
                         "span": sc, "new_fields": newf, "matches": m, "why": why,
                         "provenance": r.get("provenance"), "effect_override": r.get("effect_override")})
            if not errs: drafts.append(r)
    elapsed = time.time() - t0
    n = len(rows); valid = sum(r["schema"] == "ok" for r in rows)
    strict = sum(r["span"] == "strict" for r in rows); fuzzy = sum(r["span"] == "fuzzy" for r in rows)
    fail = sum(r["span"] == "fail" for r in rows)
    matched = sum(1 for r in rows if r["matches"]); newr = valid - matched
    newf = sorted({f for r in rows for f in r["new_fields"]})
    os.makedirs(os.path.join(HERE, "out", "runs"), exist_ok=True)
    yaml.safe_dump(kept + drafts, open(drafts_path, "w"), sort_keys=False, allow_unicode=True, width=100)
    L = [f"# rulegen run — pages {pages} · backend {args.backend} · model {model_used} · {time.strftime('%Y-%m-%d %H:%M')} · {elapsed:.0f}s\n",
         "| metric | value | derivation |", "| --- | --- | --- |",
         f"| rules drafted | {n} | LLM output entries over {len(pages)} page(s) |",
         f"| schema-valid | {valid}/{n} | jsonschema validation against rules/criteria.schema.json |",
         f"| span verified (strict) | {strict}/{valid} | normalized quoted span is a substring of the page text |",
         f"| span verified (fuzzy ≥0.85) | {fuzzy}/{valid} | best-window SequenceMatcher ratio |",
         f"| span FAILED | {fail}/{valid} | neither — the LLM paraphrased or invented; these are rejected |",
         f"| matched an existing reviewed rule | {matched}/{valid} | same decision point + span-token Jaccard ≥0.5 or identical field set |",
         f"| new candidates (not in reviewed rulebook) | {newr}/{valid} | valid, not matched — for human review |",
         f"| new field names proposed | {len(newf)} | fields outside x-known-fields: {newf} |",
         "\n## Per-rule\n", "| id | page | schema | span | matches existing | provenance | override | new fields |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        L.append(f"| {r['id']} | {r['page']} | {r['schema']} | {r['span']} | {r['matches'] or '—'} {('('+r['why']+')') if r['why'] else ''} | {r['provenance']} | {r['effect_override'] or ''} | {', '.join(r['new_fields'])} |")
    L.append("\n## Reading it\n- Span FAILED = the protocol's auto-reject (`hallucinated-criterion`): no quotable support on the page.\n- 'Matched' ≈ draft survival evidence (the extractor rediscovers reviewed rules); 'new' = candidates for the review log, not rules.\n- Schema-invalid = the LLM tried to change the shape; the shape is not negotiable.")
    rep = "\n".join(L)
    open(os.path.join(HERE, "out", "runs", f"{tag}.md"), "w").write(rep)
    print(f"\n[drafts: {drafts_path} ({len(kept)+len(drafts)} entries) · run log: out/runs/{tag}.md]")
    print(rep)

def _gate(r, validator, known, text_by_page, cited):
    """schema -> span (cited page first, then every page) -> page attribution -> diff. Shared by both modes."""
    errs = [e.message for e in validator.iter_errors(r)]
    if errs: return {"schema": "INVALID: " + errs[0][:80], "span": "n/a", "found": None, "new_fields": [], "matches": None, "why": None}
    sc, found = "fail", None
    order = ([cited] if cited in text_by_page else []) + [p for p in text_by_page if p != cited]
    for pg in order:
        sc = span_check(str(r.get("span", "")), text_by_page[pg])
        if sc != "fail": found = pg; break
    if found is not None and found != cited:
        r["source"] = re.sub(r"p\.\d+", f"p.{found}", str(r.get("source", "")), count=1)
    m, why = match_existing(r)
    return {"schema": "ok", "span": sc, "found": found, "new_fields": sorted(fields_of(r.get("when")) - known), "matches": m, "why": why}

def run_whole(args, doc):
    """One call: the PDF bytes + the same system prompt. No model rotation: a quota error aborts."""
    import llm_gemini
    from google.genai import types
    validator = jsonschema.Draft202012Validator(SCHEMA); known = set(SCHEMA["x-known-fields"])
    text_by_page = {i + 1 - OFFSET: doc[i].get_text() for i in range(len(doc)) if i + 1 - OFFSET >= 1}
    pdf = open(PDF, "rb").read()
    prompt = ("Read the ENTIRE attached ESI v5 handbook and extract every triage criterion from all of it, "
              "following the system instructions exactly. For 'source', cite the PRINTED page number shown on "
              "the page itself (the handbook's own numbering), e.g. 'ESI v5 p.12 (...)'. Return ONLY "
              "{\"rules\": [...]}.")
    if args.exhaustive:
        prompt += ("\n\nBE EXHAUSTIVE. This is an enumeration task, not a summary: go chapter by chapter "
                   "(decision points A, B, C, D; the high-risk examples by body system; the vital-sign tables; "
                   "the pediatric fever rules) and emit one rule for EVERY distinct criterion, example, and "
                   "threshold the handbook states. A complete extraction of this handbook has on the order of "
                   "60 or more rules. Do not stop early.")
    cfg = types.GenerateContentConfig(system_instruction=SYSTEM, response_mime_type="application/json",
                                      temperature=0.4, max_output_tokens=65536)
    t0 = time.time()
    try:
        resp = llm_gemini.client().models.generate_content(
            model=args.model, config=cfg,
            contents=[types.Part.from_bytes(data=pdf, mime_type="application/pdf"), prompt])
    except Exception as e:
        sys.exit(f"whole-mode call failed on {args.model} (no rotation by design): {str(e)[:300]}")
    txt = re.sub(r"^```(json)?|```$", "", (resp.text or "").strip(), flags=re.M).strip()
    try: out = json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", txt, re.S); out = json.loads(m.group(0)) if m else {}
    rules = out.get("rules", []) if isinstance(out, dict) else []
    elapsed = time.time() - t0
    print(f"whole: {len(rules)} drafted in {elapsed:.0f}s ({len(txt):,} chars)", flush=True)
    drafts, rows, counter = [], [], {}
    for r in rules:
        if not isinstance(r, dict): continue
        dp = r.get("decision_point", "X"); counter[dp] = counter.get(dp, 0) + 1
        slug = re.sub(r"^[ABCD]-\d\d\.", "", str(r.get("id", "unnamed")))
        r["id"] = f"{dp}-{60 + counter[dp]:02d}.{slug}"
        m = re.search(r"(?:p\.?\s*|page\s+)(\d+)", str(r.get("source", "")), re.I); cited = int(m.group(1)) if m else None
        g = _gate(r, validator, known, text_by_page, cited)
        rows.append({"id": r["id"], "cited": cited, **g, "provenance": r.get("provenance"), "effect_override": r.get("effect_override")})
        if g["schema"] == "ok": drafts.append(r)
    n = len(rows); valid = sum(r["schema"] == "ok" for r in rows)
    strict = sum(r["span"] == "strict" for r in rows); fuzzy = sum(r["span"] == "fuzzy" for r in rows); fail = sum(r["span"] == "fail" for r in rows)
    attributed = [r for r in rows if r["found"] is not None]; page_ok = sum(1 for r in attributed if r["found"] == r["cited"])
    matched = sum(1 for r in rows if r["matches"]); newf = sorted({f for r in rows for f in r["new_fields"]})
    os.makedirs(os.path.join(HERE, "out", "runs"), exist_ok=True)
    yaml.safe_dump(drafts, open(os.path.join(HERE, "out", "criteria.draft.whole" + ("-exhaustive" if args.exhaustive else "") + ".yaml"), "w"), sort_keys=False, allow_unicode=True, width=100)
    tag = time.strftime("%Y-%m-%d-%H%M") + ("-whole-exhaustive" if args.exhaustive else "-whole")
    L = [f"# rulegen run — mode WHOLE (PDF sent in one call) · model {args.model} · {time.strftime('%Y-%m-%d %H:%M')} · {elapsed:.0f}s\n",
         "| metric | value | derivation |", "| --- | --- | --- |",
         f"| rules drafted | {n} | one call over the whole handbook |",
         f"| schema-valid | {valid}/{n} | jsonschema against rules/criteria.schema.json |",
         f"| span verified (strict) | {strict}/{valid} | quoted span found verbatim on some page (cited page tried first) |",
         f"| span verified (fuzzy ≥0.85) | {fuzzy}/{valid} | best-window ratio |",
         f"| span FAILED | {fail}/{valid} | not found on any page — rejected |",
         f"| page attribution correct | {page_ok}/{len(attributed)} | model's cited printed page == page where the span was found |",
         f"| matched an existing reviewed rule | {matched}/{valid} | same matcher as per-page mode |",
         f"| new candidates | {valid - matched}/{valid} | valid, not matched |",
         f"| new field names proposed | {len(newf)} | {newf} |",
         "\n## Per-rule\n", "| id | cited p. | found p. | schema | span | matches | provenance | override | new fields |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        L.append(f"| {r['id']} | {r['cited']} | {r['found']} | {r['schema']} | {r['span']} | {r['matches'] or '—'} | {r['provenance']} | {r['effect_override'] or ''} | {', '.join(r['new_fields'])} |")
    rep = "\n".join(L); open(os.path.join(HERE, "out", "runs", f"{tag}.md"), "w").write(rep); print(rep)

if __name__ == "__main__":
    main()
