"""
anpia_snapshot_enrichment.py -- REQ-ANPIA-REQ-01-D02

Current-snapshot and historical-lookup joins, applied ONCE after period
aggregation -- never repeated into daily additive facts. All queries here
are small, bounded, dimension-grain lookups (current listing rows,
current stock, one MAX(order_date) per identity) -- not bulk fact
extraction.
"""

from anpia_db_connection import run_query

DIMENSION_SQL = """
SELECT DISTINCT ON (sub_source, market_place, ref_id, resolved_sku)
    sub_source, market_place, ref_id AS asin, resolved_sku,
    title, price, product_type
FROM (
    SELECT sub_source, market_place, ref_id, is_offer, price, id, title, product_type,
           COALESCE(NULLIF(mapped_sku,''), sku) AS resolved_sku
    FROM public.listing_data
    WHERE which_channel=1 AND wrong_sku=0 AND sub_source IN (6,8)
      AND market_place IN ('UK','Germany','France','Italy')
) x
ORDER BY sub_source, market_place, ref_id, resolved_sku, is_offer ASC, (price IS NULL) ASC, id ASC
"""

CATEGORY_AVG_PRICE_SQL = """
-- FIX (2026-07-20, v004): plain AVG(price) was contaminated by malformed/
-- outlier price values -- confirmed live, e.g. Germany/LIGHT_BULB had a
-- max price of EUR 649,555 against a median in the tens of pounds,
-- pulling the "average" to EUR 11,932. Excludes non-positive prices
-- (invalid) and applies a standard Tukey IQR fence (values beyond
-- Q1-1.5*IQR .. Q3+1.5*IQR) when a category has >=5 priced listings --
-- too few points below that for IQR to be meaningful, so small categories
-- use the plain (already-clean, price>0) average instead.
WITH priced AS (
    SELECT market_place, product_type, price
    FROM public.listing_data
    WHERE which_channel=1 AND wrong_sku=0 AND sub_source IN (6,8)
      AND market_place IN ('UK','Germany','France','Italy')
      AND price IS NOT NULL AND price > 0 AND product_type IS NOT NULL
),
bounds AS (
    SELECT market_place, product_type,
           COUNT(*) AS n,
           percentile_cont(0.25) WITHIN GROUP (ORDER BY price) AS q1,
           percentile_cont(0.75) WITHIN GROUP (ORDER BY price) AS q3
    FROM priced
    GROUP BY market_place, product_type
)
SELECT p.market_place, p.product_type,
       AVG(p.price) AS category_avg_price_raw,
       AVG(CASE
             WHEN b.n >= 5 AND p.price BETWEEN (b.q1 - 1.5*(b.q3-b.q1)) AND (b.q3 + 1.5*(b.q3-b.q1)) THEN p.price
             WHEN b.n < 5 THEN p.price
             ELSE NULL
           END) AS category_avg_price_trimmed,
       b.n AS sample_size,
       SUM(CASE WHEN b.n >= 5 AND NOT (p.price BETWEEN (b.q1 - 1.5*(b.q3-b.q1)) AND (b.q3 + 1.5*(b.q3-b.q1))) THEN 1 ELSE 0 END) AS excluded_outlier_count
FROM priced p
JOIN bounds b ON b.market_place=p.market_place AND b.product_type=p.product_type
GROUP BY p.market_place, p.product_type, b.n
"""

STOCK_SQL = """
SELECT sku, location, SUM(stock) AS total_stock
FROM public.location_wise_inv_stock
WHERE location IN ('UK','Germany')
GROUP BY sku, location
"""

LAST_SALE_SQL = """
SELECT order_sub_source AS sub_source, market_place, asin,
       MAX(order_date::date) AS last_sale_date
FROM public.order_transaction
WHERE source_name='AMAZON' AND order_sub_source IN (6,8)
  AND market_place IN ('UK','Germany','France','Italy')
  AND order_status='Completed'
GROUP BY order_sub_source, market_place, asin
"""

ACCOUNT_NAME = {6: "DCVoltage", 8: "LEDSONE"}
WAREHOUSE_FOR_MARKETPLACE = {"UK": "UK", "Germany": "Germany", "France": "Germany", "Italy": "Germany"}


