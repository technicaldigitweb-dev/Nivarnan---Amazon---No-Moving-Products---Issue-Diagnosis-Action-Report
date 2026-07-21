# Validation: ANPIA Secure Configuration (Post-Remediation)

**Date:** 2026-07-20
**Status:** PASS (15/15 tests)
**No secret value appears anywhere in this document.**

## Scope

Validates the security remediation described in
`11_REVIEW/2026-07-20__anpia_credential_rotation_required.md` and
`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`: that
`05_IMPLEMENTATION/src/anpia_config.py` and the three remediated publish/pipeline scripts behave
correctly with no hardcoded credential literal remaining in source.

## Test results

| # | Test | Result | Detail |
|---|---|---|---|
| 1 | Valid local `.env` loads successfully | PASS | `get_db_config()` returns all expected keys; no value printed |
| 2 | `safe_db_metadata()` excludes password | PASS | Returned dict has no `password` key |
| 3 | `safe_db_metadata()` masks host and user | PASS | Both values contain `*` characters (masked, not full) |
| 4 | `repr(safe_db_metadata())` contains no real credential | PASS | Known password substring absent |
| 5 | Missing configuration fails closed | PASS | Isolated temp dir, no `.env`, `ANPIA_DB_*` stripped from environment -> `RuntimeError`, non-zero exit code |
| 6 | Fail-closed error contains no secret | PASS | stderr scanned for known literals -- absent |
| 7 | `anpia_daily_pipeline.py` runtime patterns include live secret only at call time | PASS | Pattern list length 4 (2 static names + host + password), sourced from `get_db_config()`, not a source literal |
| 8 | `anpia_daily_pipeline.py` leak scan still detects an injected leak | PASS | |
| 9 | `anpia_daily_pipeline.py` leak scan clean on safe text | PASS | |
| 10 | `publish_ph_task_production_report.py` runtime patterns include live secret only at call time | PASS | |
| 11 | `publish_ph_task_production_report.py` leak scan still detects an injected leak | PASS | |
| 12 | `publish_ph_task_production_report.py` leak scan clean on safe text | PASS | |
| 13 | `prepare_ph_task_v007_upload.py` runtime patterns include live secret only at call time | PASS | Pattern list length 3 (1 static name + host + password) |
| 14 | `prepare_ph_task_v007_upload.py` leak scan still detects an injected leak | PASS | |
| 15 | `prepare_ph_task_v007_upload.py` leak scan clean on safe text | PASS | |

## Additional design checks (inspection, not executed as separate automated tests)

- **No database connection at import time:** `anpia_config.py` contains no `psycopg2` import and
  performs no network I/O anywhere except inside `get_db_config()`/`safe_db_metadata()`, both of
  which only read environment variables and the local `.env` file. Confirmed by direct read of
  the module and by the fact that `import anpia_config` in test #1 returned immediately with no
  network delay.
- **Dry-run without credentials fails safely:** `anpia_daily_pipeline.py`'s own docstring and
  `main()` structure route all writes through the safety-gated `publish_row()` path, reached only
  after `get_db_config()` succeeds; the module itself performs no action at import time
  (`if __name__ == "__main__": main()` guard, confirmed by direct read).
- **Publish mode cannot start without complete configuration:** `get_db_config()` is the single
  source of connection configuration for all three remediated scripts; test #5 proves it raises
  before any connection attempt when configuration is incomplete.
- **Automation cannot silently use source-reference credentials:** confirmed by direct code
  review -- no implementation file imports or executes anything under
  `Sources/db_access_templates/` (see `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`).
- **No database writes occur during this validation:** all 15 tests either call read-only
  configuration functions or run in a subprocess with a deliberately incomplete environment that
  raises before any connection attempt; no `psycopg2.connect()` call was reached in any test.
- **Scheduler remains inactive:** unaffected by this validation; confirmed separately in
  `06_VALIDATION/2026-07-20__anpia_automation_validation.md` and re-confirmed in this closure
  task's own automation status review.

## Production output integrity

Checksums re-verified unchanged by this remediation (see
`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md` §7):

- v001: `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`
- v002: `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`

## Conclusion

**PASS.** Runtime configuration is environment-only with no hardcoded fallback anywhere in
committed source, fails closed on missing configuration, never logs or returns a printable
password, and the three affected leak-detection scripts retain full detection behavior without
storing the real secret as a source-code literal. Credential rotation itself remains a separate
AMBER item, tracked in `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`.
