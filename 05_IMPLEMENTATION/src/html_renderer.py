"""
html_renderer.py -- REQ-AMZ-NMP-001-D01

Renders the report template (05_IMPLEMENTATION/templates/amazon_no_moving_report_template.html)
using plain string substitution (no Jinja2 dependency -- not installed in this
environment) and embedded JSON for client-side search/sort/pagination, per
04_DESIGN section on period logic and the "efficient rendering for large
datasets" requirement.
"""

import json
import html as html_lib


COLUMN_ORDER_TEMPLATE = [
    "Account",
    "Marketplace",
    "Amazon ASIN",
    "Amazon SKU",
    "Product Title",
    "Days Since Last Sale in Amazon",
    "Units in Stock",
    "Sessions ({p}d)",
    "Page Views ({p}d)",
    "Units Ordered ({p}d)",
    "Conversion Rate (%)",
    "Click-Through Rate (%)",
    "Buy Box %",
    "Price (£)",
    "Category Avg Price (£)",
    "PPC Spend ({p}d)",
    "ACOS (%)",
]

YELLOW_COLUMNS_FORBIDDEN = [
    "Category", "Stock Age (Days)", "Root Cause", "Recommended Action",
    "Priority", "Status", "Owner", "Last Reviewed",
]


def render_html(template_path, output_path, display_rows, summary_totals,
                 period_days, accounts, marketplaces, start_date, end_date,
                 generation_timestamp, data_source_note, sample_note=None):
    columns = [c.format(p=period_days) for c in COLUMN_ORDER_TEMPLATE]

    # Hard safety check: never allow a yellow column into the rendered output.
    for row in display_rows:
        for forbidden in YELLOW_COLUMNS_FORBIDDEN:
            assert forbidden not in row, (
                f"Yellow column '{forbidden}' found in a display row -- refusing to render."
            )

    with open(template_path, "r", encoding="utf-8") as f:
        tpl = f.read()

    account_options = "".join(f'<option value="{html_lib.escape(a)}">{html_lib.escape(a)}</option>' for a in accounts)
    marketplace_options = "".join(f'<option value="{html_lib.escape(m)}">{html_lib.escape(m)}</option>' for m in marketplaces)
    period_options = "".join(
        f'<option value="{p}"{" selected" if p == period_days else ""}>{p} days</option>'
        for p in (7, 14, 30)
    )
    table_headers = "".join(f"<th>{html_lib.escape(c)}</th>" for c in columns)

    summary_cards_html = "".join(
        f'<div class="card">{html_lib.escape(str(k))}<b>{html_lib.escape(str(v))}</b></div>'
        for k, v in summary_totals.items()
    )

    sample_block = ""
    if sample_note:
        sample_block = f'<div class="sample-note">{html_lib.escape(sample_note)}</div>'

    out = (
        tpl
        .replace("__REPORT_TITLE__", "Amazon No-Moving Products - Issue Diagnosis &amp; Action Report")
        .replace("__GENERATION_TIMESTAMP__", generation_timestamp)
        .replace("__DATA_SOURCE_NOTE__", html_lib.escape(data_source_note))
        .replace("__PERIOD_WINDOW_NOTE__", f"{period_days}-day window: {start_date} to {end_date}")
        .replace("__SAMPLE_NOTE_BLOCK__", sample_block)
        .replace("__SUMMARY_CARDS__", summary_cards_html)
        .replace("__ACCOUNT_OPTIONS__", account_options)
        .replace("__MARKETPLACE_OPTIONS__", marketplace_options)
        .replace("__PERIOD_OPTIONS__", period_options)
        .replace("__TABLE_HEADERS__", table_headers)
        .replace("__TABLE_ROWS__", "")  # rows are rendered client-side from ROW_DATA_JSON
        .replace("__ROW_DATA_JSON__", json.dumps(display_rows))
        .replace("__COLUMN_LIST_JSON__", json.dumps(columns))
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out)

    return output_path


def render_html_v002(template_path, output_path, period_display_rows, period_ranges,
                      default_period, accounts, marketplaces,
                      latest_complete_date, generation_timestamp, data_source_note,
                      sample_note=None):
    """
    period_display_rows: dict like {"7": [...], "14": [...], "30": [...]} --
        each value is the list of transformed display-row dicts for that
        period, produced INDEPENDENTLY (own SQL run, own transform call) --
        never derived by slicing another period's rows.
    period_ranges: dict like {"7": {"start": "...", "end": "..."}, ...}
    """
    for period, rows in period_display_rows.items():
        for row in rows:
            for forbidden in YELLOW_COLUMNS_FORBIDDEN:
                assert forbidden not in row, (
                    f"Yellow column '{forbidden}' found in period {period} display row -- refusing to render."
                )
            for internal_key in ("_ppc_spend_raw", "_units_ordered_raw", "_stock_raw"):
                row.pop(internal_key, None)  # strip internal helper keys before embedding client-side

    with open(template_path, "r", encoding="utf-8") as f:
        tpl = f.read()

    account_options = "".join(f'<option value="{html_lib.escape(a)}">{html_lib.escape(a)}</option>' for a in accounts)
    marketplace_options = "".join(f'<option value="{html_lib.escape(m)}">{html_lib.escape(m)}</option>' for m in marketplaces)
    period_options = "".join(
        f'<option value="{p}"{" selected" if int(p) == default_period else ""}>{p} days</option>'
        for p in period_display_rows.keys()
    )

    sample_block = f'<div class="sample-note">{html_lib.escape(sample_note)}</div>' if sample_note else ""

    out = (
        tpl
        .replace("__REPORT_TITLE__", "Amazon No-Moving Products - Issue Diagnosis &amp; Action Report")
        .replace("__GENERATION_TIMESTAMP__", generation_timestamp)
        .replace("__GENERATION_DATE__", generation_timestamp[:10])
        .replace("__LATEST_COMPLETE_DATE__", latest_complete_date)
        .replace("__DATA_SOURCE_NOTE__", html_lib.escape(data_source_note))
        .replace("__SAMPLE_NOTE_BLOCK__", sample_block)
        .replace("__ACCOUNT_OPTIONS__", account_options)
        .replace("__MARKETPLACE_OPTIONS__", marketplace_options)
        .replace("__PERIOD_OPTIONS__", period_options)
        .replace("__DATASETS_JSON__", json.dumps(period_display_rows))
        .replace("__PERIOD_RANGES_JSON__", json.dumps(period_ranges))
        .replace("__DEFAULT_PERIOD__", str(default_period))
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(out)

    return output_path
