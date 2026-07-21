# Required Field Grain Classification — ANPIA Common Daily Dataset Rebuild

**What this is:** Field-by-field classification of every required output field's true PostgreSQL source grain, per REQ-01-D02's instruction to classify before designing the common daily dataset.

**Method:** Live schema/metadata inspection and small bounded discovery queries via `mcp__claude_ai_postgres__*` (table definitions, `information_schema.columns`, distinct-value/date-range checks). **No bulk data transport was performed** — every query below returns schema metadata or small aggregate/distinct-value results, not report rows.

**Scope note:** This document classifies fields. It does **not** build or extract the common dataset — see §7 blocker in the accompanying evidence/handover for why extraction itself did not proceed in this task.

---

## New finding this session: `public.amz_traffic_by_asin`

Previous discovery (2026-07-17, decision register DEC-TECH-004/005/006) recorded Sessions, Page Views, Conversion Rate, Click-Through Rate, and Buy Box % as having **no confidently-complete approved source**. A fresh table-by-table sweep of `public` (not performed in the earlier session) found **`public.amz_traffic_by_asin`** — Amazon's own daily Sales & Traffic business report, loaded at **date + childAsin + sku + sub_source + marketplace** grain, with columns including `sessions`, `pageViews`, `unitsOrdered`, `orderedProductSales`, `buyBoxPercentage`, `unitSessionPercentage`. This resolves Sessions, Page Views, and Buy Box % (DEC-TECH-004/005 no longer "no source"), and provides a second, independently-sourced Units Ordered figure at true daily ASIN grain.

**Disclosed data-freshness gap (real finding, not resolved by this document):** coverage is not uniform. Verified via live query:

| Account | Marketplace | Min date | Max date | Rows |
|---|---|---|---|---|
| DCVoltage | UK | 2025-03-07 | **2026-04-22** | 44,947 |
| DCVoltage | Germany | 2025-03-07 | **2026-04-22** | 4,139 |
| DCVoltage | Italy | 2025-03-08 | **2026-04-22** | 504 |
| LEDSONE | UK | 2025-01-01 | 2026-06-16 | 51,773 |
| LEDSONE | Germany | 2025-01-01 | 2026-07-18 | 10,127 |
| LEDSONE | France | 2025-01-01 | 2026-07-13 | 9,164 |
| LEDSONE | Italy | 2025-03-01 | 2026-06-22 | 3,096 |
| DCVoltage | France | — | — | **0 rows (no data at all)** |

DCVoltage's feed for this table stopped updating on 2026-04-22 (~3 months before this document's date). LEDSONE's feeds are current to within 1–5 weeks depending on marketplace. **This means Sessions/Page Views/Buy Box/this-table's-Units-Ordered will be genuinely `N/A - source not available` for all DCVoltage rows in any 7/14/30-day window ending on or after 2026-04-23**, and for LEDSONE rows in periods after each marketplace's own max date. This is a real source-data gap, not a query defect — it must be surfaced in the report via the missing-data rule, not silently zero-filled.

For comparison, `public.order_transaction` (the sales/revenue source) is current: `MAX(order_date)` = **2026-07-20** for both accounts combined.

---

## Field Classification Table

