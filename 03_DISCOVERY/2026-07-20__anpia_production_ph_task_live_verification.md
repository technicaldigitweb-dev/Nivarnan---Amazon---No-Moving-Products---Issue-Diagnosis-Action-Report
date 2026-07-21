# Discovery: Live ph_task Verification for ANPIA Production Publication

**Requirement:** REQ-01-D02 -- ANPIA
**Date:** 2026-07-20
**Mode:** Read-only (session-level `SET TRANSACTION READ ONLY`)
**Database writes performed:** ZERO
**Scope discipline:** All row-convention inspection below was scoped to `project_code = 'ANPIA'`
and/or `assigned_user = 'Nivarnan'`. `project_code = 'AGE'` was never queried in this task. One
unavoidable broad sample (`action_took_by IS NOT NULL`, to understand that column's live usage
pattern) surfaced other unrelated project codes (`WLSP`, `PH-SALES`, `epc`) but **no AGE rows** --
none appeared, so none were excluded; had any appeared they would have been ignored per instruction.

## 1. Connection

Database `order_management_copy`, role `temp_user`, SSL off. `SHOW transaction_read_only` = `on` for
every query in this verification.

## 2. Schema drift since the original (pre-production) inspection

The live schema has changed since the last inspection in this project (see
`03_DISCOVERY/2026-07-20__ph_task_schema_and_value_inspection.md`). **Two columns were added:**

- `action_took_by` (text, nullable) -- "End user who completed the requested action (NULL until done)."
- `action_took_date_time` (timestamptz, nullable) -- "Timestamp when the action was completed (NULL until done)."

Current live column list (18 columns, ordinal positions 1-17 and 19 -- position 18 is a gap left by
a previously dropped column, confirming this table has had at least one other schema change in its
history beyond what was tracked in this project):

| Pos | Column | Type | Nullable | Default |
|---|---|---|---|---|
| 1 | id | integer | NO | (identity) |
| 2 | project_name | text | NO | -- |
| 3 | project_code | text | NO | -- |
| 4 | task_name | text | NO | -- |
| 5 | task_id | text | YES | -- |
| 6 | team | text | YES | -- |
| 7 | developer | text | YES | -- |
| 8 | assigned_user | text | YES | -- |
| 9 | html_content | text | YES | -- |
| 10 | description | text | YES | -- |
| 11 | phase_level | integer | NO | 0 |
| 12 | version_level | integer | NO | 0 |
| 13 | version_status | text | YES | -- |
| 14 | action_took_by | text | YES | -- |
| 15 | action_took_date_time | timestamptz | YES | -- |
| 16 | created_at | timestamptz | YES | now() |
| 17 | updated_at | timestamptz | YES | now() |
| 19 | assigned_user_team | text | YES | -- |

Constraints: PK on `id`; `NOT NULL` on `id`, `project_name`, `project_code`, `task_name`,
`phase_level`, `version_level`. **No `UNIQUE` constraint on `task_id`** (confirmed again). Indexes
exist on `assigned_user`, `version_status`, `developer`, `created_at`, `task_name`, `project_code`,
`assigned_user_team` (all plain btree, none unique). No triggers. RLS disabled. Table owner
`postgres`. Current role (`temp_user`) has SELECT/INSERT/UPDATE/DELETE privileges (inspected only,
not exercised).

## 3. Column comments -- authoritative, structural evidence (not row-inferred)

The table and every column carry descriptive comments, which is a stronger source of truth than
row-convention inference. Key findings:

- **Table comment:** "Task feed for the hosted tool. Developers publish periodic (e.g.
  weekly/monthly) tasks here, with the task content authored as HTML in `html_content`. End users
  view that HTML in the tool, perform the action the task instructs, and the row records who
  completed the action (`action_took_by`) and when (`action_took_date_time`), along with version and
  phase tracking."
- **`team`:** "Team responsible for the developed task. Ex: Development, Technical" -- the comment
  itself names `Technical` as a valid example value. This is now a **structural**, not merely
  row-inferred, basis for `team = 'Technical'`.
