# ANPIA Daily Automation -- Deployment Guide (NOT ACTIVATED)

**Status: `AUTOMATION_BUILT_NOT_ACTIVATED`.** Every file in this directory is built and statically
validated, but nothing has been installed, enabled, started, or added to any scheduler on any
machine. This document is the reference for a future deployment operator.

## What "12:00 PM Asia/Colombo" requires

Asia/Colombo is UTC+05:30 with no daylight-saving transitions, so the offset is constant year-round
-- but **do not assume the target VM's system clock/timezone is already set to Asia/Colombo.** Two
independent things must both be correct:

1. The scheduler's calendar spec must resolve to 12:00 in the *Asia/Colombo* zone specifically, not
   whatever the VM's local zone happens to be (see `check_anpia_timer.sh`).
2. `anpia_daily_pipeline.py` itself resolves "today" using a fixed `UTC+05:30` offset in Python
   (`TZ_OFFSET = datetime.timezone(datetime.timedelta(hours=5, minutes=30))`), independent of the
   host's OS timezone setting -- so even if the scheduler fires at the wrong wall-clock moment due to
   a timezone misconfiguration, the pipeline's own date resolution will not silently drift.

## Files in this directory

| File | Purpose |
|---|---|
| `run_anpia_daily.sh` | Entry point invoked by the service/cron job. Thin wrapper -- all real logic is in `anpia_daily_pipeline.py`. |
| `systemd/anpia-daily.service` | The preferred production mechanism -- oneshot service, runs as a dedicated non-root user, hardened (`ProtectSystem=strict`, `NoNewPrivileges=true`, etc.). |
| `systemd/anpia-daily.timer` | Fires the service daily at 12:00 Asia/Colombo, `Persistent=true` (catches up a missed run), `RandomizedDelaySec=0`. |
| `install_anpia_timer.sh` | Copies the unit files into `/etc/systemd/system/` and reloads systemd. **Does not enable or start** the timer -- that remains a separate, deliberate operator step. |
| `remove_anpia_timer.sh` | Cleanly disables, stops, and removes the unit files. |
| `check_anpia_timer.sh` | Read-only diagnostic -- verifies the calendar spec, checks unit-file syntax, reports current status. Safe to run any time. |
| `cron/anpia_daily.cron.example` | Fallback only, for environments without systemd. Not installed by any script here. |

## Required deployment-time decisions (deliberately left as placeholders)

The shipped files use `/opt/anpia`, user `anpia-svc`, and `/etc/anpia/.env` as illustrative
placeholders. Before running `install_anpia_timer.sh` on a real VM, the operator must confirm and
replace, in `systemd/anpia-daily.service`:

- `User=` / `Group=` -- a dedicated, non-root service account created for this purpose.
- `WorkingDirectory=` -- the real deployment path of this project on that VM.
- `EnvironmentFile=` / `ANPIA_ENV_FILE` -- the real, protected location of the `.env` credential
  file, with filesystem permissions restricting it to the service user only (`chmod 600`, owned by
  `anpia-svc`). **Never** commit this file to source control, and never place it anywhere web-served.
- `ANPIA_PYTHON_BIN` -- the real Python interpreter path (ideally inside a dedicated virtualenv with
  `psycopg2-binary` installed).

These are exactly the kind of details this task's own instructions flagged as expected to remain open
("the future VM path/user/environment details require deployment-time confirmation" -- AMBER, not a
failure).

## Installing (future operator, not part of this task)

```bash
sudo ./install_anpia_timer.sh      # copies unit files, requires typing "INSTALL" to confirm
./check_anpia_timer.sh             # verify the calendar spec and unit syntax before activating
sudo systemctl enable --now anpia-daily.timer   # <-- the actual activation step, separate and deliberate
```

## Removing

```bash
sudo ./remove_anpia_timer.sh
```

## Safety properties already built into the pipeline (not duplicated by the shell scripts)

- **Locking:** `anpia_daily_pipeline.py` acquires a file lock (`09_OUTPUTS/logs/anpia_daily_pipeline.lock`)
  plus a best-effort PostgreSQL advisory lock. A second concurrent invocation exits with code 7
  rather than running alongside the first.
- **No auto-retry after validation failure:** `anpia-daily.service` sets `Restart=no` deliberately --
  a failed run signals a real problem (data quality, connectivity, a rejected safety gate) that
  should surface to a human via the next day's manual review, not be silently retried.
- **Idempotent reruns:** a `scheduled`-trigger rerun on a day that already has a successful
  publication defaults to a no-op (see `anpia_daily_pipeline.py`'s `idempotent_rerun_check` step) --
  it does not spin up unlimited new versions from repeated timer firings.
- **One active row:** enforced by the pipeline's own live duplicate-state check before every write,
  not by any property of the scheduler.
- **`daily_task` is never referenced anywhere in this pipeline or its deployment files.**

## Connection model: MCP (interactive) vs. direct credentials (automation)

Two distinct database-connection mechanisms exist in this project and must not be conflated:

- **Approved PostgreSQL MCP connection** -- used for all interactive Claude Code work in this
  project (discovery, validation, reads, and guarded writes performed live in a session). This is
  the preferred method whenever an interactive agent session is doing the work, and the project's
  own working rule is: do not automatically fall back to direct credentials if the approved MCP
  cannot complete a required operation -- stop, report the exact limitation, and wait for explicit
  approval before using any credential fallback.
- **Direct runtime credentials** (`.env` / `ANPIA_DB_*` via `anpia_config.get_db_config()`) --
  used only by standalone automation (this deployment package) where no interactive MCP tool
  binding exists to call. A `systemd` timer or cron job runs a plain Python process with no access
  to any interactive session's MCP tools, so it has no alternative to a protected environment file.

This distinction is deliberate, not an inconsistency: interactive sessions prefer MCP; unattended
automation requires a protected local credential file. Keep the automation's runtime
configuration **disabled** (this package is not installed or enabled) until VM access and
technical approval both exist -- do not activate automation during any interim closure task.

## Log rotation guidance

`journald` (systemd path) rotates automatically per the VM's `journald.conf` -- no action needed
beyond confirming `SystemMaxUse=` is set to a sane value for the target VM's disk size. For the cron
fallback path, rotate `09_OUTPUTS/logs/anpia_daily_cron.log` with `logrotate` (weekly, keep 8 weeks,
compress) -- not configured by this task; add a `logrotate.d` entry at deployment time.

Structured JSON run logs (one file per run, in `09_OUTPUTS/logs/anpia_daily_runs/`) are small and
numerous over time (365/year) -- prune those older than ~180 days as part of the same deployment-time
logrotate/cron housekeeping, not automatically by the pipeline itself.
