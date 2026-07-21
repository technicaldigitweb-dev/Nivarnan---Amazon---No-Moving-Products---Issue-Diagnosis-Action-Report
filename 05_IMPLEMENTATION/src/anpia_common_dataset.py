"""
anpia_common_dataset.py -- REQ-ANPIA-REQ-01-D02

Builds the single common daily-grain dataset (report_date + account +
marketplace + amazon_asin + resolved_amazon_sku) by aggregating PPC,
sales, and traffic sources independently to daily grain server-side
(aggregate-before-join pattern) before joining them, once, to the
ASIN->SKU bridge. Extracts via a server-side cursor with fetchmany
batching and writes to JSONL with a checkpoint file. No raw fact table
is ever joined directly to another raw fact table.
"""

import datetime
import decimal
import json
import os

MASTER_SQL = r"""
WITH bridge AS (
  SELECT DISTINCT ON (sub_source, market_place, ref_id, resolved_sku)
    sub_source, market_place, ref_id AS asin,
    resolved_sku, title, price, product_type
  FROM (
    SELECT sub_source, market_place, ref_id, is_offer, price, id, title, product_type,
           COALESCE(NULLIF(mapped_sku,''), sku) AS resolved_sku
    FROM public.listing_data
    WHERE which_channel=1 AND wrong_sku=0 AND sub_source IN (6,8)
      AND market_place IN ('UK','Germany','France','Italy')
  ) x
  ORDER BY sub_source, market_place, ref_id, resolved_sku, is_offer ASC, (price IS NULL) ASC, id ASC
),
ppc_daily AS (
  SELECT pp.date, pp.sub_source_id AS sub_source, pp.marketplace AS market_place, pp.ref_id AS asin,
    SUM(pp.spend) AS ppc_spend, SUM(pp.clicks) AS ppc_clicks,
    SUM(pp.impressions) AS ppc_impressions, SUM(pp.sales) AS ppc_attributed_sales
  FROM public.ppc_performance pp
  JOIN public.ppc p ON p.parent_id = pp.parent_id AND p.source = pp.source AND p.record_main_type='campaign'
  WHERE pp.source=1 AND pp.sub_source_id IN (6,8) AND pp.marketplace IN ('UK','Germany','France','Italy')
    AND pp.record_type='ad' AND pp.date BETWEEN %(start)s AND %(end)s
    AND p.record_subtype != 'SB'
  GROUP BY 1,2,3,4
),
sales_daily AS (
  SELECT order_date::date AS date, order_sub_source AS sub_source, market_place, asin,
    SUM(quantity) AS units_ordered, SUM(order_total) AS ordered_sales_revenue
  FROM public.order_transaction
  WHERE source_name='AMAZON' AND order_sub_source IN (6,8) AND market_place IN ('UK','Germany','France','Italy')
    AND order_status='Completed' AND order_date::date BETWEEN %(start)s AND %(end)s
  GROUP BY 1,2,3,4
),
traffic_daily_dedup AS (
  -- FIX (2026-07-20, v004): amz_traffic_by_asin carries one row per SKU
  -- variant of an ASIN, but Amazon attributes the SAME ASIN-level session
  -- count to every variant row (confirmed live: 1,183/1,191 duplicate
  -- (date,account,marketplace,asin) groups have IDENTICAL session/pageView/
  -- buyBox values, not partial splits). Summing across these rows (the v003
  -- bug) double/multi-counted. MAX() collapses same-day duplicates to the
  -- single true value before any cross-day summation.
  SELECT date, sub_source_id AS sub_source, market_place_name AS market_place, "childAsin" AS asin,
    MAX(sessions) AS sessions, MAX("pageViews") AS page_views,
    MAX("unitsOrdered") AS units_ordered_amz_report,
    MAX("buyBoxPercentage") AS buy_box_pct
  FROM public.amz_traffic_by_asin
  WHERE sub_source_id IN (6,8) AND market_place_name IN ('UK','Germany','France','Italy')
    AND date BETWEEN %(start)s AND %(end)s
  GROUP BY 1,2,3,4
),
traffic_daily AS (
  SELECT date, sub_source, market_place, asin,
    sessions, page_views, units_ordered_amz_report,
    (buy_box_pct * sessions) AS bb_weighted_num, sessions AS bb_weight_denom
  FROM traffic_daily_dedup
),
all_keys AS (
  SELECT date, sub_source, market_place, asin FROM ppc_daily
  UNION
  SELECT date, sub_source, market_place, asin FROM sales_daily
  UNION
  SELECT date, sub_source, market_place, asin FROM traffic_daily
)
SELECT k.date, k.sub_source, k.market_place, k.asin, b.resolved_sku,
  COALESCE(ppc.ppc_spend,0) AS ppc_spend, COALESCE(ppc.ppc_clicks,0) AS ppc_clicks,
  COALESCE(ppc.ppc_impressions,0) AS ppc_impressions, COALESCE(ppc.ppc_attributed_sales,0) AS ppc_attributed_sales,
  COALESCE(s.units_ordered,0) AS units_ordered, COALESCE(s.ordered_sales_revenue,0) AS ordered_sales_revenue,
  t.sessions, t.page_views, t.units_ordered_amz_report, t.bb_weighted_num, t.bb_weight_denom
FROM all_keys k
JOIN bridge b ON b.sub_source=k.sub_source AND b.market_place=k.market_place AND b.asin=k.asin
LEFT JOIN ppc_daily ppc ON ppc.date=k.date AND ppc.sub_source=k.sub_source AND ppc.market_place=k.market_place AND ppc.asin=k.asin
LEFT JOIN sales_daily s ON s.date=k.date AND s.sub_source=k.sub_source AND s.market_place=k.market_place AND s.asin=k.asin
LEFT JOIN traffic_daily t ON t.date=k.date AND t.sub_source=k.sub_source AND t.market_place=k.market_place AND t.asin=k.asin
ORDER BY k.date, k.sub_source, k.market_place, k.asin, b.resolved_sku
"""

