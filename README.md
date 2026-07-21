# Amazon - No-Moving Products - Issue Diagnosis & Action Report

## Project identity

- **Project name:** Nivarnan - Amazon - No-Moving Products - Issue Diagnosis & Action Report
- **Project code:** ANPIA
- **Requirement / deliverable:** REQ-01-D02
- **Business owner / assigned user:** Nivarnan
- **Developer:** Satheskanth
- **GitHub repository:** `https://github.com/technicaldigitweb-dev/Nivarnan---Amazon---No-Moving-Products---Issue-Diagnosis-Action-Report.git`

## Business purpose

Generate a daily Amazon report (accounts LEDSONE and DCVoltage; marketplaces UK, Germany,
France, Italy) showing PPC spend, sales, and current stock per Amazon Account + Marketplace +
ASIN + resolved SKU, to support diagnosis and action on no-moving/attention-worthy products.
Full corrected written requirement: `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md`
§2A and `01_REQUIREMENTS/2026-07-20_satheskanth_REQ-ANPIA_REQ-01-D02.md`.

## Production report purpose and active output

One self-contained HTML report, per Amazon Account + Marketplace + ASIN + resolved SKU, showing
the 15 confirmed blue columns (ASIN, SKU, Product Title, Days Since Last Sale, Units in Stock,
Sessions, Page Views, Units Ordered, Conversion Rate, CTR, Buy Box %, Price, Category Avg Price,
PPC Spend, ACOS), filterable by account/marketplace/7-14-30-day period, with a mandatory
live-stock disclosure.

- **Active production output:** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`
  (SHA-256 `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`)
- **Prior version (preserved, not active):** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html`
  (SHA-256 `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`)
