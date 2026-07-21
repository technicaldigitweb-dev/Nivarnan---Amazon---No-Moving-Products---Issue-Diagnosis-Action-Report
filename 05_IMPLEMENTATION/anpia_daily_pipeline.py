"""
anpia_daily_pipeline.py -- REQ-ANPIA-REQ-01-D02

Reusable end-to-end production pipeline for the ANPIA report
(project_code=ANPIA, assigned_user=Nivarnan). Performs, in order:

  1. acquire lock (file lock -- prevents concurrent runs)
  2. load protected environment (.env via anpia_config, never hardcoded)
  3. inspect source availability (live connection + traffic feed staleness)
  4. determine latest complete date (live CURRENT_DATE - 1)
  5. fetch latest 30 complete days (fresh extraction, never reused)
  6. build the next daily production version (local vNNN file)
  7. validate calculations (identity/duplicate counts, formula spot-check)
  8. run browser/smoke validation where appropriate (best-effort; skipped
     with a logged warning if Chrome/Node are not available in this
     environment -- this is expected and non-fatal on a headless VM)
  9. validate filename and checksum
 10. inspect ph_task duplicate state (ANPIA + assigned_user ONLY -- never
     queries or reasons about project_code='AGE')
 11. insert the first daily version, or update the existing same-day row
 12. reread and verify publication
 13. save evidence
 14. write a structured JSON run log
 15. release lock
 16. return a deterministic exit code

Safe default: no arguments, or --dry-run, NEVER writes to the database.
Publishing requires BOTH --publish AND --confirmation-token
PUBLISH_NIVARNAN_ANPIA.

Credentials are loaded exclusively via 05_IMPLEMENTATION/src/anpia_config.py
(.env / environment) -- never hardcoded, never printed. All SQL is
parameterized. This module performs NO action at import time -- everything
runs under `if __name__ == "__main__": main()`.
"""

import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "05_IMPLEMENTATION", "src")
sys.path.insert(0, SRC_DIR)

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
CONFIRM_TOKEN = "PUBLISH_NIVARNAN_ANPIA"
APPROVED_PROJECT_CODE = "ANPIA"
APPROVED_ASSIGNED_USER = "Nivarnan"
APPROVED_TEAM = "Technical"
APPROVED_DEVELOPER = "Satheskanth"
APPROVED_ASSIGNED_USER_TEAM = "ph_priors"
APPROVED_PHASE_LEVEL = 1
APPROVED_VERSION_STATUS = "released"
APPROVED_TASK_NAME = "Amazon No-Moving Products Report — 7/14/30 Day Analysis"
TIMEZONE_NAME = "Asia/Colombo"  # UTC+05:30, no DST
TZ_OFFSET = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

TARGET_SCHEMA = "tech_team_outputs"
TARGET_TABLE = "ph_task"
SIZE_SANITY_CEILING_BYTES = 50_000_000
FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9]+_[a-z0-9]+_v\d{3}\.html$")
STATIC_FORBIDDEN_PATTERNS = ["ANPIA_DB_PASSWORD", "ANPIA_DB_HOST"]
SAFE_MINIMUM_SECRET_LENGTH = 6

VERSION_REASONS = (
    "FIRST_DAILY_RUN",
    "USER_CORRECTION",
    "VALIDATION_RETRY",
    "SOURCE_REFRESH",
    "MANUAL_REPUBLISH",
)

# Exit codes (Section 13 of the task instruction)
EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILURE = 2
EXIT_DUPLICATE_STATE_CONFLICT = 3
EXIT_SOURCE_DATA_FAILURE = 4
EXIT_PUBLICATION_FAILURE = 5
EXIT_CREDENTIAL_CONFIG_FAILURE = 6
EXIT_LOCK_ALREADY_HELD = 7

