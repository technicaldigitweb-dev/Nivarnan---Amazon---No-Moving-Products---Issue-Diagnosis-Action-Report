# Traffic Metrics Coverage Diagnosis — ANPIA v004 Fix

**What this is:** Root-cause diagnosis of the v003 defect where Sessions, Page Views, Conversion Rate, and Buy Box % appeared empty/N/A for most products, produced via live inspection of `public.amz_traffic_by_asin` (the table referred to as `fic_by_asin` in the task instructions — no table with that literal name exists; confirmed via `information_schema.tables` fuzzy search).

---

## Source table and columns

`public.amz_traffic_by_asin` — Amazon's own daily Sales & Traffic business report. Relevant columns: `date`, `sub_source_id`, `sub_source_name`, `market_place_id`, `market_place_name`, `childAsin`, `sku`, `sessions`, `pageViews`, `buyBoxPercentage`, `unitsOrdered` (a secondary cross-check field, not the primary sales source).

## Source grain

**date + account + marketplace + ASIN + SKU** — confirmed, not assumed. Live duplicate-key check on `(date, sub_source_id, market_place_name, childAsin)` alone found 1,201 "duplicate" groups out of 123,974 total rows. Investigated at scale (not sampled superficially): **1,183 of 1,191 groups (99.3%) have IDENTICAL Sessions/Page Views/Buy Box values repeated across every SKU-variant row** for that ASIN/date — confirming Amazon attributes the ASIN-level total to each SKU-variant row, not a per-SKU split. **This directly caused the v003 double/multi-counting bug** (the original SQL grouped by ASIN and used `SUM(sessions)`, summing the repeated per-variant values instead of taking the single true value).

## Date coverage (live-verified, per account+marketplace — not assumed current)

| Account | Marketplace | Feed min date | Feed max date |
|---|---|---|---|
| DCVoltage | UK | 2025-03-07 | **2026-04-22** |
| DCVoltage | Germany | 2025-03-07 | **2026-04-22** |
| DCVoltage | Italy | 2025-03-08 | **2026-04-22** |
| LEDSONE | UK | 2025-01-01 | **2026-06-16** |
| LEDSONE | Germany | 2025-01-01 | **2026-07-18** |
| LEDSONE | France | 2025-01-01 | **2026-07-13** |
| LEDSONE | Italy | 2025-03-01 | **2026-06-22** |

**New finding beyond the earlier (2026-07-20, same day) discovery:** LEDSONE UK's feed is *also* stale relative to the current reporting window (2026-06-20 to 2026-07-19) — its own max date (2026-06-16) falls **before** the 30-day window even starts. This was not previously identified because the earlier discovery only flagged DCVoltage as stale; the v003 build's near-total emptiness was actually driven by both DCVoltage (all 3 marketplaces) **and** LEDSONE UK (its single largest marketplace by catalog size) having zero overlap with the reporting window.

## Account coverage / mapping

`sub_source_id` values are identical across `amz_traffic_by_asin`, `ppc_performance`, `order_transaction`, and `listing_data` (6=DCVoltage, 8=LEDSONE) — confirmed via a targeted `ILIKE '%dcv%'` search that found no alternate identifier for DCVoltage. **No account-mapping defect exists.**

## Marketplace coverage / mapping

`market_place_name` values are plain, clean text (`UK`, `Germany`, `Italy`, `France`, plus other non-approved marketplaces like `Belgium`, `Poland`, etc. that this report correctly excludes) — no numeric IDs, abbreviations, or casing issues found. **No marketplace-mapping defect exists.**

## ASIN coverage

`childAsin` is 100% populated (0 nulls across 123,974 rows), consistently 10-character Amazon ASIN format, no whitespace/casing anomalies found in sampled rows.

## SKU coverage

`sku` is 100% populated (0 nulls). Confirmed this is the true source of the "duplicate" ASIN-grain rows (multiple SKU-variant strings per ASIN/date, e.g. `SPSDP2WH3PK` and `SPSDP2WH3PK-AMN`).

## Duplicate behavior

See "Source grain" above — resolved by taking `MAX()` per `(date, account, marketplace, ASIN)` before any cross-day summation (matches the "aggregate traffic once at ASIN grain, do not duplicate across SKUs" requirement).

## Source null behavior

`sessions`, `pageViews`, `buyBoxPercentage` have **zero NULLs** in the raw table (0 of 123,974 rows) — the v003 emptiness was never caused by null values in the source; it was caused entirely by the **absence of a matching row** for most (account, marketplace, ASIN, date) combinations in the reporting window, which a `LEFT JOIN` correctly renders as no match, not a source-side null.

## Common-dataset join keys

`(date, account, marketplace, ASIN)` — aggregated server-side before joining to the ASIN→SKU bridge (unchanged, correct pattern; only the traffic-side aggregation function was fixed).

## Failed-join causes (all three, now distinguished, not conflated)

1. **Feed genuinely doesn't reach this period** (DCVoltage — all marketplaces; LEDSONE UK and, for 7/14-day periods, LEDSONE Italy) — `N/A — source outside reporting date coverage`.
2. **Feed covers the period, but this specific ASIN was never once recorded by Amazon's feed** — `N/A — no matching traffic source row`.
3. **Feed covers the period, ASIN is confirmed tracked, and genuinely had zero sessions** — a real `0`, not N/A.

