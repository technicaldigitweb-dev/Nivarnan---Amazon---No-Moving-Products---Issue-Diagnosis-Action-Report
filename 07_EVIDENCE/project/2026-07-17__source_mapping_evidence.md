# Source Mapping Evidence

**Date:** 2026-07-17
**Project root:** `C:\Users\LED237\Documents\Projects\Nivarnan - Amazon - No-Moving Products - Issue Diagnosis & Action Report`

## 1. Original source inventory (Sources/, before any action)

| File/Folder | Type | Size (bytes) | Last modified |
|---|---|---|---|
| AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip | file | 62575 | 2026-06-19 14:48:59 +0530 |
| aios_architecture.md | file | 8590 | 2026-06-19 14:23:18 +0530 |
| Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx | file | 93529 | 2026-07-17 10:45:37 +0530 |
| db_access_templates/ | folder | — | — |
| db_access_templates/temp_user.py | file | 3705 | 2026-07-16 17:57:30 +0530 |
| db_access_templates/temp_user_access_report.pdf | file | 20830 | 2026-07-08 15:37:11 +0530 |
| db_access_templates/update_table.py | file | 4261 | 2026-07-16 17:57:52 +0530 |
| ph_task_reference/ | folder | — | — |
| ph_task_reference/ph_task_assigned_user_team_rules.md | file | 2111 | 2026-07-08 15:35:32 +0530 |
| ph_task_reference/ph_task_schema.md | file | 10188 | 2026-07-08 15:32:53 +0530 |
| ph_task_reference/ph_task_versioning_rules.md | file | 3181 | 2026-07-08 15:34:49 +0530 |
| skills 3 (1) (3).zip | file | 63183 | 2026-07-09 16:36:42 +0530 |
| skills_minimal_pack 2 (2).zip | file | 78984 | 2026-07-09 16:36:48 +0530 |
| table_location_business_details 3.xlsx | file | 29741 | 2026-07-17 10:44:36 +0530 |

`.mcp.json` (project root): confirmed present, size 216 bytes, `Jul 17 10:59`. Only top-level key names read (`mcpServers` → `ledsone-docs`, `ledsone-db`); no values printed.

## 2. ZIP top-level contents (listed, not extracted into project root)

### AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip (17 files, 72219 bytes uncompressed)
Numbered SKILL_*.md files (01–12), two .docx project instruction files, `SKILL_PROMPT_FACTORY.md`, `0.9_README_SKILL_PACK_START_HERE.md`. Full listing captured via `unzip -l`.

### skills 3 (1) (3).zip (15 files, 177914 bytes uncompressed)
`skills/SKILL_multi_table.md`, `SKILL_ppc_stock_lookup.md`, `SKILL_single_table.md`, `SKILL_threshold_validator.md`, `TABLE_ebay_msg.md`, `TABLE_expense_amz_ebay_shopify.md`, `TABLE_gate_Evalution.md`, `TABLE_inv_final_stock.md`, `TABLE_order_transaction.md`, `TABLE_ph_segment.md`, `TABLE_ppc.md`, `TABLE_shopify_msg.md`, `TABLE_thresholds.md`, `TABLE_traffic_data.md`, `TABLE_weekly_questions_answers.md`.

### skills_minimal_pack 2 (2).zip (18 files, 227073 bytes uncompressed)
`skills/SKILL_multi_table.md`, `SKILL_ppc_stock_lookup.md`, `SKILL_single_table.md`, `TABLE_amazon_returns.md`, `TABLE_amz_msg.md`, `TABLE_ebay_msg.md`, `TABLE_ebay_returns.md`, `TABLE_expense_amz_ebay_shopify.md`, `TABLE_gate_Evalution.md`, `TABLE_inv_final_stock.md`, `TABLE_message_app_logs.md`, `TABLE_msg_tag.md`, `TABLE_order_transaction.md`, `TABLE_ph_segment.md`, `TABLE_phrases.md`, `TABLE_ppc.md`, `TABLE_shopify_msg.md`, `TABLE_traffic_data.md`.

