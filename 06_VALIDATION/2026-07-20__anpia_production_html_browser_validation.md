# Validation: Production ANPIA v001 -- Real Browser Testing

**Report:** `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html`
**Method:** Real local Chrome (`Chrome/150.0.7871.125`), headless, driven via Chrome DevTools
Protocol over Node's native `WebSocket` client (no npm install, no headless-browser library).
**Screenshots:** `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v001/`
**Raw results:** `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v001/browser_results.json`

## 1. Viewports tested

Both required viewports, per instruction:

| Viewport | Console errors | Screenshot(s) |
|---|---|---|
| 1366x768 | **0** | 01, 02, 03, 04 |
| 1920x1080 | **0** | 05 |

## 2. Checks performed and results

| Check | Result |
|---|---|
| App becomes ready (data decoded/rendered) | PASS |
| Console errors at either viewport | **0** (PASS) |
| Network requests during operation | Not applicable -- file loaded via `file://`, no fetch/XHR in the app; self-contained confirmed structurally in the calculation-reconciliation evidence doc |
| Frozen identity columns (ASIN/SKU/Title) stay pixel-aligned with header during horizontal scroll | PASS -- `th`/`td` `left` values identical for all three columns at both viewports (see screenshot 02 and `frozenAlignment` in `browser_results.json`) |
| Sticky header remains visible during vertical scroll | PASS (screenshot 03) |
| Product Title renders as 3-line clamped text via `.title-text` div | PASS -- all 50 sampled title cells on the initial page measured at the 3-line-or-clamped height bucket; 0 in the 1-line or 2-line buckets (screenshot 04) |
| Metric column sort (Sessions) changes row order and updates `sortColKey` | PASS |
| Identity column header click (ASIN) does NOT trigger sort | PASS -- `sortColKey` unchanged before/after click |
| Account filter (LEDSONE) narrows visible rows | PASS -- 32,274 of 53,843 rows |
| Period switch (30-day -> 7-day) recalculates without changing total row count | PASS -- 53,843 rows in both cases (period changes values, not row membership, by design -- true zero/N/A rows are never dropped) |
| CSV column structure includes Account and Marketplace (hidden from the visible table, present in export) | PASS -- `hasAccount: true`, `hasMarketplace: true`, 17 total columns |
| No database/schema/table names visible in rendered UI | PASS -- visual review of screenshots 01/02/05 confirms only business-facing labels (Amazon ASIN, Amazon SKU, Product Title, metric names) |

## 3. Visual confirmation

Screenshot 01 (1366x768, top of table) shows the report rendering with real production data: 53,843
visible rows, 30,751 unique ASINs, 22,137 unique SKUs, £19,985.29 total PPC spend, 9,003 total units
ordered over the 30-day period, and the traffic data-quality banner (243 real / 3,382 confirmed-zero /
37,347 outside-coverage / 12,871 never-tracked) -- all computed from the fresh live extraction, not
copied from any prior version.

## 4. Conclusion

Browser validation passes at both required viewports with zero console errors. The approved UX
(frozen identity columns, 3-line titles, metric-only sorting, hidden-but-exportable Account/
Marketplace columns) carried over correctly from the v007 template into the production build.
