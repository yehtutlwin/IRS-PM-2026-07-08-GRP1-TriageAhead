## SECTION 1 : PROJECT TITLE
## TriageAhead: ED Triage Pre-Arrival Intake Assistant

A caregiver's chat that starts only after the decision to go to the emergency department, asks what a triage nurse would ask, and hands the nurse a one-page, page-cited summary before the patient is seen.

NUS-ISS Graduate Certificate in Intelligent Reasoning Systems, Practice Module, Group 1 (intake of 8 July 2026).

---

## SECTION 2 : EXECUTIVE SUMMARY / PAPER ABSTRACT

When a patient is driven to an emergency department (ED), the family member in the car usually knows the facts the triage nurse needs most: what happened, the patient's medicines, allergies and conditions. Today nobody collects those facts until the nurse asks for them at the counter. We built a system that collects them during the ride and hands the nurse a one-page summary when the patient arrives.

What the system does. A chat on the caregiver's phone opens only after the decision to go to the ED. It asks the questions a triage nurse would ask, danger signs first, in the caregiver's own language. A rule engine, built from the published Emergency Severity Index (ESI) triage handbook, reads the answers and computes an urgency floor: a statement that the patient is at least this urgent, never that they are less urgent. As soon as the floor is settled, after about a dozen questions, the chat shows a code and a QR link; on arrival the nurse scans it and sees the floor, the rule that produced it with its source page, and the history with who said each fact and when. The hospital's own process does not change; staff can use, ignore or re-confirm any line.

How it is built. The design has one organising rule: the language model translates; the rules decide. A program decides which facts are open and in what order, from an agenda derived from the rules, fields and triggers, and asks the highest-ranked next; the language model groups the top few into one natural question, words it, and turns the answer into typed facts. It never decides what is open or evaluates a rule. The knowledge base comes from three processes, each with its own check: rules are extracted from the handbook with page and quoted sentence; what the interview may ask is derived from the rules by a fixed procedure; the plain meaning and wording of each fact are authored and recorded as decisions. A learned model trained on 446,423 real ED visits from a public record of 558,029 is shown beside the floor as a labelled "practice signal" and never changes it.

---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name | Student ID (MTech Applicable) | Work Items (Who Did What) | Email (Optional) |
| :------------ |:---------------:| :-----| :-----|
| Tai Low Mun (group leader) | A0080322W | Project coordination and progress monitoring · Team meeting facilitation · Caregiver persona development and evaluation testing · Knowledge base and system review · Technical troubleshooting · Project documentation and video narration | |
| Tong Chern Haw | A0362584W | Product review, product testing and evaluation | |
| Wan Jin Quan | A0182631J | 2nd AI model integration and evaluation · structured fact extraction and testing | |
| Ye Htut Lwin | A0362667R | Product concept and positioning · reasoning architecture · knowledge base design · evaluation framing | |

**Use of AI.** An AI coding agent (Claude Code) was used under the team's direction for brainstorming and research, implementation details, automated testing and the drafting of documents; every change was reviewed by a member. The language model inside the system, and the model-drafted rule extraction, are part of the design and are described in the report (Appendix E gives the full account).

---

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

Two videos in the folder `Video`, also submitted as separate files beside this repository in the Canvas zip: `IRS-PM-2026-07-08-GRP1-TriageAhead-promotion.mp4` (business pain and value, use-case demo, pricing; 4:12) and `IRS-PM-2026-07-08-GRP1-TriageAhead-system.mp4` (system design and the technical explanation of the use cases; 5:26).

---

## SECTION 5 : USER GUIDE

`Refer to appendix C, Installation and user guide, in the project report at Github Folder: ProjectReport`, or to `SystemCode/docs/install-and-user-guide.md`.

Everything runs locally on Linux, macOS, or Windows under WSL2, with Python 3.10 or later.

**Guided, all in one.** From the repository folder:

> $ python3 SystemCode/guide/start.py

The setup guide needs only Python 3.10 or later and no package. It opens a page on this machine and shows the same text in the terminal. Section by section it checks what the machine has, shows the one command still needed, waits until that has worked, and then presents what to open: the report and the videos, the rulebook and its review app, the interview app with a free language model (Gemini or Ollama), the recorded sessions from the report and the videos, and the evidence behind the report's numbers. The guide installs and starts nothing itself. Every command is shown for the reader to run, and everything lands in the `SystemCode` folder's own virtual environment.

**By hand**, the same steps:

> $ cd SystemCode
>
> $ python3 -m venv .venv && source .venv/bin/activate
>
> $ pip install -r requirements.txt
>
> $ bash sources/download.sh          # the copyrighted handbook PDF, fetched per person
>
> $ cp .env.example .env              # then edit .env: LLM_BACKEND=ollama for the local model (no key), or a Gemini key
>
> $ bash webapp/run.sh               # the app plus a public https address, so a phone can scan the QR code
>
> **Go to URL using web browser**: the address the script prints (or http://localhost:8090 on the same machine). The caregiver uses the chat; when the report is ready the chat shows a QR code and a ticket link, and the nurse opens the one-page report from either, on any device.

`webapp/run.sh` starts the web app and a Cloudflare quick tunnel (no account or key; a new random address each start), and prints the address with its QR code in the terminal; it needs the `cloudflared` binary once per machine (macOS: `brew install cloudflared`; Debian, Ubuntu and Windows under WSL2: the amd64 `.deb` from https://github.com/cloudflare/cloudflared/releases). Without a tunnel, `python webapp/server.py` runs the same app at http://localhost:8090 for use on one machine. The local backend needs Ollama with `gemma4:12b` pulled; the Gemini and Claude backends need an API key in `.env`. `python -m pytest tests/` runs the test suite.

---

## SECTION 6 : PROJECT REPORT / PAPER

`Refer to project report at Github Folder: ProjectReport`: `IRS-PM-2026-07-08-GRP1-TriageAhead-Group-Report.pdf`, with the proposal as Appendix A, the mapping of system functions to the three courses as Appendix B and the installation and user guide as Appendix C.

---

## SECTION 7 : MISCELLANEOUS

`Refer to Github Folder: Miscellaneous`

- `IRS-PM-2026-07-08-GRP1-TriageAhead-Proposal.pdf`: the project proposal as submitted on 13 September 2026 (also Appendix A of the report).
- `IRS-PM-2026-07-08-GRP1-TriageAhead-Proposal-Slides.pdf`: the slides of the proposal presentation.

The evaluation results page every number in chapter 4 of the report is taken from, with the output file behind each, is `SystemCode/docs/evaluation-results.md`.

---

**This [Machine Reasoning (MR)](https://www.iss.nus.edu.sg/executive-education/course/detail/machine-reasoning "Machine Reasoning") course is part of the Analytics and Intelligent Systems and Graduate Certificate in [Intelligent Reasoning Systems (IRS)](https://www.iss.nus.edu.sg/stackable-certificate-programmes/intelligent-systems "Intelligent Reasoning Systems") series offered by [NUS-ISS](https://www.iss.nus.edu.sg "Institute of Systems Science, National University of Singapore").**
