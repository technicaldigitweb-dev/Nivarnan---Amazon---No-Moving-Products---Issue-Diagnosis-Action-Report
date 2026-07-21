# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System

**Template used:** `08_SKILLS/skill file creation rules/SKILL_DAILY_TEMPLATE 2.md`
**Rules used:** `08_SKILLS/skill file creation rules/Skill File Creation Updated (1).md`
**Naming/date-format conflict between the two source files resolved (user-confirmed):** YYYY-MM-DD used throughout, for both the metadata `date` field and the filename.

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
|---|---|
| date | 2026-07-17 |
| developer | satheskanth |
| project | No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report |
| project_code | ANPIA |
| phase | BUILD |
| requirement_id | REQ-01 |
| deliverable_id | D01 |
| status | IN-PROGRESS |
| evidence_location | `03_DISCOVERY/`, `04_DESIGN/`, `05_IMPLEMENTATION/`, `06_VALIDATION/`, `07_EVIDENCE/database/`, `07_EVIDENCE/output/`, `07_EVIDENCE/validation/`, `09_OUTPUTS/html/`, `10_HANDOVER/` — exact files cited throughout this document |
| blos_keys_used | NONE (no `blos` schema objects were queried or referenced today) |
| hardcoded_thresholds | NONE new (existing skill-documented filters — SB-campaign exclusion, `amzn.gr.*` alias exclusion — were reused from the primary MCP's own documented skills, not invented here) |
| three_am_standard | PASS |
| llm_queryable | YES |
| company_knowledge_candidate | YES |
| domain | Amazon Advertising / Inventory / Ecommerce Operations |
| User | Nivarnan |
| Benefit status | NO — not delivered |
| blocker_owner | External technical dependency / tool limitation |
| blockers | Claude session usage limit; MCP bulk data-fetch timeout/transfer limitation; incomplete 7-day extraction; incomplete 14-day extraction |
| technical_reviewer | Sajeesan |
| coordinator | Sathees / assigned coordinator |
| queryability_reviewer | Tamil Selvan |
| business_validator | Nivarnan / domain owner |

## File path:
`08_SKILLS/Daily Skills/2026-07-17__satheskanth__anpia__REQ-01-D01.md`

---

## Benefit Status Statement

**Benefit delivered: NO.**

The full planned benefit for 2026-07-17 was not delivered. The complete and reconciled 30-day dataset and rebuilt v002 HTML were produced, but the 7-day and 14-day datasets were not completed. Claude session limits and MCP bulk-data-fetch limitations delayed the remaining implementation. The output was not published to `tech_team_outputs.ph_task`.

**Completed today:** requirement clarification; blue/yellow column scope clarification; multi-account and multi-marketplace scope confirmation; warehouse stock mapping; database/source discovery; technical report design; daily runtime and scheduling design; MCP timeout investigation; batched-extraction design; **complete 30-day dataset extraction and reconciliation** (51,348 rows, all 8 account+marketplace combinations, exact match against independent control totals); **v002 HTML rebuild** with real UX and real-executed validation; v001 retained unchanged as failed-sample evidence.

**Not completed:** complete 7-day dataset; complete 14-day dataset; full 7/14/30 period switching (mechanism proven correct, but only the 30-day dataset is populated); final validation of all three periods; final user acceptance; ph_task pre-publication check; ph_task publication; final closure; full planned benefit delivery.

---

## 1. SYSTEM STATE

**Current system state at the start of today's session:** the AIOS mini-subfolder structure existed with a completed discovery pass for the *original* UK-only, high-spend-ASIN-filtered scope (`REQ-AMZ-NMP-001-D01`). A decision register existed with several business decisions still OPEN. No SQL, no HTML, and no implementation code existed yet.

**What was working:** the primary MCP connection (`mcp__claude_ai_postgres__*`, database `order_management_copy`) was verified and mapped — routing map, table structures (`public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data`, `public.location_wise_inv_stock`), Amazon UK filters, and PPC/sales/stock grains were all confirmed for the original UK-only scope.

**What was broken / missing:** no implementation existed; the multi-account/multi-marketplace/multi-period scope had not yet been confirmed by the business; ph_task publication metadata was unresolved; no HTML output existed.

**Starting point:** two authoritative user-provided images corrected the scope to multi-account (LEDSONE, DCVoltage) × multi-marketplace (UK, Germany, France, Italy) × multi-period (7/14/30 days), requiring a fresh discovery addendum and a full implementation build starting from zero code.

---

## 2. WHAT CHANGED TODAY

- **Change 1 — Scope correction and design:** restructured the requirement to the corrected multi-account/marketplace/period scope; created `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`; created `04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md` and `04_DESIGN/2026-07-17__daily_runtime_and_schedule_design.md`; updated the decision register (`04_DESIGN/2026-07-17__amazon_high_spend_asin_decision_register.md`) with 7 newly-approved decisions (accounts, marketplaces, periods, warehouse mapping, filters, row grain).

- **Change 2 — Implementation scaffold built:** `05_IMPLEMENTATION/sql/main_report.sql` (aggregate-then-join query, no raw-row fan-out), `05_IMPLEMENTATION/sql/validation_checks.sql`, and Python modules `db_connection.py`, `data_transform.py`, `html_renderer.py`, `validate_output.py`, `publish_to_ph_task.py`, `run_report.py`, `run_report_v002.py`, `checkpoint_manager.py`.

- **Change 3 — v001 built, defect found and fixed:** generated a 300-row sample HTML; the row-key-uniqueness validation check found a **real defect** — `public.listing_data` can carry two rows (one base "is_offer=0" row, one "offer" row with a NULL price) resolving to the same `(account, marketplace, asin, resolved_sku)` key. Fixed with a `DISTINCT ON` bridge query with a deterministic tiebreaker; re-verified at full scale afterward (zero duplicate keys across 51,348 rows).

- **Change 4 — v001 rejected; credential path investigated:** the business user rejected v001 as an unrepresentative sample and asked for full data via credential-based PostgreSQL access. Investigated: no environment variable credential exists anywhere in this session (`PG*`, `EICA_PH_TASK_PG*` all unset); `Sources/db_access_templates/*.py` were opened **under explicit user approval** and found already fully remediated ahead of a prior GitHub handover (no embedded secrets). Also opened, under separate explicit approval, `Sources/db_access_templates/temp_user_access_report.pdf` — confirmed it is a **privilege audit report**, not a credentials sheet (no host/user/password value exists in it); it confirmed the `temp_user` role's target database (`order_management_copy`) is the **same** database the primary MCP connects to, and its exact privilege scope (public schema read-only across 37 tables; `tech_team_outputs` schema full SELECT/INSERT/UPDATE/DELETE/CREATE across its 4 tables).

- **Change 5 — Real batched extraction executed:** since no credential exists, ran a real, user-approved keyset-paginated MCP batch extraction — 30 batches (sizes 300 → 1,200 → 2,100 rows, increased once proven safe) across all 8 account×marketplace combinations for the 30-day period (2026-06-16 to 2026-07-15). Confirmed DCVoltage×France is genuinely zero rows (not a missing/failed batch). Merged and deduplicated to **51,348 unique rows, zero conflicting duplicate keys**.

- **Change 6 — v002 HTML rebuilt and real-tested:** rebuilt the HTML with sticky header, frozen Account/Marketplace/ASIN/SKU columns, correct-grain summary cards (deduplicated at Account+Marketplace+ASIN before summing), Reset Filters, filter-aware Download CSV, and an honest empty state for the not-yet-extracted 7-day/14-day periods (not faked from the 30-day set). Validated with **real Node.js/V8 execution** (not simulated) of the actual client-side filter/search/sort/CSV logic against the real 51,348-row dataset — 10 required test scenarios run, 9 full PASS, 1 partial (period-switching mechanism correct, data pending). PPC Spend and Units Ordered reconciled to an **exact match** (£19,194.97 and 8,980 units respectively) against independently-computed control totals.

- **Change 7 — Requirement document restructured:** migrated the project's requirement document into the company's approved `Daily Requirement Document` template as a separate deliverable (`01_REQUIREMENTS/2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md`), archiving the prior version to `12_ARCHIVE/requirements/` with a superseded notice.

**Evidence reference:**
`03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md` ·
`04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md` ·
`04_DESIGN/2026-07-17__daily_runtime_and_schedule_design.md` ·
`07_EVIDENCE/database/2026-07-17__mcp_bulk_fetch_timeout_evidence.md` ·
`07_EVIDENCE/database/2026-07-17__mcp_batched_extraction_evidence.md` ·
`06_VALIDATION/2026-07-17__sql_validation_report.md` ·
`06_VALIDATION/2026-07-17__html_validation_report.md` ·
`07_EVIDENCE/output/2026-07-17__report_generation_evidence_v002.md` ·
`07_EVIDENCE/validation/2026-07-17__report_reconciliation_evidence_v002.md` ·
`07_EVIDENCE/validation/2026-07-17__ui_filter_csv_validation_evidence.md` ·
`09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v001.html` (failed sample, retained) ·
`09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v002.html` (current build) ·
`10_HANDOVER/2026-07-17__session_limit_continuation_note.md`

---

## 3. POSTGRESQL / MCP / DATABASE FINDING

**Table(s) involved:** `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data`, `public.location_wise_inv_stock` (schema `order_management_copy`, accessed via `PRIMARY_SKILLS_MCP` / `mcp__claude_ai_postgres__*`).

**Finding:**
- `public.listing_data` can carry more than one row for the same `(sub_source, market_place, ref_id, resolved_sku)` key — a base listing row (`is_offer=0`) and a duplicate "offer" row (`is_offer=1`, sparse fields, often a NULL price) that both resolve to the same `mapped_sku`. A bridge query using plain `DISTINCT` across all selected columns does **not** collapse these into one row.
- `SELECT current_database()` on the primary MCP connection returns `order_management_copy` — confirmed to be the exact same database the `temp_user` role (documented in `Sources/db_access_templates/temp_user_access_report.pdf`) is scoped to. This rules out a parallel-truth risk between the primary MCP and any future credential-based connection.
- `temp_user` role privileges (confirmed via `information_schema.table_privileges`, `has_table_privilege`, `has_schema_privilege` — metadata only, no live connection attempted as that role): `rolcanlogin=true`, `rolvaliduntil=NULL` (no expiry set); `public` schema = SELECT-only across 37 tables; `tech_team_outputs` schema = full SELECT/INSERT/UPDATE/DELETE/CREATE across its 4 tables.
- A single unbounded MCP query across the full ~50,000-row cross-account/marketplace scope times out after 300s with no response. The same query, scoped to one `(period, account, marketplace)` combination and paginated with an ascending `(asin, resolved_sku)` keyset, succeeds reliably at up to 2,100 rows per call.

**SQL logic/pattern discovered:**
```sql
SELECT DISTINCT ON (sub_source, market_place, ref_id, COALESCE(NULLIF(mapped_sku,''), sku))
    ...
FROM public.listing_data
WHERE which_channel = 1 AND wrong_sku = 0 AND is_parent = 0
ORDER BY sub_source, market_place, ref_id, COALESCE(NULLIF(mapped_sku,''), sku),
         is_offer ASC, (price IS NULL) ASC, id ASC
```

**Operational meaning:** the `listing_data` offer-row duplication is a normal, recurring data shape in this system, not a one-off anomaly (confirmed present across multiple accounts/marketplaces during the 30-day extraction). Any future query bridging PPC/traffic to stock through `listing_data` must apply this same deterministic dedup, not assume one row per key.

---

## 4. GAP FOUND

**Gap description:** Sessions, Page Views, Conversion Rate, Click-Through Rate, and Buy Box % have no single confidently-complete live data source — candidate tables exist but have coverage or grain problems. Category Avg Price's averaging population (marketplace-only / account+marketplace / global) is undefined. ph_task publication metadata (assigned_user, assigned_user_team, team, title format, project_code for ph_task, version status) remains unapproved.

**Impact if unresolved:** 5 of the 15 required blue columns cannot be populated with real values (shown as `N/A - source not available`); `tech_team_outputs.ph_task` publication cannot proceed at all, regardless of data completeness.

**Recommended action:** route the 5 field-source questions and the ph_task metadata approval to Sajeesan (technical reviewer) before further column population or any publication attempt.

**Owner:** Sajeesan.

> Additional gap: the 7-day and 14-day datasets have not been extracted at all (not a data-quality gap — simply not yet done, due to session-limit/time constraints).

---

## 5. VALIDATION RULE ADDED OR CHANGED

**Rule name/ID:** Row-key uniqueness guard (bridge `DISTINCT ON` fix).

**Condition checked:** no two output rows may share the same `(account, marketplace, asin, resolved_sku)` key.

**What it prevents:** silently duplicated report rows carrying conflicting `title`/`price` values for what should be a single logical listing — a real defect that was actually produced and caught during this session, not a theoretical risk.

**Where implemented:** `05_IMPLEMENTATION/sql/main_report.sql` (the `bridge` CTE), independently re-checked by `05_IMPLEMENTATION/src/validate_output.py`'s `check_row_key_uniqueness()` and by `checkpoint_manager.py`'s merge-time conflict detection.

**BLOS reference:** none — this is a SQL data-integrity construction rule, not a BLOS-governed business threshold.

---

## 6. FAILURE MODE OR EDGE CASE

**Failure scenario:** a single unbounded MCP `execute_sql` call requesting the complete ~50,000-row, all-account/all-marketplace result set for a report period.

**How it is triggered:** omitting per-combination scoping and/or keyset pagination when the underlying result set is large.

**How it is detected:** the MCP tool call is moved to a background task after 120s, then fails after a further 180s (300s total) with "sent no response or progress for 300s; aborting."

**Recovery procedure:** scope every extraction query to exactly one `(period, account, marketplace)` combination; paginate ascending on `(asin, resolved_sku)` with a batch size proven safe for this connection (2,100 rows); checkpoint every successful batch to a local JSONL file immediately; merge and deduplicate only after every combination reaches a terminal state (`complete` or a confirmed `zero_source_rows`).

**Risk level:** MEDIUM — no data corruption risk, but a retried oversized query wastes significant session time and can appear to stakeholders as "no progress" when the underlying cause is a transport/practical-limit issue, not a database or logic failure.

---

## 7. DECISIONS MADE TODAY

**Decision 1 — Row-key dedup tiebreaker order.**
Alternatives considered: keep the first-seen row arbitrarily (no explicit tiebreaker).
Reason for choice: an arbitrary/first-seen choice is non-deterministic across re-runs of the same query; the chosen order (non-offer row first, then non-null price, then lowest `id`) is deterministic and reproducible.
Trade-off accepted: negligible — both candidate rows resolve to the same inventory SKU, so only cosmetic display fields (title/price) are affected by the choice, not the underlying stock/sales logic.
Who approved: technical/implementation-level decision, not separately business-approved (it is a correctness fix, not a business-rule change).

**Decision 2 — Use MCP keyset-paginated batching instead of credential-based direct access for the 30-day extraction.**
Alternatives considered: credential-based `psycopg2` connection (attempted first, per explicit instruction); continued single unbounded MCP queries (explicitly disallowed after the first timeout).
Reason for choice: no credential value exists anywhere in this environment — confirmed by checking environment variables and, under explicit user approval, the referenced template scripts and the privilege-audit PDF.
Trade-off accepted: extraction requires many sequential MCP calls (30 for the 30-day period alone) instead of one connection and one query; the 7-day and 14-day periods were not extracted in the time available as a direct consequence.
Who approved: the business user explicitly approved this fallback path after the credential path was proven unavailable, and explicitly approved the batching strategy and its parameters (initial batch size, retry rule).

---

## 8. COMPANY KNOWLEDGE EXTRACT

### Business Rule:
None new today — the account/marketplace/warehouse/column-scope business rules were established earlier (by user-provided images) before today's session; today's work implemented and validated them, it did not invent new business rules.

### Operational Assumption:
`public.listing_data` may contain more than one row per `(which_channel, sub_source, market_place, ref_id, resolved_sku)` combination — a base listing row and one or more sparse "offer" rows. Any bridge or report built on this table must deduplicate deterministically (see §3/§5); assuming one row per key will silently produce duplicated output rows with conflicting display fields.

### Reusable Logic / Formula:
Keyset pagination pattern for large Postgres result sets fetched through this MCP connection:
```
WHERE (asin > :last_asin) OR (asin = :last_asin AND resolved_sku > :last_sku)
ORDER BY asin, resolved_sku
LIMIT :batch_size
```
2,100 rows/batch is a proven-safe size for this connection (an earlier attempt at a differently-shaped, unbounded, multi-combination query timed out at 300s; per-combination batches of this size have not timed out once in 30 consecutive batches).

### Canonical Vocabulary:
`PRIMARY_SKILLS_MCP` = `mcp__claude_ai_postgres__*`, database `order_management_copy`. `FALLBACK_PROJECT_MCP` = `mcp__ledsone-db__*` (configured via the project's `.mcp.json`), a **different, unrelated** operational database. These must never be conflated — every finding in this project's evidence is source-labelled by which connection produced it.

### Cross-Project Applicability:
**YES.** Both the keyset-pagination-via-MCP extraction pattern and the `listing_data` offer-row deduplication rule apply to any future report built against the `order_management_copy` database through this MCP connection — not only to this ANPIA deliverable.

---

## 9. LLM STANDARD CHECK

| Check | YES / NO |
|---|---|
| Could an unknown developer continue from this file without reading source code? | YES |
| Is every business threshold visible (not buried in code)? | YES (none new today; existing skill-documented filters cited, not hidden) |
| Is the GAP section completed or marked NONE? | YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | YES |
| Are evidence locations referenced? | YES |
| Is metadata complete? | YES |
| Is this extracting knowledge — not just logging activity? | YES |

**Three-AM Standard self-assessment:**
> A developer with no context could resume the 7-day and 14-day extraction (using the exact keyset-pagination pattern in §8) and complete the ph_task metadata approval and publication gate, using only this file and its referenced evidence paths, without asking anyone anything.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-07-17__satheskanth__anpia__REQ-01-D01.md`
- [x] All metadata fields filled
- [x] Sections 1–9 completed (or explicitly marked NONE)
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] Evidence location referenced

---
*DIGITWEB LK LTD — Daily Skill Increment System*
*Requirement: REQ-01 (parent) / REQ-01-D01 (deliverable) — cross-referenced to `REQ-AMZ-NMP-001-D01`, the identifier used throughout this project's discovery/design/implementation/validation evidence (see `01_REQUIREMENTS/2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md` §0 for the naming-duality note).*