| # | Field | Source schema.table | Source column(s) | Source grain | Classification | Aggregation rule | Null handling | Known limit | Validation query |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Account | `public.listing_data` / `public.ppc` / `public.order_transaction` | `sub_source_name` / `ss_name` / `ss_name` | Per-row (dimension) | CURRENT_SNAPSHOT (dimension label) | N/A (grouping key, not aggregated) | Never null — must resolve to LEDSONE or DCVoltage | `sub_source_id` values differ by table (6/8) but resolve to the same two accounts | `SELECT DISTINCT sub_source_id, sub_source_name FROM listing_data WHERE sub_source_id IN (6,8)` |
| 2 | Marketplace | same as above | `market_place` / `marketplace` | Per-row (dimension) | CURRENT_SNAPSHOT (dimension label) | N/A (grouping key) | Never null — must resolve to UK/Germany/France/Italy | Column name differs: `market_place` in `ppc`/`listing_data`/`order_transaction`, `marketplace` in `ppc_performance` | `SELECT DISTINCT market_place FROM listing_data WHERE sub_source_id IN (6,8)` |
| 3 | Amazon ASIN | `public.listing_data` | `ref_id` (where `which_channel=1`) | Per-listing (dimension) | CURRENT_SNAPSHOT | N/A (grouping key) | Never null | — | `SELECT ref_id FROM listing_data WHERE which_channel=1 AND wrong_sku=0` |
| 4 | Amazon SKU (resolved) | `public.listing_data` | `COALESCE(NULLIF(mapped_sku,''), sku)` | Per-listing (dimension) | CURRENT_SNAPSHOT | N/A (grouping key) | Never null after COALESCE | Multi-SKU ASINs exist (~3.4%, confirmed 2026-07-17) — produces multiple report rows per ASIN, by design | Unchanged from D01 `06_VALIDATION/2026-07-17__sql_validation_report.md` Check 6 |
| 5 | Product Title | `public.listing_data` | `title` | Current snapshot (not date-stamped) | CURRENT_SNAPSHOT | Take latest/current row only — never historical | `N/A - source not available` if title is empty | Sparse for eBay, not relevant here (Amazon only) | — |
| 6 | Days Since Last Sale in Amazon | `public.order_transaction` | `order_date`, `order_status='Completed'`, `asin` | Event-level (per completed order) | HISTORICAL_LOOKUP | `report_end_date - MAX(order_date::date)` per account+marketplace+ASIN+SKU, independent of the 7/14/30 window | `No sale on record` if no completed order exists up to report_end_date | Must look back beyond the report window (a sale 90 days ago must still be found) — cannot be derived from the 30-day common dataset alone | `SELECT asin, MAX(order_date::date) FROM order_transaction WHERE order_status='Completed' AND source_name='AMAZON' GROUP BY asin` |
| 7 | Units in Stock | `public.location_wise_inv_stock` | `stock`, `sku`, `location` | Current snapshot (no date column — `updated_at` only) | CURRENT_SNAPSHOT | `SUM(stock)` grouped by `(resolved_sku, location)`, joined post-aggregation; UK marketplace reads UK location, DE/FR/IT all read the shared German location | `No current stock record` if no row exists for that SKU/location | Live snapshot only — no historical stock; confirmed via raw column check (`id, sku, stock, location, updated_at` — no per-date grain exists in this table at all) | `SELECT sku, location, SUM(stock) FROM location_wise_inv_stock GROUP BY sku, location` |
| 8 | Sessions | `public.amz_traffic_by_asin` | `sessions` | **Daily** (`date` column, per childAsin/sku/sub_source/marketplace) | DAILY_ADDITIVE | `SUM(sessions)` per report_date+account+marketplace+ASIN+SKU | `N/A - source not available` where no row exists for that date (incl. all DCVoltage rows after 2026-04-22) | Freshness gap disclosed above | `SELECT date, childAsin, sku, SUM(sessions) FROM amz_traffic_by_asin WHERE sub_source_id IN (6,8) GROUP BY 1,2,3` |
| 9 | Page Views | `public.amz_traffic_by_asin` | `pageViews` | Daily | DAILY_ADDITIVE | `SUM(pageViews)` | Same as Sessions | Same freshness gap | Same pattern as Sessions |
| 10 | Units Ordered | `public.order_transaction` (primary, sales-grain) | `quantity`, `order_status='Completed'`, `order_date` | Daily (event-level, aggregable by day) | DAILY_ADDITIVE | `SUM(quantity)` per report_date+account+marketplace+ASIN+SKU, `order_status='Completed'` only | `0` is a proven fact if a query returns no completed orders for that day (not missing data) | `order_transaction.asin` bridges via `listing_data`, not `amz_traffic_by_asin.unitsOrdered` (kept as a cross-check field only, per its own freshness gap) | Reconciliation query — compare `SUM(order_transaction.quantity)` vs `SUM(amz_traffic_by_asin.unitsOrdered)` for LEDSONE UK where both are fresh |
| 11 | Conversion Rate (%) | Derived | `SUM(units ordered) / SUM(sessions) * 100` | Derived from #8 + #10 | DERIVED_RATIO | Recalculate from period-aggregated totals — never average daily percentages | `N/A - source not available` if `SUM(sessions)=0` (safe zero-denominator) | Inherits the Sessions freshness gap | — |
| 12 | Click-Through Rate (%) | `public.ppc_performance` | `clicks`, `impressions` (Amazon, `record_type='ad'`) | Daily (`date` column) | DAILY_ADDITIVE inputs → DERIVED_RATIO | `SUM(clicks) / SUM(impressions) * 100` after period aggregation | `N/A - source not available` if `SUM(impressions)=0` | This is PPC (advertising) CTR, not organic-traffic CTR from `traffic_data` — consistent with CTR sitting alongside PPC Spend/ACOS in the required-field list | Unchanged from D01 PPC pattern |
| 13 | Buy Box % | `public.amz_traffic_by_asin` | `buyBoxPercentage` | Daily (Amazon pre-computed daily percentage — **no raw won/eligible counts are exposed**, only the finished daily %) | DERIVED_RATIO (with disclosed compromise) | **Sessions-weighted average** of the daily percentage across the period: `SUM(buyBoxPercentage * sessions) / SUM(sessions)` — the closest available approximation to a true recalculated ratio, since Amazon does not expose the numerator/denominator behind this field | `N/A - source not available` where no row exists | **Genuine source limitation, not a query defect:** cannot be recalculated from true base counts because Amazon's own feed does not provide them at this grain — disclosed here rather than silently averaged naively | `SELECT date, childAsin, buyBoxPercentage, sessions FROM amz_traffic_by_asin` |
| 14 | Price (£) | `public.listing_data` | `price`, `currency` | Current snapshot | CURRENT_SNAPSHOT | Take latest/current row only | `N/A - source not available` if null | Unchanged from D01 | — |
| 15 | Category Avg Price (£) | `public.listing_data` | `AVG(price)` grouped by `product_type` (category) | Current snapshot, aggregated across current listings | CURRENT_SNAPSHOT (aggregated) | `AVG(price)` over current listing rows sharing the same `product_type`, computed once (not per day) | `N/A - source not available` if category has no priced listings | Averaging population (marketplace-only vs account+marketplace vs global) still **not approved** — same open item as D01 (decision register DEC unresolved) | — |
| 16 | PPC Spend | `public.ppc_performance` (Amazon, joined via `public.ppc` for SB exclusion) | `spend` | Daily | DAILY_ADDITIVE | `SUM(spend)` per report_date+account+marketplace+ASIN(+SKU via bridge) | `0` is a proven fact for a day with campaigns running but no spend; `N/A` only if the ASIN has zero bridge match at all | Unchanged from D01 — SB (Sponsored Brands) campaigns excluded per the established rule (ad-level ASIN mapping unreliable for SB) | Unchanged from D01 |
| 17 | ACOS (%) | Derived | `SUM(spend) / SUM(attributed sales) * 100` | Derived from #16 + PPC `sales` | DERIVED_RATIO | Recalculate from period-aggregated totals | `N/A - source not available` if `SUM(attributed sales)=0` | Unchanged from D01 | — |

