# Evidence: ph_task Read-Only Inspection

**Requirement:** REQ-01-D02 -- ANPIA
**Date:** 2026-07-20
**Database writes performed during inspection:** ZERO

## 1. Connection evidence

Every inspection query ran through `05_IMPLEMENTATION/src/anpia_db_connection.get_connection()`,
which issues `SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY` (session-level, not just a single
transaction) before any query executes. Confirmed live via `SHOW transaction_read_only` returning
`on` in every inspection script run in this task.

## 2. Structural inspection evidence (source: scratchpad `inspect_ph_task.py`, read-only)

Queries executed (all read-only `information_schema` / `pg_catalog` lookups):
- `information_schema.columns` -- full column list, types, nullability, identity metadata.
- `pg_attribute` + `col_description()` -- column comments.
- `obj_description()` -- table comment.
- `pg_constraint` + `pg_get_constraintdef()` -- constraints (PK only; no `task_id` UNIQUE live).
- `pg_indexes` -- indexes.
- `pg_trigger` -- triggers (none found).
- `pg_class.relrowsecurity` -- RLS disabled.
- `pg_get_userbyid(relowner)` -- table owner.
- `has_table_privilege(...)` x5 -- current role's SELECT/INSERT/UPDATE/DELETE/TRUNCATE privilege
  booleans (inspected only, never exercised for write privileges).
- `COUNT(*)` -- row count (271 at time of this script's run).

## 3. Row-convention inspection evidence (source: scratchpad `inspect_ph_task_rows.py`, read-only)

Queries executed (all parameterized or literal read-only `SELECT`s, no string-built predicates on
user input):
- Targeted ILIKE search across `project_name`/`project_code`/`task_name`/`assigned_user`/`developer`
  for no-moving/ANPIA/Nivarnan/Satheskanth patterns.
- 10 most recent rows overall (safe fields only -- `html_content` never printed, only presence/length).
- `GROUP BY` distinct-value summaries for `team`, `assigned_user_team`, `version_status`,
  `phase_level`.
- Distinct `developer` values matching `sath`.
- HTML content size distribution (`MIN`/`MAX`/`AVG` octet length).
- `task_id` uniqueness check (`COUNT(*)` vs `COUNT(DISTINCT task_id)`).

## 4. Final re-verification (this task, immediately before writing evidence docs)

Re-ran the duplicate/topic search live via a fresh read-only connection. Findings:
- `project_code = 'ANPIA' AND assigned_user = 'Nivarnan'`: **0 rows** (confirmed, matches script's
  live `check_duplicates()` behavior used by the dry-run).
- Broader ILIKE search (no-moving/ANPIA/Nivarnan): **3 rows**, all under `project_code = 'AGE'`,
  `developer = 'Narthanan'` -- see `03_DISCOVERY/2026-07-20__ph_task_schema_and_value_inspection.md`
  section 5 for full detail. Row id=56 ("Amazon UK No-Moving Products Report") is topically
  near-identical to this report.
- Row count: 275 (was 271 at original inspection). The +4 rows (ids 375-378) are a fully unrelated
  automated eBay-project insert batch, timestamped `2026-07-20 14:29:05`, confirmed via direct
  inspection of those rows' `project_code`/`developer`/`assigned_user`/`created_at` fields -- none
  overlap with ANPIA, Nivarnan, or Satheskanth.

## 5. Privacy discipline confirmed

At no point in any inspection query was `html_content` selected in full -- only
`(html_content IS NOT NULL)` and `octet_length(html_content)` were read, per the task's
privacy-conscious inspection instruction. No row's full HTML payload was ever printed or logged.

## 6. Conclusion

All inspection was performed read-only, via a session-level read-only transaction, using
parameterized/literal SQL only. Zero writes occurred. The row-count discrepancy and the newly
surfaced near-duplicate (AGE id=56) are both fully explained and documented above and in the
corrected manifest.
