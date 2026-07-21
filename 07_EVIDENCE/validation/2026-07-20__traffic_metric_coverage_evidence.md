# Traffic Metric Coverage Evidence — v004

**What this is:** Evidence backing `03_DISCOVERY/2026-07-20__traffic_metrics_coverage_diagnosis.md`'s coverage matrix, with before/after comparison.

---

## Sessions coverage — before (v003) vs after (v004)

**Before (v003):** every row not falling into the small "REAL activity found" bucket showed the single generic string `N/A - source not available` — no distinction between "this account/marketplace's feed doesn't reach this period" and "this specific product was never tracked."

**After (v004), 30-day period (53,843 total rows):**

| Classification | Row count | % of total |
|---|---|---|
| REAL (actual recorded value) | 281 | 0.52% |
| TRUE_ZERO (confirmed tracked, zero this period) | 3,344 | 6.21% |
| OUTSIDE_COVERAGE (feed doesn't reach this period) | 37,347 | 69.36% |
| NO_MATCH (feed covers period, ASIN never tracked) | 12,871 | 23.90% |

**"Coverage" (REAL + TRUE_ZERO, i.e., a confident value either way) rose from effectively unexplained N/A for ~99.5% of rows to a precisely reasoned classification for 100% of rows** — the underlying sparsity (only 6.7% of rows have a confident numeric value) is disclosed as a real data-availability fact, not hidden by relabeling.

## Page Views coverage

Identical classification counts to Sessions (both fields share the same `has_traffic_data`/classification logic, since both come from the same source row) — verified via the same live extraction; not independently re-derived, since Page Views and Sessions are always populated or absent together in `amz_traffic_by_asin`.

## Buy Box coverage

Same classification counts as Sessions (Buy Box requires a Sessions-weighted denominator, so its availability is a strict subset of Sessions' availability by construction) — 3,625 rows (30-day) have a real numeric Buy Box value after the scale-bug fix (see formula trace evidence), all within the valid 0–100 range.

## Account/marketplace mapping verification

Live comparison of `sub_source_id`/`market_place_name` values in `amz_traffic_by_asin` against the same identifiers used in `listing_data`/`ppc_performance`/`order_transaction`:

| ANPIA label | Source identity | Matched? |
|---|---|---|
| LEDSONE | `sub_source_id=8`, `sub_source_name='amazon Ledsone'` | YES — identical across all 4 source tables |
| DCVoltage | `sub_source_id=6`, `sub_source_name='amazon Dcvoltage'` | YES — identical across all 4 source tables |
| UK / Germany / France / Italy | `market_place_name` plain text, same spelling across all 4 source tables | YES |

**No account or marketplace mapping correction was required** — the coverage gap is entirely a date-range and per-ASIN-tracking phenomenon, not a mapping defect.

## ASIN/SKU join grain verification

Confirmed **date + account + marketplace + ASIN + SKU** is the true source grain (SKU-variant rows exist and repeat the ASIN-level value identically — see the formula trace and coverage diagnosis documents for the 1,183/1,191-group evidence). Aggregation is correctly done **once per ASIN per day** (via `MAX()`) before summing across days, and the resulting single-per-ASIN daily value is then repeated (not re-summed) across that ASIN's multiple SKU rows in the final report — matching the required "traffic values may appear on each ASIN/SKU row for comparison; aggregate cards and reconciliations must deduplicate by account + marketplace + ASIN" rule.

## Status

**PASS.** Coverage is now honestly measured and disclosed per period/account/marketplace, not hidden behind a generic label. Low coverage where the feed is genuinely stale (DCVoltage entirely, LEDSONE UK/Italy for the current window) is real and disclosed, not fabricated as zero activity.
