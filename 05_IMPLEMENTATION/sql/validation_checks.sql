-- validation_checks.sql
-- REQ-AMZ-NMP-001-D01 -- independent reconciliation control totals.
-- Each query below computes a control total INDEPENDENTLY of main_report.sql's
-- join path, so that validate_output.py can compare "source aggregate" vs
-- "report aggregate" per 06_VALIDATION/2026-07-17__sql_validation_report.md.

-- CHECK 1: PPC spend control total per account+marketplace (no ASIN/SKU join at all)
SELECT pp.sub_source_id, pp.marketplace, SUM(pp.spend) AS control_ppc_spend
FROM public.ppc_performance pp
JOIN public.ppc p ON p.parent_id = pp.parent_id AND p.record_main_type = 'campaign'
WHERE pp.source = 1
  AND pp.record_type = 'ad'
  AND pp.sub_source_id IN (6, 8)
  AND pp.marketplace IN ('UK','Germany','France','Italy')
  AND p.record_subtype <> 'SB'
  AND pp.ref_id <> '0' AND pp.sku <> '0' AND pp.sku NOT LIKE 'amzn.gr.%'
  AND pp.date BETWEEN :start_date AND :end_date
GROUP BY pp.sub_source_id, pp.marketplace;

-- CHECK 2: Units Ordered control total per account+marketplace
SELECT order_sub_source, market_place, SUM(quantity) AS control_units_ordered
FROM public.order_transaction
WHERE source_name = 'AMAZON' AND order_sub_source IN (6,8)
  AND market_place IN ('UK','Germany','France','Italy')
  AND order_status = 'Completed'
  AND order_date BETWEEN :start_date AND (:end_date::date + INTERVAL '1 day')
GROUP BY order_sub_source, market_place;

-- CHECK 3: fan-out proof -- naive join row-count vs pre-aggregated ASIN count.
-- Expect naive_matched_rows > distinct_asins whenever any ASIN has >1 listing_data row;
-- the report SQL must NOT sum spend/sales at the naive-join grain.
WITH ppc_spend AS (
    SELECT pp.sub_source_id, pp.marketplace, pp.ref_id AS asin, SUM(pp.spend) AS spend
    FROM public.ppc_performance pp
    JOIN public.ppc p ON p.parent_id = pp.parent_id AND p.record_main_type = 'campaign'
    WHERE pp.source = 1 AND pp.record_type = 'ad'
      AND pp.sub_source_id IN (6,8) AND pp.marketplace IN ('UK','Germany','France','Italy')
      AND p.record_subtype <> 'SB' AND pp.ref_id <> '0' AND pp.sku <> '0'
      AND pp.sku NOT LIKE 'amzn.gr.%'
      AND pp.date BETWEEN :start_date AND :end_date
    GROUP BY pp.sub_source_id, pp.marketplace, pp.ref_id
)
SELECT
    COUNT(DISTINCT ps.asin)                              AS distinct_asins,
    COUNT(*) FILTER (WHERE ld.ref_id IS NOT NULL)         AS naive_matched_rows
FROM ppc_spend ps
LEFT JOIN public.listing_data ld
       ON ld.ref_id = ps.asin AND ld.which_channel = 1 AND ld.wrong_sku = 0
      AND ld.sub_source = ps.sub_source_id AND ld.market_place = ps.marketplace;

-- CHECK 4: shared-German-stock double-count guard.
-- A stock SUMMARY across Germany+France+Italy rows for the same resolved SKU
-- must equal the SKU's single Germany-location stock figure, NOT 3x it.
SELECT sku, location, SUM(COALESCE(stock,0)) AS stock_qty
FROM public.location_wise_inv_stock
WHERE location = 'Germany'
GROUP BY sku, location;
-- (validate_output.py compares this single per-SKU figure against whatever the
--  rendered HTML shows on the Germany/France/Italy rows for the same SKU --
--  they must be equal per row, and any summed "total stock" card must use
--  this control query's total once, not three times.)

-- CHECK 5: amzn.gr.* alias exclusion proof (must be zero in the report's SKU column)
SELECT COUNT(*) AS amzn_gr_rows_if_not_excluded
FROM public.ppc_performance
WHERE source = 1 AND sub_source_id IN (6,8) AND marketplace IN ('UK','Germany','France','Italy')
  AND sku LIKE 'amzn.gr.%'
  AND date BETWEEN :start_date AND :end_date;

-- CHECK 6: row-key uniqueness proof (account+marketplace+asin+resolved_sku must have no duplicates)
WITH bridge AS (
    SELECT sub_source AS sub_source_id, market_place AS marketplace, ref_id AS asin,
           COALESCE(NULLIF(mapped_sku,''), sku) AS resolved_sku
    FROM public.listing_data
    WHERE which_channel = 1 AND sub_source IN (6,8)
      AND market_place IN ('UK','Germany','France','Italy')
      AND wrong_sku = 0 AND is_parent = 0
)
SELECT sub_source_id, marketplace, asin, resolved_sku, COUNT(*) AS row_count
FROM bridge
GROUP BY sub_source_id, marketplace, asin, resolved_sku
HAVING COUNT(*) > 1;
-- expect ZERO rows returned -- any row here is a row-key duplication defect.
