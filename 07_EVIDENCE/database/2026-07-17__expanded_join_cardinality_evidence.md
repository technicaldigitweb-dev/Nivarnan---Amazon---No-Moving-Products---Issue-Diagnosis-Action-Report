# Expanded Join & Cardinality Evidence (Multi-Account / Multi-Marketplace)

**What this is:** Extension of the UK-only join-multiplication evidence to the full 2-account × 4-marketplace scope, plus the new account+marketplace row-key requirement.

**Why it exists:** A wider account/marketplace scope changes the join surface (more accounts sharing ASINs, marketplace-shared warehouse stock) and must be re-risk-assessed, not assumed safe by extension.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Source:** `PRIMARY_SKILLS_MCP`.

---

## Row key requirement — confirmed necessary

The output row key is **account + marketplace + ASIN + resolved SKU**, not ASIN+SKU alone. Confirmed necessary by direct evidence: `listing_data` rows for `ref_id`/ASIN are independently scoped by `sub_source` (account) and `market_place` — the same ASIN string can and does appear under both `sub_source=6` (Dcvoltage) and `sub_source=8` (Ledsone) as fully independent listing rows with potentially different `price`, `mapped_sku`, or stock-relevant SKU. Deduplicating on ASIN+SKU alone would silently merge two operationally distinct account listings into one row.

## Shared-warehouse double counting (carried from marketplace-warehouse evidence)

Germany, France, and Italy marketplace rows all resolve to `location='Germany'` for stock. A physical-stock **summary total** across all three would triple-count the same warehouse units for any SKU that is listed for sale in more than one of those three marketplaces. Per-row display of the same figure on each marketplace's row is permitted; summary totals must deduplicate by `(resolved_sku, warehouse_location)` first.

## PPC fan-out — reconfirmed at the expanded scope

The join-multiplication mechanism proven in the UK-only discovery (naive ASIN→`listing_data` join without pre-aggregation can fan out spend up to 6x) is a property of `listing_data`'s many-rows-per-`ref_id` shape, not specific to the UK marketplace or any one account. It applies identically to all 8 account×marketplace combinations. Not independently re-measured per combination in this pass (would require 8 repeat queries); the underlying mechanism was structurally reconfirmed via the account/marketplace verification in §A/§B of the discovery addendum (same `listing_data` schema, same `wrong_sku`/`mapped_sku` columns, same join keys, used identically regardless of account or marketplace value). **Recommendation:** re-verify empirically (via the same aggregate-then-join test used in the UK-only discovery) for at least one non-UK combination (e.g. Ledsone × Germany) during SQL validation, before publication — not yet done in discovery, flagged for the validation stage.

## DCVoltage × France — cardinality is genuinely zero for spend/sales, non-zero for traffic

Already documented in the account/marketplace filter evidence — repeated here because it is a join-cardinality edge case: any join keyed on `account+marketplace+ASIN` sourced from `ppc_performance`/`order_transaction`/`listing_data` will correctly produce **zero rows** for Dcvoltage×France (there is nothing to join). A join that instead started from `traffic_data` for this combination would find rows with no PPC/sales/listing counterpart — a `BRIDGE_MISSING` condition for that specific combination if traffic fields are ever added to the confirmed field set. Since Sessions/Page Views/CTR/Buy Box % remain REVIEW_REQUIRED (not yet implemented), this risk is not yet live but must be re-checked if/when those fields are approved.

## Recommended safe sequence (unchanged in shape from the UK-only discovery, now explicitly keyed by account+marketplace)

1. Aggregate PPC spend by `account + marketplace + ASIN + period` (SB-excluded, `amzn.gr.*`-excluded).
2. Aggregate sales by `account + marketplace + ASIN + period` (`order_status='Completed'`).
3. Resolve ASIN→SKU via `listing_data`, scoped by `account + marketplace`.
4. Aggregate current stock by `resolved SKU + warehouse-mapped location` (warehouse, not marketplace, is the stock join key).
5. Join the four aggregated datasets once, on `(account, marketplace, ASIN)` for PPC/sales and `(resolved SKU, warehouse)` for stock.
6. Produce one row per `account + marketplace + ASIN + resolved SKU`.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED for the row-key and warehouse-double-count risks (both confirmed by direct evidence). **PARTIAL** for the PPC fan-out re-measurement at non-UK combinations — structurally reconfirmed, not empirically re-tested; flagged for the validation stage.

## Pass/fail rule

PASS if the row key, warehouse double-counting risk, and DCVoltage×France edge case are each backed by direct evidence, and any not-yet-empirically-retested risk is explicitly flagged rather than silently assumed safe. Met.

## Next action

During SQL validation (`06_VALIDATION/2026-07-17__sql_validation_report.md`), empirically re-run the aggregate-then-join fan-out test for at least one non-UK combination before treating the multi-marketplace SQL as fully proven.
