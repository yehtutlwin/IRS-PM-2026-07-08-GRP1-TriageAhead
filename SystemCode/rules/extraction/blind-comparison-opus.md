# Blind re-extraction (opus) compared with the current rules file

Blind re-extraction: 415 entries ({'usage': 51, 'definition': 102, 'rule': 241, 'example': 15, 'negative': 6}), 129 facts. Current: 109 entries, 92 firing rules, supported by 137 statements of the complete reading pass.
Matching: same printed page and overlapping quote (longest common run of words at least 60% of the shorter quote).

| Outcome | Count |
| --- | ---: |
| blind entries that match one of our statements | 169 of 415 |
| rule pairs compared | 217 |
| of which the comparable parts agree | 100 |
| of which something differs | 117 |
| blind entries with no statement of ours (only in the blind re-extraction) | 246 (of which rules: 117) |
| our statements with no blind entry (only in ours) | 17 |
| our firing rules reached by no blind rule | 12 |
| one rule of ours matched by several blind rules | 41 |
| one blind rule matching several of ours | 30 |

## Same sentence, something differs

| ours | blind | page | what differs | our facts | blind facts |
| --- | --- | ---: | --- | --- | --- |
| B-02.severe-pain-consider | B-008 | 6 | effect assign_level_2 vs consider_level_2; numbers [] vs [7.0] | complaint.pain_rating | has_severe_pain |
| B-35.severe-psychological-distress-consider | B-008 | 6 | effect assign_level_2 vs consider_level_2 | complaint.severe_psychological_distress | has_severe_pain |
| B-02.severe-pain-consider | B-009 | 6 | effect assign_level_2 vs consider_level_2; numbers [] vs [7.0] | complaint.pain_rating | has_severe_distress |
| B-35.severe-psychological-distress-consider | B-009 | 6 | effect assign_level_2 vs consider_level_2 | complaint.severe_psychological_distress | has_severe_distress |
| D-01.adult-danger-zone | D-018 | 6 | facts 1 vs 4; numbers [92.0] vs [18.0, 20.0, 92.0, 100.0]; joined differently (all/any) | patient.age, vitals.heart_rate, vitals.respiratory_rate, vitals.spo2 | spo2_percent |
| A-01.unresponsive | A-005 | 6 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_intubated |
| A-16.profound-hypotension | A-005 | 6 | who can supply observed vs vitals | vitals.profound_hypotension | is_intubated |
| A-11.hypoglycemia | A-005 | 6 | who can supply observed vs vitals | vitals.profound_hypoglycemia | is_intubated |
| A-01.unresponsive | A-006 | 6 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_unresponsive |
| A-16.profound-hypotension | A-006 | 6 | who can supply observed vs vitals | vitals.profound_hypotension | is_unresponsive |
| A-11.hypoglycemia | A-006 | 6 | who can supply observed vs vitals | vitals.profound_hypoglycemia | is_unresponsive |
| A-01.unresponsive | A-007 | 6 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_pulseless |
| A-16.profound-hypotension | A-007 | 6 | who can supply observed vs vitals | vitals.profound_hypotension | is_pulseless |
| A-11.hypoglycemia | A-007 | 6 | who can supply observed vs vitals | vitals.profound_hypoglycemia | is_pulseless |
| A-01.unresponsive | A-008 | 6 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_apneic |
| A-16.profound-hypotension | A-008 | 6 | who can supply observed vs vitals | vitals.profound_hypotension | is_apneic |
| A-11.hypoglycemia | A-008 | 6 | who can supply observed vs vitals | vitals.profound_hypoglycemia | is_apneic |
| A-01.unresponsive | A-009 | 6 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | respiratory_distress_severity |
| A-16.profound-hypotension | A-009 | 6 | who can supply observed vs vitals | vitals.profound_hypotension | respiratory_distress_severity |
| A-11.hypoglycemia | A-009 | 6 | who can supply observed vs vitals | vitals.profound_hypoglycemia | respiratory_distress_severity |
| A-15.intubated | A-010 | 6 | who can supply vitals vs observed | obs.intubated | is_profoundly_hypotensive |
| A-01.unresponsive | A-010 | 6 | who can supply vitals vs observed; facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_profoundly_hypotensive |
| A-04.pulseless | A-010 | 6 | who can supply vitals vs observed | obs.pulseless | is_profoundly_hypotensive |
| A-03.apneic | A-010 | 6 | who can supply vitals vs observed | obs.apneic | is_profoundly_hypotensive |
| A-05.severe-respiratory-distress | A-010 | 6 | who can supply vitals vs observed | obs.severe_respiratory_distress | is_profoundly_hypotensive |
| A-15.intubated | A-011 | 6 | who can supply vitals vs observed | obs.intubated | has_hypoglycemia |
| A-01.unresponsive | A-011 | 6 | who can supply vitals vs observed; facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_hypoglycemia |
| A-04.pulseless | A-011 | 6 | who can supply vitals vs observed | obs.pulseless | has_hypoglycemia |
| A-03.apneic | A-011 | 6 | who can supply vitals vs observed | obs.apneic | has_hypoglycemia |
| A-05.severe-respiratory-distress | A-011 | 6 | who can supply vitals vs observed | obs.severe_respiratory_distress | has_hypoglycemia |
| D-01.adult-danger-zone | D-019 | 6 | facts 1 vs 4; numbers [] vs [18.0, 20.0, 92.0, 100.0]; joined differently (all/any) | patient.age, vitals.heart_rate, vitals.respiratory_rate, vitals.spo2 | vital_sign_outside_normal_for_patient |
| D-02.pediatric-danger-zone-under-1-month | D-019 | 6 | facts 1 vs 3; numbers [] vs [1.0, 60.0, 190.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| D-06.pediatric-danger-zone-1-to-12-months | D-019 | 6 | facts 1 vs 3; numbers [] vs [1.0, 12.0, 55.0, 180.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| D-07.pediatric-danger-zone-1-to-3-years | D-019 | 6 | facts 1 vs 3; numbers [] vs [12.0, 36.0, 40.0, 140.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| D-08.pediatric-danger-zone-3-to-5-years | D-019 | 6 | facts 1 vs 3; numbers [] vs [35.0, 36.0, 60.0, 120.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| D-09.pediatric-danger-zone-5-to-12-years | D-019 | 6 | facts 1 vs 3; numbers [] vs [30.0, 60.0, 120.0, 144.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| D-10.pediatric-danger-zone-12-to-18-years | D-019 | 6 | facts 1 vs 3; numbers [] vs [20.0, 100.0, 144.0, 216.0]; joined differently (all/any) | patient.age_months, vitals.heart_rate, vitals.respiratory_rate | vital_sign_outside_normal_for_patient |
| B-56.infant-under-28-days-fever | D-020 | 6 | decision point D vs B; who can supply vitals vs reported; numbers [1.0, 28.0, 38.0] vs [28.0] | complaint.fever, patient.age_days | age_days, temperature_celsius |
| B-57.infant-under-90-days-temperature-over-38 | D-020 | 6 | decision point D vs B; numbers [1.0, 28.0, 38.0] vs [38.0, 90.0] | patient.age_days, vitals.temp_c | age_days, temperature_celsius |
| B-58.infant-1-to-3-months-fever-consider | D-021 | 6 | decision point D vs B | patient.age_months, vitals.temp_c | age_months, temperature_celsius |
| A-01.unresponsive | A-014 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_unresponsive |
| A-01.unresponsive | A-015 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_active_seizure |
| A-01.unresponsive | A-016 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_occluded_airway |
| A-01.unresponsive | A-017 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_impaired_gas_exchange |
| A-01.unresponsive | A-018 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_ineffective_perfusion |
| A-01.unresponsive | A-022 | 9 | facts 1 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | has_impaired_gas_exchange |
| A-01.unresponsive | A-024 | 9 | facts 2 vs 3; joined differently (all/any) | obs.avpu, obs.nonverbal_acute, obs.not_following_commands | is_obtunded, is_unresponsive |
| A-13.flaccid-infant | A-032 | 9 | numbers [12.0] vs [] | obs.flaccid, patient.age_group | age_months, is_flaccid |
| A-14.penetrating-trauma-unstable | A-036 | 9 | facts 2 vs 3 | E.body_region, E.mechanism, obs.requires_lifesaving_intervention | has_penetrating_trauma_head_neck_chest_abdomen, needs_immediate_lifesaving_intervention |
| B-04.chest-pain-acs-suspect | B-027 | 12 | who can supply observed vs reported; facts 3 vs 2 | complaint.acs_suspicion, complaint.category | chest_pain_suspicious_for_acs, has_chest_pain, needs_immediate_lifesaving_intervention |
| B-05.stroke-signs | B-028 | 12 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.stroke_signs | has_signs_of_stroke, needs_immediate_lifesaving_intervention |
| B-06.possible-ectopic-stable | B-029 | 12 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.possible_ectopic_pregnancy | is_hemodynamically_stable, possible_ectopic_pregnancy |
| B-08.transplant-fever-or-infection | B-031 | 12 | facts 2 vs 4; joined differently (all/any) | complaint.fever, complaint.infection_signs, complaint.transplant_rejection_signs, history.transplant_recipient_or_listed | has_fever, is_transplant_recipient |
| B-08.transplant-fever-or-infection | B-032 | 12 | who can supply observed vs reported; facts 2 vs 4; joined differently (all/any) | complaint.fever, complaint.infection_signs, complaint.transplant_rejection_signs, history.transplant_recipient_or_listed | has_signs_of_infection, is_transplant_recipient |
| B-10.needle-stick-hcw | B-035 | 12 | facts 2 vs 1; joined differently (all/any) | complaint.needle_stick_healthcare_worker | has_needle_stick_injury, is_health_care_worker |
| B-12.increasing-respiratory-effort | B-037 | 12 | who can supply observed vs reported | complaint.increasing_respiratory_effort | has_increasing_respiratory_effort |
| B-13.postpartum-hemorrhage | B-038 | 12 | facts 2 vs 1; joined differently (all/any) | complaint.postpartum_hemorrhage | has_heavy_vaginal_bleeding, is_postpartum |
| B-01.new-altered-mental-status | B-042 | 12 | who can supply observed vs reported; facts 2 vs 3; joined differently (all/any) | history.baseline_mental_status, obs.confusion_lethargy_disorientation, obs.new_confusion_lethargy_disorientation | baseline_mental_status_unknown, is_confused_lethargic_or_disoriented |
| B-03.severe-pain-systemic-cause | B-046 | 12 | numbers [] vs [7.0] | complaint.pain_cause_class, complaint.pain_rating | has_severe_pain, pain_from_systemic_disruption |
| B-03.severe-pain-systemic-cause | B-047 | 12 | numbers [] vs [7.0] | complaint.pain_cause_class, complaint.pain_rating | has_severe_distress, pain_from_systemic_disruption |
| B-11.sexual-assault | B-049 | 12 | facts 2 vs 1; joined differently (all/any) | complaint.sexual_assault | is_distraught, is_sexual_assault_survivor |
| B-35.severe-psychological-distress-consider | B-053 | 12 | effect assign_level_2 vs consider_level_2 | complaint.severe_psychological_distress | is_survivor_of_domestic_violence |
| B-33.headache-with-neck-pain-or-nuchal-rigidity | B-059 | 12 | facts 2 vs 3; joined differently (all/any) | complaint.category, complaint.neck_pain, obs.nuchal_rigidity | has_headache, has_neck_pain |
| B-33.headache-with-neck-pain-or-nuchal-rigidity | B-060 | 12 | who can supply observed vs reported; facts 2 vs 3; joined differently (all/any) | complaint.category, complaint.neck_pain, obs.nuchal_rigidity | has_headache, has_nuchal_rigidity |
| B-05.stroke-signs | B-065 | 12 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.stroke_signs | has_headache, has_signs_of_stroke |
| B-31.post-ictal | B-066 | 12 | who can supply observed vs reported | complaint.post_ictal_after_seizure | is_post_ictal |
| B-29.pediatric-subtle-ams | B-069 | 13 | effect consider_level_2 vs assign_level_2; who can supply observed vs reported | obs.subtle_mental_status_change, patient.age | age_years, has_subtle_mental_status_change |
| B-14.stridor-or-secretions | B-072 | 13 | facts 1 vs 2; joined differently (all/any) | obs.cannot_manage_secretions, obs.stridor | unable_to_manage_secretions |
| B-14.stridor-or-secretions | B-073 | 13 | facts 1 vs 2; joined differently (all/any) | obs.cannot_manage_secretions, obs.stridor | has_stridor |
| B-15.high-risk-epistaxis | B-074 | 13 | who can supply observed vs reported; facts 2 vs 4; joined differently (all/any) | M.anticoagulant, complaint.brisk_or_posterior_bleeding, complaint.category, history.thrombocytopenia_or_clotting_disorder | has_brisk_nosebleed, is_posterior_nosebleed |
| B-15.high-risk-epistaxis | B-075 | 13 | facts 2 vs 4; joined differently (all/any) | M.anticoagulant, complaint.brisk_or_posterior_bleeding, complaint.category, history.thrombocytopenia_or_clotting_disorder | has_brisk_nosebleed, has_thrombocytopenia |
| B-15.high-risk-epistaxis | B-076 | 13 | facts 2 vs 4; joined differently (all/any) | M.anticoagulant, complaint.brisk_or_posterior_bleeding, complaint.category, history.thrombocytopenia_or_clotting_disorder | has_brisk_nosebleed, has_clotting_disorder |
| B-15.high-risk-epistaxis | B-077 | 13 | facts 2 vs 4; joined differently (all/any) | M.anticoagulant, complaint.brisk_or_posterior_bleeding, complaint.category, history.thrombocytopenia_or_clotting_disorder | has_brisk_nosebleed, takes_anticoagulant |
| B-54.respiratory-distress-signs-consider | B-081 | 13 | who can supply vitals vs reported | complaint.respiratory_distress_signs | respiratory_distress_severity |
| A-05.severe-respiratory-distress | A-045 | 13 | facts 2 vs 1; joined differently (all/any) | obs.severe_respiratory_distress | needs_immediate_lifesaving_intervention, respiratory_distress_severity |
| A-17.chest-pain-unstable-lifesaving | A-046 | 13 | facts 2 vs 3 | complaint.category, obs.hemodynamically_unstable, obs.requires_lifesaving_intervention | has_chest_pain, needs_immediate_lifesaving_intervention |
| B-17.abdo-pain-pregnant-or-postpartum | B-084 | 14 | effect consider_level_2 vs assign_level_2; facts 3 vs 2; joined differently (all/any) | complaint.category, history.pregnant_or_postpartum | has_abdominal_pain, is_postpartum, is_pregnant |
| B-18.abdo-pain-sepsis-or-hypoperfusion | B-085 | 14 | effect consider_level_2 vs assign_level_2; facts 2 vs 3; joined differently (all/any) | complaint.category, obs.hypoperfusion_signs, obs.sepsis_signs | has_abdominal_pain, has_signs_of_sepsis |
| B-18.abdo-pain-sepsis-or-hypoperfusion | B-086 | 14 | effect consider_level_2 vs assign_level_2; facts 2 vs 3; joined differently (all/any) | complaint.category, obs.hypoperfusion_signs, obs.sepsis_signs | has_abdominal_pain, has_signs_of_hypoperfusion |
| B-19.abdo-pain-trauma | B-087 | 14 | effect consider_level_2 vs assign_level_2 | E.abdominal_trauma, complaint.category | has_abdominal_pain, has_abdominal_trauma |
| B-20.abdo-pain-refractory-constant-maximal | B-088 | 14 | effect consider_level_2 vs assign_level_2 | complaint.category, complaint.pain_refractory_constant_or_maximal_onset | abdominal_pain_refractory_constant_or_maximal_at_onset, has_abdominal_pain |
| B-21.abdo-pain-vaginal-bleeding | B-092 | 14 | effect consider_level_2 vs assign_level_2 | complaint.category, complaint.vaginal_bleeding | has_abdominal_pain, has_vaginal_bleeding |
| B-37.pregnant-postpartum-sbp-out-of-range | B-094 | 14 | facts 3 vs 2; numbers [90.0] vs [90.0, 150.0] | history.pregnant_or_postpartum, vitals.sbp | is_postpartum, is_pregnant, systolic_bp_mmhg |
| B-37.pregnant-postpartum-sbp-out-of-range | B-095 | 14 | facts 3 vs 2; numbers [150.0] vs [90.0, 150.0] | history.pregnant_or_postpartum, vitals.sbp | is_postpartum, is_pregnant, systolic_bp_mmhg |
| B-13.postpartum-hemorrhage | B-102 | 14 | facts 2 vs 1; joined differently (all/any) | complaint.postpartum_hemorrhage | has_heavy_vaginal_bleeding, is_postpartum |
| A-18.pregnancy-hemodynamic-instability-lifesaving | A-047 | 14 | facts 4 vs 3; joined differently (all/any) | history.pregnant_or_postpartum, obs.hemodynamically_unstable, obs.requires_lifesaving_intervention | is_hemodynamically_stable, is_postpartum, is_pregnant, needs_immediate_lifesaving_intervention |
| B-43.uti-elderly-or-urosepsis-signs | B-105 | 14 | facts 2 vs 4; numbers [] vs [65.0]; joined differently (all/any) | complaint.back_pain, complaint.chills_or_rigors, complaint.uti_symptoms, patient.age | has_uti_symptoms, is_elderly |
| B-43.uti-elderly-or-urosepsis-signs | B-106 | 14 | numbers [] vs [65.0]; joined differently (all/any) | complaint.back_pain, complaint.chills_or_rigors, complaint.uti_symptoms, patient.age | has_back_pain, has_chills, has_rigors, has_uti_symptoms |
| B-44.vehicle-ejection | B-108 | 15 | numbers [6.0] vs [] | E.vehicle_ejection | fall_height_meters |
| B-45.mechanical-extrication | B-108 | 15 | numbers [6.0] vs [] | E.mechanical_extrication | fall_height_meters |
| B-11.sexual-assault | B-108 | 15 | numbers [6.0] vs [] | complaint.sexual_assault | fall_height_meters |
| B-22.fall-from-6-metres-or-more | B-109 | 15 | numbers [] vs [6.0] | E.fall_height_meters | ejected_from_vehicle |
| B-22.fall-from-6-metres-or-more | B-110 | 15 | numbers [] vs [6.0] | E.fall_height_meters | required_mechanical_extrication |
| B-22.fall-from-6-metres-or-more | B-111 | 15 | numbers [] vs [6.0] | E.fall_height_meters | is_sexual_assault_survivor |
| B-23.penetrating-trauma-stable | B-112 | 15 | effect consider_level_2 vs assign_level_2; who can supply observed vs reported; facts 2 vs 3 | E.body_region, E.mechanism, obs.hemodynamically_unstable | has_penetrating_trauma_head_neck_chest_abdomen, is_hemodynamically_stable |
| B-24.extremity-neurovascular-compromise | B-113 | 15 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.extremity_neurovascular_compromise | has_extremity_injury, has_neurovascular_compromise |
| B-46.compartment-syndrome-symptoms | B-113 | 15 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.compartment_syndrome_symptoms | has_extremity_injury, has_neurovascular_compromise |
| B-47.partial-or-complete-amputation | B-113 | 15 | who can supply observed vs reported; facts 2 vs 1; joined differently (all/any) | complaint.amputation_partial_or_complete | has_extremity_injury, has_neurovascular_compromise |
| B-24.extremity-neurovascular-compromise | B-114 | 15 | who can supply observed vs reported | complaint.extremity_neurovascular_compromise | has_symptoms_of_compartment_syndrome |
| B-46.compartment-syndrome-symptoms | B-114 | 15 | who can supply observed vs reported | complaint.compartment_syndrome_symptoms | has_symptoms_of_compartment_syndrome |
| B-47.partial-or-complete-amputation | B-114 | 15 | who can supply observed vs reported | complaint.amputation_partial_or_complete | has_symptoms_of_compartment_syndrome |
| B-25.pelvis-femur-fracture-consider | B-116 | 15 | who can supply observed vs reported | complaint.possible_pelvis_femur_fracture_or_dislocation | possible_pelvic_fracture |
| B-25.pelvis-femur-fracture-consider | B-117 | 15 | who can supply observed vs reported | complaint.possible_pelvis_femur_fracture_or_dislocation | possible_femur_fracture |
| B-25.pelvis-femur-fracture-consider | B-118 | 15 | who can supply observed vs reported | complaint.possible_pelvis_femur_fracture_or_dislocation | has_dislocation |
| B-48.unexplained-changes-possible-ingestion-consider | B-119 | 15 | effect assign_level_2 vs consider_level_2; who can supply reported vs observed | obs.unexplained_ams_breathing_or_rhythm_change | toxic_ingestion |
| B-08.transplant-fever-or-infection | B-121 | 15 | facts 2 vs 4; joined differently (all/any) | complaint.fever, complaint.infection_signs, complaint.transplant_rejection_signs, history.transplant_recipient_or_listed | has_fever, is_transplant_recipient |
| B-08.transplant-fever-or-infection | B-122 | 15 | who can supply observed vs reported; facts 2 vs 4; joined differently (all/any) | complaint.fever, complaint.infection_signs, complaint.transplant_rejection_signs, history.transplant_recipient_or_listed | has_signs_of_infection, is_transplant_recipient |
| B-08.transplant-fever-or-infection | B-123 | 15 | who can supply observed vs reported; facts 2 vs 4; joined differently (all/any) | complaint.fever, complaint.infection_signs, complaint.transplant_rejection_signs, history.transplant_recipient_or_listed | has_signs_of_transplant_rejection, is_transplant_recipient |
| B-09.suicidal-or-homicidal | B-130 | 15 | who can supply observed vs reported | complaint.danger_to_self_or_others | is_psychotic |
| B-51.psychotic-or-violent | B-130 | 15 | who can supply observed vs reported | complaint.psychotic_or_violent | is_psychotic |
| B-56.infant-under-28-days-fever | D-052 | 23 | decision point D vs B | complaint.fever, patient.age_days | age_days, has_fever |
| B-57.infant-under-90-days-temperature-over-38 | D-061 | 24 | decision point D vs B | patient.age_days, vitals.temp_c | age_days, temperature_celsius |
| B-60.child-hypothermia-under-36-consider | D-062 | 24 | decision point D vs B | patient.age, vitals.temp_c | age_years, temperature_celsius |
| B-61.child-over-3-months-temperature-red-flag-consider | D-065 | 24 | decision point D vs B; numbers [3.0, 18.0, 38.5] vs [3.0, 18.0, 36.0, 38.5]; joined differently (all/any) | patient.age, patient.age_months, vitals.temp_c | age_months, age_years, temperature_celsius |
| B-61.child-over-3-months-temperature-red-flag-consider | D-066 | 24 | decision point D vs B; numbers [3.0, 18.0, 36.0] vs [3.0, 18.0, 36.0, 38.5]; joined differently (all/any) | patient.age, patient.age_months, vitals.temp_c | age_months, age_years, temperature_celsius |
| D-01.adult-danger-zone | D-073 | 25 | facts 1 vs 4; numbers [] vs [18.0, 20.0, 92.0, 100.0]; joined differently (all/any) | patient.age, vitals.heart_rate, vitals.respiratory_rate, vitals.spo2 | high_risk_vital_sign_exceeded |
| D-01.adult-danger-zone | D-074 | 25 | effect assign_level_2 vs reassess_uptriage; facts 3 vs 4; numbers [] vs [18.0, 20.0, 92.0, 100.0]; joined differently (all/any) | patient.age, vitals.heart_rate, vitals.respiratory_rate, vitals.spo2 | current_esi_level, high_risk_vital_sign_exceeded, vitals_remain_out_of_range_on_reassessment |

## Only in the blind re-extraction

| blind | page | kind | effect | quote |
| --- | ---: | --- | --- | --- |
| C-001 | 1 | definition | resource_band | For patients determined to be stable, prediction of resources necessary to move the patient to a final disposition |
| N-002 | 2 | usage | none | While patient throughput and flow is outside the scope of ESI |
| N-004 | 5 | usage | none | The ESI is intended for use by nurses with both emergency nursing and triage experience. |
| C-002 | 5 | usage | resource_band | If a patient does not meet high risk instability criteria (ESI level 1 or 2), the triage nurse then evaluates expected resource needs |
| B-001 | 5 | rule | assign_level_2 | Decision point B is used to determine whether the patient is likely to deteriorate and/or require more immediate care |
| C-003 | 5 | usage | resource_band | Decision point C is used only after level 1 and 2 are excluded and patients are determined to be physiologically stable |
| C-004 | 5 | definition | resource_band | ESI levels 3, 4, and 5 are based on how many resources the nurse anticipates will be used to reach a disposition decision. |
| D-001 | 5 | definition | reassess_uptriage | Decision point D incorporates vital signs to identify more subtle high- risk presentations |
| D-002 | 5 | definition | reassess_uptriage | Do the patient’s vital signs warrant a reassessment of the acuity level? |
| B-002 | 5 | rule | assign_level_2 | High risk-confused/distress? |
| B-003 | 5 | rule | assign_level_2 | High risk-confused/distress? |
| B-004 | 5 | rule | assign_level_2 | High risk-confused/distress? |
| B-005 | 5 | rule | assign_level_2 | High risk-confused/distress? |
| C-005 | 5 | rule | resource_band | None One Many |
| C-006 | 5 | rule | resource_band | None One Many |
| C-007 | 5 | rule | resource_band | None One Many |
| D-003 | 5 | rule | reassess_uptriage | High-risk vital signs? |
| N-006 | 6 | usage | none | The algorithm assumes the user has sufficient clinical knowledge to identify physiologic instability |
| A-003 | 6 | rule | assign_level_1 | Requires immediate lifesaving intervention? |
| B-006 | 6 | rule | assign_level_2 | High-risk situation? |
| B-007 | 6 | rule | assign_level_2 | Confused/lethargic/disoriented? |
| C-008 | 6 | rule | resource_band | None One Many |
| C-009 | 6 | rule | resource_band | None One Many |
| C-010 | 6 | rule | resource_band | None One Many |
| D-004 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-005 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-006 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-007 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-008 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-009 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-010 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-011 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-012 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-013 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-014 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-015 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-016 | 6 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-017 | 6 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| A-004 | 6 | definition | assign_level_1 | Immediate life-saving intervention required: Airway or respiratory support, emergency medications, hemodynamic interventions |
| B-010 | 6 | definition | assign_level_2 | High-risk situation: May become unstable, have high risk for deterioration, or exhibit newly altered mental status. |
| C-012 | 6 | definition | resource_band | complete blood count, electrolytes, and coagulant studies equal one resource because they are all laboratory tests |
| C-013 | 6 | definition | resource_band | Labs (blood, urine) |
| C-014 | 6 | definition | resource_band | Electrocardiogram, radiographs |
| C-015 | 6 | definition | resource_band | Computed tomography, magnetic resonance imaging, ultrasound, angiography |
| C-016 | 6 | definition | resource_band | Intravenous fluids (hydration) |
| C-017 | 6 | definition | resource_band | Intravenous, intramuscular, or nebulized medications |
| C-018 | 6 | definition | resource_band | Specialty consultation |
| C-020 | 6 | definition | resource_band | Complex procedure = 2 (procedural sedation) |
| C-021 | 6 | definition | resource_band | History and physicaI exam (Including pelvic) |
| C-022 | 6 | definition | resource_band | Point-of-care testing |
| C-024 | 6 | definition | resource_band | Oral medications |
| C-025 | 6 | definition | resource_band | Tetanus immunization |
| C-026 | 6 | definition | resource_band | Prescription refills |
| C-027 | 6 | definition | resource_band | Phone call to primary care physician |
| C-028 | 6 | definition | resource_band | Simple wound care (dressings, recheck) |
| C-029 | 6 | definition | resource_band | Crutches, splints, slings |
| D-022 | 6 | rule | consider_level_2 | T > 39°C (102.2°F) or < 36°C (96.8°F) |
| D-023 | 6 | rule | consider_level_2 | T > 39°C (102.2°F) or < 36°C (96.8°F) |
| D-024 | 6 | rule | consider_level_2 | Incomplete immunizations |
| D-025 | 6 | rule | consider_level_2 | No obvious source of fever |
| N-007 | 7 | usage | none | it was not developed to be a means of updating or communicating a change in patient condition after the provider has seen the patient |
| N-009 | 7 | usage | none | What is critical to this process is documentation of the change in condition, the reason for the change in ESI level, and the resultant acti |
| N-010 | 7 | usage | none | A dangerous but not uncommon practice is for colleagues to question the assigned acuity level or pressure the triage nurse to downgrade |
| N-012 | 7 | usage | none | Nor should the ESI level be used to manipulate metrics such as door-to-ECG or door-to-CT times. |
| N-013 | 7 | usage | none | the nurse follows decision points A through D to objectively assess them and assign an appropriate ESI acuity level |
| A-019 | 9 | rule | assign_level_1 | Requires immediate life-saving intervention? |
| A-037 | 9 | definition | assign_level_1 | Assisted ventilation Intubation Surgical airway Emergent non-invasive positive pressure ventilation |
| A-038 | 9 | definition | assign_level_1 | Defibrillation Emergent cardioversion External pacing |
| A-039 | 9 | definition | assign_level_1 | Chest needle decompression Pericardiocentesis Open thoracotomy |
| A-043 | 10 | usage | assign_level_1 | There are certain ESI level-1 patients who may be discharged from the ED if they have a reversible cause |
| B-012 | 11 | usage | none | it is determined that the patient does not meet ESI level-1 criteria, the nurse moves to decision point B |
| B-016 | 11 | rule | assign_level_2 | Confused/lethargic/disoriented? |
| B-017 | 11 | rule | assign_level_2 | Severe pain/distress? |
| B-018 | 11 | rule | assign_level_2 | Severe pain/distress? |
| B-019 | 11 | rule | assign_level_2 | Is the situation high-risk? |
| B-020 | 11 | rule | assign_level_2 | Is the patient likely to deteriorate? |
| B-021 | 11 | rule | assign_level_2 | Does the patient have an acute change in mental status? |
| B-022 | 11 | rule | assign_level_2 | Is the patient in severe pain or distress (physiological or psychological)? |
| B-023 | 11 | rule | assign_level_2 | Is the patient in severe pain or distress (physiological or psychological)? |
| B-024 | 11 | definition | assign_level_2 | A high- risk patient is one whose condition could easily deteriorate or who presents with symptoms suggestive of a condition requiring time- |
| B-039 | 12 | definition | assign_level_2 | the presence of confusion, lethargy, or disorientation refers to a new onset or an altered mental status (AMS). |
| B-040 | 12 | definition | assign_level_2 | AMS indicates a change in the level of consciousness and/or orientation from a patient’s baseline mental status. |
| B-041 | 12 | rule | assign_level_2 | AMS is a high-risk complaint |
| B-050 | 12 | rule | assign_level_2 | Behavioral outbursts at triage |
| B-051 | 12 | rule | assign_level_2 | Combativeness |
| B-052 | 12 | rule | assign_level_2 | Survivor of sexual violence |
| B-054 | 12 | rule | assign_level_2 | Acute grief reaction |
| B-055 | 12 | rule | assign_level_2 | Suicidal ideation, plan, or attempt |
| B-056 | 12 | rule | assign_level_2 | Prenatal loss |
| B-057 | 12 | usage | assign_level_2 | The following sections provides a nonexhaustive list of examples of other presenting symptoms and red flags that would warrant an ESI level- |
| B-058 | 12 | rule | assign_level_2 | Most concerning is the “thunderclap headache” (a severe, rapid-onset headache) |
| B-061 | 12 | rule | assign_level_2 | Other presentations of concern that warrant an ESI 2 designation include headache plus fever, vomiting, lower back pain, altered mental stat |
| B-062 | 12 | rule | assign_level_2 | Other presentations of concern that warrant an ESI 2 designation include headache plus fever, vomiting, lower back pain, altered mental stat |
| B-063 | 12 | rule | assign_level_2 | Other presentations of concern that warrant an ESI 2 designation include headache plus fever, vomiting, lower back pain, altered mental stat |
| B-064 | 12 | rule | assign_level_2 | Other presentations of concern that warrant an ESI 2 designation include headache plus fever, vomiting, lower back pain, altered mental stat |
| B-070 | 13 | definition | none | the elements of the score that predict urgency include the presence of altered vision; sudden diplopia, anisocoria, or exophthalmos; red eye |
| B-079 | 13 | rule | assign_level_2 | The high-risk patient is one who is currently ventilating and oxygenating adequately but is in respiratory distress and has the potential to |
| B-093 | 14 | definition | none | Critical determinants of acuity include blood pressure; bleeding; and abdominal, head, or chest pain. |
| B-096 | 14 | rule | assign_level_2 | Pregnant patients with chest pain and/or shortness of breath, abdominal pain, or headache |
| B-097 | 14 | rule | assign_level_2 | Pregnant patients with chest pain and/or shortness of breath, abdominal pain, or headache |
| B-098 | 14 | rule | assign_level_2 | Pregnant patients with chest pain and/or shortness of breath, abdominal pain, or headache |
| B-099 | 14 | rule | assign_level_2 | Pregnant patients with chest pain and/or shortness of breath, abdominal pain, or headache |
| N-016 | 15 | usage | none | ESI level-2 patients remain a high priority, and placement and treatment should be initiated rapidly. |
| C-030 | 19 | usage | resource_band | an ESI 1 or 2 designation has been ruled out, the presumed stability of the patient enables the nurse to move to the next decision point |
| C-031 | 19 | rule | resource_band | Patients who require two or more resources are assigned level 3 |
| C-034 | 19 | definition | resource_band | Resource prediction requires the nurse to determine how many resources are likely to be used in order for the provider to reach a dispositio |
| C-036 | 19 | rule | resource_band | None One Many |
| C-037 | 19 | rule | resource_band | None One Many |
| C-038 | 19 | rule | resource_band | None One Many |
| C-040 | 19 | definition | resource_band | A complete blood count and electrolyte panel comprise one resource (lab test). |
| C-041 | 19 | definition | resource_band | A complete blood count and chest radiograph are two resources (lab test, radiograph). |
| C-042 | 19 | definition | resource_band | A complete blood count and a urinalysis are both lab tests and together count as only one resource. |
| C-043 | 19 | definition | resource_band | A chest radiograph and abdominal radiograph are one resource (radiograph). |
| C-044 | 19 | definition | resource_band | Cervical-spine films and a computed tomography scan of the head are two resources (radiograph and computed tomography scan). |
| C-045 | 19 | definition | resource_band | it is important to realize that resources are defined by presentational acuity |
| C-046 | 19 | usage | resource_band | Consideration of resources is included in the triage level assignment for ESI levels 3, 4, and 5, while ESI level 1 and 2 decisions are base |
| C-047 | 20 | definition | resource_band | Labs (blood, urine) |
| C-048 | 20 | definition | resource_band | Electrocardiogram, radiographs |
| C-049 | 20 | definition | resource_band | Computed tomography, magnetic resonance imaging, ultrasound, angiography |
| C-050 | 20 | definition | resource_band | Intravenous fluids (hydration) |
| C-051 | 20 | definition | resource_band | Intravenous, intramuscular, or nebulized medications |
| C-052 | 20 | definition | resource_band | Specialty consultation |
| C-053 | 20 | definition | resource_band | Simple procedure = 1 (laceration repair, urinary catheter) |
| C-054 | 20 | definition | resource_band | Complex procedure = 2 (procedural sedation |
| C-055 | 20 | definition | resource_band | History and physical exam (including pelvic) |
| C-056 | 20 | definition | resource_band | Point-of-care testing |
| C-057 | 20 | definition | resource_band | Saline or heparin lock |
| C-058 | 20 | definition | resource_band | Oral medications |
| C-059 | 20 | definition | resource_band | Tetanus immunization |
| C-060 | 20 | definition | resource_band | Prescription refills |
| C-061 | 20 | definition | resource_band | Phone call to primary care physician |
| C-062 | 20 | definition | resource_band | Simple wound care (dressings, recheck) |
| C-063 | 20 | definition | resource_band | Crutches, splints, slings |
| C-064 | 20 | example | resource_band | Healthy 3-year-old patient with right ear pain, up to date on immunizations. Vital signs WNL. |
| C-065 | 20 | example | resource_band | A 42-year-old patient who lost their rescue inhaler and needs a new prescription |
| C-066 | 20 | example | resource_band | Healthy 19-year-old patient with a sore throat. Vital signs WNL |
| C-067 | 20 | example | resource_band | Healthy 29-year-old assigned female at birth with dysuria. |
| C-068 | 20 | example | resource_band | A 22-year-old assigned male at birth with right lower quadrant abdominal pain since early this morning |
| C-069 | 20 | example | resource_band | A 45-year-old patient with left lower leg pain and swelling |
| C-071 | 20 | example | resource_band | If that is the case the patient would be an ESI level 5. |
| C-072 | 20 | definition | resource_band | All three tests count as one resource (labs) |
| D-026 | 23 | usage | reassess_uptriage | For patients not meeting ESI level-1 or 2- criteria, a complete set of vital signs needs to be obtained |
| D-027 | 23 | usage | reassess_uptriage | Obtain a full set of vital signs to assist in determining patient acuity. |
| D-028 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-029 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-030 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-031 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-032 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-033 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-034 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-035 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-036 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-037 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-038 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-039 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-040 | 23 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-041 | 23 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-042 | 23 | rule | reassess_uptriage | SpO2 < 92% |
| D-044 | 23 | usage | none | The nurse can obtain vital signs if it may assist in confirming the triage acuity level. |
| D-045 | 23 | usage | none | Some patients may not be identified as ESI level 1 or 2 until vital signs are taken. |
| A-048 | 23 | example | assign_level_1 | the patient is unstable and should be assigned ESI level 1 no matter how “good” the patient appears |
| D-047 | 23 | usage | none | vital signs must be contextualized in light of the patient’s history, medications, and presentation. |
| D-050 | 23 | usage | none | Patients may present with medication-mediated “normal” vital signs, yet still be quite ill. |
| D-051 | 23 | usage | none | A full set of vital signs should be attempted in triage. |
| D-054 | 23 | example | resource_band | a 10-month-old who is up-to-date on immunizations, who presents with fever and pulling on his ear, could be assigned to ESI level 5 |
| D-055 | 24 | definition | reassess_uptriage | Term neonate to <1 month 90–190 35–60 67–84 |
| D-056 | 24 | definition | reassess_uptriage | Infant, 1–12 months 90–180 30–55 72–104 |
| D-057 | 24 | definition | reassess_uptriage | Toddler, 1–3 years 80–140 22–40 86–104 |
| D-058 | 24 | definition | reassess_uptriage | Preschooler, 3–5 years 65–120 18–35 89–112 |
| D-059 | 24 | definition | reassess_uptriage | School age, 5–12 years 70–120 16–30 90–115 |
| D-060 | 24 | definition | reassess_uptriage | Adolescent, 12–18 years 60–100 12–20 100–130 |
| D-063 | 24 | rule | assign_level_2 | < 90 days > 38°C (100.4°F) or < 36°C (96.8°F) |
| D-064 | 24 | rule | consider_level_2 | < 90 days > 38°C (100.4°F) or < 36°C (96.8°F) |
| D-068 | 24 | example | assign_level_2 | This patient meets the criteria for being uptriaged from level 3 to level 2 based on her vital signs. |
| D-069 | 24 | example | assign_level_2 | Based on vital sign assessment, the nurse should triage them to an ESI level 2. |
| D-070 | 25 | example | assign_level_2 | After assessing vital signs, the nurse should uptriage the patient to an ESI level 2. |
| D-071 | 25 | example | resource_band | The heart rate falls just outside the accepted parameter for the age of the patient, but other vital signs are within expected limits. |
| D-072 | 25 | example | assign_level_2 | it is critical to consider that as a cause of her elevated heart rate and respiratory rate and uptriage the patient to an ESI 2 |
| N-018 | 27 | usage | none | that ESI level should not be changed, unless the patient condition changes before they are placed from the waiting area |
| N-020 | 27 | usage | none | an appropriate note should be made in the medical record reflecting the patient’s change in condition and change in ESI level |
| N-021 | 27 | usage | none | ESI is not intended as an ongoing measurement of patient acuity. |
| N-023 | 27 | usage | none | if they are appropriately trained in the use of ESI, can assess patients at the initial encounter and assign an ESI level |
| N-024 | 27 | usage | none | It is not appropriate for a physician or advanced practice provider to assign a second ESI after the patient has been triaged by a nurse. |
| N-027 | 27 | usage | none | it should not be used to calculate billing |
| N-029 | 27 | usage | none | In tracking acuity in each department, distribution by percentage should be used. |
| A-049 | 29 | rule | assign_level_1 | Requires immediate lifesaving intervention? |
| B-132 | 29 | rule | assign_level_2 | High-risk situation? |
| B-133 | 29 | rule | assign_level_2 | Confused/lethargic/disoriented? |
| B-134 | 29 | rule | assign_level_2 | Severe pain/distress? |
| B-135 | 29 | rule | assign_level_2 | Severe pain/distress? |
| C-073 | 29 | rule | resource_band | None One Many |
| C-074 | 29 | rule | resource_band | None One Many |
| C-075 | 29 | rule | resource_band | None One Many |
| D-075 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-076 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-077 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-078 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-079 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-080 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-081 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-082 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-083 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-084 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-085 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-086 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-087 | 29 | rule | reassess_uptriage | > 190 > 180 > 140 > 120 > 120 > 100 > 100 |
| D-088 | 29 | rule | reassess_uptriage | > 60 > 55 > 40 > 35 > 30 > 20 > 20 |
| D-089 | 29 | rule | reassess_uptriage | SpO2 < 92% |
| A-050 | 30 | definition | assign_level_1 | Immediate life-saving intervention required: Airway or respiratory support, emergency medications, hemodynamic interventions |
| A-051 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-052 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-053 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-054 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-055 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-056 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-057 | 30 | rule | assign_level_1 | Clinical presentations requiring lifesaving interventions include the following: intubated, unresponsive, pulselessness, apneic, severe resp |
| A-058 | 30 | definition | assign_level_1 | Is nonverbal and not following commands (acutely) |
| A-059 | 30 | definition | assign_level_1 | Requires noxious stimulus (P or U on AVPU scale) |
| B-136 | 30 | definition | assign_level_2 | High-risk situation: May become unstable, have high risk for deterioration, or exhibit newly altered mental status. |
| B-137 | 30 | definition | assign_level_2 | Severe pain or distress is determined by patient report, corroborated with clinical observation. |
| C-076 | 30 | definition | resource_band | Count the number of different types of resources, not the individual tests or radiographs. |
| C-077 | 30 | definition | resource_band | complete blood count, electrolytes, and coagulant studies equal one resource because they are all laboratory tests |
| C-078 | 30 | definition | resource_band | Labs (blood, urine) |
| C-079 | 30 | definition | resource_band | Electrocardiogram, radiographs |
| C-080 | 30 | definition | resource_band | Computed tomography, magnetic resonance imaging, ultrasound, angiography |
| C-081 | 30 | definition | resource_band | Intravenous fluids (hydration) |
| C-082 | 30 | definition | resource_band | Intravenous, intramuscular, or nebulized medications |
| C-083 | 30 | definition | resource_band | Specialty consultation |
| C-084 | 30 | definition | resource_band | Simple procedure = 1 (laceration repair, urinary catheter) |
| C-085 | 30 | definition | resource_band | Complex procedure = 2 (procedural sedation) |
| C-086 | 30 | definition | resource_band | History and physicaI exam (Including pelvic) |
| C-087 | 30 | definition | resource_band | Point-of-care testing |
| C-088 | 30 | definition | resource_band | Saline or heparin lock |
| C-089 | 30 | definition | resource_band | Oral medications |
| C-090 | 30 | definition | resource_band | Tetanus immunization |
| C-091 | 30 | definition | resource_band | Prescription refills |
| C-092 | 30 | definition | resource_band | Phone call to primary care physician |
| C-093 | 30 | definition | resource_band | Simple wound care (dressings, recheck) |
| C-094 | 30 | definition | resource_band | Crutches, splints, slings |
| D-090 | 30 | rule | reassess_uptriage | Reassess to determine whether the patient warrants a higher acuity level if a patient has one or more vital signs outside the normal paramet |
| D-091 | 30 | rule | assign_level_2 | 1-28 days of age: Assign at least ESI 2 if T > 38° C |
| D-092 | 30 | rule | consider_level_2 | 1-3 months: Consider assigning ESI 2 if T > 38 ° C |
| D-093 | 30 | rule | consider_level_2 | T > 39°C (102.2°F) or < 36°C (96.8°F) |
| D-094 | 30 | rule | consider_level_2 | T > 39°C (102.2°F) or < 36°C (96.8°F) |
| D-095 | 30 | rule | consider_level_2 | Incomplete immunizations |
| D-096 | 30 | rule | consider_level_2 | No obvious source of fever |

## Only in ours

| statement | page | kind | supports | quote |
| ---: | ---: | --- | --- | --- |
| 16 | 6 | consider / matches | ['B-59.child-over-3-months-fever-consider'] | 3 months and older: Consider assigning ESI 2 or 3 if |
| 33 | 9 | definition / new | A-LIST.lifesaving-interventions | Table 3-1. Examples of Lifesaving Interventions |
| 52 | 12 | definition / refine | B-01.new-altered-mental-status | other clinical signs, such as confusion, somnolence, agitation, or belligerence, are commonly referred to as AMS |
| 59 | 12 | level2 / matches | ['B-32.thunderclap-headache'] | which is often associated with subarachnoid hemorrhage |
| 61 | 12 | level2 / matches | ['B-34.headache-red-flags'] | headache plus fever, vomiting, lower back pain, altered mental status, and/or signs and symptoms of stroke |
| 67 | 13 | consider / matches | ['B-28.ocular-high-risk-constellation'] | with more symptoms in constellation predicting a more emergent problem |
| 72 | 13 | definition / refine | B-16.button-battery-or-magnet-ingestion | especially in children less than 6 years of age and involving batteries greater than 20 mm in diameter |
| 77 | 13 | consider / new | B-62.possible-acs-without-chest-pain-consider | Patients with cardiac events may present with fatigue, nausea, vomiting, and/or weakness |
| 80 | 13 | consider / matches | ['B-55.recent-covid-cardiac-risk-consider'] | A recent Covid-19 infection increases cardiac risk |
| 87 | 14 | definition / not_a_rule |  | In younger children, pneumonia can present as abdominal pain |
| 89 | 14 | consider / new | B-63.elderly-abdominal-pain-consider | Elderly patients with abdominal pain are likely to need hospitalization |
| 92 | 14 | level2 / matches | ['B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache'] | abdominal pain, or headache (Sperling et al., 2015) should be triaged as ESI 2 |
| 97 | 14 | definition / not_a_rule |  | Assessing for current or recent COVID-19 infection is important to assessing risk |
| 117 | 20 | example / test_material |  | Table 5-2 Patient Presentations and Predicting Resources |
| 119 | 23 | consider / new | B-64.pale-diaphoretic-or-cyanotic-appearance | These patients may appear pale, diaphoretic, or cyanotic |
| 120 | 23 | level1 / matches | ['A-12.severe-brady-or-tachycardia'] | heart rate of 32 beats/minute or 180 beats/minute is discovered during vital sign measurement |
| 130 | 24 | vitals / matches | ['D-02.pediatric-danger-zone-under-1-month', 'D-06.pediatric-danger-zone-1-to-12-months', 'D-07.pediatric-danger-zone-1-to-3-years', 'D-08.pediatric-danger-zone-3-to-5-years', 'D-09.pediatric-danger-zone-5-to-12-years', 'D-10.pediatric-danger-zone-12-to-18-years'] | Table 6-1 lists the normal vital sign ranges for each pediatric age group |

## Our firing rules that no blind rule reached

B-27.geriatric-trauma-caution, B-28.ocular-high-risk-constellation, B-30.anticoagulated-trauma, B-32.thunderclap-headache, B-34.headache-red-flags, B-38.pregnant-chest-pain-breathlessness-abdo-pain-or-headache, B-52.geriatric-vitals-medication-context-consider, B-53.pediatric-respiratory-distress-signs-consider, B-55.recent-covid-cardiac-risk-consider, B-59.child-over-3-months-fever-consider, D-04.context-beta-blockers-consider, D-05.context-immunosuppression-consider

## Cut differently

One rule of ours, several in the blind re-extraction:

- A-22.requires-lifesaving-intervention: A-001, A-002
- B-02.severe-pain-consider: B-008, B-009, B-043
- B-35.severe-psychological-distress-consider: B-008, B-009, B-053
- D-01.adult-danger-zone: D-018, D-019, D-073, D-074
- A-15.intubated: A-005, A-006, A-007, A-008, A-009, A-010, A-011
- A-01.unresponsive: A-005, A-006, A-007, A-008, A-009, A-010, A-011, A-014, A-015, A-016, A-017, A-018, A-022, A-024
- A-04.pulseless: A-005, A-006, A-007, A-008, A-009, A-010, A-011
- A-03.apneic: A-005, A-006, A-007, A-008, A-009, A-010, A-011
- A-05.severe-respiratory-distress: A-005, A-006, A-007, A-008, A-009, A-010, A-011, A-045
- A-16.profound-hypotension: A-005, A-006, A-007, A-008, A-009, A-010, A-011
- A-11.hypoglycemia: A-005, A-006, A-007, A-008, A-009, A-010, A-011, A-029
- B-56.infant-under-28-days-fever: D-020, D-052
- B-57.infant-under-90-days-temperature-over-38: D-020, D-061
- A-07.active-seizure: A-014, A-015, A-016, A-017, A-018, A-022
- A-06.occluded-airway: A-014, A-015, A-016, A-017, A-018, A-020, A-022
- A-21.impaired-gas-exchange: A-014, A-015, A-016, A-017, A-018, A-022
- A-19.ineffective-tissue-perfusion: A-014, A-015, A-016, A-017, A-018, A-022, A-023
- A-12.severe-brady-or-tachycardia: A-030, A-031
- A-02.arrest-or-imminent: A-033, A-034, A-035
- B-05.stroke-signs: B-028, B-065
- B-08.transplant-fever-or-infection: B-031, B-032, B-121, B-122, B-123
- B-09.suicidal-or-homicidal: B-033, B-034, B-125, B-126, B-127, B-128, B-129, B-130, B-131
- B-11.sexual-assault: B-036, B-049, B-108, B-109, B-110, B-111
- B-13.postpartum-hemorrhage: B-038, B-102
- B-03.severe-pain-systemic-cause: B-046, B-047
- B-33.headache-with-neck-pain-or-nuchal-rigidity: B-059, B-060
- B-14.stridor-or-secretions: B-072, B-073
- B-15.high-risk-epistaxis: B-074, B-075, B-076, B-077
- B-16.button-battery-or-magnet-ingestion: B-078, B-090, B-091
- B-18.abdo-pain-sepsis-or-hypoperfusion: B-085, B-086
- B-37.pregnant-postpartum-sbp-out-of-range: B-094, B-095
- B-43.uti-elderly-or-urosepsis-signs: B-105, B-106
- B-22.fall-from-6-metres-or-more: B-108, B-109, B-110, B-111
- B-44.vehicle-ejection: B-108, B-109, B-110, B-111
- B-45.mechanical-extrication: B-108, B-109, B-110, B-111
- B-24.extremity-neurovascular-compromise: B-113, B-114, B-115
- B-46.compartment-syndrome-symptoms: B-113, B-114, B-115
- B-47.partial-or-complete-amputation: B-113, B-114, B-115
- B-25.pelvis-femur-fracture-consider: B-116, B-117, B-118
- B-51.psychotic-or-violent: B-128, B-129, B-130, B-131
- B-61.child-over-3-months-temperature-red-flag-consider: D-065, D-066

One blind rule, several of ours:

- B-008: B-02.severe-pain-consider, B-35.severe-psychological-distress-consider
- B-009: B-02.severe-pain-consider, B-35.severe-psychological-distress-consider
- D-018: D-01.adult-danger-zone, D-11.spo2-below-92-any-age
- A-005: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-006: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-007: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-008: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-009: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-010: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- A-011: A-01.unresponsive, A-03.apneic, A-04.pulseless, A-05.severe-respiratory-distress, A-11.hypoglycemia, A-15.intubated, A-16.profound-hypotension
- D-019: D-01.adult-danger-zone, D-02.pediatric-danger-zone-under-1-month, D-06.pediatric-danger-zone-1-to-12-months, D-07.pediatric-danger-zone-1-to-3-years, D-08.pediatric-danger-zone-3-to-5-years, D-09.pediatric-danger-zone-5-to-12-years, D-10.pediatric-danger-zone-12-to-18-years
- D-020: B-56.infant-under-28-days-fever, B-57.infant-under-90-days-temperature-over-38
- A-014: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- A-015: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- A-016: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- A-017: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- A-018: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- A-022: A-01.unresponsive, A-06.occluded-airway, A-07.active-seizure, A-19.ineffective-tissue-perfusion, A-21.impaired-gas-exchange
- B-108: B-11.sexual-assault, B-22.fall-from-6-metres-or-more, B-44.vehicle-ejection, B-45.mechanical-extrication
- B-109: B-11.sexual-assault, B-22.fall-from-6-metres-or-more, B-44.vehicle-ejection, B-45.mechanical-extrication
- B-110: B-11.sexual-assault, B-22.fall-from-6-metres-or-more, B-44.vehicle-ejection, B-45.mechanical-extrication
- B-111: B-11.sexual-assault, B-22.fall-from-6-metres-or-more, B-44.vehicle-ejection, B-45.mechanical-extrication
- B-113: B-24.extremity-neurovascular-compromise, B-46.compartment-syndrome-symptoms, B-47.partial-or-complete-amputation
- B-114: B-24.extremity-neurovascular-compromise, B-46.compartment-syndrome-symptoms, B-47.partial-or-complete-amputation
- B-115: B-24.extremity-neurovascular-compromise, B-46.compartment-syndrome-symptoms, B-47.partial-or-complete-amputation
- B-119: B-26.suspected-toxic-ingestion, B-48.unexplained-changes-possible-ingestion-consider
- B-128: B-09.suicidal-or-homicidal, B-51.psychotic-or-violent
- B-129: B-09.suicidal-or-homicidal, B-51.psychotic-or-violent
- B-130: B-09.suicidal-or-homicidal, B-51.psychotic-or-violent
- B-131: B-09.suicidal-or-homicidal, B-51.psychotic-or-violent

## Same sentence, comparable parts agree (fact names side by side)

| ours | blind | our facts | blind facts |
| --- | --- | --- | --- |
| A-22.requires-lifesaving-intervention | A-001 | obs.requires_lifesaving_intervention | needs_immediate_lifesaving_intervention |
| A-22.requires-lifesaving-intervention | A-002 | obs.requires_lifesaving_intervention | needs_immediate_lifesaving_intervention |
| D-11.spo2-below-92-any-age | D-018 | vitals.spo2 | spo2_percent |
| A-15.intubated | A-005 | obs.intubated | is_intubated |
| A-04.pulseless | A-005 | obs.pulseless | is_intubated |
| A-03.apneic | A-005 | obs.apneic | is_intubated |
| A-05.severe-respiratory-distress | A-005 | obs.severe_respiratory_distress | is_intubated |
| A-15.intubated | A-006 | obs.intubated | is_unresponsive |
| A-04.pulseless | A-006 | obs.pulseless | is_unresponsive |
| A-03.apneic | A-006 | obs.apneic | is_unresponsive |
| A-05.severe-respiratory-distress | A-006 | obs.severe_respiratory_distress | is_unresponsive |
| A-15.intubated | A-007 | obs.intubated | is_pulseless |
| A-04.pulseless | A-007 | obs.pulseless | is_pulseless |
| A-03.apneic | A-007 | obs.apneic | is_pulseless |
| A-05.severe-respiratory-distress | A-007 | obs.severe_respiratory_distress | is_pulseless |
| A-15.intubated | A-008 | obs.intubated | is_apneic |
| A-04.pulseless | A-008 | obs.pulseless | is_apneic |
| A-03.apneic | A-008 | obs.apneic | is_apneic |
| A-05.severe-respiratory-distress | A-008 | obs.severe_respiratory_distress | is_apneic |
| A-15.intubated | A-009 | obs.intubated | respiratory_distress_severity |
| A-04.pulseless | A-009 | obs.pulseless | respiratory_distress_severity |
| A-03.apneic | A-009 | obs.apneic | respiratory_distress_severity |
| A-05.severe-respiratory-distress | A-009 | obs.severe_respiratory_distress | respiratory_distress_severity |
| A-16.profound-hypotension | A-010 | vitals.profound_hypotension | is_profoundly_hypotensive |
| A-11.hypoglycemia | A-010 | vitals.profound_hypoglycemia | is_profoundly_hypotensive |
| A-16.profound-hypotension | A-011 | vitals.profound_hypotension | has_hypoglycemia |
| A-11.hypoglycemia | A-011 | vitals.profound_hypoglycemia | has_hypoglycemia |
| A-07.active-seizure | A-014 | obs.active_seizure | is_unresponsive |
| A-06.occluded-airway | A-014 | obs.airway_occluded_or_ineffective_clearance | is_unresponsive |
| A-21.impaired-gas-exchange | A-014 | obs.impaired_gas_exchange | is_unresponsive |
| A-19.ineffective-tissue-perfusion | A-014 | obs.ineffective_tissue_perfusion | is_unresponsive |
| A-07.active-seizure | A-015 | obs.active_seizure | has_active_seizure |
| A-06.occluded-airway | A-015 | obs.airway_occluded_or_ineffective_clearance | has_active_seizure |
| A-21.impaired-gas-exchange | A-015 | obs.impaired_gas_exchange | has_active_seizure |
| A-19.ineffective-tissue-perfusion | A-015 | obs.ineffective_tissue_perfusion | has_active_seizure |
| A-07.active-seizure | A-016 | obs.active_seizure | has_occluded_airway |
| A-06.occluded-airway | A-016 | obs.airway_occluded_or_ineffective_clearance | has_occluded_airway |
| A-21.impaired-gas-exchange | A-016 | obs.impaired_gas_exchange | has_occluded_airway |
| A-19.ineffective-tissue-perfusion | A-016 | obs.ineffective_tissue_perfusion | has_occluded_airway |
| A-07.active-seizure | A-017 | obs.active_seizure | has_impaired_gas_exchange |
| A-06.occluded-airway | A-017 | obs.airway_occluded_or_ineffective_clearance | has_impaired_gas_exchange |
| A-21.impaired-gas-exchange | A-017 | obs.impaired_gas_exchange | has_impaired_gas_exchange |
| A-19.ineffective-tissue-perfusion | A-017 | obs.ineffective_tissue_perfusion | has_impaired_gas_exchange |
| A-07.active-seizure | A-018 | obs.active_seizure | has_ineffective_perfusion |
| A-06.occluded-airway | A-018 | obs.airway_occluded_or_ineffective_clearance | has_ineffective_perfusion |
| A-21.impaired-gas-exchange | A-018 | obs.impaired_gas_exchange | has_ineffective_perfusion |
| A-19.ineffective-tissue-perfusion | A-018 | obs.ineffective_tissue_perfusion | has_ineffective_perfusion |
| A-06.occluded-airway | A-020 | obs.airway_occluded_or_ineffective_clearance | has_ineffective_airway_clearance |
| A-20.ineffective-respiratory-pattern | A-021 | obs.ineffective_respiratory_pattern | has_ineffective_respiratory_pattern |
| A-07.active-seizure | A-022 | obs.active_seizure | has_impaired_gas_exchange |
| A-06.occluded-airway | A-022 | obs.airway_occluded_or_ineffective_clearance | has_impaired_gas_exchange |
| A-21.impaired-gas-exchange | A-022 | obs.impaired_gas_exchange | has_impaired_gas_exchange |
| A-19.ineffective-tissue-perfusion | A-022 | obs.ineffective_tissue_perfusion | has_impaired_gas_exchange |
| A-19.ineffective-tissue-perfusion | A-023 | obs.ineffective_tissue_perfusion | has_ineffective_perfusion |
| A-08.spo2-below-90-with-compromise | A-025 | obs.respiratory_compromise_signs, vitals.spo2, vitals.spo2_is_patients_norm | has_other_signs_of_respiratory_compromise, low_spo2_is_patients_norm, spo2_percent |
| A-09.anaphylaxis | A-026 | obs.anaphylaxis | has_anaphylaxis |
| A-10.hypotension-with-hypoperfusion | A-027 | obs.hypoperfusion_signs, vitals.hypotension | has_signs_of_hypoperfusion, is_hypotensive |
| A-11.hypoglycemia | A-029 | vitals.profound_hypoglycemia | has_hypoglycemia |
| A-12.severe-brady-or-tachycardia | A-030 | vitals.extreme_heart_rate | has_severe_bradycardia |
| A-12.severe-brady-or-tachycardia | A-031 | vitals.extreme_heart_rate | has_severe_tachycardia |
| A-02.arrest-or-imminent | A-033 | obs.cardiac_or_pulmonary_arrest | is_pulseless |
| A-02.arrest-or-imminent | A-034 | obs.cardiac_or_pulmonary_arrest | is_apneic |
| A-02.arrest-or-imminent | A-035 | obs.cardiac_or_pulmonary_arrest | arrest_appears_imminent |
| B-07.immunocompromised-fever | B-030 | complaint.fever, history.immunocompromised | has_fever, is_on_chemotherapy |
| B-09.suicidal-or-homicidal | B-033 | complaint.danger_to_self_or_others | is_suicidal |
| B-09.suicidal-or-homicidal | B-034 | complaint.danger_to_self_or_others | is_homicidal |
| B-11.sexual-assault | B-036 | complaint.sexual_assault | is_sexual_assault_survivor |
| B-02.severe-pain-consider | B-043 | complaint.pain_rating | pain_score |
| B-16.button-battery-or-magnet-ingestion | B-078 | complaint.button_battery_or_magnet_ingestion | swallowed_button_battery |
| B-36.abnormal-ecg-chest-pain | B-083 | complaint.category, vitals.ecg_abnormal | ecg_abnormal, has_chest_pain |
| B-16.button-battery-or-magnet-ingestion | B-090 | complaint.button_battery_or_magnet_ingestion | swallowed_button_battery |
| B-16.button-battery-or-magnet-ingestion | B-091 | complaint.button_battery_or_magnet_ingestion | swallowed_earth_magnet |
| B-39.pregnant-heavy-bleeding-abnormal-vitals-infection | B-100 | complaint.heavy_vaginal_bleeding, complaint.infection_signs, history.pregnant_or_postpartum, vitals.abnormal_for_patient | has_abnormal_vital_signs, has_heavy_vaginal_bleeding, has_signs_of_infection, is_pregnant |
| B-41.testicular-or-scrotal-pain-torsion-consider | B-103 | complaint.testicular_or_scrotal_pain | has_testicular_or_scrotal_pain |
| B-42.unilateral-lower-quadrant-pain-torsion-or-ectopic-consider | B-104 | complaint.unilateral_lower_quadrant_pain, patient.has_ovaries | has_ovaries, has_unilateral_lower_quadrant_pain |
| B-49.severe-flank-pain | B-107 | complaint.severe_flank_pain | has_severe_flank_pain |
| B-22.fall-from-6-metres-or-more | B-108 | E.fall_height_meters | fall_height_meters |
| B-44.vehicle-ejection | B-109 | E.vehicle_ejection | ejected_from_vehicle |
| B-45.mechanical-extrication | B-109 | E.mechanical_extrication | ejected_from_vehicle |
| B-11.sexual-assault | B-109 | complaint.sexual_assault | ejected_from_vehicle |
| B-44.vehicle-ejection | B-110 | E.vehicle_ejection | required_mechanical_extrication |
| B-45.mechanical-extrication | B-110 | E.mechanical_extrication | required_mechanical_extrication |
| B-11.sexual-assault | B-110 | complaint.sexual_assault | required_mechanical_extrication |
| B-44.vehicle-ejection | B-111 | E.vehicle_ejection | is_sexual_assault_survivor |
| B-45.mechanical-extrication | B-111 | E.mechanical_extrication | is_sexual_assault_survivor |
| B-11.sexual-assault | B-111 | complaint.sexual_assault | is_sexual_assault_survivor |
| B-24.extremity-neurovascular-compromise | B-115 | complaint.extremity_neurovascular_compromise | has_amputation |
| B-46.compartment-syndrome-symptoms | B-115 | complaint.compartment_syndrome_symptoms | has_amputation |
| B-47.partial-or-complete-amputation | B-115 | complaint.amputation_partial_or_complete | has_amputation |
| B-26.suspected-toxic-ingestion | B-119 | complaint.known_toxic_ingestion | toxic_ingestion |
| B-50.transplant-list-consider | B-124 | history.on_transplant_list | is_on_transplant_list |
| B-09.suicidal-or-homicidal | B-125 | complaint.danger_to_self_or_others | is_danger_to_self |
| B-09.suicidal-or-homicidal | B-126 | complaint.danger_to_self_or_others | is_danger_to_others |
| B-09.suicidal-or-homicidal | B-127 | complaint.danger_to_self_or_others | is_danger_to_environment |
| B-09.suicidal-or-homicidal | B-128 | complaint.danger_to_self_or_others | is_suicidal |
| B-51.psychotic-or-violent | B-128 | complaint.psychotic_or_violent | is_suicidal |
| B-09.suicidal-or-homicidal | B-129 | complaint.danger_to_self_or_others | is_homicidal |
| B-51.psychotic-or-violent | B-129 | complaint.psychotic_or_violent | is_homicidal |
| B-09.suicidal-or-homicidal | B-131 | complaint.danger_to_self_or_others | is_violent |
| B-51.psychotic-or-violent | B-131 | complaint.psychotic_or_violent | is_violent |
