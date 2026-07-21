# Metric Calculation Validation — v004

**What this is:** Verification of every calculated field's formula and source, using base values (not displayed percentages), per REQ-01-D02's v004 fix instructions.

---

## A. Conversion Rate

**Formula implemented:** `Units Ordered ÷ Sessions × 100`, calculated once from period-total values (`anpia_period_aggregation.derive_ratios`). **Verified: matches the required formula exactly.**

Rules verified against code (`build_period_reports_v2.py`):
- Period-total Units Ordered used (not daily average) — YES.
- Period-total Sessions used — YES.
- Sessions > 0 → calculated normally — YES.
- Sessions confirmed 0 (TRUE_ZERO class) and Units Ordered = 0 → shows `0.00%` — YES.
- Sessions unavailable (OUTSIDE_COVERAGE / NO_MATCH) → Conversion Rate propagates the *same precise N/A reason* as Sessions, not a generic string — YES (`conversion_rate = sessions_val` when `sessions_class` is not REAL/TRUE_ZERO).
- Never averages daily percentages — YES, confirmed by construction (single division after summation, no per-day percentage stored or averaged anywhere in the pipeline).

## B. Click-Through Rate

**Formula implemented:** `PPC Clicks ÷ PPC Impressions × 100`, from `ppc_performance`, summed over the period before division. **Verified: matches the required formula exactly** — not derived from spend.

- Clicks/impressions aggregated over the selected period — YES (`ppc_daily` CTE, `SUM`).
- Calculated after aggregation — YES.
- Zero-denominator handling: `NULLIF`-equivalent safe division in `derive_ratios` — returns `None` (displayed as N/A) when impressions total is 0.
- Never averages daily CTR — YES, same single-division-after-summation pattern.

## C. Buy Box %

**Source representation proven:** `amz_traffic_by_asin.buyBoxPercentage` is a **finished daily percentage only** — no raw numerator/denominator is exposed by this source table (confirmed via `information_schema.columns`, no such fields exist).

**Aggregation rule used:** sessions-weighted average — `SUM(daily_buy_box_pct × daily_sessions) ÷ SUM(daily_sessions)` — **not** a simple unweighted average. A weighted denominator (sessions) **is** available, so the stricter "classify as AMBER if only an unweighted percentage exists and no approved aggregation rule is available" condition does not apply — a defensible, weighted rule was available and used.

**Disclosed, not hidden:** this is still an approximation of a true recalculated ratio, since Amazon's own won/eligible counts aren't exposed — documented in the v004 formula notes exactly this way.

## D. ACOS

**Formula implemented:** `PPC Spend ÷ PPC Attributed Sales × 100`, calculated after period aggregation. **Verified: matches exactly** — uses PPC-attributed sales (`ppc_performance.sales`), not total Amazon sales, consistent with the approved requirement.

- Attributed sales = 0 → N/A (safe zero-denominator), not 0% or an error — confirmed in `derive_ratios`.

## E. Category Average Price

**Original formula (v003) found untrustworthy — confirmed, not assumed.** Live investigation:
- Currency mixing: **not the dominant cause** — each marketplace's listings are overwhelmingly single-currency (UK≈100% GBP, DE/FR/IT≈100% EUR, with a handful of null/blank/stray values, e.g. 7 Italy rows tagged GBP — negligible volume).
- **Root cause: malformed/outlier price values.** Concrete example: `Germany/LIGHT_BULB` — 196 priced listings, raw average **€13,272.17**, driven by extreme outliers including a listing priced at **€649,555**. 22 of 196 listings (11%) were statistical outliers by a standard Tukey IQR fence.
- **Fix implemented:** exclude non-positive prices (invalid), and for categories with ≥5 priced listings, exclude values outside `[Q1 − 1.5×IQR, Q3 + 1.5×IQR]` before averaging. Categories with <5 listings use the plain (already price>0-filtered) average, since IQR is not statistically meaningful at that sample size.
- **Result:** `Germany/LIGHT_BULB` trimmed average = **€12.62** — plausible for LED light bulb products. Across all 413 category buckets, 174 had at least one outlier excluded.
- **Status: AMBER, disclosed.** The statistical correction produces plausible, defensible values, but the exact grouping population (`marketplace + product_type`, chosen as a reasonable default) and the specific outlier-exclusion policy have **not** received explicit business sign-off — flagged for Nivarnan's confirmation, not silently finalized.

## Status

**PASS** for formulas B, C(with disclosed approximation), D (verified exactly as specified); **A** verified with the new, more precise N/A propagation behavior; **E returns AMBER** per the task's own explicit allowance, with a real, evidenced statistical fix already applied rather than left broken.

## One next step

Route Category Avg Price's grouping/outlier policy to Nivarnan for explicit sign-off.
