"""The guide's content: sections, their checks, and the words shown for each.

The terminal view and the web page both render these objects, so the two never differ.
Every path, port and command the guide refers to is here and nowhere else; when the
repository's layout changes, change this file.

`root` is the submission repository (README, ProjectReport, Miscellaneous, Video, SystemCode).
The code, the virtual environment and every command live in SystemCode; paths shown to the
reader are relative to that folder, paths the guide serves are relative to the repository.
"""
import os
from dataclasses import dataclass, field
from typing import Callable

from . import checks


@dataclass
class Check:
    id: str
    title: str                      # what is checked, as a noun phrase
    run: Callable[[], tuple]        # () -> (ok, detail)
    fix: object = ""                # what to install or do, in plain words (str, or () -> str)
    command: object = ""            # the exact command, only when it is straightforward (str, or () -> str)
    optional: bool = False          # a failing optional check does not hold the section


@dataclass
class Item:
    title: str
    path: str = ""                  # repository-relative; the web page serves it, the terminal prints it
    note: str = ""                  # what it is, in a sentence or two (**bold** allowed)
    url: str = ""                   # an address instead of a path
    command: str = ""               # a command to try instead of a page to open; the guide never runs it
    group: str = ""                 # a heading over consecutive items with the same group
    meta: str = ""                  # a short fact shown beside the kind of item ("109 entries")
    ready: bool = True              # False: the page is not reachable yet, so the title is shown without a link


@dataclass
class Section:
    id: str
    title: str
    why: str                        # one paragraph: what this section is for
    checks: list = field(default_factory=list)
    items: object = field(default_factory=list)  # things to open or read once the checks pass (list, or () -> list)
    aside: object = field(default_factory=list)  # things to open or read at any time, shown whether or not the checks pass (list, or () -> list)
    done: str = ""                  # shown once every check passes: what you can do now


CODE = "SystemCode"
PY = f"{CODE}/.venv/bin/python"          # every command runs from the repository folder, where the guide is started
GUIDE_PY = checks.guide_python()         # the Python that started the guide, reused for the virtual environment
PIP = f"{CODE}/.venv/bin/pip"


def code_dir(root):
    return os.path.join(root, CODE)


def sections(root=None):
    root = root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return [setup(root), documents(root), rulebook(root), interview_app(root), evidence(root)]


# ---- 2. the documents -------------------------------------------------------------------------

STEM = "IRS-PM-2026-07-08-GRP1-TriageAhead"
DOCUMENTS = [
    # (title, repository path, one line). A video (.mp4) is listed the same way; the page plays it.
    ("Group report", f"ProjectReport/{STEM}-Group-Report.pdf",
     "the project report: the idea, the system, the knowledge base, the evaluation, the conclusions; "
     "the proposal is its Appendix A and the installation and user guide its Appendix C"),
    ("Proposal", f"Miscellaneous/{STEM}-Proposal.pdf", "the practice-module proposal as submitted on 13 September 2026"),
    ("Proposal slides", f"Miscellaneous/{STEM}-Proposal-Slides.pdf", "the slides of the proposal presentation"),
    ("Promotion video", f"Video/{STEM}-promotion.mp4",
     "4 minutes 12 seconds: the business pain and value, the use-case demo on the real app, the waiting room, "
     "the evidence, the market and the price"),
    ("System video", f"Video/{STEM}-system.mp4",
     "5 minutes 26 seconds: the system design and the technical explanation of the use cases, the experiments "
     "and the technique groups"),
]
def documents(root):
    def present():
        missing = [t for t, p, _ in DOCUMENTS if not os.path.isfile(os.path.join(root, p))]
        if missing:
            return False, "missing from this checkout: " + ", ".join(missing)
        return True, f"all {len(DOCUMENTS)} documents are in this checkout"

    return Section(
        id="documents",
        title="2. The documents",
        why=("**Nothing to install.** These are the delivered documents and videos, as committed in the "
             "repository. Each opens in the browser."),
        checks=[
            Check(id="docs-present", title="The documents in this checkout", run=present,
                  fix="A file the guide expected is not in this checkout. A fresh pull of the repository restores it."),
        ],
        items=[Item(t, p, n) for t, p, n in DOCUMENTS],
        done=("**The group report is the place to start.** The proposal and the slides are where it began. "
              "The two videos show the system in use and how it is built."),
    )


