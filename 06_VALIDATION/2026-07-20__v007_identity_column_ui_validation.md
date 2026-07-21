# v007 Identity Column UI Validation

**What this is:** Validation of v007's correction to v006's identity-column layout (Product Title alignment/clipping, freezing all three identity columns, removing sorting from identity headers).

**Note on supplied screenshots:** the task requested saving three user-supplied defect screenshots into `07_EVIDENCE/screenshots/v007/user-reported-ui-defect/` (`01_v006_product_title_alignment_issue.png`, `02_v006_product_title_scroll_alignment_issue.png`, `03_v006_product_title_hidden_issue.png`). **No image attachments were included in the message that requested this task** — the folder was created as instructed, but it is empty, since there was nothing to save. This is disclosed here rather than fabricated. The defects were instead addressed from the detailed textual description in the task instructions (points 1–7), which was sufficient to identify and fix the underlying issues.

---

## Root cause of the reported defects

v006 froze only ASIN and SKU; Product Title scrolled with the metric columns, used a 2-line clamp applied directly to the `<td>` (`display: -webkit-box` on the table cell itself), and retained a click-to-sort handler shared with every other header.

## Fix applied

1. **Product Title is now frozen** as the third identity column, using the same CSS-variable pattern as ASIN/SKU (`--w-title: 360px`, `--left-title: 285px` = `--w-asin + --w-sku` = 115+170), applied identically to both `<th class="col-title">` and `<td class="col-title">`.
2. **Line-clamp moved off the `<td>`** onto an inner `<div class="title-text">` (per the required structure), so the `<td>` itself never loses standard table-cell layout behaviour. The inner div uses `-webkit-line-clamp: 3` (was 2), `min-height: 60px`.
3. **Consistent row height**: `min-height: 60px` on `.title-text` — confirmed live (real browser measurement) that a 9-character title (`"HEAD-4363"`) and a 175-character title both produce an identical `60px` div height, `75px` row height (60px + 2×7px padding). Short titles are never visually "shorter" than long ones.
4. **Sorting removed from ASIN, SKU, and Product Title headers**: `sortable: false` in `VISIBLE_COLUMNS` for these three; `renderHeader()` skips attaching any click/keydown listener and omits the sort-hint span entirely for non-sortable columns; `th.no-sort { cursor: default; }`. All 12 metric columns remain `sortable: true`, unchanged.

## Reconciliation with v006

**0 mismatches** across 53,843 products × 3 periods × 13 fields (including `title` itself) — v007 reuses v006's exact embedded payload and `calcProduct()` function unchanged; only rendering/layout code was touched. Full detail in `07_EVIDENCE/validation/2026-07-20__v007_product_title_alignment_evidence.md`.

## Real-browser confirmation

Chrome 150.0.7871.125 (already installed, not downloaded for this task), driven via the Chrome DevTools Protocol, both required viewports. Full detail and screenshots in `07_EVIDENCE/validation/2026-07-20__v007_browser_validation_evidence.md`.

## Status

**PASS.**