ACCOUNT_NAME = {6: "DCVoltage", 8: "LEDSONE"}


def _json_default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, decimal.Decimal):
        return float(o)
    raise TypeError(f"Not JSON serializable: {type(o)}")


def extract_common_dataset(conn, start_date, end_date, output_path, checkpoint_path, batch_size=5000):
    """Streams the master aggregation query via a server-side cursor,
    writing each row as one JSON line. Returns summary stats. Never
    materializes the whole result set in memory at once."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    row_count = 0
    dup_check = set()
    duplicate_keys = 0
    null_key_count = 0

    with conn.cursor(name="anpia_common_dataset_cursor") as cur:
        cur.itersize = batch_size
        cur.execute(MASTER_SQL, {"start": start_date, "end": end_date})

        with open(output_path, "w", encoding="utf-8") as out_f:
            while True:
                batch = cur.fetchmany(batch_size)
                if not batch:
                    break
                for row in batch:
                    date_, sub_source, market_place, asin, resolved_sku = (
                        row[0], row[1], row[2], row[3], row[4]
                    )
                    key = (date_, sub_source, market_place, asin, resolved_sku)
                    if any(v is None for v in key):
                        null_key_count += 1
                    if key in dup_check:
                        duplicate_keys += 1
                    else:
                        dup_check.add(key)

                    record = {
                        "report_date": date_.isoformat() if hasattr(date_, "isoformat") else date_,
                        "account": ACCOUNT_NAME.get(sub_source, str(sub_source)),
                        "sub_source_id": sub_source,
                        "marketplace": market_place,
                        "asin": asin,
                        "resolved_sku": resolved_sku,
                        "ppc_spend": float(row[5]) if row[5] is not None else 0.0,
                        "ppc_clicks": int(row[6]) if row[6] is not None else 0,
                        "ppc_impressions": int(row[7]) if row[7] is not None else 0,
                        "ppc_attributed_sales": float(row[8]) if row[8] is not None else 0.0,
                        "units_ordered": int(row[9]) if row[9] is not None else 0,
                        "ordered_sales_revenue": float(row[10]) if row[10] is not None else 0.0,
                        "sessions": int(row[11]) if row[11] is not None else None,
                        "page_views": int(row[12]) if row[12] is not None else None,
                        "units_ordered_amz_report": int(row[13]) if row[13] is not None else None,
                        "bb_weighted_num": float(row[14]) if row[14] is not None else None,
                        "bb_weight_denom": float(row[15]) if row[15] is not None else None,
                    }
                    out_f.write(json.dumps(record, default=_json_default) + "\n")
                    row_count += 1

                with open(checkpoint_path, "w", encoding="utf-8") as ckpt_f:
                    json.dump({
                        "status": "IN_PROGRESS",
                        "rows_written_so_far": row_count,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    }, ckpt_f)

    summary = {
        "status": "COMPLETE",
        "row_count": row_count,
        "duplicate_keys": duplicate_keys,
        "null_key_count": null_key_count,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "output_path": output_path,
    }
    with open(checkpoint_path, "w", encoding="utf-8") as ckpt_f:
        json.dump(summary, ckpt_f, indent=2)
    return summary