def setup(root):
    return Section(
        id="setup",
        title="1. Python and the packages",
        why=("**Everything runs from one virtual environment inside the `SystemCode` folder, `.venv`.** "
             "Nothing is installed system-wide.\n\n"
             "Each command in this guide runs in a second terminal, in the repository folder, the one that "
             "holds `README.md` and `SystemCode`. The guide notices when a command has worked and moves on.\n\n"
             "The guide starts each app on a port of its own, so nothing else on the machine is mistaken for it."),
        checks=[
            Check(
                id="checkout",
                title="The repository folder",
                run=lambda: checks.file_present(os.path.join(code_dir(root), "requirements.txt"), "SystemCode/requirements.txt"),
                fix="The guide finds its files only inside a complete copy of the repository.",
            ),
            Check(
                id="linux-fs",
                title="A Linux or macOS file system",
                run=checks.not_under_windows_mount,
                fix="**Under WSL2, keep the repository in your Linux home folder**, not under `/mnt/c/`. "
                    "The Windows-mounted paths are much slower and break file permissions. "
                    "A fresh clone into the Linux home folder avoids both.",
                optional=True,
            ),
            Check(
                id="venv-module",
                title="Python's venv module",
                run=lambda: checks.system_python_has("venv, ensurepip"),
                fix=f"Debian and Ubuntu ship Python without the venv module. The command below adds it for `{GUIDE_PY}`. "
                    "This is the one system-wide install. macOS and python.org Pythons already have it.",
                command=lambda: "sudo apt install " + (GUIDE_PY if GUIDE_PY.startswith("python3.") else "python3") + "-venv",
            ),
            Check(
                id="venv",
                title="The virtual environment .venv",
                run=lambda: checks.venv_present(code_dir(root)),
                fix=lambda: (f"**The virtual environment was made with a different Python than the one running the guide.** "
                             f"The guide runs on `{GUIDE_PY}`; the packages must be installed for that same Python. "
                             f"The command below removes the old environment and makes it again with `{GUIDE_PY}`."
                             if checks.venv_mismatch(code_dir(root)) else
                             f"The virtual environment lives inside the `SystemCode` folder. The command below creates it "
                             f"there with `{GUIDE_PY}`, the Python that is running this guide, and brings its pip up to date."),
                command=lambda: ((f"rm -rf {CODE}/.venv && " if checks.venv_mismatch(code_dir(root)) else "")
                                 + f"{GUIDE_PY} -m venv {CODE}/.venv && {CODE}/.venv/bin/pip install --upgrade pip"),
            ),
            Check(
                id="packages",
                title="The packages, installed into .venv",
                run=lambda: checks.venv_imports(code_dir(root), ["yaml", "segno"]),
                fix="The project's packages install into `.venv` with the command below. It takes a few minutes "
                    "and a few hundred megabytes. Nothing outside the `SystemCode` folder changes.",
                command=f"{PIP} install -r {CODE}/requirements.txt",
            ),
        ],
        done="**Python and the packages are in place.**",
    )


# ---- 3. the rulebook and its review ----------------------------------------------------------

REVIEW_PORTS = [9091, 9191]             # the guide's own ports for the review app (its default is 8091), and a fallback
REVIEW_SIGNATURE = "Rulebook review"
HANDBOOK_PDFS = [                       # fetched per person by sources/download.sh (copyright); never committed
    (f"{CODE}/sources/ESI-Handbook-5th-Edition-3-2023.pdf", "the ESI handbook, 5th edition"),
    (f"{CODE}/sources/NICE-NG232-main-guideline.pdf", "the NICE head-injury guideline"),
]
RULE_FILES = [
    ("The rules", f"{CODE}/rules/criteria.yaml",
     "one entry per rule: the facts it reads, its effect, the handbook page and the quoted sentence"),
    ("The fields", f"{CODE}/rules/fields.yaml", "every fact the rules read, with its meaning and everyday wording"),
    ("The bridges", f"{CODE}/rules/bridges.yaml",
     "cited translations from what a family member can report to the fact a rule reads"),
    ("The triggers", f"{CODE}/rules/triggers.yaml", "when each question is asked, with its reason"),
    ("The fuzzy terms and options", f"{CODE}/rules/terms.yaml",
     "the number, band or list behind each word the handbook leaves open (infant, elderly, a blood thinner)"),
    ("The agenda", f"{CODE}/rules/derived/agenda.yaml",
     "what the interview may ask, derived from the rules by rules/derive.py; never edited directly"),
    ("The test cases", f"{CODE}/tests/v4_cases.yaml", "the handbook's practice cases written as test cases"),
]
REVIEW_PAGES = [   # (title, path on the review app, one line)
    ("Rules", "/", "every rule beside its handbook page, the quoted sentence highlighted where it is found"),
    ("Bridges", "/?set=bridges", "each everyday sign beside the page that ties it to the fact a rule reads"),
    ("Triggers", "/?set=triggers", "the authored conditions that open a question, each with its reason"),
    ("Terms and options", "/?set=terms", "the fuzzy terms and the options of the choice fields, with their sources"),
    ("Handover and screening questions", "/?set=history", "the questions no rule reads, asked for the nurse"),
    ("Practice cases", "/cases", "the handbook's practice cases beside their page, with the rule engine's outcome on each"),
]