- v002 fixed a user-reported row-density defect in the hosted view (real-browser-verified 15
  rows visible vs. v001's 4-8) via spacing-only CSS changes, never font-size.

## Source-data scope

Amazon only; accounts LEDSONE + DCVoltage; marketplaces UK/Germany/France/Italy; current stock
(UK -> UK warehouse, Germany/France/Italy -> shared German warehouse); ASIN-to-SKU mapping (row
key = account+marketplace+ASIN+resolved SKU, all valid combinations shown, no Top-N/percentile/
spend cutoff). Full scope detail in
`01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` §2A and
`03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`.

## 7/14/30-day reporting architecture

The report supports 7, 14, and 30 complete-day period views (sales/PPC aggregated over the
selected window; stock is always the current live snapshot, not historical). See
`04_DESIGN/2026-07-20__common_daily_dataset_design.md` for the extraction/aggregation design and
`05_IMPLEMENTATION/src/anpia_period_aggregation.py` for the implementation.

## Production Connection Model

- Source-data reads use protected PostgreSQL credentials (`ANPIA_DB_*` via
  `05_IMPLEMENTATION/src/anpia_config.py`), never MCP.
- Final HTML publication uses the same protected credential configuration -- also never MCP.
- `tech_team_outputs.ph_task` is the only production output table; the production pipeline
  contains no `daily_task` code path at all.
- MCP is not a production runtime dependency (see "Database access method" below for what MCP
  *was* used for, and why that is historical/interactive, not production).
- Automation is built but remains inactive pending VM access.

## ph_task publication result (production pipeline output)

Published to `tech_team_outputs.ph_task` row **id=399** -- updated in place from v001 to v002
(`version_level` 1 -> 2, `version_status='released'`), `project_code=ANPIA`,
`assigned_user=Nivarnan`. Exactly one same-day ANPIA row confirmed before and after the write.
This is the **only** production output table -- the write was performed with credential-based
PostgreSQL connections (`publish_ph_task_production_report.py` / `anpia_daily_pipeline.py`), not
MCP. Evidence: `07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json`,
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`.

## daily_task record (separate developer daily-work record -- NOT part of production)

`daily_task.tbl_anpia_satheskanth` is a **separate developer daily-work-record tool**, entirely
outside the ANPIA production pipeline: no production dependency, no scheduler dependency, no
source-data dependency, no ph_task publication dependency, and no future automatic execution.
`update_daily_task_anpia.py` is never called by `anpia_daily_pipeline.py`, `update_to_table.py`,
or any deployment file. Today's row: `daily_task.tbl_anpia_satheskanth` id=2
(`work_date=2026-07-20`, `developer=Satheskanth`, `project_code=ANPIA`, `requirement_id=REQ-01`,
`deliverable_id=D02`, `aios_phase=DEPLOY`, `status=COMPLETE`), written via a direct interactive
MCP tool call in an earlier session, not by any script. One matching row confirmed before/after.
Evidence: `07_EVIDENCE/publication/2026-07-20_anpia_daily_task_manifest.json`,
`07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`.

## Manual "update to table" command

A reusable, dry-run-safe, safety-gated pipeline for republishing the report on demand:

- `05_IMPLEMENTATION/anpia_daily_pipeline.py` -- full 16-step pipeline (lock, fresh extraction,
  build, validate, publish, evidence, structured log)
- `05_IMPLEMENTATION/update_to_table.py` + `08_SKILLS/anpia-update-to-table/SKILL.md` -- the
  documented manual command and its usage pattern
- Safe default: no arguments or `--dry-run` never writes to the database. Publishing requires
  both `--publish` and a confirmation token.

## Future automation design and status

**`AUTOMATION_BUILT_NOT_ACTIVATED`.** A full deployment package targeting a daily 12:00 PM
Asia/Colombo run exists in `05_IMPLEMENTATION/deployment/` (systemd service + timer preferred,
cron fallback, install/remove/check scripts) but has **not** been installed, enabled, or started
on any machine.

**Reason:** VM access has not yet been provided. Deployment prerequisite: a target VM, a
dedicated non-root service account, the real deployment path, and a protected `.env` file on
that VM (never committed -- see `.env.example` for the required variable names only). Full
detail: `05_IMPLEMENTATION/deployment/README.md`.

## Evidence, validation, and handover locations

- Evidence index: `07_EVIDENCE/EVIDENCE_INDEX.md`
- Validation index: `06_VALIDATION/VALIDATION_INDEX.md`
- **Final system handover (single continuation document):** `10_HANDOVER/2026-07-20__anpia_final_system_handover.md`
- Earlier project-delivery handover (superseded by the above for continuation purposes, kept as
  audit trail): `10_HANDOVER/2026-07-20__anpia_final_project_handover.md`
- Start-here (queryable project entry point): `00_PROJECT_CONTROL/START-HERE.md`

## Database access method

**The production runtime -- `anpia_daily_pipeline.py`, `publish_ph_task_production_report.py`,
`update_to_table.py`, and the scheduled-automation package -- has zero MCP dependency.** All
source-data reads and the `ph_task` publication write use only credential-based PostgreSQL
connections, loaded exclusively through `05_IMPLEMENTATION/src/anpia_config.py`
(`get_db_config()` / `safe_db_metadata()`) -- environment-only, no hardcoded fallback, fails
closed when configuration is incomplete. Confirmed directly from code: no MCP import, no MCP
command, no MCP URL, and no Claude Code tool dependency exist anywhere in these files (see
`06_VALIDATION/2026-07-20__anpia_final_production_architecture_validation.md`).

Separately, **the approved PostgreSQL MCP connection** (`mcp__claude_ai_postgres__*`) was used
during development for interactive, one-off Claude Code session work -- live discovery,
validation reads, and (for the `daily_task` row specifically) a guarded write performed directly
via MCP tool calls in-session, not by any pipeline script. This is historical evidence of how
*administrative/session* work was done; it does **not** represent, and is never invoked by, the
production runtime architecture described above.

`.mcp.json` documents two configured MCP servers (`ledsone-docs`, `ledsone-db`); this project's
own `mcp__claude_ai_postgres__*` connection is provided by the runtime environment, not by
`.mcp.json`. `.mcp.json` itself is not modified as part of routine project work and is not
tracked in Git (local tooling configuration).

## Current sources

`Sources/` is the preserved original intake location (not tracked in Git -- see `.gitignore`).
Approved, non-sensitive assets have been mapped/copied (with checksum verification) into the
governed AIOS structure -- see `02_SOURCE/2026-07-17__source_register.md` for the full mapping:

- `00_PROJECT_CONTROL/source_references/` -- AIOS project instructions, `aios_architecture.md`
- `02_SOURCE/requirements/` -- Nivarnan requirement workbook (authoritative requirement source)
- `08_SKILLS/database/` -- database routing reference workbook
- `08_SKILLS/ph_task_reference/` -- approved ph_task schema/versioning/team reference

`Sources/skills 3 (1) (3).zip` and `Sources/skills_minimal_pack 2 (2).zip` remain **unresolved
(AMBER)** -- conflicting overlapping content, neither selected as canonical.

**`Sources/db_access_templates/`** (`temp_user.py`, `update_table.py`,
`temp_user_access_report.pdf`) is a **protected, security-restricted** location as of 2026-07-20
-- a pre-Git secret scan found real database credentials in these files. They are not modified,
not executed, and not imported by any implementation code. See
`00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md` and
`11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`.

## Reviewers

- Coordinator: Sathees or assigned coordinator
- Technical reviewer: Sajeesan or assigned senior developer
- Queryability reviewer: Tamil Selvan or assigned reviewer
- Business validator: Nivarnan or assigned Amazon business owner

## Known limitations

- Current stock is a live snapshot, not historical stock (mandatory disclosure included in the
  report).
- Sessions, Page Views, Buy Box %, Conversion Rate, and Click-Through Rate have no single
  confidently-complete live source (see `07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md`).
- The real hosted-modal container dimensions remain unconfirmed -- the v002 row-density fix rests
  on a disclosed, calibrated browser simulation, not a direct measurement of the real hosted
  tool.
- A documented company-default convention for `ph_task` versioning (insert-new + reject-old) was
  found to conflict with the update-in-place approach actually used for row 399 -- flagged for
  owner review, not silently resolved (`08_SKILLS/ph_task_reference/ph_task_versioning_rules.md`).
- `daily_task.tbl_anpia_satheskanth` mapping conventions (`aios_phase` value, `deliverable_id`
  format, `developer` casing) differ slightly from the one 2026-07-17 precedent row -- flagged
  for owner standardization, not a functional blocker.
- Credential rotation for the exposed database password is **required, not yet confirmed** --
  see `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`. The credential never reached
  Git history (caught by the pre-commit secret scan).
- VM access is required before automation can be installed or activated.

## Safety rules

- No database credentials are to be stored in this repository or in any file under version
  control (`.env` is git-ignored; `.env.example` contains variable names only).
- No source files under `Sources/` are to be moved, renamed, deleted, or modified without
  explicit approval.
- `.mcp.json` is not to be modified as part of routine project work.
- No database write actions without explicit approval; no table, schema, view, function, index,
  trigger, or constraint creation.
- No business-rule creation (e.g. thresholds) without business validation.
- No credential exposure; no work outside the project root; no parent-AIOS promotion without
  explicit review.
- Automation must not be installed, enabled, or started without explicit VM-deployment approval.

## Safe next step

Deploy to the approved VM and enable the tested systemd timer only after (1) VM access is
granted, (2) the deployment placeholders in
`05_IMPLEMENTATION/deployment/systemd/anpia-daily.service` are replaced with real values, and
(3) technical and coordinator approval is given. In parallel, route the open AMBER items above
(credential rotation, ph_task versioning convention, daily_task mapping standardization, skill
ZIP sign-off) to their respective owners.
