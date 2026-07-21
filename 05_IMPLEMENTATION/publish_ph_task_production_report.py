"""
publish_ph_task_production_report.py -- REQ-ANPIA-REQ-01-D02

Safe-by-default publication script for the ANPIA production report
(project_code=ANPIA, assigned_user=Nivarnan) into tech_team_outputs.ph_task.

Default execution (no flags, or --dry-run) NEVER writes to the database --
it only validates. A real write requires ALL FOUR of:
    --execute
    --confirmation-token PUBLISH_NIVARNAN_ANPIA
    --approved-manifest-sha256 <sha256 of the manifest FILE itself>
    --expected-action <the live-proven action>

Identity rule: project_code AGE belongs to unrelated work. This script
never queries or reasons about project_code='AGE' rows for any decision.
The only relevant publication identity is project_code=ANPIA +
assigned_user=Nivarnan + report date.

Credentials are loaded exclusively via 05_IMPLEMENTATION/src/anpia_config.py
(.env / environment) -- never hardcoded, never read from chat, never
printed. All SQL is parameterized (%s placeholders) -- no string-formatted
SQL. This module performs NO action at import time -- everything runs
under `if __name__ == "__main__": main()`.
"""

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

CONFIRM_TOKEN = "PUBLISH_NIVARNAN_ANPIA"
APPROVED_PROJECT_CODE = "ANPIA"
APPROVED_ASSIGNED_USER = "Nivarnan"
TARGET_SCHEMA = "tech_team_outputs"
TARGET_TABLE = "ph_task"
SIZE_SANITY_CEILING_BYTES = 50_000_000
VALID_EXPECTED_ACTIONS = (
    "SAFE_NEW_INSERT",
    "UPDATE_SAME_DAY_ACTIVE_ROW",
    "UPDATE_EXISTING_ROW",
    "REPLACE_SAME_DAY_ACTIVE_CONTENT",
    "BLOCKED_UNCONFIRMED_COLUMN_RULE",
)
# YYYY-MM-DD_username_projectcode_vNNN.html -- lowercase username/project code, 3-digit version.
FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+_[a-z0-9]+_v\d{3}\.html$")
STATIC_FORBIDDEN_PATTERNS = [
    "ANPIA_DB_PASSWORD",
    "ANPIA_DB_HOST",
]
SAFE_MINIMUM_SECRET_LENGTH = 6
EXPECTED_COLUMNS = {
    "id", "project_name", "project_code", "task_name", "task_id", "team", "developer",
    "assigned_user", "html_content", "description", "phase_level", "version_level",
    "version_status", "action_took_by", "action_took_date_time", "created_at", "updated_at",
    "assigned_user_team",
}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Dry-run-safe ph_task publication for the ANPIA production report.")
    p.add_argument("--manifest", default=None, help="Path to the production manifest JSON.")
    p.add_argument("--dry-run", action="store_true", help="Validate only, never write (this is also the default).")
    p.add_argument("--execute", action="store_true", help="Required (with the other three flags) to attempt a real write.")
    p.add_argument("--confirmation-token", default=None, help="Must exactly equal the fixed non-secret phrase to allow a write.")
    p.add_argument("--approved-manifest-sha256", default=None, help="SHA-256 of the manifest FILE itself, as approved by the reviewer.")
    p.add_argument("--expected-action", choices=VALID_EXPECTED_ACTIONS, default=None,
                    help="The action the caller expects the live duplicate check to confirm.")
    return p.parse_args(argv)


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_of_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_manifest(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"manifest not found: {path}")
    manifest_sha256 = sha256_of_file(path)
    with open(path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return manifest, manifest_sha256


def validate_filename(filename):
    return bool(FILENAME_RE.match(filename or ""))


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
    return [p for p in _runtime_forbidden_patterns() if p in html_text]


def confirm_self_contained(html_text):
    issues = []
    lowered = html_text.lower()
    if "<script src=" in lowered:
        issues.append("external <script src=...> reference found")
    if '<link rel="stylesheet" href="http' in lowered or "<link rel='stylesheet' href='http" in lowered:
        issues.append("external stylesheet reference found")
    if "cdn." in lowered:
        issues.append("possible CDN reference found")
    return issues


def get_readonly_connection():
    from anpia_db_connection import get_connection
    return get_connection()


def get_writable_connection():
    """A writable (non-readonly-session) connection, used ONLY on the write
    path (--execute with all gates passed). Credentials come exclusively
    from anpia_config.get_db_config() -- same source as the read-only
    helper, never hardcoded, never printed."""
    import psycopg2
    from anpia_config import get_db_config

    cfg = get_db_config()
    try:
        conn = psycopg2.connect(**cfg)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as exc:
        text = str(exc).replace(cfg["password"], "***REDACTED***")
        raise RuntimeError(f"Could not connect to ANPIA database: {text}") from exc


def reverify_live_schema(conn):
    """Re-fetches the live column set immediately before a write, so a
    schema change between dry-run and execute time is caught rather than
    silently producing a malformed INSERT."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema=%s AND table_name=%s",
            (TARGET_SCHEMA, TARGET_TABLE),
        )
        live_columns = {r[0] for r in cur.fetchall()}
    missing = EXPECTED_COLUMNS - live_columns
    return live_columns, missing


def check_anpia_only_duplicates(conn, project_code, assigned_user):
    """ANPIA-only, AGE-excluded duplicate check. Never queries
    project_code='AGE' under any circumstance."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, task_id, version_level, version_status, created_at "
            "FROM tech_team_outputs.ph_task "
            "WHERE project_code = %s AND assigned_user = %s "
            "ORDER BY created_at DESC",
            (project_code, assigned_user),
        )
        rows = cur.fetchall()
    return len(rows), rows


