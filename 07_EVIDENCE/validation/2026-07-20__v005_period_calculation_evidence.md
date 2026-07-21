# v005 Period Calculation Evidence

**What this is:** Verification that v005's single embedded 30-day daily-grain dataset, plus JavaScript-computed period aggregation, is structurally correct and produces exact results — building on `06_VALIDATION/2026-07-20__v005_single_dataset_reconciliation.md`.

---

## Single dataset confirmed — no independent period datasets embedded

The embedded payload (verified by decompressing the actual file) contains exactly one structure: `{ DATES, ACCOUNTS, MARKETPLACES, TITLES, FEED_COVERAGE, PRODUCTS }`. `DATES` has exactly 30 entries (2026-06-20 to 2026-07-19). Each `PRODUCTS` entry carries 9 fixed 30-position daily arrays (Sessions, Page Views, Units Ordered, Clicks, Impressions, Spend, Attributed Sales, Buy Box numerator, Buy Box denominator) plus static snapshot fields — **no separate 7-day or 14-day array or object exists anywhere in the payload.**

## Daily array integrity

Sampled 1,000 of 53,843 products: **every one of the 9 daily-metric arrays has exactly 30 positions**, no exceptions.

## Period index derivation (dynamic, not hardcoded per the task's "or calculate indexes dynamically" option)

`periodRange(days)` computes `[DATES.length - days, DATES.length - 1]` at call time from the actual date array length — confirmed via execution: 7-day → `[23,29]`, 14-day → `[16,29]`, 30-day → `[0,29]`, matching the task's specified index ranges exactly without those numbers being hardcoded in the calculation function itself (only `DATES.length` is used).

## Summation rule (never averaging percentages)

`calcProduct()` sums each raw daily metric across the selected index range, then computes every ratio (Conversion Rate, CTR, ACOS, Buy Box %) **once**, from the summed totals — confirmed by direct code inspection: no daily percentage is ever read or averaged; only the raw base metrics (`sessionsArr[i]`, `unitsArr[i]`, etc.) are summed.

## Buy Box scale (confirmed correct, no double ×100)

The daily `buyBoxNum`/`buyBoxDenom` arrays already carry the pre-multiplied `dailyBuyBoxPct × dailySessions` numerator (matching v004's post-fix convention). `calcProduct()` computes `bbNum / bbDenom` with **no additional `× 100`** — confirmed live: all 3,625 numeric 30-day Buy Box values fall within `[0, 100]` (min=0, max=100), with no value found outside that range across the full dataset.

## Missing-data classification (never converted to a fabricated zero)

Re-implements the same 3-tier rule proven correct in v004:
1. If any day in the selected range has a non-null Sessions value → sum is a real, confident number (which may legitimately be `0`).
2. Else, if the account+marketplace's `FEED_COVERAGE` range doesn't overlap the selected period at all → `"N/A — source outside reporting date coverage"`.
3. Else, if the product's `everTracked` flag is `0` (never once appeared in the traffic feed's full history) → `"N/A — no matching traffic source row"`.
4. Else (feed covers the period, product is tracked, but literally zero matching days) → `0` (confirmed zero).

Verified live (30-day): REAL=243, TRUE_ZERO=3,382 (by this counting method — some rows classified "a real matching day was found" happen to have summed to 0, consistent with the same nuance already documented in v004's own evidence), OUTSIDE_COVERAGE=37,347, NO_MATCH=12,871 — identical distribution to v004's server-side classification.

## Conversion Rate / CTR / ACOS formula verification

All three recomputed from the reconciliation run and cross-checked field-by-field against v004's stored values — **0 mismatches across 53,843 products × 3 periods** (see the reconciliation document). Zero-denominator handling confirmed: Conversion Rate is `null` (displays as N/A) when Sessions is confirmedly `0` but Units Ordered is nonzero (the same real edge case documented in v004's formula trace evidence, correctly reproduced here).

## Category Average Price

Passed through unchanged from the pre-computed, outlier-corrected value already validated in v004 (no recalculation happens client-side — it is a static snapshot field per product, as specified: "Average valid product price within the same marketplace and approved product group," computed server-side once). Confirmed max value in the 30-day dataset: £609.06 — matches v004 exactly, confirming no corruption occurred in the compaction/embedding process.

## Status

**PASS.**
