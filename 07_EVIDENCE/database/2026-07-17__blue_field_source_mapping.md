# Blue Field Source Mapping

**What this is:** Field-by-field source mapping for all 15 required blue columns, each traced to MCP/table/column/filters/aggregation/status.

**Why it exists:** Per instruction, no formula may be invented and every stored value's grain must be verified before use.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Source:** `PRIMARY_SKILLS_MCP` — `get_object_details`, `execute_sql` against `public.listing_data`, `public.order_transaction`, `public.location_wise_inv_stock`, `public.ppc`, `public.ppc_performance`, `public.amz_traffic_by_asin`, `public.traffic_data`, `public.amazon_search_query_performance`.

---

| # | Output field | Business definition | Source MCP | schema.table | Source column | Account filter | Marketplace filter | Date filter | Aggregation grain | Calculation | Missing-data handling | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Amazon ASIN | Channel product identifier | PRIMARY | `public.listing_data` | `ref_id` | `sub_source IN (6,8)` | `market_place IN (...)` | n/a (dimension) | 1 row per distinct ASIN in scope | none | n/a | **VERIFIED** |
| 2 | Amazon SKU | Resolved inventory SKU | PRIMARY | `public.listing_data` | `COALESCE(NULLIF(mapped_sku,''), sku)` | same | same | n/a | per ASIN | `COALESCE` resolution, then base-SKU cleaning (per `ppc-stock-lookup` skill) | if no listing_data row matches → "No mapping" | **VERIFIED** |
| 3 | Product Title | Listing display title | PRIMARY | `public.listing_data` | `title` | same | same | n/a | per ASIN/SKU | none | if blank → "Not available" | **VERIFIED** |
| 4 | Days Since Last Sale in Amazon | Days since the ASIN's most recent completed order | PRIMARY | `public.order_transaction` | `MAX(order_date)` | `order_sub_source IN (6,8)` | `market_place IN (...)` | `order_status='Completed'`, no window (all-time max) | per account+marketplace+ASIN | `(complete_end_date - MAX(order_date)::date)` in days | if never sold → "No sale on record" (not 0) | **VERIFIED** |
| 5 | Units in Stock | Current live stock, warehouse-mapped | PRIMARY | `public.location_wise_inv_stock` | `SUM(COALESCE(stock,0))` | n/a (stock is not account-partitioned) | mapped via marketplace→warehouse rule | n/a (live snapshot) | per resolved SKU + warehouse location | `SUM` grouped by `sku` (duplicate-row safe) | if no stock row → "No current stock record" (not 0) | **VERIFIED** |
| 6 | Sessions | Amazon detail-page session count | — | — | — | — | — | — | — | — | "N/A — source pending confirmation" | **REVIEW_REQUIRED** (see note A) |
| 7 | Page Views | Amazon detail-page view count | — | — | — | — | — | — | — | — | "N/A — source pending confirmation" | **REVIEW_REQUIRED** (see note A) |
| 8 | Units Ordered | Units sold in period | PRIMARY | `public.order_transaction` | `SUM(quantity)` | `order_sub_source IN (6,8)` | `market_place IN (...)` | `order_status='Completed'`, period window | per account+marketplace+ASIN+period | `SUM` | if none → 0 (zero is a proven, valid value here — absence of sale rows genuinely means 0 units) | **PARTIAL** — verified via `order_transaction`; a second, non-reconciled candidate (`amz_traffic_by_asin.unitsOrdered`) exists and is deliberately **not** used (see note B) |
| 9 | Conversion Rate (%) | Share of sessions converting to a sale | — | — | — | — | — | — | — | Workbook-documented formula: `Units Ordered / Sessions` | "N/A — source pending confirmation" | **REVIEW_REQUIRED** (depends on Sessions, note A) |
| 10 | Click-Through Rate (%) | Share of impressions resulting in a click | — | — | — | — | — | — | — | Workbook-documented formula: `Clicks / Impressions` | "N/A — source pending confirmation" | **REVIEW_REQUIRED** (see note C) |
| 11 | Buy Box % | Share of sessions where the account won the Buy Box | — | — | — | — | — | — | — | — | "N/A — source pending confirmation" | **REVIEW_REQUIRED** (see note A) |
| 12 | Price (£) | Current listing price | PRIMARY | `public.listing_data` | `price` (filter `currency='GBP'` where applicable, else document currency shown) | `sub_source IN (6,8)` | `market_place IN (...)` | n/a (live) | per ASIN/SKU | none | if blank → "Not available" | **VERIFIED** |
| 13 | Category Avg Price (£) | Average price across the ASIN's category | PRIMARY | `public.listing_data` (join `category`/`product_type` internally) | `AVG(price)` | not yet decided — see note D | not yet decided — see note D | n/a | category population scope undecided | `AVG(price) GROUP BY category` | "N/A — averaging scope pending confirmation" | **PARTIAL** (see note D) |
| 14 | PPC Spend | Advertising spend in period | PRIMARY | `public.ppc_performance` (+ `public.ppc` for SB exclusion) | `SUM(spend)` | `sub_source_id IN (6,8)` | `marketplace IN (...)` | `source=1, record_type='ad'`, period window | per account+marketplace+ASIN+period | `SUM`, `record_subtype <> 'SB'`, `sku NOT LIKE 'amzn.gr.%'` | if none → 0 (proven valid — no PPC activity is a real zero) | **VERIFIED** |
| 15 | ACOS (%) | Advertising Cost of Sale | PRIMARY | `public.ppc_performance` (calculated) | `SUM(spend)/NULLIF(SUM(sales),0)*100` | same as PPC Spend | same | same | same | Live-documented formula (`get_table_definition('ppc')`, "Required Metric Set") — **no stored ACOS column exists** | if `sales=0` → "N/A (no attributed sales)", not divide-by-zero/0% | **VERIFIED (calculated, formula sourced from primary MCP's own documentation)** |

## Notes

**A — Sessions/Page Views/Buy Box % source ambiguity.** Two candidate tables were checked live:
- `public.amz_traffic_by_asin` — daily grain (`sessions`, `pageViews`, `buyBoxPercentage`, `unitSessionPercentage`, `unitsOrdered` columns exist), matches Amazon's own Business Report terminology. **But** recent-date row counts (6–29 rows/day across the full 2-account×4-marketplace scope in July 2026) are 10–40x below the table's own 551-day historical average (~224 rows/day) — a real, verified coverage degradation, not assumed.
- `public.traffic_data` — has `impression`/`click`/`conversion` but **no Sessions/Page Views/Buy Box% columns at all**, and is confirmed **weekly**-cadence (rows exactly 7 days apart: 2026-07-04, 2026-07-11), not daily.

Neither is safe to build on without a decision: `amz_traffic_by_asin` for correctness-if-complete but currently sparse; `traffic_data` wrong grain entirely (no Sessions/PageViews/BuyBox columns, and weekly not daily). **No value was invented for these fields.**

**B — Units Ordered dual-candidate.** `order_transaction` (transactional, `order_status='Completed'`) and `amz_traffic_by_asin.unitsOrdered` (Amazon's Business Report attribution) are two independent systems that are not guaranteed to match exactly (returns/cancellations/attribution-window differences). `order_transaction` was selected as authoritative because it is fully verified, already used for PPC/sales grain consistency, and is the same source the earlier UK-only discovery validated for revenue/units. This is recorded as a decision with rationale, not a silent choice — flagged PARTIAL pending Sajeesan's confirmation that this is the intended source (vs. the Business Report figure).

**C — CTR three-candidate ambiguity.** The authoritative workbook itself defines CTR as "Clicks / Impressions" sourced from "Brand Analytics / Advertising Console" (from the original `NoMoving_DataMapping` sheet, reviewed in the prior UK-only discovery) — this points to either `ppc_performance` (Advertising Console = PPC) or `amazon_search_query_performance` (Brand Analytics), not decisively to one. `traffic_data` also has impression/click but is weekly-cadence (ruled out for a daily/7-14-30-day report on cadence grounds alone). No value was invented; the two remaining candidates are recorded for technical decision.

**D — Category Avg Price population scope.** The averaging population (same marketplace only? same account+marketplace? global across both accounts and all 4 marketplaces?) has no documented business rule anywhere in the workbook, the images, or the task instruction. `Category`/`product_type` and `price` both exist on `listing_data` and are technically sufficient to compute any of these variants — the blocker is purely the scope decision, not data availability.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer — required to resolve notes A, B, C, D before those 5 fields (6 counting both PARTIAL fields fully) can move from placeholder to live data.

## Status

**8 of 15 fields VERIFIED**, 2 PARTIAL (usable with a documented interim default), 5 REVIEW_REQUIRED (rendered as explicit "N/A — pending source confirmation", not guessed).

## Pass/fail rule

PASS if every field's status is backed by a live query or an explicit, reasoned "no safe source found" — not a guess. Met for all 15 fields.

## Next action

Route notes A–D to Sajeesan; implement the 8 VERIFIED + 2 PARTIAL fields with real data now; leave the 5 REVIEW_REQUIRED fields as explicit placeholders in the v001 HTML output.
