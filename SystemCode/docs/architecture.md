# System architecture and design

This document states the design of the whole system as submitted. Every part links to its file.

## 1. Purpose and boundaries

The system is a pre-arrival intake assistant for an emergency department. A family member (or the patient) already on the
way answers a chat on their phone; at the counter the nurse scans a code and reads a one-page report. The report gives a
**floor** on the ESI level ("at least ESI-2"), never a level, computed from facts a caregiver can state, by rules taken from
the ESI handbook with their page quoted; a history in the handover order; and one advisory sentence from past practice.

What it does not do, by design: it never assigns a level (the nurse does, with the vital signs the system never has); it never
gives care advice, except one line, to call 995, when a danger sign is reported; it never claims ESI-1, because every
level-1 criterion in the handbook is a clinician's finding; it never reassures. Outside it: the hospital's systems, identity
checks (name and date of birth are "as declared"), and anything after the nurse's assessment.

## 2. The parts

| Part | What it does | Reads | Writes | File |
| --- | --- | --- | --- | --- |
| Chat page | the caregiver's side: questions, the status line while a turn is slow, the "we've arrived" button, the code and QR on a button once the report is ready | the state API | answers to the answer API | [webapp/chat.html](../webapp/chat.html) |
| Web server | one session per ticket: start, answer, arrival, check-in, report, QR; the two stages of the interview; the one permitted advice; the worsening check | the derived agenda, the rules, the bridges | the session file (facts, messages, event log) | [webapp/server.py](../webapp/server.py) |
| Interview control | which facts are open now, in what order, which may be asked together; the pre-arrival stage stops when the floor is settled | [rules/derived/agenda.yaml](../rules/derived/agenda.yaml) (derived from the rules, the field file and the triggers) | the next question's fields | [prototype/engine.py](../prototype/engine.py) (`open_fields`, `pre_arrival_fields`, `cap_yes_no`) |
| Question wording | a language model writes the question for the chosen fields in plain words (dynamic mode: it also chooses which of the top-ranked open fields fit one sentence, at most two yes/no) | the fields' everyday wording and the recent chat | the question text | `pick_and_ask_dynamic` in the server; the static alternative kept for comparison runs |
| Fact extraction | a language model turns the answer into facts: only the fields offered, only the allowed values, a decision for every asked field, a quote per write | the field file: name, type, gloss, options with their definitions | writes to the fact store, through the guard | [prototype/extraction.py](../prototype/extraction.py), [prototype/extract_instructions.txt](../prototype/extract_instructions.txt) |
| The guard | drops a deduced value (stated-only fields), a denial of an item the answer did not address, a write whose quote is not in the answer | the field file, the keywords of each field | nothing: it filters | `extraction.guard`, `engine.field_keywords` |
| Fact store | every fact with its value, status (reported, probable, confirmed, unknown), who said it, the turn and the time; complaints as a list; derived facts added, never removed | | the session's facts | `engine.Facts`, [prototype/cli.py](../prototype/cli.py) |
| Derivation | after every answer: bridges (everyday signs to a clinical fact), age from the date of birth, the age band, a blood thinner from medicine names, absolute times | [rules/bridges.yaml](../rules/bridges.yaml), [rules/terms.yaml](../rules/terms.yaml) | derived facts | `engine.derive` |
| Rule engine | facts in; ESI-1 indicators, the floor, consider flags and context notes out; deterministic | [rules/criteria.yaml](../rules/criteria.yaml) | the evaluation tree | `engine.evaluate_tree` |
| Practice signal | a classifier on pre-arrival facts, trained on past visits; one sentence on the report; never touches the floor | the stored facts | one probability, shown as a band | [prototype/practice_signal.py](../prototype/practice_signal.py), model under `prototype/models/` |
| Report | the nurse's page: danger signs, the floor with rules and pages, flags and notes, the practice signal, the facts with their provenance, what was not collected, an AI summary checked against the facts | the fact store and the tree | HTML and text | `render_html_report` in the server, [prototype/report.py](../prototype/report.py) |
| Review site | one page per rule, bridge, trigger, term and option, history question and practice case, with the cited page rendered and a verdict form | the knowledge files and the handbook PDFs | verdicts in a local database, exported as a log | [review/app.py](../review/app.py), [review/cases.py](../review/cases.py) |
| Evaluation harness | plays a scripted caregiver through the real web interview and scores floors, rules, facts, questions, re-asks, wording; keeps every session and an index of runs | [prototype/personas.yaml](../prototype/personas.yaml) | [experiments/out/RUNS.md](../experiments/out/RUNS.md) and the run reports | [experiments/task_i_harness.py](../experiments/task_i_harness.py) |
| Checks | the validator (every quote on its page, every field defined, bridges, triggers, terms and options consistent) and the derivation that regenerates the index and the agenda | the knowledge files | the derived files; a failure | [rules/validate.py](../rules/validate.py), [rules/derive.py](../rules/derive.py) |

