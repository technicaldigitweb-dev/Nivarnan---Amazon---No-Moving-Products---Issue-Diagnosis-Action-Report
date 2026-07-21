# Nivarnan Blue/Yellow Column Scope — Evidence

**What this is:** Verified record of what the user-provided report-column reference image proves about required (blue) and excluded (yellow) output columns.

**Why it exists:** Column scope is authoritative requirement evidence and must not be silently reinterpreted or invented.

**Business question supported:** REQ-AMZ-NMP-001-D01 — which columns the daily Amazon report must display.

**Source-image path:** `02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png`

**Path discrepancy note:** the task instruction specified a target path of `02_SOURCE/requirements/evidence/2026-07-17__nivarnan_report_column_reference.png`. The image was found instead at `02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png` (also briefly observed under a doubled `.png.png` extension mid-copy, which self-corrected to a single `.png` by the time it was read). Per instruction ("do not maintain duplicate copies of the images in multiple AIOS folders"), the image was **not** copied or duplicated to the originally-specified path — this file references its actual, existing location.

**Confirmed via:** direct visual inspection of the image (a screenshot of Google Sheets, tab "NoMoving_Report-Satheskanth-17/07", of the authoritative Nivarnan workbook), not inferred from filename or prior conversation memory.

---

## What the image proves

The image is a screenshot of the `NoMoving_Report-Satheskanth-17/07` sheet with 23 header columns (A–W), color-coded:

- **Columns A, B, C, F, G, H, I, J, K, L, M, N, O, P, Q** — required, populated with real example data in every visible row (rows 4–11).
- **Columns D, E, R, S, T, U, V, W** — carry a **yellow** header/fill or are explicitly marked exclusionary in the image's own "Additional Instructions" block ("Only get blue colour filled datas only." / "Not this" — the "Not this" label is itself shown against a yellow-filled header cell).

## Confirmed required (blue) columns — 15, in image column order

| # | Column (image) | Column (image position) |
|---|---|---|
| 1 | Amazon ASIN | A |
| 2 | Amazon SKU | B |
| 3 | Product Title | C |
| 4 | Days Since Last Sale in amazon | F |
| 5 | Units in Stock | G |
| 6 | Sessions (30d) | H |
| 7 | Page Views (30d) | I |
| 8 | Units Ordered (30d) | J |
| 9 | Conversion Rate (%) | K |
| 10 | Click-Through Rate (%) | L |
| 11 | Buy Box % | M |
| 12 | Price (£) | N |
| 13 | Category Avg Price (£) | O |
| 14 | PPC Spend (30d £) | P |
| 15 | ACOS (%) | Q |

This exactly matches the 15 blue columns listed in the task instruction (Section 5) — independently confirmed by direct image inspection, not merely copied from the instruction text.

## Confirmed excluded (yellow) columns — 8

| # | Column (image) | Column (image position) |
|---|---|---|
| 1 | Category | D |
| 2 | Stock Age (Days) | E |
| 3 | Root Cause | R |
| 4 | Recommended Action | S |
| 5 | Priority | T |
| 6 | Status | U |
| 7 | Owner | V |
| 8 | Last Reviewed | W |

This exactly matches the 8 yellow columns listed in the task instruction (Section 6) — independently confirmed.

## Excluded scope

The 8 yellow columns above must not appear in the HTML table, CSV/Excel export, filters, summary cards, or ph_task HTML content, and must not be re-added under a renamed label. `Category` may be used internally only to compute `Category Avg Price`; `Stock Age (Days)`'s underlying freshness timestamp may be used internally for validation only — neither is displayed.

## Unresolved interpretation

- The image's period labels are all "(30d)" (Sessions (30d), Page Views (30d), Units Ordered (30d), PPC Spend (30d £)) — this is the workbook's **static reference example**, not proof that 7-day and 14-day views should keep a hardcoded "30d" label. Per the task instruction, displayed labels must reflect the selected period (e.g. "Sessions (7d)") — this is a display-logic requirement layered on top of the image, not contradicted by it.
- The image does not show a `Sales Revenue` column anywhere. Per the task instruction's own clarification, Sales Revenue must **not** be added as an output column without separate explicit written confirmation — this image provides no such confirmation, so Sales Revenue remains excluded from the output pending that confirmation.

## Owner/reviewer

Business validator: Nivarnan. Coordinator: Satheskanth (developer) / Sathees (coordinator).

## Status

VALIDATED — confirmed by direct image inspection.

## Pass/fail rule

PASS if every blue and yellow column claim in this file is traceable to a directly-observed image element, not to instruction text alone. **PASS** — both column lists were independently re-derived from the image and matched the instruction text exactly.

## Next action

Use this file as the authoritative column scope for field-level source mapping (`07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md`) and for the HTML template's column set.
