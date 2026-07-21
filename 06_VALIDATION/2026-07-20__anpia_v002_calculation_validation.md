# Validation: ANPIA Production v002 -- Calculation Reconciliation

**Report:** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`

## 1. Fresh extraction summary

- `latest_complete_date()` queried live -> 2026-07-19 (unchanged calendar day from v001; source data
  itself was re-pulled fresh, not reused).
- Window: 2026-06-20 to 2026-07-19 (30 days).
- Extraction: 268,404 rows, 0 duplicate keys, 0 null-key rows, 19.0 seconds
  (`09_OUTPUTS/data/2026-07-20__anpia_production_v002_common_daily_facts.jsonl`).
- Identity count: **53,843**, duplicate identity count: **0**
  (`09_OUTPUTS/data/2026-07-20__anpia_production_v002_compact_dataset.json`).
- Compact dataset: 67,463,812 bytes raw -> 2,917,789 bytes gzip -> 3,890,388 base64 characters.
- Final HTML: 3,923,170 bytes, SHA-256 `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`.

## 2. Method

Same two-implementation cross-check methodology used for v001: the report's own embedded
`calcProduct()` (run headlessly via Node's native `DecompressionStream`) compared against an
independent Python recomputation driven by a fresh live query of `load_traffic_feed_coverage()` /
`load_ever_tracked_asins()` plus a direct scan of the v002 raw extraction JSONL.

## 3. Sample and fields

6 LEDSONE/France products with real activity in the recent window (same selection heuristic as the
v001 reconciliation, re-run fresh against v002's data -- not the same underlying values, since the
extraction was independently re-pulled). Fields compared: `units`, `spend`, `sessions`, `pageViews`,
`conversionRate`, `buyBox`, across 7/14/30-day windows -> **108 total field comparisons**.

## 4. Result

**0 mismatches out of 108 comparisons.** Edge cases (confirmed-zero sessions with nonzero units
correctly producing `conversionRate = null`, not `0`) reproduced correctly, matching the same
data-quality-signal behavior validated in the v001 reconciliation.

## 5. Structural checks

- `PRODUCTS.length` = 53,843 (matches identity count; 0 client-side duplicate keys, independently
  re-checked against the v002 payload).
- `DATES` = 30 entries, 2026-06-20 to 2026-07-19.
- No credential-like strings found in the decompressed dataset text.
- Approved calculation rules (traffic dedup via `MAX()`, Buy Box 0-100 scale, Tukey-IQR Category Avg
  Price, 4-tier missing-data classification, warehouse mapping) are all unchanged from v001 --
  reused without modification, since this task did not request any formula change, only a fresh data
  pull and a UI fix.

## 6. Conclusion

Calculation reconciliation for v002 passes with zero discrepancies against fresh live data,
consistent with the v001 result and confirming the calculation logic itself was not altered by the
UI/template change (only presentation CSS changed between v007/v001's template and v008/v002's).