## 3. The two lanes of the report

**The rule lane** comes from the handbook. Each rule is a condition over facts with the page and sentence it comes from; the
engine applies them deterministically; the result is a floor, flags and notes, each with its citation. The same facts give the
same output every time, and every line of it can be checked against the page.

**The learned lane** comes from hospital data: a classifier trained on 446,000 past visits at one site, using only facts a
caregiver can report, which says how similar past visits were triaged ("most were ESI 1 or 2"). It is advisory, it is shown
below the floor, and it writes nothing into the rule engine.

They are kept apart because they answer different questions with different warrant. The handbook says what *should* raise
the level; the data says what *did* at one hospital, including its own under- and over-triage. A learned signal can
corroborate a floor; it must never lower one, and it must never be the floor, because it cannot cite a page and it changes
when the data changes.

## 4. The flow of one session

```mermaid
sequenceDiagram
    autonumber
    actor Caregiver
    participant Chat as Chat page
    participant Server as Web server
    participant Agenda as Interview control<br/>(derived agenda, triggers)
    participant LM as Language model
    participant Store as Fact store<br/>(+ derivation, bridges)
    participant Engine as Rule engine
    participant Nurse

    Caregiver->>Chat: opens the link, confirms "already coming in"
    Chat->>Server: start
    Server->>Agenda: open fields (stage: settle the floor)
    Agenda-->>Server: ranked open fields
    Server->>LM: word a question for the top fields (at most two yes/no)
    LM-->>Chat: question
    loop each answer
        Caregiver->>Chat: answer
        Chat->>Server: answer (status line shows "reading your answer")
        Server->>LM: fact extraction: decision per asked field, quote per write
        LM-->>Server: writes
        Server->>Store: guard, write, derive (bridges, age, blood thinner)
        Store->>Engine: facts
        Engine-->>Server: indicators, floor, flags, notes
        alt a danger sign or an ESI-1 indicator
            Server-->>Chat: the one advice: call 995 now (once)
        end
        Server->>Agenda: open fields
        alt floor settled (at least ESI-2 and the essentials in, or nothing left that could set a level)
            Server-->>Chat: "that's enough for the team": code, QR and link on a header button; questions continue (history, flags, notes)
        end
        Server->>LM: next question
        LM-->>Chat: question
    end
    Caregiver->>Chat: "We've arrived" button
    Chat->>Server: arrived: waiting-room phase, baseline for the worsening check
    loop every 15 minutes while the page is open
        Chat->>Caregiver: "How is the patient doing right now compared to when you arrived?"
        Caregiver->>Server: answer; a worsening is banner on the report and advice to tell the counter
    end
    Nurse->>Server: scans the code: report page (changes nothing in the chat)
    Server-->>Nurse: floor with pages, flags, notes, practice signal, facts with provenance, not collected
```


## 5. Where knowledge and data enter

In one sentence: the handbook and the other documents become the rules, bridges, terms and history questions that the interview and
the engine read; the Yale visit data trains one advisory classifier and supplies the test visits for evaluation; the data
never touches the rules or the interview.

## 6. The knowledge base and extraction design

How the rules, fields, questions, bridges, triggers and terms are kept and produced is described in
[knowledge-base.md](knowledge-base.md): the table of every file, its process (extracted, derived or authored) and its state,
and what each property of a field is for and who reads it.

## 7. Where a language model is used, and where it is not

Used, three places at run time: to word a question (and in dynamic mode to choose which of the top-ranked open facts fit one
sentence), to turn an answer into facts, and to write the report's summary paragraph (which is shown only if every number in
it is in the stored facts). Used once, offline, under constraints and checks, to extract the rules from the handbook.

Not used: choosing the level (the rules do, deterministically); choosing what is open and in what order (the derived agenda and
the triggers do; the model picks only among the top-ranked open facts); deciding when the report is ready (the stage rule);
the danger-sign advice (code); the practice signal (a classifier, not a language model); anything on the review site.

The interview has run on three model backends through one seam ([prototype/llm.py](../prototype/llm.py)): a local model
(gemma4:12b through Ollama), Gemini's free tier, and Claude Opus 5.5; the comparison on the same personas is in
[interview-v2-backends.md](../experiments/out/interview-v2-backends.md).
