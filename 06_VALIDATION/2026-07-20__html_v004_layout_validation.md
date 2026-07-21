# HTML v004 Layout Validation

**What this is:** Validation of v004's redesigned table layout (frozen columns, column grouping, Product Title readability, numeric alignment).

**Method disclosed honestly:** no real browser automation tool (Playwright/Puppeteer/similar) is available in this environment — checked via `ToolSearch`, none found. Layout correctness is verified two ways: (1) **CSS arithmetic consistency** — the sticky-offset custom properties are checked for correct cumulative-sum relationships, which is what actually prevents overlap in any standards-compliant browser; (2) **real Node.js/V8 execution** of the actual embedded data/logic (parse, render-equivalent formatting, sort). **Visual rendering / screenshots were not captured** — disclosed as a gap, not hidden, consistent with this project's established practice of not claiming untested outcomes.

---

## Frozen-column offset arithmetic (replaces v003's approximate JS array)

| Variable | Value | Should equal | Check |
|---|---|---|---|
| `--w-account` | 110px | (defined) | — |
| `--w-marketplace` | 115px | (defined) | — |
| `--w-asin` | 115px | (defined) | — |
| `--w-sku` | 170px | (defined) | — |
| `--left-account` | 0px | 0 | PASS |
| `--left-marketplace` | 110px | `--w-account` = 110 | PASS |
| `--left-asin` | 225px | `--w-account + --w-marketplace` = 110+115=225 | PASS |
| `--left-sku` | 340px | `--w-account + --w-marketplace + --w-asin` = 110+115+115=340 | PASS |
| `--frozen-end` | 510px | sum of all four = 110+115+115+170=510 | PASS |

Each frozen `th`/`td` pair shares identical `width`, `min-width`, `max-width`, and `left` (same CSS class, same variables) — a standards-compliant browser cannot render an overlap when offsets are exact cumulative sums and widths are fixed (`box-sizing: border-box` set globally). This is the structural guarantee that replaces v003's approximate `[90,100,110,140]` JS array, which had no such enforced relationship to actual column widths.

## Visible separator after the last frozen column

`td.col-sku` and `th.col-sku` carry `border-right: 3px solid var(--accent-light)` — confirmed present in the generated HTML (`CSS_HAS_SEPARATOR: true`, Node.js string check).

## Z-index layering

Frozen `td`s: `z-index: 3`. Frozen `th`s: `z-index: 6` (header row itself already `z-index: 5`, frozen header cells raised above it to stay visible over both scrolling body cells and the plain sticky header). Non-frozen header cells: `z-index: 5`. This ordering prevents a frozen header cell from being drawn under a scrolling body cell.

## Column order (Product Title placement)

Confirmed via Node.js inspection of `COLUMN_DEFS` in the generated file: Account → Marketplace → Amazon ASIN → Amazon SKU (all frozen) → Product Title (not frozen, immediately after) → Days Since Last Sale → Units in Stock → Sessions → Page Views → Buy Box % → Units Ordered → Conversion Rate → PPC Spend → CTR → ACOS → Price → Category Avg Price. **Matches the required IDENTITY / RECENCY / TRAFFIC / SALES / ADVERTISING / PRICE grouping exactly** (`COLUMN_ORDER_TRAFFIC_BEFORE_SALES: true`, `COLUMN_ORDER_SALES_BEFORE_ADS: true`).

Visual group separators: a `col-group-sep` CSS class (2px left border) is applied to the first column of each new group (Days Since Last Sale, Sessions, Units Ordered, PPC Spend, Price) — verified present in `COLUMN_DEFS`.

## Product Title readability

`title-cell` CSS: `max-width: 380px`, `-webkit-line-clamp: 2` (two-line wrap with ellipsis overflow), `white-space: normal` (was `nowrap` in v003, forcing single-line truncation only) — allows genuine two-line wrapping as required, full text available via the `title` HTML attribute (tooltip) on the cell, unchanged mechanism from v003 but now paired with actual wrapping instead of forced single-line overflow.

## Numeric column alignment

All metric columns (`num` class): `text-align: right`, `font-variant-numeric: tabular-nums` (consistent digit width for clean vertical alignment of numbers). Zero-vs-N/A distinguished via CSS class: real/confirmed-zero values render in normal text color; N/A values render in a distinct amber/italic style (`.na` class, `color:#9a6b00`, `background:#fff9ec`) — a genuine zero is never visually indistinguishable from an unavailable value.

## Status

**PASS** for all layout properties checkable via CSS-arithmetic and DOM-structure inspection. **Real-browser visual confirmation (viewport testing, screenshots, actual overlap-free rendering as seen by a human) was not performed** — disclosed explicitly as an AMBER-adjacent gap in the accompanying evidence file, not claimed as done.

## One next step

If real-browser visual confirmation is required before user acceptance, it should be performed on a machine with a browser-automation tool available (Playwright/Puppeteer) or manually by opening the file — this environment could not perform it.
