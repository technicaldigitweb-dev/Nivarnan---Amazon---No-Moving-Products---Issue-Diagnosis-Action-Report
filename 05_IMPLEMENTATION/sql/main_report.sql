-- main_report.sql
-- REQ-AMZ-NMP-001-D01 — Amazon multi-account/multi-marketplace daily report
--
-- Parameters (bind before execution): :start_date, :end_date, :period_days
-- Accounts fixed: sub_source_id IN (6, 8)  -- 6=DCVoltage, 8=LEDSONE
-- Marketplaces fixed: marketplace/market_place IN ('UK','Germany','France','Italy')
--
-- Implements the mandatory aggregation-before-join sequence from
-- 04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md :
--   1. Aggregate PPC independently by account+marketplace+ASIN+period (SB and amzn.gr.* excluded)
--   2. Aggregate sales independently by account+marketplace+ASIN+period
--   3. Resolve ASIN->SKU via listing_data (wrong_sku=0, mapped_sku fallback)
--   4. Aggregate current stock by warehouse-mapped location + resolved SKU
--   5. Join only the aggregated datasets, once, producing one row per
--      account + marketplace + ASIN + resolved SKU.
--
-- Fields NOT included below (Sessions, Page Views, Buy Box %, Conversion Rate,
-- Click-Through Rate, Category Avg Price) are REVIEW_REQUIRED per
-- 07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md and
-- decision register DEC-TECH-004/005/006 -- they are rendered as an explicit
-- "N/A - pending source confirmation" placeholder by data_transform.py,
-- not computed here, so that no formula is invented in SQL.

WITH accounts(sub_source_id, account_label) AS (
    VALUES (8, 'LEDSONE'), (6, 'DCVoltage')
),

ppc_agg AS (                                   -- (1) PPC spend, aggregated first
    SELECT
        pp.sub_source_id,
        pp.marketplace,
        pp.ref_id                          AS asin,
        SUM(pp.spend)                      AS ppc_spend,
        SUM(pp.sales)                      AS ppc_attributed_sales
    FROM public.ppc_performance pp
    JOIN public.ppc p
        ON p.parent_id = pp.parent_id
       AND p.record_main_type = 'campaign'
    WHERE pp.source = 1
      AND pp.record_type = 'ad'
      AND pp.sub_source_id IN (6, 8)
      AND pp.marketplace IN ('UK', 'Germany', 'France', 'Italy')
      AND p.record_subtype <> 'SB'              -- exclude Sponsored Brands (not ASIN-attributable)
      AND pp.ref_id <> '0'
      AND pp.sku <> '0'
      AND pp.sku NOT LIKE 'amzn.gr.%'            -- exclude Amazon-generated platform aliases
      AND pp.date BETWEEN :start_date AND :end_date
    GROUP BY pp.sub_source_id, pp.marketplace, pp.ref_id
),

sales_agg AS (                                 -- (2) Sales, aggregated independently
    SELECT
        order_sub_source AS sub_source_id,
        market_place      AS marketplace,
        asin,
        SUM(quantity)                       AS units_ordered,
        MAX(order_date)                     AS last_order_date
    FROM public.order_transaction
    WHERE source_name = 'AMAZON'
      AND order_sub_source IN (6, 8)
      AND market_place IN ('UK', 'Germany', 'France', 'Italy')
      AND order_status = 'Completed'
      AND order_date BETWEEN :start_date AND (:end_date::date + INTERVAL '1 day')
    GROUP BY order_sub_source, market_place, asin
),

last_sale_agg AS (                             -- Days Since Last Sale = all-time max, no period window
    SELECT
        order_sub_source AS sub_source_id,
        market_place      AS marketplace,
        asin,
        MAX(order_date)::date AS last_sale_date
    FROM public.order_transaction
    WHERE source_name = 'AMAZON'
      AND order_sub_source IN (6, 8)
      AND market_place IN ('UK', 'Germany', 'France', 'Italy')
      AND order_status = 'Completed'
    GROUP BY order_sub_source, market_place, asin
),