TESTS_NOTE = ("The handbook's practice cases, run against the rule engine, plus checks of the interview's agenda "
              "and bridges. In the last line pytest prints:\n\n"
              "- **passed**: the engine gives the book's answer.\n"
              "- **xfailed**: a known failure, kept on purpose. Its reason is in the test cases file below.\n"
              "- **skipped**: the book decides on vital signs, which the system leaves to the nurse.")


def count_entries(path):
    try:
        with open(path, encoding="utf-8") as f:
            return sum(1 for ln in f if ln.startswith("- id:"))
    except OSError:
        return 0


def rulebook(root):
    def rules_present():
        n = count_entries(os.path.join(code_dir(root), "rules", "criteria.yaml"))
        return (n > 0, f"rules/criteria.yaml has {n} entries" if n else "rules/criteria.yaml is missing or empty")

    def pdfs_present():
        missing = [what for p, what in HANDBOOK_PDFS if not os.path.isfile(os.path.join(root, p))]
        if missing:
            return False, "not fetched yet: " + ", ".join(missing)
        return True, "the handbook PDFs are in SystemCode/sources/"

    def pdf_command():
        return f"bash {CODE}/sources/download.sh" if checks.tool("curl")[0] else ""

    def pdf_fix():
        if checks.tool("curl")[0]:
            return ("**The rules quote the ESI handbook and the NICE guideline.** Both are copyrighted, so each copy "
                    "is fetched by the script below rather than shipped. The files stay in `sources/` and are never committed.")
        return ("**The rules quote the ESI handbook and the NICE guideline.** The script that fetches them, "
                "`sources/download.sh`, needs curl.\n\n"
                "On Debian and Ubuntu, `sudo apt install curl` adds it. After that, `bash SystemCode/sources/download.sh` fetches the files.")

    def app():
        ok, detail, port = checks.app_answering(REVIEW_PORTS, REVIEW_SIGNATURE)
        return ok, detail

    def app_command():
        port = REVIEW_PORTS[0] if checks.port_free(REVIEW_PORTS[0]) else REVIEW_PORTS[1]
        return f"REVIEW_PORT={port} {PY} {CODE}/review/app.py"

    def items():
        ok, _, port = checks.app_answering(REVIEW_PORTS, REVIEW_SIGNATURE)
        base = f"http://localhost:{port or REVIEW_PORTS[0]}"
        out = [Item(t, url=base + p, note=n, group="The rule review app") for t, p, n in REVIEW_PAGES]
        out.append(Item("The test cases, run against the rule engine", command=f"{PY} -m pytest {CODE}/tests/ -q", note=TESTS_NOTE,
                        group="The test cases"))
        for t, p, n in RULE_FILES:
            c = count_entries(os.path.join(root, p))
            out.append(Item(t, p, n, group="The knowledge files", meta=f"{c} entries" if c else ""))
        return out

    return Section(
        id="rulebook",
        title="3. The rulebook and its review",
        why=("**The rule review app is what we built for professional review and human oversight of the "
             "knowledge base.**\n\n"
             "The rules were extracted from the ESI handbook by a language model. Every rule carries the handbook "
             "page and the sentence it quotes. The review app puts each rule beside that page, with the sentence "
             "highlighted where the page really says it. A clinician or an examiner can judge the rule there and "
             "record a verdict: accept, edit, reject or unsure.\n\n"
             "- Recording a verdict is optional. The mechanism is what is on show.\n"
             "- The app is a small server from the repository. It runs in a second terminal and stays open "
             "while the pages are read. Ctrl-C stops it.\n"
             "- The test cases are the handbook's own practice cases. One command runs them against the rule engine."),
        checks=[
            Check(id="rules-present", title="The rules file", run=rules_present,
                  fix="rules/criteria.yaml is not in this checkout. A fresh pull of the repository restores it."),
            Check(id="packages", title="PyYAML and PyMuPDF in .venv",
                  run=lambda: checks.venv_imports(code_dir(root), ["yaml", "pymupdf"]),
                  fix="The review app reads the rules with PyYAML and renders the handbook pages with PyMuPDF. "
                      "Both install into `.venv` with the command below.",
                  command=f"{PIP} install -r {CODE}/requirements.txt"),
            Check(id="pdfs", title="The handbook PDFs", run=pdfs_present, fix=pdf_fix, command=pdf_command),
            Check(id="review-app", title="The rule review app, running", run=app,
                  fix="**The review app runs in a second terminal and stays open while its pages are read.**\n\n"
                      "Verdicts go to a small local file, `SystemCode/review/reviews.db`, which git ignores. "
                      "If port 9091 is taken, the command below uses 9191 and the guide looks there.",
                  command=app_command),
        ],
        items=items,
        done=("**The review app is at the first link below. Any rule is a good place to start.** "
              "The page on the right is the handbook. The highlight is the sentence the rule rests on."),
    )


