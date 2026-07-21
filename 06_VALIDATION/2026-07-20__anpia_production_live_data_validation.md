# Validation: Production ANPIA v001 -- Fresh Live Data

**Report:** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html`
**Requirement:** REQ-01-D02 -- ANPIA

## 1. Fresh extraction (not reused from v005/v006/v007)

The v005-v007 development iterations all reused the same single dataset extraction performed once
at v005 time (confirmed: v007's generator script extracts the Base64 payload directly out of
v006's HTML rather than re-querying the database -- see
`09_OUTPUTS/html/test_versions/README.md`). This production build re-ran the **entire** pipeline
against the live database:

1. `latest_complete_date()` queried live -> **2026-07-19** (unchanged from the earlier session, since
   the source's `CURRENT_DATE` is still 2026-07-20 -- same calendar day, but source table contents
   can and do change intraday).
2. Master aggregation extraction (`anpia_common_dataset.extract_common_dataset`) re-run fresh:
   window **2026-06-20 to 2026-07-19** (30 days), output
   `09_OUTPUTS/data/2026-07-20__anpia_production_v001_common_daily_facts.jsonl`.
   - Row count: **268,404**
   - Duplicate `(date, sub_source, market_place, asin, resolved_sku)` keys: **0**
   - Null-key rows: **0**
   - Elapsed: 42.0 seconds
3. Enrichment queries (`anpia_snapshot_enrichment`) re-run fresh: dimension bridge, category average
   price (Tukey-IQR trimmed), current stock, last-sale date, traffic feed coverage, ever-tracked
   ASINs -- all live, all read-only.
4. Compact dataset rebuilt fresh:
   `09_OUTPUTS/data/2026-07-20__anpia_production_v001_compact_dataset.json`
   - Identity count (unique Account+Marketplace+ASIN+SKU rows): **53,843**
   - Duplicate identity count: **0**
   - Title count: 47,364
   - Raw JSON size: 67,463,812 bytes

## 2. Compression and embedding

- gzip level 9: 2,917,789 bytes (4.3% of raw)
- Base64: 3,890,388 characters
- Embedded into the approved v007 template (unchanged UX/CSS/JS -- only the report title,
  generation timestamp, and data payload placeholders were substituted)
- Final production HTML: **3,922,120 bytes**, SHA-256
  `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`, UTF-8 valid.

## 3. Traffic feed coverage -- freshly observed (differs from the earlier session's diagnosis)

| Account | Marketplace | Coverage within this 30-day window (day index) | Calendar dates |
|---|---|---|---|
| DCVoltage | France, Germany, Italy, UK | None (no overlap) | Feed stopped before 2026-06-20 for all marketplaces |
| LEDSONE | France | [0, 23] | 2026-06-20 to 2026-07-13 |
| LEDSONE | Germany | [0, 28] | 2026-06-20 to 2026-07-18 |
| LEDSONE | Italy | [0, 2] | 2026-06-20 to 2026-06-22 |
| LEDSONE | UK | None (no overlap) | Feed's last date is before 2026-06-20 |

This is a genuinely fresh observation, not copied from the earlier session's diagnosis. Notably,
**LEDSONE France now shows staleness** (last coverage 2026-07-13, 6 days before the latest complete
date) where an earlier session note described it as "current" -- consistent with real time having
progressed and that account's feed continuing to lag since the earlier check. This is disclosed
rather than smoothed over; it directly affects which cells render as `TRUE_ZERO` vs.
`OUTSIDE_COVERAGE` for LEDSONE France rows in the most recent days of the 30-day window.

## 4. Approved formulas and rules preserved unchanged

All source mappings and formulas validated in the earlier v003-v007 development cycle were reused
without modification for this production build:
- Traffic deduplication: `MAX()` per `(date, account, marketplace, asin)` before cross-day summation
  (prevents the confirmed same-ASIN-repeated-across-SKU-variant double count).
- Buy Box: stored 0-100 scale, no extra `x100` applied.
- Conversion Rate: `units / sessions * 100`, with `0` only when sessions is a confirmed real zero and
  units is also zero, `null` (N/A) when sessions is zero but units is nonzero (data-quality flag, not
  a computable rate).
- CTR: `clicks / impressions * 100`, null when impressions = 0.
- ACOS: `spend / attributedSales * 100`, null when attributedSales = 0.
- Current stock: UK marketplace -> UK warehouse; Germany/France/Italy -> shared German warehouse.
- Category Average Price: Tukey IQR-fenced trim (categories with >=5 priced listings), plain average
  otherwise.
- Days Since Last Sale: `latest_complete_date - MAX(order_date)` per Account+Marketplace+ASIN.
- Missing-data 4-tier classification (REAL / TRUE_ZERO / OUTSIDE_COVERAGE / NO_MATCH) preserved;
  missing values are never silently converted to zero.

## 5. Conclusion

The production report was built from a genuinely fresh, independent live-database extraction and
enrichment pass -- not a copy or rename of any prior development file. Full calculation reconciliation
evidence is in `07_EVIDENCE/validation/2026-07-20__anpia_production_calculation_reconciliation.md`.
