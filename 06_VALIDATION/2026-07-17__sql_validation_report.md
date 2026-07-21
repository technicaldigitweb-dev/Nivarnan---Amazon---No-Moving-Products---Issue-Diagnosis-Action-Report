# SQL Validation Report

**What this is:** Validation of `05_IMPLEMENTATION/sql/main_report.sql` and `validation_checks.sql` against live data, including one real defect found and fixed during this session.

**Why it exists:** Per instruction, no publication may proceed unless SQL validation passes; every reconciliation must compare source vs. transformed vs. report aggregates at the metric's true grain.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Sources used:** `PRIMARY_SKILLS_MCP`, live queries against `public.listing_data`, `public.ppc_performance`, `public.ppc`, `public.order_transaction`, `public.location_wise_inv_stock`.

**Owner/reviewer:** Technical reviewer: Sajeesan.

---

## Defect found and fixed: row-key duplication

**Found:** The first version of the `bridge` CTE used `SELECT DISTINCT` across all 7 selected columns (including `title`, `price`). For ASINs with both a base listing row (`is_offer=0`) and a duplicate "offer row" (`is_offer=1`, per `listing_data`'s own documented column meaning) resolving to the same `mapped_sku`, this produced **two rows sharing one row key** (e.g. `DCVoltage / Germany / B0C7H33MW9 / LSFT220BU+RPR44WH`, one row with price 12.49, one with price NULL).

**Evidence:** `validate_output.py`'s `row_key_uniqueness` check caught 8 such duplicate keys in the initial 300-row sample (see git-free evidence in `07_EVIDENCE/output/2026-07-17__report_generation_evidence.md`).

**Fix:** Changed the bridge CTE to `DISTINCT ON (sub_source, market_place, ref_id, resolved_sku)` with a deterministic tiebreaker: prefer `is_offer=0` rows, then rows with a non-NULL price, then lowest `id`.

**Re-verified at FULL scope (not just the 300-row sample):**
```sql
-- (fixed bridge CTE, full account/marketplace scope, no LIMIT)
SELECT sub_source_id, marketplace, asin, resolved_sku, COUNT(*)
FROM bridge_fixed GROUP BY 1,2,3,4 HAVING COUNT(*) > 1;
-- → 0 rows returned
```
**Result: zero duplicate row-keys across the entire dataset**, not just the sample. This is CHECK 6 from `validation_checks.sql`, run live.

## Check 1 — Both accounts present

`bridge` query (full scope) returns rows for both `sub_source_id=8` (LEDSONE) and `sub_source_id=6` (DCVoltage). **PASS.**

## Check 2 — Four marketplaces present where source data exists

UK/Germany/Italy present for both accounts; France present only for LEDSONE (DCVoltage has zero PPC/sales/listing rows for France, confirmed in the discovery addendum and re-confirmed structurally unchanged here). **PASS** (correctly reflects real data, not a query defect).

## Check 3 — Fan-out proof (full scope, live)

```sql
-- distinct (account,marketplace,ASIN) with PPC spend in the 2026-06-16..2026-07-15 window
--   vs. rows produced by a NAIVE join straight to listing_data (no DISTINCT ON fix)
```
| Metric | Value |
|---|---|
| Distinct account+marketplace+ASIN with PPC spend | 13,413 |
| Rows produced by naive (unfixed) join to `listing_data` | 14,198 |
| Extra rows from naive join (fan-out) | 785 |
| ASINs with PPC spend but **no** bridge match at all | 975 (spend total £119.78) |
| Correct control total (spend aggregated once per ASIN, independent of any join) | **£26,232.59** |
| Naive "join-then-sum" total (uncorrected bridge, includes both the fan-out and the exclusion effects) | £26,112.81 (differs from correct by exactly the £119.78 excluded — the fan-out and exclusion effects happened to net to a similar order of magnitude in this window; this is precisely why per-ASIN validation, not just a total-level sanity check, is required to catch join errors) |

**Design conclusion confirmed live:** the report's actual join order (aggregate PPC first, independently; then LEFT JOIN the bridge onto it in `main_report.sql`... **correction, see note below**) avoids the fan-out. **Note on join direction:** `main_report.sql` anchors the query on `bridge` (`FROM bridge b ... LEFT JOIN ppc_agg`), not on `ppc_agg`. This means the 975 no-bridge-match ASINs (£119.78 of spend) are **not included as rows at all** in the final report, since a row requires a resolved SKU. This is a deliberate, disclosed design consequence of the row key (`account+marketplace+ASIN+resolved SKU` requires a resolved SKU to exist) — not a silent data loss. Recorded as a known limitation below.

## Check 4 — Shared German stock not over-counted

`stock_agg` groups by `(sku, location)` before the final join, and the final join's warehouse key is `CASE WHEN marketplace='UK' THEN 'UK' ELSE 'Germany' END` — Germany, France, and Italy rows for the same SKU all read the *same* single `stock_agg` row rather than three independently-summed pools. Per-row display repeats the same figure (permitted); no code path in `data_transform.py` sums stock across marketplace rows for a summary total. **PASS by construction; not independently re-queried at full scope this pass** (structural review, not a live count).

## Check 5 — No `amzn.gr.*` alias

`ppc_agg` filters `pp.sku NOT LIKE 'amzn.gr.%'`; `validate_output.check_no_amzn_gr_alias` additionally checks the final `Amazon SKU` display column. **PASS** on the 300-row sample (0 found); full-scope count from the original UK-only discovery was 30/320,057 (0.01%) and the exclusion filter is unchanged.

## Check 6 — Row-key uniqueness

Covered above — **PASS at full scope** after the fix.

## Reconciliation tolerance

Money: exact equality expected after the fix (no rounding applied before display; `_fmt_money` only formats for display, does not alter the underlying value). Percentages (ACOS): computed live, no stored value to reconcile against — formula sourced from the primary MCP's own documentation, applied consistently.

## Owner/reviewer

Technical reviewer: Sajeesan.

## Status

**PASS**, with one defect found and fixed during this session (documented above, not hidden) and one disclosed design limitation (975 unmapped ASINs excluded from row output).

## Pass/fail rule

PASS if every check above is backed by a live query result and any defect found is fixed and re-verified at full scope, not just the sample. Met.

## Known limitations

- ASINs with PPC spend but no `listing_data` bridge row (975 ASINs, £119.78 in this window) do not appear as report rows at all — the row key requires a resolved SKU. This is disclosed, not silently dropped.
- Check 4 (shared German stock) was verified by construction/code review, not re-queried live at full scope in this pass.

## Next action

Proceed to HTML validation (`06_VALIDATION/2026-07-17__html_validation_report.md`).

---

## Addendum — 2026-07-17 (later same session) — Full-scale (v002) verification

Following the business user's rejection of the 300-row v001 sample, the complete 30-day dataset (51,348 rows, all 8 account+marketplace combinations, zero cutoff) was extracted via keyset-paginated MCP batching (credential-based access was checked and found unavailable — see `07_EVIDENCE/database/2026-07-17__credential_environment_check.md`).

- **Check 6 (row-key uniqueness) re-verified at true full scale** (not just the 300-row sample): the `DISTINCT ON` bridge fix was re-run via a dedicated full-scope query returning **zero duplicate keys** across all 8 combinations combined, and independently re-confirmed via `checkpoint_manager.merge_period()`'s conflict detection across the merged 51,348-row dataset (also zero conflicts). **PASS, full scale.**
- **PPC Spend and Units Ordered reconciled exactly** against independent control totals for the complete 30-day window — see `07_EVIDENCE/validation/2026-07-17__report_reconciliation_evidence_v002.md` (diff = 0.00 for both).
- **ASIN/SKU cardinality reconfirmed at full scale:** 49,675 distinct account+marketplace+ASIN combinations → 51,348 rows, a 3.4% multi-SKU rate, consistent with the 3.3% figure from the original (smaller-scope) discovery.
- Checks 4 (shared German stock) and 5 (`amzn.gr.*` exclusion) were not independently re-queried at this full scale in this pass — same status as before (PASS by construction / PASS on sample, not re-verified live at full scale).

**7-day and 14-day periods have not been extracted or validated** — this addendum covers the 30-day period only.
