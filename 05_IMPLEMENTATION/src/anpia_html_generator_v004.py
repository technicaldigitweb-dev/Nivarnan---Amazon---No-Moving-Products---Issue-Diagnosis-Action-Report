"""
anpia_html_generator_v004.py -- REQ-ANPIA-REQ-01-D02 v004 fix

Renders v004 HTML using the v004 template (new CSS-variable-based frozen
columns, grouped column order, data-quality panel, formula notes). Row
values from the v2 period-report JSONL are already precisely classified
(a real number, a confirmed 0, or one of the specific N/A reason strings)
-- this module only formats currency/percentage display, it does not
invent or override any classification decided upstream.
"""

import json

NO_SALE = "No sale on record"
NO_STOCK = "No current stock record"
PRICE_NA = "N/A — source not available"


def _passthrough_or_na(v, default_na=PRICE_NA):
    return v if v is not None else default_na


def row_to_display(r, period_days):
    return {
        "Account": r["account"],
        "Marketplace": r["marketplace"],
        "Amazon ASIN": r["asin"],
        "Amazon SKU": r["sku"],
        "Product Title": r["product_title"] if r["product_title"] else PRICE_NA,
        "Days Since Last Sale in Amazon": r["days_since_last_sale"] if r["days_since_last_sale"] is not None else NO_SALE,
        "Units in Stock": r["units_in_stock"] if r["units_in_stock"] is not None else NO_STOCK,
        f"Sessions ({period_days}d)": r["sessions"],
        f"Page Views ({period_days}d)": r["page_views"],
        "Buy Box %": r["buy_box_percentage"],
        f"Units Ordered ({period_days}d)": r["units_ordered"],
        "Conversion Rate (%)": _passthrough_or_na(r["conversion_rate"]),
        f"PPC Spend ({period_days}d)": r["ppc_spend"],
        "Click-Through Rate (%)": _passthrough_or_na(r["click_through_rate"]),
        "ACOS (%)": _passthrough_or_na(r["acos"]),
        "Price (£)": _passthrough_or_na(r["price"]),
        "Category Avg Price (£)": _passthrough_or_na(r["category_avg_price"]),
    }


def build_html(template_text, period_jsonl_paths, period_ranges, coverage_stats,
               generation_timestamp, generation_date, latest_complete_date,
               formula_notes_html, default_period="30"):
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
    html = html.replace("__REPORT_TITLE__", "Amazon No-Moving Products Report -- LEDSONE &amp; DCVoltage (v004)")
    html = html.replace("__GENERATION_TIMESTAMP__", generation_timestamp)
    html = html.replace("__LATEST_COMPLETE_DATE__", latest_complete_date)
    html = html.replace("__DATA_SOURCE_NOTE__", "Direct PostgreSQL (ANPIA_DB_*), corrected common daily dataset, REQ-01-D02 v004")
    html = html.replace("__ACCOUNT_OPTIONS__", account_options)
    html = html.replace("__MARKETPLACE_OPTIONS__", marketplace_options)
    html = html.replace("__PERIOD_OPTIONS__", period_options)
    html = html.replace("__DATASETS_JSON__", json.dumps(datasets))
    html = html.replace("__PERIOD_RANGES_JSON__", json.dumps(period_ranges))
    html = html.replace("__COVERAGE_STATS_JSON__", json.dumps(coverage_stats))
    html = html.replace("__DEFAULT_PERIOD__", f'"{default_period}"')
    html = html.replace("__GENERATION_DATE__", generation_date)
    html = html.replace("__FORMULA_NOTES_HTML__", formula_notes_html)
    return html