# ---- 4. the interview app ---------------------------------------------------------------------

WEBAPP_PORTS = [9090, 9190]             # the guide's own ports for the interview app (its default is 8090), and a fallback
WEBAPP_SIGNATURE = "ED Pre-Arrival Intake"
PLACEHOLDER_KEY = "your_key_here"       # what .env.example ships
RECORDED, RECORDED_SID = "experiments/out/sessions-hand-played-2026-10-15", "OTTER-8193"   # section 3.2 and Figure 5 of the report
WAITING, WAITING_SID = "experiments/out/sessions-waiting-room-2026-10-19", "SAGA-7904"      # the promotion video's waiting room
LOCAL_SESSIONS = "prototype/out/sessions-local"   # the app's own sessions folder, relative to SystemCode; git ignores it
OLLAMA_DEFAULT_MODEL = "gemma4:12b"

BACKENDS_NOTE = (
    "**Gemini, recommended.** A free key from Google AI Studio (`https://aistudio.google.com/apikey`), nothing to "
    "install. In `SystemCode/.env`:\n\n"
    "- `LLM_BACKEND=gemini`\n"
    "- `GEMINI_API_KEY=` followed by the key\n\n"
    "The free tier paces its calls, so a turn takes several seconds and a session about twenty minutes.\n\n"
    "**Ollama, the alternative.** A model on this machine, with no key and no quota. It needs Ollama "
    "(`https://ollama.com/download`), the model pulled once with `ollama pull gemma4:12b` (about 7 GB), and a "
    "GPU with 8 GB of memory for comfortable speed. In `SystemCode/.env`: `LLM_BACKEND=ollama`."
)


