# Daily Runtime and Schedule Design

**What this is:** The design for how this report would run as a reusable daily automation, and what remains to be approved before any scheduler is activated.

**Why it exists:** The user requirement says the report should generate daily; per instruction, the runtime/scheduling must be designed and documented, but **not activated** without explicit approval of machine, time, and method.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Coordinator (Sathees/Satheskanth). Technical reviewer: Sajeesan.

**Status:** DESIGNED — NOT ACTIVATED.

---

## Daily run sequence

1. Determine the common complete end date live (same logic as discovery §C — check for a partial-day row-count drop-off on the latest available PPC/sales date for each of the 8 account×marketplace combinations; do not assume `CURRENT_DATE - 1` blindly).
2. Run `05_IMPLEMENTATION/sql/main_report.sql` (parameterized by end date and period) via the primary MCP connection for each of 7/14/30-day windows (or on-demand per period, if the HTML uses server-side period switching rather than embedding all three).
3. Transform results (`data_transform.py`): resolve SKU bridge, apply warehouse mapping, compute ACOS, apply missing-data rules, deduplicate summary totals per §D of the design.
4. Render HTML (`html_renderer.py`) from the transformed data + template.
5. Run `validate_output.py` (SQL/HTML/reconciliation checks per the validation reports).
6. If validation passes AND ph_task metadata (DEC-TECH-001) is approved: publish via `publish_to_ph_task.py`. If either fails, stop and log — do not publish a partially-validated or unapproved report.
7. Log run outcome (success/failure, validation summary, publication result) to `09_OUTPUTS/logs/`.

## Default reporting period

30 days, per instruction ("The default initial view may use 30 days only when the user requirement or existing approved template supports it") — the reference image's own example data is uniformly labelled "(30d)", supporting this as the default. All three periods (7/14/30) remain selectable.

## How 7/14/30 views are supported

Each period is computed from the same common complete end date with a different start-date offset (§E of the main design doc). The v001 HTML embeds all three period datasets client-side if total output size is acceptable (per instruction); if not, the default period (30d) is rendered and a note states other periods require a re-run — this decision is made at implementation time based on actual output size, not assumed here.

## Latest-complete-date calculation

Not `CURRENT_DATE`. Computed by comparing the latest available date's row count against the trailing 9-day average for both PPC and sales, per account×marketplace combination; if the latest date's count is materially below trend (as empirically found for 2026-07-16 in discovery), the prior date is used as the complete end date, applied as one common date across all combinations (matching the discovery's approach) unless a future requirement asks for true per-combination end dates.

## Output versioning

Filename pattern: `09_OUTPUTS/html/YYYY-MM-DD__nivarnan__amazon_no_moving_report_vNNN.html` — date is the generation date, version increments only if the same date is regenerated (e.g. after a correction). ph_task publication versioning follows the append-only rule in `08_SKILLS/ph_task_reference/ph_task_versioning_rules.md` (new row per release, `version_status='rejected'` set on the prior row) — not the HTML filename version.

## Validation gate

No publication proceeds unless `06_VALIDATION/2026-07-17__sql_validation_report.md` and `.../html_validation_report.md` both PASS and `07_EVIDENCE/validation/2026-07-17__report_reconciliation_evidence.md` shows no unexplained difference beyond documented tolerance.

## Publication gate

No `tech_team_outputs.ph_task` write proceeds unless `06_VALIDATION/2026-07-17__ph_task_prepublication_check.md` PASSes — which itself requires DEC-TECH-001 (exact ph_task metadata) to be approved. **Currently blocked.**

## Retry behavior (designed, not yet implemented as code)

On a transient MCP/query failure: retry the failing step up to 2 times with a short backoff; on repeated failure, stop the run, do not publish a partial report, and log the failure with the exact step and error.

## Failure logging

Every run (success or failure) writes a log entry to `09_OUTPUTS/logs/YYYY-MM-DD__run_log.txt` (or `.json`) recording: start time, end time, period(s) run, validation result, publication result (or reason not attempted), and any error encountered.

## Credential handling

No credentials are stored in any file in this project. A future production runtime would need its own credential-handling mechanism (e.g. environment variables or a secrets manager) for the primary MCP connection — this is explicitly **out of scope to design in detail here**, since it depends on where/how the daily job actually executes (which machine, which orchestrator), a decision not yet made (see Scheduling options below). No `db_connection.py` in this project contains or will contain a literal credential.

## Scheduling options (not activated)

Candidate mechanisms, to be chosen by the coordinator: OS-level cron/Task Scheduler on an approved machine; the AIOS project's own scheduling convention (if one exists — not found in `00_PROJECT_CONTROL/`, so no existing mechanism to reuse was found); an external CI/scheduler product. **None is selected. No scheduler is activated by this design.**

## Owner

Coordinator (Sathees/Satheskanth) for scheduling machine/time approval; Sajeesan for runtime/credential mechanism approval.

## Rollback or stop behavior

If validation fails mid-run: do not publish; preserve the generated HTML/logs as evidence of the failed run (do not delete); the next scheduled run attempts fresh, it does not retry a stale failed output.

## Pass/fail rule

PASS if every element in this design (sequence, period logic, versioning, gates, retry, logging, credentials, scheduling) is documented without inventing an execution time or activating any scheduler.

## Known limitations

No execution time, machine, or scheduling method is approved. This design describes the intended reusable shape only.

## Next action

Route the scheduling machine/time decision to the coordinator; do not activate any scheduler until that decision is recorded here with an approval date.
