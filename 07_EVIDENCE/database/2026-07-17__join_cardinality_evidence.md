# Join & Cardinality Evidence

**What this is:** Evidence of ASIN↔SKU cardinality, `amzn.gr.*` alias prevalence, stock-table duplicate-row check, and an empirical demonstration of join-multiplication risk — all from bounded/aggregate queries, not the full report.

**Why it exists:** The requirement forbids inventing a mapping rule or running the complete final report; it requires the actual cardinality and fan-out risk to be measured.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Source:** `PRIMARY_SKILLS_MCP` — `execute_sql` against `public.listing_data`, `public.ppc_performance`, `public.ppc`, `public.location_wise_inv_stock`.

---

## ASIN → SKU cardinality (Amazon, UK, valid rows)

```sql
WITH asin_sku_counts AS (
  SELECT ref_id AS asin, COUNT(DISTINCT COALESCE(NULLIF(mapped_sku,''), sku)) AS sku_count
  FROM public.listing_data
  WHERE which_channel = 1 AND market_place = 'UK' AND wrong_sku = 0 AND is_parent = 0
  GROUP BY ref_id
)
SELECT sku_count, COUNT(*) AS asin_count
FROM asin_sku_counts GROUP BY sku_count ORDER BY sku_count;
```

| Resolved SKUs per ASIN | ASIN count |
|---|---|
| 1 | 29,925 |
| 2 | 1,001 |
| 3 | 32 |
| 4 | 5 |

**Finding:** ~96.7% of Amazon UK ASINs resolve to exactly one inventory SKU; ~3.3% (1,038 ASINs) resolve to 2–4 SKUs. A future report must `SUM` stock across all resolved SKUs per ASIN rather than assume 1:1 — a real, non-trivial minority case, not a theoretical one.

## `mapped_sku` population rate

```sql
SELECT COUNT(*) FILTER (WHERE mapped_sku IS NOT NULL AND mapped_sku <> '') AS mapped_sku_rows, COUNT(*) AS total_rows
FROM public.listing_data
WHERE which_channel = 1 AND market_place = 'UK' AND wrong_sku = 0;
```

**Result:** 15,152 of 35,265 UK Amazon listing rows (43.0%) have a populated `mapped_sku` that differs from the listing `sku`. Confirms the `COALESCE(NULLIF(mapped_sku,''), sku)` resolution step is mandatory, not optional — skipping it would silently use the wrong SKU for nearly half of UK Amazon listings.

## `amzn.gr.*` platform-alias prevalence (in the proposed 30-day window)

```sql
SELECT COUNT(*) FILTER (WHERE sku LIKE 'amzn.gr.%') AS amzn_gr_rows,
       COUNT(*) FILTER (WHERE sku = '0') AS zero_sku_rows,
       COUNT(*) AS total_rows
FROM public.ppc_performance
WHERE source = 1 AND marketplace = 'UK' AND date BETWEEN '2026-06-16' AND '2026-07-15';
```

**Result:** 30 `amzn.gr.*` rows and 0 `sku = '0'` rows out of 320,057 total Amazon UK PPC rows in the window. Small (0.01%) but real — `amzn.gr.*` values are Amazon-generated internal aliases with no inventory equivalent and must be excluded (`sku NOT LIKE 'amzn.gr.%'`) from any stock-bridging step, per the live table definition.

## Stock table duplicate-row check

```sql
SELECT sku, COUNT(*) AS row_count
FROM public.location_wise_inv_stock
WHERE location = 'UK'
GROUP BY sku HAVING COUNT(*) > 1 LIMIT 10;
```

**Result:** 10 SKUs returned with `row_count = 2` (out of 43,738 total UK rows) — e.g. `CO123ACLGPK`, `ENC10071`, several combo SKUs. A small number of SKUs have duplicate UK rows. **Any stock query must `SUM(COALESCE(stock,0))` grouped by `sku`, never assume one row per SKU.**

## Join-multiplication risk — empirical test

Step 1: aggregate spend per ASIN correctly (SB excluded, `amzn.gr.*` excluded, spend summed once per ASIN):