def interview_app(root):
    env_path = os.path.join(code_dir(root), ".env")

    def env():
        return checks.dotenv(env_path)

    def backend():
        return (env().get("LLM_BACKEND") or "gemini").strip().lower()

    def env_present():
        return checks.file_present(env_path, "SystemCode/.env")

    def model():
        b = backend()
        if b == "gemini":
            key = env().get("GEMINI_API_KEY", "")
            if not key or key == PLACEHOLDER_KEY:
                return False, "backend gemini: no GEMINI_API_KEY in SystemCode/.env yet"
            return True, f"backend gemini, key set ({len(key.split(','))} key{'s' if ',' in key else ''})"
        if b == "ollama":
            want = env().get("OLLAMA_MODEL") or OLLAMA_DEFAULT_MODEL
            models = checks.ollama_models(env().get("OLLAMA_HOST") or "http://localhost:11434")
            if models is None:
                return False, "backend ollama: no Ollama server answers on this machine"
            if want not in models and want.split(":")[0] not in [m.split(":")[0] for m in models]:
                return False, f"backend ollama: the server has no model {want} (it has: {', '.join(models) or 'none'})"
            return True, f"backend ollama, model {want} is present"
        if b == "claude":
            ok = bool(env().get("ANTHROPIC_API_KEY"))
            return ok, "backend claude, key set" if ok else "backend claude: no ANTHROPIC_API_KEY in SystemCode/.env"
        return False, f"LLM_BACKEND={b!r} is not one the app knows (gemini, ollama or claude)"

    def model_fix():
        b = backend()
        if b == "gemini":
            return ("**A Gemini key is still needed.** It is free: `https://aistudio.google.com/apikey` gives one in a "
                    "minute. It goes into `SystemCode/.env` as the value of `GEMINI_API_KEY`.\n\n" + BACKENDS_NOTE)
        if b == "ollama":
            return ("**Ollama is still needed on this machine**, with the model pulled.\n\n" + BACKENDS_NOTE)
        return BACKENDS_NOTE

    def model_command():
        b = backend()
        if b == "ollama" and checks.ollama_models(env().get("OLLAMA_HOST") or "http://localhost:11434") is not None:
            return f"ollama pull {env().get('OLLAMA_MODEL') or OLLAMA_DEFAULT_MODEL}"
        return ""

    def app():
        ok, detail, port = checks.app_answering(WEBAPP_PORTS, WEBAPP_SIGNATURE, probe="/api/info", probe_what="info page")
        return ok, detail

    def app_command():
        port = WEBAPP_PORTS[0] if checks.port_free(WEBAPP_PORTS[0]) else WEBAPP_PORTS[1]
        return f"WEBAPP_PORT={port} {PY} {CODE}/webapp/server.py"

    def base():
        ok, _, port = checks.app_answering(WEBAPP_PORTS, WEBAPP_SIGNATURE, probe="/api/info", probe_what="info page")
        return f"http://localhost:{port or WEBAPP_PORTS[0]}"

    def aside():
        # the app that has the recorded session is the one to link: another copy of the app on the same port
        # (a second checkout on this machine) answers its info page but not the session
        up, _, port = checks.app_answering(WEBAPP_PORTS, WEBAPP_SIGNATURE, probe=f"/api/state/{RECORDED_SID}",
                                           probe_what=f"session {RECORDED_SID}")
        b = f"http://localhost:{port or WEBAPP_PORTS[0]}"
        placed = os.path.isfile(os.path.join(code_dir(root), LOCAL_SESSIONS, RECORDED_SID + ".json"))
        ready = bool(up and placed)
        grp = "Without playing a session: the one the group report walks through, shown in the app"
        state = ("**The links below are live.** " if ready else
                 "**The links below open once the app runs and the sessions are in place.** ")
        out = [Item("The recorded sessions, placed where the app reads them",
                    command=f"mkdir -p {CODE}/{LOCAL_SESSIONS} && cp {CODE}/{RECORDED}/{RECORDED_SID}.* "
                            f"{CODE}/{WAITING}/{WAITING_SID}.* {CODE}/{LOCAL_SESSIONS}/",
                    group=grp,
                    note=state + ("Already in place. " if placed else "") +
                         "The app shows only the sessions in its own folder, and opening a report adds to a session's "
                         "files, so the recorded copies stay as recorded. Git ignores that folder.\n\n"
                         "The app needs no language model for this: started with the command in the steps above, "
                         "before any `.env` exists, it still shows these sessions. Only the AI summary stays unwritten.")]
        out += [
            Item(f"Session {RECORDED_SID}: the family's chat", url=f"{b}/chat/{RECORDED_SID}", ready=ready,
                 note=f"**The session section 3.2 of the group report walks through and Figure 5 shows, used in both "
                      "videos.** A fall at home, a patient on a blood thinner. The chat as the family saw it, with the "
                      "ticket and the QR link at the end."),
            Item(f"Session {RECORDED_SID}: the nurse's report", url=f"{b}/r/{RECORDED_SID}", ready=ready,
                 note="The page the nurse opens: the floor of at least ESI-2 from the anticoagulated-trauma rule with "
                      "its source pages, the consider flags, the complaints and the history with who said each fact. "
                      "The AI summary is written on the first opening, one call to the model."),
            Item(f"Session {WAITING_SID}: the nurse's report after the waiting room", url=f"{b}/r/{WAITING_SID}", ready=ready,
                 note=f"**The promotion video's waiting-room segment.** After the family pressed the arrived button, the "
                      "chat checked in. A worsening answer told the family to alert the counter and put the banner at "
                      "the top of this page."),
        ]
        return out

    def items():
        b = base()
        return [
            Item("The caregiver chat", url=b + "/",
                 note="**The system itself.** The first question is whether an ambulance is on the way or the patient "
                      "is already heading to the emergency department. From there the reader answers as a family "
                      "member would, in their own words, as briefly as they like.\n\n"
                      "After about a dozen answers the floor is settled and the chat shows a ticket and the QR link to "
                      "**the nurse's report**: the urgency floor with the rules that set it and their handbook pages, "
                      "the complaints, the history in AMPLE order with who said each fact, and an AI summary written "
                      "from the stored facts only."),
            Item("A dry run of the rule engine", command=f"{PY} {CODE}/prototype/run.py dry",
                 note="Four made-up cases given to the rule engine as facts, with no language model involved: the "
                      "floor of each and the rules that fired, in a few lines. The rules decide; the model only "
                      "translates."),
        ]

    return Section(
        id="interview-app",
        title="4. The interview app",
        why=("**The chat is the system.** A family member answers in their own words. The language model phrases "
             "each question and turns each answer into facts. The rules decide the urgency floor; the model never "
             "does.\n\n"
             "The model comes from one of two free backends, chosen in `SystemCode/.env`:\n\n"
             "- **Gemini**, recommended: a free key from Google AI Studio, nothing to install.\n"
             "- **Ollama**: a model on this machine, for a computer with a GPU.\n\n"
             "The system video shows a whole session, for anyone who would rather watch than play."),
        checks=[
            Check(id="webapp-packages", title="The app's packages in .venv",
                  run=lambda: checks.venv_imports(code_dir(root), ["yaml", "segno", "numpy", "pandas", "joblib", "sklearn",
                                                                  "google.genai"]),
                  fix="The project's packages install into `.venv` with the command below.",
                  command=f"{PIP} install -r {CODE}/requirements.txt"),
            Check(id="env", title="The settings file SystemCode/.env", run=env_present,
                  fix="**The app reads its backend and key from `SystemCode/.env`.** The command below makes it from "
                      "the example. Git ignores it, so a key never leaves this machine.",
                  command=f"cp {CODE}/.env.example {CODE}/.env"),
            Check(id="model", title="A language model the app can use", run=model, fix=model_fix, command=model_command),
            Check(id="webapp", title="The interview app, running", run=app,
                  fix="**The interview app runs in a second terminal and stays open while it is used.** Ctrl-C stops it.\n\n"
                      "If port 9090 is taken, the command below uses 9190 and the guide looks there.",
                  command=app_command),
        ],
        items=items,
        aside=aside,
        done=("**The chat is at the first link below.** Playing a caregiver takes about a dozen answers. "
              "A turn takes several seconds on the free tier.\n\n"
              "When the floor is settled, the chat shows the ticket and the link to the nurse's report."),
    )


