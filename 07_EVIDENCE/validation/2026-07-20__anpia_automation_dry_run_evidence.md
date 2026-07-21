# Evidence: ANPIA Central Pipeline -- Dry-Run Execution

**Script:** `05_IMPLEMENTATION/anpia_daily_pipeline.py`
**Database writes performed by this evidence:** ZERO

## 1. Full dry-run execution (real, not simulated)

```
python 05_IMPLEMENTATION/anpia_daily_pipeline.py --dry-run --report-date 2099-01-01 --trigger-source manual
```

A deliberately far-future test date (2099-01-01) was used so the resulting local HTML artifact could
not be confused with a real production version, and was removed after the test completed (see
Section 3). The pipeline still performed a genuine, live, fresh 30-day extraction against the real
database -- only the *filename label* was a test value, not the underlying data or logic.

Full step sequence and results:

| Step | Status | Detail |
|---|---|---|
| acquire_lock | OK | |
| load_protected_environment | OK | |
| inspect_source_availability | OK | database_connected=true |
| acquire_pg_advisory_lock | OK | |
| determine_latest_complete_date | OK | 2026-07-19 |
| determine_version | OK | version=v001, action=**UPDATE_EXISTING_ROW**, existing_row_id=399, version_reason=MANUAL_REPUBLISH |
| fetch_latest_30_days | OK | row_count=268,404 |
| build_daily_production_version | OK | identity_count=53,843 |
| validate_calculations | OK | identity_count=53,843 |
| compress_dataset | OK | |
| render_html_from_template | OK | |
| secret_scan | OK | |
| validate_filename | OK | |
| write_local_html | OK | 3,952,130 bytes, sha256=f98ef6616ef0c5e163192496b3c41dee2c6a44361c6b2aeb80dd425ef470c04c |
| browser_smoke_validation | OK | `{"productCount":53843,"datesCount":30}` -- ran a real headless-Chrome-free Node `DecompressionStream` check, confirmed available on this machine |
| inspect_duplicate_state | OK | same_day_anpia_row_count=1 |
| insert_or_update_publication | **SKIPPED** | dry-run mode -- no write attempted |
| release_lock | OK | |

**RESULT: DRY_RUN_COMPLETE, EXIT_CODE: 0**

## 2. Notable correctness confirmation

`determine_version()` correctly identified that a live `ANPIA`/`Nivarnan` row already exists
(id=399) and set `action=UPDATE_EXISTING_ROW` -- even though the test used a report date
(2099-01-01) far outside any real reporting window. This is expected and correct: `ph_task` has no
dedicated report-date column (a structural fact documented since the original schema discovery), so
the "one active row" concept the pipeline enforces is genuinely "one row per `project_code` +
`assigned_user`", not "one row per literal calendar day" -- exactly matching how row id=399 has been
used in practice throughout this project (v001 inserted once, v002 updated the same row in place).

## 3. Lock and gate tests

- **Lock contention:** a stale lock file was manually placed at
  `09_OUTPUTS/logs/anpia_daily_pipeline.lock` before invoking the pipeline again; result:
  `[FAIL] acquire_lock -- lock already held`, **exit code 7**, as specified. Lock file removed after
  the test.
- **Publish without token:** `--publish` supplied without `--confirmation-token`; result:
  `[FAIL] safety_gate_confirmation_token`, **exit code 2**, before any database connection was even
  opened.

## 4. Cleanup

The test artifact (`2099-01-01_nivarnan_anpia_v001.html` and its intermediate extraction/compact-
dataset files) was deleted after the dry-run completed, since it was not a requested deliverable --
only the structured JSON run log (`09_OUTPUTS/logs/anpia_daily_runs/run_20260720T164428.555977_0530.json`)
was retained as the permanent evidence record. Real production files
(`2026-07-20_nivarnan_anpia_v001.html`, `v002.html`) and `ph_task` row 399 were confirmed unchanged
before and after this test (checksums re-verified).

## 5. Conclusion

The central pipeline executes correctly end-to-end against real live data, correctly derives the
insert-vs-update decision, correctly enforces its lock and confirmation-token gates, and performed
zero database writes during this dry-run evidence gathering.
