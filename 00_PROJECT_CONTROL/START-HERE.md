# START HERE -- ANPIA

**For:** a new developer or a clean LLM session picking up this project cold.
**Read `README.md` first for full context** -- this document is a short map, not a duplicate.

## What this project does

Generates a daily self-contained HTML report for Amazon accounts LEDSONE and DCVoltage (UK,
Germany, France, Italy marketplaces), showing PPC spend, sales, and current stock per
Account + Marketplace + ASIN + resolved SKU, to support diagnosis and action on no-moving
products. Business owner: Nivarnan. Project code: `ANPIA`. Requirement: `REQ-01-D02`.

## What was delivered (2026-07-20)

1. A validated, self-contained production HTML report.
2. Publication of that report to `tech_team_outputs.ph_task`.
3. A daily work-log row in `daily_task.tbl_anpia_satheskanth`.
4. A manual, safety-gated "update to table" pipeline.
5. A disabled (not installed) daily automation package.
6. This Git repository, initialized and pushed after a pre-push secret scan and remediation.

## Which file is the active production report

`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`
(SHA-256 `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`)

v001 in the same folder is the immediately prior version, preserved unchanged, not active.

## What was published to ph_task

`tech_team_outputs.ph_task` row `id=399`, updated in place to v002 (`version_level=2`,
`version_status='released'`). Detail: `07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`.

## What was recorded in daily_task

`daily_task.tbl_anpia_satheskanth` row `id=2` (2026-07-20, Satheskanth, ANPIA, REQ-01, D02,
DEPLOY, COMPLETE). Detail: `07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`.

## How "update to table" works

`05_IMPLEMENTATION/update_to_table.py` (see `08_SKILLS/anpia-update-to-table/SKILL.md` for the
exact command and usage pattern) drives `05_IMPLEMENTATION/anpia_daily_pipeline.py` -- a 16-step,
lock-protected pipeline: fresh extraction, build, validate, publish (guarded), evidence, log.
Default is dry-run; publishing requires an explicit flag plus confirmation token.

## Where validation evidence exists

- `06_VALIDATION/VALIDATION_INDEX.md` -- grouped index of every validation report
- `07_EVIDENCE/EVIDENCE_INDEX.md` -- grouped index of every evidence file

## What automation files exist, and why automation is inactive

Full systemd/cron deployment package in `05_IMPLEMENTATION/deployment/` (service, timer,
install/remove/check scripts, cron fallback). Status: `AUTOMATION_BUILT_NOT_ACTIVATED`. Reason:
VM access has not yet been provided -- nothing has been installed, enabled, or started on any
machine. See `05_IMPLEMENTATION/deployment/README.md`.

## What is needed after VM access

1. A dedicated non-root service account, the real deployment path, and Python interpreter path.
2. A protected `.env` on that VM (never committed) populated from `.env.example`'s variable
   names.
3. Run `./install_anpia_timer.sh` and `./check_anpia_timer.sh`, then a deliberate, separate
   `systemctl enable --now anpia-daily.timer` step -- only after technical and coordinator
   approval.

## What must not be changed

- `09_OUTPUTS/html/production/*.html` -- both versions, checksums are the integrity proof.
- `Sources/` and anything under it, especially `Sources/db_access_templates/` (protected,
  security-restricted -- see `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`).
- `tech_team_outputs.ph_task` row 399 and `daily_task.tbl_anpia_satheskanth` row 2, except via
  the guarded pipelines that produced them.
- `.env` (never commit; git-ignored by design).
- The disabled state of the automation package, until VM access and approval both exist.

## Known open items (not blockers to the delivered benefit)

See README.md "Known limitations" and the final handover for the full list --- in short:
credential rotation not yet confirmed, ph_task versioning-convention conflict, daily_task
mapping-convention standardization, real hosted-modal dimensions unconfirmed, VM access pending.

## Full handover

`10_HANDOVER/2026-07-20__anpia_final_project_handover.md`