# ---- 5. the evidence behind the report --------------------------------------------------------

EXTRACTION_FILES = [
    ("The complete reading pass of the handbook", f"{CODE}/rules/extraction/v5-complete-pass.yaml",
     "137 sentences of the fifth edition that assign or condition a level, a flag or a reassessment, each with its "
     "printed page; the rules file was rebuilt from this pass on 4 October 2026"),
    ("Four blind re-extractions, compared with the rules file", f"{CODE}/rules/extraction/blind-re-extractions-comparison.md",
     "four models (Claude Opus, Claude Fable, Gemini, GPT) each read the handbook without seeing our rules; rule by "
     "rule, which of them found the same sentence"),
    ("What the comparison changed", f"{CODE}/rules/extraction/BLIND-RE-EXTRACTIONS-ANALYSIS.md",
     "the analysis applied to the rules file on 5 October 2026: the effects corrected, and the two exceptions kept"),
]
RESULTS_PAGE = (f"{CODE}/docs/evaluation-results.md",
                "**Every number in chapter 4 of the report is taken from this page**, and each number names the output "
                "file it comes from. The six questions, the method of each, the result, and the limitations.")
NUMBER_FILES = [
    ("Number 1, encoding fidelity", f"{CODE}/experiments/out/number1-encoding-fidelity.md",
     "154 of 174 handbook cases pass, no level-1 case missed; computed from the test cases of section 3"),
    ("Numbers 2 and 4, the final set of 27 personas", f"{CODE}/experiments/out/task-i-20261019-1452-v2z-27-personas-final-set-sheet-player-local-t0.md",
     "fact capture and the end-to-end floor on the final persona set, played through the real interview"),
    ("Number 3, a model deciding directly", f"{CODE}/experiments/out/number3-handbook.md",
     "the rules against a language model asked for the level itself: the model under-triages, the engine never names a lower level"),
    ("Number 4, arm B", f"{CODE}/experiments/out/number4-second-arm-20261019-27-personas.md",
     "a language model running its own interview on the same 27 personas, for comparison with ours"),
    ("Number 5, the learned signal", f"{CODE}/experiments/out/practice-signal.md",
     "the classifier trained on past visits: AUROC 0.71 from pre-arrival facts, 0.89 once vital signs are known"),
    ("Number 6, floor soundness", f"{CODE}/experiments/out/task-g-full.md",
     "the rules run over 558,029 real visits: how often the floor is stricter than the nurse's level"),
    ("Every persona run, indexed", f"{CODE}/experiments/out/RUNS.md",
     "one row per run of the persona harness, regenerated by the harness itself, with the session transcripts beside it"),
]


