# MCP Batched Extraction Evidence

**What this is:** Full record of the keyset-paginated MCP batch extraction that produced the complete, uncapped 30-day dataset after the initial bulk-query timeout and the credential-not-available finding.

**Why it exists:** Documents exactly how the "no cutoff, all combinations" requirement was actually satisfied without credential-based access, which real batches ran, and what remains outstanding (7-day/14-day periods).

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Technical reviewer: Sajeesan. Owner: Satheskanth.

---

## Reason batching was selected

1. A single unbounded query across all 8 account+marketplace combinations timed out (300s, no response) — see `2026-07-17__mcp_bulk_fetch_timeout_evidence.md`.
2. Credential-based direct PostgreSQL access was checked and found unavailable — see `2026-07-17__credential_environment_check.md` (no `EICA_PH_TASK_PG*` or generic `PG*` environment variables set anywhere in this session's environment; the referenced template scripts are already fully remediated with no embedded secrets).
3. Per explicit instruction, MCP batching using keyset pagination (never OFFSET) was approved as the path forward, scoped one `(period, account, marketplace)` combination at a time, with aggregation happening before pagination (never paginating raw source rows).

## Batch strategy

- **Row identity / dedup key:** `account + marketplace + asin + resolved_sku`, per the design document.
- **Ordering key for pagination:** `(asin, resolved_sku)` ascending, using the explicit `asin > :last OR (asin = :last AND resolved_sku > :last_sku)` pattern (tuple comparison avoided for portability).
- **Aggregation before pagination:** each batch query aggregates PPC (SB-excluded, `amzn.gr.*`-excluded), sales, last-sale-date, and stock independently, resolves the ASIN→SKU bridge via `listing_data` (`DISTINCT ON` with a deterministic tiebreaker — see the SQL validation report for the defect this fixed), and joins only the pre-aggregated results — exactly the sequence from the design document, applied per combination.
- **Initial batch size:** started at 300 (matching the earlier proven-safe sample size).
- **Batch size increase:** after two clean 300-row batches with no timeout, batch size was increased to 1,200, then 2,100 rows per call — all subsequent batches used 2,100 as the standard size, since the earlier timeout was determined to be unrelated to raw response size (300-row batches had already produced ~170KB responses handled via the platform's automatic file-offload mechanism without issue) and more likely a transient/query-plan issue specific to one earlier attempt. This significantly reduced the total number of calls needed (roughly 25 batches total instead of an estimated 165+ at a conservative 300-row size).
- **Final batch size:** 2,100 (unchanged from the increase — no further timeouts were encountered after the initial one, aside from two transient socket-closed errors that succeeded on immediate retry).

## Periods processed

**30-day period (2026-06-16 to 2026-07-15): COMPLETE for all 8 combinations.**
**7-day and 14-day periods: NOT YET EXTRACTED** — the same proven mechanism applies but was not run in this session due to time; this is the primary remaining blocker, not a technical failure.

## Account/marketplace combinations (30-day period)

| Combination | Batches | Rows | Status |
|---|---|---|---|
| DCVoltage × France | 0 (confirmed zero via `COUNT(*)`) | 0 | ZERO_SOURCE_ROWS |
| DCVoltage × Italy | 5 | 3,947 | COMPLETE |
| DCVoltage × Germany | 2 | 3,861 | COMPLETE |
| LEDSONE × Italy | 2 | 3,869 | COMPLETE |
| LEDSONE × France | 3 | 5,630 | COMPLETE |
| LEDSONE × Germany | 4 | 6,503 | COMPLETE |
| DCVoltage × UK | 7 | 12,895 | COMPLETE |
| LEDSONE × UK | 7 | 14,643 | COMPLETE (confirmed exhausted — final keyset query returned 0 rows) |
| **Total** | **30 batches** | **51,348 rows** | **8 of 8 combinations complete** |

## Retries

- One query (LEDSONE/Germany batch, and separately DCVoltage/UK batch) hit a transient `socket connection was closed unexpectedly` error — both succeeded immediately on retry with the identical query, no batch size reduction needed, no data lost (the failed attempt produced no batch file, so no duplicate/partial data risk).
- No batch required more than one retry. No key range was skipped.

## Failed ranges

**None.** Every combination reached a terminating condition: either an explicit zero-row confirmation (DCVoltage×France) or a final batch returning fewer rows than requested / a follow-up query returning zero rows (all others).

## Expected vs. fetched counts

The "expected" count for each combination was the `COUNT(DISTINCT asin)` measured during the multi-account/marketplace discovery addendum (e.g. DCVoltage×Italy: 3,894 ASINs). Actual row counts are slightly higher (e.g. 3,947) because a small percentage of ASINs resolve to multiple SKUs — consistent with, and not contradicting, the ~3.3% multi-SKU-ASIN rate already documented in the original join-cardinality evidence.

## Duplicates

**Zero conflicting duplicate keys** across the full merged 51,348-row dataset, confirmed by `checkpoint_manager.merge_period()`'s conflict-detection logic (which would raise a flag if the same `account+marketplace+asin+resolved_sku` key appeared with different data across batches — none did).

## Checkpoint and dataset paths

- Checkpoint: `09_OUTPUTS/logs/mcp_checkpoints/2026-07-17__mcp_extraction_checkpoint.json`
- Raw batch files: `09_OUTPUTS/logs/mcp_batches/2026-07-17__30d__<account>__<marketplace>__batch_NNNN.jsonl` (30 files)
- Merged complete 30-day dataset: `09_OUTPUTS/logs/2026-07-17__amazon_report_30d_complete.json` (51,348 rows)

## Database writes

**NONE** — every query executed was `SELECT`, read-only.

## Credential exposure

**NONE** — no credential value was read, logged, or used at any point in this extraction; it was performed entirely through the pre-authorized `PRIMARY_SKILLS_MCP` tool connection.

## Status

**30-day period: COMPLETE.** 7-day/14-day periods: NOT STARTED.

## Pass/fail rule

PASS for the 30-day period specifically (every combination reached a terminal, evidenced state; zero duplicates; zero skipped ranges). Overall extraction is **PARTIAL** pending 7-day/14-day.

## Next action

Repeat the identical batching process (same SQL shape, `date BETWEEN` bounds changed to the 7-day and 14-day windows) for the remaining two periods.