- **`version_status`:** "Status of the current version: **released, completed, rejected**." This is
  the authoritative, documented value set -- narrower than the full set of live legacy values found
  in the general table (`released`, `completed`, `active`, `Released`, `retired`, `rejected`), which
  includes values not sanctioned by the current column comment (likely legacy/pre-convention rows).
  **Critically: there is no "draft" / "pending" / "deferred" value in the documented convention.**
  This *resolves* the previously-unresolved `version_status` conflict from the earlier ph_task task:
  the schema is designed such that a row is only ever created once a real released/completed/rejected
  decision exists -- there is no schema-level way to represent "awaiting confirmation." This confirms
  the correctness of not inserting any row during Stage 1.
- **`assigned_user_team`:** "Which board this task feeds: `ph_priors` or `ebay_priors`. Nullable,
  developer-set (like team/developer). NULL rows appear on neither board until backfilled." This
  documents exactly two valid non-null values and confirms NULL is a legitimate, documented default
  -- not a guess.
- **`action_took_by` / `action_took_date_time`:** always NULL at row-creation time by design; they
  record the *end user's* completion action after the fact, not the developer/publisher.
- **`html_content`:** "Task content authored by the developer as HTML; rendered to the end user in
  the hosted tool."
- **No `pass_fail` column exists.** A targeted search (`column_name ILIKE '%pass%' OR '%fail%'`)
  found nothing. Per this task's Section 10 instruction ("use only columns that actually exist"),
  `pass_fail` is omitted from the proposed column-value table entirely.
- **No dedicated filename/path/report-date/active-flag column exists.** A targeted search
  (`%filename%`, `%path%`, `%active%`, `%status%`, `%date%`, `%day%`) found only `version_status`,
  `action_took_date_time`, and `updated_at` -- none of which are a dedicated report-date, filename,
  path, or boolean-active field. **Conclusion:** the production filename and report date must be
  communicated through `task_name`/`task_id`/`description` text if needed; there is no structured
  column for them, and "one active row" is a convention enforced by application logic /
  human process, not a database constraint or flag.

## 4. ANPIA-only duplicate/identity check (AGE excluded)

| Query | Result |
|---|---|
| `project_code = 'ANPIA'` (exact) | **0 rows** |
| `project_code ILIKE 'anpia'` (case-insensitive, catches case variants) | **0 rows** |
| `project_code = 'ANPIA' AND assigned_user = 'Nivarnan'` | **0 rows** |

**No ANPIA row of any kind exists in `ph_task`.** There is therefore no same-day row, no prior
version, and no existing convention row to compare against for this project specifically. This is a
clean, unambiguous **SAFE_NEW_INSERT** state from the ANPIA-only perspective (see
`06_VALIDATION`/manifest for the final classification).

## 5. Row count integrity

Row count observed during this verification: **283** (continues to climb from 271 -> 275 -> 283
across this project's ph_task work sessions, consistent with `ph_task` being an actively
written-to, shared production table used by many other teams/projects -- not something this task's
read-only inspection affects).

## 6. Consequence for proposed column values (Section 10 of the production task)

Because zero ANPIA rows exist, per this task's own instruction ("If a required value cannot be
proven from actual table structure, relevant ANPIA rows, or approved project instructions, mark it
as UNCONFIRMED. Do not invent a value.") most row-convention-dependent fields are legitimately
**UNCONFIRMED**, resolved only where:
(a) the value is given directly by approved project instruction (`project_code`, `assigned_user`),
(b) the value is structurally evidenced by a column comment (`team = 'Technical'` example;
`version_status` documented set; `assigned_user_team` documented set/NULL-safety), or
(c) the value is structurally required and derivable from this project's own established identity
(e.g. `developer` = the consistent author identity used throughout this project's requirement/
handover documents).

Full field-by-field table is in `06_VALIDATION/2026-07-20__anpia_production_live_data_validation.md`
and the production manifest.

## 7. Conclusion

Live schema re-verified, ANPIA-only duplicate check confirms a clean `SAFE_NEW_INSERT` state (no
AGE contamination), and the documented `version_status` value set structurally confirms that no row
should be created until a real publication decision is made -- consistent with this task remaining
at Stage 1 (no writes). Zero database writes were performed during this verification.
