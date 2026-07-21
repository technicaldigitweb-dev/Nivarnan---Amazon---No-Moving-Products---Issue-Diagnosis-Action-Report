# Discovery — Amazon High-Spend ASIN, Sales & UK Stock

**What this is:** The controlled, read-only discovery record for REQ-AMZ-NMP-001-D01 — existing-asset check, project-control rules, workbook review, ph_task rules, and full live-database verification (tables, filters, grains, dates, cardinality, join risk) across two PostgreSQL MCP connections.

**Why it exists:** Per project control (Skill 04/05/08/09), no SQL/HTML/automation may be built before discovery proves the source of truth, structure, and safety.

**Business question supported:** Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action?

**Sources used:** `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md`, `00_PROJECT_CONTROL/source_references/`, `02_SOURCE/requirements/` (Nivarnan workbook), `08_SKILLS/ph_task_reference/`, `PRIMARY_SKILLS_MCP` (`claude_ai_postgres`), `FALLBACK_PROJECT_MCP` (`ledsone-db`, superseded for this requirement's data areas — see below), both unresolved skill ZIPs (as discovery leads only).

**Evidence produced:** `07_EVIDENCE/database/2026-07-17__database_source_selection_evidence.md`, `2026-07-17__routing_map_sample_evidence.md`, `2026-07-17__candidate_table_structure_evidence.md`, `2026-07-17__data_freshness_evidence.md`, `2026-07-17__join_cardinality_evidence.md`, `07_EVIDENCE/project/2026-07-17__existing_asset_inventory.md`, `2026-07-17__duplicate_risk_review.md`, `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`.

**Owner/reviewer:** Coordinator: Sathees or assigned coordinator. Technical reviewer: Sajeesan or assigned senior developer. Queryability reviewer: Tamil Selvan or assigned reviewer. Business validator: Nivarnan or assigned Amazon business owner.

**Status:** DISCOVERY COMPLETE — AMBER (technically complete; business decisions unresolved — see §9).

---

## 1. Existing reusable assets

No SQL, HTML template, ph_task publisher, or saved report exists anywhere in this project. However, the primary MCP's own skill registry (`ppc-stock-lookup`, `text-to-sql-single`, `text-to-sql-multi`) already documents a validated method for exactly this question — "top N ASINs/SKUs by spend, with their stock" (Mode B). Full detail: `07_EVIDENCE/project/2026-07-17__existing_asset_inventory.md`.

## 2. Project-control rules applied

From `00_PROJECT_CONTROL/source_references/` (AIOS skill pack + `0.1 LLM PROJECT INSTRUCTION.md.docx`):

- **Existing-asset-first (Skill 04):** search before create — applied in §1 above.
- **Duplicate-truth prevention (Skill 05):** one canonical source per business rule — applied throughout; see §7 and the duplicate-risk review.
- **Evidence-first (Skill 08):** no evidence = no completed work — every claim in this file traces to a saved evidence file.
- **Queryability-first (Skill 09):** every asset must self-answer what/why/source/evidence/status/next-step — applied to every file this discovery created.
- **Database writes:** RED work, "production data changes... financial/PPC logic change" require written approval — none performed.
- **ph_task publication:** covered separately in §4; no insert/update performed.
- **Capability learning/reuse (Skill 06/07):** the validated primary-MCP skill (`ppc-stock-lookup`) is the capability to reuse, not re-derive.

## 3. Workbook findings (`02_SOURCE/requirements/...Nivarnan-v001.xlsx`)

8 sheets: `0. Index` (hidden), `NoMoving_Report-Satheskanth-170` (visible), `2. NoMoving_DataMapping`, `3. PriceErosion_Report`, `4. PriceErosion_DataMapping`, `5. TopASIN_Inv_Report`, `6. TopASIN_Inv_DataMapping`, `7. Rules_and_Thresholds` (all hidden).

The workbook documents **three separate reports**: No-Moving Products, Price Erosion Monitoring, and Top-Performing ASIN Inventory. **None of the three is a PPC-spend report** — no sheet, column, or threshold in this workbook references PPC/advertising spend at all. The closest conceptual match is "5. TopASIN_Inv_Report" (sales rank, units sold, revenue, stock, reorder point) — but it ranks by **Sales Rank**, not by ad spend.

- **Expected output fields (closest analog, TopASIN_Inv_Report):** ASIN, SKU, Product Title, Category, Sales Rank, Units Sold (30d), Revenue (30d), Avg Daily Sales, Lead Time, Safety Stock, Sell-Through Rate, Current Stock, Days of Cover, Reorder Point, Safety Multiplier, Safe Bucket Qty, Performance Tier, Stockout Risk, Replenish Action, Last Updated.
- **Thresholds sheet (`7. Rules_and_Thresholds`):** contains thresholds for No-Moving Products (traffic, conversion, pricing, dead-stock, high-priority), Price Erosion (margin, daily-drop, erosion triggers), and Top-Performing ASIN tiers (top 10%/20%, safety multipliers, stockout risk bands). **No PPC-spend threshold exists anywhere in the workbook** — confirms "high spend" is genuinely undefined, not merely omitted from the written requirement.
- **In scope for REQ-AMZ-NMP-001-D01:** none of the three built-in reports directly — this requirement is a **new, related** analysis (PPC spend + sales + stock) that borrows the sales/stock shape of TopASIN_Inv_Report but adds a spend dimension the workbook does not have.
- **Out of scope:** No-Moving Products diagnosis logic, Price Erosion monitoring, reorder-point/safety-stock/safe-bucket calculations — none of these are part of this requirement.
- **Requires Nivarnan's approval:** any threshold this new report introduces (since no equivalent exists in `7. Rules_and_Thresholds` to reuse), per the workbook's own instruction ("Edit values here; rule engine should read from this sheet, not hardcode numbers" — a new PPC-spend threshold would need to be added there, which is a business-rule decision, not a technical one).

## 4. ph_task rules (`08_SKILLS/ph_task_reference/`)

- **Table:** `tech_team_outputs.ph_task`. **Required columns (NOT NULL):** `project_name`, `project_code`, `task_name`. **Key optional columns:** `task_id`, `team`, `developer`, `assigned_user`, `assigned_user_team`, `html_content`, `description`.
- **Routing rule:** `assigned_user_team` must be exactly `ph_priors` or `ebay_priors` (lowercase, underscore) — determines which dashboard board the task appears on. Leaving it empty makes the task invisible to end users without an error.
- **Versioning:** `phase_level` and `version_level` are plain integers, default 0, incremented by 1 each release.
- **Insert-vs-update:** **append-only for new versions** — release v2+ by inserting a **new row** with `version_level` incremented; **never update the old row's content**. The only update permitted on the old row is setting `version_status = 'rejected'`.
- **Duplicate-prevention / one-active-output rule:** the dashboard's Pending/Completed views hide any row with `version_status = 'rejected'` — forgetting to set this leaves both old and new versions visible simultaneously.
- **HTML storage:** task body is stored directly as HTML in `html_content`.
- **Audit/evidence:** `action_took_by`/`action_took_date_time` record completion; both NULL = pending.
- **Mandatory validation before writing:** none of this discovery performed or is authorized to perform any ph_task write — `database_write_permission` and `production_change_permission` remain NOT APPROVED per the requirement metadata.

## 5. Database connection audit — GREEN

Two MCP connections were checked. Full detail and safety checklist: `07_EVIDENCE/database/2026-07-17__database_source_selection_evidence.md`.

- **Primary skills MCP:** `claude_ai_postgres` — CONFIRMED by tool identity/shape (13 tools; `get_table_definition`/`list_skills` content matches this project's routing workbook and skill ZIPs exactly; schema list includes `tech_team_outputs`, matching `ph_task`'s schema). Endpoint string (`https://mcp.vintageinterior.co.uk/mcp`) is PARTIAL confidence only — not independently verifiable from this sandbox.
- **Fallback project MCP:** `ledsone-db` (via `.mcp.json`) — CONFIRMED, but proven to be a **different physical database** (no `table_routing_map`, no `public.ppc`/`order_transaction`/`location_wise_inv_stock`; only `public.migrations`). Its earlier findings (recorded before this priority order was confirmed) are labelled `SUPERSEDED AS PRIMARY-SOURCE EVIDENCE — RETAINED AS POSSIBLE FALLBACK EVIDENCE`, not deleted.
- **Fallback usage:** **not required** — no element needed by this requirement was proven missing from the primary.

## 6. Routing-map coverage — FULL

`public.table_routing_map` (primary MCP) routes: Advertising/PPC → `public.ppc`, `public.ppc_performance` (+2 log tables); Sales/Orders → `public.order_transaction`; Inventory/Stock → `public.location_wise_inv_stock`, `public.inv_final_stock`. Full query evidence: `07_EVIDENCE/database/2026-07-17__routing_map_sample_evidence.md`.

## 7. Confirmed tables, columns, grains, and filters

All from `PRIMARY_SKILLS_MCP`, full detail in `07_EVIDENCE/database/2026-07-17__candidate_table_structure_evidence.md`:

| Table | Role | Grain | Amazon UK filter |
|---|---|---|---|
| `public.ppc_performance` | PPC spend fact | 1 row per ad per date (Amazon) | `source=1 AND marketplace='UK'` |
| `public.ppc` | PPC campaign/ad metadata (SB exclusion join) | 1 row per entity | `source=1 AND market_place='UK'` |
| `public.order_transaction` | Sales fact | 1 row per order line | `source_name='AMAZON' AND market_place='UK'` |
| `public.location_wise_inv_stock` | Current UK stock | live snapshot, ~1 row per SKU per location (small duplicate-row exceptions found) | `location='UK'` |
| `public.listing_data` | ASIN→SKU bridge (mandatory — never bridge via `order_transaction` for a PPC-sourced report) | up to several rows per `ref_id` | `which_channel=1 AND market_place='UK' AND wrong_sku=0` |

## 8. PPC / sales date coverage and reporting window

- **PPC (`PRIMARY_SKILLS_MCP`):** full range 2025-01-01 → 2026-07-16; latest **complete** date = **2026-07-15** (2026-07-16 row count ~8,150 vs. trailing average ~10,000–11,200 — partial day).
- **Sales (`PRIMARY_SKILLS_MCP`):** full range 2020-08-03 → 2026-07-16 14:29:45; latest **complete** date = **2026-07-15** (2026-07-16 has only 50 completed orders vs. trailing average ~180–230 — partial day).
- **Latest complete common 30-day window: 2026-06-16 to 2026-07-15 inclusive.**
- Full evidence: `07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md`.

## 9. Stock freshness

UK stock (`location_wise_inv_stock`) `updated_at` ranges up to 2026-07-16 22:33:22 — genuinely live. **These stock figures are based on live data, not past records** — stock cannot be pinned to the 2026-06-16–2026-07-15 window; any future report must state stock is "as of today," separately from the PPC/sales window.

## 10. ASIN/SKU cardinality and join-multiplication risk

- 96.7% of Amazon UK ASINs → exactly 1 resolved SKU; 3.3% (1,038 ASINs) → 2–4 SKUs. `mapped_sku` populated on 43.0% of UK Amazon listing rows — resolution step is mandatory.
- `amzn.gr.*` platform aliases: 30 rows (0.01%) in the 30-day PPC window — must be excluded.
- Stock table: a small number of UK SKUs have duplicate rows — must `SUM(COALESCE(stock,0))` grouped by `sku`.
- **Empirically demonstrated** (not theoretical): naively joining pre-aggregated ASIN spend to `listing_data` without re-aggregating produces up to 6x row fan-out per ASIN. Safe sequence: aggregate PPC by ASIN → aggregate sales by ASIN → resolve ASIN→SKU bridge separately → aggregate stock by SKU → join only the pre-aggregated results. Full evidence: `07_EVIDENCE/database/2026-07-17__join_cardinality_evidence.md`.

## 11. Skill-ZIP reconciliation

For the 3 files relevant to this requirement, `skills_minimal_pack 2 (2).zip` matches live database/skill evidence; `skills 3 (1) (3).zip` contains superseded content (including a stale bridge-table name, `ebay_products`, that does not exist live — current name is `listing_data`). Status remains `REVIEW_REQUIRED` pending technical reviewer sign-off; no ZIP content was copied or merged. Full detail: `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`.

## 12. Missing information / open questions (not guessed)

1. What qualifies as "high spend": Top N, threshold, percentile, or another rule? (Confirmed absent from the workbook's `Rules_and_Thresholds` sheet — genuinely undefined, requires Nivarnan's decision.)
2. Should spend-with-zero-sales ASINs be included, or specifically called out?
3. Should "sales" report revenue (`order_total`), units (`quantity`), orders (`COUNT(DISTINCT order_item_info)`), or all three?
4. Display rule for one ASIN mapped to multiple SKUs (affects 3.3% of ASINs) — sum stock and list all SKUs, or something else?
5. Acceptable stock-freshness age/threshold for flagging stale rows — none defined; live data ranges from same-day to ~2.5 months old per row.
6. ph_task `assigned_user`/`assigned_user_team`/`project_code`/`title`/`version_status` values for this specific report — not yet assigned.
7. Should Git be initialized for this project, and which remote repository should be used? (Still not initialized — confirmed via `git status` returning "not a git repository.")
8. What numeric KPI or time-saving target should this report be judged against?
9. Final canonical-version sign-off for the 3 reconciled skill-ZIP files, and separately for the 9 files not touched by this requirement.
10. `order_transaction.order_status` contains an undocumented "Canceled" (single-L) value alongside "Cancelled" — needs a decision on whether both must be excluded identically from any future refund/cancellation-aware sales metric (not needed for this requirement, since only `order_status='Completed'` is used, but noted for the open question about refund/cancellation treatment).

## 13. GitHub / Drive / wiki access actually available

**Not checked / not accessible in this session** — no GitHub repository, Google Drive, or wiki connector was queried, because none is configured as an approved source for this project (confirmed: `git status` shows no repository; no Drive/wiki reference exists in `00_PROJECT_CONTROL` or the requirement doc). This is recorded as "not accessible," not claimed as checked.

## 14. Safety checklist

- **Database writes:** NONE — every query was `SELECT`, bounded by explicit filters/`LIMIT`/`GROUP BY`.
- **Restricted files opened:** NONE — `Sources/db_access_templates/` was not opened.
- **`.mcp.json` changed:** NO — checksum unchanged throughout (`69c55f9bafa405570a950550915ecb79b11266b52018b2e64f67c34118c3ff22`).
- **Credentials exposed:** NONE — no connection string, password, host, or token was read or printed from either MCP's configuration.
- **Final SQL/HTML/automation/ph_task publication:** NOT built — this is discovery only, per instruction.

## Pass/fail rule

PASS (of this discovery) if every one of the 19 discovery pass-rule conditions in the task instructions is evidenced above or in the linked evidence files, and every open business decision is listed rather than guessed. **This discovery meets that bar.**

## Final decision: AMBER

Technically complete — every table, filter, grain, date window, cardinality risk, and connection-priority question is evidenced. **AMBER, not GREEN, because 10 business decisions remain genuinely unresolved** (§12) and require Nivarnan/coordinator/technical-reviewer input before implementation can begin.

## Next action

Route the 10 open questions in §12 to Nivarnan (business/high-spend definition), Sajeesan (skill-ZIP reconciliation sign-off, ph_task field values), and the coordinator (Git decision, KPI target) — see `10_HANDOVER/2026-07-17__discovery_handover.md`.
