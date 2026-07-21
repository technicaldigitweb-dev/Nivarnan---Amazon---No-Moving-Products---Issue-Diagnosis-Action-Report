# ANPIA Validation Index

**Date:** 2026-07-20
**Purpose:** Concise pointer index of every validation performed across this project. Each row
links to the full report rather than duplicating its content.

| Category | Validation file | Status | Date | Evidence path | Known limitation |
|---|---|---|---|---|---|
| Source-data validation | `06_VALIDATION/2026-07-20__anpia_production_live_data_validation.md` | PASS | 2026-07-20 | `07_EVIDENCE/database/2026-07-20__common_daily_dataset_extraction_evidence.md` | Sessions/Page Views/Buy Box %/Conversion Rate/CTR lack a single confidently-complete source |
| Source-data validation (SQL) | `06_VALIDATION/2026-07-17__sql_validation_report.md` | PASS | 2026-07-17 | `07_EVIDENCE/database/` | Superseded by later live-data validation as scope corrected |
| Calculation reconciliation | `06_VALIDATION/2026-07-20__anpia_v002_calculation_validation.md` | PASS -- 0/108 mismatches | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_production_calculation_reconciliation.md` | None outstanding |
| Calculation reconciliation (dataset build) | `06_VALIDATION/2026-07-20__metric_calculation_validation.md`, `06_VALIDATION/2026-07-20__common_dataset_validation_report.md` | PASS | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__common_dataset_reconciliation_evidence.md` | None outstanding |
| Browser validation | `06_VALIDATION/2026-07-20__anpia_production_html_browser_validation.md` | PASS -- 18/18 checks, 0 console errors, 0 network requests | 2026-07-20 | `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/validated/browser_results.json` | Real hosted-modal container dimensions unconfirmed (simulation-based) |
| v002 UI validation | `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` | PASS -- 15 rows visible at every tested viewport | 2026-07-20 | `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/validated/` | Same hosted-dimension caveat as above; not yet user-confirmed on the real hosted tool |
| ph_task publication validation | `06_VALIDATION/2026-07-20__anpia_v002_publication_validation.md` | PASS | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md` | ph_task versioning-convention conflict (insert-new+reject-old vs. update-in-place) unresolved -- see `08_SKILLS/ph_task_reference/ph_task_versioning_rules.md` |
| Automation validation | `06_VALIDATION/2026-07-20__anpia_automation_validation.md` | `AUTOMATION_BUILT_NOT_ACTIVATED` | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md` | VM access not yet available |
| Manual update-to-table validation | `06_VALIDATION/2026-07-20__ph_task_upload_script_validation.md` | PASS | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_update_to_table_command_evidence.md` | None outstanding |
| daily_task validation | (covered directly in evidence, no standalone `06_VALIDATION` file) | PASS | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_daily_task_dry_run.md`, `.../2026-07-20__anpia_daily_task_publication_evidence.md` | 3 mapping-convention items (aios_phase, deliverable_id format, developer casing) flagged for owner standardization |
| Secret scan / secure configuration | `06_VALIDATION/2026-07-20__anpia_secure_configuration_validation.md` | PASS -- 15/15 tests | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md` | Credential rotation itself not yet confirmed (AMBER) -- `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md` |
| GitHub closure validation | (covered directly in evidence, no standalone `06_VALIDATION` file) | PASS | 2026-07-20 | `07_EVIDENCE/validation/2026-07-20__anpia_git_github_publication_evidence.md` | None outstanding |
| Earlier iteration validations (v004-v007, superseded by v002 production release) | `06_VALIDATION/2026-07-20__html_v004_layout_validation.md`, `.../2026-07-20__v005_file_size_and_performance_validation.md`, `.../2026-07-20__v005_single_dataset_reconciliation.md`, `.../2026-07-20__v006_data_reconciliation.md`, `.../2026-07-20__v006_user_experience_validation.md`, `.../2026-07-20__v007_identity_column_ui_validation.md`, `.../2026-07-20__html_validation_report.md`, `.../2026-07-17__html_validation_report.md` | PASS (historical, retained as audit trail) | 2026-07-17 / 2026-07-20 | `07_EVIDENCE/validation/` (matching filenames per version) | Superseded by v002; kept for build-history traceability, not re-verified in this index |

## Notes

This index links to full reports rather than duplicating their content, per project convention.
Statuses reflect each report's own stated result at the time it was written; none were
re-executed to produce this index.
