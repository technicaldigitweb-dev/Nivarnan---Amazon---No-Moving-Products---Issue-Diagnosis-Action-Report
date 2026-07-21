# Security Notice: ANPIA Database Credential Rotation Required

**Date:** 2026-07-20
**Status:** AMBER -- security item, not a blocker to today's delivered business benefit.
**No credential value appears anywhere in this document.**

## What was found

During final closure of the ANPIA project (secret scan ahead of Git initialization), a real,
live PostgreSQL host and password were found in plaintext in two locations:

1. **Local source/reference files** -- `Sources/db_access_templates/temp_user.py` and
   `update_table.py`, as `os.getenv(<VAR>, "<default>")` fallback literals. These are protected,
   read-only reference material (see `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`) and
   were **not modified**.
2. **Implementation files** -- `05_IMPLEMENTATION/anpia_daily_pipeline.py`,
   `publish_ph_task_production_report.py`, and `prepare_ph_task_v007_upload.py` each contained
   the same host/password as literal entries in a static `FORBIDDEN_CREDENTIAL_PATTERNS` list
   (used to scan generated report HTML for accidental credential leakage before publishing).
   These **were remediated** -- see below.

The real, active `.env` file (git-ignored, correctly excluded throughout the project) also
contains these values, as intended for local direct-connection use.

## Remediation performed

- The three implementation files above no longer contain any credential literal. Each now
  builds its leak-detection pattern list **at call time**, loading the live host/password from
  `anpia_config.get_db_config()` (environment-only, no hardcoded fallback) and discarding the
  list immediately after the scan. Static, non-secret patterns (`ANPIA_DB_PASSWORD`,
  `ANPIA_DB_HOST`) remain as literals -- these are variable *names*, not values.
- `05_IMPLEMENTATION/src/anpia_config.py` gained a new `safe_db_metadata()` function that
  returns database name and SSL mode in full, with host/user masked, and never returns the
  password -- for use anywhere connection metadata needs to be logged or recorded in evidence.
- A stale, inaccurate docstring claim in `05_IMPLEMENTATION/src/db_connection.py` (asserting the
  protected reference files were "confirmed to contain no embedded credentials") was corrected.
- 15 targeted tests were run confirming: valid config still loads correctly; `safe_db_metadata()`
  masks host/user and excludes the password; a missing/absent configuration fails closed
  (`RuntimeError`, non-zero exit, no secret in the traceback); and all three remediated scripts'
  leak-detection scan still correctly flags injected leak text and passes clean text -- see
  `07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`.
- `.gitignore` was updated to exclude `Sources/db_access_templates/`,
  `02_SOURCE/db_access_templates/`, and a broader set of runtime/temp/cache/secret paths.

## What was NOT done

- The protected source reference files (`temp_user.py`, `update_table.py`,
  `temp_user_access_report.pdf`) were not modified, executed, or imported -- checksums proven
  unchanged before/after in `00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md`.
- **The exposed credential was not rotated.** This notice records that rotation is required; it
  does not perform it. Rotation requires access to the database server and authorization from
  whoever owns `order_management_copy`'s `temp_user` role -- outside this task's scope and
  outside this session's available access.

## Status

**Rotation status: REQUIRED / NOT YET CONFIRMED.**

The credential was in local files only. Because this closure task's own secret scan caught the
exposure *before* any Git commit or push occurred (confirmed in
`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md` §5 -- no Git
history existed at any point containing these values), this is a precautionary rotation
recommendation rather than a confirmed public exposure. It should still be treated as required
good practice, since the value has existed in plaintext local files (including .env, by design)
throughout the project.

## Owner / reviewer

Whoever owns the `order_management_copy` database and the `temp_user` role (likely the same
audience that provisioned the original credential) -- not resolvable from this project's own
files.

## Evidence path

`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`

## Next action

Route this notice to the database owner for a rotation decision. Until rotation is confirmed and
evidenced, this remains an AMBER item in project closure -- it does not block today's delivered
business benefit or the GitHub push, since no credential value reached Git history.
