"""
prepare_ph_task_v007_upload.py -- REQ-ANPIA-REQ-01-D02

Safe-by-default preparation/upload script for publishing the ANPIA v007 HTML
report to tech_team_outputs.ph_task. Default execution (no flags, or
--dry-run) NEVER writes to the database -- it only validates. A real write
requires BOTH --execute AND the exact --confirm-publication-token value.

Credentials are loaded exclusively via 05_IMPLEMENTATION/src/anpia_config.py
(.env / environment) -- never hardcoded, never read from chat, never printed.
All SQL is parameterized (%s placeholders) -- no string-formatted SQL.

This module performs NO action at import time -- everything runs under
`if __name__ == "__main__": main()`.
"""

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

CONFIRM_TOKEN = "PUBLISH_ANPIA_V007"
TARGET_SCHEMA = "tech_team_outputs"
TARGET_TABLE = "ph_task"
# No proven hard database or application limit was found (html_content is
# TEXT, no character_maximum_length; the largest existing live value found
# during discovery was 18,237,445 bytes). This is a conservative sanity
# ceiling only, not evidence of an actual limit.
SIZE_SANITY_CEILING_BYTES = 50_000_000

STATIC_FORBIDDEN_PATTERNS = [
    "ANPIA_DB_PASSWORD",
]
SAFE_MINIMUM_SECRET_LENGTH = 6


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Dry-run-safe ph_task publication preparation for ANPIA v007.")
    p.add_argument("--html-path", default=None, help="Path to the v007 HTML file.")
    p.add_argument("--manifest", default=None, help="Path to the publication manifest JSON.")
    p.add_argument("--dry-run", action="store_true", help="Validate only, never write (this is also the default).")
    p.add_argument("--execute", action="store_true", help="Required (with --confirm-publication-token) to perform a real write.")
    p.add_argument("--expected-action", choices=["SAFE_NEW_INSERT", "UPDATE_EXISTING_SAME_DAY_ROW", "VERSIONED_NEW_ROW"], default=None,
                    help="The action the caller expects the duplicate check to confirm.")
    p.add_argument("--confirm-publication-token", default=None, help="Must exactly equal the fixed non-secret phrase to allow a write.")
    return p.parse_args(argv)


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_html_bytes(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"HTML file not found: {path}")
    with open(path, "rb") as f:
        return f.read()


def validate_utf8(html_bytes):
    try:
        html_bytes.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def _runtime_forbidden_patterns():
    """Builds the leak-detection pattern list at call time. The live host/
    password are never stored as source-code literals -- they are loaded
    here from the environment via anpia_config (the same no-hardcoded-
    fallback source anpia_config.py itself uses) and folded into the list
    only for the duration of this scan."""
    patterns = list(STATIC_FORBIDDEN_PATTERNS)
    try:
        from anpia_config import get_db_config
        cfg = get_db_config()
        for key in ("host", "password"):
            value = cfg.get(key)
            if value and len(value) >= SAFE_MINIMUM_SECRET_LENGTH:
                patterns.append(value)
    except Exception:
        pass
    return patterns


def scan_forbidden_patterns(html_text):
    found = [p for p in _runtime_forbidden_patterns() if p in html_text]
    return found


def confirm_self_contained(html_text):
    """Best-effort structural check: no <script src=, <link href= (external
    stylesheet), or fetch()/XMLHttpRequest calls to a remote origin. Does not
    guarantee self-containment, but catches the obvious cases."""
    issues = []
    lowered = html_text.lower()
    if "<script src=" in lowered:
        issues.append("external <script src=...> reference found")
    if '<link rel="stylesheet" href="http' in lowered or "<link rel='stylesheet' href='http" in lowered:
        issues.append("external stylesheet reference found")
    if "cdn." in lowered:
        issues.append("possible CDN reference found")
    return issues


def get_db_connection_readonly():
    from anpia_db_connection import get_connection
    return get_connection()


