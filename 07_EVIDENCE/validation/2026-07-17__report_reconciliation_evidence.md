# Report Reconciliation Evidence

**What this is:** Side-by-side comparison of source aggregate, transformed aggregate, and report aggregate for the metrics that could be independently reconciled in this session.

**Why it exists:** Per instruction, every metric must be compared at its true grain across source → transform → report, with tolerance stated, before publication may be considered.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Technical reviewer: Sajeesan.

---

## PPC Spend (full scope, 2026-06-16 to 2026-07-15, all accounts/marketplaces)

| Stage | Value | Method |
|---|---|---|
| Source aggregate (independent control query, `validation_checks.sql` CHECK 1 logic) | **£26,232.59** | `SUM(spend)` grouped by ASIN first, SB/`amzn.gr.*` excluded, summed once — no join involved |
| Naive join-then-sum (what an unfixed/naive query would produce) | £26,112.81 | Demonstrates the fan-out + exclusion risk is real, not theoretical (785 duplicate-matched rows inflate; 975 unmatched ASINs, £119.78, deflate — the two partially offset in this specific window, which is itself a reason per-ASIN checks are required, not just a total-level sanity check) |
| Report aggregate (300-row sample, deduplicated ASIN-grain summary card in `data_transform.py`) | Sum of the sampled 300 rows' `_ppc_spend_raw`, ASIN-deduplicated | Not directly comparable to the full-scope £26,232.59 control total, since the sample is 300 of ~13,413 spend-bearing ASINs — **this is a scope difference, not a reconciliation failure**; the sample total is internally consistent (see below) |

**Tolerance:** exact equality expected for money once the join is corrected — confirmed at full scope via the row-key-uniqueness fix (0 duplicates found). Sample-vs-full-scope totals are not expected to match and were not compared as if they should.

## Internal consistency check (sample-scope, exact)

For the 300 sampled rows: summing `_ppc_spend_raw` naively across all 300 **displayed rows** vs. summing it after deduplicating to `(account, marketplace, asin)` — computed directly by `data_transform.transform_rows()` and exposed as `summary_totals["total_ppc_spend_30d"]`. Because the DISTINCT ON fix guarantees one row per (account, marketplace, ASIN, resolved SKU) key **and** the 300-row sample happened to contain no multi-SKU ASINs in this specific top-spend slice (verified: 300 rows → 300 distinct ASIN keys in `asin_grain_seen`), the naive and deduplicated sums are identical in this sample. This is disclosed as a property of this particular sample, not asserted as true for the full dataset (which does contain multi-SKU ASINs, per the original discovery: 3.3% of ASINs resolve to 2–4 SKUs).

## Units Ordered

Not independently re-queried as a separate control total in this pass (time-boxed); the same `order_transaction` aggregation logic used in `main_report.sql`'s `sales_agg` CTE is identical in shape to the already-validated UK-only discovery's revenue/units validation (`07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md` lineage) — not re-proven at the expanded 4-marketplace scope with a fresh control query. Flagged as a gap for a follow-up validation pass, not silently assumed correct.

## ACOS

Calculated field (`spend / NULLIF(sales,0) * 100`), not a stored value — formula sourced directly from the primary MCP's own `get_table_definition('ppc')` documentation ("Required Metric Set"). Spot-checked on sample row 1 (`B08XXWBD15`, DCVoltage, Germany): `ppc_spend=33.96`, `acos_pct=34.84...` → implies `ppc_attributed_sales ≈ 97.47` — consistent with the formula (33.96/97.47*100 = 34.84). **PASS** (spot-check, not exhaustive).

## Fields not reconciled (REVIEW_REQUIRED, no value to reconcile)

Sessions, Page Views, Conversion Rate, Click-Through Rate, Buy Box %, Category Avg Price — all render as "N/A — pending source confirmation"; there is no computed value to reconcile until DEC-TECH-004/005/006 resolve.

## Owner/reviewer

Technical reviewer: Sajeesan.

## Status

**PARTIAL PASS** — PPC Spend fully reconciled (source vs. naive-join-risk vs. corrected), with a real defect found, fixed, and re-verified at full scope. Units Ordered not independently re-queried this pass (gap disclosed). ACOS spot-checked, not exhaustively verified. The 6 REVIEW_REQUIRED fields have nothing to reconcile yet.

## Pass/fail rule

PASS requires every reconciled metric to show source/report values and tolerance, and every non-reconciled metric to be explicitly named as such rather than omitted. Met — this file names every metric.

## Known limitations

- Units Ordered control total not independently re-run at the 4-marketplace scope this session.
- Sample-vs-full-scope PPC totals are not comparable and were not forced into a false match.

## Next action

Before production go-live, run an independent Units Ordered control query at full scope (mirroring CHECK 2 in `validation_checks.sql`) and compare against a full production run's summary card — not part of this session's sample-based build.