## 3. Folder recursive listings (filenames only)

`db_access_templates/`: temp_user.py, temp_user_access_report.pdf, update_table.py — file contents **not** printed. Credential-keyword scan performed by count only (see §6).

`ph_task_reference/`: ph_task_assigned_user_team_rules.md, ph_task_schema.md, ph_task_versioning_rules.md — contents read in full (safe, non-secret schema documentation) to resolve the Step 7 governance-vs-skill classification.

## 4. Classifications

| Asset | Classification |
|---|---|
| AIOS GPT Project instructions ZIP | PROJECT_CONTROL |
| aios_architecture.md | PROJECT_CONTROL |
| Nivarnan workbook (v001.xlsx) | REQUIREMENT_SOURCE |
| db_access_templates/temp_user.py | RESTRICTED_DATABASE_ACCESS |
| db_access_templates/temp_user_access_report.pdf | RESTRICTED_DATABASE_ACCESS |
| db_access_templates/update_table.py | RESTRICTED_DATABASE_ACCESS |
| ph_task_reference/ (all 3 files) | DATABASE_SKILL (technical schema/workflow reference — not governance) |
| skills 3 (1) (3).zip | DATABASE_SKILL (copy withheld — version conflict) |
| skills_minimal_pack 2 (2).zip | DATABASE_SKILL (copy withheld — version conflict) |
| table_location_business_details 3.xlsx | DATABASE_SKILL (confirmed "Table Routing Map") |
| .mcp.json | CONFIGURATION |

Full detail and reasoning in `02_SOURCE/2026-07-17__source_register.md`.

## 5. Checksums

SHA-256 (whole file), computed with `sha256sum`:

| File | SHA-256 |
|---|---|
| AIOS GPT Project instructions ZIP | 75a122157b46856841e44af4e9f07eb9ef42dae071c71f115c23b0ebe110a47e |
| aios_architecture.md | 41a9e418bfd2a7e0699cccf3cd5a60c9d8ce1ed43c0864027a401ff3d7fcac1a |
| Nivarnan workbook | 3b09c62ca897c03c4e8c2c4cd5944b7d2f80c1b755b0a88a0029a500aaab1dc3 |
| db_access_templates/temp_user.py | 75127caf875b9bc62cd8ffb5740572a57cb3af13a1e7a47892498ebb5f63af6b |
| db_access_templates/temp_user_access_report.pdf | b0c2641ae879e33e898df8b7d109d5a630510031aafd62b3de274babe175a5cd |
| db_access_templates/update_table.py | a4e2d7ea6169dfa2802a47cac6031155009e105558aa3e291499eb2485ac6025 |
| ph_task_reference/ph_task_assigned_user_team_rules.md | 82e6d4d8a5e9b841ce26cd74b8ff807d411f4d67f5dbbdb953e90a87ada19f3f |
| ph_task_reference/ph_task_schema.md | 718338bd8dd9809509b26c5b51fd668c8714ae3e2dfa433dca010920b82ab40b |
| ph_task_reference/ph_task_versioning_rules.md | 93f94c4486900475b3d18148cfaa6ef166132b6c0b3bb7ececd9f0579679cf71 |
| skills 3 (1) (3).zip (whole file) | 72810946557f288c2a4e0217bde70ee250f7906e6248b3522bc2a149d1d6dc82 |
| skills_minimal_pack 2 (2).zip (whole file) | 068578f1b906b621938ee768a812863a4e02932ee3a39bb58355a7ad346ff6db |
| table_location_business_details 3.xlsx | 7432ac67ab804782b0ab5884c19ac8fe522a62cafb3f7de8dbeef9e309ef1bbf |
| .mcp.json (unchanged) | 69c55f9bafa405570a950550915ecb79b11266b52018b2e64f67c34118c3ff22 |

## 6. Duplicate/version findings

### skills 3 (1) (3).zip vs skills_minimal_pack 2 (2).zip

Per-entry CRC-32 comparison (via `unzip -v`, no extraction):

