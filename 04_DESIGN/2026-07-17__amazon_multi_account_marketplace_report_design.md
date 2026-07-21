# Amazon Multi-Account/Marketplace Report — Design

**What this is:** The technical design for the REQ-AMZ-NMP-001-D01 daily report, translating the discovery evidence and approved decisions into field-level source mapping, row key, grain, period logic, stock logic, and missing-data handling.

**Why it exists:** Per project control, no SQL/HTML may be built before a documented design traces every field to its source.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Sources used:** `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`, all `07_EVIDENCE/database/2026-07-17__*` files, `04_DESIGN/2026-07-17__amazon_high_spend_asin_decision_register.md`.

**Owner/reviewer:** Technical reviewer: Sajeesan. Business validator: Nivarnan.

**Status:** DESIGN — approved for the 10 VERIFIED/PARTIAL fields; 5 fields pending DEC-TECH-004/005/006.

---

## A. Field-level source map

| Field | MCP | Table | Column/expression | Filters | Aggregation | Output format |
|---|---|---|---|---|---|---|
| Amazon Account | PRIMARY | `listing_data`/`ppc`/`order_transaction` | display label from `sub_source_id` (8→"LEDSONE", 6→"DCVoltage") | `sub_source_id IN (6,8)` | dimension | text |
| Marketplace | PRIMARY | same | `marketplace`/`market_place` | `IN ('UK','Germany','France','Italy')` | dimension | text |
| Amazon ASIN | PRIMARY | `listing_data` | `ref_id` | `which_channel=1, wrong_sku=0, is_parent=0` | dimension | text |
| Amazon SKU | PRIMARY | `listing_data` | `COALESCE(NULLIF(mapped_sku,''), sku)`, then base-SKU suffix cleaning | same | dimension | text |
| Product Title | PRIMARY | `listing_data` | `title` | same | 1:1 per ASIN/SKU | text |
| Days Since Last Sale in Amazon | PRIMARY | `order_transaction` | `report_end_date - MAX(order_date)::date` | `order_sub_source IN(6,8), market_place IN(...), order_status='Completed'`, all-time max (no period window) | per account+marketplace+ASIN | integer days, or "No sale on record" |
| Units in Stock | PRIMARY | `location_wise_inv_stock` | `SUM(COALESCE(stock,0))` | `location = CASE WHEN marketplace='UK' THEN 'UK' ELSE 'Germany' END`, `sku = resolved SKU` | per resolved SKU + warehouse | integer, or "No current stock record" |
| Price (£) | PRIMARY | `listing_data` | `price` | same as ASIN, plus currency check | per ASIN/SKU (live) | currency, 2dp |
| PPC Spend (Nd) | PRIMARY | `ppc_performance` + `ppc` (SB join) | `SUM(spend)` | `source=1, sub_source_id IN(6,8), marketplace IN(...), record_type='ad', p.record_subtype<>'SB', sku NOT LIKE 'amzn.gr.%'`, period window | per account+marketplace+ASIN+period | currency, 2dp |
| ACOS (%) | PRIMARY | `ppc_performance` (calculated) | `SUM(spend)/NULLIF(SUM(sales),0)*100` | same as PPC Spend | same | %, or "N/A (no attributed sales)" |
| Units Ordered (Nd) | PRIMARY | `order_transaction` | `SUM(quantity)` | `order_status='Completed'`, period window | per account+marketplace+ASIN+period | integer |
| Sessions (Nd) | — | — | — | — | — | **"N/A — pending source confirmation" (DEC-TECH-004 open)** |
| Page Views (Nd) | — | — | — | — | — | **"N/A — pending source confirmation" (DEC-TECH-004 open)** |
| Conversion Rate (%) | — | — | Workbook formula: `Units Ordered / Sessions` — cannot compute without Sessions | — | — | **"N/A — pending source confirmation" (DEC-TECH-004 open)** |
| Click-Through Rate (%) | — | — | Workbook formula: `Clicks / Impressions` | — | — | **"N/A — pending source confirmation" (DEC-TECH-005 open)** |
| Buy Box % | — | — | — | — | — | **"N/A — pending source confirmation" (DEC-TECH-004 open)** |
| Category Avg Price (£) | — | `listing_data` (category population undecided) | `AVG(price)` | population scope undecided | — | **"N/A — pending source confirmation" (DEC-TECH-006 open)** |

## B. Row key

**`account + marketplace + ASIN + resolved SKU`** (DEC-BUS-004, approved). One row per unique combination. Multi-SKU ASINs produce multiple rows, one per resolved SKU — stock is per-row (per SKU), never summed across an ASIN's SKUs into a single figure.

## C. Metric grain classification

