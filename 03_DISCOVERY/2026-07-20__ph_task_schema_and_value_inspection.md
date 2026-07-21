# Discovery: tech_team_outputs.ph_task Schema and Value Inspection

**Requirement:** REQ-01-D02 (cross-ref REQ-AMZ-NMP-001-D01) -- ANPIA
**Date:** 2026-07-20
**Mode:** Read-only (`BEGIN; SET TRANSACTION READ ONLY;` session, via `anpia_db_connection.get_connection()`)
**Database writes performed:** ZERO

## 1. Purpose

Inspect `tech_team_outputs.ph_task` structurally and by row-convention, in strict read-only mode, to
determine safe, evidence-based candidate values for a future ANPIA v007 publication row -- without
inserting, updating, or deleting anything.

## 2. Connection

- Database: `order_management_copy`
- Role: `temp_user`
- SSL: off
- `SHOW transaction_read_only` confirmed `on` for the full duration of every inspection script run.

## 3. Structural findings

- Columns (ordinal order): `id` (identity PK), `project_name`, `project_code`, `task_name`, `task_id`,
  `team`, `developer`, `assigned_user`, `assigned_user_team`, `html_content` (text), `description`,
  `phase_level` (int), `version_level` (int), `version_status` (text, enum-like by convention only --
  not a DB-enforced enum type), `created_at`, `updated_at`.
- **Constraints:** primary key on `id` only. No `UNIQUE` constraint exists on `task_id` at the live
  schema level, despite the reference script `Sources/db_access_templates/update_table.py` documenting
  one in its DDL docstring. Confirmed via `pg_constraint` that the constraint is not present.
- **Triggers:** none.
- **Row-level security:** disabled (`relrowsecurity = false`).
- **Owner / privileges:** current role (`temp_user`) confirmed `SELECT`-capable; `INSERT`/`UPDATE`/
  `DELETE`/`TRUNCATE` privilege booleans were also inspected (read-only inspection, not exercised).
- **Column comments:** present on several columns describing intended conventions (e.g.
  `assigned_user_team` NULL-safe backfill convention).

## 4. Row-convention findings (as of original inspection, 271 total rows)

- `team`: dominant values include `Technical` and `PH Team`. The same developer (Satheskanth) uses
  both across different projects -- **not** a fixed per-developer constant.
- `assigned_user_team`: dominant convention `ph_priors` (216 of 271 rows); other values include
  `ebay_priors`, `ah_priors`; NULL is a valid, documented "not yet backfilled" state.
- `version_status`: live distinct values are `released` (224), `completed` (38), `active` (4),
  `Released` (2, stray case variant), `retired` (2), `rejected` (1). **No value represents a
  "deferred / pending review" state.**
- `phase_level`: dominant value `1` (182 of 271 rows, 67%).
- `developer`: exact live capitalization for this project's developer confirmed as `Satheskanth`.
- HTML content size precedent: existing rows range up to ~18.2 MB, comfortably covering v007's
  3,922,103 bytes.
- `task_id` duplication: 12 of 267 non-null `task_id` values were already duplicated at original
  inspection, consistent with the missing `UNIQUE` constraint above.

## 5. Duplicate / near-duplicate search -- IMPORTANT CORRECTION ON FINAL RE-VERIFICATION

An initial broad ILIKE search (`project_name`/`project_code`/`task_name`/`assigned_user`/`developer`
against no-moving/ANPIA/Nivarnan/Satheskanth patterns) and a script-level exact-match check
(`project_code = 'ANPIA' AND assigned_user = 'Nivarnan'`) were both run. The exact-match check
correctly and consistently returns **0 rows** for `project_code = 'ANPIA'`.

However, on final re-verification before writing this document, the broader search surfaced **3
existing rows** where `assigned_user = 'Nivarnan'` under a **different** `project_code` (`AGE` /
`Amazon_Grow_Engine`, developer `Narthanan`):

| id | task_name | task_id | version_status | created_at |
|----|-----------|---------|-----------------|------------|
| 56 | Amazon UK No-Moving Products Report | AUNMP-2026-06-25-V1 | released | 2026-07-02 |
| 57 | Amazon UK Price Erosion Monitoring & Control Report | AUPEM-2026-06-16-V1 | released | 2026-07-03 |
| 112 | Inventory Optimization for High-Performing ASINs | AGE-TOPASIN-INV-2026-07-03-V1 | released | 2026-07-07 |

Row **id=56 is topically near-identical** to this ANPIA report: same subject (No-Moving Products,
Issue Diagnosis and Action Report), same `assigned_user` (Nivarnan), `version_status='released'`
(i.e. treated as a live, published artifact -- not a draft). It differs in scope (UK-only vs. this
report's UK/DE/FR/IT), `project_code` (`AGE` vs `ANPIA`), and `developer` (`Narthanan` vs
`Satheskanth`).

This directly affects the duplicate-risk classification -- see
`07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json`, which was corrected
from `SAFE_NEW_INSERT` to `BLOCKED_AMBIGUOUS` as a result. Full detail in
`07_EVIDENCE/validation/2026-07-20__ph_task_read_only_inspection_evidence.md`.

## 6. Row-count integrity check

- Row count at original inspection: **271**.
- Row count at final re-verification: **275** (+4).
- The +4 rows (ids 375-378) were all created at `2026-07-20 14:29:05` by an unrelated automated
  process: `project_code='ebra'` (eBay Return Analysis Dashboard), `developer='Abiraj'`, assigned to
  Thinesh/Jarsini/kobiga/powsteena. None reference ANPIA, no-moving products, Nivarnan, or
  Satheskanth. This confirms `ph_task` is an actively written-to, shared production table, and that
  the row-count change is unrelated to this task's read-only inspection and dry-run testing.

## 7. Conclusion

Structural and row-convention discovery is complete. The candidate publication values, their
confidence levels, and the corrected `BLOCKED_AMBIGUOUS` duplicate-risk classification are recorded
in the manifest. **No database writes were performed at any point during this discovery.**