| Filename | In skills 3? (CRC-32) | In minimal_pack? (CRC-32) | Result |
|---|---|---|---|
| SKILL_multi_table.md | Yes (3ab61f79, 22752B) | Yes (b2834ff1, 22772B) | **CONFLICTING** — different content |
| SKILL_ppc_stock_lookup.md | Yes (009a1d33, 13436B) | Yes (dd5d7702, 22197B) | **CONFLICTING** — different content, minimal_pack much larger |
| SKILL_single_table.md | Yes (a0c4fb9a, 8919B) | Yes (a0c4fb9a, 8919B) | **IDENTICAL** — same CRC-32, same size |
| SKILL_threshold_validator.md | Yes (246c09cf, 16422B) | No | Only in skills 3 |
| TABLE_ebay_msg.md | Yes (c25dd738, 7285B) | Yes (60f67b29, 10162B) | **CONFLICTING** |
| TABLE_expense_amz_ebay_shopify.md | Yes (ab779cc8, 18400B) | Yes (6150e610, 18618B) | **CONFLICTING** |
| TABLE_gate_Evalution.md | Yes (5b93a2b5, 6311B) | Yes (25b6c403, 6593B) | **CONFLICTING** |
| TABLE_inv_final_stock.md | Yes (552d6ecc, 11512B) | Yes (552d6ecc, 11512B) | **IDENTICAL** — same CRC-32, same size |
| TABLE_order_transaction.md | Yes (bc6af87d, 13584B) | Yes (581e1839, 14509B) | **CONFLICTING** |
| TABLE_ph_segment.md | Yes (946057a9, 8990B) | Yes (1255fd47, 9573B) | **CONFLICTING** |
| TABLE_ppc.md | Yes (ac368407, 24473B) | Yes (ecf9afbc, 36270B) | **CONFLICTING** — minimal_pack much larger |
| TABLE_shopify_msg.md | Yes (7a888bfa, 5222B) | Yes (167bc05b, 9272B) | **CONFLICTING** |
| TABLE_thresholds.md | Yes (17983353, 6217B) | No | Only in skills 3 |
| TABLE_traffic_data.md | Yes (6f179082, 4480B) | Yes (b2779584, 4683B) | **CONFLICTING** |
| TABLE_weekly_questions_answers.md | Yes (fa69aaac, 9911B) | No | Only in skills 3 |
| TABLE_amazon_returns.md | No | Yes (d4fa7c12, 9903B) | Only in minimal_pack |
| TABLE_amz_msg.md | No | Yes (2f6fa498, 10880B) | Only in minimal_pack |
| TABLE_ebay_returns.md | No | Yes (8fdf1c5e, 9866B) | Only in minimal_pack |
| TABLE_message_app_logs.md | No | Yes (c13d5dc7, 6316B) | Only in minimal_pack |
| TABLE_msg_tag.md | No | Yes (ccb898cb, 5775B) | Only in minimal_pack |
| TABLE_phrases.md | No | Yes (37442d56, 9253B) | Only in minimal_pack |

**Conclusion:** 2 files are byte-identical between the two zips. 10 overlapping filenames have conflicting (different) content — `skills_minimal_pack 2 (2).zip` entries are dated later (2026-06-08/12) than `skills 3 (1) (3).zip` entries (2026-04-24 to 2026-05-26), suggesting the minimal pack is a newer revision for those files, but this was **not assumed** as a safe basis for copying. 3 files exist only in `skills 3 (1) (3).zip` and are absent from the minimal pack. Neither archive is a strict superset of the other. **No merge performed. Neither zip's contents were copied.** Both remain in `Sources/` unchanged, marked `REVIEW_REQUIRED` in the source register.

### AIOS project-instruction ZIP
No overlapping filename found against any other asset in `Sources/`. No duplicate/version risk identified.

## 7. Files copied and destination paths

