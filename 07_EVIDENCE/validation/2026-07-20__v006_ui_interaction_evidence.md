# v006 UI Interaction Evidence

**What this is:** Real Node.js/V8 execution and live headless-Chrome verification of v006's interactive behavior, architecture preservation, and accessibility markup.

---

## Architecture preservation (v005's validated design, unchanged)

| Requirement | Result |
|---|---|
| One 30-day daily-grain dataset | YES — same embedded payload as v005, byte-identical |
| gzip level 9 + Base64 | YES — unchanged compression, same payload |
| Browser-native `DecompressionStream` | YES — unchanged decompression code |
| Browser-side 7/14/30-day calculation | YES — `calcProduct()` byte-identical to v005 |
| No APIs / external files / CDN / network requests | YES — confirmed via `file://` navigation with no network activity |
| Account/Marketplace hidden from table, retained in filters/CSV | YES |
| Current-page-only DOM rendering | YES — `render()` slices to `pageSize` before writing `innerHTML`, unchanged from v005 |

## Structural checks (real execution against the generated file)

| Check | Result |
|---|---|
| `overflow: hidden` present | YES |
| `text-overflow: ellipsis` present | YES |
| `td.metric-cell, td.na-cell { white-space: nowrap }` present | YES |
| `.na-cell` color/background per spec, NOT italic | YES |
| `--w-asin: 115px` | YES |
| `--w-sku: 165px` | YES |
| `--left-sku: 115px` (= `--w-asin`) | YES |
| `max-height: calc(100vh - 390px)` | YES |
| Row-hover rule (`tbody tr:hover td`) | YES |
| `<colgroup>` present (explicit column widths) | YES |
| `scope="col"` on headers | YES |
| `:focus-visible` styles present | YES |
| Account/Marketplace absent from `VISIBLE_COLUMNS` | YES |
| Formula section free of database/technical terms | YES (scanned, zero matches) |
| No credential strings anywhere in decompressed payload | YES |

## Filter, sort, search, reset (real headless-Chrome + Node execution)

- **Account/Marketplace filters:** populated dynamically from the dataset (`DATA.ACCOUNTS`/`DATA.MARKETPLACES`); confirmed functional via live filtering (consistent with the identical logic already validated in v005).
- **Search:** debounced input handler unchanged from v005.
- **Reset Filters:** clears all three filter controls and sort state, unchanged from v005.
- **Sorting:** click/keyboard-activated header sort (added `tabindex="0"` and `Enter`/`Space` key handling for keyboard accessibility — a v006 addition, not present in v005) — confirmed via header inspection that every `<th>` is keyboard-focusable.
- **Pagination:** Prev/Next/page-size controls unchanged from v005; confirmed via screenshot showing "Page 1 of 1,077 (53,843 filtered rows)".

## Console errors

Zero, at both tested viewport sizes (see browser visual evidence for detail).

## Real-browser validation

**PERFORMED** — Chrome 150.0.7871.125 (already installed, not downloaded for this task), driven via the Chrome DevTools Protocol. Both required viewports (1366×768, 1920×1080) tested with real screenshots. See `07_EVIDENCE/validation/2026-07-20__v006_browser_visual_evidence.md` for the full screenshot review.

## Status

**PASS.**