def build_insert_sql_and_params(manifest, html_text):
    sql = """
        INSERT INTO tech_team_outputs.ph_task
            (project_name, project_code, task_name, task_id, team, developer,
             assigned_user, assigned_user_team, html_content, description,
             phase_level, version_level, version_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, project_code, assigned_user, version_level, version_status, created_at
    """
    v = manifest["proposed_column_values"]
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


def build_update_sql_and_params(manifest, html_text, target_row_id, project_code, assigned_user):
    """UPDATE path for the same-day-version rule: only the columns this
    task's manifest declares as changed are touched (html_content,
    version_level, version_status, description, updated_at). All other
    columns (project_code, assigned_user, team, developer,
    assigned_user_team, phase_level, task_name, task_id, action_took_by,
    action_took_date_time) are left untouched by this statement, matching
    'preserve approved unchanged metadata'. WHERE clause is scoped to the
    exact row id AND project_code AND assigned_user -- never a bare id-only
    match -- so a stale/incorrect target_row_id cannot silently update the
    wrong row."""
    sql = """
        UPDATE tech_team_outputs.ph_task
        SET html_content = %s, description = %s, version_level = %s, version_status = %s,
            updated_at = now()
        WHERE id = %s AND project_code = %s AND assigned_user = %s
        RETURNING id, project_code, assigned_user, version_level, version_status, updated_at
    """
    v = manifest["proposed_column_values"]
    params = (
        html_text,
        v["description"]["value"],
        v["version_level"]["value"],
        v["version_status"]["value"],
        target_row_id,
        project_code,
        assigned_user,
    )
    return sql, params


