# Sheet check: the rule engine on each persona answer sheet (2026-10-19 13:55)

The engine is given the sheet's `truth` facts directly (the anticoagulant as confirmed, the rest as reported) and its floor and fired rules are compared with the author's expectation. Agreement: 25 of 27.

| persona | expected floor | engine floor | expected rules | fired | agree | truth fields with no schema field | kind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1-fall-anticoag | at least ESI-2 | at least ESI-2 | B-30.anticoagulated-trauma | B-30.anticoagulated-trauma | yes | - |  |
| P2-chest-pain | at least ESI-2 | at least ESI-2 | B-04.chest-pain-acs-suspect | B-04.chest-pain-acs-suspect | yes | - |  |
| P4-sore-throat | none | none | - | - | yes | - |  |
| P6-acute-gout | none | none | - | - | yes | complaint.trauma, history.gout |  |
| P7-heat-stroke | ESI-1 | none | synthetic.heat-stroke-altered-mental-status | - | NO | danger_signs.altered_mental_status, complaint.collapse, environment.heat_exposure, measurements.temperature_c | facts with no field (synthetic persona): a schema gap, recorded, not a rule gap |
| P8-decompensated-liver-disease | at least ESI-2 | none | synthetic.liver-disease-confusion | - | NO | danger_signs.altered_mental_status, complaint.hematemesis, complaint.melena, history.cirrhosis, history.hepatitis_b, signs.jaundice, signs.ascites | facts with no field (synthetic persona): a schema gap, recorded, not a rule gap |
| P9-breathing-no-pain | none | none | - | - | yes | - |  |
| P10-infant-fever | at least ESI-2 | at least ESI-2 | B-56.infant-under-28-days-fever | B-56.infant-under-28-days-fever | yes | - |  |
| P12-elderly-confusion-uti | at least ESI-2 | at least ESI-2 | B-01.new-altered-mental-status, B-43.uti-elderly-or-urosepsis-signs | B-01.new-altered-mental-status, B-43.uti-elderly-or-urosepsis-signs | yes | - |  |
| P13-cast-too-tight | at least ESI-2 | at least ESI-2 | B-24.extremity-neurovascular-compromise | B-24.extremity-neurovascular-compromise | yes | - |  |
| P14-child-knee-cut | none | none | - | - | yes | - |  |
| P15-suicidal-thoughts | at least ESI-2 | at least ESI-2 | B-09.suicidal-or-homicidal | B-09.suicidal-or-homicidal | yes | - |  |
| P16-intentional-overdose | at least ESI-2 | at least ESI-2 | B-26.suspected-toxic-ingestion | B-26.suspected-toxic-ingestion | yes | - |  |
| P17-nosebleed-clotting | at least ESI-2 | at least ESI-2 | B-15.high-risk-epistaxis | B-15.high-risk-epistaxis | yes | - |  |
| P18-fall-no-floor | none | none | - | - | yes | - |  |
| P19-headache-no-floor | none | none | - | - | yes | - |  |
| P20-cancer-pain | at least ESI-2 | at least ESI-2 | B-03.severe-pain-systemic-cause | B-03.severe-pain-systemic-cause | yes | - |  |
| P21-child-shunt-not-right | at least ESI-2 | at least ESI-2 | B-29.pediatric-subtle-ams, B-01.new-altered-mental-status | B-01.new-altered-mental-status, B-29.pediatric-subtle-ams | yes | - |  |
| ND-P20-infant-fever | at least ESI-2 | at least ESI-2 | B-57.infant-under-90-days-temperature-over-38 | B-57.infant-under-90-days-temperature-over-38 | yes | - |  |
| ND-P23-elderly-confusion | at least ESI-2 | at least ESI-2 | B-01.new-altered-mental-status | B-01.new-altered-mental-status | yes | - |  |
| ND-P27-resolved-speech-change | at least ESI-2 | at least ESI-2 | B-05.stroke-signs | B-05.stroke-signs | yes | - |  |
| ND-P28-postpartum-bleeding | at least ESI-2 | at least ESI-2 | B-13.postpartum-hemorrhage | B-13.postpartum-hemorrhage | yes | - |  |
| ND-P29-pregnant-headache | at least ESI-2 | at least ESI-2 | B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | yes | - |  |
| CH-I29-03-possible-ectopic | at least ESI-2 | at least ESI-2 | B-06.possible-ectopic-stable | B-06.possible-ectopic-stable, B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache | yes | - |  |
| CH-I29-04-fever-during-chemotherapy | at least ESI-2 | at least ESI-2 | B-07.immunocompromised-fever | B-07.immunocompromised-fever | yes | - |  |
| CH-I29-08-sexual-assault | at least ESI-2 | at least ESI-2 | B-11.sexual-assault | B-11.sexual-assault | yes | - |  |
| CH-I29-09-child-increasing-work-of-breathing | at least ESI-2 | at least ESI-2 | B-12.increasing-respiratory-effort | B-12.increasing-respiratory-effort | yes | - |  |

Notes. The two synthetic personas (heat stroke, liver disease) name rules that do not exist and facts no field holds; they were written to show the schema's edge and are kept as such, so their disagreement is a recorded schema gap, not a rule gap. The breathing persona's sheet states (since 16 Oct 2026) that the breathing is not getting worse, so no floor is expected and none fires.
