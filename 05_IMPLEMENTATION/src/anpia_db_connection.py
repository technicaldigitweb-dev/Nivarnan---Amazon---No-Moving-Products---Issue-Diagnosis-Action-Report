"""
anpia_db_connection.py -- REQ-ANPIA-REQ-01-D02

Direct PostgreSQL connection helper for the ANPIA rebuild. Credentials are
loaded exclusively via anpia_config.get_db_config() (.env/environment only,
no hardcoded fallback). Connection errors are redacted before being raised
further. Extraction (this module + anpia_source_discovery.py /
anpia_common_dataset.py) is kept strictly separate from any future
publication code -- no ph_task write path exists anywhere in this module.
"""

import psycopg2
import psycopg2.extras

from anpia_config import get_db_config


def _redact(exc: Exception, password: str) -> str:
    text = str(exc)
    if password:
        text = text.replace(password, "***REDACTED***")
    return text


def get_connection():
    """Returns a psycopg2 connection. Never logs the config dict. Redacts
    the password from any connection-error text before re-raising."""
    cfg = get_db_config()
    try:
        conn = psycopg2.connect(**cfg)
        conn.set_session(readonly=True, autocommit=False)
        return conn
    except psycopg2.OperationalError as exc:
        raise RuntimeError(f"Could not connect to ANPIA database: {_redact(exc, cfg['password'])}") from exc


def server_side_cursor(conn, name="anpia_cursor", batch_size=2000):
    """Named (server-side) read-only cursor for large result sets -- caller
    must iterate with cursor.fetchmany(batch_size), never .fetchall()."""
    cur = conn.cursor(name=name, cursor_factory=psycopg2.extras.RealDictCursor)
    cur.itersize = batch_size
    return cur


def run_scalar(conn, sql, params=None):
    """Runs a single bounded query and returns the first column of the
    first row. Uses an ordinary (non-server-side) cursor -- only for small,
    bounded metadata/validation queries, never bulk extraction."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else None


def run_query(conn, sql, params=None):
    """Runs a single bounded query and returns all rows as a list of dicts.
    Only for small, bounded metadata/aggregate queries -- never for raw
    fact-table bulk extraction (use server_side_cursor for that)."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def safe_close(conn, cur=None):
    """Rolls back any open transaction and closes cursor/connection safely.
    Never raises."""
    try:
        if cur is not None:
            cur.close()
    except Exception:
        pass
    try:
        if conn is not None:
            conn.rollback()
    except Exception:
        pass
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass
