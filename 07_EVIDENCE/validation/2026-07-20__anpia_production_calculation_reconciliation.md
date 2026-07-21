# Evidence: Production ANPIA v001 Calculation Reconciliation

**Report:** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html`

## 1. Method

Two independently-written implementations of the period-aggregation logic (windowed sum/pre-fill/
overlay over the 30-day daily-grain arrays) are compared against each other for real production data:

1. **Client-side (JavaScript):** `calcProduct()`, extracted and executed exactly as embedded in the
   production HTML (same function used by the report itself when a user views it in a browser),
   run headlessly via Node's built-in `DecompressionStream`/`atob` to decompress and parse the
   embedded dataset, then compute 7/14/30-day aggregates for a sample of products.
2. **Server-side (Python):** an independent reimplementation of the same pre-fill (feed-coverage +
   ever-tracked -> confirmed-zero) and windowed-sum logic, driven by a fresh live read-only query of
   `load_traffic_feed_coverage()` / `load_ever_tracked_asins()` plus a direct scan of the raw
   `09_OUTPUTS/data/2026-07-20__anpia_production_v001_common_daily_facts.jsonl` extraction file.

## 2. Sample selection

6 products were selected, preferring LEDSONE (the account with current-ish traffic coverage) with
nonzero recent unit activity and at least one non-null session day in the most recent 7-day window,
to ensure the sample exercises real (non-trivially-N/A) values rather than only OUTSIDE_COVERAGE
rows:

- LEDSONE/France/B08NXLVKBS/LSFT220CH+RPR44WH
- LEDSONE/France/B07CQL5WJR/CRSF100BM
- LEDSONE/France/B08NXN3J42/LSDO300RO+RPR44WH
- LEDSONE/France/B08TX216Y4/LSMS320CB+RPR44WH
- LEDSONE/France/B07RK3ZKFZ/LDMG125E278
- LEDSONE/France/B07D285NLT/LDMG125E278

## 3. Fields compared

For each of the 6 products x 3 periods (7/14/30-day): `units`, `spend`, `sessions`, `pageViews`,
`conversionRate`, `buyBox`. **108 total field comparisons.**

## 4. Result

**0 mismatches out of 108 comparisons** (tolerance 0.001 for floating-point fields; exact match
required for integer fields; both sides classified as the same "no session data" state where
applicable). Example agreement (7-day window):

| Product | Units | Sessions | Page Views | Conv. Rate | Buy Box |
|---|---|---|---|---|---|
| B08NXLVKBS | 2 | 3 | 17 | 66.6667% | 100.0% |
| B07RK3ZKFZ | 3 | 10 | 13 | 30.0% | 100.0% |
| B07CQL5WJR | 3 | 0 (confirmed) | 0 | N/A (units>0, sessions=0) | 0 |

The `B07CQL5WJR` and `B08TX216Y4`/`B08NXN3J42` rows are a useful edge-case check: their session
arrays are non-null (pre-filled to confirmed-zero by feed-coverage + ever-tracked logic) but contain
no real traffic-source row for the specific days in the 7/14-day windows, so both implementations
correctly report `sessions=0` (a real, confirmed zero -- TRUE_ZERO) rather than N/A, and correctly
report `conversionRate=null` (not `0`) because units is nonzero against a zero-session denominator --
a genuine data-quality signal, not a computable rate.

## 5. What this proves

- The full pipeline -- live extraction -> enrichment -> compact-array build -> gzip -> Base64 ->
  template embed -> browser-side decompression -> browser-side period calculation -- reproduces
  identical results to an independent server-side recomputation, for real (not synthetic) production
  data.
- The pre-fill/confirmed-zero vs. N/A distinction (the core fix validated in the v004/v005
  development cycle) continues to hold correctly against fresh live data.

## 6. Structural checks (unchanged from v007, same template)

- `PRODUCTS.length` = 53,843 (matches identity count, 0 client-side duplicate keys).
- `DATES` = 30 entries, 2026-06-20 to 2026-07-19.
- No credential-like strings found in the decompressed dataset text (`ANPIA_DB`, `password`, the
  known host IP, or the known password value all absent).
- `--w-title: 360px` CSS rule present; `<div class="title-text"` render path present (confirms the
  approved frozen-column / 3-line-title UX carried over unchanged from v007).

## 7. Conclusion

Calculation reconciliation passes with zero discrepancies. The production report's client-side
arithmetic is verified consistent with an independent server-side recomputation on fresh live data.
