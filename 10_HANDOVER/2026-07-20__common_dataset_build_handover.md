# Common Dataset Build Handover — ANPIA Rebuild (REQ-01-D02)

**Date:** 2026-07-20 · **Developer:** Satheskanth · **Project code:** ANPIA · **Requirement:** REQ-01-D02

**This document supersedes the earlier same-day version**, which recorded the build as blocked (no direct-credential source available). The user subsequently authorized reading the real connection values from the approved reference files and transferring them into a protected local `.env`; this handover reflects the real, completed build that followed.

## What was built

1. **Secure credential pipeline:** real values extracted from `temp_user.py` via a static AST parse (never import/exec), written only to a git-ignored `.env`, never printed/logged. `05_IMPLEMENTATION/src/anpia_config.py` + `anpia_db_connection.py` load credentials exclusively from `.env`/environment, no hardcoded fallback, redacted error text, read-only session.
2. **Live direct PostgreSQL connection** — confirmed working (database/role matched expected, PostgreSQL 18; SSL not active despite `sslmode=prefer`, disclosed honestly).
3. **Live privilege verification** — source tables SELECT-only (confirmed for all 7 candidate tables), `ph_task` full CRUD + schema CREATE (confirmed excessive relative to strict least privilege, matching the earlier PDF-based finding, now independently reproduced live).
4. **Real 30-day common daily dataset** — 268,404 rows, direct PostgreSQL extraction via server-side cursor + `fetchmany` batching, 0 duplicate keys, 0 null keys, 37.5 seconds. Path: `09_OUTPUTS/data/2026-07-20__anpia_common_daily_facts.jsonl`.
5. **A real defect found and fixed mid-build:** the first period-report version silently excluded zero-activity ASIN/SKUs, violating the "no cutoff" rule — critical given this report's purpose is surfacing *no-moving* products. Fixed by enumerating the full 53,843-row bridge dimension for every period.
6. **Three derived report views** (7/14/30-day), each 53,843 rows, all derived from the one common dataset — `09_OUTPUTS/data/2026-07-20__anpia_{7d,14d,30d}_report.jsonl`.
7. **Full reconciliation** — an initial raw-sum discrepancy was investigated (not accepted at face value) and closed to an exact match, traced precisely to the known multi-SKU-repeat and unmapped-ASIN effects (£104.43 / 58 units on the 30-day period, matching the independently-measured unmapped-ASIN total exactly).
8. **v003 HTML** — `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html`, 126,852,855 bytes, built from the real common dataset, validated via real Node.js/V8 execution (not simulated).
9. **Live re-validation of field sources** — resolved the DCVoltage `amz_traffic_by_asin` freshness question (genuine upstream feed stop on 2026-04-22, confirmed not a mapping error) and the Category Avg Price source gap (now confirmed available via `listing_data.product_type`, 100% populated).

## Source tables (confirmed live)

`public.ppc` + `public.ppc_performance` (PPC, SB-excluded), `public.order_transaction` (primary sales, `order_status='Completed'`), `public.listing_data` (ASIN↔SKU bridge, `DISTINCT ON` dedup), `public.location_wise_inv_stock` (stock, clean `UK`/`Germany` location values), `public.amz_traffic_by_asin` (Sessions/Page Views/Buy Box — newly resolved source, account-dependent freshness).

## Common daily grain

`report_date + account + marketplace + amazon_asin + resolved_amazon_sku`.

## Date window

Latest complete date: **2026-07-19** (yesterday relative to the source's own `CURRENT_DATE`, excluding the still-accruing current day). 7-day: 2026-07-13→2026-07-19. 14-day: 2026-07-06→2026-07-19. 30-day: 2026-06-20→2026-07-19.

## Formulas

Conversion Rate = `SUM(units_ordered)/SUM(sessions)×100`; CTR = `SUM(clicks)/SUM(impressions)×100`; ACOS = `SUM(spend)/SUM(attributed_sales)×100`; Buy Box % = sessions-weighted average of Amazon's own daily percentage (disclosed compromise — no raw won/eligible counts exposed). All recalculated from period-summed totals, safe zero-denominator handling.

## Snapshot handling

Stock/price/title/category-avg-price joined once, post-aggregation. Warehouse mapping confirmed against real, clean location values: UK→`UK`, Germany/France/Italy→`Germany` (shared, never triple-counted).

## Historical last-sale handling

`report_end_date − MAX(order_date::date)` from `order_transaction` (`Completed` only), searched with no lower time bound, `No sale on record` when none exists — 20,985 identities resolved live.

## Output paths

- Common dataset: `09_OUTPUTS/data/2026-07-20__anpia_common_daily_facts.jsonl`
- Period views: `09_OUTPUTS/data/2026-07-20__anpia_7d_report.jsonl`, `_14d_report.jsonl`, `_30d_report.jsonl`
- Checkpoints: `09_OUTPUTS/logs/direct_db_checkpoints/2026-07-20__anpia_checkpoint.json`, `2026-07-20__period_summary.json`
- HTML: `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html`

## Validation status

**PASS**, with one real defect found and fixed (completeness/no-cutoff violation) and one initial reconciliation discrepancy investigated and fully explained (not swept under the rug). Full detail: `06_VALIDATION/2026-07-20__common_dataset_validation_report.md`, `06_VALIDATION/2026-07-20__html_validation_report.md`, and the four `07_EVIDENCE/` files (credential access, extraction, reconciliation, UI/CSV).

## Security status

Reference files (`temp_user.py`, `update_table.py`, the PDF) unchanged throughout — checksums verified identical before and after. Credentials never printed/logged; transferred via static AST parse only. `.env` git-ignored, not placed under any shared/evidence folder. Repository-wide credential scan clean (zero matches outside `.env` and the three known reference files). No database writes performed at any point.

## Remaining blockers

1. **Excess `tech_team_outputs` privilege scope** (schema-wide CRUD+CREATE, not scoped to `ph_task` alone) — unchanged, flagged to Sajeesan, not remediated by this task (out of scope — grant changes were not authorized).
2. **v003 file size (126.9MB)** — larger than v002's already-flagged 41.7MB, because v003 correctly includes the full zero-activity-inclusive population for all three periods (a correctness improvement, not a regression) — network delivery time unmeasured, unresolved production question for the coordinator.
3. **Category Avg Price averaging population** — defaulted to `(marketplace, product_type)`, disclosed, pending explicit business sign-off from Nivarnan.
4. **DCVoltage traffic-data gap** — Sessions/Page Views/Buy Box will show `N/A` for DCVoltage from 2026-04-23 onward in any report window; this is a real, external upstream data gap (not something this codebase can fix) — worth escalating to whoever manages DCVoltage's Amazon Seller Central / Business Reports connection.
5. **SSL not active** on the direct connection despite `sslmode=prefer` — disclosed, not investigated further in this task (server-side TLS configuration is outside this task's scope).

## Publication status

**DEFERRED — VALIDATION AND USER ACCEPTANCE REQUIRED.** No ph_task pre-publication check was created; no write to `tech_team_outputs.ph_task` occurred or was attempted, per instruction.

## One next step

Present v003 to Nivarnan for business review (accuracy, Category Avg Price population choice, file-size/delivery tolerance) before any ph_task publication is considered; in parallel, route the excess-privilege finding to Sajeesan.
