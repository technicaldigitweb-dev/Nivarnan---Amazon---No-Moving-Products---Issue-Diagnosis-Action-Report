"""
anpia_period_aggregation.py -- REQ-ANPIA-REQ-01-D02

Derives the 7-, 14-, and 30-day report views from the single common daily
dataset (one file, one extraction) by filtering and summing -- never by
independently re-extracting per period, and never by deriving 7/14-day
values from an already-aggregated 30-day row.
"""

import datetime
import json


def _new_bucket():
    return {
        "ppc_spend": 0.0, "ppc_clicks": 0, "ppc_impressions": 0, "ppc_attributed_sales": 0.0,
        "units_ordered": 0, "ordered_sales_revenue": 0.0,
        "sessions": 0, "page_views": 0, "bb_weighted_num": 0.0, "bb_weight_denom": 0.0,
        "has_traffic_data": False,
        "days_present": 0,
    }


def aggregate_periods(common_dataset_path, end_date):
    """Single pass over the common daily JSONL. Returns three dicts (7d,
    14d, 30d), each keyed by (account, marketplace, asin, resolved_sku),
    with additive totals only -- derived ratios are computed by the
    caller after this function returns, from these summed totals."""
    windows = {
        "7d": end_date - datetime.timedelta(days=6),
        "14d": end_date - datetime.timedelta(days=13),
        "30d": end_date - datetime.timedelta(days=29),
    }
    results = {"7d": {}, "14d": {}, "30d": {}}

    with open(common_dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            report_date = datetime.date.fromisoformat(rec["report_date"])
            key = (rec["account"], rec["marketplace"], rec["asin"], rec["resolved_sku"])

            for period, window_start in windows.items():
                if report_date < window_start or report_date > end_date:
                    continue
                bucket = results[period].setdefault(key, _new_bucket())
                bucket["ppc_spend"] += rec["ppc_spend"]
                bucket["ppc_clicks"] += rec["ppc_clicks"]
                bucket["ppc_impressions"] += rec["ppc_impressions"]
                bucket["ppc_attributed_sales"] += rec["ppc_attributed_sales"]
                bucket["units_ordered"] += rec["units_ordered"]
                bucket["ordered_sales_revenue"] += rec["ordered_sales_revenue"]
                if rec["sessions"] is not None:
                    bucket["sessions"] += rec["sessions"]
                    bucket["has_traffic_data"] = True
                if rec["page_views"] is not None:
                    bucket["page_views"] += rec["page_views"]
                if rec["bb_weighted_num"] is not None:
                    bucket["bb_weighted_num"] += rec["bb_weighted_num"]
                if rec["bb_weight_denom"] is not None:
                    bucket["bb_weight_denom"] += rec["bb_weight_denom"]
                bucket["days_present"] += 1

    return results, windows


def derive_ratios(bucket):
    """Recalculates all derived ratios from period-summed base totals.
    Never averages daily percentages. Safe zero-denominator handling."""
    sessions = bucket["sessions"]
    impressions = bucket["ppc_impressions"]
    attributed_sales = bucket["ppc_attributed_sales"]
    bb_denom = bucket["bb_weight_denom"]

    conversion_rate = (bucket["units_ordered"] / sessions * 100) if sessions else None
    ctr = (bucket["ppc_clicks"] / impressions * 100) if impressions else None
    acos = (bucket["ppc_spend"] / attributed_sales * 100) if attributed_sales else None
    # FIX (2026-07-20, v004): amz_traffic_by_asin.buyBoxPercentage is already
    # on a 0-100 scale (confirmed live: MIN=0.0, MAX=100.0, sample values of
    # 100.0 meaning 100%) -- bb_weighted_num = buyBoxPercentage * sessions
    # already carries that scale, so dividing by bb_denom (session-weighted
    # average) requires NO further *100. The original *100 here double-
    # applied the percentage conversion, producing values up to 10000.0
    # (e.g. a true 100% Buy Box rendered as 10000.0) -- found via the
    # formula-trace evidence gathering for this exact fix task.
    buy_box_pct = (bucket["bb_weighted_num"] / bb_denom) if bb_denom else None

    return {
        "conversion_rate": conversion_rate,
        "click_through_rate": ctr,
        "acos": acos,
        "buy_box_percentage": buy_box_pct,
    }
