# v007 Identity Column UI Handover

**Date:** 2026-07-20 · **Developer:** Satheskanth · **Project code:** ANPIA · **Requirement:** REQ-01-D02

## Disclosure: user-supplied screenshots not received

The task requested saving three user-supplied defect screenshots into `07_EVIDENCE/screenshots/v007/user-reported-ui-defect/`. **No image attachments were included in the message that requested this task** — the folder exists (created as instructed) but is empty. This is disclosed plainly rather than fabricated or silently skipped. The fix proceeded from the detailed textual defect description in the task instructions (points 1–7), which fully specified the required behaviour and was sufficient to implement and verify the correction.

## What was built

`09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v007.html` (3,922,103 bytes) — corrects v006's Product Title layout, freezes all three identity columns, and removes sorting from identity headers. v005 and v006 preserved unchanged (checksums verified before and after).

## What was fixed

1. **Product Title frozen** as a third sticky identity column (`--w-title: 360px`, `--left-title: 285px`), using the exact same header/body CSS-variable pattern already proven correct for ASIN/SKU in the v006 fix.
2. **Line-clamp moved off the `<td>`** onto an inner `.title-text` div, per the required structure — the table cell itself keeps standard `display: table-cell` behaviour.
3. **Three-line display** (was 2 in v006), `min-height: 60px` for a consistent row height regardless of title length — verified live: a 9-character title and a 175-character title both measure exactly 60px/75px (div/row height).
4. **Sorting removed from ASIN, SKU, and Product Title headers** — no click handler, no keyboard handler, no sort-hint indicator, `cursor: default`. All 12 metric columns remain sortable, confirmed via a live click test that changed row order.

## Data reconciliation

**0 mismatches** across 53,843 products × 3 periods × 13 fields (2,100,477 comparisons) against v006 — expected, since v007 reuses v006's exact dataset and calculation function unchanged; only the identity-column presentation was touched.

## Validation status

**PASS.** Real Chrome browser testing performed (Chrome 150.0.7871.125, already installed, not downloaded for this task) at both required viewports, covering all 15 required test scenarios (scroll behaviour, title-length edge cases, sort/no-sort behaviour, filters, period switching, search, pagination, CSV structure). Zero console errors. Five required screenshots plus a raw results JSON saved to `07_EVIDENCE/screenshots/v007/validated/`.

## Security status

Reference files unchanged (checksums verified before/after). No database writes performed. Credential scan clean across v007 and all new evidence files.

## File size

3,922,103 bytes — 876 bytes larger than v006 (3,921,227 bytes), from the additional CSS/JS for the third frozen column and the no-sort logic; the embedded dataset itself is byte-identical.

## Remaining blockers

1. **User-supplied defect screenshots were never received** — if the user still wants those specific images preserved as evidence, they should be re-sent as attachments in a follow-up message.
2. Category Avg Price business sign-off — unchanged, still pending.
3. DCVoltage / LEDSONE-UK / LEDSONE-Italy traffic-feed staleness — unchanged, external upstream gap.
4. `tech_team_outputs` excess-privilege scope — unchanged, still pending Sajeesan's review.

## Publication status

**DEFERRED — USER REVIEW REQUIRED.** No write to `tech_team_outputs.ph_task` occurred or was attempted. Database writes: NONE.

## One next step

Present v007 to Nivarnan for business review; separately, ask whether the three originally-referenced defect screenshots should be re-sent for the evidence record (not required for the fix itself, which is independently verified).
