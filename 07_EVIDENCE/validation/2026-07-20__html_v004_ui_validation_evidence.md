# HTML v004 UI Validation Evidence

**What this is:** Real Node.js/V8 execution results for v004 (139,416,832 bytes), honestly scoped to what this environment can actually verify.

---

## What was tested (real execution, not simulated)

| Check | Result |
|---|---|
| File parses without error | YES — 1.59s at 139.4MB |
| Row counts (7/14/30-day) | 53,843 / 53,843 / 53,843 — correct, matches the Python-side build exactly |
| Yellow fields in row data | NONE (clean) |
| N/A classification correctness | 2 precise reasons only (`source outside reporting date coverage`, `no matching traffic source row`) — the old generic `N/A - source not available` string confirmed **absent** from Sessions/Page Views/Buy Box data |
| DCVoltage rows all classified OUTSIDE_COVERAGE | YES — all 21,569 rows |
| LEDSONE UK rows all classified OUTSIDE_COVERAGE | YES — all 15,778 rows (new finding this task) |
| LEDSONE Germany rows with real numeric Sessions | 1,569 of 6,786 |
| Multi-SKU double-count check | Example ASIN `B097DWPVNN` (LEDSONE/France, 2 SKU rows): both show Sessions=1 (identical, not summed to 2) |
| Category Avg Price maximum (30d) | £609.06 (plausible; down from v003's implausible >£11,000+ range) |
| Buy Box % range | 0–100, 100% of 3,625 numeric values within valid range (post-fix; was up to 10000.0 pre-fix) |
| Formula notes section present | YES |
| Formula notes mention DCVoltage limitation | YES |
| CSS frozen-column left-offset variables present | YES |
| CSS visible separator after last frozen column | YES |
| Column order: Traffic before Sales before Advertising | YES (matches required IDENTITY→RECENCY→TRAFFIC→SALES→ADS→PRICE grouping) |
| Sort performance (30-day array, full sort) | 17ms |
| CSV generation performance (30-day array, all columns) | 231ms, 24,763,735 characters |
| Credential strings in dataset/CSV | Investigated one flagged 4-digit numeric substring match ("5435") — confirmed a false positive (coincidental digits inside a floating-point percentage value, e.g. `0.5712245626561943`), not the real port number in context. No match for the real host, password, or `ANPIA_DB_*` variable names anywhere. |

## What was NOT tested (disclosed honestly, not hidden)

- **No real browser rendering.** No Playwright/Puppeteer/similar tool is available in this environment (checked via `ToolSearch`, none found). Desktop/laptop/narrow viewport rendering, actual pixel-level overlap-freedom, horizontal/vertical scroll behavior, and visible sticky-header behavior were **not visually confirmed**.
- **No screenshots** were captured, for the same reason.
- Frozen-column non-overlap is instead verified via **CSS arithmetic consistency** (see `06_VALIDATION/2026-07-20__html_v004_layout_validation.md`) — a standards-compliant browser cannot overlap columns whose offsets are exact cumulative sums of fixed widths, but this is a structural argument, not a rendered observation.

## Filter/sort/period/account/marketplace logic

Re-executed the same real filter/sort functions from the template (unchanged from v003's already-validated implementation, only the column set and N/A values changed) against the actual v004 data — account and marketplace filters, search, and period switching all produced correct, independently-checkable row counts (see the coverage evidence file for exact DCVoltage/LEDSONE-UK/LEDSONE-Germany breakdowns, all matching the Python-side build).

## Status

**PASS** for everything testable via real code execution in this environment. **Real-browser visual confirmation is an explicit, disclosed gap**, not claimed as passed.

## One next step

If visual/screenshot confirmation is required before user sign-off, it needs to be performed in an environment with real browser access.
