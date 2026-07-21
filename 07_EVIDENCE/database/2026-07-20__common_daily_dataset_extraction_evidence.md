# Common Daily Dataset Extraction Evidence — ANPIA Rebuild (REQ-01-D02)

**What this is:** Record of the real, direct-PostgreSQL common-daily-dataset extraction, superseding the earlier same-day version of this file (which recorded the extraction as blocked — no credential source was available at that time).

---

## Reference-file integrity (this task)

| File | Size (bytes) | Before SHA-256 | After SHA-256 | Match |
|---|---|---|---|---|
| `Sources/db_access_templates/temp_user.py` | 1,921 | 7C3F7099B200EB6B4CFDB181149444E738E30FDEBA34A4C6DB7E51BA88B98FA8 | 7C3F7099B200EB6B4CFDB181149444E738E30FDEBA34A4C6DB7E51BA88B98FA8 | YES |
| `Sources/db_access_templates/update_table.py` | 2,588 | 9784D14AB8E0646E454A8EFFE9E049DFDD10A8FB32FE4FD63CFA29A1120FF5BC | 9784D14AB8E0646E454A8EFFE9E049DFDD10A8FB32FE4FD63CFA29A1120FF5BC | YES |
| `Sources/db_access_templates/temp_user_access_report.pdf` | 20,830 | B0C2641AE879E33E898DF8B7D109D5A630510031AAFD62B3DE274BABE175A5CD | B0C2641AE879E33E898DF8B7D109D5A630510031AAFD62B3DE274BABE175A5CD | YES |

All three reference files unchanged, not edited, not executed, not imported, not renamed/moved throughout this task.

## Previous extracted data

The 2026-07-17 30-day dataset (`09_OUTPUTS/logs/2026-07-17__amazon_report_30d_complete.json`, the 30 MCP batch files, and v002's embedded totals) was **not read, queried, or referenced** for source truth in this extraction. Marked: **SUPERSEDED FOR IMPLEMENTATION — NOT REUSED.** Files remain on disk unchanged, as historical evidence.

## Extraction method

Direct PostgreSQL via `psycopg2` (`anpia_db_connection.get_connection()`), read-only session. A single master aggregation SQL query (aggregate-before-join pattern: PPC, sales, and traffic each aggregated to `(date, account, marketplace, asin)` grain independently in their own CTE, then joined once to the ASIN→resolved-SKU bridge — never a raw fact table joined directly to another raw fact table) was executed via a **server-side (named) cursor** with `fetchmany(5000)` batching, streaming results to JSONL with a checkpoint file written after every batch.

- Common dataset path: `09_OUTPUTS/data/2026-07-20__anpia_common_daily_facts.jsonl`
- Checkpoint path: `09_OUTPUTS/logs/direct_db_checkpoints/2026-07-20__anpia_checkpoint.json`
- Window: **2026-06-20 to 2026-07-19** (30 complete days; latest complete date = yesterday relative to the source's own `CURRENT_DATE`, excluding the still-accruing current day)
- Batch size: 5,000 rows/fetch
- Elapsed: 37.5 seconds

## Extraction result

**268,404 rows.** Duplicate daily keys: **0**. Null key components: **0**. Status: `COMPLETE`.

## Sources aggregated (each independently, before any join)

- `public.ppc_performance` joined to `public.ppc` (SB-campaign exclusion) — daily PPC spend/clicks/impressions/attributed sales
- `public.order_transaction` (`order_status='Completed'`) — daily units ordered/sales revenue (primary sales source)
- `public.amz_traffic_by_asin` — daily sessions/page views/Buy-Box-weighted-numerator (secondary, account/marketplace-dependent freshness — see field classification doc)
- `public.listing_data` (`DISTINCT ON` bridge, same tiebreaker as D01's validated fix: prefer non-offer rows, then non-null price, then lowest id) — ASIN→resolved-SKU dimension

## Real defect found and fixed during this task: completeness violation

**Found:** the first version of the period-report builder only emitted rows for `(account, marketplace, asin, resolved_sku)` keys that had at least one day of recorded PPC/sales/traffic activity in the window — silently excluding true zero-activity ASIN/SKUs. This produced only 11,425/12,441/14,085 rows for the 7/14/30-day periods, directly violating the established "no cutoff — all valid combinations must appear, including zero-spend and zero-sales rows" rule, and was especially significant given this report's entire purpose is surfacing **no-moving** (i.e., often zero-activity) products.

**Fix:** the period-report builder was changed to enumerate the **full bridge dimension** (53,843 distinct account+marketplace+ASIN+resolved-SKU combinations across the 7 valid account×marketplace pairs) for every period, defaulting additive metrics to `0` and traffic-sourced fields to `N/A - source not available` where no activity was recorded — never silently dropping the row.

**Re-verified:** all three periods now correctly return **53,843 rows** each.

## Post-fix row counts

| Period | Row count |
|---|---|
| 7-day | 53,843 |
| 14-day | 53,843 |
| 30-day | 53,843 |

(Consistent, correctly, with the same universe for every period — only the additive/derived values differ, not the row population, per the "one common dataset, three filtered views" rule.)

## Database writes performed

**NONE.**

## Status

**PASS**, with one real defect found and fixed during this session (documented above, not hidden), matching this project's established practice from D01's own row-key defect discovery.

## Reviewer required

Sajeesan — technical review of the completeness fix and the aggregate-before-join SQL.

## One next step

Proceed to period aggregation, snapshot enrichment, reconciliation, and HTML generation — see the accompanying validation/reconciliation evidence files and the handover.
