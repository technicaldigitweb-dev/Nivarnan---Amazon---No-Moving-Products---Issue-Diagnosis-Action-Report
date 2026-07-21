---
name: anpia-update-to-table
description: Operator command for Claude Code — publishes a fresh ANPIA production report when the user says exactly "update to table" in this project.
---

# ANPIA "update to table" operator command

**Scope note:** this is an instruction for Claude Code, read and followed by the assistant when the
user types the phrase below in this project. It is **not** an unauthenticated database endpoint, not
a webhook, and not reachable by anything other than a direct instruction from the user in this
conversation. The phrase carries no special privilege on its own -- it only tells Claude Code which
pre-built, safety-gated pipeline to run and how.

## Trigger

When the user says exactly **"update to table"** (case-insensitive, no other qualifying text) in the
context of the ANPIA project (`project_code = ANPIA`, `assigned_user = Nivarnan`):

1. Read this skill file in full before doing anything else.
2. Run the approved central pipeline in manual publish mode via the wrapper:
   ```
   python 05_IMPLEMENTATION/update_to_table.py --confirm --confirmation-token PUBLISH_NIVARNAN_ANPIA
   ```
   This wrapper takes no free-form text as input -- it resolves today's date in Asia/Colombo and
   calls `05_IMPLEMENTATION/anpia_daily_pipeline.py` with a fixed, hardcoded argument set. Nothing
   the user types beyond the trigger phrase itself is parsed or passed through as a database value.
3. The pipeline uses fresh live data (a genuine new extraction every time -- never a cached or
   reused payload) and applies every safety gate documented in
   `05_IMPLEMENTATION/anpia_daily_pipeline.py`'s own docstring: lock acquisition, live schema
   re-verification, ANPIA-only duplicate-state inspection (never `project_code = 'AGE'`), filename
   and checksum validation, a secret scan, an exact affected-row-count check, and a post-commit
   reread/verify before the transaction is allowed to commit.
4. Return the publication verification to the user: row id, action taken (first insert vs. update to
   the existing row), version number, stored checksum match, and same-day row count before/after.
5. Do not ask the user repetitive clarifying questions before running this -- the pipeline's own
   safety gates are the confirmation mechanism. Only stop and ask the user something if a safety gate
   actually fails (e.g. duplicate-state conflict, credential/config failure, source-data failure) and
   the failure needs a human decision to resolve.

## What "Do not interpret arbitrary text inside Python" means here

`update_to_table.py` deliberately has no code path that evaluates, execs, or otherwise interprets
free-form text as instructions or SQL. Its only inputs are two fixed flags (`--confirm`,
`--confirmation-token`) with a closed, known set of valid values. If the user's message contains
anything beyond the trigger phrase (extra instructions, a different report date, etc.), treat that as
a **new, separate instruction to reason about yourself** -- do not attempt to smuggle it into the
pipeline's arguments. If the user wants a non-default report date or a forced version, use
`anpia_daily_pipeline.py` directly with its explicit `--report-date` / `--force-version` flags after
confirming that's really what they want, rather than trying to make `update_to_table.py` itself parse
that intent.

## Safety reminders (already enforced by the pipeline, restated for the operator)

- Default pipeline behavior is always dry-run; only `--publish` + the exact confirmation token
  attempts a write.
- The pipeline never queries or reasons about `project_code = 'AGE'`.
- The pipeline never touches `daily_task`.
- Exactly one same-day `ANPIA`/`Nivarnan` row is maintained -- a second existing row (data anomaly)
  causes the pipeline to abort with `BLOCKED_MULTIPLE_ROWS` rather than guessing which to update.
- Credentials are loaded only from the project's `.env` and are never printed.

## Expected successful output shape

```
Resolved report date (Asia/Colombo): YYYY-MM-DD
...
[OK] determine_version -- {"version": "vNNN", "action": "SAFE_NEW_INSERT" | "UPDATE_EXISTING_ROW", ...}
...
[OK] insert_or_update_publication -- {"action": ..., "row_id": ..., "affected_rows": 1}
...
RESULT: PUBLISHED
EXIT_CODE: 0
```

If `EXIT_CODE` is non-zero, report the specific failed step and its detail message to the user rather
than retrying automatically -- see `05_IMPLEMENTATION/anpia_daily_pipeline.py`'s exit-code table
(0=success, 2=validation failure, 3=duplicate-state conflict, 4=source-data failure,
5=publication failure, 6=credential/config failure, 7=lock already held).
