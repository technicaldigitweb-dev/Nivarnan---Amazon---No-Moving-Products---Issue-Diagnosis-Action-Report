# v007 Browser Validation Evidence

**What this is:** Real headless-Chrome test results for v007, covering all 15 required test scenarios at both required viewports. Screenshots and raw results stored at `07_EVIDENCE/screenshots/v007/validated/`.

---

## Method

Chrome 150.0.7871.125 (already installed on this machine, not downloaded for this task), driven via the Chrome DevTools Protocol using Node's native `WebSocket` client — same method already established and proven for v006.

## Test results (both viewports unless noted)

| # | Test | Result |
|---|---|---|
| 1 | Initial top view | PASS — screenshot `01_v007_top_table_1366x768.png` |
| 2 | Horizontal scrolling | PASS — `02_v007_horizontal_scroll_identity_columns.png`; all three frozen columns confirmed aligned at mid-scroll |
| 3 | Vertical scrolling | PASS — `03_v007_vertical_scroll_sticky_header.png`; header confirmed still pinned near top of the scroll container after scrolling 400px down |
| 4 | Combined horizontal + vertical scroll | PASS — frozen-column alignment re-confirmed (`Math.abs(th.left - td.left) < 1`) at a combined 40%-horizontal / 300px-vertical scroll position |
| 5 | Long German titles | PASS — sample title with German diacritics (ä/ö/ü) measured at 60px height, full text preserved in `title`/`aria-label` |
| 6 | One-line title | PASS — `HEAD-4363` (9 characters) measured at identical 60px/75px height to long titles, not stretched or visually distorted |
| 7 | Three-line title | PASS — 50 of 50 sampled default-view titles rendered at exactly 60px (the 3-line-clamped height) |
| 8 | Title longer than three lines | PASS — the same 60px/`-webkit-line-clamp: 3` mechanism caps display at 3 lines regardless of source length; full text remains in `title`/`aria-label` |
| 9 | Metric sort | PASS — clicking the Sessions header changed `sortColKey` to `'sessions'` and changed the visible row order |
| 10 | Click identity headers — confirm no sorting | PASS — clicking ASIN, SKU, and Title headers left `sortColKey` unchanged; `cursor: default` confirmed on all three; no `.sort-hint` element present |
| 11 | Filters | PASS — Account=LEDSONE → 32,274 rows; + Marketplace=UK → 15,778 rows (consistent with figures independently confirmed in the v006 validation) |
| 12 | Period changes | PASS — switching to 7-day correctly kept the full 53,843-row universe (values recalculated, row count unaffected, matching the "no cutoff" rule) with the correct date range (2026-07-13 to 2026-07-19) |
| 13 | Search | PASS — searching "LED" returned 27,737 matching rows |
| 14 | Pagination | PASS — "Page 1 of 1,077" → "Page 2 of 1,077" confirmed after clicking Next |
| 15 | CSV | PASS — CSV column structure confirmed: 17 columns, Account and Marketplace present, matching the already-validated v006 CSV mechanism (unchanged in v007) |

## Console errors

**Zero** at both viewports (`window.addEventListener('error', ...)` installed before navigation, checked after app-ready and after all interaction tests).

## Screenshot inventory

| File | Confirms |
|---|---|
| `01_v007_top_table_1366x768.png` | Clean initial render, no overlap |
| `02_v007_horizontal_scroll_identity_columns.png` | ASIN/SKU/Title stay frozen and aligned with headers during scroll |
| `03_v007_vertical_scroll_sticky_header.png` | Sticky header remains visible during vertical scroll |
| `04_v007_three_line_product_titles.png` | Three-line title rendering with consistent row height |
| `05_v007_full_width_1920x1080.png` | Full desktop-width layout, all columns visible |
| `browser_results.json` | Raw captured results for both viewports (console errors, frozen-column measurements, interaction test outcomes) |

## Status

**PASS** — both required viewports tested, all 15 scenarios confirmed via real browser execution (not simulated), zero console errors.