## Mapping corrections

None required — account and marketplace mapping were already correct. The defect was entirely in (a) the same-day multi-SKU aggregation function and (b) the lack of a distinction between "outside coverage," "no matching row," and "confirmed zero."

## DCVoltage freshness limitation

Confirmed root cause (re-verified this session): DCVoltage's sales (`order_transaction`) and PPC (`ppc_performance`) are both current to 2026-07-19 — DCVoltage is fully active. Only the `amz_traffic_by_asin` feed stopped on 2026-04-22, specifically and only for this one report type. Monthly row-count trend (checked in the earlier same-day session) shows a genuine gradual-then-hard-stop pattern, not a sudden mapping break.

## Traffic data availability by marketplace (coverage %, real+confirmed-zero rows ÷ total rows, 30-day period)

| Account | Marketplace | Coverage % |
|---|---|---|
| DCVoltage | UK / Germany / Italy | 0.0% (feed entirely outside window) |
| LEDSONE | UK | 0.0% (feed entirely outside window) |
| LEDSONE | Italy | 16.43% (30-day only; 0% for 7/14-day — feed barely overlaps window start) |
| LEDSONE | Germany | 23.12% |
| LEDSONE | France | 24.46% |

**Low coverage even where the feed is current is expected, not a defect**: Amazon's Business Report only emits a row for an ASIN/date with actual measurable sessions; most of this catalog is long-tail, exactly the "no-moving products" this report exists to surface — the majority of rows having zero recorded sessions across a 30-day window is a plausible business reality for a slow-moving-inventory catalog, not proof of a broken join.

## Recommended output behavior

Implemented in v004: precise per-row N/A classification (see above), a visible data-quality panel disclosing exact REAL/TRUE_ZERO/OUTSIDE_COVERAGE/NO_MATCH counts per period, and an explicit DCVoltage/LEDSONE-UK/LEDSONE-Italy freshness warning — never a blanket, unexplained "N/A - source not available."

## Coverage matrix — Period × Account × Marketplace

| Period | Account | Marketplace | Rows | REAL | TRUE_ZERO | OUTSIDE_COVERAGE | NO_MATCH | Coverage % | Reason for missing values |
|---|---|---|---|---|---|---|---|---|---|
| 7d | DCVoltage | UK | 13,641 | 0 | 0 | 13,641 | 0 | 0.0% | Feed stopped 2026-04-22, entirely before window |
| 7d | DCVoltage | Germany | 3,967 | 0 | 0 | 3,967 | 0 | 0.0% | Same |
| 7d | DCVoltage | Italy | 3,961 | 0 | 0 | 3,961 | 0 | 0.0% | Same |
| 7d | LEDSONE | UK | 15,778 | 0 | 0 | 15,778 | 0 | 0.0% | Feed stopped 2026-06-16, before window start 2026-07-13 |
| 7d | LEDSONE | Germany | 6,786 | 43 | 1,526 | 0 | 5,217 | 23.12% | Feed current; most ASINs never tracked (long-tail) |
| 7d | LEDSONE | France | 5,736 | 8 | 1,395 | 0 | 4,333 | 24.46% | Feed current; most ASINs never tracked |
| 7d | LEDSONE | Italy | 3,974 | 0 | 0 | 3,974 | 0 | 0.0% | Feed stopped 2026-06-22, before window start 2026-07-13 |
| 14d | DCVoltage | UK/Germany/Italy | 13,641/3,967/3,961 | 0 | 0 | all | 0 | 0.0% | Same as 7d |
| 14d | LEDSONE | UK/Italy | 15,778/3,974 | 0 | 0 | all | 0 | 0.0% | Feed stopped before window start (2026-07-06) |
| 14d | LEDSONE | Germany | 6,786 | 57 | 1,512 | 0 | 5,217 | 23.12% | Feed current |
| 14d | LEDSONE | France | 5,736 | 106 | 1,297 | 0 | 4,333 | 24.46% | Feed current |
| 30d | DCVoltage | UK/Germany/Italy | 13,641/3,967/3,961 | 0 | 0 | all | 0 | 0.0% | Feed stopped before window start (2026-06-20) |
| 30d | LEDSONE | UK | 15,778 | 0 | 0 | 15,778 | 0 | 0.0% | Feed stopped 2026-06-16, before window start |
| 30d | LEDSONE | Italy | 3,974 | 5 | 648 | 0 | 3,321 | 16.43% | Feed covers only 2026-06-20 to 2026-06-22 (3 of 30 days) |
| 30d | LEDSONE | Germany | 6,786 | 92 | 1,477 | 0 | 5,217 | 23.12% | Feed current |
| 30d | LEDSONE | France | 5,736 | 184 | 1,219 | 0 | 4,333 | 24.46% | Feed current |

## One next step

Escalate the LEDSONE-UK and LEDSONE-Italy traffic-feed staleness to whoever manages Amazon Business Report ingestion for LEDSONE (same escalation as the already-known DCVoltage gap) — this is a real, external upstream data issue this codebase cannot fix.
