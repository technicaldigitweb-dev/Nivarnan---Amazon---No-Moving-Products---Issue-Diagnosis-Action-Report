# v005 Single-Dataset Reconciliation

**What this is:** Exhaustive row-level reconciliation of v005's client-side (JavaScript) period calculations against v004's server-side (Python) period calculations, using v004 as the approved comparison output.

**Method:** v005's actual embedded compressed dataset was decompressed via the real browser-compatible `DecompressionStream('gzip')` API (executed in Node.js, which implements the same Web Streams API), and the exact same JavaScript calculation function embedded in the v005 HTML file was re-executed against it. Results were compared field-by-field against v004's actual generated period JSONL output files — **every product, every period, not a sample.**

---

## Result

| Period | Products checked | Mismatches | Missing in v005 |
|---|---|---|---|
| 7-day | 53,843 | **0** | 0 |
| 14-day | 53,843 | **0** | 0 |
| 30-day | 53,843 | **0** | 0 |

**53,843 products × 3 periods × 11 compared fields (Sessions, Units Ordered, Conversion Rate, Buy Box %, PPC Spend, CTR, ACOS, Units in Stock, Price, Category Avg Price, Days Since Last Sale) = 1,776,819 individual value comparisons. Zero mismatches.**

## Tolerances applied

- Counts (Sessions, Units Ordered, Units in Stock, Days Since Last Sale): exact match required.
- Currency (PPC Spend, Price, Category Avg Price): £0.01 tolerance.
- Percentages (Conversion Rate, CTR, ACOS, Buy Box %): 0.01 percentage point tolerance.
- `null` vs `null` (both sources agreeing a value is unavailable) and matching N/A reason strings: treated as an exact match, not a mismatch.

## No omitted products, no duplicates

Distinct identity count in v005's embedded dataset: **53,843** — matches v004's product universe exactly. Duplicate `(account, marketplace, ASIN, SKU)` identity check on the embedded data: **0 duplicates** (verified via `Set` cardinality check against the raw `PRODUCTS` array).

## Period date ranges (self-derived from the 30-date array, confirmed correct)

| Period | Index range | Dates |
|---|---|---|
| 7-day | [23, 29] | 2026-07-13 to 2026-07-19 |
| 14-day | [16, 29] | 2026-07-06 to 2026-07-19 |
| 30-day | [0, 29] | 2026-06-20 to 2026-07-19 |

Matches v004's periods exactly.

## Aggregate dedup totals (independent cross-check, matches v004's own reconciliation)

| Period | PPC Spend (dedup) | Units Ordered (dedup) |
|---|---|---|
| 7-day | £4,284.48 | 1,802 |
| 14-day | £8,801.49 | 3,905 |
| 30-day | £19,985.29 | 9,003 |

Identical to the figures independently reconciled in v004's own validation (`07_EVIDENCE/validation/2026-07-20__common_dataset_reconciliation_evidence.md`).

## Why this reconciliation is expected to be exact, not merely close

v005's JavaScript `calcProduct()` function is a direct, deliberate re-implementation of the exact same logic already proven correct in v004's Python `derive_ratios()`/`classify_traffic_value()` functions (same source-classification rules: REAL / TRUE_ZERO / OUTSIDE_COVERAGE / NO_MATCH, same Buy Box weighted-average formula post-fix, same zero-denominator handling) — both draw from the identical underlying 30-day common daily dataset (`09_OUTPUTS/data/2026-07-20__anpia_common_daily_facts.jsonl`, 268,404 rows, unchanged from v004). The reconciliation confirms the JavaScript port introduced no discrepancy, not that two independently-designed methods happened to agree.

## Status

**PASS.**
