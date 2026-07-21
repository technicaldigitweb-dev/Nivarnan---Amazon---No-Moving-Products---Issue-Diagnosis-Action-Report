# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System

**Template used:** `08_SKILLS/skill file creation rules/SKILL_DAILY_TEMPLATE 2.md`
**Rules used:** `08_SKILLS/skill file creation rules/Skill File Creation Updated (1).md`
**Path note:** the task that requested this file referenced these two files under
`08_SKILLS/Daily Skills/skill file creation rules/...`. The actual files live one level up, at
`08_SKILLS/skill file creation rules/...` (no `Daily Skills/` segment). Both were located and read in
full before writing anything here — flagged as a path discrepancy, not silently corrected elsewhere.
**Naming/date-format:** YYYY-MM-DD used throughout (metadata `date` field and filename), matching the
rules file's explicit standard and the 2026-07-17 precedent file in this same folder.

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| date | 2026-07-20 |
| developer | satheskanth |
| project | No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report |
| project_code | ANPIA |
| phase | IMPLEMENTATION / PRODUCTION DELIVERY |
| requirement_id | REQ-01 |
| deliverable_id | D02 |
| status | COMPLETE |
| evidence_location | `06_VALIDATION/`, `07_EVIDENCE/publication/`, `07_EVIDENCE/validation/`, `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/`, `09_OUTPUTS/html/production/`, `10_HANDOVER/` — exact files cited throughout this document |
| blos_keys_used | NONE USED |
| hardcoded_thresholds | NONE (the `50,000,000`-byte HTML sanity ceiling and the `984px`/`373px` row-density CSS values used in the publish scripts and the v008 template are disclosed, real-browser-measured implementation constants, not business thresholds — see §8) |
| three_am_standard | PASS |
| llm_queryable | YES |
| company_knowledge_candidate | YES |
| domain | Amazon Advertising / Inventory / Ecommerce Operations |
| User | Nivarnan |
| Benefit status | PASS |

## File path:
`08_SKILLS/Daily Skills/2026-07-20__satheskanth__anpia__REQ-01-D02.md`

**Identity discipline note:** `project_code = ANPIA`, `assigned_user = Nivarnan` throughout — the
only production identity used or referenced anywhere in this file.

---

## Benefit Status Statement

**Benefit delivered: YES. PASS.**

A production-quality Amazon No-Moving Products report was built from fresh live data, validated with
zero calculation mismatches and zero browser console errors, and published to
`tech_team_outputs.ph_task` — first as a new row (v001, id=399), then corrected in place to v002
after a user-reported UX defect was fixed. A reusable daily pipeline, a manual "update to table"
command, and a complete (but intentionally inactive) future scheduling system were also built today.

---

## 1. SYSTEM STATE

**Current system state at the start of today's session:** `tech_team_outputs.ph_task` row id=399 held
the v001 ANPIA production report (published in the immediately preceding session on this same date),
with `version_level=1`, `version_status=released`. Local file
`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` existed. No automation, no manual
publication command, and no scheduler existed yet.

**What was working:** the full extraction -> enrichment -> compact-dataset -> compression -> template
-> browser-decompression pipeline (proven across the v001-v007 development cycle and the v001
production build); the safety-gated `publish_ph_task_production_report.py` INSERT path.

**What was broken / missing:** the user reported that the hosted view of v001 showed only
approximately 5 rows of the data table, with excessive surrounding whitespace — this session started
with that specific defect and no automation of any kind.

**Starting point:** two distinct instructions from the business/technical owner: (1) fix the row-
density defect and publish it as a corrected v002, replacing v001 in place (one active row rule); (2)
build a complete, reusable daily production pipeline plus a disabled future 12:00 PM Asia/Colombo
scheduler.

---

## 2. WHAT CHANGED TODAY

- **Change 1 — v001 published (first production publication of the day):** fresh live 30-day
  extraction (268,404 rows, 0 duplicate keys), 53,843-identity compact dataset, 0/108 calculation
  mismatches against an independent Python recomputation, 0 browser console errors at both required
  viewports. Published as a new `ph_task` row (id=399) via a safety-gated INSERT script requiring
  four independent conditions (execute flag, confirmation token, approved-manifest checksum,
  live-matched expected action) before any write. Evidence: `06_VALIDATION/2026-07-20__anpia_production_live_data_validation.md`,
  `06_VALIDATION/2026-07-20__anpia_production_html_browser_validation.md`,
  `07_EVIDENCE/validation/2026-07-20__anpia_production_calculation_reconciliation.md`,
  `07_EVIDENCE/validation/2026-07-20__anpia_production_ph_task_dry_run.md`,
  `07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json`.

