# Amazon High-Spend ASIN Decision Register

## 1. Metadata

- requirement_id: REQ-AMZ-NMP-001-D01
- date: 2026-07-17
- project: Amazon - No-Moving Products - Issue Diagnosis & Action Report
- discovery_status: AMBER (expanded 2026-07-17 to multi-account/multi-marketplace scope — see `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`)
- design_status: IN_PROGRESS — business scope/row-grain decisions resolved by written instruction (§3 below); ph_task publication, stock-freshness threshold, and 3 field-source decisions remain OPEN
- database_write_permission: NOT APPROVED
- implementation_permission: APPROVED FOR VERIFIED/PARTIAL FIELDS ONLY — full implementation (all 15 blue columns) remains gated on DEC-TECH-001 (ph_task) and the field-source decisions in §3

## 2. Verified Discovery Baseline

> **SCOPE NOTE (2026-07-17):** the bullets below describe the original UK-only discovery baseline and are preserved for audit trail. Scope has since expanded to 2 accounts × 4 marketplaces — see `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md` and `07_EVIDENCE/database/2026-07-17__account_marketplace_filter_evidence.md`, `.../marketplace_warehouse_mapping_evidence.md`, `.../blue_field_source_mapping.md`, `.../expanded_join_cardinality_evidence.md` for the current baseline. The UK-specific filter values below remain correct as the UK-marketplace case within the wider scope.

- **Primary MCP used:** `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__*`) exclusively. Fallback project MCP (`ledsone-db`, via `.mcp.json`) was checked but is **not required** — it is a different, non-matching physical database; no report field is sourced from it. See `07_EVIDENCE/database/2026-07-17__database_source_selection_evidence.md`.
- **Selected tables:** PPC — `public.ppc`, `public.ppc_performance`; Sales — `public.order_transaction`; ASIN→SKU bridge — `public.listing_data`; Current UK stock — `public.location_wise_inv_stock`. See `07_EVIDENCE/database/2026-07-17__candidate_table_structure_evidence.md`.
- **Verified filters:** PPC `source=1, marketplace='UK'`; Sales `source_name='AMAZON', market_place='UK'`; Stock `location='UK'`; Listing bridge `which_channel=1, market_place='UK', wrong_sku=0`. See `07_EVIDENCE/database/2026-07-17__candidate_table_structure_evidence.md`.
- **Reporting window:** latest complete common 30-day period = **2026-06-16 through 2026-07-15**. 2026-07-16 excluded — both PPC and sales proven partial for that date via row-count drop-off. See `07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md`.
- **Stock freshness:** current live snapshot only, `updated_at` verified up to 2026-07-16 22:33:22. Every future report output must carry: **"These stock figures are based on live data, not past records."** See `07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md`.
- **ASIN/SKU bridge rule:** `public.listing_data` is the only approved bridge (never `order_transaction`); resolved SKU = `COALESCE(mapped_sku, sku)`, subject to final SQL validation. 43% of Amazon UK listing rows require `mapped_sku`; 3.3% of ASINs resolve to 2–4 SKUs; `amzn.gr.*` aliases must be excluded. See `07_EVIDENCE/database/2026-07-17__join_cardinality_evidence.md`.
- **Join-fan-out evidence:** a naive raw join can multiply PPC spend by up to 6x (empirically demonstrated, not theoretical). Mandatory order: (1) aggregate PPC spend by ASIN, (2) aggregate sales independently by ASIN, (3) resolve ASIN→SKU via `listing_data`, (4) aggregate current stock independently by resolved SKU, (5) join the aggregated datasets once. Raw PPC rows must never be joined directly to raw sales, listing, or stock rows. See `07_EVIDENCE/database/2026-07-17__join_cardinality_evidence.md`.
- **Fallback MCP not required:** confirmed — no element needed by this requirement was proven missing from the primary. See `07_EVIDENCE/database/2026-07-17__database_source_selection_evidence.md` §5.
- **Skill reconciliation status:** for the three relevant file-level conflicts, `skills_minimal_pack 2 (2).zip` matched live evidence more closely than `skills 3 (1) (3).zip` (which contains a stale bridge-table name, `ebay_products`, not present in the live schema). Status remains **REVIEW_REQUIRED** pending technical sign-off — no ZIP content has been copied, merged, or promoted. See `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`.

