"""
run_report.py -- REQ-AMZ-NMP-001-D01 orchestrator.

Production mode: loads config, opens a real database connection (db_connection.py),
executes sql/main_report.sql for the requested period, transforms, renders,
validates, and (only if explicitly instructed and DEC-TECH-001 is approved)
publishes.

This-session mode: this Claude agent has no local database credentials
(by design -- Sources/db_access_templates/ is restricted and was not opened).
Report data for the actual 2026-07-17 v001 HTML was instead fetched via the
pre-authorized PRIMARY_SKILLS_MCP tool connection and saved to a local JSON
file; this script's --from-json mode reads that file so the exact same
transform/render/validate code path is used regardless of how the raw rows
were obtained.

Usage (production):
    python run_report.py --period 30 --start-date 2026-06-16 --end-date 2026-07-15

Usage (this session, using MCP-fetched data):
    python run_report.py --from-json raw_rows.json --period 30 \\
        --start-date 2026-06-16 --end-date 2026-07-15 --sample-note "..."
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import data_transform
import html_renderer
import validate_output


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "report_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_from_db(period_days, start_date, end_date):
    import db_connection  # only imported here -- not needed in --from-json mode
    conn = db_connection.get_connection()
    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "main_report.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_text = f.read()
    with conn.cursor() as cur:
        cur.execute(sql_text, {"start_date": start_date, "end_date": end_date, "period_days": period_days})
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, required=True, choices=[7, 14, 30])
    ap.add_argument("--start-date", required=True)
    ap.add_argument("--end-date", required=True)
    ap.add_argument("--from-json", help="Path to a JSON file of pre-fetched raw rows (this-session mode)")
    ap.add_argument("--sample-note", default=None)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    config = load_config()

    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            raw_rows = json.load(f)
        data_source_note = (
            "PRIMARY_SKILLS_MCP (mcp__claude_ai_postgres__*), fetched by the implementing "
            "agent this session and saved locally -- see 07_EVIDENCE/output/2026-07-17__report_generation_evidence.md"
        )
    else:
        raw_rows = fetch_from_db(args.period, args.start_date, args.end_date)
        data_source_note = "PRIMARY_SKILLS_MCP (live database connection at run time)"

    display_rows, summary_totals = data_transform.transform_rows(
        raw_rows, args.period, config["missing_data_placeholder"]
    )

    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "amazon_no_moving_report_template.html")
    account_labels = [a["label"] for a in config["accounts"]]

    out_path = html_renderer.render_html(
        template_path=template_path,
        output_path=args.output,
        display_rows=display_rows,
        summary_totals=summary_totals,
        period_days=args.period,
        accounts=account_labels,
        marketplaces=config["marketplaces"],
        start_date=args.start_date,
        end_date=args.end_date,
        generation_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        data_source_note=data_source_note,
        sample_note=args.sample_note,
    )

    overall, results = validate_output.run_all_checks(display_rows, summary_totals, out_path)
    print(f"Rendered: {out_path}")
    print(f"Validation overall: {overall}")
    for k, v in results.items():
        if v[0] == "FAIL":
            print(f"  FAIL: {k} -> {v[1]}")

    # ph_task publication is NEVER attempted from this orchestrator automatically.
    # publish_to_ph_task.publish() must be called explicitly, separately, only
    # after DEC-TECH-001 is approved.


if __name__ == "__main__":
    main()
