# v004 Metric and Layout Fix Handover

**Date:** 2026-07-20 · **Developer:** Satheskanth · **Project code:** ANPIA · **Requirement:** REQ-01-D02

## What was built

v004 (`09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v004.html`, 139,416,832 bytes) — a corrected rebuild of v003 (preserved, unmodified) addressing all five reported defects, plus **two additional real defects found during this task's own verification work** (not reported by the user, but caught by rigorous root-cause investigation).

## Root causes found and fixed

1. **Traffic double-counting (root cause of "empty" Sessions/Page Views/Conversion Rate/Buy Box):** `amz_traffic_by_asin` stores one row per SKU variant of an ASIN, but Amazon repeats the identical ASIN-level session count on every variant row (confirmed: 1,183/1,191 duplicate groups, 99.3%, show identical values). The v003 SQL summed across these duplicates, multi-counting. **Fixed:** `MAX()` collapses same-day duplicates to the true value before any cross-day summation.
2. **LEDSONE UK traffic feed also stale — new finding.** Previously only DCVoltage was known to be stale (2026-04-22). This task found LEDSONE UK's feed stopped 2026-06-16 — also entirely outside the current 30-day reporting window (2026-06-20 to 2026-07-19). LEDSONE Italy (stopped 2026-06-22) has only a 3-day overlap with the 30-day window and zero overlap with 7/14-day.
3. **Generic N/A replaced with 4 precise classifications**, based on live-verified per-account/marketplace feed date coverage and a live-verified per-ASIN "ever tracked by the feed" set — not invented, not defaulted to zero.
4. **Category Avg Price contamination (root cause of implausible >£11,000 values):** confirmed via live investigation — not currency mixing, but malformed/outlier price values (one Germany/LIGHT_BULB listing at €649,555 against a plausible median in the tens of pounds). **Fixed:** exclude non-positive prices, apply a Tukey IQR outlier fence for categories with ≥5 listings. Result: Germany/LIGHT_BULB corrected from €13,272 (raw) to €12.62 (trimmed) — plausible. **Still AMBER** pending explicit business sign-off on the exact grouping/outlier policy.
5. **Sticky column layout rebuilt** with CSS custom properties (`--w-account`, `--left-marketplace`, etc.) whose cumulative-sum relationship is verified correct by construction, replacing v003's unenforced approximate JS offset array.
6. **Buy Box % scale bug — found during this task's own trace-evidence work, not user-reported.** `buyBoxPercentage` is stored on a 0–100 scale; the period-aggregation formula multiplied by 100 a second time, producing values up to 10000.0 for a true 100%. Fixed; re-verified 100% of numeric Buy Box values now fall within 0–100.
7. **Column reordering** into IDENTITY → INVENTORY/RECENCY → TRAFFIC → SALES → ADVERTISING → PRICE groups, with visual group separators, per the required layout.
8. **Formula and data-source notes section** added at the page end, documenting only the formulas actually implemented in code (verified against the real `derive_ratios`/`classify_traffic_value` logic, not written from memory).
9. **Data-quality panel** added above the table showing real REAL/TRUE_ZERO/OUTSIDE_COVERAGE/NO_MATCH counts per period, plus an explicit DCVoltage/LEDSONE-UK/LEDSONE-Italy freshness warning.

## Coverage reality (disclosed, not hidden)

Even after all fixes, only ~6.7% of 30-day rows have a confident numeric Sessions value (0.52% REAL + 6.21% TRUE_ZERO) — the rest is either genuinely outside the feed's date coverage (69.4%, DCVoltage + LEDSONE UK) or genuinely never tracked by Amazon's feed (23.9%, long-tail low-activity products). This low coverage is now **honestly measured and displayed**, not evidence of a remaining defect — it reflects real source-data sparsity for a "no-moving products" catalog.

## Validation status

**PASS** for everything verifiable via real code execution (Node.js/V8 parse, filter, sort, CSV, classification correctness — see the four validation/evidence files). **Real-browser visual rendering was not performed** — no browser automation tool is available in this environment; disclosed explicitly, not claimed as tested.

## Security status

Reference files unchanged throughout (checksums verified identical before/after). No database writes performed (read-only connection, read-only queries throughout). Credential scan clean — one 4-digit numeric false-positive match ("5435" inside an unrelated floating-point value) investigated and resolved.

## Remaining blockers

1. **Category Avg Price grouping/outlier policy** — statistically corrected and plausible, but not yet business-approved.
2. **LEDSONE UK and LEDSONE Italy traffic-feed staleness** — new findings this task, real external upstream gaps, need escalation alongside the existing DCVoltage escalation.
3. **v004 file size (139.4MB)**, larger than v003's 126.9MB — same disclosed, unresolved delivery question, now slightly larger due to added classification/data-quality metadata.
4. **No real-browser visual confirmation** — recommend performing this before final user sign-off, in an environment with browser access.
5. `tech_team_outputs` excess-privilege scope — unchanged, still pending Sajeesan's review.

## Publication status

**DEFERRED — USER REVIEW REQUIRED.** No write to `tech_team_outputs.ph_task` occurred or was attempted. `daily_task` was not modified.

## Database writes

**NONE.**

## One next step

Present v004 to Nivarnan for business review (traffic coverage reality, Category Avg Price policy, file-size tolerance) and route the LEDSONE UK/Italy traffic-feed gap to whoever manages LEDSONE's Amazon Business Report ingestion.