def evidence(root):
    def pdf_present():
        p = HANDBOOK_PDFS[0]
        return checks.file_present(os.path.join(root, p[0]), p[1])

    def items():
        out = [Item("The quote check", command=f"{PY} {CODE}/rules/validate.py", group="The rules against the handbook, mechanically",
                    note="**Every quoted sentence of every rule is looked up on its cited handbook page.** The last line "
                         "reports the rule entries checked, how many quotes were found verbatim, and the failures. "
                         "It takes about a second. Terms, bridges and triggers are checked the same way.")]
        out += [Item(t, p, n, group="How the rules were extracted") for t, p, n in EXTRACTION_FILES]
        out.append(Item("The evaluation results page", RESULTS_PAGE[0], RESULTS_PAGE[1], group="The six evaluation numbers"))
        out += [Item(t, p, n) for t, p, n in NUMBER_FILES]
        out += [
            Item("Number 1 again, from the test cases", command=f"{PY} {CODE}/experiments/number1_report.py",
                 group="Reruns, for a reader who wants to verify",
                 note="Recomputes the encoding-fidelity numbers from the test cases. A few seconds, nothing to download. "
                      "Each rerun writes its output file in place, so afterwards `git status` shows whether anything changed."),
            Item("Numbers 5 and 6, on the real visits", command=f"bash {CODE}/data/download-yale.sh && {PY} {CODE}/data/convert-yale.py "
                                                                 f"&& {PY} {CODE}/experiments/task_g_full.py",
                 note="The Yale emergency-department dataset, about 99 MB, fetched once from its authors' repository and "
                      "converted. Then the rules over all its visits, about four minutes. The learned signal retrains with "
                      "`experiments/task_h_learned_comparator.py`, about five minutes."),
            Item("Numbers 2 and 4, a persona run", command=f"{PY} {CODE}/experiments/task_i_harness.py --help",
                 note="A run plays every persona through the real interview, so it needs the app's language model from "
                      "section 4 and twenty minutes or more. The option list explains the choices."),
        ]
        return out

    return Section(
        id="evidence",
        title="5. The evidence behind the report",
        why=("**Every number in the report comes from a file in this repository, and the file names the script that "
             "made it.**\n\n"
             "Three kinds of evidence are here:\n\n"
             "- the rules checked against the handbook's pages, mechanically, in one command\n"
             "- the record of how the rules were extracted and compared with four blind re-extractions\n"
             "- the six evaluation numbers, each with its output file\n\n"
             "Reading needs nothing beyond section 1. Rerunning is optional and listed last."),
        checks=[
            Check(id="evidence-packages", title="PyMuPDF and jsonschema in .venv",
                  run=lambda: checks.venv_imports(code_dir(root), ["pymupdf", "jsonschema"]),
                  fix="The quote check reads the handbook with PyMuPDF and the rules' schema with jsonschema. "
                      "Both install into `.venv` with the command below.",
                  command=f"{PIP} install -r {CODE}/requirements.txt"),
            Check(id="evidence-pdf", title="The ESI handbook PDF", run=pdf_present,
                  fix="**The quote check needs the handbook.** It is copyrighted, so the script below fetches each person's "
                      "own copy into `SystemCode/sources/`, never committed. Section 3 uses the same file.",
                  command=f"bash {CODE}/sources/download.sh"),
        ],
        items=items,
        done=("**The results page is the place to start.** Each of its six numbers links the output file behind it, "
              "and the files below are the same ones."),
    )
