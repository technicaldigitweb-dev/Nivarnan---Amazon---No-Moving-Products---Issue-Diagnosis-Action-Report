"""
anpia_source_discovery.py -- REQ-ANPIA-REQ-01-D02

Small, bounded metadata/discovery queries used to resolve the live
parameters the common-dataset extraction needs (latest complete date,
approved account/marketplace scope). Not used for bulk extraction.
"""

import datetime

from anpia_db_connection import run_query

APPROVED_ACCOUNTS = {6: "DCVoltage", 8: "LEDSONE"}
APPROVED_MARKETPLACES = ["UK", "Germany", "France", "Italy"]


def latest_complete_date(conn):
    """Latest complete date = yesterday relative to the source's own current
    date, driven by order_transaction (the primary sales source, confirmed
    live/current), excluding the still-accruing current day."""
    row = run_query(conn, "SELECT CURRENT_DATE AS today")[0]
    return row["today"] - datetime.timedelta(days=1)