def load_dimension(conn):
    rows = run_query(conn, DIMENSION_SQL)
    out = {}
    for r in rows:
        key = (ACCOUNT_NAME.get(r["sub_source"], str(r["sub_source"])), r["market_place"], r["asin"], r["resolved_sku"])
        out[key] = {"title": r["title"], "price": float(r["price"]) if r["price"] is not None else None, "product_type": r["product_type"]}
    return out


def load_category_avg_price(conn):
    """Returns {(marketplace, product_type): value}, using the outlier-
    trimmed average. Also returns a parallel diagnostics dict so callers
    can disclose sample size and how many outliers were excluded, per
    category -- never silently substitutes a value without a trail."""
    rows = run_query(conn, CATEGORY_AVG_PRICE_SQL)
    out = {}
    diagnostics = {}
    for r in rows:
        key = (r["market_place"], r["product_type"])
        trimmed = r["category_avg_price_trimmed"]
        raw = r["category_avg_price_raw"]
        out[key] = float(trimmed) if trimmed is not None else float(raw)
        diagnostics[key] = {
            "sample_size": r["sample_size"],
            "excluded_outlier_count": r["excluded_outlier_count"],
            "raw_avg": float(raw),
            "trimmed_avg": float(trimmed) if trimmed is not None else float(raw),
        }
    return out, diagnostics


def load_stock(conn):
    rows = run_query(conn, STOCK_SQL)
    out = {}
    for r in rows:
        out[(r["sku"], r["location"])] = int(r["total_stock"]) if r["total_stock"] is not None else 0
    return out


def load_last_sale(conn):
    rows = run_query(conn, LAST_SALE_SQL)
    out = {}
    for r in rows:
        key = (ACCOUNT_NAME.get(r["sub_source"], str(r["sub_source"])), r["market_place"], r["asin"])
        out[key] = r["last_sale_date"]
    return out


def warehouse_for(marketplace):
    return WAREHOUSE_FOR_MARKETPLACE.get(marketplace, "Germany")


TRAFFIC_FEED_COVERAGE_SQL = """
SELECT sub_source_id, market_place_name, MIN(date) AS feed_min, MAX(date) AS feed_max
FROM public.amz_traffic_by_asin
WHERE sub_source_id IN (6,8) AND market_place_name IN ('UK','Germany','France','Italy')
GROUP BY 1,2
"""

EVER_TRACKED_ASINS_SQL = """
SELECT sub_source_id, market_place_name, "childAsin" AS asin
FROM public.amz_traffic_by_asin
WHERE sub_source_id IN (6,8) AND market_place_name IN ('UK','Germany','France','Italy')
GROUP BY 1,2,3
"""


def load_traffic_feed_coverage(conn):
    """Returns {(account, marketplace): (feed_min_date, feed_max_date)} --
    the account+marketplace-level date range the traffic source actually
    covers, used to distinguish 'this period is entirely outside the feed's
    coverage' from 'the feed covers this period but this ASIN had no rows'."""
    rows = run_query(conn, TRAFFIC_FEED_COVERAGE_SQL)
    out = {}
    for r in rows:
        key = (ACCOUNT_NAME.get(r["sub_source_id"], str(r["sub_source_id"])), r["market_place_name"])
        out[key] = (r["feed_min"], r["feed_max"])
    return out


def load_ever_tracked_asins(conn):
    """Returns {(account, marketplace): set(asin, ...)} -- every ASIN that
    has EVER appeared in the traffic feed for that account+marketplace,
    across the feed's full history (not just the reporting window). Used
    to distinguish 'this ASIN is tracked by Amazon's feed but had zero
    sessions this period' (a true, confident 0) from 'this ASIN has never
    once appeared in the feed' (N/A -- no matching traffic source row)."""
    rows = run_query(conn, EVER_TRACKED_ASINS_SQL)
    out = {}
    for r in rows:
        key = (ACCOUNT_NAME.get(r["sub_source_id"], str(r["sub_source_id"])), r["market_place_name"])
        out.setdefault(key, set()).add(r["asin"])
    return out
