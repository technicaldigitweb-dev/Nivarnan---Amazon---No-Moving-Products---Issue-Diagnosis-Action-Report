# Amazon - No-Moving Products - Issue Diagnosis & Action Report

## Project Name
Nivarnan - Amazon - No-Moving Products - Issue Diagnosis & Action Report

## Purpose
Generate a daily Amazon report (accounts LEDSONE and DCVoltage; marketplaces UK, Germany, France, Italy) showing PPC spend, sales, and current stock per Amazon Account + Marketplace + ASIN + resolved SKU, to support diagnosis and action on no-moving/attention-worthy products. **Scope corrected 2026-07-17** from an earlier UK-only, high-spend-filtered draft — see `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` §2A (REQ-AMZ-NMP-001-D01) for the full corrected written requirement; §2 is preserved as superseded audit trail.

## Business Question
Across LEDSONE and DCVoltage's UK, Germany, France, and Italy Amazon listings, what is each ASIN/SKU's PPC spend, recent sales, and current stock — viewed over 7, 14, or 30 complete days?

## Approved Scope
**Included:** Amazon only; accounts LEDSONE + DCVoltage; marketplaces UK/Germany/France/Italy; 7/14/30-complete-day period views; sales during the same period; current stock (UK→UK warehouse, Germany/France/Italy→shared German warehouse); ASIN-to-SKU mapping (row key = account+marketplace+ASIN+resolved SKU, all valid combinations shown, no Top-N/percentile/spend cutoff); account+marketplace+period filters; the 15 confirmed blue columns only; future HTML output; future ph_task publication after approval.

**Excluded:** eBay or Shopify; marketplaces beyond UK/Germany/France/Italy; historical stock reconstruction; PPC changes; stock changes; reorder-rule changes; threshold creation; schema/table/view changes; ph_task writes during discovery; full automation before validation; the 8 yellow columns (Category, Stock Age (Days), Root Cause, Recommended Action, Priority, Status, Owner, Last Reviewed) in any output.

Full scope detail in `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` §2A and `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`.

## Current Sources
- `Sources/Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx`
- `Sources/table_location_business_details 3.xlsx`
- `Sources/aios_architecture.md`
- `Sources/db_access_templates/` (temp_user.py, update_table.py, temp_user_access_report.pdf)
- `Sources/ph_task_reference/` (ph_task_assigned_user_team_rules.md, ph_task_schema.md, ph_task_versioning_rules.md)
- `Sources/AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip`
- `Sources/skills 3 (1) (3).zip`
- `Sources/skills_minimal_pack 2 (2).zip`

`Sources/` remains the preserved original intake location; nothing has been moved or deleted from it. Approved, non-sensitive assets have since been mapped/copied (with checksum verification) into the AIOS structure — see `02_SOURCE/2026-07-17__source_register.md` for the full mapping:

- `00_PROJECT_CONTROL/source_references/` — AIOS project instructions ZIP, `aios_architecture.md` (authoritative project control)
- `02_SOURCE/requirements/` — Nivarnan requirement workbook (authoritative requirement source)
- `08_SKILLS/database/` — `table_location_business_details 3.xlsx` (approved database routing reference)
- `08_SKILLS/ph_task_reference/` — approved ph_task schema/versioning/team reference

`Sources/skills 3 (1) (3).zip` and `Sources/skills_minimal_pack 2 (2).zip` remain **unresolved (AMBER)** — they contain conflicting overlapping content and neither has been selected, merged, or copied as canonical. `Sources/db_access_templates/` remains restricted (not opened beyond a keyword-count scan, not copied).

## Database Access Method
Two live PostgreSQL MCP connections are available: **primary** `mcp__claude_ai_postgres__*` (the AIOS/skills-related database — used for all report data; confirmed to be the database this project's routing workbook, skill files, and `ph_task` schema were written against) and **fallback** `.mcp.json`'s `mcp__ledsone-db__*` (a different, legitimate operational database — used only if a required field is proven missing from the primary; not needed so far). `.mcp.json` itself remains unchanged; no credential values have been read from either connection's configuration.

## Expected Output
One validated HTML report (`09_OUTPUTS/html/`) showing, per Amazon Account + Marketplace + ASIN + resolved SKU: the 15 confirmed blue columns (ASIN, SKU, Product Title, Days Since Last Sale, Units in Stock, Sessions, Page Views, Units Ordered, Conversion Rate, CTR, Buy Box %, Price, Category Avg Price, PPC Spend, ACOS), filterable by account/marketplace/7-14-30-day period, with a mandatory live-stock disclosure. Future publication to `tech_team_outputs.ph_task` only after technical validation, business approval, and verification of ph_task maintenance rules — no database publication is approved yet.

## Reviewers
- Coordinator: Sathees or assigned coordinator
- Technical reviewer: Sajeesan or assigned senior developer
- Queryability reviewer: Tamil Selvan or assigned reviewer
- Business validator: Nivarnan or assigned Amazon business owner

## Current Status
Scope corrected 2026-07-17 to multi-account (LEDSONE, DCVoltage) / multi-marketplace (UK, Germany, France, Italy) per two authoritative user-provided images. Discovery (`03_DISCOVERY/`) and design/implementation are in progress for REQ-AMZ-NMP-001-D01. 8 of 15 blue columns are fully source-verified; 2 have a documented interim default; 5 remain REVIEW_REQUIRED pending a technical decision on the traffic-data source (see `07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md`). `database_write_permission` and `production_change_permission` are **NOT APPROVED** — no ph_task publication will occur until ph_task metadata is explicitly approved.

## Safety Rules
- No database credentials are to be stored in this repository or in any file under version control.
- No source files are to be moved, renamed, deleted, or modified without explicit approval.
- `mcp.json` / `.mcp.json` is not to be modified as part of routine project work.
- No database write actions without explicit approval.
- Read-only discovery first; no production/database writes; no table, schema, view, or function creation.
- No `ph_task` insert or update without explicit approval; no ph_task writes during discovery.
- No business-rule creation (e.g. "high spend" definition) without business validation.
- No credential exposure; no work outside the project root; no parent-AIOS promotion.
- The two conflicting database skill ZIPs (`Sources/skills 3 (1) (3).zip`, `Sources/skills_minimal_pack 2 (2).zip`) must not be selected, merged, or copied as canonical without technical review.

## Next Step
Route the open questions in `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` §13 (ph_task metadata, stock-freshness threshold, Git decision, KPI, skill-ZIP sign-off, and the 3 field-source decisions) to Nivarnan/Sajeesan/coordinator; proceed with build/validation for all currently-sourced fields in the interim.

## Known Limitations
- Current stock is a live snapshot, not historical stock (mandatory disclosure included in the report).
- The two database skill ZIPs have unresolved version conflicts for files outside this requirement's scope (AMBER technical-review item); for the 3 files this requirement touches, live evidence favors `skills_minimal_pack 2 (2).zip`.
- Git is not initialized.
- Sessions, Page Views, Buy Box %, Conversion Rate, and Click-Through Rate have no single confidently-complete live source yet (see `07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md`) — shown as "N/A — pending source confirmation" in the v001 output.
- Category Avg Price's averaging population (marketplace-only / account+marketplace / global) is undecided.
- DCVoltage has no PPC/sales/listing presence in the France marketplace (confirmed zero rows) — renders as an empty combination, not an error.
- ph_task publication is blocked pending exact metadata approval (assigned_user, team, title format, project code, version status).