bridge AS (                                    -- (3) ASIN -> resolved SKU bridge (listing_data only)
    -- DISTINCT ON guarantees exactly one row per (account, marketplace, ASIN,
    -- resolved SKU) -- the row-key grain this report requires. Without this,
    -- an ASIN with both a base "is_offer=0" listing row and a duplicate
    -- "is_offer=1" offer row resolving to the SAME mapped_sku produces two
    -- rows sharing one row key, which the validation's row-key-uniqueness
    -- check correctly flags as a defect (found empirically during v001 build
    -- -- see 07_EVIDENCE/output/2026-07-17__report_generation_evidence.md).
    -- Preference order: non-offer row first, then the row with a non-null
    -- price, then lowest id (deterministic, not arbitrary).
    SELECT DISTINCT ON (sub_source, market_place, ref_id, COALESCE(NULLIF(mapped_sku, ''), sku))
        sub_source                                       AS sub_source_id,
        market_place                                      AS marketplace,
        ref_id                                             AS asin,
        COALESCE(NULLIF(mapped_sku, ''), sku)              AS resolved_sku,
        title,
        price,
        currency
    FROM public.listing_data
    WHERE which_channel = 1
      AND sub_source IN (6, 8)
      AND market_place IN ('UK', 'Germany', 'France', 'Italy')
      AND wrong_sku = 0
      AND is_parent = 0                                    -- parent rows have no sellable SKU
    ORDER BY sub_source, market_place, ref_id, COALESCE(NULLIF(mapped_sku, ''), sku),
             is_offer ASC, (price IS NULL) ASC, id ASC
),

stock_agg AS (                                 -- (4) Current stock, aggregated by resolved SKU + warehouse
    SELECT sku, location, SUM(COALESCE(stock, 0)) AS stock_qty, MAX(updated_at) AS stock_updated_at
    FROM public.location_wise_inv_stock
    WHERE location IN ('UK', 'Germany')
    GROUP BY sku, location
)

SELECT                                          -- (5) single join of pre-aggregated datasets
    a.account_label                                        AS account,
    b.marketplace,
    b.asin,
    b.resolved_sku,
    b.title                                                AS product_title,
    b.price,
    b.currency,
    ls.last_sale_date,
    (:end_date::date - ls.last_sale_date)                  AS days_since_last_sale,
    s.stock_qty,
    s.stock_updated_at,
    COALESCE(sa.units_ordered, 0)                          AS units_ordered,
    COALESCE(pa.ppc_spend, 0)                              AS ppc_spend,
    CASE WHEN COALESCE(pa.ppc_attributed_sales, 0) = 0 THEN NULL
         ELSE (pa.ppc_spend / NULLIF(pa.ppc_attributed_sales, 0)) * 100
    END                                                     AS acos_pct
FROM bridge b
JOIN accounts a ON a.sub_source_id = b.sub_source_id
LEFT JOIN ppc_agg pa
       ON pa.sub_source_id = b.sub_source_id
      AND pa.marketplace   = b.marketplace
      AND pa.asin          = b.asin
LEFT JOIN sales_agg sa
       ON sa.sub_source_id = b.sub_source_id
      AND sa.marketplace   = b.marketplace
      AND sa.asin          = b.asin
LEFT JOIN last_sale_agg ls
       ON ls.sub_source_id = b.sub_source_id
      AND ls.marketplace   = b.marketplace
      AND ls.asin          = b.asin
LEFT JOIN stock_agg s
       ON s.sku      = b.resolved_sku
      AND s.location = (CASE WHEN b.marketplace = 'UK' THEN 'UK' ELSE 'Germany' END)
ORDER BY a.account_label, b.marketplace, pa.ppc_spend DESC NULLS LAST, b.asin, b.resolved_sku;

-- NOTE ON SCALE: this query's unfiltered result set covers ~49,700+ distinct
-- ASINs (per 07_EVIDENCE/database/2026-07-17__expanded_join_cardinality_evidence.md
-- discovery counts) before SKU expansion -- i.e. tens of thousands of output
-- rows. Per the corrected requirement, NO Top-N/percentile/spend cutoff may be
-- applied here. Pagination/rendering-scale handling belongs in html_renderer.py
-- and the HTML template, not in this query, per the design document.
