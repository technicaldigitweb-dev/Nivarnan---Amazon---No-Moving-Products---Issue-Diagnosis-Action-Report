"""
anpia_config.py -- REQ-ANPIA-REQ-01-D02

Loads ANPIA_DB_* connection settings from a local .env file (git-ignored,
never committed) and/or the process environment. No credential value is
ever printed, logged, or returned in any form other than the config dict
consumed directly by anpia_db_connection.py.

.env is parsed manually (no external dependency) -- KEY=VALUE lines only,
'#'-prefixed lines and blank lines are skipped, values are not shell-
expanded or quote-processed beyond simple stripping.
"""

import os

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")

_REQUIRED_VARS = (
    "ANPIA_DB_HOST",
    "ANPIA_DB_PORT",
    "ANPIA_DB_NAME",
    "ANPIA_DB_USER",
    "ANPIA_DB_PASSWORD",
)

_loaded = False


def _load_env_file():
    """Populates os.environ from .env for any key not already set in the
    real environment (real environment always takes precedence). Silently
    no-ops if .env does not exist -- this is not an error, since values
    may already be set directly in the environment."""
    global _loaded
    if _loaded:
        return
    if os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key and key not in os.environ:
                    os.environ[key] = value
    _loaded = True


def get_db_config() -> dict:
    """Returns the ANPIA direct-connection config dict. Raises RuntimeError
    naming the missing variable(s) if any required value is absent --
    never falls back to a hardcoded value."""
    _load_env_file()
    missing = [name for name in _REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required ANPIA_DB_* variable(s): "
            f"{', '.join(missing)}. Populate a local .env (see .env.example) "
            "before connecting -- there is no hardcoded fallback."
        )
    return {
        "host": os.environ["ANPIA_DB_HOST"],
        "port": os.environ["ANPIA_DB_PORT"],
        "dbname": os.environ["ANPIA_DB_NAME"],
        "user": os.environ["ANPIA_DB_USER"],
        "password": os.environ["ANPIA_DB_PASSWORD"],
        "sslmode": os.environ.get("ANPIA_DB_SSLMODE", "prefer"),
        "connect_timeout": 15,
    }


def _mask(value: str) -> str:
    """Keeps the first 2 characters (enough to distinguish values in logs
    without reconstructing them) and masks the rest."""
    if not value:
        return ""
    if len(value) <= 2:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 2)


def safe_db_metadata() -> dict:
    """Returns non-secret connection metadata safe to print, log, or place
    in evidence/handover documents: database name and SSL mode in full,
    host and user masked. Never returns the password or a full DSN. Raises
    RuntimeError (same as get_db_config()) if required configuration is
    missing -- there is no fallback metadata to report."""
    cfg = get_db_config()
    return {
        "host": _mask(cfg["host"]),
        "port": cfg["port"],
        "dbname": cfg["dbname"],
        "user": _mask(cfg["user"]),
        "sslmode": cfg["sslmode"],
    }
