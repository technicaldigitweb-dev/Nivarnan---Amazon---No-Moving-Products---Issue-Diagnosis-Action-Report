# Validation: ANPIA Final Production Architecture (Verification Only)

**Date:** 2026-07-20
**Status:** PASS
**Scope:** Verification of the already-completed system against its documented architecture.
No rebuild, no new data fetch, no database write. Database writes performed by this
validation: **ZERO**.

## Files inspected

- `05_IMPLEMENTATION/anpia_daily_pipeline.py`
- `05_IMPLEMENTATION/update_to_table.py`
- `05_IMPLEMENTATION/src/anpia_config.py`
- `05_IMPLEMENTATION/publish_ph_task_production_report.py`
- `05_IMPLEMENTATION/deployment/run_anpia_daily.sh`
- `05_IMPLEMENTATION/deployment/systemd/anpia-daily.service`
- `05_IMPLEMENTATION/deployment/systemd/anpia-daily.timer`
- `05_IMPLEMENTATION/deployment/README.md`
- `05_IMPLEMENTATION/update_daily_task_anpia.py`

## Source-data connection proof

`anpia_daily_pipeline.py` loads connection configuration via
`from anpia_config import get_db_config` (lines 522-523, 634-635, 814-815) and connects with
`psycopg2.connect(**cfg)` / `anpia_db_connection.get_connection()` (lines 644-646, 816).
`get_db_config()` (`05_IMPLEMENTATION/src/anpia_config.py`) reads `ANPIA_DB_*` exclusively from
environment variables / a local `.env` file -- no hardcoded fallback, raises `RuntimeError`
naming the missing variable(s) when incomplete. **Confirmed: credential-based, environment-only.**

## Publication connection proof

`publish_ph_task_production_report.py` uses the identical pattern: `from anpia_config import
get_db_config` (lines 123-124, 161, 163), `psycopg2.connect(**cfg)` (line 165). The write path
(`build_update_sql_and_params()` / `build_insert_sql_and_params()`, both parameterized) targets
only `tech_team_outputs.ph_task`. **Confirmed: credential-based, same source as the read path.**

## Production table proof

`grep -n "TARGET_SCHEMA\|TARGET_TABLE"` on both `anpia_daily_pipeline.py` and
`publish_ph_task_production_report.py` returns `TARGET_SCHEMA = "tech_team_outputs"` /
`TARGET_TABLE = "ph_task"` in both files. Every `INSERT`/`UPDATE`/`SELECT` statement in either
file targets `tech_team_outputs.ph_task` only -- confirmed by direct grep of every SQL statement
in both files. **No other table is written by the production pipeline.**

## MCP dependency scan

`grep -ni "mcp"` across `anpia_daily_pipeline.py`, `publish_ph_task_production_report.py`, and
`update_to_table.py`: **0 matches.** No MCP import, no MCP command, no MCP URL, no Claude Code
tool dependency exists in any of these three files, nor in the deployment package
(`run_anpia_daily.sh`, `anpia-daily.service`, `anpia-daily.timer`). **Confirmed: zero MCP
production dependency.**

Historical evidence in this project's `07_EVIDENCE/` and `11_REVIEW/` directories does document
interactive, one-off MCP tool usage during development (live discovery, validation reads, and the
`daily_task` row insert). This is disclosed as historical/interactive-session activity, not as
part of the production runtime -- see the corrected "Database access method" section in
`README.md` and the equivalent section in `05_IMPLEMENTATION/deployment/README.md`.

## daily_task dependency scan

`grep -ni "daily_task\|update_daily_task_anpia"` across `anpia_daily_pipeline.py`,
`publish_ph_task_production_report.py`, and `update_to_table.py`: **0 matches.**
`05_IMPLEMENTATION/update_daily_task_anpia.py` exists as a standalone script and is never
imported or subprocess-called by any production file. **Confirmed:
`daily_task.tbl_anpia_satheskanth` is entirely outside the production pipeline** -- classified
`SEPARATE_DAILY_WORK_RECORD_TOOL`: purpose is a developer daily completion record; no production
dependency; no scheduler dependency; no source-data dependency; no ph_task publication
dependency; no future automatic execution. It is not deleted, not called, and not included in
any production flow description as part of this validation.

