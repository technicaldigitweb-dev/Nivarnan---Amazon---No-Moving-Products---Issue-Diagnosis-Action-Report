# Account & Marketplace Filter Evidence

**What this is:** Live-query evidence for exact account and marketplace stored values across all tables this report uses.

**Why it exists:** The task instruction explicitly forbids guessing whether marketplace values are country names, codes, or IDs, and forbids assuming names match across tables.

**Business question supported:** REQ-AMZ-NMP-001-D01 (multi-account, multi-marketplace scope).

**Source:** `PRIMARY_SKILLS_MCP` — `execute_sql` against `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data`, `public.traffic_data`.

---

## Account identifiers

```sql
SELECT DISTINCT ss_name, sub_source_id FROM public.ppc
WHERE source = 1 AND (ss_name ILIKE '%ledsone%' OR ss_name ILIKE '%dcvoltage%' OR ss_name ILIKE '%dcv%')
ORDER BY ss_name;
-- → amazon Dcvoltage (6), amazon Ledsone (8)

SELECT DISTINCT ss_name, order_sub_source FROM public.order_transaction
WHERE source_name = 'AMAZON' AND (ss_name ILIKE '%ledsone%' OR ss_name ILIKE '%dcvoltage%' OR ss_name ILIKE '%dcv%')
ORDER BY ss_name;
-- → amazon Dcvoltage (6), amazon Ledsone (8), amazon Ledsonede (14, OUT OF SCOPE), DCV UK (236, OUT OF SCOPE)

SELECT DISTINCT sub_source_name, sub_source FROM public.listing_data
WHERE which_channel = 1 AND (sub_source_name ILIKE '%ledsone%' OR sub_source_name ILIKE '%dcvoltage%' OR sub_source_name ILIKE '%dcv%')
ORDER BY sub_source_name;
-- → amazon Dcvoltage (6), amazon Ledsone (8)
```

**Confirmed:** `sub_source_id = 8` ↔ LEDSONE (`'amazon Ledsone'`), `sub_source_id = 6` ↔ DCVoltage (`'amazon Dcvoltage'`) — identical ID and spelling across `ppc`, `order_transaction` (as `order_sub_source`), and `listing_data` (as `sub_source`). No join/mapping needed across tables — one ID per account works everywhere. Two additional Amazon accounts exist (`amazon Ledsonede` id 14, `DCV UK` id 236) — explicitly excluded per the corrected business requirement (only LEDSONE and DCVoltage are in scope).

## Marketplace values

```sql
SELECT DISTINCT marketplace, sub_source_id FROM public.ppc_performance
WHERE source = 1 AND sub_source_id IN (6,8) ORDER BY marketplace, sub_source_id;
```

Result (accounts 6 and 8 combined): Canada, France(8 only), Germany, Italy, Mexico, Netherlands, Spain(6 only), UK, US — all as **plain country names** (`'UK'`, `'Germany'`, `'France'`, `'Italy'`), not codes. Same exact strings independently confirmed in `order_transaction.market_place` and `listing_data.market_place`.

**In-scope marketplace values, confirmed identical across all three tables: `'UK'`, `'Germany'`, `'France'`, `'Italy'`.**

## Material finding — DCVoltage × France

```sql
SELECT 'ppc_performance', COUNT(*) FROM public.ppc_performance WHERE source=1 AND sub_source_id=6 AND marketplace='France'
UNION ALL SELECT 'order_transaction', COUNT(*) FROM public.order_transaction WHERE source_name='AMAZON' AND order_sub_source=6 AND market_place='France'
UNION ALL SELECT 'listing_data', COUNT(*) FROM public.listing_data WHERE which_channel=1 AND sub_source=6 AND market_place='France';
-- → all three return 0
```

DCVoltage has **zero** PPC, sales, and listing rows for France. However:

```sql
SELECT market_place, sub_source_name, COUNT(*), MAX(date) FROM public.traffic_data
WHERE sub_source=6 AND which_channel=1 AND market_place='France' GROUP BY market_place, sub_source_name;
-- → 5,521 rows, latest 2026-07-11
```

DCVoltage **does** have organic traffic (impression/click) rows for France — a real, verified asymmetry: Amazon shows some visibility for DCVoltage's France listings, but DCVoltage runs no PPC there and has made no completed sales there in the dataset. This must render as a genuine empty/near-empty combination in the report (not an error, not silently hidden from the filter).

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED.

## Pass/fail rule

PASS if every account/marketplace value used in implementation SQL is traceable to a live query result in this file. Met.

## Known limitations

`traffic_data`'s own cadence (weekly, see `2026-07-17__blue_field_source_mapping.md`) means its account/marketplace coverage was checked but not used to gate the account/marketplace filter list itself — the filter list is driven by PPC+sales+listing presence, which is daily-grain and fully verified.

## Next action

Use `sub_source_id IN (6,8)` and `marketplace IN ('UK','Germany','France','Italy')` as the fixed filter set in all report SQL; render DCVoltage×France explicitly as no-data rather than omitting it.