---

## Classification summary

- **DAILY_ADDITIVE:** Sessions, Page Views, Units Ordered, PPC Spend, PPC clicks/impressions/attributed-sales (inputs to CTR/ACOS)
- **DERIVED_RATIO:** Conversion Rate, Click-Through Rate, ACOS, Buy Box % (with the disclosed sessions-weighted-average compromise for Buy Box, since raw counts aren't exposed)
- **CURRENT_SNAPSHOT:** Account/Marketplace/ASIN/SKU (dimensions), Product Title, Units in Stock, Price, Category Avg Price
- **HISTORICAL_LOOKUP:** Days Since Last Sale in Amazon
- **PERIOD_ONLY:** none — every required field was resolved to a daily-or-finer source grain (a material improvement over the 2026-07-17 discovery, which had 5 fields with no approved source at all)

## Known limits carried into the common dataset design

1. Buy Box % cannot be recalculated from true base counts (Amazon does not expose them) — sessions-weighted daily average is the documented, disclosed compromise.
2. `amz_traffic_by_asin` has an account/marketplace-dependent freshness ceiling (DCVoltage: 2026-04-22; LEDSONE varies 2026-06-16 to 2026-07-18) — any report window extending past those dates will show genuine `N/A` for Sessions/Page Views/this-table's-Units-Ordered/Buy-Box on the affected rows. Units Ordered for the report itself uses `order_transaction` (current to 2026-07-20), not this table, so the core sales metric is unaffected.
3. `amz_traffic_by_asin` has zero rows for DCVoltage×France (consistent with the 2026-07-17 finding that DCVoltage has no France presence at all).
4. Category Avg Price's averaging population is still unapproved (unchanged open item).

## Next step

Use this classification to build `04_DESIGN/2026-07-20__common_daily_dataset_design.md` (next document).

---

## Addendum — 2026-07-20 (later same session) — Live re-validation with direct PostgreSQL access

Following user authorization to use direct credentials, every field above was re-checked live (not assumed) via `05_IMPLEMENTATION/src/anpia_*` modules. Two material updates:

### Category Avg Price — source now confirmed approved

`listing_data.product_type` is **100% populated** for both accounts' Amazon listings (90,327/90,327 rows have a non-null `product_type`, 150 distinct categories) — verified via a live `COUNT`/`COUNT(product_type)` query. The averaging-population question (marketplace-only vs. account+marketplace vs. global) remains a business decision not resolved by data availability alone; this implementation defaulted to **`(marketplace, product_type)`** as a reasonable, disclosed default — not silently invented, and explicitly flagged for business sign-off in the handover.

### DCVoltage `amz_traffic_by_asin` freshness — root cause confirmed

Investigated per instruction ("do not silently treat stale data as current zero activity"). Live findings:
- `order_transaction` (sales) and `ppc_performance` (PPC) for DCVoltage are both current to **2026-07-19** — DCVoltage is fully active on sales and advertising.
- `amz_traffic_by_asin` for DCVoltage stops at **2026-04-22** across all marketplaces — confirmed via `MAX(date)` per source, run in the same query as the sales/PPC freshness check.
- No alternate `sub_source_id` exists for DCVoltage in `amz_traffic_by_asin` (checked via `sub_source_name ILIKE '%dcv%'` — only `sub_source_id=6` found, same identifier used everywhere else) — rules out a wrong-account-identifier explanation.
- Monthly row-count trend for DCVoltage×UK in this table shows a genuine, gradual decline (4,426 → 3,116 rows/month from Sept 2025 through March 2026) followed by a **hard stop** after 2026-04-22 (1,956 rows that partial month, then zero) — this pattern is consistent with a real upstream feed/API disconnection specific to this one report type for this one account, not a marketplace-mapping error and not genuine zero business activity.

**Conclusion: "source data truly stops" (the correct explanation per the three offered in the task instructions) — not a mapping error, not zero activity.** Sessions/Page Views/Buy Box % for DCVoltage will correctly show `N/A - source not available` for any date after 2026-04-22, clearly distinguished from a `0` value, per the missing-data rule.

### fic_by_asin

No table literally named `fic_by_asin` exists. A fuzzy `information_schema.tables` search confirms this refers to the already-identified `public.amz_traffic_by_asin` — re-confirmed, same table used throughout this addendum.

### No change

All other field classifications, sources, and grains from the original table above were re-confirmed live and required no changes.
