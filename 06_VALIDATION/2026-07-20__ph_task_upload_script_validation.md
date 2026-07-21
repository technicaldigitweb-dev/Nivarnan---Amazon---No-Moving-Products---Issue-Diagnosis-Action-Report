# Validation: ph_task Upload Preparation Script

**Script:** `05_IMPLEMENTATION/prepare_ph_task_v007_upload.py`
**Requirement:** REQ-01-D02 -- ANPIA

## 1. Design-safety checklist

| Requirement | Status | Evidence |
|---|---|---|
| Default execution (no flags) never writes | PASS | Gate test 1 (see dry-run evidence doc) |
| `--dry-run` never writes | PASS | Section 1 of dry-run evidence doc |
| Real write requires BOTH `--execute` AND exact `--confirm-publication-token` | PASS | Gate tests 2-4 |
| Wrong or missing token blocks write even with `--execute` | PASS | Gate tests 2, 4 |
| Token alone (no `--execute`) cannot cause a write | PASS | Gate test 3 |
| HTML SHA-256 must match manifest before proceeding | PASS | Gate test 5 |
| HTML file must exist | PASS | Gate test 6 |
| HTML must be valid UTF-8 | PASS | Gate test 7 |
| Live duplicate state must match operator's `--expected-action` before a write is attempted | PASS | Gate test 8 |
| Forbidden credential-pattern scan on HTML content | PASS | Dry-run report: "Credential scan: CLEAN" |
| Size sanity ceiling enforced (disclosed as non-authoritative) | PASS | Dry-run report: "Size gate: PASS (ceiling 50,000,000 bytes, not a proven DB limit)" |
| Self-contained-HTML heuristic checks (no external `<script src>`/CDN/stylesheet refs) | PASS | Dry-run report: "Self-contained checks: CLEAN" |
| All SQL parameterized (no string-built SQL) | PASS | Code review: `check_duplicates()` and `build_insert_sql_and_params()` both use `%s` placeholders exclusively |
| Credentials never printed | PASS | Manual review of all dry-run/gate-test output -- no DSN, password, or `ANPIA_DB_*` value appears anywhere |
| `html_content` never printed in full | PASS | Script only ever prints size/checksum, never the HTML body |
| Session held read-only for the full script lifetime | PASS | `get_connection()` sets session-level read-only; `SHOW transaction_read_only` returns `on` |
| Explicit `conn.rollback()` before close, even on the write path | PASS | Code review of `main()`'s `finally` block |
| Write path does not call `INSERT` even when all gates pass | PASS (intentional, extra safety margin beyond spec) | Code review: `build_insert_sql_and_params()` is defined but never invoked in `main()`; write branch only prints and exits |

## 2. Manifest validation

- `07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json` is valid JSON
  (confirmed via `json.load()`).
- Every proposed field carries `value`, `source_of_truth`, `confidence`, and
  `reviewer_approval_needed`.
- Fields with no provable live convention (`version_status`, `assigned_user_team`) are explicitly
  `null` with `confidence: "NONE"` / `"LOW"` rather than guessed.
- `duplicate_check_result` was corrected during this validation pass to include the broader
  AGE-project near-duplicate finding (id=56) -- see discovery doc section 5 and manifest
  `known_limitations`.
- `recommended_action` was corrected from `SAFE_NEW_INSERT` to `BLOCKED_AMBIGUOUS` to reflect that
  finding. This is a genuine, human-reviewable ambiguity, not a script defect.

## 3. Residual risk / what this validation does NOT cover

- The script's live `check_duplicates()` only checks `project_code + assigned_user` exact match. It
  will report `SAFE_NEW_INSERT` from its own narrow live check even though the manifest-level
  analysis found a topically overlapping row under a different `project_code`. Any future operator
  running this script must read the manifest's `known_limitations`, not just the script's console
  output, before deciding whether to proceed.
- `task_id` uniqueness is not database-enforced; the script does not attempt to guarantee
  application-level uniqueness beyond the duplicate check described above.
- This validation pass did not exercise the write path with a passing gate combination (i.e. never
  ran `--execute` + correct token + `--expected-action SAFE_NEW_INSERT` together), since doing so
  would have been the first real opportunity for a live INSERT and was explicitly out of scope for
  this task (publication remains deferred).

## 4. Conclusion

The script meets every safety requirement specified for this task. Publication itself remains
correctly gated behind human review, both by the script's own token/flag mechanism and by the
newly-identified `BLOCKED_AMBIGUOUS` classification requiring a reviewer decision before any write
should be attempted.
