# Static slots versus dynamic grouping - persona harness

Same nine personas, same persona player, same rulebook and slot file. *Static*: the fixed slots, one question per slot. *Dynamic*: the program ranks the open fields; the model chooses which of the top-ranked ones to ask together (at most 4, top one always included, a confirmation alone) and writes the question. Re-ask = a question all of whose fields had already been asked.

| configuration | interview model | floors ok | rules ok | facts captured | danger misses | turns / persona | questions / persona | re-asks total | source |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| static-gemma4 | gemma4:12b (ollama) | 7/9 | 7/9 | 45/64 (70%) | 0 | 12.9 | 11.0 | 37 | `task-i-20260926-0335-static-gemma4.md` |
| dynamic-gemma4 | gemma4:12b (ollama) | 7/9 | 7/9 | 46/64 (72%) | 0 | 8.9 | 8.9 | 20 | `task-i-20260926-0343-dynamic-gemma4.md` |
| static-qwen35 | qwen3.5:9b (ollama) | 7/9 | 7/9 | 46/64 (72%) | 0 | 7.1 | 7.1 | 7 | `task-i-20260926-0347-static-qwen35.md` |
| dynamic-qwen35 | qwen3.5:9b (ollama) | 8/9 | 7/9 | 47/64 (73%) | 0 | 7.3 | 7.3 | 6 | `task-i-20260926-0351-dynamic-qwen35.md` |
| static-gemini | Gemini (cloud) | not completed | | | | | | | rate-limited: 30–60 s waits per call on the free tier; the harness timed out on the first persona; partial sessions discarded |
| dynamic-gemini | Gemini (cloud) | not completed | | | | | | | same; not re-run |

**Caveats.** One run per configuration, so small differences (one floor, one fact) are within run-to-run variation; the two hard
personas (heat stroke, decompensated liver disease) miss facts in every configuration because their facts lie outside the schema,
not because of grouping. In the local configurations the persona is played by the same model as the interview, so part of the
Qwen advantage may be a more complete persona; the Gemini configurations, with the persona held at gemma4, were meant to separate
the two and did not complete.

## Per persona, by configuration: the same persona, one session each

Each cell links to the transcript of that session (ticket, floor, facts captured, questions asked, re-asks). Read a row across to compare the same persona under the four configurations; the persona's answers come from a fixed script, so only the questions differ.