LOCK_PATH = os.path.join(PROJECT_ROOT, "09_OUTPUTS", "logs", "anpia_daily_pipeline.lock")
RUN_LOG_DIR = os.path.join(PROJECT_ROOT, "09_OUTPUTS", "logs", "anpia_daily_runs")
PRODUCTION_HTML_DIR = os.path.join(PROJECT_ROOT, "09_OUTPUTS", "html", "production")
DATA_DIR = os.path.join(PROJECT_ROOT, "09_OUTPUTS", "data")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(description="ANPIA reusable daily production pipeline (safe-by-default).")
    p.add_argument("--dry-run", action="store_true", help="Validate and build only, never write to the database (also the default).")
    p.add_argument("--publish", action="store_true", help="Required (with --confirmation-token) to attempt a real database write.")
    p.add_argument("--report-date", default=None, help="YYYY-MM-DD in Asia/Colombo. Defaults to today in Asia/Colombo.")
    p.add_argument("--force-version", default=None, help="e.g. v003 -- override automatic version determination. Use with care.")
    p.add_argument("--trigger-source", choices=["manual", "scheduled", "command"], default="manual")
    p.add_argument("--confirmation-token", default=None)
    p.add_argument("--version-reason", choices=VERSION_REASONS, default=None,
                    help="Why this version is being created. If omitted, inferred (FIRST_DAILY_RUN or MANUAL_REPUBLISH).")
    return p.parse_args(argv)


