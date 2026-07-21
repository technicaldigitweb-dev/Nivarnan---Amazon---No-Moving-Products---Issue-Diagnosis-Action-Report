# Evidence: Production ANPIA v001 -- ph_task Publish Script Dry-Run and Safety-Gate Tests

**Script:** `05_IMPLEMENTATION/publish_ph_task_production_report.py`
**Manifest:** `07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json`
**Database writes performed across all testing:** ZERO

## 1. Official dry-run (correct manifest, no write flags)

```
python 05_IMPLEMENTATION/publish_ph_task_production_report.py \
  --manifest "07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json" \
  --dry-run
```

Result: exit code **0**. Summary:
- Manifest SHA-256 computed: `eaa0fa3f6e602915c52c26983fafbd38bfcc530c062bc74ca03badefb741e2a7`
- project_code = ANPIA (approved), assigned_user = Nivarnan (approved)
- production_filename format valid
- HTML checksum/size/UTF-8/credential-scan/self-contained checks: all PASS
- Live connection succeeded, read-only transaction confirmed on
- Live schema re-verified: 18/18 expected columns present
- ANPIA-only duplicate check (AGE never queried): 0 existing rows -> live action **SAFE_NEW_INSERT**
- All 17 proposed column values printed (non-secret; `html_content` shown only as size+checksum)
- **WRITE EXECUTED: NO (dry-run mode)**

## 2. Safety-gate test results (all 12 required tests)

| # | Test | Expected | Actual | Exit code |
|---|---|---|---|---|
| 1 | No arguments | Fail safely | `SAFETY GATE FAILED: manifest not found: None` | 2 |
| 2 | `--execute` without token | Fail safely | `SAFETY GATE FAILED: --execute was supplied without the correct --confirmation-token.` | 2 |
| 3 | Token without `--execute` | Runs as harmless dry-run | Full valid dry-run report, `WRITE EXECUTED: NO (dry-run mode)` | 0 |
| 4 | Wrong token | Fail safely | Same gate message as #2 | 2 |
| 5 | Wrong manifest checksum (`--approved-manifest-sha256` mismatch) | Fail safely | `SAFETY GATE FAILED: manifest SHA-256 does not match --approved-manifest-sha256.` (both values printed) | 2 |
| 6 | Missing HTML file | Fail safely | `SAFETY GATE FAILED: HTML file not found: ...` | 2 |
| 7 | Invalid filename format | Fail safely | `SAFETY GATE FAILED: production_filename '...' does not match YYYY-MM-DD_username_projectcode_vNNN.html.` | 2 |
| 8 | `project_code` other than ANPIA (tested with `AGE`) | Fail safely | `SAFETY GATE FAILED: manifest project_code 'AGE' is not the approved 'ANPIA'.` | 2 |
| 9 | `assigned_user` other than Nivarnan | Fail safely | `SAFETY GATE FAILED: manifest assigned_user 'SomeoneElse' is not the approved 'Nivarnan'.` | 2 |
| 10 | Duplicate state different from manifest (`--expected-action UPDATE_SAME_DAY_ACTIVE_ROW` against a real live state of 0 rows / SAFE_NEW_INSERT, with `--execute` + correct token + correct manifest checksum) | Abort before any DML | `Expected action (...) matches live duplicate state: NO` then `ABORTING WRITE: expected action does not match the live duplicate-check result.` | 3 |
| 11 | Report checksum mismatch | Fail safely | `SAFETY GATE FAILED: HTML SHA-256 does not match the manifest.` (expected/actual both printed) | 2 |
| 12 | Invalid UTF-8 | Fail safely | `SAFETY GATE FAILED: HTML is not valid UTF-8.` | 2 |

All 12 tests behaved exactly as required. **No test reached the `INSERT` statement.** Test 10 is the
most significant: it exercised the full write path up through the live duplicate re-check with a
*valid* token, a *valid* approved-manifest checksum, and `--execute` set -- and still correctly
aborted before any write, because the live database state did not match the declared expectation.

## 3. Test 8 in particular -- AGE-exclusion verified under adversarial conditions

Test 8 deliberately set `project_code: "AGE"` in a tampered manifest to confirm the script actively
rejects any attempt to publish under the excluded project code, rather than merely never defaulting
to it. This is a direct, adversarial test of this task's core identity rule.

## 4. Post-testing integrity re-verification

- Production HTML SHA-256 unchanged: `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`.
- Reference file checksums unchanged (`temp_user.py`, `update_table.py`, `temp_user_access_report.pdf`
  -- all match values recorded earlier in this project).
- `ph_task` total row count: **283** both before and after this round of testing (unchanged).
- `ph_task` rows with `project_code = 'ANPIA'`: **0** both before and after (unchanged).
- Secret scan across all 7 files created in this task (script, manifest, discovery/validation/
  evidence docs, test_versions README): CLEAN.
- All temporary tamper manifests/files used for gate tests 5-12 were created in the session
  scratchpad directory (outside the project tree) and deleted after use.

## 5. Conclusion

The production publish script is safe-by-default: it requires four independent conditions
(`--execute`, correct confirmation token, correct approved-manifest checksum, and a live-matching
expected action) before it will even attempt a write, re-verifies the live schema and ANPIA-only
duplicate state a second time immediately before the write (closing the race window between
inspection and execution), and would reread the just-inserted row inside the same transaction before
committing. All 12 required failure-mode tests and the standard dry-run behave exactly as specified.
No database write occurred at any point in this task.
