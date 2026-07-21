# Common Daily Dataset Design — ANPIA Rebuild (REQ-01-D02)

**What this is:** Design for the single common daily-grain dataset that all three (7/14/30-day) report views must derive from, per REQ-01-D02's explicit correction (no independently-fetched per-period datasets).

**Status:** DESIGN ONLY. The dataset described here has **not** been extracted or populated — see the accompanying evidence/handover for why extraction did not proceed in this task (no direct-PostgreSQL credential source available).

**Depends on:** `03_DISCOVERY/2026-07-20__required_field_grain_classification.md`.

---

## Daily-grain key

```
report_date + account + marketplace + amazon_asin + resolved_amazon_sku
```

`account` = resolved from `sub_source_id` (6 → DCVoltage, 8 → LEDSONE). `marketplace` = `market_place`/`marketplace` text value (UK/Germany/France/Italy). `resolved_amazon_sku` = `COALESCE(NULLIF(mapped_sku,''), sku)` from `listing_data`, per the established, previously-validated bridge rule (unchanged from D01 — the `DISTINCT ON` tiebreaker fix that resolved the 2026-07-17 row-key-duplication defect still applies).

## Source-to-target mapping

| Common dataset field | Source | Grain |
|---|---|---|
| `report_date` | driving date column per source (see below) | daily |
| `account`, `marketplace`, `asin`, `resolved_sku` | `listing_data` bridge (dimension resolution, current snapshot) | n/a (join key) |
| `ppc_spend`, `ppc_clicks`, `ppc_impressions`, `ppc_attributed_sales` | `ppc_performance.date` (Amazon, `record_type='ad'`, joined to `ppc` for SB exclusion) | daily |
| `sessions`, `page_views`, `units_ordered_amz_report`, `ordered_sales_revenue_amz_report`, `buy_box_percentage` | `amz_traffic_by_asin.date` | daily |
| `units_ordered`, `sales_revenue` (primary sales metric) | `order_transaction.order_date::date`, `order_status='Completed'` | daily (event-level, aggregated per day) |

