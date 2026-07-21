# v006 Browser Visual Evidence

**What this is:** Real headless-Chrome screenshot evidence for v006, driven via the Chrome DevTools Protocol (Chrome 150.0.7871.125, already installed on this machine — not downloaded or installed for this task). Screenshots stored at `07_EVIDENCE/screenshots/v006/`.

---

## Method

Chrome was launched with `--headless=new --remote-debugging-port=9222`, driven via a Node.js script using Node's native `WebSocket` client (no new packages installed) to issue Chrome DevTools Protocol commands: navigate to the local `v006.html` file (`file://` URL, confirming no network dependency), wait for the app to signal ready, evaluate JavaScript to set scroll position / expand the formula section / move the mouse, and capture PNG screenshots via `Page.captureScreenshot`.

## Two real defects found via this exact process (not caught by data reconciliation)

1. **ASIN/SKU columns showing "N/A" instead of real values** — caught because the first screenshot's captured `aria-label` read `"Unavailable: B07C7G69F8"` (an ASIN) instead of a reason. Fixed (see `06_VALIDATION/2026-07-20__v006_user_experience_validation.md`), re-screenshotted, confirmed resolved.
2. **Frozen header cells scrolling away from their frozen body cells** — caught because `1366_768_4_frozen_scroll.png` visually showed "Amazon ASIN"/"Amazon SKU" headers missing and metric headers shifted two positions left of their data. Fixed, re-screenshotted, confirmed resolved (`th.col-asin`/`td.col-asin` `getBoundingClientRect().left` now identical at every scroll position).

All screenshots referenced below are from the **final, fixed** version.

## Screenshot inventory (both required viewports)

| # | File | Confirms |
|---|---|---|
| 1 | `{1366_768,1920_1080}_1_left_side.png` | Header, summary cards, toolbar, and left portion of the table (ASIN/SKU/Title/first metrics) render cleanly; no overlap |
| 2 | `{...}_2_middle_metrics.png` | Mid-scroll view — Sessions through PPC Spend readable, no merged columns |
| 3 | `{...}_3_rightmost.png` | CTR/ACOS/Price/Category Avg Price fully readable at the right edge; ASIN/SKU remain frozen and correctly aligned with their own header |
| 4 | `{...}_4_frozen_scroll.png` | Mid-scroll (35% of scroll width) — confirms the header/body alignment fix; ASIN/SKU headers and values both correctly pinned and aligned |
| 5 | `{...}_5_na_hover_attempt.png` | Mouse positioned over a real N/A cell; DOM attributes captured directly (see below) — native OS tooltip popup itself is not reliably captured by headless screenshot (a known headless-browser limitation, disclosed not hidden) |
| 6 | `{...}_6_formula_collapsed.png` | Formula section shows only the "Calculation Formulas" heading by default |
| 7 | `{...}_7_formula_expanded.png` | Formula section expanded, showing all six required formulas in plain language, no database/technical terms |

## Direct visual confirmations (from viewing the actual PNG files)

- **No text crosses a cell boundary** at any captured scroll position, either viewport.
- **No merged-looking columns** — every metric has its own clearly bordered cell with visible group separators (thicker line after SKU, Days Since Last Sale, Sessions, Units Ordered, PPC Spend, Price).
- **N/A cells** show the compact amber-highlighted `N/A` text, visually distinct from real `0`/`£0.00`/`0.00%` values (plain text, no highlight).
- **Product Title** wraps to two lines, normal (non-italic) weight, consistent row height across rows with short and long titles (German/French text confirmed wrapping correctly, e.g. "12 V POWERSUPPLY 300 W 25 A Transformator für LED Strip Modul Treiber Beleuchtung Outdoor Wasserdicht IP67 AC 110–…").
- **Frozen ASIN/SKU columns** stay visible and correctly aligned with their headers through the full scroll range (left / 35% / 100%).
- **Formula section** collapses/expands correctly via the native `<details>` element; expanded content is short, plain-language, and contains no PostgreSQL/schema/table/SQL/database references (confirmed both visually and via text-scan in the UI validation evidence).
- **Pagination** ("Page 1 of 1,077 (53,843 filtered rows)") is visible and correctly reflects the full dataset, confirming only the current page is rendered while the full row count is tracked.

## Accessible reason text (direct DOM inspection, real browser)

Live-queried a real N/A cell's attributes in the running page:

```
title: "Source outside reporting date coverage"
aria-label: "Unavailable: Source outside reporting date coverage"
text content: "N/A"
```

This confirms the full missing-data reason is genuinely present and accessible, not deleted, even though the compact visible text is `N/A`.

## Console errors

**Zero** JavaScript console errors captured at either viewport size (`window.addEventListener('error', ...)` installed before navigation, checked after app-ready).

## Limitation disclosed

The native OS-rendered tooltip popup itself (the small yellow box that appears on hover in a real desktop browser) was not visible in the `_5_na_hover_attempt.png` screenshots — this is a known limitation of headless Chrome's screenshot capture (native title-attribute tooltips are rendered by the OS/browser chrome, outside the page's paint surface that `Page.captureScreenshot` captures). The underlying `title`/`aria-label` attributes were confirmed correct via direct DOM inspection instead, which is a stronger, more precise form of evidence for correctness (screen readers and assistive technology read the DOM attribute directly, not a rendered tooltip bitmap).

## Status

**PASS** for both required viewports (1366×768, 1920×1080), with real screenshots as evidence, not a claimed-but-untested result.