## 3. Decision Register

| decision_id | question | decision_owner | available_choices | selected_decision | rationale | implementation_effect | validation_effect | status | approval_date |
|---|---|---|---|---|---|---|---|---|---|
| DEC-BUS-001 | What qualifies as a high-spend ASIN? | Nivarnan | Top 10 ASINs by PPC spend; Top 20 ASINs by PPC spend; Spend greater than an approved GBP threshold; Top approved percentile; Another business-defined rule | **No cutoff — all valid combinations shown; PPC spend is display/sort only** | Resolved by the two authoritative user-provided images and the corrected written requirement §2A: "Do not apply a Top-10, Top-20, percentile, or minimum-spend cutoff unless a later written instruction explicitly approves it" — no such instruction exists, so the original high-spend-filter question is moot. | No ranking/cutoff `WHERE`/`LIMIT` clause; result set = all in-scope combinations. | Row-count reconciliation is against the full combination set, not a filtered top-N. | **RESOLVED — SUPERSEDED BY WRITTEN INSTRUCTION** | 2026-07-17 |
| DEC-BUS-002 | Should ASINs with PPC spend but zero sales during the period be included? | Nivarnan | Include and flag as zero-sales risk; Exclude; Display in a separate section | **Included — all valid combinations appear regardless of spend/sales** | Same written-instruction basis as DEC-BUS-001 — "ALL valid account, marketplace, ASIN, and SKU combinations within the approved data scope must appear." | No `HAVING` filter excludes zero-sales rows. | Reconciliation must include zero-sales rows, not just spend>0 rows. | **RESOLVED — SUPERSEDED BY WRITTEN INSTRUCTION** | 2026-07-17 |
| DEC-BUS-003 | Which sales measures should the report show? | Nivarnan | Revenue only; Units only; Orders only; Revenue and units; Revenue, units, and distinct orders | **Units Ordered only (no revenue column)** | Resolved by the confirmed blue-column image (`07_EVIDENCE/project/2026-07-17__nivarnan_blue_yellow_column_scope.md`) — no Sales Revenue column is present; the instruction explicitly forbids silently adding Sales Revenue without separate written confirmation. | Sales aggregate pulls `SUM(quantity)` only from `order_transaction`. | Reconciliation covers Units Ordered only; Sales Revenue is not validated (not displayed). | **RESOLVED — SUPERSEDED BY WRITTEN INSTRUCTION** | 2026-07-17 |
| DEC-BUS-004 | ~~How should one ASIN mapped to multiple SKUs be shown?~~ **Redefined 2026-07-17 per written instruction:** row grain for the multi-account/multi-marketplace scope. | Nivarnan | ~~One row per ASIN with total stock; nested breakdown; one row per ASIN/SKU; summary + expandable~~ → **One Amazon ASIN and one Amazon SKU per output row** | **One Amazon ASIN and one Amazon SKU per output row (row key = account + marketplace + ASIN + resolved SKU)** | Explicit written instruction (task section "Add these approved decisions to the decision register"). Supersedes but answers the original DEC-BUS-004 question directly: multi-SKU ASINs are shown as multiple rows (one per resolved SKU), not aggregated into one row. | Output grain = account+marketplace+ASIN+SKU, one row each; stock is per-SKU, not summed across an ASIN's SKUs. | Validation checks each row individually; **aggregating stock across an ASIN's SKUs would now be a defect**, not a display choice — the multi-SKU stockout-hiding risk originally noted is avoided by this grain choice. | **APPROVED** | 2026-07-17 |
| DEC-BUS-005 | How old may the latest stock update be before the report shows a stale-data warning or fails? | Nivarnan, with Sajeesan technical confirmation | 15 minutes; 1 hour; 6 hours; 24 hours; Another approved threshold | — | — | Determines whether a freshness check/warning is added to the stock-lookup step, and its threshold value. The mandatory "live data, not past records" disclosure is unaffected by this decision and is included regardless. | Determines the freshness-tolerance test in validation. | OPEN — non-blocking for v001 (disclosure-only output does not require a threshold) | — |
| DEC-BUS-006 | Are all confirmed blue columns required, and all yellow columns excluded? | Nivarnan | — | **Yes — all 15 blue columns required; all 8 yellow columns excluded from HTML, CSV, filters, summary cards, and ph_task HTML content** | Directly confirmed by both authoritative images; see `07_EVIDENCE/project/2026-07-17__nivarnan_blue_yellow_column_scope.md`. | Determines the full output column set. | Validation checks presence of all 15 and absence of all 8. | **APPROVED** | 2026-07-17 |
| DEC-BUS-007 | Which accounts are in scope? | Nivarnan | — | **LEDSONE and DCVoltage** (`sub_source_id` 8 and 6 respectively) | Confirmed by image + live account-mapping verification, `07_EVIDENCE/database/2026-07-17__account_marketplace_filter_evidence.md`. | Account filter values in all report SQL. | Validation checks both accounts present (DCVoltage×France legitimately empty — see evidence). | **APPROVED** | 2026-07-17 |
| DEC-BUS-008 | Which marketplaces are in scope? | Nivarnan | — | **UK, Germany, France, Italy** | Confirmed by image + live marketplace verification. | Marketplace filter values in all report SQL. | Validation checks all four appear where source data exists. | **APPROVED** | 2026-07-17 |
| DEC-BUS-009 | Which reporting periods are supported? | Nivarnan | — | **7, 14, and 30 complete days, all three available** | Confirmed by image ("7/14/30 Days filter"). | Period selector logic; labels must reflect selected period (no hardcoded "30d"). | Validation checks all three periods produce correct, non-hardcoded date ranges. | **APPROVED** | 2026-07-17 |
| DEC-BUS-010 | How does marketplace map to warehouse stock? | Nivarnan | — | **UK marketplace → UK warehouse; Germany, France, Italy marketplaces → shared German warehouse** | Confirmed by image + live warehouse-value verification (`07_EVIDENCE/database/2026-07-17__marketplace_warehouse_mapping_evidence.md` — no France/Italy warehouse exists in the database at all, independently confirming the rule). | Stock join key = `CASE WHEN marketplace='UK' THEN 'UK' ELSE 'Germany' END`. | Validation checks shared German stock is not triple-counted in summary totals. | **APPROVED** | 2026-07-17 |
| DEC-BUS-011 | Which filters must the output provide? | Nivarnan | — | **Account filter, marketplace filter, period filter (7/14/30)** | Confirmed by image ("Account wise, Market place wise filters should be there.") plus period filter from DEC-BUS-009. | HTML must include all three filter controls. | Validation checks filters actually change displayed rows/values. | **APPROVED** | 2026-07-17 |
| DEC-TECH-001 | What exact ph_task metadata should be used? | Sajeesan or assigned technical reviewer | Required values to approve: assigned_user; assigned_user_team; team; title format; project code; version status; active-output rule; insert-versus-update behavior; superseded-output handling | — | — | Determines every field written on ph_task insert, and the versioning/supersede behavior on release. | No ph_task write may occur until this is approved or publication is formally deferred. | **OPEN — BLOCKS PUBLICATION** | — |
| DEC-TECH-002 | Is the file-level preference for the relevant skills in skills_minimal_pack approved? | Sajeesan or assigned technical reviewer | Approve the three file-level recommendations; Reject and specify corrected canonical files; Require additional comparison | — | — | Determines whether `skills_minimal_pack 2 (2).zip`'s three relevant files may be treated as canonical for implementation. | Determines which skill-file content SQL generation may be based on. | OPEN | — |
| DEC-TECH-003 | How should order_status values 'Canceled' and 'Cancelled' be treated? | Sajeesan, with Nivarnan confirming business meaning | Treat both as cancelled; Exclude only one verified value; Keep both pending a frequency and semantic check | — | — | Determines the `order_status` filter/exclusion list used in any refund- or cancellation-aware sales measure. **No refund-aware or net-sales measure may be implemented until this treatment is approved.** | Affects reconciliation between gross and net sales totals if a net measure is ever built. | OPEN — non-blocking (this report uses `order_status='Completed'` units only, no refund-aware measure) | — |
| DEC-TECH-004 | What is the live source for Sessions/Page Views/Buy Box %/Conversion Rate? | Sajeesan or assigned technical reviewer | `amz_traffic_by_asin` (daily grain, but recent coverage is 10–40x below historical average); another/corrected source | — | — | Determines whether these 4 columns can move from "N/A — pending source confirmation" to live data. | Blocks reconciliation testing for these 4 columns. | **OPEN — NEW, BLOCKS 4 BLUE COLUMNS** | — |
| DEC-TECH-005 | What is the live source for Click-Through Rate? | Sajeesan or assigned technical reviewer | `ppc_performance` (advertising CTR); `amazon_search_query_performance` (Brand Analytics CTR, different grain) | — | — | Determines the CTR formula/source. | Blocks reconciliation testing for this column. | **OPEN — NEW, BLOCKS 1 BLUE COLUMN** | — |
| DEC-TECH-006 | What population should Category Avg Price average over? | Nivarnan, with Sajeesan technical input | Same marketplace only; same account+marketplace; global across both accounts and all 4 marketplaces | — | — | Determines the `AVG(price) GROUP BY` scope. | Blocks reconciliation testing for this column. | **OPEN — NEW, BLOCKS 1 BLUE COLUMN** | — |
| DEC-CTRL-001 | Should Git be initialized in this project root, and which remote repository should be used? | Coordinator | Record: repository URL; branch; visibility; credential-scan requirement; initial commit approval | — | — | Determines whether/how this project's work is version-controlled and pushed. | N/A to report validation; affects evidence durability/traceability. | OPEN — non-blocking, no commit/push will be attempted | — |
| DEC-CTRL-002 | What measurable KPI determines that the automation succeeded? | Coordinator and Nivarnan | manual time saved per run; reduction in report preparation time; report data-accuracy percentage; zero duplicated spend/sales amounts; report availability before an approved daily deadline; a combined KPI | — | — | Determines what the implementation is ultimately measured against for success/failure. | Determines the acceptance test the finished report must pass. | OPEN | — |

