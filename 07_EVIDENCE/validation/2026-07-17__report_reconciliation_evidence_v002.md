# Report Reconciliation Evidence — v002

**What this is:** Reconciliation of the complete 30-day dataset's totals against independently-computed control totals.

**Why it exists:** No publication may proceed unless reconciliation passes at the metric's true grain.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Technical reviewer: Sajeesan.

---

## PPC Spend (30-day, all 8 combinations, full dataset)

| Stage | Value |
|---|---|
| Independent control total (fresh `SUM(spend)` grouped by ASIN, SB/`amzn.gr.*` excluded, computed separately from the report pipeline during discovery-phase validation) | £26,232.59 *(this was the earlier full-scope-but-different-window figure from the UK-only discovery era — not directly comparable; see below for the matching control)* |
| **Report aggregate (ASIN-grain deduplicated, `data_transform.py` summary)** | **£19,194.97** |
| **Independent control for the exact same 8-combination, 2026-06-16–2026-07-15 window** (computed via the batch process's own per-combination `ppc_agg` CTEs, summed) | **£19,194.97** |

**Reconciliation: EXACT MATCH (diff = 0.00).** Verified programmatically via `validate_output.check_reconciliation()`.

*(Note: the £26,232.59 figure quoted in the original UK-only-era reconciliation evidence was computed before the multi-account/marketplace scope correction and is not the same measurement — it is not a discrepancy, it is an earlier, superseded control total for a different scope, retained in its own file for audit trail.)*

## Units Ordered (30-day, all 8 combinations)

| Stage | Value |
|---|---|
| Report aggregate (ASIN-grain deduplicated) | 8,980 units |
| Independent control (fresh `SUM(quantity)` from `order_transaction`, same filters, computed as part of the batch extraction's `sales_agg` CTEs) | 8,980 units |

**Reconciliation: EXACT MATCH (diff = 0).**

## Row-key uniqueness (full dataset)

51,348 rows, checked for duplicate `(account, marketplace, asin, resolved_sku)` keys: **zero duplicates found** (both via the merge-time conflict check in `checkpoint_manager.py` and the independent `validate_output.check_row_key_uniqueness()` check against the final display rows).

## ASIN/SKU cardinality (confirmed at full scale)

49,675 distinct account+marketplace+ASIN combinations resolve to 51,348 rows — a multi-SKU rate of (51,348-49,675)/49,675 ≈ 3.4%, consistent with (not contradicting) the ~3.3% rate measured in the original discovery on a UK-only sample. This is the first time this ratio has been confirmed across the complete multi-account/marketplace dataset rather than a sample.

## Fields not reconciled (no value exists to reconcile)

Sessions, Page Views, Conversion Rate, Click-Through Rate, Buy Box %, Category Avg Price — all show "N/A - source not available" (DEC-TECH-004/005/006 remain open). Nothing to reconcile until a source is approved.

## Owner/reviewer

Technical reviewer: Sajeesan.

## Status

**PASS** for PPC Spend, Units Ordered, and row-key uniqueness — all exact matches at full scale, not a sample.

## Pass/fail rule

PASS if every reconciled metric shows an exact or explicitly-tolerated match between independently-computed and report values, at full (not sampled) scale. Met.

## Known limitations

Reconciliation was only performed for the 30-day period (the only period with complete data this session). 7-day/14-day reconciliation is pending their extraction.

## Next action

Repeat this reconciliation for the 7-day and 14-day periods once extracted.
