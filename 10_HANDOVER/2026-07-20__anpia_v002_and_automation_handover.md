# Handover: ANPIA Production v002 and Daily Automation System

**Requirement:** REQ-01-D02 (cross-ref REQ-AMZ-NMP-001-D01)
**Date:** 2026-07-20
**Status:** v002 published. Automation built, not activated.

## 1. What was done

1. **v001 preserved** -- confirmed unchanged locally (SHA-256
   `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`) and in `ph_task` before any
   work began, and re-confirmed unchanged at the end of this task.
2. **User-reported defect documented honestly** -- the task referred to "the supplied screenshot,"
   but no image was actually attached to the message. This was disclosed rather than fabricated (see
   `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/user-reported-defect/DEFECT_RECORD.md`).
   The defect's root cause was instead diagnosed by real-browser measurement of v001 itself.
3. **Fresh live data extraction** -- a genuinely new 268,404-row extraction (not reused from v001),
   producing an independently-built compact dataset (53,843 identities, 0 duplicates).
4. **Row-density fix (v008 template)** -- v001's `.table-wrap` used `max-height` with a 420px floor,
   which real-browser measurement showed produced only 4 complete rows in any hosted viewport
   <=800px tall (matching the reported "~5 rows"). Fixed via tightened spacing (no font-size
   reduction anywhere) plus a `height: clamp(984px, calc(100vh - 373px), 1100px)` rule, real-browser-
   verified to reliably show **15 rows** within the table's own scroll region at every tested
   viewport (up from 4-8). See `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` for the full,
   honest breakdown of what "15 rows visible" does and doesn't mean given the mathematically
   unavoidable trade-off between required toolbar/summary UI and hosted-viewport height.
5. **18/18 browser validation checks passed**, 0 console errors, 0 network requests, 6 screenshots
   captured.
6. **Calculation reconciliation: 0/108 mismatches** against an independent Python recomputation.
7. **Pre-publication gate passed** -- row 399 re-read live immediately before publication; every
   expected value (project_code, assigned_user, version_level=1, version_status=released, stored
   checksum, same-day row count=1) matched exactly.
8. **Row 399 updated to v002** -- `publish_ph_task_production_report.py` was extended to support a
   safety-gated `UPDATE_EXISTING_ROW` path (in addition to its existing `SAFE_NEW_INSERT` path),
   tested with two new adversarial gate tests (wrong `target_row_id`, action mismatch), then executed
   successfully. Independently re-verified post-commit: `version_level=2`, `version_status=released`,
   stored HTML checksum matches v002 exactly, same-day row count still exactly 1, total row count
   unchanged (284) confirming an UPDATE occurred, not an INSERT.
9. **Central reusable pipeline built** -- `05_IMPLEMENTATION/anpia_daily_pipeline.py`, a genuine
   16-step, Python-only (no Node dependency for the core path), lock-protected, safety-gated
   publication pipeline. Real dry-run executed successfully end-to-end against live data.
10. **"update to table" command wrapper and skill built** -- `05_IMPLEMENTATION/update_to_table.py`
    (fixed-argument-only, no free-text interpretation) and `08_SKILLS/anpia-update-to-table/SKILL.md`.
    Real dry-run executed successfully.
11. **Full deployment package built** -- systemd service + timer (daily 12:00 Asia/Colombo,
    `Persistent=true`, `RandomizedDelaySec=0`, hardened, non-root), install/remove/check scripts, a
    cron fallback (reference only), and a deployment README documenting every placeholder a future
    operator must fill in.
12. **Nothing activated** -- no unit installed, enabled, or started; nothing added to any crontab;
    no Windows Scheduled Task created. `AUTOMATION_BUILT_NOT_ACTIVATED` is the accurate final status.

## 2. What is NOT done (by design)

- No second same-day `ph_task` row was ever created -- row 399 was updated in place throughout.
- `daily_task` was not touched anywhere in this task (confirmed by code review -- zero references in
  any script written or modified).
- The automation is not scheduled or running anywhere.
- Disk-space checking is not implemented in the pipeline (disclosed gap, see
  `06_VALIDATION/2026-07-20__anpia_automation_validation.md` Section 5).

## 3. Open items for a human reviewer

1. **Hosted-modal dimensions remain unconfirmed.** The "15 rows" fix was calibrated against a
   disclosed, defensible assumption (an ~850px/700px simulated hosted viewport height), not the real
   hosted tool's actual iframe/modal size, which this task provided no way to access. If the real
   hosted container differs meaningfully, the `984px` floor and `373px` calc budget in
   `.table-wrap` (in `amazon_no_moving_report_template_v008.html`) can be retuned using the exact
   same real-browser measurement methodology documented in
   `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md`.
2. **Deployment placeholders** -- `/opt/anpia`, `anpia-svc`, `/etc/anpia/.env` in the systemd/cron
   files are illustrative, not the real target VM's values. A future deployment operator must fill
   these in (see `05_IMPLEMENTATION/deployment/README.md`) before running `install_anpia_timer.sh`.
3. **`systemd-analyze` / `systemctl` verification** could not be run on this Windows development
   machine -- must be run for real on the target Linux VM via `check_anpia_timer.sh` before
   activation.
4. **Disk-space check** is a disclosed, not-yet-implemented safety gap in the pipeline.

## 4. Files produced or modified in this task

**v002 report and data:**
`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`,
`05_IMPLEMENTATION/templates/amazon_no_moving_report_template_v008.html`,
`09_OUTPUTS/data/2026-07-20__anpia_production_v002_*` (extraction, compact dataset, compressed payload)

**Evidence and defect record:**
`07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/user-reported-defect/DEFECT_RECORD.md`,
`07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/validated/` (6 PNGs + `browser_results.json`)

**Validation docs:**
`06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md`,
`06_VALIDATION/2026-07-20__anpia_v002_calculation_validation.md`,
`06_VALIDATION/2026-07-20__anpia_v002_publication_validation.md`,
`06_VALIDATION/2026-07-20__anpia_automation_validation.md`

**Publication:**
`07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json`,
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`,
`05_IMPLEMENTATION/publish_ph_task_production_report.py` (extended for UPDATE support)

**Automation:**
`05_IMPLEMENTATION/anpia_daily_pipeline.py`,
`05_IMPLEMENTATION/update_to_table.py`,
`08_SKILLS/anpia-update-to-table/SKILL.md`,
`05_IMPLEMENTATION/deployment/` (service, timer, install/remove/check scripts, cron example, README),
`07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md`,
`07_EVIDENCE/validation/2026-07-20__anpia_update_to_table_command_evidence.md`

This handover document.

## 5. Recommended next step

Confirm with Nivarnan whether the real hosted-tool row visibility now looks acceptable (item 1 in
Section 3) -- that is the one substantive open question this task could not resolve without either a
real screenshot or live access to the hosted tool. Everything else (v002 publication, automation
build) is complete and verified.
