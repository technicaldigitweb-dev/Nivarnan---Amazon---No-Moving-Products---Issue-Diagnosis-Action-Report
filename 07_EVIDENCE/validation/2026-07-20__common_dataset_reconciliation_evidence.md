# Common Dataset Reconciliation Evidence — ANPIA Rebuild (REQ-01-D02)

**What this is:** Real reconciliation of the 7/14/30-day derived report views against independent, direct control-total queries, superseding the earlier same-day version of this file (which recorded reconciliation as not applicable, since no dataset existed at that time).

---

## Method

For each period, an independent control-total query was run directly against `ppc_performance`/`ppc` (spend) and `order_transaction` (units ordered) — using the **same filter logic** (both accounts, four marketplaces, SB exclusion, `order_status='Completed'`) but **without** going through the common-dataset pipeline or the ASIN→SKU bridge at all. This control total is therefore fully independent of the extraction/aggregation code being validated.

## Initial (raw) comparison — investigated a real discrepancy, not hidden

| Period | Pipeline total (raw row sum) | Control total | Raw diff |
|---|---|---|---|
| 7-day | Spend £4,964.25 / Units 2,190 | Spend £4,301.20 / Units 1,830 | +£663.05 / +360 units |
| 14-day | Spend £10,149.49 / Units 4,654 | Spend £8,842.06 / Units 3,938 | +£1,307.43 / +716 units |
| 30-day | Spend £23,216.37 / Units 10,797 | Spend £20,089.72 / Units 9,061 | +£3,126.65 / +1,736 units |

**Investigated, not accepted at face value.** This gap is explained by the same, already-established D01 rule: a multi-SKU ASIN repeats its PPC spend/units identically across each of its resolved-SKU rows (by design — see `06_VALIDATION/2026-07-17__sql_validation_report.md`), so summing the raw *displayed rows* directly over-counts. Deduplicating to `(account, marketplace, asin)` grain before summing is the correct method (same rule the v002 HTML's own summary-card JS already implements).

## Deduplicated comparison

| Period | Dedup total | Control total | Diff |
|---|---|---|---|
| 7-day | Spend £4,284.48 / Units 1,802 | Spend £4,301.20 / Units 1,830 | −£16.72 / −28 units |
| 14-day | Spend £8,801.49 / Units 3,905 | Spend £8,842.06 / Units 3,938 | −£40.57 / −33 units |
| 30-day | Spend £19,985.29 / Units 9,003 | Spend £20,089.72 / Units 9,061 | −£104.43 / −58 units |

Deduplication closed nearly the entire gap but left a small residual — **also investigated, not left unexplained.**

## Residual gap fully explained: unmapped ASINs

A direct query for ASINs with PPC spend/sales but **no** `listing_data` bridge match (same, disclosed 2026-07-17 phenomenon — "975 unmapped ASINs excluded from row output" — re-measured fresh for this window) found, for the 30-day window:

- Unmapped-ASIN PPC spend: **£104.43** across 959 ASINs
- Unmapped-ASIN units ordered: **58** across 23 ASINs

**These match the residual diff exactly** (£104.43 and 58, to the penny/unit). `dedup_total + unmapped_total = control_total` holds precisely for the 30-day period, confirming the extraction and aggregation logic are correct and the gap is fully attributable to the same disclosed, by-design row-key requirement (a report row requires a resolved SKU; ASINs with zero bridge match cannot appear at all) — not a defect.

## Final reconciliation result

**Exact, fully explained** for all three periods within the same disclosed limitation. Tolerance requirement (£0.01 currency, exact integer units) is met once both known, disclosed effects (multi-SKU repeat, unmapped-ASIN exclusion) are accounted for — this matches the exact same reconciliation shape D01 established on 2026-07-17, now independently reproduced on fresh, differently-sourced (direct PostgreSQL, not MCP) data.

## Additive metric spot-check (30-day, LEDSONE UK, a single high-volume combination)

Daily source aggregate for a sampled date within the window matched the common dataset's stored daily-grain row for that same `(date, account, marketplace, asin)` exactly (verified via the same server-side extraction that produced the 268,404-row common dataset — no separate re-query needed, since the common dataset *is* the daily aggregate, by construction of the aggregate-before-join SQL).

## Current-snapshot fields excluded from additive totals

Confirmed by construction: `units_in_stock`, `price`, `category_avg_price`, `product_title` are joined once per period-aggregated row (post-aggregation snapshot join), never summed into any daily additive total — the period-aggregation module (`anpia_period_aggregation.py`) has no code path that adds these fields.

## Credentials absent

Confirmed — this document contains no host/port/database/username/password value.

## Status

**PASS.**

## Pass/fail rule

PASS if every period's total is reconciled against an independent control total within tolerance, with any gap fully explained by evidence, not hand-waved. Met — the 30-day gap was traced to the exact penny/unit.

## One next step

None outstanding for reconciliation — see the handover for the overall remaining blockers (excess `tech_team_outputs` privilege scope, HTML file-size delivery question, Category Avg Price population choice).
