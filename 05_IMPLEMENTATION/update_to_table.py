"""
update_to_table.py -- REQ-ANPIA-REQ-01-D02

Manual command-entry wrapper for the operator phrase "update to table" (an
operator instruction to Claude Code for this project, NOT an unauthenticated
database endpoint, NOT a natural-language interpreter, and NOT reachable by
any external or public input). This script accepts no free-form text --
it takes exactly the fixed CLI flags below and passes a fixed, hardcoded
set of arguments through to `anpia_daily_pipeline.py`. There is no code
path in this file that parses, evaluates, or otherwise interprets
arbitrary text as instructions.

What it does:
  1. Resolves today's date in Asia/Colombo (never relies on the host
     machine's local timezone).
  2. Calls anpia_daily_pipeline.py in manual trigger mode, letting the
     pipeline itself decide (via its own live duplicate-state check)
     whether this is the first daily publication or an update to an
     existing same-day row.
  3. Requires the same --confirmation-token as the underlying pipeline to
     actually publish -- default behavior (no --confirm) is a dry-run.
  4. Prints a concise publication result.

Usage:
  python update_to_table.py --dry-run
  python update_to_table.py --confirm --confirmation-token PUBLISH_NIVARNAN_ANPIA

This module performs NO action at import time -- everything runs under
`if __name__ == "__main__": main()`.
"""

import argparse
import datetime
import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "anpia_daily_pipeline.py")
TZ_OFFSET = datetime.timezone(datetime.timedelta(hours=5, minutes=30))  # Asia/Colombo, no DST
CONFIRM_TOKEN = "PUBLISH_NIVARNAN_ANPIA"


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Fixed-behavior wrapper for the 'update to table' operator command. "
                     "Takes no free-form text input."
    )
    p.add_argument("--confirm", action="store_true",
                    help="Required (with --confirmation-token) to actually publish. Default is dry-run.")
    p.add_argument("--confirmation-token", default=None)
    return p.parse_args(argv)


def resolve_today_colombo():
    return datetime.datetime.now(TZ_OFFSET).date()


def main():
    args = parse_args()
    report_date = resolve_today_colombo()

    print("=" * 70)
    print("update_to_table -- ANPIA manual publication command")
    print("=" * 70)
    print(f"Resolved report date (Asia/Colombo): {report_date.isoformat()}")

    pipeline_args = [
        sys.executable, PIPELINE_PATH,
        "--report-date", report_date.isoformat(),
        "--trigger-source", "command",
    ]

    if args.confirm:
        if args.confirmation_token != CONFIRM_TOKEN:
            print("SAFETY GATE FAILED: --confirm was supplied without the correct --confirmation-token.")
            print("PUBLICATION RESULT: NOT ATTEMPTED")
            sys.exit(2)
        pipeline_args += ["--publish", "--confirmation-token", args.confirmation_token]
        print("Mode: PUBLISH (the underlying pipeline will still re-verify every safety gate live)")
    else:
        pipeline_args += ["--dry-run"]
        print("Mode: DRY-RUN (default -- pass --confirm --confirmation-token PUBLISH_NIVARNAN_ANPIA to publish)")

    print(f"\nInvoking: {' '.join(pipeline_args)}\n")
    result = subprocess.run(pipeline_args, cwd=PROJECT_ROOT)

    print("\n" + "=" * 70)
    print(f"PUBLICATION RESULT: {'SEE PIPELINE OUTPUT ABOVE'}")
    print(f"PIPELINE EXIT CODE: {result.returncode}")
    print("=" * 70)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
