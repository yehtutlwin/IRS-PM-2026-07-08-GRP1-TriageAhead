# Task I - persona runs through the real interview (20260926-0347)

Interview: mode static, backend ollama (qwen3.5:9b). Persona played by ollama (qwen3.5:9b). 9 personas x 1 run(s). Tag: static-qwen35

Floors 7/9 · expected rules 7/9 · extraction 46/64 (72%) · danger-sign misses 0 · questions 64 · re-asks 7

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | re-asks | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag | 1 | at least ESI-2 | yes | yes | 9/9 | 7 | 7 | 0 |  |
| P2-chest-pain | 1 | at least ESI-2 | yes | yes | 6/6 | 6 | 6 | 1 |  |
| P3-abdo-pregnant | 1 | at least ESI-2 | yes | yes | 5/6 | 7 | 7 | 1 | complaint.vaginal_bleeding: want=False got=None |
| P4-sore-throat | 1 | - | yes | yes | 5/5 | 6 | 6 | 0 |  |
| P6-stroke-resolved | 1 | at least ESI-2 | yes | yes | 6/6 | 7 | 7 | 1 |  |
| P5-fever-chemo | 1 | at least ESI-2 | yes | yes | 4/5 | 8 | 8 | 2 | complaint.pain_rating: want=0 got=None |
| P6-acute-gout | 1 | - | yes | yes | 5/7 | 9 | 9 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke | 1 | at least ESI-2 | NO | NO | 1/8 | 8 | 8 | 1 | red_flags.responsive: want=True got=False; red_flags.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting: want |
| P8-decompensated-liver-disease | 1 | - | NO | NO | 5/12 | 6 | 6 | 0 | red_flags.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: want= |