Two independent Units Ordered figures exist (`order_transaction` and `amz_traffic_by_asin.unitsOrdered`) — `order_transaction` is the **primary** figure for the report (per D01's established rule: `order_total`/`quantity` from `order_transaction`, never `item_price*quantity`); `amz_traffic_by_asin`'s figure is retained in the daily facts only as a cross-check field, not displayed, given its account-dependent freshness gap (see classification doc).

## Additive fields (SUM per day, then SUM again across the period)

`ppc_spend`, `ppc_clicks`, `ppc_impressions`, `ppc_attributed_sales`, `sessions`, `page_views`, `units_ordered`, `ordered_sales_revenue`.

## Derived metrics (recalculated after period aggregation — never stored as daily percentages)

- Conversion Rate = `SUM(units_ordered) / SUM(sessions) * 100`
- Click-Through Rate = `SUM(ppc_clicks) / SUM(ppc_impressions) * 100`
- ACOS = `SUM(ppc_spend) / SUM(ppc_attributed_sales) * 100`
- Buy Box % = `SUM(buy_box_percentage_daily * sessions) / SUM(sessions)` (sessions-weighted average — disclosed compromise, see classification doc §Buy Box)

All four use safe zero-denominator handling: `NULLIF(denominator, 0)`, surfaced as `N/A - source not available` when the denominator is zero across the whole period, not as `0` or `#DIV/0!`.

## Current snapshot joins (joined once, after 7/14/30 aggregation — never per daily row)

- `listing_data`: Product Title, Price, current dimension resolution.
- `listing_data` aggregated by `product_type`: Category Avg Price (population still unapproved — open item).
- `location_wise_inv_stock`, aggregated `SUM(stock)` by `(resolved_sku, location)` **before** the join, joined by warehouse-mapping rule (UK→UK location; Germany/France/Italy→shared German location). Never repeated-and-summed across marketplace rows in any total.

## Historical lookup join (joined once, after aggregation)

Days Since Last Sale: for each final `account+marketplace+ASIN+resolved_sku` identity, `report_end_date - MAX(order_date::date)` from `order_transaction` where `order_status='Completed'`, with **no** lower bound on how far back it searches (a sale from a year ago must still be found — this lookup is independent of the 7/14/30-day window). `No sale on record` when no completed order exists at all for that identity up to `report_end_date`.

## Missing-data rules

Unchanged from D01: explicit `N/A - source not available` / `No mapping` / `No sale on record` / `No current stock record` — never substitute `0` for a genuinely unknown value; `0` is used only where zero is a proven fact (e.g., a day with active campaigns but confirmed zero spend, or a day with confirmed zero completed orders).

## Duplicate prevention

Daily-grain key (`report_date, account, marketplace, asin, resolved_sku`) must be unique in the common dataset — enforced by aggregating each source (PPC, traffic, sales) independently to this exact grain **before** any join (aggregate-before-join pattern, unchanged from D01's fan-out fix), then joining pre-aggregated sources only, never raw event-level rows to each other directly.

## Partition / date-window rules

Latest complete date is determined from the **primary sales source** (`order_transaction`), not from the least-fresh supplementary source (`amz_traffic_by_asin`), since the core report identity (spend/sales/stock) must not be held hostage to a secondary field's freshness gap. As of 2026-07-20, `MAX(order_date::date)` for both accounts = **2026-07-20** — however the current, still-in-progress day must be excluded per the "no incomplete day" rule, so the actual latest **complete** date requires one more check (`MAX(order_date::date)` where a full day's data is confirmed settled — e.g., excluding "today" and using yesterday, 2026-07-19, unless evidence shows same-day data is already complete; this final determination is deferred to the actual extraction run, not fixed in this design document, since it depends on live data at extraction time).

7-day: `latest_complete_date - 6` through `latest_complete_date`.
14-day: `latest_complete_date - 13` through `latest_complete_date`.
30-day: `latest_complete_date - 29` through `latest_complete_date`.

All three periods read from the **same** common daily dataset (built once, covering the full 30-day window) — the 7-day and 14-day views are simply narrower `WHERE report_date BETWEEN ...` filters over the same rows, aggregated to the same final report grain (`account+marketplace+ASIN+resolved_sku`), never derived by dividing or sampling the 30-day aggregate.

## Validation rules (to be executed once the dataset is actually built)

1. Daily key uniqueness: `COUNT(*) = COUNT(DISTINCT report_date, account, marketplace, asin, resolved_sku)`.
2. Null key count = 0 for all five key columns.
3. Source date coverage matches the resolved date window exactly (no gaps, no rows outside the window).
4. Both accounts present; all four marketplaces present where source data exists (DCVoltage×France expected to be genuinely absent, as previously confirmed).
5. No raw-table join fan-out (aggregate-before-join structurally prevents this — verify row counts pre/post join match expectations, same method as D01's Check 3).
6. Daily source totals reconcile against the common dataset's daily totals (spot-check per source).
7. 7/14/30-day derived aggregates reconcile against independently-summed daily rows for the same window (not against each other).
8. Current-snapshot fields (stock, price, title, category avg price) excluded from any additive daily total.
9. Credential scan clean (no secrets in the dataset file or checkpoints).

## Known limits

- Buy Box % is a sessions-weighted average of Amazon's own daily percentage, not a true recalculation from raw won/eligible counts (Amazon does not expose those counts at this grain).
- Sessions/Page Views/this-table's-Units-Ordered are genuinely unavailable (`N/A`) for DCVoltage rows in any window after 2026-04-22, and for LEDSONE rows past each marketplace's own max date (see classification doc for exact dates) — this will visibly reduce data completeness for the most recent days of the report for these specific fields only; the core PPC/sales/stock fields are unaffected.
- Category Avg Price averaging population remains unapproved (unchanged open item from D01).
- The exact "latest complete date" determination is deferred to actual extraction time (requires a live query against current data, not fixed at design time).

## Next step

Extraction against this design requires either (a) a working direct PostgreSQL credential (`ANPIA_DB_*` env vars, currently unset — see `07_EVIDENCE/database/2026-07-20__direct_credential_access_validation.md`) or (b) explicit approval to use bounded MCP batching for this purpose (as was approved for the 2026-07-17 30-day extraction) — this task's own instructions explicitly disallow MCP for bulk transport and require direct credential access, so extraction did not proceed; see the handover for the resulting blocker and required next action.
