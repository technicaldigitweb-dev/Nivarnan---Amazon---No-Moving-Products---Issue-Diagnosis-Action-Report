# START HERE -- ANPIA

**For:** a new developer or a clean LLM session picking up this project cold.
**Read `README.md` first for full context** -- this document is a short map, not a duplicate.

**No further local build work is required. The next operational task begins only after VM
access is provided.** See the final system handover for full detail:
`10_HANDOVER/2026-07-20__anpia_final_system_handover.md`.

## What this project does

Generates a daily self-contained HTML report for Amazon accounts LEDSONE and DCVoltage (UK,
Germany, France, Italy marketplaces), showing PPC spend, sales, and current stock per
Account + Marketplace + ASIN + resolved SKU, to support diagnosis and action on no-moving
products. Business owner: Nivarnan. Developer: Satheskanth. Project code: `ANPIA`. Requirement:
`REQ-01-D02`.

## What was delivered (2026-07-20) -- SYSTEM_COMPLETED

1. A validated, self-contained production HTML report.
2. Publication of that report to `tech_team_outputs.ph_task` (the only production output table).
3. A manual, safety-gated "update to table" command that runs the same production pipeline.
4. A disabled (not installed) daily automation package, targeting 12:00 PM Asia/Colombo.
5. This Git repository, initialized and pushed after a pre-push secret scan and remediation.
6. Separately (not part of production): a daily developer work-log row in
   `daily_task.tbl_anpia_satheskanth` -- see "daily_task is separate" below.

## The central pipeline and how "update to table" works

`05_IMPLEMENTATION/anpia_daily_pipeline.py` is the single production pipeline: fresh extraction,
build, validate, publish (guarded), evidence, structured log -- credential-based PostgreSQL
connections only, no MCP dependency anywhere in this file.
`05_IMPLEMENTATION/update_to_table.py` (see `08_SKILLS/anpia-update-to-table/SKILL.md` for the
exact command) is a thin, fixed-argument wrapper that invokes this same pipeline -- it is not a
separate implementation. Default is dry-run; publishing requires an explicit flag plus
confirmation token.

## Which file is the active production report

`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`
(SHA-256 `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`)

v001 in the same folder is the immediately prior version, preserved unchanged, not active.

## What was published to ph_task

`tech_team_outputs.ph_task` row `id=399`, updated in place to v002 (`version_level=2`,
`version_status='released'`), via credential-based PostgreSQL connection (not MCP). Detail:
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`.

## daily_task is separate -- not part of production

`daily_task.tbl_anpia_satheskanth` is a **separate developer daily-work-record tool**: no
production dependency, no scheduler dependency, no source-data dependency, no ph_task
publication dependency, no future automatic execution. `update_daily_task_anpia.py` is never
called by the production pipeline or any deployment file. Today's row: id=2 (2026-07-20,
Satheskanth, ANPIA, REQ-01, D02, DEPLOY, COMPLETE), written via a direct interactive MCP tool
call in an earlier session -- not by any pipeline script. Detail:
`07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`.

## The scheduler deployment package, and why automation is inactive

Full systemd/cron deployment package in `05_IMPLEMENTATION/deployment/` (service, timer,
install/remove/check scripts, cron fallback) -- credential-based only, zero MCP dependency.
Status: `AUTOMATION_BUILT_NOT_ACTIVATED`. Reason: VM access has not yet been provided -- nothing
has been installed, enabled, or started on any machine. See
`05_IMPLEMENTATION/deployment/README.md`.

## What is needed after VM access

1. A dedicated non-root service account, the real deployment path, and Python interpreter path.
2. A protected `.env` on that VM (never committed) populated from `.env.example`'s variable
   names.
3. Run `./install_anpia_timer.sh` and `./check_anpia_timer.sh`, then a deliberate, separate
   `systemctl enable --now anpia-daily.timer` step -- only after technical and coordinator
   approval.

## Where validation evidence exists

- `06_VALIDATION/VALIDATION_INDEX.md` -- grouped index of every validation report (includes
  `06_VALIDATION/2026-07-20__anpia_final_production_architecture_validation.md`, the
  code-level proof of the connection model described above)
- `07_EVIDENCE/EVIDENCE_INDEX.md` -- grouped index of every evidence file

## GitHub repository

`https://github.com/technicaldigitweb-dev/Nivarnan---Amazon---No-Moving-Products---Issue-Diagnosis-Action-Report.git`
(branch `main`)

## What must not be changed

- `09_OUTPUTS/html/production/*.html` -- both versions, checksums are the integrity proof.
- `Sources/` and anything under it, especially `Sources/db_access_templates/` (protected,
  security-restricted -- see `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`).
- `tech_team_outputs.ph_task` row 399 and `daily_task.tbl_anpia_satheskanth` row 2, except via
  the guarded tools that produced them.
- `.env` (never commit; git-ignored by design).
- The disabled state of the automation package, until VM access and approval both exist.

## Known open items (not blockers to the delivered benefit)

See the final system handover for the full list -- in short: credential rotation not yet
confirmed, ph_task versioning-convention conflict, daily_task mapping-convention
standardization, real hosted-modal dimensions unconfirmed, VM access pending.

## Full handover

`10_HANDOVER/2026-07-20__anpia_final_system_handover.md`