- **Change 2 — Row-density root cause diagnosed by real-browser measurement, not guesswork:** no
  screenshot was actually attached to the defect report despite the instruction referring to "the
  supplied screenshot" — this was disclosed honestly (`07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/user-reported-defect/DEFECT_RECORD.md`)
  rather than fabricated. Instead, v001's real behavior was measured directly in headless Chrome:
  `.table-wrap` used `max-height` with a 420px floor and a measured 75px row height, producing exactly
  **4** complete rows at any hosted viewport <=800px tall — closely matching the reported "~5 rows."

- **Change 3 — v002 built: fresh data + row-density fix, zero text shrinkage:** a new template,
  `05_IMPLEMENTATION/templates/amazon_no_moving_report_template_v008.html`, tightens cell/section
  padding (row height 75px -> 61px, real-browser-measured) and replaces `max-height` with
  `height: clamp(984px, calc(100vh - 373px), 1100px)`. Result: **15 rows** reliably reachable within
  the table's own scroll region at every tested viewport (1920x1080 and 1366x768, both direct and a
  disclosed hosted-modal simulation), up from 4-8 in v001 — real-browser-verified, **no font-size was
  reduced anywhere**. Built from a second, independent fresh 30-day extraction (not reused from v001).
  Evidence: `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` (includes an honest breakdown of
  what "15 rows visible" does and doesn't mean, given the mathematical impossibility of fitting
  required toolbar/summary UI plus 15 full rows into a single unscrolled screenshot at a realistic
  hosted height), `06_VALIDATION/2026-07-20__anpia_v002_calculation_validation.md` (0/108 mismatches).

- **Change 4 — Row 399 updated to v002 (not a second row):** `publish_ph_task_production_report.py`
  was extended with a new, independently gate-tested `UPDATE_EXISTING_ROW` path (parameterized
  `UPDATE ... WHERE id = %s AND project_code = %s AND assigned_user = %s`, touching only
  `html_content`/`description`/`version_level`/`version_status`/`updated_at`). Pre-publication gate
  re-read row 399 live immediately before writing and confirmed every expected value matched exactly.
  Post-commit: `version_level=2`, stored checksum matches v002 exactly, same-day ANPIA row count still
  exactly 1, total `ph_task` row count unchanged (284) confirming an UPDATE occurred, not an INSERT.
  Evidence: `06_VALIDATION/2026-07-20__anpia_v002_publication_validation.md`,
  `07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`,
  `07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json`.

- **Change 5 — Reusable central pipeline built:** `05_IMPLEMENTATION/anpia_daily_pipeline.py`, a
  16-step, Python-only (no Node dependency on the core path) pipeline: lock -> env -> source check ->
  latest-date -> fresh extraction -> build -> validate -> smoke-check -> filename/checksum validate ->
  duplicate-state inspect -> insert-or-update -> reread/verify -> evidence -> structured JSON run log
  -> release lock -> deterministic exit code (0/2/3/4/5/6/7). Real dry-run executed successfully
  end-to-end against live data; lock-contention (exit 7) and missing-token (exit 2) gates also tested
  live. Evidence: `07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md`.

- **Change 6 — Manual "update to table" command built:** `05_IMPLEMENTATION/update_to_table.py`
  (fixed-argument-only wrapper, no free-text interpretation of any kind) and
  `08_SKILLS/anpia-update-to-table/SKILL.md` (the Claude Code operator instruction for the trigger
  phrase). Real dry-run executed successfully. Evidence:
  `07_EVIDENCE/validation/2026-07-20__anpia_update_to_table_command_evidence.md`.

- **Change 7 — Future scheduler built, explicitly not activated:** systemd service + timer (daily
  12:00 Asia/Colombo, `Persistent=true`, `RandomizedDelaySec=0`, hardened, non-root), install/remove/
  check scripts, a cron fallback (reference only), and a deployment README documenting every
  placeholder a future operator must fill in. Nothing installed, enabled, started, or scheduled
  anywhere. Status: `AUTOMATION_BUILT_NOT_ACTIVATED`. Evidence:
  `06_VALIDATION/2026-07-20__anpia_automation_validation.md`,
  `10_HANDOVER/2026-07-20__anpia_v002_and_automation_handover.md`.

