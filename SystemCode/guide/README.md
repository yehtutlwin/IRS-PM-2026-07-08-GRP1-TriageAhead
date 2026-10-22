# Setup guide: the program that checks what a machine has and says what to install next

For someone who has just cloned the submission repository and wants to see what was delivered: the report
and videos, the rulebook and its review app, the interview web app, the evaluation.

```bash
python3 SystemCode/guide/start.py
```

It runs on the system Python with the standard library only, so it works before anything is installed.
It opens a web page on this machine (the first free port from 9095) and shows the same text in the
terminal. Section by section it checks what is in place, names the first thing missing, shows the one
command to type when the command is straightforward, and re-checks every two seconds until it passes.
It never installs, writes or starts anything itself.

| file | what |
| --- | --- |
| `start.py` | entry: the Python-version and platform check, then the two views |
| `lib/steps.py` | the content: every section, check, command and sentence; the one place that knows the repository's layout (the documents at the top level, the code and the virtual environment in `SystemCode`) |
| `lib/checks.py` | the read-only checks (a tool on the path, a file present, an import inside `.venv`, a port answering) |
| `lib/state.py` | the state both views share and the actions (continue, skip, back, re-check) |
| `lib/cli.py`, `lib/web.py` | the terminal view and the web page |
| `lib/files.py` | serves the repository's files to the page: PDFs and videos as they are, Markdown and YAML through small readers (Markdown drawn by the guide; YAML by js-yaml and json-formatter-js from a CDN) |

Sections: 1 (Python and the packages), 2 (the documents), 3 (the rulebook and its review), 4 (the interview app, with Gemini or Ollama), 5 (the evidence behind the report: the quote check, the extraction record, the six evaluation numbers).
