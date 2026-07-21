# v006 User-Experience Validation

**What this is:** Validation of the v006 user-experience correction against v005's reported visual defect (long N/A explanations overflowing into adjacent columns, merged-looking metric columns).

---

## Root cause of the v005 defect

`td { white-space: nowrap; }` applied globally with no `overflow`/`text-overflow` control, and `.na` only set color/italic/background — no width containment. Long strings like `N/A — source outside reporting date coverage` (46 characters) rendered at full width inside fixed ~110–140px cells with nowrap, visually spilling into neighboring cells.

## Fix applied

Every `td` now has `overflow: hidden; text-overflow: ellipsis;` by default; `td.metric-cell`/`td.na-cell` additionally force `white-space: nowrap`. Critically, the **cell text itself was shortened to the literal string `N/A`** (3 characters) for every unavailable value — confirmed via direct extraction and execution of the real `fmt()` function from the generated file (not a reimplementation): every tested N/A input (`'N/A — source outside reporting date coverage'`, `'N/A — no matching traffic source row'`, `null`) returns `{ text: 'N/A', ... }`. A 3-character string cannot overflow a 100px+ cell under any font size used in this report — the defect is structurally impossible now, not just visually improved.

## Two real defects found and fixed during this task's own verification (not user-reported, found via testing)

1. **ASIN/SKU columns destroyed by the N/A-formatting logic.** The original `render()` implementation routed every non-title column through `fmt()`, which treats *any* string value as an N/A reason code. Since `asin`/`sku` are also plain strings, real product identifiers were being replaced with "N/A" in the visible table and in the accessible `aria-label` (found via the real-browser screenshot capture: an N/A cell's `aria-label` read `"Unavailable: B07C7G69F8"` — an ASIN, not a reason). Fixed by excluding `asin`/`sku` from the `fmt()` path entirely, rendering them as plain identity text.
2. **Frozen header cells not actually frozen.** `renderHeader()` applied only the alignment class to each `<th>`, omitting the structural class (`col-asin`/`col-sku`) that the sticky-column CSS rules depend on. Result: `document.querySelector('th.col-asin')` returned `null` — the header cells for ASIN/SKU scrolled away horizontally during scroll while the body cells beneath them (which had the class) correctly stayed pinned, producing severe header/data misalignment (confirmed visually in a real-browser screenshot before the fix, and confirmed resolved via `getBoundingClientRect()` comparison after — header and body cells now report identical `left` positions at every scroll offset).

Both defects were caught by combining real Node.js execution of the extracted functions with real headless-Chrome screenshot review — neither would have been caught by data reconciliation alone, since neither affected calculated values.

## Compact N/A display

Confirmed: cell text is always exactly `N/A`; the full reason is carried in the `title` attribute (native tooltip) and a matching `aria-label` (`"Unavailable: <reason>"`) — never deleted, only moved out of the compact cell text, satisfying the required accessible markup pattern.

## Visual confirmation (real browser)

See `07_EVIDENCE/validation/2026-07-20__v006_browser_visual_evidence.md` for the full screenshot-by-screenshot review. Summary: no text crosses a cell boundary at any tested scroll position or viewport size; ASIN/SKU remain frozen and aligned with their headers throughout horizontal scroll; Product Title wraps to two lines without distorting row height; numeric columns are right-aligned with consistent decimal formatting; zero (`0`/`0.00%`/`£0.00`) is visually distinct from N/A (amber background) at a glance.

## Status

**PASS**, with two real defects found and fixed during this task's own testing (documented above, not hidden) in addition to the reported v005 defect.
