#!/usr/bin/env python3
"""Setup guide: checks what this machine has, says what to install next, and waits.

    python3 SystemCode/guide/start.py

Runs on the system Python with the standard library only, so it works before anything
is installed. It never installs, writes or starts anything itself: it tells, waits, and
verifies. The same text is shown in this terminal and on a web page (the address is
printed below); either place can move the guide on.
"""
import os
import sys

if sys.version_info < (3, 10):
    print(f"This guide needs Python 3.10 or newer; this is Python {sys.version.split()[0]}.")
    print("Install a newer Python (python.org, or your package manager) and run the guide with it:")
    print("    python3.12 guide/start.py")
    sys.exit(1)

if sys.platform == "win32":
    print("The project's scripts need a Unix shell. On Windows, run everything inside WSL2 (Ubuntu):")
    print("    PowerShell as administrator:  wsl --install -d Ubuntu")
    print("then open the Ubuntu app, clone the repository into your Linux home folder and run")
    print("    python3 SystemCode/guide/start.py")
    print("there. See SystemCode/docs/platform-setup.md for the full steps.")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))          # SystemCode/guide
ROOT = os.path.dirname(os.path.dirname(HERE))              # the repository: README, ProjectReport, SystemCode, ...
sys.path.insert(0, HERE)

from lib import cli, state, steps, web  # noqa: E402


def main():
    st = state.State(steps.sections(ROOT), root=ROOT)
    st.start_checking()
    try:
        url = web.serve(st)
    except OSError as e:
        url = None
        print(f"(no web page: {e}; the terminal view works on its own)")
    try:
        cli.run(st, url)
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")


if __name__ == "__main__":
    main()
