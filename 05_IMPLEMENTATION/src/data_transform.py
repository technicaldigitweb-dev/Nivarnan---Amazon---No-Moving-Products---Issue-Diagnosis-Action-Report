"""
data_transform.py -- REQ-AMZ-NMP-001-D01

Transforms raw report rows (as produced by 05_IMPLEMENTATION/sql/main_report.sql,
one dict per row) into display-ready rows plus deduplicated summary totals,
per 04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md
sections D (repeated metrics) and G (missing data).

No formula is invented here for the REVIEW_REQUIRED fields (Sessions, Page
Views, Buy Box %, Conversion Rate, Click-Through Rate, Category Avg Price) --
they are always rendered as config["missing_data_placeholder"].
"""

REVIEW_REQUIRED_COLUMNS = [
    "Sessions",
    "Page Views",
    "Conversion Rate (%)",
    "Click-Through Rate (%)",
    "Buy Box %",
    "Category Avg Price (£)",
]


def _fmt_money(value):
    if value is None:
        return "N/A"
    return f"£{value:,.2f}"


def _fmt_pct(value):
    if value is None:
        return "N/A (no attributed sales)"
    return f"{value:.2f}%"


def transform_rows(raw_rows, period_days, missing_data_placeholder):
    """
    raw_rows: list of dicts with keys matching main_report.sql's SELECT list:
        account, marketplace, asin, resolved_sku, product_title, price, currency,
        last_sale_date, days_since_last_sale, stock_qty, stock_updated_at,
        units_ordered, ppc_spend, acos_pct
    Returns (display_rows, summary_totals).
    """
    display_rows = []
    for r in raw_rows:
        row = {
            "Account": r.get("account"),
            "Marketplace": r.get("marketplace"),
            "Amazon ASIN": r.get("asin"),
            "Amazon SKU": r.get("resolved_sku") or "No mapping",
            "Product Title": r.get("product_title") or "Not available",
            "Days Since Last Sale in Amazon": (
                "No sale on record"
                if r.get("days_since_last_sale") is None
                else int(r["days_since_last_sale"])
            ),
            "Units in Stock": (
                "No current stock record"
                if r.get("stock_qty") is None
                else int(r["stock_qty"])
            ),
            f"Sessions ({period_days}d)": missing_data_placeholder,
            f"Page Views ({period_days}d)": missing_data_placeholder,
            f"Units Ordered ({period_days}d)": int(r.get("units_ordered") or 0),
            "Conversion Rate (%)": missing_data_placeholder,
            "Click-Through Rate (%)": missing_data_placeholder,
            "Buy Box %": missing_data_placeholder,
            "Price (£)": _fmt_money(r.get("price")),
            "Category Avg Price (£)": missing_data_placeholder,
            f"PPC Spend ({period_days}d)": _fmt_money(r.get("ppc_spend")),
            "ACOS (%)": _fmt_pct(r.get("acos_pct")),
            # internal, not displayed as a column but used for validation/dedup:
            "_ppc_spend_raw": r.get("ppc_spend") or 0,
            "_units_ordered_raw": r.get("units_ordered") or 0,
            "_stock_raw": r.get("stock_qty"),
        }
        display_rows.append(row)

    # Summary totals MUST be computed at account+marketplace+ASIN grain (deduplicated),
    # never by summing the visible per-row (per-SKU) values, because PPC Spend/
    # Units Ordered/ACOS repeat identically across a multi-SKU ASIN's rows.
    asin_grain_seen = {}
    for r in raw_rows:
        key = (r.get("account"), r.get("marketplace"), r.get("asin"))
        if key not in asin_grain_seen:
            asin_grain_seen[key] = {
                "ppc_spend": r.get("ppc_spend") or 0,
                "units_ordered": r.get("units_ordered") or 0,
            }

    summary_totals = {
        "total_asin_marketplace_account_combinations": len(asin_grain_seen),
        "total_display_rows": len(display_rows),
        f"total_ppc_spend_{period_days}d": round(
            sum(v["ppc_spend"] for v in asin_grain_seen.values()), 2
        ),
        f"total_units_ordered_{period_days}d": sum(
            v["units_ordered"] for v in asin_grain_seen.values()
        ),
    }

    return display_rows, summary_totals
