# Common Dataset Validation Report — ANPIA Rebuild (REQ-01-D02)

**What this is:** Consolidated validation of the common daily dataset and its three derived period views, built via direct PostgreSQL access on 2026-07-20.

**Sources used:** direct connection (`anpia_db_connection`, `PRIMARY = ANPIA_DB_*` credentials), database `order_management_copy`, tables `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data`, `public.location_wise_inv_stock`, `public.amz_traffic_by_asin`.

---

## Daily key uniqueness

**PASS.** 268,404 rows in the common daily dataset, 0 duplicate `(report_date, account, marketplace, asin, resolved_sku)` keys, 0 null key components — verified during extraction (`anpia_common_dataset.extract_common_dataset`, in-line duplicate/null tracking) and independently consistent with the aggregate-before-join SQL design (each source aggregated to this exact grain before any join).

## Source date coverage

**PASS.** Window 2026-06-20 to 2026-07-19 (30 complete days), determined from `order_transaction`'s own `CURRENT_DATE - 1` (excludes the still-accruing current day, per instruction).

## Both accounts / all marketplaces present

**PASS.** LEDSONE and DCVoltage both present in all three period views; UK, Germany, Italy present for both accounts; France present for LEDSONE only — DCVoltage×France confirmed genuinely absent (0 bridge rows, 0 activity), not a mapping defect, consistent with the 2026-07-17 finding, re-confirmed fresh.

## No raw-table join fan-out

**PASS by construction.** Every source (`ppc_daily`, `sales_daily`, `traffic_daily`) is a `GROUP BY`-aggregated CTE before any join; the bridge dimension uses the same `DISTINCT ON` tiebreaker validated on 2026-07-17 (prefers non-offer rows, non-null price, lowest id). No two raw fact tables are ever joined directly to each other.

## Completeness (no cutoff) — real defect found and fixed

**Initially FAILED, then fixed and re-verified PASS.** See `07_EVIDENCE/database/2026-07-20__common_daily_dataset_extraction_evidence.md` for the full account — the first period-builder version silently excluded zero-activity ASIN/SKUs (11,425–14,085 rows instead of the full 53,843-row bridge universe). Fixed by enumerating the full dimension for every period. Re-verified: all three periods now correctly return 53,843 rows each.

## Reconciliation (all three periods)

**PASS.** See `07_EVIDENCE/validation/2026-07-20__common_dataset_reconciliation_evidence.md` for full detail — an initial raw-sum discrepancy was investigated (not accepted at face value), traced to the known multi-SKU-ASIN repeat effect plus the known unmapped-ASIN exclusion effect, and closed to an exact match (£104.43 / 58 units residual on the 30-day period matched the independently-measured unmapped-ASIN total to the penny).

## No previous unusable dataset reused

**PASS.** Confirmed — see extraction evidence file's explicit "Previous extracted data" section.

## Current-snapshot fields excluded from additive daily totals

**PASS by construction.** `units_in_stock`, `price`, `category_avg_price`, `product_title` are joined once per final report row (post-period-aggregation), never present in the daily-grain common dataset's additive fields at all (the common dataset only carries `ppc_*`, `units_ordered`, `ordered_sales_revenue`, `sessions`, `page_views`, `bb_weighted_num`/`bb_weight_denom`).

## Credentials absent

**PASS.** Confirmed via repository-wide scan (see credential-access evidence file) — zero matches outside `.env` and the three known, separately-documented reference files.

## Field classification (re-validated live, per REQ-01-D02 §10)

See `03_DISCOVERY/2026-07-20__required_field_grain_classification.md` (updated this session) — all 17 fields re-confirmed against live schema. Two material updates from the 2026-07-17 classification:
- **Category Avg Price** now has a confirmed approved source: `listing_data.product_type` is 100% populated for both accounts (150 distinct categories) — averaging population defaulted to `(marketplace, product_type)`, disclosed as a reasonable default pending explicit business sign-off, not silently invented.
- **DCVoltage traffic-data freshness** root-caused: `amz_traffic_by_asin` genuinely stopped updating for DCVoltage on 2026-04-22 (a real upstream feed disconnection — gradual-then-hard-stop row-count pattern, thousands of rows/month before the cutoff, zero after) while `order_transaction`/`ppc_performance` remain current to 2026-07-19 — confirmed NOT a wrong-account-identifier or wrong-marketplace-mapping issue (no alternate `sub_source_id` exists for DCVoltage in that table).

## Status

**PASS**, with one real defect found and fixed during this session (completeness/no-cutoff violation), documented transparently rather than hidden.

## Pass/fail rule

PASS if daily keys are unique, dates cover the resolved window exactly, both accounts and all available marketplaces appear, no fan-out exists, completeness holds (no cutoff), all periods reconcile within tolerance, no previous dataset was reused, and no credentials are exposed. Met.

## One next step

Route the Category Avg Price averaging-population default (`marketplace + product_type`) to the business owner (Nivarnan) for explicit confirmation, and the excess `tech_team_outputs` privilege scope to Sajeesan — neither blocks this validation's PASS status.
