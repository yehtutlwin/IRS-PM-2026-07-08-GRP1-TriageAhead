"""Plain-language names and explanations for every drafting configuration ("origin").
Shared by build_review.py (review page) and relate.py (graph legend) so labels stay consistent."""
LABEL = {
    "spike": "Rulebook v2 (Claude, consolidated + mechanically verified)",
    "perpage": "Gemini 3.6 Flash via API · page by page",
    "perpage.agy.gemini-3.6-flash-medium": "Gemini 3.6 Flash via Antigravity CLI · page by page",
    "perpage.agy.gemini-3.1-pro-high": "Gemini 3.1 Pro via Antigravity CLI · page by page",
    "agentic.gemini-3.6-flash-medium": "Gemini 3.6 Flash · agent with tools",
    "agentic.gemini-3.1-pro-high": "Gemini 3.1 Pro · agent with tools",
    "whole-exhaustive": "Gemini 3.6 Flash via API · whole PDF, told to be exhaustive",
    "whole": "Gemini 3.6 Flash via API · whole PDF, plain prompt",
}
EXPLAIN = [
    ("Rulebook v2 (Claude, consolidated + mechanically verified)",
     "The current `rules/criteria.yaml`: 91 executable rules. Version 1 was a feasibility spike (one drafting pass, unverified). Version 2 (29 Aug) was produced by Claude re-reading every source page and consolidating what all seven drafters found: printed-page citations, one rule per criterion, executable pediatric vital-sign and fever rules, the gaps filled — and it passes `rules/validate.py` (schema + every quoted span found verbatim on its cited page). It is still LLM-drafted, not human-verified: 'matched the rulebook' means drafters agree, not that the rule is clinically right. Change log: rules/CHANGELOG.md."),
    ("Gemini via API, page by page",
     "The handbook's text is extracted page by page with a PDF library; each page is sent to the Gemini API (free key, model gemini-3.6-flash) in one call together with the JSON schema, the field vocabulary and the drafting rules; the model returns rules for that page only. Nine calls for the nine decision-point pages. The model cannot use tools or see anything but the page text (plus a few hundred characters of the neighbouring pages so sentences that cross a page break can be completed)."),
    ("Gemini via Antigravity CLI, page by page",
     "Same page-by-page method, but the call goes through Antigravity CLI (`agy`) — Google's command-line AI tool for Google AI Pro subscribers, the successor to Gemini CLI — instead of the API key. That is what gives access to the Pro-tier model (gemini-3.1-pro-high) and higher limits. Tools are switched off, so it is still a pure model call: same prompt, same schema, same checks."),
    ("Gemini via API, whole PDF",
     "The entire handbook PDF is sent to the Gemini API in a single call and the model is asked to extract every criterion and cite the printed page number. 'Plain prompt' is the same instructions as the page runs; 'told to be exhaustive' adds an explicit instruction to enumerate rather than summarise. Reading the PDF natively lets the model see figures and tables that text extraction mangles, but one call over a long document tends to under-generate."),
    ("Gemini agent with tools",
     "Antigravity CLI run as an agent: it gets a fresh folder containing the PDF, the page texts, the schema and an instructions file — and nothing else (in particular, not the reviewed rulebook or earlier drafts) — and may read files and run commands to do the job, writing its rules to an output file. Its full transcript is kept as the run log. The agent typically writes its own checking scripts before finishing."),
    ("Then, for every drafter alike",
     "Every draft passes the same three gates before it counts: (1) schema — it must match `rules/criteria.schema.json` exactly; (2) span — its quoted text must be found verbatim on the cited page; (3) diff — it is matched against the reviewed rulebook to tell re-finds from new candidates. Nothing is promoted into `criteria.yaml` by any of this; a human page-check is the final gate."),
]
