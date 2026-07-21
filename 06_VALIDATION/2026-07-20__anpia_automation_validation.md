# Validation: ANPIA Daily Automation (Built, Not Activated)

**Status: `AUTOMATION_BUILT_NOT_ACTIVATED`.**

## 1. Components built

| Component | Path | Status |
|---|---|---|
| Central pipeline | `05_IMPLEMENTATION/anpia_daily_pipeline.py` | Built, real dry-run executed successfully |
| Manual command wrapper | `05_IMPLEMENTATION/update_to_table.py` | Built, real dry-run executed successfully |
| Operator skill | `08_SKILLS/anpia-update-to-table/SKILL.md` | Written |
| systemd service | `05_IMPLEMENTATION/deployment/systemd/anpia-daily.service` | Written, syntax valid (`bash -n` N/A -- INI format; content reviewed) |
| systemd timer | `05_IMPLEMENTATION/deployment/systemd/anpia-daily.timer` | Written -- `OnCalendar=*-*-* 12:00:00 Asia/Colombo` |
| Install/remove/check scripts | `05_IMPLEMENTATION/deployment/{install,remove,check}_anpia_timer.sh` | Written, `bash -n` PASS on all three |
| Daily entry point | `05_IMPLEMENTATION/deployment/run_anpia_daily.sh` | Written, `bash -n` PASS |
| Cron fallback (reference only, not installed) | `05_IMPLEMENTATION/deployment/cron/anpia_daily.cron.example` | Written |
| Deployment guide | `05_IMPLEMENTATION/deployment/README.md` | Written |

## 2. Static validation performed

- **Python syntax:** `python -m py_compile` PASS on `anpia_daily_pipeline.py` and `update_to_table.py`.
- **Shell syntax:** `bash -n` PASS on all four `.sh` files.
- **systemd unit verification:** `systemd-analyze` / `systemctl` are **not available on this
  development machine** (Windows) -- this is disclosed as AMBER, exactly as anticipated by this
  task's own instructions ("Return AMBER when: ... systemd-analyze is unavailable locally"). The
  unit files were instead validated by manual review against the systemd unit-file spec and by the
  explicit requirements list in this task (dedicated non-root user, explicit `WorkingDirectory`,
  explicit `EnvironmentFile`, `TimeoutStartSec`, `Restart=no`, hardening directives). `check_anpia_timer.sh`
  is provided specifically so a future operator can run the real `systemd-analyze verify` /
  `systemd-analyze calendar` checks on the actual target VM before activation.
- **Simulated schedule calculation:** computed independently in Python (not copied from the unit
  file) that 12:00 Asia/Colombo (UTC+05:30, no DST) is a constant 06:30 UTC year-round:

  | Date | Asia/Colombo 12:00 | UTC equivalent |
  |---|---|---|
  | 2026-01-15 | 12:00 | 06:30 |
  | 2026-07-20 | 12:00 | 06:30 |
  | 2026-12-25 | 12:00 | 06:30 |

  Confirms no DST-related drift risk for this specific timezone -- the `OnCalendar=` spec's behavior
  is safe to reason about without seasonal caveats.
- **Real, executed dry-run** of the full pipeline (not just static checks) -- see
  `07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md`.
- **Real, executed dry-run** of the `update_to_table.py` command wrapper -- see
  `07_EVIDENCE/validation/2026-07-20__anpia_update_to_table_command_evidence.md`.

## 3. Automation safety requirements (Section 13) -- implementation mapping

| Requirement | Implementation |
|---|---|
| File lock or PostgreSQL advisory lock | Both: `PipelineLock` (file, primary) + `acquire_pg_advisory_lock()` (defense in depth) |
| Maximum one concurrent run | File lock uses `os.O_CREAT \| os.O_EXCL` -- a second run gets `FileExistsError` and exits 7 |
| No retry after validation failure | `anpia-daily.service` sets `Restart=no`; the pipeline itself does not loop or retry on any validation-step failure |
| Transaction rollback on publication failure | `except Exception: wconn.rollback()` wraps the entire write block in both `publish_ph_task_production_report.py` and the pipeline's inline write path |
| Idempotent same-day behaviour | `idempotent_rerun_check` step -- a `scheduled` trigger on an already-published day defaults to no-op |
| One active same-day row | Enforced by the live ANPIA-only duplicate check before every write; `BLOCKED_MULTIPLE_ROWS` if more than one is ever found |
| Local version history preservation | `write_local_html` refuses to overwrite an existing local file (`LOCAL_FILE_ALREADY_EXISTS`) rather than silently replacing it |
| Structured JSON run log | `RunLog` class -- one JSON file per run under `09_OUTPUTS/logs/anpia_daily_runs/` |
| Clear success/failure exit codes | 0/2/3/4/5/6/7, documented in the pipeline's own docstring and this task's return format |
| Log rotation guidance | Documented in `05_IMPLEMENTATION/deployment/README.md` (journald + logrotate, not automated by this task) |
| Disk-space check | **Not implemented** -- disclosed gap, see Section 5 below |
| HTML size check | `SIZE_SANITY_CEILING_BYTES = 50_000_000`, enforced before any write |
| Checksum check | SHA-256 computed and compared at every step where the HTML is validated or published |
| Secret scan | `scan_forbidden_patterns()`, run before every write |
| Source freshness check | `latest_complete_date()` queried live every run -- never cached or assumed |
| Stale traffic disclosure without blocking unaffected metrics | Preserved unchanged from the existing 4-tier N/A classification (REAL/TRUE_ZERO/OUTSIDE_COVERAGE/NO_MATCH) -- traffic staleness never blocks sales/PPC/stock metrics |
| No partial publication | Single transaction per write; `RETURNING` + rowcount check + reread-before-commit; any exception rolls back the whole transaction |
| No `daily_task` writes | Zero references to `daily_task` anywhere in the pipeline, the wrapper, or the deployment scripts (confirmed by code review) |

## 4. Versioning-rule mapping (Section 14)

Implemented in `determine_version()`: zero existing rows -> `SAFE_NEW_INSERT` / `FIRST_DAILY_RUN`;
exactly one existing row -> `UPDATE_EXISTING_ROW` / `MANUAL_REPUBLISH` (or a caller-supplied
`--version-reason`); more than one existing row -> `BLOCKED_MULTIPLE_ROWS` (refuses to guess). The
`idempotent_rerun_check` step specifically prevents a `scheduled` trigger from creating unlimited
versions on repeated timer firings when no correction is needed.

## 5. Known gap (disclosed, not silently omitted)

**Disk-space check is not implemented.** The pipeline does not currently verify free disk space
before writing the ~4MB HTML output or the ~70-110MB intermediate extraction/compact-dataset files.
On a VM with very limited free space this could fail mid-write. Recommended follow-up: add a
`shutil.disk_usage()` check (e.g. require >=500MB free) as an early pipeline step, failing fast with
exit code 4 rather than partway through a run.

## 6. Conclusion

All required automation components are built and pass every static/simulated check available on this
development machine, plus two real, successfully-completed dry-run executions (pipeline and wrapper).
Nothing has been installed, enabled, started, or scheduled anywhere -- `AUTOMATION_BUILT_NOT_ACTIVATED`
is the accurate, final status for this task.