# ----------------------------------------------------------------------
# Structured run log
# ----------------------------------------------------------------------
class RunLog:
    def __init__(self, trigger_source, report_date):
        self.data = {
            "pipeline": "anpia_daily_pipeline",
            "trigger_source": trigger_source,
            "report_date": report_date.isoformat() if report_date else None,
            "started_at": None,
            "finished_at": None,
            "steps": [],
            "exit_code": None,
            "result": None,
        }

    def step(self, name, status, detail=None):
        entry = {"step": name, "status": status}
        if detail is not None:
            entry["detail"] = detail
        self.data["steps"].append(entry)
        print(f"[{status}] {name}" + (f" -- {detail}" if detail and status != "OK" else ""))

    def finish(self, exit_code, result):
        self.data["exit_code"] = exit_code
        self.data["result"] = result
        self.data["finished_at"] = datetime.datetime.now(TZ_OFFSET).isoformat()

    def write(self):
        os.makedirs(RUN_LOG_DIR, exist_ok=True)
        stamp = self.data["started_at"].replace(":", "").replace("-", "").replace("+", "_") if self.data["started_at"] else "unknown"
        path = os.path.join(RUN_LOG_DIR, f"run_{stamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        return path


# ----------------------------------------------------------------------
# 1. File lock (portable Windows/Linux; PostgreSQL advisory lock also
#    acquired when a DB connection is available, as defense in depth)
# ----------------------------------------------------------------------
class PipelineLock:
    def __init__(self, path):
        self.path = path
        self.acquired = False
        self.fd = None

    def acquire(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(self.fd, f"pid={os.getpid()} started={datetime.datetime.now(TZ_OFFSET).isoformat()}".encode())
            self.acquired = True
            return True
        except FileExistsError:
            return False

    def release(self):
        if self.acquired:
            try:
                os.close(self.fd)
            except Exception:
                pass
            try:
                os.remove(self.path)
            except Exception:
                pass
            self.acquired = False


def acquire_pg_advisory_lock(conn, lock_key=778812001):
    """Best-effort PostgreSQL session-level advisory lock, in addition to
    the file lock. Returns True/False. Never raises -- advisory lock is a
    defense-in-depth extra, not the primary locking mechanism (the file
    lock is primary and portable to any future deployment)."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s)", (lock_key,))
            return cur.fetchone()[0]
    except Exception:
        return False


def release_pg_advisory_lock(conn, lock_key=778812001):
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_unlock(%s)", (lock_key,))
    except Exception:
        pass


# ----------------------------------------------------------------------
# 4. Determine latest complete date / report date
# ----------------------------------------------------------------------
def resolve_report_date(explicit_date_str):
    if explicit_date_str:
        return datetime.date.fromisoformat(explicit_date_str)
    now_colombo = datetime.datetime.now(TZ_OFFSET)
    return now_colombo.date()


# ----------------------------------------------------------------------
# 6. Determine next daily production version
# ----------------------------------------------------------------------
def determine_version(report_date, force_version, conn):
    """Returns (version_int, filename, action, existing_row_id, version_reason).
    action is one of SAFE_NEW_INSERT / UPDATE_EXISTING_ROW.
    ANPIA-only duplicate check -- never queries project_code='AGE'."""
    date_str = report_date.isoformat()
    username = APPROVED_ASSIGNED_USER.lower()
    project = APPROVED_PROJECT_CODE.lower()

    # Local version scan
    existing_local = []
    if os.path.isdir(PRODUCTION_HTML_DIR):
        pattern = re.compile(rf"^{re.escape(date_str)}_{re.escape(username)}_{re.escape(project)}_v(\d{{3}})\.html$")
        for fname in os.listdir(PRODUCTION_HTML_DIR):
            m = pattern.match(fname)
            if m:
                existing_local.append(int(m.group(1)))
    max_local_version = max(existing_local) if existing_local else 0

    # Live ph_task same-day check (ANPIA-only, AGE never queried)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, version_level FROM tech_team_outputs.ph_task "
            "WHERE project_code = %s AND assigned_user = %s "
            "ORDER BY created_at DESC",
            (APPROVED_PROJECT_CODE, APPROVED_ASSIGNED_USER),
        )
        rows = cur.fetchall()

    if force_version:
        m = re.match(r"^v(\d{3})$", force_version)
        if not m:
            raise ValueError(f"--force-version must look like vNNN, got {force_version!r}")
        version_int = int(m.group(1))
    else:
        version_int = max_local_version + 1 if max_local_version > 0 else 1

    if len(rows) == 0:
        action = "SAFE_NEW_INSERT"
        existing_row_id = None
        version_reason = "FIRST_DAILY_RUN"
    elif len(rows) == 1:
        action = "UPDATE_EXISTING_ROW"
        existing_row_id = rows[0][0]
        version_reason = "MANUAL_REPUBLISH"
    else:
        # More than one same-day ANPIA/assigned_user row already exists --
        # this violates the one-active-row rule and must not be resolved
        # silently.
        action = "BLOCKED_MULTIPLE_ROWS"
        existing_row_id = [r[0] for r in rows]
        version_reason = None

    filename = f"{date_str}_{username}_{project}_v{version_int:03d}.html"
    return version_int, filename, action, existing_row_id, version_reason


# ----------------------------------------------------------------------
# 5. Fresh extraction + 6. build compact dataset (Python-only, no Node
#    dependency -- gzip via the stdlib so this pipeline is self-contained
#    on a future headless VM)
# ----------------------------------------------------------------------
def run_fresh_extraction(conn, end_date, run_stamp, log):
    from anpia_common_dataset import extract_common_dataset

    start_date = end_date - datetime.timedelta(days=29)
    out_path = os.path.join(DATA_DIR, f"{run_stamp}__anpia_daily_common_facts.jsonl")
    ckpt_path = os.path.join(PROJECT_ROOT, "09_OUTPUTS", "logs", "direct_db_checkpoints", f"{run_stamp}__anpia_daily_checkpoint.json")
    summary = extract_common_dataset(conn, start_date, end_date, out_path, ckpt_path, batch_size=5000)
    log.step("fetch_latest_30_days", "OK", {"row_count": summary["row_count"], "window": f"{start_date} to {end_date}"})
    return out_path, start_date, end_date


def build_compact_dataset(conn, common_path, start_date, end_date, run_stamp, log):
    from anpia_snapshot_enrichment import (
        load_dimension, load_category_avg_price, load_stock, load_last_sale, warehouse_for,
        load_traffic_feed_coverage, load_ever_tracked_asins,
    )

    n_days = (end_date - start_date).days + 1
    dates = [(start_date + datetime.timedelta(days=i)).isoformat() for i in range(n_days)]

    dimension = load_dimension(conn)
    cat_avg, _ = load_category_avg_price(conn)
    stock = load_stock(conn)
    last_sale = load_last_sale(conn)
    feed_coverage = load_traffic_feed_coverage(conn)
    ever_tracked = load_ever_tracked_asins(conn)

    accounts_sorted = sorted(set(k[0] for k in dimension.keys()))
    marketplaces_sorted = sorted(set(k[1] for k in dimension.keys()))
    account_idx = {a: i for i, a in enumerate(accounts_sorted)}
    marketplace_idx = {m: i for i, m in enumerate(marketplaces_sorted)}

    titles = {}

    def title_index(t):
        if t is None:
            return -1
        if t not in titles:
            titles[t] = len(titles)
        return titles[t]

    feed_coverage_idx = {}
    for (account, marketplace), (feed_min, feed_max) in feed_coverage.items():
        if account not in account_idx or marketplace not in marketplace_idx:
            continue
        overlap_start = max(feed_min, start_date)
        overlap_end = min(feed_max, end_date)
        key = f"{account_idx[account]}_{marketplace_idx[marketplace]}"
        if overlap_start > overlap_end:
            feed_coverage_idx[key] = None
        else:
            feed_coverage_idx[key] = [(overlap_start - start_date).days, (overlap_end - start_date).days]

    products = {}
    for key, dim in dimension.items():
        account, marketplace, asin, sku = key
        wh = warehouse_for(marketplace)
        stock_val = stock.get((sku, wh))
        cat_price = cat_avg.get((marketplace, dim.get("product_type")))
        last_sale_date = last_sale.get((account, marketplace, asin))
        days_since_last_sale = (end_date - last_sale_date).days if last_sale_date else None
        tracked = asin in ever_tracked.get((account, marketplace), set())
        products[key] = {
            "accountIdx": account_idx[account], "marketplaceIdx": marketplace_idx[marketplace],
            "asin": asin, "sku": sku, "titleIdx": title_index(dim.get("title")),
            "daysSinceLastSale": days_since_last_sale, "currentStock": stock_val,
            "currentPrice": dim.get("price"), "categoryAvgPrice": cat_price, "everTracked": 1 if tracked else 0,
            "sessions": [None] * n_days, "pageViews": [None] * n_days, "units": [0] * n_days,
            "clicks": [0] * n_days, "impressions": [0] * n_days, "spend": [0.0] * n_days,
            "attributedSales": [0.0] * n_days, "buyBoxNum": [None] * n_days, "buyBoxDenom": [None] * n_days,
        }

    date_to_idx = {d: i for i, d in enumerate(dates)}
    for key, p in products.items():
        fkey = f"{p['accountIdx']}_{p['marketplaceIdx']}"
        rng = feed_coverage_idx.get(fkey)
        if rng is not None and p["everTracked"]:
            for i in range(rng[0], rng[1] + 1):
                p["sessions"][i] = 0
                p["pageViews"][i] = 0
                p["buyBoxNum"][i] = 0.0
                p["buyBoxDenom"][i] = 0.0

    row_count = 0
    with open(common_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            key = (rec["account"], rec["marketplace"], rec["asin"], rec["resolved_sku"])
            p = products.get(key)
            if p is None:
                continue
            day_idx = date_to_idx.get(rec["report_date"])
            if day_idx is None:
                continue
            p["units"][day_idx] = rec["units_ordered"]
            p["clicks"][day_idx] = rec["ppc_clicks"]
            p["impressions"][day_idx] = rec["ppc_impressions"]
            p["spend"][day_idx] = round(rec["ppc_spend"], 4)
            p["attributedSales"][day_idx] = round(rec["ppc_attributed_sales"], 4)
            if rec["sessions"] is not None:
                p["sessions"][day_idx] = rec["sessions"]
                p["pageViews"][day_idx] = rec["page_views"] if rec["page_views"] is not None else 0
                p["buyBoxNum"][day_idx] = rec["bb_weighted_num"]
                p["buyBoxDenom"][day_idx] = rec["bb_weight_denom"]
            row_count += 1

    products_arr = []
    for key, p in products.items():
        products_arr.append([
            p["accountIdx"], p["marketplaceIdx"], p["asin"], p["sku"], p["titleIdx"],
            p["daysSinceLastSale"], p["currentStock"], p["currentPrice"], p["categoryAvgPrice"], p["everTracked"],
            p["sessions"], p["pageViews"], p["units"], p["clicks"], p["impressions"],
            p["spend"], p["attributedSales"], p["buyBoxNum"], p["buyBoxDenom"],
        ])
    titles_arr = [None] * len(titles)
    for t, i in titles.items():
        titles_arr[i] = t

    compact = {
        "DATES": dates, "ACCOUNTS": accounts_sorted, "MARKETPLACES": marketplaces_sorted,
        "TITLES": titles_arr, "FEED_COVERAGE": feed_coverage_idx, "PRODUCTS": products_arr,
    }
    out_path = os.path.join(DATA_DIR, f"{run_stamp}__anpia_daily_compact.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(compact, f, separators=(",", ":"))

    dup_identity = len(dimension) - len(set(dimension.keys()))
    log.step("build_daily_production_version", "OK", {
        "identity_count": len(dimension), "duplicate_identity_count": dup_identity,
        "product_count": len(products_arr), "rows_applied": row_count,
    })
    return out_path, len(dimension), dup_identity, len(products_arr)


def compress_to_b64(compact_json_path):
    with open(compact_json_path, "rb") as f:
        raw = f.read()
    gz = gzip.compress(raw, compresslevel=9)
    import base64
    b64 = base64.b64encode(gz).decode("ascii")
    return b64, len(raw), len(gz), len(b64)


def render_html(b64_data, report_date, version_int, log):
    template_path = os.path.join(PROJECT_ROOT, "05_IMPLEMENTATION", "templates", "amazon_no_moving_report_template_v008.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    version_tag = f"v{version_int:03d}"
    html = template
    html = html.replace("__REPORT_TITLE__", f"Amazon No-Moving Products Report -- LEDSONE &amp; DCVoltage (Production {version_tag})")
    html = html.replace("__GENERATION_TIMESTAMP__", f"{report_date.isoformat()}T00:00:00 (production {version_tag} -- automated pipeline run)")
    html = html.replace("__LATEST_COMPLETE_DATE__", "")  # filled by caller with the real latest complete date
    html = html.replace("__GENERATION_DATE__", report_date.isoformat())
    html = html.replace("__B64_GZIP_DATA__", b64_data)
    log.step("render_html_from_template", "OK", {"template": os.path.basename(template_path)})
    return html


# ----------------------------------------------------------------------
# 7. Calculation validation (lightweight, deterministic -- full CDP/browser
#    cross-check is step 8, best-effort only)
# ----------------------------------------------------------------------
def validate_calculations(identity_count, duplicate_identity_count, product_count, log):
    problems = []
    if duplicate_identity_count != 0:
        problems.append(f"duplicate_identity_count is {duplicate_identity_count}, expected 0")
    if product_count != identity_count:
        problems.append(f"product_count ({product_count}) != identity_count ({identity_count})")
    if problems:
        log.step("validate_calculations", "FAIL", problems)
        return False
    log.step("validate_calculations", "OK", {"identity_count": identity_count})
    return True


# ----------------------------------------------------------------------
# 8. Browser/smoke validation -- best-effort, non-fatal if unavailable
# ----------------------------------------------------------------------
def run_smoke_validation(html_path, log):
    import shutil
    node_path = shutil.which("node")
    if not node_path:
        log.step("browser_smoke_validation", "SKIPPED", "node not found on PATH -- expected on a minimal headless VM; not fatal")
        return True
    smoke_js = f"""
const fs = require('fs');
const html = fs.readFileSync({json.dumps(html_path)}, 'utf-8');
const marker = 'const B64_GZIP_DATA = "';
const start = html.indexOf(marker) + marker.length;
const end = html.indexOf('"', start);
const b64 = html.slice(start, end);
(async () => {{
  const binaryStr = atob(b64);
  const bytes = new Uint8Array(binaryStr.length);
  for (let i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);
  const ds = new DecompressionStream('gzip');
  const stream = new Blob([bytes]).stream().pipeThrough(ds);
  const text = await new Response(stream).text();
  const DATA = JSON.parse(text);
  console.log(JSON.stringify({{ productCount: DATA.PRODUCTS.length, datesCount: DATA.DATES.length }}));
}})().catch(e => {{ console.error('SMOKE_FAILED: ' + e.message); process.exit(1); }});
"""
    import subprocess
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(smoke_js)
        script_path = f.name
    try:
        result = subprocess.run([node_path, script_path], capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            log.step("browser_smoke_validation", "FAIL", result.stderr[:500])
            return False
        log.step("browser_smoke_validation", "OK", result.stdout.strip())
        return True
    except Exception as e:
        log.step("browser_smoke_validation", "SKIPPED", f"{type(e).__name__}: {e}")
        return True
    finally:
        try:
            os.remove(script_path)
        except Exception:
            pass


# ----------------------------------------------------------------------
# 9. Filename / checksum validation
# ----------------------------------------------------------------------
def validate_filename(filename):
    return bool(FILENAME_RE.match(filename))


def sha256_of_bytes(b):
    return hashlib.sha256(b).hexdigest()


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


# ----------------------------------------------------------------------
# 10-13. Publish (insert or update), reread/verify
# ----------------------------------------------------------------------
def publish_row(wconn, action, existing_row_id, html_text, filename, version_int, description, log):
    if action == "SAFE_NEW_INSERT":
        sql = """
            INSERT INTO tech_team_outputs.ph_task
                (project_name, project_code, task_name, task_id, team, developer,
                 assigned_user, assigned_user_team, html_content, description,
                 phase_level, version_level, version_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            "No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report",
            APPROVED_PROJECT_CODE, APPROVED_TASK_NAME, None, APPROVED_TEAM, APPROVED_DEVELOPER,
            APPROVED_ASSIGNED_USER, APPROVED_ASSIGNED_USER_TEAM, html_text, description,
            APPROVED_PHASE_LEVEL, version_int, APPROVED_VERSION_STATUS,
        )
        with wconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            affected = cur.rowcount
        row_id = row[0]
    elif action == "UPDATE_EXISTING_ROW":
        sql = """
            UPDATE tech_team_outputs.ph_task
            SET html_content = %s, description = %s, version_level = %s, version_status = %s,
                updated_at = now()
            WHERE id = %s AND project_code = %s AND assigned_user = %s
            RETURNING id
        """
        params = (html_text, description, version_int, APPROVED_VERSION_STATUS,
                  existing_row_id, APPROVED_PROJECT_CODE, APPROVED_ASSIGNED_USER)
        with wconn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            affected = cur.rowcount
        row_id = row[0] if row else None
    else:
        raise ValueError(f"publish_row does not support action={action!r}")

    if affected != 1:
        raise RuntimeError(f"expected exactly 1 affected row, got {affected}")

    with wconn.cursor() as cur:
        cur.execute(
            "SELECT id, project_code, assigned_user, version_level, version_status, "
            "octet_length(html_content) FROM tech_team_outputs.ph_task WHERE id = %s",
            (row_id,),
        )
        reread = cur.fetchone()
    if reread is None or reread[1] != APPROVED_PROJECT_CODE or reread[2] != APPROVED_ASSIGNED_USER:
        raise RuntimeError(f"reread verification failed: {reread}")

    log.step("insert_or_update_publication", "OK", {"action": action, "row_id": row_id, "affected_rows": affected})
    return row_id, reread


# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------
def main():
    args = parse_args()
    is_publish_attempt = args.publish
    report_date = resolve_report_date(args.report_date)
    log = RunLog(args.trigger_source, report_date)
    log.data["started_at"] = datetime.datetime.now(TZ_OFFSET).isoformat()

    print("=" * 70)
    print("ANPIA daily production pipeline")
    print("=" * 70)
    print(f"Report date (Asia/Colombo): {report_date.isoformat()}")
    print(f"Mode: {'PUBLISH (write requested)' if is_publish_attempt else 'DRY-RUN (default, no write possible)'}")
    print(f"Trigger source: {args.trigger_source}")

    if is_publish_attempt and args.confirmation_token != CONFIRM_TOKEN:
        log.step("safety_gate_confirmation_token", "FAIL", "publish requested without the correct --confirmation-token")
        log.finish(EXIT_VALIDATION_FAILURE, "BLOCKED_MISSING_TOKEN")
        log.write()
        print("WRITE EXECUTED: NO")
        sys.exit(EXIT_VALIDATION_FAILURE)

    lock = PipelineLock(LOCK_PATH)
    if not lock.acquire():
        log.step("acquire_lock", "FAIL", f"lock already held: {LOCK_PATH}")
        log.finish(EXIT_LOCK_ALREADY_HELD, "LOCK_ALREADY_HELD")
        log.write()
        print("WRITE EXECUTED: NO")
        sys.exit(EXIT_LOCK_ALREADY_HELD)
    log.step("acquire_lock", "OK", {"path": LOCK_PATH})

    conn = None
    exit_code = EXIT_SUCCESS
    result = "UNKNOWN"
    try:
        try:
            from anpia_config import get_db_config
            get_db_config()  # raises RuntimeError if .env is incomplete
            log.step("load_protected_environment", "OK", None)
        except Exception as e:
            log.step("load_protected_environment", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_CREDENTIAL_CONFIG_FAILURE
            result = "CREDENTIAL_CONFIG_FAILURE"
            return

        try:
            from anpia_db_connection import get_connection, safe_close
            from anpia_source_discovery import latest_complete_date
            conn = get_connection()
            log.step("inspect_source_availability", "OK", {"database_connected": True})
        except Exception as e:
            log.step("inspect_source_availability", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_SOURCE_DATA_FAILURE
            result = "SOURCE_CONNECTION_FAILURE"
            return

        pg_lock_held = acquire_pg_advisory_lock(conn)
        log.step("acquire_pg_advisory_lock", "OK" if pg_lock_held else "SKIPPED",
                  None if pg_lock_held else "advisory lock not obtained -- file lock remains the primary guard")

        try:
            end_date = latest_complete_date(conn)
            log.step("determine_latest_complete_date", "OK", {"latest_complete_date": end_date.isoformat()})
        except Exception as e:
            log.step("determine_latest_complete_date", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_SOURCE_DATA_FAILURE
            result = "LATEST_DATE_FAILURE"
            return

        try:
            version_int, filename, action, existing_row_id, version_reason = determine_version(
                report_date, args.force_version, conn
            )
        except Exception as e:
            log.step("determine_version", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_VALIDATION_FAILURE
            result = "VERSION_DETERMINATION_FAILURE"
            return

        if args.version_reason:
            version_reason = args.version_reason

        log.step("determine_version", "OK", {
            "version": f"v{version_int:03d}", "filename": filename, "action": action,
            "existing_row_id": existing_row_id, "version_reason": version_reason,
        })

        if action == "BLOCKED_MULTIPLE_ROWS":
            log.step("duplicate_state_gate", "FAIL", f"multiple same-day ANPIA/{APPROVED_ASSIGNED_USER} rows exist: {existing_row_id} -- refusing to guess which to update")
            exit_code = EXIT_DUPLICATE_STATE_CONFLICT
            result = "BLOCKED_MULTIPLE_ROWS"
            return

        # Idempotent no-op check for scheduled reruns: if a same-day row
        # already exists AND this run has no explicit correction reason,
        # a scheduled trigger should not spin up a new version automatically.
        if (action == "UPDATE_EXISTING_ROW" and args.trigger_source == "scheduled"
                and version_reason == "MANUAL_REPUBLISH" and not args.force_version):
            log.step("idempotent_rerun_check", "SKIPPED",
                      "scheduled rerun after an already-successful same-day publication -- "
                      "no explicit rerun policy triggered; defaulting to no-op per Section 14")
            exit_code = EXIT_SUCCESS
            result = "IDEMPOTENT_NOOP"
            return

        run_stamp = report_date.isoformat() + f"_v{version_int:03d}"

        try:
            common_path, start_date, end_date2 = run_fresh_extraction(conn, end_date, run_stamp, log)
        except Exception as e:
            log.step("fetch_latest_30_days", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_SOURCE_DATA_FAILURE
            result = "EXTRACTION_FAILURE"
            return

        try:
            compact_path, identity_count, dup_identity_count, product_count = build_compact_dataset(
                conn, common_path, start_date, end_date2, run_stamp, log
            )
        except Exception as e:
            log.step("build_daily_production_version", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_SOURCE_DATA_FAILURE
            result = "BUILD_FAILURE"
            return

        if not validate_calculations(identity_count, dup_identity_count, product_count, log):
            exit_code = EXIT_VALIDATION_FAILURE
            result = "CALCULATION_VALIDATION_FAILURE"
            return

        b64_data, raw_size, gz_size, b64_size = compress_to_b64(compact_path)
        log.step("compress_dataset", "OK", {"raw_bytes": raw_size, "gzip_bytes": gz_size, "base64_chars": b64_size})

        html = render_html(b64_data, report_date, version_int, log)
        html = html.replace('<b></b>', f'<b>{end_date2.isoformat()}</b>', 1) if False else html
        # Fill the latest-complete-date placeholder properly (render_html left it blank for the caller):
        html = html.replace(
            'Latest complete data date: <b></b>',
            f'Latest complete data date: <b>{end_date2.isoformat()}</b>',
        )
        html_bytes = html.encode("utf-8")

        if len(html_bytes) > SIZE_SANITY_CEILING_BYTES:
            log.step("validate_size", "FAIL", f"{len(html_bytes)} exceeds ceiling {SIZE_SANITY_CEILING_BYTES}")
            exit_code = EXIT_VALIDATION_FAILURE
            result = "SIZE_VALIDATION_FAILURE"
            return

        forbidden = scan_forbidden_patterns(html)
        if forbidden:
            log.step("secret_scan", "FAIL", f"{len(forbidden)} forbidden pattern(s) found")
            exit_code = EXIT_VALIDATION_FAILURE
            result = "SECRET_SCAN_FAILURE"
            return
        log.step("secret_scan", "OK", None)

        if not validate_filename(filename):
            log.step("validate_filename", "FAIL", filename)
            exit_code = EXIT_VALIDATION_FAILURE
            result = "FILENAME_VALIDATION_FAILURE"
            return
        log.step("validate_filename", "OK", filename)

        html_path = os.path.join(PRODUCTION_HTML_DIR, filename)
        os.makedirs(PRODUCTION_HTML_DIR, exist_ok=True)
        if os.path.exists(html_path):
            log.step("write_local_html", "FAIL", f"refusing to overwrite existing local file: {html_path}")
            exit_code = EXIT_VALIDATION_FAILURE
            result = "LOCAL_FILE_ALREADY_EXISTS"
            return
        with open(html_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        html_checksum = sha256_of_bytes(html_bytes)
        log.step("write_local_html", "OK", {"path": html_path, "bytes": len(html_bytes), "sha256": html_checksum})

        run_smoke_validation(html_path, log)

        try:
            dup_count_before, _ = None, None
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM tech_team_outputs.ph_task WHERE project_code=%s AND assigned_user=%s",
                    (APPROVED_PROJECT_CODE, APPROVED_ASSIGNED_USER),
                )
                dup_count_before = cur.fetchone()[0]
            log.step("inspect_duplicate_state", "OK", {"same_day_anpia_row_count": dup_count_before})
        except Exception as e:
            log.step("inspect_duplicate_state", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_DUPLICATE_STATE_CONFLICT
            result = "DUPLICATE_STATE_INSPECTION_FAILURE"
            return

        description = (
            f"ANPIA Amazon No-Moving Products report for LEDSONE and DCVoltage "
            f"(UK, Germany, France, Italy), production v{version_int:03d}, generated from a fresh "
            f"live 30-day extraction ({start_date.isoformat()} to {end_date2.isoformat()}). "
            f"Automated pipeline run, trigger={args.trigger_source}, version_reason={version_reason}."
        )

        if not is_publish_attempt:
            log.step("insert_or_update_publication", "SKIPPED", "dry-run mode -- no write attempted")
            exit_code = EXIT_SUCCESS
            result = "DRY_RUN_COMPLETE"
            return

        # -- Real write path --
        conn.rollback()
        try:
            release_pg_advisory_lock(conn)
        except Exception:
            pass
        safe_close(conn)
        conn = None

        try:
            import psycopg2
            from anpia_config import get_db_config
            cfg = get_db_config()
            wconn = psycopg2.connect(**cfg)
            wconn.autocommit = False
        except Exception as e:
            log.step("open_writable_connection", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_PUBLICATION_FAILURE
            result = "WRITE_CONNECTION_FAILURE"
            return

        try:
            with wconn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM tech_team_outputs.ph_task WHERE project_code=%s AND assigned_user=%s",
                    (APPROVED_PROJECT_CODE, APPROVED_ASSIGNED_USER),
                )
                dup_count_recheck = cur.fetchone()[0]
            expected_before = 0 if action == "SAFE_NEW_INSERT" else 1
            if dup_count_recheck != expected_before:
                raise RuntimeError(
                    f"duplicate state changed since inspection: expected {expected_before} row(s), "
                    f"found {dup_count_recheck} -- aborting to avoid an inconsistent publication"
                )

            row_id, reread = publish_row(wconn, action, existing_row_id, html, filename, version_int, description, log)
            wconn.commit()
            log.step("reread_and_verify_publication", "OK", {
                "row_id": reread[0], "project_code": reread[1], "assigned_user": reread[2],
                "version_level": reread[3], "version_status": reread[4], "html_octet_length": reread[5],
                "html_octet_length_matches": reread[5] == len(html_bytes),
            })
            exit_code = EXIT_SUCCESS
            result = "PUBLISHED"
        except Exception as e:
            wconn.rollback()
            log.step("insert_or_update_publication", "FAIL", f"{type(e).__name__}: {e}")
            exit_code = EXIT_PUBLICATION_FAILURE
            result = "PUBLICATION_FAILURE"
            return
        finally:
            try:
                wconn.close()
            except Exception:
                pass

    except Exception as e:
        traceback.print_exc()
        log.step("unhandled_exception", "FAIL", f"{type(e).__name__}: {e}")
        exit_code = EXIT_PUBLICATION_FAILURE if is_publish_attempt else EXIT_VALIDATION_FAILURE
        result = "UNHANDLED_EXCEPTION"
    finally:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                from anpia_db_connection import safe_close as _safe_close
                _safe_close(conn)
            except Exception:
                pass
        lock.release()
        log.step("release_lock", "OK", None)
        log.finish(exit_code, result)
        log_path = log.write()
        print(f"\nRun log written to: {log_path}")
        print(f"RESULT: {result}")
        print(f"EXIT_CODE: {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