| Field | Grain |
|---|---|
| ASIN, SKU, Product Title, Price | account-marketplace-ASIN-SKU level |
| Days Since Last Sale, PPC Spend, ACOS, Units Ordered | account-marketplace-ASIN level (repeats identically across an ASIN's multiple SKU rows — see §D) |
| Units in Stock | SKU-warehouse level (genuinely varies per SKU row, does not repeat) |
| Category Avg Price | category-marketplace level (repeats across all ASINs sharing a category, once resolved) |
| Sessions/Page Views/Conversion Rate/CTR/Buy Box % | not yet implemented — grain pending DEC-TECH-004/005 |

## D. Repeated metrics

PPC Spend, ACOS, Units Ordered, and Days Since Last Sale are computed at **ASIN** grain, not SKU grain — for a multi-SKU ASIN (3.3% of ASINs per prior discovery), these four values will be **identical** across that ASIN's multiple output rows (one per SKU). This is intentional and documented, not a bug:

- **Repeated-value behavior documented:** yes, here and in the HTML template's column footnote.
- **Report totals deduplicate at the correct metric grain:** any PPC Spend/Units Ordered/ACOS **summary total** shown on the page must be computed from a pre-deduplicated `(account, marketplace, ASIN)` set, not by summing the visible per-row values (which would multiply a multi-SKU ASIN's spend by its SKU count). Enforced in `data_transform.py` by keeping a separate ASIN-grain aggregate for any summary card, distinct from the row-grain table data.
- **CSV/export grain indicator:** the CSV includes the same account+marketplace+ASIN+SKU row grain as the HTML table (no separate rollup file in v001) — a footnote/header comment states PPC Spend/ACOS/Units Ordered/Days-Since-Last-Sale are ASIN-level and repeat across an ASIN's SKU rows.
- **Validation proves no inflated totals:** `06_VALIDATION/2026-07-17__sql_validation_report.md` includes a reconciliation check comparing `SUM(distinct ASIN-grain spend)` against a naive `SUM(all displayed rows)` to prove the two differ by exactly the expected multi-SKU duplication factor, not more.

## E. Period logic

Global common complete end date = **2026-07-15** (verified in discovery; both PPC and sales proven partial on 2026-07-16 across all 6 "healthy" account×marketplace combinations). Applied as **one global end-date rule** (not per-account-marketplace), with Dcvoltage×Italy's PPC sparsity within the window documented as a known coverage limitation rather than hidden.

- 7-day window: 2026-07-09 to 2026-07-15
- 14-day window: 2026-07-02 to 2026-07-15
- 30-day window: 2026-06-16 to 2026-07-15

Column labels are generated from the selected period at render time (`f"PPC Spend ({period}d)"`), never hardcoded to "30d" in the data-transform logic — the period value is a parameter threaded through every query and every label.

## F. Stock logic

- Current stock only — no historical stock, no period-window filter applied to the stock query.
- Warehouse key = `CASE WHEN marketplace='UK' THEN 'UK' ELSE 'Germany' END`.
- Any summary/total stock figure is computed by first deduplicating on `(resolved_sku, warehouse_location)` before summing, so a SKU sold under both Germany, France, and Italy marketplace rows is not counted three times in a total.
- Per-row display shows the same German-warehouse figure independently on each of the Germany/France/Italy rows for a given SKU — this is intentional (operational comparison) and is not itself a duplication bug; only *summary totals* must deduplicate.
- Mandatory disclosure, shown once near the top of the HTML page and repeated as a column-header tooltip on "Units in Stock": **"These stock figures are based on live data, not past records."**

## G. Missing data

| Condition | Display value |
|---|---|
| No `listing_data` bridge row for a PPC/sales-observed ASIN | row omitted from bridge-dependent columns only if the ASIN cannot be resolved to any SKU at all; otherwise SKU shown, dependent fields "No mapping" |
| No stock row for the resolved SKU/warehouse | "No current stock record" |
| ASIN never sold in this account+marketplace | "No sale on record" for Days Since Last Sale |
| No sales/PPC activity in the selected period | `0` (a proven, valid value — not missing data) |
| Sessions/Page Views/Conversion Rate/CTR/Buy Box %/Category Avg Price | "N/A — pending source confirmation" (not `0`, not blank — explicitly distinct from a proven zero) |

Zero is never substituted for a genuinely unknown/unconfirmed value.

## Pass/fail rule

PASS if every displayed field traces to this table (or an explicit N/A reason), the row key and grain are unambiguous, repeated-value behavior is documented with a validation check, and stock/period logic match the discovery evidence exactly.

## Known limitations

5 of 15 blue columns are not yet implemented (DEC-TECH-004/005/006 open). Category Avg Price's default population (marketplace-scoped, both accounts) is a documented recommendation, not an approval.

## Next action

Proceed to implementation (`05_IMPLEMENTATION/`) for the 10 VERIFIED/PARTIAL fields.
