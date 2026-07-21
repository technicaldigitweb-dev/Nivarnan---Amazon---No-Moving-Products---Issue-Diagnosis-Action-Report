"""
run_report_v002.py -- REQ-AMZ-NMP-001-D01, v002 orchestrator.

Builds the multi-period (7/14/30-day) HTML report from three INDEPENDENTLY
fetched raw-row JSON files (one per period -- each its own live query result,
never derived by slicing another period's data), per the user's rejection of
v001 (period switching did not actually change data) and the requirement that
Sessions/Page Views/Units Ordered/PPC Spend/ACOS/CTR each have their own
period-specific figures.

This-session mode only (see db_connection.py / run_report.py docstring for
why: no database credentials are available to this agent in this
environment -- confirmed by direct inspection of Sources/db_access_templates/,
which is fully remediated with no embedded secrets, and no PGHOST/PGUSER/etc.
environment variables are set).

Usage:
    python run_report_v002.py \\
        --json-7 raw_rows_7d.json --start-7 2026-07-09 --end-7 2026-07-15 \\
        --json-14 raw_rows_14d.json --start-14 2026-07-02 --end-14 2026-07-15 \\
        --json-30 raw_rows_30d.json --start-30 2026-06-16 --end-30 2026-07-15 \\
        --default-period 30 \\
        --output ../../09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v002.html
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import data_transform
import html_renderer


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "report_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    for p in (7, 14, 30):
        ap.add_argument(f"--json-{p}", required=True)
        ap.add_argument(f"--start-{p}", required=True)
        ap.add_argument(f"--end-{p}", required=True)
    ap.add_argument("--default-period", type=int, default=30, choices=[7, 14, 30])
    ap.add_argument("--latest-complete-date", required=True)
    ap.add_argument("--sample-note", default=None)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    config = load_config()
    account_labels = [a["label"] for a in config["accounts"]]

    period_display_rows = {}
    period_ranges = {}
    all_summaries = {}

    for p in (7, 14, 30):
        json_path = getattr(args, f"json_{p}")
        start = getattr(args, f"start_{p}")
        end = getattr(args, f"end_{p}")
        with open(json_path, "r", encoding="utf-8") as f:
            raw_rows = json.load(f)
        display_rows, summary_totals = data_transform.transform_rows(
            raw_rows, p, config["missing_data_placeholder"]
        )
        period_display_rows[str(p)] = display_rows
        period_ranges[str(p)] = {"start": start, "end": end}
        all_summaries[str(p)] = summary_totals
        print(f"period {p}d: {len(display_rows)} rows, summary={summary_totals}")

    template_path = os.path.join(
        os.path.dirname(__file__), "..", "templates", "amazon_no_moving_report_template_v002.html"
    )

    out_path = html_renderer.render_html_v002(
        template_path=template_path,
        output_path=args.output,
        period_display_rows=period_display_rows,
        period_ranges=period_ranges,
        default_period=args.default_period,
        accounts=account_labels,
        marketplaces=config["marketplaces"],
        latest_complete_date=args.latest_complete_date,
        generation_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        data_source_note=(
            "PRIMARY_SKILLS_MCP (mcp__claude_ai_postgres__*) -- three independent "
            "live queries, one per period, fetched by the implementing agent this "
            "session. See 07_EVIDENCE/output/2026-07-17__report_generation_evidence_v002.md."
        ),
        sample_note=args.sample_note,
    )
    print(f"Rendered: {out_path}")

    # Write a machine-readable summary alongside for the validation step.
    summary_path = os.path.join(os.path.dirname(args.output), "..", "logs", "2026-07-17__v002_summary_totals.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)
    print(f"Summary totals written: {summary_path}")


if __name__ == "__main__":
    main()
