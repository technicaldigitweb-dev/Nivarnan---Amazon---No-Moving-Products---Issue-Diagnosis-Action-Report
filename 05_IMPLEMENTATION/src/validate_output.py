"""
validate_output.py -- REQ-AMZ-NMP-001-D01

Runs the checks listed in 06_VALIDATION/2026-07-17__sql_validation_report.md
against the transformed rows, the rendered HTML file, and (where supplied)
independent control totals from validation_checks.sql. Returns a dict of
check_name -> (PASS/FAIL, detail) rather than raising, so a caller can log a
full report even if some checks fail.
"""

import re

YELLOW_COLUMNS_FORBIDDEN = [
    "Category", "Stock Age (Days)", "Root Cause", "Recommended Action",
    "Priority", "Status", "Owner", "Last Reviewed",
]

REQUIRED_BLUE_COLUMN_SUBSTRINGS = [
    "Amazon ASIN", "Amazon SKU", "Product Title",
    "Days Since Last Sale in Amazon", "Units in Stock",
    "Sessions", "Page Views", "Units Ordered",
    "Conversion Rate (%)", "Click-Through Rate (%)", "Buy Box %",
    "Price (£)", "Category Avg Price (£)", "PPC Spend", "ACOS (%)",
]


def check_columns_present(rendered_html):
    results = {}
    for col in REQUIRED_BLUE_COLUMN_SUBSTRINGS:
        results[f"blue_column_present::{col}"] = ("PASS" if col in rendered_html else "FAIL", None)
    for col in YELLOW_COLUMNS_FORBIDDEN:
        # match as a table header token, not as a substring of an unrelated word
        found = re.search(rf">{re.escape(col)}<", rendered_html) is not None
        results[f"yellow_column_absent::{col}"] = ("FAIL" if found else "PASS", None)
    return results


def check_row_key_uniqueness(display_rows):
    seen = set()
    dupes = []
    for r in display_rows:
        key = (r.get("Account"), r.get("Marketplace"), r.get("Amazon ASIN"), r.get("Amazon SKU"))
        if key in seen:
            dupes.append(key)
        seen.add(key)
    return {"row_key_uniqueness": ("PASS" if not dupes else "FAIL", dupes[:10])}


def check_no_amzn_gr_alias(display_rows):
    bad = [r["Amazon SKU"] for r in display_rows if str(r.get("Amazon SKU", "")).startswith("amzn.gr.")]
    return {"no_amzn_gr_alias_in_sku": ("PASS" if not bad else "FAIL", bad[:10])}


def check_reconciliation(summary_totals, control_totals, tolerance=0.01):
    results = {}
    for key, control_value in control_totals.items():
        report_value = summary_totals.get(key)
        if report_value is None:
            results[f"reconciliation::{key}"] = ("FAIL", "key missing from summary_totals")
            continue
        diff = abs(report_value - control_value)
        ok = diff <= max(tolerance, abs(control_value) * 0.0001)
        results[f"reconciliation::{key}"] = (
            "PASS" if ok else "FAIL",
            f"report={report_value} control={control_value} diff={diff}",
        )
    return results


def check_credentials_absent(rendered_html):
    suspicious_patterns = [
        r"password\s*=", r"PGPASSWORD", r"postgres(?:ql)?://[^/\s]+:[^/\s]+@",
        r"secret", r"api[_-]?key",
    ]
    found = [p for p in suspicious_patterns if re.search(p, rendered_html, re.IGNORECASE)]
    return {"no_credentials_in_output": ("PASS" if not found else "FAIL", found)}


def run_all_checks(display_rows, summary_totals, rendered_html_path, control_totals=None):
    with open(rendered_html_path, "r", encoding="utf-8") as f:
        rendered_html = f.read()

    results = {}
    results.update(check_columns_present(rendered_html))
    results.update(check_row_key_uniqueness(display_rows))
    results.update(check_no_amzn_gr_alias(display_rows))
    results.update(check_credentials_absent(rendered_html))
    if control_totals:
        results.update(check_reconciliation(summary_totals, control_totals))

    overall = "PASS" if all(v[0] == "PASS" for v in results.values()) else "FAIL"
    return overall, results
