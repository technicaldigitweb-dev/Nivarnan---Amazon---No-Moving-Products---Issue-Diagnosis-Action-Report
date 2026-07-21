"""
anpia_html_generator.py -- REQ-ANPIA-REQ-01-D02

Renders the v003 HTML from the three period JSONL files (7d/14d/30d),
using the existing, already-validated v002 template's client-side logic
unchanged (period switching, filters, sort, pagination, CSV export). Only
the embedded DATASETS/PERIOD_RANGES and the row-formatting rules are new.
"""

import json

NA = "N/A - source not available"
NO_SALE = "No sale on record"
NO_STOCK = "No current stock record"


def _fmt_int_or_na(v):
    return v if v is not None else NA


def _fmt_money(v):
    if v is None:
        return NA
    return f"£{v:,.2f}"


def _fmt_pct(v):
    if v is None:
        return NA
    return f"{v:.2f}%"


def row_to_display(r, period_days):
    return {
        "Account": r["account"],
        "Marketplace": r["marketplace"],
        "Amazon ASIN": r["asin"],
        "Amazon SKU": r["sku"],
        "Product Title": r["product_title"] if r["product_title"] else NA,
        "Days Since Last Sale in Amazon": r["days_since_last_sale"] if r["days_since_last_sale"] is not None else NO_SALE,
        "Units in Stock": r["units_in_stock"] if r["units_in_stock"] is not None else NO_STOCK,
        f"Sessions ({period_days}d)": _fmt_int_or_na(r["sessions"]),
        f"Page Views ({period_days}d)": _fmt_int_or_na(r["page_views"]),
        f"Units Ordered ({period_days}d)": r["units_ordered"],
        "Conversion Rate (%)": _fmt_pct(r["conversion_rate"]),
        "Click-Through Rate (%)": _fmt_pct(r["click_through_rate"]),
        "Buy Box %": _fmt_pct(r["buy_box_percentage"]),
        "Price (£)": _fmt_money(r["price"]),
        "Category Avg Price (£)": _fmt_money(r["category_avg_price"]),
        f"PPC Spend ({period_days}d)": _fmt_money(r["ppc_spend"]).replace("£", ""),
        "ACOS (%)": _fmt_pct(r["acos"]),
    }


def build_html(template_text, period_jsonl_paths, period_ranges, generation_timestamp, generation_date, latest_complete_date, default_period="30"):
    datasets = {}
    accounts = set()
    marketplaces = set()

    for period, path in period_jsonl_paths.items():
        rows_display = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                rows_display.append(row_to_display(r, period))
                accounts.add(r["account"])
                marketplaces.add(r["marketplace"])
        datasets[period] = rows_display

    account_options = "".join(f'<option value="{a}">{a}</option>' for a in sorted(accounts))
    marketplace_options = "".join(f'<option value="{m}">{m}</option>' for m in sorted(marketplaces))
    period_options = "".join(
        f'<option value="{p}"{" selected" if p == default_period else ""}>{p} days</option>'
        for p in ["7", "14", "30"]
    )

    html = template_text
    html = html.replace("__REPORT_TITLE__", "Amazon No-Moving Products Report -- LEDSONE &amp; DCVoltage")
    html = html.replace("__GENERATION_TIMESTAMP__", generation_timestamp)
    html = html.replace("__LATEST_COMPLETE_DATE__", latest_complete_date)
    html = html.replace("__DATA_SOURCE_NOTE__", "Direct PostgreSQL (ANPIA_DB_*), common daily dataset, REQ-01-D02")
    html = html.replace("__SAMPLE_NOTE_BLOCK__", "")
    html = html.replace("__ACCOUNT_OPTIONS__", account_options)
    html = html.replace("__MARKETPLACE_OPTIONS__", marketplace_options)
    html = html.replace("__PERIOD_OPTIONS__", period_options)
    html = html.replace("__DATASETS_JSON__", json.dumps(datasets))
    html = html.replace("__PERIOD_RANGES_JSON__", json.dumps(period_ranges))
    html = html.replace("__DEFAULT_PERIOD__", f'"{default_period}"')
    html = html.replace("__GENERATION_DATE__", generation_date)
    return html