| Original | Destination | Checksum match |
|---|---|---|
| Sources/AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip | 00_PROJECT_CONTROL/source_references/AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip | MATCH |
| Sources/aios_architecture.md | 00_PROJECT_CONTROL/source_references/aios_architecture.md | MATCH |
| Sources/Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx | 02_SOURCE/requirements/Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx | MATCH |
| Sources/table_location_business_details 3.xlsx | 08_SKILLS/database/table_location_business_details 3.xlsx | MATCH |
| Sources/ph_task_reference/ph_task_assigned_user_team_rules.md | 08_SKILLS/ph_task_reference/ph_task_assigned_user_team_rules.md | MATCH |
| Sources/ph_task_reference/ph_task_schema.md | 08_SKILLS/ph_task_reference/ph_task_schema.md | MATCH |
| Sources/ph_task_reference/ph_task_versioning_rules.md | 08_SKILLS/ph_task_reference/ph_task_versioning_rules.md | MATCH |

All copies performed with `cp -p` (preserves original file, timestamps). All 7 checksums verified identical between original and copy after the operation.

## 8. Files intentionally kept in Sources/ (not copied)

- `skills 3 (1) (3).zip` — unresolved version conflict with `skills_minimal_pack 2 (2).zip` (see §6).
- `skills_minimal_pack 2 (2).zip` — unresolved version conflict with `skills 3 (1) (3).zip` (see §6).
- `db_access_templates/temp_user.py` — RESTRICTED_DATABASE_ACCESS.
- `db_access_templates/temp_user_access_report.pdf` — RESTRICTED_DATABASE_ACCESS.
- `db_access_templates/update_table.py` — RESTRICTED_DATABASE_ACCESS.

## 9. Restricted files

`Sources/db_access_templates/` (all 3 files) — contain database access/credential-related content (keyword scan found `password`, `host`, `user`, `connection` references; exact values not opened or printed). Remain under `Sources/db_access_templates/` per instructions, pending technical review. Not copied to any documentation or skills folder.

## 10. Files moved
**NONE.** All original files remain in their original locations under `Sources/`.

## 11. Files deleted
**NONE.**

## 12. .mcp.json changed
**NO.** Confirmed unchanged — checksum `69c55f9bafa405570a950550915ecb79b11266b52018b2e64f67c34118c3ff22` recorded before and after this task, no modification made. Only top-level key names were read; no values were printed.

## 13. Credentials exposed
**NO.**
- `db_access_templates/*.py` files were scanned for keyword *counts* only (`password`, `host`, `user`, `token`, `connection`, `secret`); no matching lines or values were printed or copied anywhere.
- `db_access_templates/temp_user_access_report.pdf` was not opened.
- `.mcp.json` values were not read or printed — only its top-level JSON key names.

## 14. Database actions
**NONE.** No PostgreSQL connection, query, or inspection was performed at any point in this task.

## 15. Git status (before and after)

**Before:**
```
git status        → fatal: not a git repository (or any of the parent directories): .git
git branch --show-current → fatal: not a git repository (or any of the parent directories): .git
git remote -v      → fatal: not a git repository (or any of the parent directories): .git
```

**After:** Unchanged — still not a git repository. Same three commands return the same result.

## 16. Addendum — 2026-07-17 — Requirement documentation (REQ-AMZ-NMP-001-D01)

- **Requirement file created:** `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` (status: REQUIREMENT_DRAFT).
- **README updated:** `README.md` — Purpose, Business Question, Approved Scope, Current Sources, Database Access Method, Expected Output, Reviewers, Current Status, Safety Rules, Next Step, and Known Limitations placeholders filled/refreshed; no valid existing material overwritten.
- **Skill conflict:** remains **AMBER** — `Sources/skills 3 (1) (3).zip` and `Sources/skills_minimal_pack 2 (2).zip` were not selected, merged, or copied as canonical during this task.
- **Files moved:** NONE.
- **Files deleted:** NONE.
- **Database actions:** NONE — no PostgreSQL inspection performed.
- **Credentials exposed:** NONE — `.mcp.json` and `db_access_templates/` were not opened or read during this task.
