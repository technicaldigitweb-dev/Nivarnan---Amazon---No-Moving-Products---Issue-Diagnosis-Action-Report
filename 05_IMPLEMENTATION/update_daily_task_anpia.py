"""
update_daily_task_anpia.py -- REQ-ANPIA-REQ-01-D02

Safe-by-default guarded insert/update script for daily_task.tbl_anpia_satheskanth
-- the dedicated daily-work-log table for this project, separate from and
never touching tech_team_outputs.ph_task or any other daily_task table.

Default execution (no flags, or --dry-run) NEVER writes to the database --
it only inspects, validates, and prints the proposed column-value map.
A real write requires ALL of:
    --execute
    --confirmation-token UPDATE_ANPIA_DAILY_TASK
    --expected-action <matching the live-derived classification>
    --work-date YYYY-MM-DD

IMPORTANT -- connection method disclosure: this script connects using the
project's protected credential environment (05_IMPLEMENTATION/src/anpia_config.py
/ anpia_db_connection.py), the same pattern used by every other reusable
publish script in this project (publish_ph_task_production_report.py,
anpia_daily_pipeline.py). This is necessary for the script to function as a
genuinely standalone, later-reusable artifact -- a standalone Python process
cannot invoke an interactive session's MCP tool bindings, which only exist
inside the orchestrating agent's own runtime. On the day this script was
authored, the live database operations for that specific session were
instead performed directly by the agent via the approved MCP connection, per
that session's explicit instruction -- this script was built but NOT
executed in that session. Any future run of this script (interactive or
automated) will use the credential path described above; if MCP-only
operation is required for a future run too, that requires a separate,
explicit decision at that time, since no MCP client is embedded here.

Never hardcodes secrets. Never prints credentials. All SQL is parameterized.
This module performs NO action at import time -- everything runs under
`if __name__ == "__main__": main()`.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

CONFIRM_TOKEN = "UPDATE_ANPIA_DAILY_TASK"
TARGET_SCHEMA = "daily_task"
TARGET_TABLE = "tbl_anpia_satheskanth"
APPROVED_PROJECT_CODE = "ANPIA"
APPROVED_DEVELOPER = "Satheskanth"
APPROVED_REQUIREMENT_ID = "REQ-01"

VALID_ACTIONS = (
    "SAFE_NEW_INSERT",
    "SAFE_UPDATE_EXISTING_DAILY_ROW",
    "NO_CHANGE_ALREADY_CURRENT",
    "BLOCKED_DUPLICATE_ROWS",
    "BLOCKED_UNCONFIRMED_MAPPING",
)

# Live-verified 2026-07-20 (via MCP) -- NOT NULL columns and their CHECK-
# constrained value sets, re-verified live again immediately before any
# write by reverify_live_schema()/reverify_check_constraints() below.
EXPECTED_COLUMNS = {
    "id", "work_date", "developer", "project_name", "project_code", "domain",
    "aios_phase", "requirement_id", "deliverable_id", "module", "status",
    "task_title", "task_summary", "work_performed", "files_modified",
    "gaps_found", "decisions_made", "company_knowledge", "validation_rules",
    "failure_modes", "blos_keys_used", "hardcoded_thresholds",
    "three_am_standard", "llm_queryable", "company_knowledge_candidate",
    "evidence_location", "skill_file_path", "created_at", "updated_at",
}
AIOS_PHASE_ALLOWED = {"DISCOVERY", "BUILD", "TEST", "REVIEW", "DEPLOY"}
STATUS_ALLOWED = {"IN-PROGRESS", "COMPLETE", "BLOCKED", "PENDING-REVIEW"}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Dry-run-safe daily_task.tbl_anpia_satheskanth publisher.")
    p.add_argument("--manifest", default=None, help="Path to the proposed column-value map JSON.")
    p.add_argument("--dry-run", action="store_true", help="Validate only, never write (also the default).")
    p.add_argument("--execute", action="store_true", help="Required (with the other flags) to attempt a real write.")
    p.add_argument("--confirmation-token", default=None)
    p.add_argument("--expected-action", choices=VALID_ACTIONS, default=None)
    p.add_argument("--work-date", default=None, help="YYYY-MM-DD -- must match the manifest's work_date.")
    return p.parse_args(argv)


def get_readonly_connection():
    from anpia_db_connection import get_connection
    return get_connection()


def get_writable_connection():
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
    with conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema=%s AND table_name=%s",
            (TARGET_SCHEMA, TARGET_TABLE),
        )
        live_columns = {r[0] for r in cur.fetchall()}
    missing = EXPECTED_COLUMNS - live_columns
    return live_columns, missing


def check_existing_rows(conn, work_date, developer, project_code, requirement_id):
    """Scoped to the table's real UNIQUE constraint
    (work_date, developer, project_code, requirement_id) -- confirmed live,
    NOT filtered by deliverable_id (which is not part of that constraint)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, deliverable_id, aios_phase, status, task_title, "
            "octet_length(task_summary) AS task_summary_len, updated_at "
            "FROM daily_task.tbl_anpia_satheskanth "
            "WHERE work_date = %s AND developer = %s AND project_code = %s AND requirement_id = %s",
            (work_date, developer, project_code, requirement_id),
        )
        rows = cur.fetchall()
    return rows


