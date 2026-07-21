# v007 Product Title Alignment Evidence

**What this is:** Detailed evidence for the Product Title freeze, 3-line display, and row-alignment fix, plus the full v007-vs-v006 reconciliation.

---

## Sticky offset verification (live `getBoundingClientRect()`, real browser)

At a mid-scroll horizontal position (1366×768 viewport):

| Element | left | width |
|---|---|---|
| `th.col-asin` | 21 | 115 |
| `td.col-asin` | 21 | 115 |
| `th.col-sku` | 136 | 170 |
| `td.col-sku` | 136 | 170 |
| `th.col-title` | 306 | 360 |
| `td.col-title` | 306 | 360 |

Header and body positions are **identical** for all three frozen columns, at every tested scroll position (top, mid-scroll, combined horizontal+vertical). `136 = 21 + 115` (SKU starts where ASIN ends); `306` is offset by the 21px table-wrap border/padding from the CSS `--left-title: 285px` value, consistently applied to both header and body — no gap, no overlap. Re-confirmed at the 1920×1080 viewport with identical relative results.

## Row-height / line-count evidence

Sampled 30 rows on the default (30-day) view — all had 3-line-or-longer titles (naturally, this catalog's German/Italian product titles are typically verbose) and all measured **exactly 60px** div height / **75px** row height, matching the `min-height: 60px` CSS rule precisely.

**Short-title case, specifically located and measured:** product `HEAD-4363` (a 9-character title) — `divHeight: 60`, `rowHeight: 75`, `computedMinHeight: "60px"` — **identical** to the long-title rows. Screenshot inspection confirms the short title displays with generous whitespace below it inside the 60px box, not stretched or distorted, and every other cell in that row (ASIN, SKU, Days Since Last Sale, Units in Stock, etc.) is vertically centred and aligned with it — one logical row remains one visual row.

## Title text and accessibility

`title` attribute and `aria-label` on the inner `.title-text` div both carry the **full, untruncated** title (verified directly: for a 175-character title, both attributes returned the complete 175-character string, matching the visible/clamped text's source exactly). Confirmed not italic (`font-style: normal` in the applicable CSS rule, verified via computed style inspection).

## Sorting removed from identity columns (live interaction test)

- Clicked `th.col-asin`, `th.col-sku`, `th.col-title` in sequence (real mouse click events via CDP `Input.dispatchMouseEvent`, not simulated) — `sortColKey` was unchanged before and after all three clicks.
- Computed `cursor` style for all three identity headers: `"default"` (not `"pointer"`).
- Confirmed no `.sort-hint` span exists inside any of the three identity headers' DOM.
- Metric column sort (Sessions) was tested immediately after and **did** change the row order and set `sortColKey = 'sessions'` — confirming sortability was removed selectively, not globally broken.

## Full reconciliation (v007 vs v006)

| Period | Products | Fields compared | Mismatches |
|---|---|---|---|
| 7-day | 53,843 | 13 (incl. `title`) | 0 |
| 14-day | 53,843 | 13 | 0 |
| 30-day | 53,843 | 13 | 0 |

**Total: 2,100,477 comparisons, 0 mismatches.** The embedded B64 payload is byte-identical between v006 and v007 (`B64_PAYLOAD_IDENTICAL_TO_V006: true`), and `calcProduct()` is unchanged — this reconciliation confirms the layout-only changes did not alter any value, including the `title` field itself (relevant here since Product Title's rendering changed structurally).

## Status

**PASS.**
