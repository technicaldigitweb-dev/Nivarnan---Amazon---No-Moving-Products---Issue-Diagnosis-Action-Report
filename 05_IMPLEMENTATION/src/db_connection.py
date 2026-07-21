"""
db_connection.py -- REQ-ANPIA-REQ-01-D02

Direct PostgreSQL connection helper for the ANPIA common-daily-dataset
rebuild. Reads all connection details from environment variables only --
NEVER hardcodes a host, user, password, or connection string in this file.
`Sources/db_access_templates/temp_user.py` and `update_table.py` are
protected, read-only reference material only (see
00_PROJECT_CONTROL/PROTECTED_SOURCE_INVENTORY.md) -- they are excluded
from Git and MUST NOT be treated as a credential-free pattern to copy;
this module does not import or execute them.

Required environment variables (set by the runtime -- e.g. via a local,
git-ignored .env file loaded by the caller -- never by this file):
    ANPIA_DB_HOST
    ANPIA_DB_PORT
    ANPIA_DB_NAME
    ANPIA_DB_USER
    ANPIA_DB_PASSWORD
    ANPIA_DB_SSLMODE   (optional, defaults to "prefer")
"""

import os
import psycopg2
import psycopg2.extras

_REQUIRED_ENV_VARS = (
    "ANPIA_DB_HOST",
    "ANPIA_DB_PORT",
    "ANPIA_DB_NAME",
    "ANPIA_DB_USER",
    "ANPIA_DB_PASSWORD",
)


def _redact(exc: Exception) -> str:
    """Returns a connection-error message with the password value stripped,
    even if a driver or OS error ever echoes the DSN. Never logs secrets."""
    text = str(exc)
    password = os.environ.get("ANPIA_DB_PASSWORD")
    if password:
        text = text.replace(password, "***REDACTED***")
    return text


def load_db_config() -> dict:
    """Reads connection settings from environment variables only. Raises a
    clear error naming the missing variable(s) -- never falls back to a
    hardcoded value, and never logs the password or a full DSN."""
    missing = [name for name in _REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s) for the ANPIA direct "
            f"connection: {', '.join(missing)}. Set them (e.g. in a local, "
            "git-ignored .env file) before running this script -- there is "
            "no hardcoded fallback."
        )
    return {
        "host": os.environ["ANPIA_DB_HOST"],
        "port": os.environ["ANPIA_DB_PORT"],
        "dbname": os.environ["ANPIA_DB_NAME"],
        "user": os.environ["ANPIA_DB_USER"],
        "password": os.environ["ANPIA_DB_PASSWORD"],
        "sslmode": os.environ.get("ANPIA_DB_SSLMODE", "prefer"),
        "connect_timeout": 10,
    }


def get_connection():
    """
    Returns a psycopg2 connection using only environment-variable credentials.
    Raises RuntimeError if required environment variables are not set.
    Connection errors are re-raised with the password redacted from the
    message text (defense in depth -- psycopg2's own error text does not
    normally include the password, but this guards against edge cases).
    """
    db_config = load_db_config()
    try:
        return psycopg2.connect(**db_config)
    except psycopg2.OperationalError as exc:
        raise RuntimeError(f"Could not connect to ANPIA database: {_redact(exc)}") from exc


def read_only_cursor(conn, name=None, batch_size=2000):
    """
    Opens a read-only transaction and returns a server-side (named) cursor
    for large result sets, so the whole result set is never materialized in
    Python memory at once. Caller must iterate with cursor.fetchmany(batch_size)
    and is responsible for closing the cursor (use as a context manager).

    conn.autocommit is left False; the caller must call conn.rollback() after
    use (read-only transactions have nothing to commit) -- see
    run_report_v003.py for the calling pattern.
    """
    conn.set_session(readonly=True, autocommit=False)
    cur = conn.cursor(name=name or "anpia_server_cursor", cursor_factory=psycopg2.extras.RealDictCursor)
    cur.itersize = batch_size
    return cur


def safe_close(conn, cur=None):
    """Rolls back any open transaction and closes cursor/connection safely.
    Never raises -- swallows close-time errors so cleanup never masks the
    original exception in a caller's try/finally block."""
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