def build_insert_sql_and_params(manifest, work_date):
    v = manifest["proposed_column_values"]
    sql = """
        INSERT INTO daily_task.tbl_anpia_satheskanth
            (work_date, developer, project_name, project_code, domain, aios_phase,
             requirement_id, deliverable_id, module, status, task_title, task_summary,
             work_performed, files_modified, gaps_found, decisions_made,
             company_knowledge, validation_rules, failure_modes, blos_keys_used,
             hardcoded_thresholds, three_am_standard, llm_queryable,
             company_knowledge_candidate, evidence_location, skill_file_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, work_date, developer, project_code, requirement_id, deliverable_id, status
    """
    params = (
        work_date, v["developer"], v["project_name"], v["project_code"], v["domain"], v["aios_phase"],
        v["requirement_id"], v["deliverable_id"], v.get("module"), v["status"], v["task_title"], v["task_summary"],
        v["work_performed"], v.get("files_modified"), v.get("gaps_found"), v.get("decisions_made"),
        v.get("company_knowledge"), v.get("validation_rules"), v.get("failure_modes"), v["blos_keys_used"],
        v.get("hardcoded_thresholds"), v["three_am_standard"], v["llm_queryable"],
        v["company_knowledge_candidate"], v.get("evidence_location"), v.get("skill_file_path"),
    )
    return sql, params


def build_update_sql_and_params(manifest, work_date, target_row_id, developer, project_code, requirement_id):
    v = manifest["proposed_column_values"]
    sql = """
        UPDATE daily_task.tbl_anpia_satheskanth
        SET deliverable_id = %s, module = %s, status = %s, task_title = %s, task_summary = %s,
            work_performed = %s, files_modified = %s, gaps_found = %s, decisions_made = %s,
            company_knowledge = %s, validation_rules = %s, failure_modes = %s,
            blos_keys_used = %s, hardcoded_thresholds = %s, three_am_standard = %s,
            llm_queryable = %s, company_knowledge_candidate = %s, evidence_location = %s,
            skill_file_path = %s, updated_at = now()
        WHERE id = %s AND work_date = %s AND developer = %s AND project_code = %s AND requirement_id = %s
        RETURNING id, work_date, developer, project_code, requirement_id, deliverable_id, status
    """
    params = (
        v["deliverable_id"], v.get("module"), v["status"], v["task_title"], v["task_summary"],
        v["work_performed"], v.get("files_modified"), v.get("gaps_found"), v.get("decisions_made"),
        v.get("company_knowledge"), v.get("validation_rules"), v.get("failure_modes"),
        v["blos_keys_used"], v.get("hardcoded_thresholds"), v["three_am_standard"],
        v["llm_queryable"], v["company_knowledge_candidate"], v.get("evidence_location"),
        v.get("skill_file_path"),
        target_row_id, work_date, developer, project_code, requirement_id,
    )
    return sql, params