All fields in the "Record" sub-items of DEC-CTRL-001 (repository URL, branch, visibility, credential-scan requirement, initial commit approval) are individually **OPEN** — none has been set.

## 4. Recommended Default Options

**RECOMMENDATION — NOT APPROVED.** These are starting-point suggestions only, offered to speed up the decision conversation. None of them is selected, binding, or usable for implementation until the named owner explicitly approves it in §3 above.

- ~~High spend: Top 20 ASINs by PPC spend.~~ **Moot** — DEC-BUS-001 was resolved by written instruction (no cutoff).
- ~~Zero-sales ASINs: include and flag.~~ **Moot** — DEC-BUS-002 was resolved by written instruction (all combinations included).
- ~~Sales fields: revenue, units, and distinct orders.~~ **Moot** — DEC-BUS-003 was resolved by the confirmed blue-column image (Units Ordered only, no revenue).
- ~~Multi-SKU ASINs: one ASIN summary row with expandable SKU details.~~ **Moot** — DEC-BUS-004 was redefined and approved by written instruction (one row per ASIN+SKU, not aggregated).
- **Stock freshness warning: older than 6 hours.** Still a live recommendation for DEC-BUS-005 — a middle-ground threshold; not needed to ship v001 since the mandatory live-data disclosure doesn't depend on it.
- **Cancelled statuses: treat both Canceled and Cancelled as cancelled, after validating actual frequencies.** Still live for DEC-TECH-003, though now non-blocking (this report doesn't build a refund-aware measure).
- **Accuracy KPI: no spend or sales fan-out and reconciled aggregate totals.** Still live for DEC-CTRL-002.
- **NEW — Sessions/Page Views/Buy Box %/Conversion Rate source (DEC-TECH-004): recommend a technical spike to determine why `amz_traffic_by_asin`'s recent-date coverage is 10–40x below its historical average before deciding whether to use it or find another source** — using it as-is without understanding the coverage drop risks silently under-reporting these 4 columns for most rows.
- **NEW — CTR source (DEC-TECH-005): recommend `public.ppc_performance` (clicks/impressions) as the simpler, already-verified, ASIN-grain-matched candidate**, with `amazon_search_query_performance` reserved as a fallback if Sajeesan determines "Brand Analytics" (not "Advertising Console") is the intended source.
- **NEW — Category Avg Price population (DEC-TECH-006): recommend averaging within the same marketplace, across both accounts** — price is marketplace-dependent (currency/local pricing) but not meaningfully account-dependent, so a marketplace-scoped average is the most defensible default pending confirmation.

## 5. Design Gate

**DESIGN MAY START only when:**

1. DEC-BUS-001 is approved.
2. DEC-BUS-002 is approved.
3. DEC-BUS-003 is approved.
4. DEC-BUS-004 is approved.
5. DEC-BUS-005 is approved.
6. DEC-TECH-001 is approved or publication is formally deferred.
7. DEC-TECH-003 is approved when net/refund-aware sales are required.
8. DEC-CTRL-002 is approved.

Git (DEC-CTRL-001) and skill-review (DEC-TECH-002) decisions may remain open only if:
- no commit/push is attempted; and
- no unapproved skill content is promoted.

**Current state (updated 2026-07-17): gate PARTIALLY OPEN.** DEC-BUS-001–004 are RESOLVED/APPROVED by written instruction. DEC-BUS-005 remains OPEN but is treated as non-blocking (condition 5 waived for v001 — no stale-data warning feature is being built, only the always-included live-data disclosure). DEC-TECH-003 is not required (condition 7 does not apply — no refund-aware measure in this report). **DEC-TECH-001 (ph_task) and DEC-CTRL-002 (KPI) remain OPEN and unwaived** — design/implementation of the HTML report may proceed, but **ph_task publication is blocked** until DEC-TECH-001 is resolved or publication is formally deferred. Three new decisions (DEC-TECH-004/005/006) block 6 of the 15 blue columns from moving off "N/A — pending source confirmation."

## 6. Implementation Gate

**IMPLEMENTATION MAY START only when:**

- the design gate passes;
- SQL aggregation grains are documented;
- field-level source mapping is approved;
- expected HTML fields are approved;
- validation totals and tolerances are defined;
- database writes remain separately gated.

**Current state (updated 2026-07-17): gate PARTIALLY OPEN for the HTML build.** Design gate is sufficiently open to proceed (§5). SQL aggregation grains: documented in `04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md`. Field-level source mapping: **approved for 8 VERIFIED + 2 PARTIAL fields**, NOT approved for 5 REVIEW_REQUIRED fields (DEC-TECH-004/005/006). Expected HTML fields: approved (DEC-BUS-006). Validation totals/tolerances: defined in the validation reports. **Database writes (ph_task) remain separately gated on DEC-TECH-001 and are NOT authorized by this implementation gate.**

## 7. Current Pass/Fail

**AMBER — DECISIONS REQUIRED (narrowed scope, updated 2026-07-17)**

7 of the original 10 decisions are now RESOLVED/APPROVED (DEC-BUS-001–004, 006–011). Remaining OPEN and load-bearing: DEC-BUS-005 (non-blocking), DEC-TECH-001 (**blocks ph_task publication**), DEC-TECH-002 (non-blocking for this requirement), DEC-TECH-003 (non-blocking, not needed), DEC-TECH-004/005/006 (**block 6 of 15 blue columns**), DEC-CTRL-001 (non-blocking, no Git action taken), DEC-CTRL-002 (open, does not block HTML build). This document still passes as a decision register: every unresolved decision has a named owner, available choices are stated where applicable, no decision has been invented, resolved decisions cite their written-instruction basis rather than being silently assumed, recommendations in §4 are clearly separated from and labelled as not-approved, and the design/implementation gates are explicit about what is and is not unblocked.

## 8. One Next Step

Route DEC-TECH-001 (ph_task metadata — blocks publication) and DEC-TECH-004/005/006 (field sources — block 6 columns) to Sajeesan; route DEC-BUS-005 and DEC-CTRL-002 to Nivarnan/coordinator. Proceed with HTML build/validation for the 8 VERIFIED + 2 PARTIAL fields in the interim; do not publish to ph_task until DEC-TECH-001 resolves.