**Evidence reference (full list):**
`06_VALIDATION/2026-07-20__anpia_production_live_data_validation.md` ·
`06_VALIDATION/2026-07-20__anpia_production_html_browser_validation.md` ·
`06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` ·
`06_VALIDATION/2026-07-20__anpia_v002_calculation_validation.md` ·
`06_VALIDATION/2026-07-20__anpia_v002_publication_validation.md` ·
`06_VALIDATION/2026-07-20__anpia_automation_validation.md` ·
`07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json` ·
`07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v002_ph_task_manifest.json` ·
`07_EVIDENCE/validation/2026-07-20__anpia_production_calculation_reconciliation.md` ·
`07_EVIDENCE/validation/2026-07-20__anpia_production_ph_task_dry_run.md` ·
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md` ·
`07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md` ·
`07_EVIDENCE/validation/2026-07-20__anpia_update_to_table_command_evidence.md` ·
`07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/validated/browser_results.json` (+6 PNGs) ·
`07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/user-reported-defect/DEFECT_RECORD.md` ·
`10_HANDOVER/2026-07-20__anpia_production_publication_preconfirmation_handover.md` ·
`10_HANDOVER/2026-07-20__anpia_v002_and_automation_handover.md` ·
`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` (preserved, unchanged) ·
`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html` (current active production report)

---

## 3. POSTGRESQL / MCP / DATABASE FINDING

**Table(s) involved:** `tech_team_outputs.ph_task` (PostgreSQL, database `order_management_copy`,
direct `psycopg2` connection via `05_IMPLEMENTATION/src/anpia_config.py`/`anpia_db_connection.py`).

**Finding:** live re-inspection this session confirmed `ph_task`'s documented value set for
`version_status` is exactly `released` / `completed` / `rejected` (per the live column comment) —
there is no "pending/awaiting confirmation" state representable in the schema. Two columns
(`action_took_by`, `action_took_date_time`) exist and are correctly left `NULL` at publish time
(populated later, by the hosted tool, when the end user acts) — confirmed via column comment and
preserved unchanged by both the INSERT and UPDATE code paths built today. No `UNIQUE` constraint
exists on `task_id`; the "one active row" rule is enforced entirely by application-level checks
(`project_code + assigned_user`), not by the database schema.

**SQL logic/pattern discovered (the new UPDATE path):**
```sql
UPDATE tech_team_outputs.ph_task
SET html_content = %s, description = %s, version_level = %s, version_status = %s, updated_at = now()
WHERE id = %s AND project_code = %s AND assigned_user = %s
RETURNING id, project_code, assigned_user, version_level, version_status, updated_at
```
Never a bare `id`-only match — the `WHERE` clause always re-asserts `project_code`/`assigned_user` so
a stale or incorrect target id cannot silently touch the wrong row.

**Operational meaning:** publishing a corrected version of an ANPIA report is a live, parameterized
`UPDATE` against the single existing row for that `project_code`+`assigned_user`, not a fresh
`INSERT` — see §4 for a real conflict this created against a separate, pre-existing company
convention.

---

## 4. GAP FOUND

**Gap description — real, evidence-based, discovered today:** `08_SKILLS/ph_task_reference/ph_task_versioning_rules.md`
(existing company reference, dated 2026-07-08) documents that the standard company procedure for
releasing a new version of a `ph_task` row is to **INSERT a new row** (incrementing `version_level`)
and **set the OLD row's `version_status = 'rejected'`** — specifically because the hosted dashboard's
Pending/Completed views hide `rejected` rows, which is how the documented convention achieves "only
the newest version shows." Today's v002 publication instead **updated row 399 in place** — same row
id, `version_level` incremented from 1 to 2, `version_status` re-asserted as `released` (never set to
`rejected`, because there was never a second row to distinguish it from). This was done under
explicit, repeated instruction from the business/technical owner ("Update the existing row id=399 to
v002... Do not insert another same-day row"), not by mistake, and it does satisfy the same end goal
(exactly one visible row) — but it is a genuine deviation from the documented default company
procedure for `ph_task` versioning.

**Impact if unresolved:** (1) `created_at` on row 399 still reflects the *original* v001 publication
time, not the v002 correction — any future reporting that assumes `created_at` approximates "when
this version was released" will be misled for ANPIA specifically. (2) There is no database-level
historical trail of v001's exact stored content any more (only the local file preserves it) — the
insert+reject pattern would have kept both rows queryable in the database. (3) Future ANPIA runs (via
`anpia_daily_pipeline.py`, which also implements UPDATE-in-place for the `UPDATE_EXISTING_ROW`
action) will continue this same pattern unless explicitly changed.

**Recommended action:** route this specific conflict — "should ANPIA continue update-in-place, or
should it switch to the documented insert+reject pattern?" — to whoever owns `ph_task` dashboard
conventions (the same audience as `ph_task_versioning_rules.md`'s "For: Vithushali" / "check with the
dev team" note). If update-in-place is confirmed correct for ANPIA (e.g. because the dashboard
doesn't need per-version history, only the current state), `ph_task_versioning_rules.md` itself should
probably be amended to note ANPIA as a documented exception, so a future developer reading that
reference file doesn't assume today's approach was an error.

**Owner:** unassigned — needs routing per the above.

---

## 5. VALIDATION RULE ADDED OR CHANGED

**Rule name/ID:** UPDATE-path row-identity triple-check (extends the INSERT-path safety gates built
in the prior session).

**Condition checked:** a live `UPDATE_EXISTING_ROW` action is only permitted when three independent
signals agree: (1) the manifest's own declared `proposed_action` and `target_row_id`, (2) a live
re-query finding **exactly one** same-day `project_code`+`assigned_user` row whose id matches that
`target_row_id`, and (3) the operator's `--expected-action` CLI flag.

**What it prevents:** updating the wrong row (or updating when a second, unexpected row has appeared
since the manifest was written) — tested live today with a deliberately wrong `target_row_id` (999
instead of 399), which correctly fell through to `BLOCKED_UNCONFIRMED_COLUMN_RULE` rather than ever
being treated as a valid update target.

**Where implemented:** `05_IMPLEMENTATION/publish_ph_task_production_report.py`
(`check_anpia_only_duplicates`, `build_update_sql_and_params`, and the write-path branch in `main()`).

**BLOS reference:** none — this is a data-integrity/authorization guard, not a BLOS-governed business
threshold.

---

## 6. FAILURE MODE OR EDGE CASE

**Failure scenario:** the row-density fix (§2 Change 3) cannot be *perfectly* validated against the
real hosted tool, because no screenshot was ever actually attached to the defect report and this
session has no live access to the hosted tool's iframe/modal dimensions.

**How it is triggered:** any future difference between the real hosted container's available content
height and the disclosed simulation used today (~850px/700px, calibrated against the reported "~5
rows" symptom, not measured directly).

**How it is detected:** if the real hosted view still shows meaningfully fewer than ~15 rows after
v002, that is direct evidence the real container is shorter than simulated.

**Recovery procedure:** retune the `984px` floor and `373px` calc budget in `.table-wrap`
(`amazon_no_moving_report_template_v008.html`) using the exact same real-browser measurement
methodology already documented in `06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` (measure
real row/header height, recompute the floor for the target row count).

**Risk level:** LOW — the fix is a large, real, measured improvement regardless (4-8 rows -> 15 rows
in every tested condition); the only open question is whether "every tested condition" precisely
matches the one real condition (the actual hosted tool) that matters most.

---

## 7. DECISIONS MADE TODAY

**Decision 1 — Update row 399 in place rather than insert-and-reject.**
Alternatives considered: the documented company default (`ph_task_versioning_rules.md`) of inserting
a new row and marking the old one `rejected`.
Reason for choice: explicit, repeated business/technical-owner instruction specifically for ANPIA
("Keep only one ph_task publication... Update the existing row id=399... Do not insert another
same-day row").
Trade-off accepted: loses per-version database history (see §4 GAP) in exchange for a simpler,
single-row model that matches how ANPIA's `ph_task` row has been treated throughout this project.
Who approved: the business/technical owner, in the task instruction itself.

**Decision 2 — Disclose the missing defect screenshot rather than fabricate one.**
Alternatives considered: silently proceeding as if a screenshot had been reviewed, or inventing
plausible-sounding visual details.
Reason for choice: this project's standing discipline (evidence-first, no invented facts) applies
even when it would be easier to pretend. The defect was instead diagnosed from the text description
plus real-browser measurement of v001's actual behavior.
Trade-off accepted: the exact real hosted-container height remains unconfirmed (see §6).
Who approved: not separately approved -- a direct application of this project's existing standing
rule.

**Decision 3 — Fix row density via spacing only, never font-size.**
Alternatives considered: shrinking table font size to fit more rows.
Reason for choice: the task instruction explicitly required this ("Do not solve this by shrinking
text to an unreadable size").
Trade-off accepted: the achievable row-height reduction (75px -> 61px) is smaller than font-shrinking
would have allowed, so 15 rows required a larger `.table-wrap` floor (984px) than a font-shrink
approach would have needed -- accepted because it keeps every value equally readable.
Who approved: the task instruction itself (explicit constraint).

---

## 8. COMPANY KNOWLEDGE EXTRACT

### Business Rule:
A `ph_task` "one active row per project+user" requirement can be satisfied two different ways: the
documented company default (insert new + reject old, relying on the dashboard's `rejected`-hiding
behavior) or a simpler update-in-place model (used for ANPIA today, by explicit instruction). Both
achieve "exactly one visible row," but they are **not** equivalent for anyone who later needs
per-version history from the database itself -- see the open gap in §4.

### Operational Assumption:
The system assumes a fixed, non-secret confirmation token (`PUBLISH_NIVARNAN_ANPIA`) plus an
independently-computed manifest-file checksum are sufficient proof that a human reviewed and approved
specific column values before a write. This is not a credential -- it is a mechanical double-check
against accidental automated writes, mirrored identically across `publish_ph_task_production_report.py`
and `anpia_daily_pipeline.py`.

### Reusable Logic / Formula:
Real-browser row-density tuning pattern (reusable for any dense HTML table embedded in a constrained
host viewport): measure actual rendered row height and header height in real Chrome via CDP, then set
`floor = target_row_count * measured_row_height + header_height + scrollbar_allowance`, and use
`height: clamp(floor, calc(100vh - pretable_content_height), ceiling)` on the scrollable container --
never guess these pixel values from the CSS alone; measure, then compute, then re-measure to confirm.

### Canonical Vocabulary:
`ANPIA` = this project's `ph_task` `project_code`. `PUBLISH_NIVARNAN_ANPIA` = the fixed, non-secret
confirmation phrase gating any ANPIA `ph_task` write (not a password).

### Cross-Project Applicability:
**YES.** The real-browser row-density measurement/tuning pattern, the manifest-checksum-plus-token
double-confirmation write-gating pattern, and the insert-vs-update `ph_task` versioning question
(§4) all apply beyond ANPIA -- to any project publishing dense HTML reports into a hosted tool, and to
any project writing multiple versions into `tech_team_outputs.ph_task`.

---

## 9. LLM STANDARD CHECK

| Check | YES / NO |
|---|---|
| Could an unknown developer continue from this file without reading source code? | YES |
| Is every business threshold visible (not buried in code)? | YES (none used today; the disclosed implementation constants in §8/metadata are not business thresholds) |
| Is the GAP section completed or marked NONE? | YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | YES |
| Are evidence locations referenced? | YES |
| Is metadata complete? | YES |
| Is this extracting knowledge — not just logging activity? | YES |

**Three-AM Standard self-assessment:**
> A developer with no context could resolve the §4 versioning-convention conflict, run
> `python 05_IMPLEMENTATION/update_to_table.py --confirm --confirmation-token PUBLISH_NIVARNAN_ANPIA`
> for tomorrow's report, and deploy the (currently inactive) scheduler using
> `05_IMPLEMENTATION/deployment/README.md`, using only this file and its referenced evidence, without
> asking anyone anything except the one open §4 question.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-20__satheskanth__anpia__REQ-01-D02.md`
- [x] All metadata fields filled
- [x] Sections 1–9 completed (or explicitly marked NONE)
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] Evidence location referenced

---
*DIGITWEB LK LTD — Daily Skill Increment System*
*Requirement: REQ-01 (parent) / REQ-01-D02 (deliverable) — cross-referenced to `REQ-AMZ-NMP-001-D01`,
the identifier used throughout this project's discovery/design/implementation/validation evidence.*