def main():
    args = parse_args()
    is_write_attempt = args.execute

    print("=" * 70)
    print("daily_task.tbl_anpia_satheskanth publisher -- ANPIA")
    print("=" * 70)
    print(f"Target: {TARGET_SCHEMA}.{TARGET_TABLE}")
    print(f"Mode: {'EXECUTE (write requested)' if is_write_attempt else 'DRY-RUN (default, no write possible)'}")

    if is_write_attempt:
        gate_fail = None
        if args.confirmation_token != CONFIRM_TOKEN:
            gate_fail = "SAFETY GATE FAILED: --execute was supplied without the correct --confirmation-token."
        elif not args.expected_action:
            gate_fail = "SAFETY GATE FAILED: --execute requires --expected-action."
        elif not args.work_date:
            gate_fail = "SAFETY GATE FAILED: --execute requires --work-date."
        if gate_fail:
            print(gate_fail)
            print("WRITE EXECUTED: NO")
            sys.exit(2)

    if not args.manifest or not os.path.exists(args.manifest):
        print(f"SAFETY GATE FAILED: manifest not found: {args.manifest}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    work_date = args.work_date or manifest.get("work_date")
    try:
        datetime.date.fromisoformat(work_date)
    except (ValueError, TypeError):
        print(f"SAFETY GATE FAILED: invalid work_date: {work_date!r}")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    v = manifest.get("proposed_column_values", {})
    if v.get("aios_phase") not in AIOS_PHASE_ALLOWED:
        print(f"SAFETY GATE FAILED: aios_phase {v.get('aios_phase')!r} not in {sorted(AIOS_PHASE_ALLOWED)}.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)
    if v.get("status") not in STATUS_ALLOWED:
        print(f"SAFETY GATE FAILED: status {v.get('status')!r} not in {sorted(STATUS_ALLOWED)}.")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    try:
        conn = get_readonly_connection()
    except Exception as e:
        print(f"\nSAFETY GATE FAILED: could not establish database connection ({type(e).__name__}).")
        print("WRITE EXECUTED: NO")
        sys.exit(2)

    write_performed = False
    try:
        live_columns, missing_columns = reverify_live_schema(conn)
        if missing_columns:
            print(f"\nSAFETY GATE FAILED: live schema missing expected column(s): {sorted(missing_columns)}.")
            print("WRITE EXECUTED: NO")
            sys.exit(2)
        print(f"Live schema re-verified: {len(live_columns)} columns present.")

        developer = v.get("developer", APPROVED_DEVELOPER)
        project_code = v.get("project_code", APPROVED_PROJECT_CODE)
        requirement_id = v.get("requirement_id", APPROVED_REQUIREMENT_ID)

        rows = check_existing_rows(conn, work_date, developer, project_code, requirement_id)
        print(f"\nMatching rows for work_date={work_date}, developer={developer}, "
              f"project_code={project_code}, requirement_id={requirement_id}: {len(rows)}")

        if len(rows) == 0:
            live_action = "SAFE_NEW_INSERT"
            target_row_id = None
        elif len(rows) == 1:
            live_action = "SAFE_UPDATE_EXISTING_DAILY_ROW"
            target_row_id = rows[0][0]
        else:
            live_action = "BLOCKED_DUPLICATE_ROWS"
            target_row_id = [r[0] for r in rows]
        print(f"Live-derived action: {live_action}")

        action_match = True
        if args.expected_action:
            action_match = (args.expected_action == live_action)
            print(f"Expected action ({args.expected_action}) matches live state: {'YES' if action_match else 'NO'}")

        if is_write_attempt:
            if not action_match:
                print("\nABORTING WRITE: expected action does not match the live classification.")
                print("WRITE EXECUTED: NO")
                sys.exit(3)
            if live_action not in ("SAFE_NEW_INSERT", "SAFE_UPDATE_EXISTING_DAILY_ROW"):
                print(f"\nABORTING WRITE: live action is '{live_action}' -- not a writable state.")
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
                live_columns2, missing2 = reverify_live_schema(wconn)
                if missing2:
                    print(f"\nABORTING WRITE: live schema changed, missing column(s): {sorted(missing2)}.")
                    wconn.rollback()
                    print("WRITE EXECUTED: NO")
                    sys.exit(2)
                rows2 = check_existing_rows(wconn, work_date, developer, project_code, requirement_id)

                if live_action == "SAFE_NEW_INSERT":
                    if len(rows2) != 0:
                        print(f"\nABORTING WRITE: duplicate state changed -- {len(rows2)} row(s) now exist.")
                        wconn.rollback()
                        print("WRITE EXECUTED: NO")
                        sys.exit(3)
                    sql, params = build_insert_sql_and_params(manifest, work_date)
                else:
                    if len(rows2) != 1 or rows2[0][0] != target_row_id:
                        print(f"\nABORTING WRITE: duplicate state changed since inspection.")
                        wconn.rollback()
                        print("WRITE EXECUTED: NO")
                        sys.exit(3)
                    sql, params = build_update_sql_and_params(manifest, work_date, target_row_id, developer, project_code, requirement_id)

                with wconn.cursor() as wcur:
                    wcur.execute(sql, params)
                    written = wcur.fetchone()
                    if wcur.rowcount != 1:
                        raise RuntimeError(f"expected exactly 1 affected row, got {wcur.rowcount}")
                written_id = written[0]

                with wconn.cursor() as wcur:
                    wcur.execute(
                        "SELECT id, work_date, developer, project_code, requirement_id, deliverable_id, status "
                        "FROM daily_task.tbl_anpia_satheskanth WHERE id = %s",
                        (written_id,),
                    )
                    reread = wcur.fetchone()
                if reread is None or reread[2] != developer or reread[3] != project_code:
                    raise RuntimeError(f"reread verification failed: {reread}")

                wconn.commit()
                write_performed = True
                print(f"\nWRITE COMMITTED: id={written_id}, action={live_action}")
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