## Missing-config fail-closed result

Re-confirmed from `05_IMPLEMENTATION/src/anpia_config.py`: `get_db_config()` raises
`RuntimeError` naming every missing `ANPIA_DB_*` variable when configuration is incomplete, with
no hardcoded fallback value anywhere in the function. This was functionally tested (isolated
temp directory, environment stripped of `ANPIA_DB_*`) during the prior security-remediation task
(`06_VALIDATION/2026-07-20__anpia_secure_configuration_validation.md`, test #5) and re-confirmed
by direct code inspection in this validation -- unchanged since that test.

## Hardcoded-secret scan

An exact-value scan (the same two known real credential literals used throughout this project's
prior remediation evidence, not reproduced here) across `anpia_daily_pipeline.py`,
`publish_ph_task_production_report.py`, `prepare_ph_task_v007_upload.py`, and
`anpia_config.py`: **0 matches.** Consistent with the prior remediation
(`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`) -- confirmed
unchanged, no regression.

## Production checksum verification

| File | Expected SHA-256 | Actual SHA-256 (this validation) | Match |
|---|---|---|---|
| `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` | `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` | `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` | YES |
| `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html` | `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2` | `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2` | YES |

Neither file was modified by this task.

## Publication evidence re-read (existing evidence only, no new database read)

`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md` confirms: `ph_task`
row id=399; `project_code=ANPIA`; `assigned_user=Nivarnan`; v001 was the first published
version (row inserted originally, confirmed elsewhere in this project's evidence trail); row 399
was then updated in place to v002 (`version_level` 1->2); same-day ANPIA row count = 1 both
before and after (`284 -> 284` total `ph_task` rows, confirming an UPDATE not an INSERT); stored
`html_content` SHA-256 recomputed independently post-commit matched the v002 source file exactly.
**No new database read was required or performed** -- existing evidence was sufficient.

## Automation completion result

All required assets present in `05_IMPLEMENTATION/deployment/`: `run_anpia_daily.sh`,
`systemd/anpia-daily.service`, `systemd/anpia-daily.timer`, `install_anpia_timer.sh`,
`remove_anpia_timer.sh`, `check_anpia_timer.sh`, `cron/anpia_daily.cron.example`, `README.md`.
Confirmed present in the pipeline itself: file lock + PostgreSQL advisory lock
(`acquire_pg_advisory_lock`), no-auto-retry policy (`Restart=no` in the service unit, deliberate),
deterministic exit codes (`EXIT_SUCCESS=0` through `EXIT_LOCK_ALREADY_HELD=7`), secret-safe
logging (structured JSON run log, no credential fields), post-commit publication verification
(reread inside the same transaction before commit), and idempotent same-day handling
(`idempotent_rerun_check` step). Configured schedule: `OnCalendar=*-*-* 12:00:00 Asia/Colombo`
in `anpia-daily.timer`, `RandomizedDelaySec=0`, `Persistent=true`.

## Scheduler inactive result

Checked directly on this workstation: no `crontab` command available (Windows dev machine,
expected), no `systemctl`/systemd present, and no Windows Scheduled Task matching "anpia" exists
(`schtasks /query` filtered for "anpia" -- zero matches). `AUTOMATION_BUILT_NOT_ACTIVATED`
confirmed. No installation script was run during this validation.

## Database writes during this validation

**ZERO.** All checks in this document were performed via static code inspection (`grep`,
direct file reads), local checksum recomputation (`sha256sum`), local scheduler-state checks
(`crontab`/`schtasks`), and reading of pre-existing evidence files. No database connection was
opened, no MCP tool was called, and no credential-based connection script was executed.

## Conclusion

**PASS.** The completed implementation matches the confirmed production architecture exactly:
credential-based source-data reads, credential-based `ph_task` publication, `tech_team_outputs.ph_task`
as the sole production output table, zero MCP dependency, zero `daily_task` dependency,
fail-closed configuration, no hardcoded secrets, unchanged production checksums, a complete and
verified automation package that remains correctly inactive. No rebuild was performed or
required.
