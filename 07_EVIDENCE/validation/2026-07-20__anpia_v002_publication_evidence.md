# Evidence: ANPIA Production v002 -- ph_task UPDATE (Executed)

**Requirement:** REQ-01-D02 -- ANPIA
**Date:** 2026-07-20
**Status:** PUBLISHED. Row id=399 updated in place -- no second row inserted.

## 1. Pre-publication gate (Section 8)

Live re-read of row 399, immediately before finalizing the manifest, confirmed every expected value:

| Check | Result |
|---|---|
| Row 399 exists | YES |
| project_code = ANPIA | YES |
| assigned_user = Nivarnan | YES |
| version_level (before) | 1 |
| version_status (before) | released |
| Stored HTML octet length (before) | 3,922,120 -- matches approved v001 exactly |
| Stored HTML SHA-256 (before, recomputed) | `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` -- matches approved v001 exactly |
| Same-day ANPIA row count (before) | 1 |
| Second same-day row exists | NO |

All values matched expectations exactly -- no abort condition was triggered.

## 2. Script extension

`05_IMPLEMENTATION/publish_ph_task_production_report.py` was extended to support `UPDATE_EXISTING_ROW`
in addition to its existing `SAFE_NEW_INSERT` path (previously used for the v001 publication):

- `build_update_sql_and_params()` -- a parameterized `UPDATE ... WHERE id = %s AND project_code = %s
  AND assigned_user = %s` (never a bare `id`-only match) that touches only `html_content`,
  `description`, `version_level`, `version_status`, and `updated_at` (via `now()`) -- every other
  column (`project_code`, `assigned_user`, `team`, `developer`, `assigned_user_team`, `phase_level`,
  `task_name`, `task_id`, `action_took_by`, `action_took_date_time`, `created_at`) is left untouched.
- The live duplicate check now derives `UPDATE_EXISTING_ROW` only when exactly one same-day
  ANPIA/Nivarnan row exists **and its id matches the manifest's declared `target_row_id`** -- a
  mismatch (wrong id, zero rows, or more than one row) falls through to
  `BLOCKED_UNCONFIRMED_COLUMN_RULE` rather than ever guessing which row to touch.
- The write path additionally requires the live-derived action to equal the **manifest's own
  declared** `proposed_action`, not just the operator-supplied `--expected-action` -- three
  independent signals (manifest declaration, live database state, and operator's CLI flag) must all
  agree before any write is attempted.

Two new safety-gate tests were run before execution: a tampered manifest with `target_row_id: 999`
(correctly fell through to `BLOCKED_UNCONFIRMED_COLUMN_RULE`, not `UPDATE_EXISTING_ROW`), and
`--expected-action SAFE_NEW_INSERT` against the real live state (correctly aborted with exit code 3,
`ABORTING WRITE: expected action does not match the live duplicate-check result.`).

## 3. Execution

```
python 05_IMPLEMENTATION/publish_ph_task_production_report.py \
  --manifest "07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json" \
  --execute \
  --confirmation-token "PUBLISH_NIVARNAN_ANPIA" \
  --approved-manifest-sha256 "b8ef5c8e9e603bd2351ddc2ab37dbd3c6c895086dec09e5bd2e25cfd33809835" \
  --expected-action "UPDATE_EXISTING_ROW"
```

Result: exit code **0**. Live duplicate check confirmed exactly 1 row (id=399) matching the
manifest's declared `target_row_id`; `UPDATE ... RETURNING id` reported exactly 1 affected row; the
script rereads the row (identity + stored HTML length) inside the same uncommitted transaction before
committing.

**`WRITE COMMITTED: action=UPDATE_EXISTING_ROW, id=399, project_code=ANPIA, assigned_user=Nivarnan, version_level=2, version_status=released, html_octet_length=3923170`**

## 4. Independent post-commit verification (separate read-only connection)

| Field | Verified value |
|---|---|
| id | 399 (unchanged -- no new row) |
| project_code | ANPIA (unchanged) |
| assigned_user | Nivarnan (unchanged) |
| team / developer / assigned_user_team / phase_level | Technical / Satheskanth / ph_priors / 1 (all unchanged) |
| task_name / task_id | unchanged / NULL (unchanged) |
| action_took_by / action_took_date_time | NULL / NULL (unchanged, as expected) |
| created_at | unchanged (2026-07-20T15:44:19.538101+05:30) |
| updated_at | changed to 2026-07-20T16:41:25.483869+05:30 (correct -- only field the UPDATE touches automatically) |
| version_level | **2** |
| version_status | released |
| stored html_content byte length | 3,923,170 (exact match to source v002 file) |
| stored html_content SHA-256 (recomputed independently) | `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2` (exact match) |
| Same-day ANPIA row count after commit | **1** (unchanged -- confirms no second row was inserted) |
| Total ph_task row count | 284 -> **284** (unchanged, confirming an UPDATE occurred, not an INSERT) |

## 5. Scope discipline confirmed

- `project_code = 'AGE'` was not queried at any point in this execution.
- `daily_task` was not touched -- the publish script has no code path referencing it.
- No credentials were printed at any point.
- Full HTML content was never printed -- only size and checksum.
- v001's local file and its own `ph_task` history (id=399's pre-update state) are fully preserved --
  only the row's *current* content was updated, consistent with the "one active same-day
  publication" rule; v001 remains addressable via
  `09_OUTPUTS/html/test_versions/README.md`-equivalent local preservation (v001's file was never
  deleted or modified).

## 6. Conclusion

ANPIA production v002 is now live in `tech_team_outputs.ph_task` row id=399, replacing v001's content
in place. Every claimed field was verified byte-for-byte against the approved manifest and the source
HTML file via an independent post-commit reread, and the same-day-row invariant (exactly one ANPIA/
Nivarnan row) was confirmed both before and after the write.
