# Evidence: ph_task Upload Script Dry-Run and Safety-Gate Tests

**Script:** `05_IMPLEMENTATION/prepare_ph_task_v007_upload.py`
**Manifest:** `07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json`
**Database writes performed across all testing:** ZERO (confirmed by re-verified row count and
checksum stability -- see section 3)

## 1. Official final dry-run (correct inputs, no flags forcing a write)

Command:
```
python 05_IMPLEMENTATION/prepare_ph_task_v007_upload.py \
  --html-path "09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v007.html" \
  --manifest "07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json" \
  --dry-run
```
Result: exit code **0**. Full captured output saved to
`07_EVIDENCE/publication/2026-07-20__ph_task_final_dry_run_output.txt`. Summary:
- Checksum gate: PASS (`60b11a8a077f81db70e77012cf5dd2f45cd2f9983db3e9c61848760e126da192`)
- Size gate: PASS (3,922,103 bytes vs. 50,000,000 ceiling)
- UTF-8 valid: YES
- Credential scan: CLEAN
- Self-contained checks: CLEAN
- Connection: succeeded, read-only txn = on
- Duplicate check (script-level, project_code+assigned_user exact match): 0 rows -> live
  recommendation `SAFE_NEW_INSERT`
- **WRITE EXECUTED: NO (dry-run mode)**

Note: the script's own live duplicate check is intentionally narrow (project_code + assigned_user
exact match only) and does not detect the broader AGE-project near-duplicate documented in
`03_DISCOVERY/2026-07-20__ph_task_schema_and_value_inspection.md` section 5. The manifest's
`recommended_action` (`BLOCKED_AMBIGUOUS`) is the authoritative, human-reviewable classification;
the script's live check is a narrower automated cross-check only, not a substitute for it.

## 2. Safety-gate test results (all 8 required tests)

| # | Test | Command variant | Expected | Actual | Exit code |
|---|------|------------------|----------|--------|-----------|
| 1 | No arguments | (none) | Fail safely | `SAFETY GATE FAILED: manifest not found: None` | 2 |
| 2 | `--execute` without token | `--execute` only | Fail safely | `SAFETY GATE FAILED: --execute was supplied without the correct --confirm-publication-token.` | 2 |
| 3 | Token without `--execute` | `--confirm-publication-token PUBLISH_ANPIA_V007` (no `--execute`) | Runs as harmless dry-run (token alone cannot cause a write) | Full valid dry-run report, `WRITE EXECUTED: NO (dry-run mode)` | 0 |
| 4 | Wrong token | `--execute --confirm-publication-token WRONG_TOKEN` | Fail safely | Same gate message as #2 | 2 |
| 5 | Incorrect checksum | Manifest with tampered `html_sha256` | Fail safely | `SAFETY GATE FAILED: HTML SHA-256 does not match the manifest.` (expected/actual both printed) | 2 |
| 6 | Missing HTML file | `--html-path` pointing to nonexistent file | Fail safely | `SAFETY GATE FAILED: HTML file not found: ...` | 2 |
| 7 | Invalid UTF-8 | `--html-path` pointing to a file with invalid UTF-8 bytes, manifest checksum matched to that file | Fail safely | `SAFETY GATE FAILED: HTML is not valid UTF-8.` | 2 |
| 8 | Duplicate state mismatch under `--execute` | `--execute --confirm-publication-token PUBLISH_ANPIA_V007 --expected-action UPDATE_EXISTING_SAME_DAY_ROW` (live state is actually 0 rows / SAFE_NEW_INSERT) | Abort before any DML | `Expected action (UPDATE_EXISTING_SAME_DAY_ROW) matches live duplicate state: NO` then `ABORTING WRITE: expected action does not match the live duplicate-check result.` | 3 |

All 8 tests failed safely (or, for test 3, correctly ran as a no-op dry-run). **No test reached or
executed the `INSERT` statement.** The script's write path additionally never calls
`build_insert_sql_and_params()`'s result through `cursor.execute()` in this script version -- the
write path is coded as intentionally inert (prints
`"WRITE PATH REACHED BUT INTENTIONALLY NOT COMMITTED."` and exits) even when all gates pass, as an
extra layer of protection beyond the token/flag gate.

## 3. Post-testing integrity re-verification

- v007 HTML SHA-256 unchanged: `60b11a8a077f81db70e77012cf5dd2f45cd2f9983db3e9c61848760e126da192`
  (matches manifest and pre-testing value).
- Reference file checksums unchanged:
  - `temp_user.py`: `6dd2825c266ff94b35ee0cf3372b8a62480736e5f76c0e1df4a2a51dc52a1049`
  - `update_table.py`: `9784d14ab8e0646e454a8effe9e049dfdd10a8fb32fe4fd63cfa29a1120ff5bc`
  - `temp_user_access_report.pdf`: `b0c2641ae879e33e898df8b7d109d5a630510031aafd62b3de274babe175a5cd`
- `.env` confirmed present at project root and covered by `.gitignore` patterns (`.env`, `.env.local`,
  `.env.*.local`, `.env.*`).
- `ph_task` row count: 271 at original inspection -> 275 at final re-verification, fully explained by
  an unrelated automated insert batch (see discovery doc section 6). Not caused by this task's
  testing.

## 4. Test artifact cleanup

All temporary tamper files used for gate tests 5 and 7 (`bad_checksum_manifest.json`,
`invalid_utf8.html`, `invalid_utf8_manifest.json`) were created in the session scratchpad directory
(outside the project tree) and deleted after use. No test artifacts were committed to the project.

## 5. Conclusion

The script is safe-by-default: it requires both `--execute` and the exact confirmation token to
attempt a write, cross-checks the live duplicate state against an operator-declared expectation
before proceeding, and does not execute a real `INSERT` in this version regardless of flags. All 8
required failure-mode tests and the standard dry-run behave exactly as specified. No database write
occurred at any point.
