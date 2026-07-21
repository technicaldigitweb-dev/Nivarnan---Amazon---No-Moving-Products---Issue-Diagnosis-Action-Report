# Evidence: daily_task.tbl_anpia_satheskanth -- Dry-Run / Discovery

**Requirement:** REQ-01-D02 -- ANPIA
**Date:** 2026-07-20
**Connection method:** Approved PostgreSQL MCP (`mcp__claude_ai_postgres__execute_sql`), per this
task's explicit `DATABASE CONNECTION RULE`. No `.env` credentials or direct `psycopg2` connection
were read or used for any operation in this document.
**Database writes performed in this document:** ZERO

## 0. MCP connection identification (disclosed reasoning)

No tool literally named "vintageinterior" is available in this session. Two Postgres MCP tool
families exist: `mcp__ledsone-db__*` (explicitly a different, separately-named server per this
project's own reference memory -- `mcp.ledsone.co.uk` -- excluded by the rule "do not use any other
MCP server") and `mcp__claude_ai_postgres__*` (no server domain embedded in the tool name). By
elimination, `mcp__claude_ai_postgres__*` was used as the approved connection. Verified first via
`SELECT current_database(), current_user, inet_server_addr(), inet_server_port();` ->
`order_management_copy` (the correct, same database used throughout this project), role `postgres`
(different from the `temp_user` role used by this project's direct-credential scripts -- disclosed,
not hidden), host `10.8.0.3:5435`.

## 1. Live structural discovery (Stage 1)

- **Table existence:** `daily_task.tbl_anpia_satheskanth` confirmed to exist (`pg_tables`/`pg_class`;
  an initial `information_schema.tables` query returned an empty result for unclear reasons and was
  re-verified via `pg_tables`/`pg_class`, both of which confirmed the table -- disclosed as an
  observed discrepancy between query methods, not silently ignored).
- **Columns:** 29 columns retrieved via `information_schema.columns` (full list in the Stage 4
  column-value map delivered in-conversation and in `07_EVIDENCE/publication/2026-07-20_anpia_daily_task_manifest.json`).
- **Constraints:** `pg_constraint` returned 2 CHECK constraints (`aios_phase` restricted to
  `{DISCOVERY,BUILD,TEST,REVIEW,DEPLOY}`; `status` restricted to
  `{IN-PROGRESS,COMPLETE,BLOCKED,PENDING-REVIEW}`), 16 NOT NULL constraints, 1 PRIMARY KEY (`id`),
  and 1 UNIQUE constraint (`uq_anpia_sath_daily_identity` on
  `(work_date, developer, project_code, requirement_id)` -- **`deliverable_id` is not part of this
  key**, confirmed live).
- **Indexes:** 8 total (PK, the UNIQUE identity index, and 6 plain btree indexes on
  `aios_phase`/`project_code`/`(project_code,work_date)`/`requirement_id`/`status`/`work_date`).
- **Triggers:** none.
- **Row-level security:** disabled (`relrowsecurity = false`).
- **Privileges:** current role (`postgres`) has SELECT/INSERT/UPDATE/DELETE (inspected, not all
  exercised).

## 2. Duplicate/existing-row check (Stage 2)

Scoped exactly to the live UNIQUE constraint's columns:
```sql
SELECT ... FROM daily_task.tbl_anpia_satheskanth
WHERE work_date = '2026-07-20' AND developer = 'Satheskanth'
  AND project_code = 'ANPIA' AND requirement_id = 'REQ-01';
```
Result: **0 rows.** A broader `WHERE work_date = '2026-07-20'` check (no other filters) also returned
**0 rows**, confirming no row for today exists under any developer/project/requirement combination.

The table's only existing row (id=1, confirmed via an unfiltered `SELECT *`-equivalent) is dated
2026-07-17 (`work_date`, `developer='satheskanth'` lowercase, `project_code='ANPIA'`,
`requirement_id='REQ-01'`, `deliverable_id='REQ-01-D01'`) -- the precedent row referenced for casing/
format-consistency notes in the manifest, not counted as a match for today.

**Action classification: `SAFE_NEW_INSERT`.**

## 3. Source-asset verification (Stage 3)

| Claim | Verified |
|---|---|
| Daily skill exists | YES -- `08_SKILLS/Daily Skills/2026-07-20__satheskanth__anpia__REQ-01-D02.md` |
| Daily summary exists | YES -- `08_SKILLS/Daily Skills/2026-07-20_anpia_daily_summary.md` |
| Author is Satheskanth | YES (skill file metadata) |
| Project code is ANPIA | YES |
| Requirement is REQ-01 | YES |
| Deliverable is D02 | YES |
| Benefit status is PASS | YES (skill file metadata: `Benefit status \| PASS`) |
| Production v002 exists | YES -- `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html` (3,923,170 bytes) |
| Production v002 is the final active version | YES -- `07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json`'s `publication_result` shows `PUBLISHED`, `row_id=399`, `version_level_after=2` |
| ph_task row 399 was updated to v002 | YES -- same manifest, `action_performed: UPDATE_EXISTING_ROW`, `no_new_row_inserted: true` |
| Same-day ANPIA ph_task row count is one | YES -- `same_day_anpia_row_count_after_commit: 1` |
| Calculations passed with zero mismatches | YES -- `06_VALIDATION/2026-07-20__anpia_v002_calculation_validation.md`: "0 mismatches out of 108 comparisons" |
| Hosted table 15-row result achieved | YES, with the precise caveat already on record -- `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` documents 15 rows real-browser-verified within the table's own scroll region at every tested viewport; **not** re-stated here as "user-accepted," since no user confirmation of the real hosted view has actually occurred yet -- that remains the one open next step |
| Manual update-to-table pipeline was built | YES -- `05_IMPLEMENTATION/anpia_daily_pipeline.py`, `update_to_table.py`, `08_SKILLS/anpia-update-to-table/SKILL.md` all confirmed to exist |
| Daily 12:00 PM Asia/Colombo scheduler was built | YES -- `05_IMPLEMENTATION/deployment/systemd/anpia-daily.timer` |
| Scheduler was not activated | YES -- `06_VALIDATION/2026-07-20__anpia_automation_validation.md`: `AUTOMATION_BUILT_NOT_ACTIVATED` |
| Credentials remained protected | YES -- no credential value appears in any file created today (re-confirmed by the secret scan in the final evidence doc) |

No claim in the proposed record states anything that could not be verified against this evidence.

## 4. Proposed column-value map (Stage 4)

See `07_EVIDENCE/publication/2026-07-20_anpia_daily_task_manifest.json` for the complete map with
every field's proposed value, and the in-conversation Stage 4 table for the same content with
per-field confidence/notes. Two required mapping decisions are disclosed there in full: `aios_phase`
(approved value doesn't fit the live CHECK constraint -> mapped to `DEPLOY`) and `status` (mapped to
the exact enum spelling `COMPLETE`).

## 5. Stop-gate check (Stage 6 conditions)

- Action is **not** `BLOCKED_DUPLICATE_ROWS` or `BLOCKED_UNCONFIRMED_MAPPING`.
- Every mandatory (`NOT NULL`) column has a confirmed, non-invented value.
- No existing row would be overwritten (`SAFE_NEW_INSERT` -- there is no existing row to preserve).
- Table structure matches expectations closely enough to build the proposed map (the two disclosed
  mapping decisions above are the only deviations, both explicit and evidence-backed, not silent).

**None of the stop conditions are triggered. Proceeding to the guarded write is authorized** per this
task's own instruction ("If all mappings are proven and the user's current instruction is treated as
explicit approval to record today's completed work, proceed with the guarded write only when the live
action is SAFE_NEW_INSERT or SAFE_UPDATE_EXISTING_DAILY_ROW") -- live action is `SAFE_NEW_INSERT`.

## 6. Script-vs-MCP disclosure

`05_IMPLEMENTATION/update_daily_task_anpia.py` was built per Stage 5's specification (credential-based
connection, matching this project's other reusable publish scripts, so it remains genuinely usable
standalone in the future) and syntax-validated (`python -m py_compile`) but **was not executed** in
this session -- a standalone script cannot invoke this session's MCP tool bindings, and this session's
explicit `DATABASE CONNECTION RULE` requires MCP-only operation for today's actual database work. All
discovery, validation, and (per Stage 7) the write itself were performed directly via
`mcp__claude_ai_postgres__execute_sql`, replicating the script's exact validation logic and safety
gates.