def inspect_connection(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user, current_setting('ssl')")
        db, usr, ssl = cur.fetchone()
        cur.execute("SHOW transaction_read_only")
        readonly = cur.fetchone()[0]
    return {"database": db, "user": usr, "ssl": ssl, "transaction_read_only": readonly}


def check_duplicates(conn, manifest):
    """Parameterized SELECT only -- looks for an existing row matching this
    publication's logical identity (project_code + assigned_user, most
    recent). Returns (count, sample_rows) without ever writing."""
    project_code = manifest["proposed_values"]["project_code"]["value"]
    assigned_user = manifest["proposed_values"]["assigned_user"]["value"]
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, task_id, version_level, version_status, created_at
            FROM tech_team_outputs.ph_task
            WHERE project_code = %s AND assigned_user = %s
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (project_code, assigned_user),
        )
        rows = cur.fetchall()
    return len(rows), rows


def build_insert_sql_and_params(manifest, html_text):
    """Returns (sql, params) using ONLY %s placeholders -- no string
    interpolation of any value into the SQL text itself. Not executed by
    this module unless --execute and the correct token are both supplied."""
    v = manifest["proposed_values"]
    sql = """
        INSERT INTO tech_team_outputs.ph_task
            (project_name, project_code, task_name, task_id, team, developer,
             assigned_user, assigned_user_team, html_content, description,
             phase_level, version_level, version_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    params = (
        v["project_name"]["value"],
        v["project_code"]["value"],
        v["task_name"]["value"],
        v["task_id"]["value"],
        v["team"]["value"],
        v["developer"]["value"],
        v["assigned_user"]["value"],
        v["assigned_user_team"]["value"],
        html_text,
        v["description"]["value"],
        v["phase_level"]["value"],
        v["version_level"]["value"],
        v["version_status"]["value"],
    )
    return sql, params


def main():
    args = parse_args()
    is_write_attempt = args.execute

    print("=" * 70)
    print("ph_task publication preparation -- ANPIA v007")
    print("=" * 70)
    print(f"Target: {TARGET_SCHEMA}.{TARGET_TABLE}")
    print(f"Mode: {'EXECUTE (write requested)' if is_write_attempt else 'DRY-RUN (default, no write possible)'}")

    # ---- Safety gate 1: --execute requires the exact confirmation token ----
    if is_write_attempt:
        if args.confirm_publication_token != CONFIRM_TOKEN:
            print("SAFETY GATE FAILED: --execute was supplied without the correct --confirm-publication-token.")
            print("WRITE EXECUTED: NO")
            sys.exit(2)

    # ---- Load manifest ----
    if not args.manifest or not os.path.exists(args.manifest):
        print(f"SAFETY GATE FAILED: manifest not found: {args.manifest}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # ---- Load and validate HTML ----
    try:
        html_bytes = load_html_bytes(args.html_path)
    except FileNotFoundError as e:
        print(f"SAFETY GATE FAILED: {e}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    html_size = len(html_bytes)
    html_sha256 = hashlib.sha256(html_bytes).hexdigest()

    if not validate_utf8(html_bytes):
        print("SAFETY GATE FAILED: HTML is not valid UTF-8.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    html_text = html_bytes.decode("utf-8")

    expected_sha256 = (manifest.get("html_sha256") or "")
    checksum_ok = (html_sha256.lower() == expected_sha256.lower())
    if not checksum_ok:
        print("SAFETY GATE FAILED: HTML SHA-256 does not match the manifest.")
        print(f"  expected: {expected_sha256}")
        print(f"  actual:   {html_sha256}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    size_ok = html_size <= SIZE_SANITY_CEILING_BYTES
    if not size_ok:
        print(f"SAFETY GATE FAILED: HTML size {html_size} exceeds the sanity ceiling {SIZE_SANITY_CEILING_BYTES}.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    forbidden_found = scan_forbidden_patterns(html_text)
    if forbidden_found:
        print(f"SAFETY GATE FAILED: forbidden credential-like pattern(s) found in HTML: {len(forbidden_found)} match(es).")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    self_contained_issues = confirm_self_contained(html_text)

    print("\n--- File validation ---")
    print(f"HTML path:      {args.html_path}")
    print(f"HTML size:      {html_size:,} bytes")
    print(f"HTML SHA-256:   {html_sha256}")
    print(f"Checksum gate:  {'PASS' if checksum_ok else 'FAIL'}")
    print(f"Size gate:      {'PASS' if size_ok else 'FAIL'} (ceiling {SIZE_SANITY_CEILING_BYTES:,} bytes, not a proven DB limit)")
    print(f"UTF-8 valid:    YES")
    print(f"Credential scan: {'CLEAN' if not forbidden_found else 'FOUND ' + str(len(forbidden_found))}")
    print(f"Self-contained checks: {'CLEAN' if not self_contained_issues else self_contained_issues}")

    # ---- Connect read-only and inspect ----
    try:
        conn = get_db_connection_readonly()
    except Exception as e:
        print(f"\nSAFETY GATE FAILED: could not establish database connection ({type(e).__name__}).")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    try:
        conn_info = inspect_connection(conn)
        print("\n--- Connection ---")
        print(f"Connected:      YES")
        print(f"Database:       {conn_info['database']}")
        print(f"Role:           {conn_info['user']}")
        print(f"SSL:            {conn_info['ssl']}")
        print(f"Read-only txn:  {conn_info['transaction_read_only']}")

        dup_count, dup_rows = check_duplicates(conn, manifest)
        print("\n--- Duplicate check ---")
        print(f"Existing rows matching project_code + assigned_user: {dup_count}")
        recommended_action = "SAFE_NEW_INSERT" if dup_count == 0 else "UPDATE_EXISTING_SAME_DAY_ROW_OR_VERSIONED_NEW_ROW"
        print(f"Recommended action from live check: {recommended_action}")

        action_match = True
        if args.expected_action:
            if args.expected_action == "SAFE_NEW_INSERT" and dup_count != 0:
                action_match = False
            if args.expected_action in ("UPDATE_EXISTING_SAME_DAY_ROW", "VERSIONED_NEW_ROW") and dup_count == 0:
                action_match = False
            print(f"Expected action ({args.expected_action}) matches live duplicate state: {'YES' if action_match else 'NO'}")

        print("\n--- Proposed publication values (non-secret) ---")
        for field, info in manifest.get("proposed_values", {}).items():
            print(f"  {field}: {info.get('value')!r}  (confidence={info.get('confidence')}, source={info.get('source_of_truth')})")

        print("\n--- Operation ---")
        print(f"SQL operation type: {'INSERT (parameterized)' if not dup_count else 'INSERT/UPDATE (parameterized) -- requires reviewer decision'}")
        print("SQL VALUES: <not printed -- see manifest for non-secret field values; html_content is never printed>")

        write_performed = False
        if is_write_attempt:
            if not action_match:
                print("\nABORTING WRITE: expected action does not match the live duplicate-check result.")
                print("WRITE EXECUTED: NO")
                sys.exit(3)
            # This task's own instructions explicitly forbid ever reaching a
            # commit during this task. The write path below is intentionally
            # inert: it demonstrates the safe pattern (transaction, verified
            # row count, rollback-on-mismatch) but does not commit here. A
            # future, separately-authorized run would replace this guard.
            print("\nWRITE PATH REACHED BUT INTENTIONALLY NOT COMMITTED.")
            print("This script version does not perform live INSERT/UPDATE execution -- see handover for the follow-up task required to enable it.")
            print("WRITE EXECUTED: NO")
        else:
            print("\nWRITE EXECUTED: NO (dry-run mode)")

        conn.rollback()

    finally:
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    print("\n" + "=" * 70)
    print("Dry-run complete." if not is_write_attempt else "Execute-mode run complete (no write performed by this script version).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
