# Evidence: ANPIA Pre-Git Secret Remediation

**Date:** 2026-07-20
**Status:** REMEDIATION PASS (implementation code); rotation AMBER (see
`11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`).
**No secret value is reproduced anywhere in this document.**

## 1. What triggered this

During final-closure repository preparation (Git init + first push), a targeted secret scan of
files proposed for commit found a real live PostgreSQL host and password hardcoded as string
literals in three approved implementation files (used there as a static leak-detection guard
list) and, separately, as `os.getenv` fallback defaults in two protected reference-only files
under `Sources/db_access_templates/`. Full detail and remediation steps are in
`11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`.

## 2. Files scanned

Entire project tree except `09_OUTPUTS/data/` and `09_OUTPUTS/logs/` (already git-ignored, raw
per-run extraction data/logs, not commit candidates) -- approximately 400+ files across
`00_PROJECT_CONTROL/` through `12_ARCHIVE/`, `Sources/`, and root-level config files.

## 3. Files remediated

| File | Change |
|---|---|
| `05_IMPLEMENTATION/anpia_daily_pipeline.py` | `FORBIDDEN_CREDENTIAL_PATTERNS` (2 real-value literals) replaced with `STATIC_FORBIDDEN_PATTERNS` (variable names only) + runtime `_runtime_forbidden_patterns()` that loads the live value from `anpia_config.get_db_config()` at call time |
| `05_IMPLEMENTATION/publish_ph_task_production_report.py` | Same pattern |
| `05_IMPLEMENTATION/prepare_ph_task_v007_upload.py` | Same pattern |
| `05_IMPLEMENTATION/src/anpia_config.py` | Added `safe_db_metadata()` (masks host/user, excludes password, never returns a DSN) |
| `05_IMPLEMENTATION/src/db_connection.py` | Corrected a stale/inaccurate docstring claim that the protected reference files were "confirmed credential-free" |

Zero implementation files contain a real credential literal after remediation (§5).

## 4. Files excluded (not modified, not staged)

- `Sources/db_access_templates/temp_user.py`
- `Sources/db_access_templates/update_table.py`
- `Sources/db_access_templates/temp_user_access_report.pdf`

Checksums proven unchanged before/after in `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`.
`.gitignore` updated with `Sources/db_access_templates/` and `02_SOURCE/db_access_templates/`
(the latter does not currently exist but is excluded defensively).

## 5. Scan results

**A. Exact-value scan** (the two known real literals, searched across the full tree excluding
`09_OUTPUTS/{data,logs}` and the protected `db_access_templates/` folder): **0 matches. CLEAN.**
(Prior to remediation, this scan matched 5 files: `.env` (expected, git-ignored), the 3
implementation files (since remediated), and the 2 protected template files (excluded from
Git, left unmodified by design).)

**B. Pattern scan** (`password=`, `passwd=`, `DB_PASSWORD=`, `postgres(ql)://user:pass@host`,
private-key headers, `ghp_`/`github_pat_` tokens, `api_key=`, `authorization: bearer`, Slack
`xox*` tokens -- same scope as §A): **0 matches. CLEAN.**

**C. Entropy/tool scan:** `gitleaks`, `trufflehog`, and `detect-secrets` are not installed in
this environment; per this task's own instruction, no unapproved global software was installed
to run this task. §A and §B (custom exact-value and pattern greps) serve as the substitute
control for this session.

**D. Staged-content scan:** performed after `git add` in
`07_EVIDENCE/validation/2026-07-20__anpia_git_github_publication_evidence.md` (this document
covers pre-staging state only).

**E. Git object/history scan:** confirmed no `.git` directory existed anywhere in the project
root prior to this task's `git init` (checked directly). Therefore the exposed credential values
were **never** committed to Git and never existed in Git history at any point -- the exposure
was confined to local, uncommitted files (`.env` by design, plus the now-remediated
implementation files and the excluded protected templates).

## 6. Runtime-remediation functional tests

15 targeted tests were run (throwaway script, not part of the project) confirming: valid `.env`
config still loads correctly (all fields present, no value printed); `safe_db_metadata()` masks
host/user and excludes password; `repr()` of the masked metadata contains no real credential
substring; a missing/absent configuration (isolated temp directory, no `.env`, `ANPIA_DB_*`
stripped from environment) fails closed with `RuntimeError`, non-zero exit code, and no secret
substring in the traceback; and all three remediated scripts' `scan_forbidden_patterns()` still
correctly flags injected leak text and returns clean on safe text, while
`_runtime_forbidden_patterns()` demonstrably includes the live secret value at call time without
it ever existing as a source-code literal. **15/15 PASS.**

## 7. Production output integrity

Re-verified unchanged by this remediation work:

| File | SHA-256 |
|---|---|
| `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` | `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` |
| `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html` | `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2` |

Both match the values recorded in prior evidence exactly -- no business output was touched by
this security remediation.

## 8. Conclusion

Implementation-code remediation: **PASS**. No credential literal remains in any file proposed
for Git commit. Rotation of the underlying credential itself remains a separate, unconfirmed
AMBER item -- see `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`. Safe to proceed
to Git initialization and staging.