| persona | static-gemma4 | dynamic-gemma4 | static-qwen35 | dynamic-qwen35 |
| --- | --- | --- | --- | --- |
| P1-fall-anticoag | [VANDA-4983](sessions-static-gemma4/VANDA-4983.transcript.txt) · floor ok · 9/9 facts · 13 q · 3 re-asks | [LION-9717](sessions-dynamic-gemma4/LION-9717.transcript.txt) · floor ok · 9/9 facts · 10 q · 1 re-asks | [MERLION-1744](sessions-static-qwen35/MERLION-1744.transcript.txt) · floor ok · 9/9 facts · 7 q · 0 re-asks | [DURIAN-7266](sessions-dynamic-qwen35/DURIAN-7266.transcript.txt) · floor ok · 9/9 facts · 6 q · 0 re-asks |
| P2-chest-pain | [SAGA-1965](sessions-static-gemma4/SAGA-1965.transcript.txt) · floor ok · 6/6 facts · 10 q · 3 re-asks | [LION-4434](sessions-dynamic-gemma4/LION-4434.transcript.txt) · floor ok · 6/6 facts · 6 q · 0 re-asks | [CANNA-4298](sessions-static-qwen35/CANNA-4298.transcript.txt) · floor ok · 6/6 facts · 6 q · 1 re-asks | [LION-1485](sessions-dynamic-qwen35/LION-1485.transcript.txt) · floor ok · 6/6 facts · 6 q · 1 re-asks |
| P3-abdo-pregnant | [LION-6744](sessions-static-gemma4/LION-6744.transcript.txt) · floor ok · 5/6 facts · 9 q · 3 re-asks | [TIGER-3130](sessions-dynamic-gemma4/TIGER-3130.transcript.txt) · floor ok · 5/6 facts · 5 q · 0 re-asks | [VANDA-9856](sessions-static-qwen35/VANDA-9856.transcript.txt) · floor ok · 5/6 facts · 7 q · 1 re-asks | [ORCHID-2335](sessions-dynamic-qwen35/ORCHID-2335.transcript.txt) · floor ok · 5/6 facts · 6 q · 0 re-asks |
| P4-sore-throat | [SAGA-9740](sessions-static-gemma4/SAGA-9740.transcript.txt) · floor ok · 4/5 facts · 11 q · 5 re-asks | [DURIAN-3997](sessions-dynamic-gemma4/DURIAN-3997.transcript.txt) · floor ok · 4/5 facts · 7 q · 1 re-asks | [PANDA-1258](sessions-static-qwen35/PANDA-1258.transcript.txt) · floor ok · 5/5 facts · 6 q · 0 re-asks | [EAGLE-8686](sessions-dynamic-qwen35/EAGLE-8686.transcript.txt) · floor ok · 4/5 facts · 6 q · 0 re-asks |
| P5-fever-chemo | [OTTER-1721](sessions-static-gemma4/OTTER-1721.transcript.txt) · floor ok · 4/5 facts · 10 q · 4 re-asks | [EAGLE-6170](sessions-dynamic-gemma4/EAGLE-6170.transcript.txt) · floor ok · 4/5 facts · 8 q · 2 re-asks | [RAFFLES-2005](sessions-static-qwen35/RAFFLES-2005.transcript.txt) · floor ok · 4/5 facts · 8 q · 2 re-asks | [LOTUS-8528](sessions-dynamic-qwen35/LOTUS-8528.transcript.txt) · floor ok · 5/5 facts · 7 q · 0 re-asks |
| P6-acute-gout | [TIGER-8025](sessions-static-gemma4/TIGER-8025.transcript.txt) · floor ok · 5/7 facts · 11 q · 4 re-asks | [HERON-5776](sessions-dynamic-gemma4/HERON-5776.transcript.txt) · floor ok · 5/7 facts · 12 q · 5 re-asks | [TIGER-9009](sessions-static-qwen35/TIGER-9009.transcript.txt) · floor ok · 5/7 facts · 9 q · 1 re-asks | [ORCHID-4119](sessions-dynamic-qwen35/ORCHID-4119.transcript.txt) · floor ok · 5/7 facts · 10 q · 2 re-asks |
| P6-stroke-resolved | [EAGLE-6708](sessions-static-gemma4/EAGLE-6708.transcript.txt) · floor ok · 6/6 facts · 12 q · 5 re-asks | [RAFFLES-7907](sessions-dynamic-gemma4/RAFFLES-7907.transcript.txt) · floor ok · 6/6 facts · 11 q · 4 re-asks | [DURIAN-6969](sessions-static-qwen35/DURIAN-6969.transcript.txt) · floor ok · 6/6 facts · 7 q · 1 re-asks | [OTTER-3378](sessions-dynamic-qwen35/OTTER-3378.transcript.txt) · floor ok · 6/6 facts · 10 q · 1 re-asks |
| P7-heat-stroke | [MERLION-2587](sessions-static-gemma4/MERLION-2587.transcript.txt) · FLOOR at least ESI-2 · 1/8 facts · 11 q · 4 re-asks | [TIGER-9198](sessions-dynamic-gemma4/TIGER-9198.transcript.txt) · FLOOR at least ESI-2 · 2/8 facts · 12 q · 4 re-asks | [VANDA-4476](sessions-static-qwen35/VANDA-4476.transcript.txt) · FLOOR at least ESI-2 · 1/8 facts · 8 q · 1 re-asks | [RAFFLES-2025](sessions-dynamic-qwen35/RAFFLES-2025.transcript.txt) · FLOOR at least ESI-2 · 2/8 facts · 7 q · 0 re-asks |
| P8-decompensated-liver-disease | [MERLION-8840](sessions-static-gemma4/MERLION-8840.transcript.txt) · FLOOR None · 5/12 facts · 12 q · 6 re-asks | [TIGER-7307](sessions-dynamic-gemma4/TIGER-7307.transcript.txt) · FLOOR None · 5/12 facts · 9 q · 3 re-asks | [DURIAN-3466](sessions-static-qwen35/DURIAN-3466.transcript.txt) · FLOOR None · 5/12 facts · 6 q · 0 re-asks | [VANDA-8749](sessions-dynamic-qwen35/VANDA-8749.transcript.txt) · floor ok · 5/12 facts · 8 q · 2 re-asks |

## Misses by field (all configurations)

| field | static-gemma4 | dynamic-gemma4 | static-qwen35 | dynamic-qwen35 |
| --- | ---: | ---: | ---: | ---: |
| red_flags.altered_mental_status | 2 | 2 | 2 | 2 |
| infection.fever | 2 | 2 | 1 | 2 |
| complaint.vaginal_bleeding | 1 | 1 | 1 | 1 |
| complaint.trauma | 1 | 1 | 1 | 1 |
| history.gout | 1 | 1 | 1 | 1 |
| complaint.collapse | 1 | 1 | 1 | 1 |
| complaint.vomiting | 1 | 1 | 1 | 1 |
| environment.heat_exposure | 1 | 1 | 1 | 1 |
| measurements.temperature_c | 1 | 1 | 1 | 1 |
| complaint.hematemesis | 1 | 1 | 1 | 1 |
| complaint.melena | 1 | 1 | 1 | 1 |
| history.cirrhosis | 1 | 1 | 1 | 1 |
| history.hepatitis_b | 1 | 1 | 1 | 1 |
| signs.jaundice | 1 | 1 | 1 | 1 |
| signs.ascites | 1 | 1 | 1 | 1 |
| complaint.pain_rating | 1 | 1 | 1 |  |
| red_flags.responsive | 1 |  | 1 |  |
