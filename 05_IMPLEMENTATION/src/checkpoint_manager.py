"""
checkpoint_manager.py -- REQ-AMZ-NMP-001-D01

Utilities for the keyset-paginated MCP batch extraction process. This module
does NOT call the database itself (the MCP tool connection is only reachable
through the implementing agent's own tool-calling interface, not from a
Python subprocess) -- it manages the LOCAL side of the process: writing/
reading batch JSONL files, tracking the extraction checkpoint, and merging +
deduplicating the final per-period datasets.

Row identity (dedup key) = account + marketplace + asin + resolved_sku,
per 04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md.
"""

import json
import os
from datetime import datetime, timezone

BATCH_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "09_OUTPUTS", "logs", "mcp_batches")
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "09_OUTPUTS", "logs", "mcp_checkpoints")
CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "2026-07-17__mcp_extraction_checkpoint.json")


def _now():
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs():
    os.makedirs(BATCH_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)


def load_checkpoint():
    ensure_dirs()
    if not os.path.exists(CHECKPOINT_FILE):
        return {"requirement_id": "REQ-AMZ-NMP-001-D01", "combinations": {}}
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_checkpoint(cp):
    ensure_dirs()
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2)


def combo_key(period, account, marketplace):
    return f"{period}d__{account.lower()}__{marketplace.lower()}"


def record_batch(period, account, marketplace, batch_num, rows, last_asin, last_sku, status="in_progress"):
    """
    rows: list of clean (already-parsed, no Decimal/datetime objects) row dicts
    for this batch. Writes them to a batch JSONL file and updates the checkpoint.
    """
    ensure_dirs()
    key = combo_key(period, account, marketplace)
    fname = f"2026-07-17__{key}__batch_{batch_num:04d}.jsonl"
    fpath = os.path.join(BATCH_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    cp = load_checkpoint()
    combos = cp.setdefault("combinations", {})
    entry = combos.setdefault(key, {
        "period": period, "account": account, "marketplace": marketplace,
        "batches": [], "cumulative_rows": 0, "status": "in_progress",
    })
    entry["batches"].append({
        "batch_num": batch_num, "file": fname, "rows": len(rows),
        "last_asin": last_asin, "last_sku": last_sku, "timestamp": _now(),
    })
    entry["cumulative_rows"] = sum(b["rows"] for b in entry["batches"])
    entry["status"] = status
    entry["last_asin"] = last_asin
    entry["last_sku"] = last_sku
    save_checkpoint(cp)
    return fpath


def mark_status(period, account, marketplace, status, note=None):
    cp = load_checkpoint()
    key = combo_key(period, account, marketplace)
    combos = cp.setdefault("combinations", {})
    entry = combos.setdefault(key, {
        "period": period, "account": account, "marketplace": marketplace,
        "batches": [], "cumulative_rows": 0,
    })
    entry["status"] = status
    if note:
        entry["note"] = note
    entry["updated_at"] = _now()
    save_checkpoint(cp)


def merge_period(period, out_path):
    """
    Reads all COMPLETE combinations' batch files for a given period, merges,
    deduplicates by (account, marketplace, asin, resolved_sku), and writes the
    complete period dataset. Raises on conflicting duplicate values (same key,
    different data) rather than silently picking one.
    """
    cp = load_checkpoint()
    seen = {}
    conflicts = []
    combos_included = []
    for key, entry in cp.get("combinations", {}).items():
        if entry["period"] != period:
            continue
        if entry["status"] not in ("complete", "zero_source_rows"):
            continue
        combos_included.append(key)
        for batch in entry.get("batches", []):
            fpath = os.path.join(BATCH_DIR, batch["file"])
            if not os.path.exists(fpath):
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    dedup_key = (row["account"], row["marketplace"], row["asin"], row["resolved_sku"])
                    if dedup_key in seen:
                        if seen[dedup_key] != row:
                            conflicts.append(dedup_key)
                    else:
                        seen[dedup_key] = row

    merged_rows = list(seen.values())
    merged_rows.sort(key=lambda r: (r["account"], r["marketplace"], r["asin"], r["resolved_sku"]))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged_rows, f)

    return {
        "period": period,
        "combinations_included": combos_included,
        "total_unique_rows": len(merged_rows),
        "conflicting_duplicate_keys": conflicts,
        "output_path": out_path,
    }


def summary():
    cp = load_checkpoint()
    out = {}
    for key, entry in cp.get("combinations", {}).items():
        out[key] = {"status": entry.get("status"), "cumulative_rows": entry.get("cumulative_rows", 0)}
    return out