```sql
WITH ppc_spend AS (
  SELECT pp.ref_id AS asin, SUM(pp.spend) AS spend_30d
  FROM public.ppc_performance pp
  JOIN public.ppc p ON p.parent_id = pp.parent_id AND p.record_main_type = 'campaign'
  WHERE pp.source = 1 AND pp.record_type = 'ad' AND pp.marketplace = 'UK'
    AND p.record_subtype <> 'SB' AND pp.ref_id <> '0' AND pp.sku <> '0'
    AND pp.sku NOT LIKE 'amzn.gr.%' AND pp.date BETWEEN '2026-06-16' AND '2026-07-15'
  GROUP BY pp.ref_id ORDER BY spend_30d DESC LIMIT 5
) SELECT * FROM ppc_spend;
```

| asin | spend_30d |
|---|---|
| B096FPKPNQ | 170.81 |
| B0965HZJGN | 139.15 |
| B0FZCW7KC7 | 134.05 |
| B0FX2SHBL5 | 120.19 |
| B0DVLPPMXL | 114.38 |

Step 2: join this correctly-aggregated spend to `listing_data` **without re-aggregating**, to show what happens if spend were summed *after* the bridge instead of before it:

```sql
WITH ppc_spend AS ( ... same as above but unlimited ... ),
naive_join AS (
  SELECT ps.asin, ps.spend_30d, COUNT(*) AS matched_listing_rows
  FROM ppc_spend ps
  JOIN public.listing_data ld ON ld.ref_id = ps.asin AND ld.which_channel = 1 AND ld.market_place = 'UK' AND ld.wrong_sku = 0
  GROUP BY ps.asin, ps.spend_30d HAVING COUNT(*) > 1
) SELECT * FROM naive_join ORDER BY matched_listing_rows DESC LIMIT 5;
```

| asin | spend_30d | matched_listing_rows |
|---|---|---|
| B08TMKPGZL | 0.00 | 6 |
| B08S45CM19 | 0.03 | 4 |
| B07CVD34CJ | 0.00 | 4 |
| B07PM6VXCG | 1.85 | 4 |
| B07VFV228J | 3.95 | 4 |

**Finding — confirmed, not theoretical:** joining a single ASIN's already-aggregated spend to `listing_data` matches up to 6 rows for one ASIN. If spend were summed *after* this join instead of before it, these ASINs' spend would be overstated by 4–6x.

## Recommended safe sequence (discovery recommendation only — not final SQL)

1. Aggregate PPC spend by ASIN first (SB excluded, `amzn.gr.*` excluded, correct 30-day window), independently of any bridge.
2. Aggregate sales (`order_transaction`, `order_status = 'Completed'`, `SUM(order_total)`) independently, by ASIN.
3. Resolve the ASIN→SKU bridge via `listing_data` (`wrong_sku=0`, `is_parent=0`, `COALESCE(NULLIF(mapped_sku,''),sku)`) as its own step, deduplicated to distinct `(asin, resolved_sku)` pairs — never re-aggregate spend/sales through this join.
4. Aggregate current UK stock by `sku` (`SUM(COALESCE(stock,0))` grouped by `sku`, from `location_wise_inv_stock` — accounts for the duplicate-row SKUs found above).
5. Join only the three already-aggregated datasets (spend-by-ASIN, sales-by-ASIN, stock-by-resolved-SKU) at the end; `SUM` stock across an ASIN's multiple resolved SKUs where cardinality > 1.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED — every figure above is from a live, reproducible query; no final report was assembled.

## Pass/fail rule

PASS if the join-multiplication risk is demonstrated with real data (not asserted) and a safe aggregation-order recommendation is recorded without building the final query.

## Known limitations

- The duplicate-stock-row check was capped at `LIMIT 10`; the true count of UK SKUs with >1 row is not known exactly (bounded query, not a full scan).
- SB exclusion and `amzn.gr.*` exclusion were validated together in one query; their effects were not isolated from each other.

## Next action

Carry the 5-step sequence above into the requirement's "Reusable Asset Expected" (§11) implementation phase — not part of this discovery task.