def main():
    args = parse_args()
    is_write_attempt = args.execute

    print("=" * 70)
    print("ph_task production publication -- ANPIA")
    print("=" * 70)
    print(f"Target: {TARGET_SCHEMA}.{TARGET_TABLE}")
    print(f"Mode: {'EXECUTE (write requested)' if is_write_attempt else 'DRY-RUN (default, no write possible)'}")

    if is_write_attempt:
        gate_fail = None
        if args.confirmation_token != CONFIRM_TOKEN:
            gate_fail = "SAFETY GATE FAILED: --execute was supplied without the correct --confirmation-token."
        elif not args.approved_manifest_sha256:
            gate_fail = "SAFETY GATE FAILED: --execute requires --approved-manifest-sha256."
        elif not args.expected_action:
            gate_fail = "SAFETY GATE FAILED: --execute requires --expected-action."
        if gate_fail:
            print(gate_fail)
            print("WRITE EXECUTED: NO")
            sys.exit(2)

    # -- Manifest --
    try:
        manifest, manifest_sha256 = load_manifest(args.manifest)
    except FileNotFoundError as e:
        print(f"SAFETY GATE FAILED: {e}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    print(f"\nManifest path:   {args.manifest}")
    print(f"Manifest SHA-256: {manifest_sha256}")

    if is_write_attempt:
        if manifest_sha256.lower() != (args.approved_manifest_sha256 or "").lower():
            print("SAFETY GATE FAILED: manifest SHA-256 does not match --approved-manifest-sha256.")
            print(f"  computed:  {manifest_sha256}")
            print(f"  approved:  {args.approved_manifest_sha256}")
            print("WRITE EXECUTED: NO")
            sys.exit(2)

    # -- Identity validation (ANPIA / Nivarnan only) --
    project_code = manifest.get("project_code")
    assigned_user = manifest.get("assigned_user")
    if project_code != APPROVED_PROJECT_CODE:
        print(f"SAFETY GATE FAILED: manifest project_code '{project_code}' is not the approved '{APPROVED_PROJECT_CODE}'.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    if assigned_user != APPROVED_ASSIGNED_USER:
        print(f"SAFETY GATE FAILED: manifest assigned_user '{assigned_user}' is not the approved '{APPROVED_ASSIGNED_USER}'.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    print(f"project_code:    {project_code} (OK)")
    print(f"assigned_user:   {assigned_user} (OK)")

    # -- Filename format --
    production_filename = manifest.get("production_filename")
    if not validate_filename(production_filename):
        print(f"SAFETY GATE FAILED: production_filename '{production_filename}' does not match YYYY-MM-DD_username_projectcode_vNNN.html.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    print(f"production_filename: {production_filename} (format OK)")

    # -- HTML file --
    html_path = manifest.get("html_path")
    try:
        html_bytes = load_html_bytes(html_path)
    except FileNotFoundError as e:
        print(f"SAFETY GATE FAILED: {e}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    html_size = len(html_bytes)
    html_sha256 = sha256_of_bytes(html_bytes)

    if not validate_utf8(html_bytes):
        print("SAFETY GATE FAILED: HTML is not valid UTF-8.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    html_text = html_bytes.decode("utf-8")

    expected_sha256 = (manifest.get("html_sha256") or "")
    if html_sha256.lower() != expected_sha256.lower():
        print("SAFETY GATE FAILED: HTML SHA-256 does not match the manifest.")
        print(f"  expected: {expected_sha256}")
        print(f"  actual:   {html_sha256}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    expected_size = manifest.get("html_byte_size")
    if expected_size is not None and html_size != expected_size:
        print(f"SAFETY GATE FAILED: HTML size {html_size} does not match manifest's {expected_size}.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    if html_size > SIZE_SANITY_CEILING_BYTES:
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
    print(f"HTML path:       {html_path}")
    print(f"HTML size:       {html_size:,} bytes")
    print(f"HTML SHA-256:    {html_sha256}")
    print("Checksum gate:   PASS")
    print("Size gate:       PASS")
    print("UTF-8 valid:     YES")
    print("Credential scan: CLEAN")
    print(f"Self-contained checks: {'CLEAN' if not self_contained_issues else self_contained_issues}")

    # -- Connect (read-only for inspection/dry-run; only re-open writable right before the write) --
    try:
        conn = get_readonly_connection()
    except Exception as e:
        print(f"\nSAFETY GATE FAILED: could not establish database connection ({type(e).__name__}).")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    write_performed = False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, current_setting('ssl')")
            db, usr, ssl = cur.fetchone()
            cur.execute("SHOW transaction_read_only")
            readonly = cur.fetchone()[0]
        print("\n--- Connection (read-only inspection) ---")
        print(f"Connected:      YES")
        print(f"Database:       {db}")
        print(f"Role:           {usr}")
        print(f"SSL:            {ssl}")
        print(f"Read-only txn:  {readonly}")

        live_columns, missing_columns = reverify_live_schema(conn)
        if missing_columns:
            print(f"\nSAFETY GATE FAILED: live schema is missing expected column(s): {sorted(missing_columns)}.")
            print("WRITE EXECUTED: NO")
            sys.exit(2)
        print(f"Live schema re-verified: {len(live_columns)} columns present, all {len(EXPECTED_COLUMNS)} expected columns found.")

        manifest_action = manifest.get("proposed_action")
        target_row_id = manifest.get("target_row_id")

        dup_count, dup_rows = check_anpia_only_duplicates(conn, project_code, assigned_user)
        dup_row_ids = [r[0] for r in dup_rows]
        if dup_count == 0:
            live_action = "SAFE_NEW_INSERT"
        elif dup_count == 1 and target_row_id is not None and dup_row_ids[0] == target_row_id:
            live_action = "UPDATE_EXISTING_ROW"
        else:
            live_action = "BLOCKED_UNCONFIRMED_COLUMN_RULE"
        print("\n--- ANPIA-only duplicate check (AGE excluded) ---")
        print(f"Existing rows for project_code='{project_code}' AND assigned_user='{assigned_user}': {dup_count} (ids: {dup_row_ids})")
        print(f"Manifest declares: action={manifest_action}, target_row_id={target_row_id}")
        print(f"Live-derived action: {live_action}")

        action_match = True
        if args.expected_action:
            action_match = (args.expected_action == live_action)
            print(f"Expected action ({args.expected_action}) matches live duplicate state: {'YES' if action_match else 'NO'}")

        print("\n--- Proposed publication values (non-secret) ---")
        for col, spec in manifest.get("proposed_column_values", {}).items():
            val = spec.get("value")
            if col == "html_content":
                val = f"<{spec.get('byte_size')} bytes, sha256={spec.get('sha256')}, not printed>"
            print(f"  {col}: {val!r}  (confidence={spec.get('confidence')}, reviewer_approval_needed={spec.get('reviewer_approval_needed')})")

        print(f"\nOperation: parameterized INSERT ... RETURNING id")
        print("SQL VALUES: <not printed -- see manifest for non-secret field values; html_content is never printed>")

        if is_write_attempt:
            if not action_match:
                print("\nABORTING WRITE: expected action does not match the live duplicate-check result.")
                print("WRITE EXECUTED: NO")
                sys.exit(3)
            if live_action not in ("SAFE_NEW_INSERT", "UPDATE_EXISTING_ROW"):
                print(f"\nABORTING WRITE: live action is '{live_action}' -- this script only performs SAFE_NEW_INSERT or UPDATE_EXISTING_ROW.")
                print("WRITE EXECUTED: NO")
                sys.exit(3)
            if live_action != manifest_action:
                print(f"\nABORTING WRITE: live-derived action ({live_action}) does not match the manifest's declared proposed_action ({manifest_action}).")
                print("WRITE EXECUTED: NO")
                sys.exit(3)

            conn.rollback()
            conn.close()

            try:
                wconn = get_writable_connection()
            except Exception as e:
                print(f"\nSAFETY GATE FAILED: could not establish writable connection ({type(e).__name__}).")
                print("WRITE EXECUTED: NO")
                sys.exit(2)

            try:
                # Re-verify schema and duplicate state again, inside the write connection,
                # immediately before the write -- closes the race window between the
                # read-only inspection above and the actual write.
                live_columns2, missing2 = reverify_live_schema(wconn)
                if missing2:
                    print(f"\nABORTING WRITE: live schema changed, missing column(s): {sorted(missing2)}.")
                    wconn.rollback()
                    print("WRITE EXECUTED: NO")
                    sys.exit(2)
                dup_count2, dup_rows2 = check_anpia_only_duplicates(wconn, project_code, assigned_user)
                dup_row_ids2 = [r[0] for r in dup_rows2]

                if live_action == "SAFE_NEW_INSERT":
                    if dup_count2 != 0:
                        print(f"\nABORTING WRITE: duplicate state changed since inspection -- {dup_count2} row(s) now exist for this project_code+assigned_user.")
                        wconn.rollback()
                        print("WRITE EXECUTED: NO")
                        sys.exit(3)

                    sql, params = build_insert_sql_and_params(manifest, html_text)
                    with wconn.cursor() as wcur:
                        wcur.execute(sql, params)
                        written = wcur.fetchone()
                        if wcur.rowcount != 1:
                            raise RuntimeError(f"expected exactly 1 affected row, got {wcur.rowcount}")
                    written_id = written[0]

                else:  # UPDATE_EXISTING_ROW
                    if dup_count2 != 1 or dup_row_ids2[0] != target_row_id:
                        print(f"\nABORTING WRITE: duplicate state changed since inspection -- expected exactly row id={target_row_id}, found {dup_row_ids2}.")
                        wconn.rollback()
                        print("WRITE EXECUTED: NO")
                        sys.exit(3)

                    sql, params = build_update_sql_and_params(manifest, html_text, target_row_id, project_code, assigned_user)
                    with wconn.cursor() as wcur:
                        wcur.execute(sql, params)
                        written = wcur.fetchone()
                        if wcur.rowcount != 1:
                            raise RuntimeError(f"expected exactly 1 affected row, got {wcur.rowcount}")
                    written_id = written[0]

                # Reread and verify the published row, still inside the same
                # uncommitted transaction, before committing.
                with wconn.cursor() as wcur:
                    wcur.execute(
                        "SELECT id, project_code, assigned_user, version_level, version_status, "
                        "octet_length(html_content) "
                        "FROM tech_team_outputs.ph_task WHERE id = %s",
                        (written_id,),
                    )
                    reread = wcur.fetchone()
                if reread is None:
                    raise RuntimeError("reread of written row returned no result")
                if reread[1] != project_code or reread[2] != assigned_user:
                    raise RuntimeError(f"reread row identity mismatch: {reread}")
                if reread[5] != html_size:
                    raise RuntimeError(f"reread html_content length mismatch: stored={reread[5]}, expected={html_size}")

                wconn.commit()
                write_performed = True
                print(f"\nWRITE COMMITTED: action={live_action}, id={written_id}, project_code={reread[1]}, "
                      f"assigned_user={reread[2]}, version_level={reread[3]}, version_status={reread[4]}, "
                      f"html_octet_length={reread[5]}")
            except Exception as e:
                wconn.rollback()
                print(f"\nABORTING WRITE: {type(e).__name__}: {e}")
                print("WRITE EXECUTED: NO")
                sys.exit(4)
            finally:
                try:
                    wconn.close()
                except Exception:
                    pass
        else:
            print("\nWRITE EXECUTED: NO (dry-run mode)")

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
    print(f"{'Publication complete.' if write_performed else 'Dry-run complete.'}")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
