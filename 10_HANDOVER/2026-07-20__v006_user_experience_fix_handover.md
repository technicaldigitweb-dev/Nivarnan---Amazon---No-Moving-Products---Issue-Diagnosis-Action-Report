# v006 User-Experience Fix Handover

**Date:** 2026-07-20 · **Developer:** Satheskanth · **Project code:** ANPIA · **Requirement:** REQ-01-D02

## What was built

`09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v006.html` (3,921,227 bytes) — a presentation-layer correction of v005, addressing the reported defect (long N/A explanations overflowing into adjacent columns, columns appearing merged) while reusing v005's exact validated architecture and dataset unchanged. v005 preserved (checksum-verified unchanged).

## What was fixed

1. **The reported defect:** every unavailable-data cell now displays the compact text `N/A` only (never the long internal reason string), styled with an amber background clearly distinct from a real zero. The full reason is always available via the `title` attribute (native tooltip) and a matching `aria-label`, confirmed via direct DOM inspection in a real running browser — never deleted, only moved out of the visible cell text.
2. **A real defect found during this task's own testing, not user-reported:** the initial fix routed *every* string-typed field through the N/A-formatting function, which silently turned real ASIN/SKU values into "N/A" (caught via a real-browser screenshot showing `aria-label="Unavailable: B07C7G69F8"` — an ASIN, not a reason). Fixed by excluding ASIN/SKU from that code path.
3. **A second real defect found the same way:** frozen header cells for ASIN/SKU were missing the CSS class the sticky-positioning rules depend on, so the headers scrolled away horizontally while the body cells beneath them stayed correctly pinned — a severe header/data misalignment, visually confirmed in a screenshot before the fix and confirmed resolved (identical `getBoundingClientRect()` positions for header and body) after.

Both of these were caught only because real browser screenshots were reviewed, not just data reconciliation — reconciliation alone (0 mismatches, confirmed) would have missed both, since neither affected calculated values.

## Column/layout changes

Column order and visibility unchanged from v005 (Account/Marketplace hidden from the table, retained in filters and CSV). Widths updated to the specified values (SKU 165px, explicit widths for all 15 metric columns via a `<colgroup>`). Sticky columns limited to ASIN/SKU (unchanged). Row hover, group separators, centred numeric headers with abbreviation tooltips (CTR/ACOS), keyboard-focusable/sortable headers, and `scope="col"` accessibility markup are new in v006.

## Data reconciliation

**0 mismatches** across 53,843 products × 3 periods × 12 fields (1,938,348 comparisons) against v005 — expected and confirmed, since v006 reuses v005's exact dataset and calculation function unchanged; only rendering logic was touched.

## Validation status

**PASS.** Real headless-Chrome browser validation was performed (Chrome 150.0.7871.125, already installed on this machine, not downloaded for this task) at both required viewports (1366×768, 1920×1080), driven via the Chrome DevTools Protocol with real screenshots as evidence — not claimed without proof. Zero console errors. Full detail across the four validation/evidence documents.

## Security status

Reference files unchanged (checksums verified before/after). No database writes performed. Credential scan clean across v006 and all new evidence files.

## File size

3,921,227 bytes — 6,081 bytes larger than v005 (3,915,146 bytes), driven entirely by the additional CSS/JS for the presentation fixes; the embedded dataset itself is byte-identical. Well under the 5MB preferred target.

## Remaining blockers

1. **Native OS tooltip popup rendering** was not captured in the headless screenshot (a known headless-browser limitation) — the underlying `title`/`aria-label` attributes were confirmed correct via direct DOM inspection instead, which is arguably the more meaningful check (it's what assistive technology actually reads).
2. Category Avg Price business sign-off — unchanged, still pending.
3. DCVoltage / LEDSONE-UK / LEDSONE-Italy traffic-feed staleness — unchanged, external upstream gap.
4. `tech_team_outputs` excess-privilege scope — unchanged, still pending Sajeesan's review.

## Publication status

**DEFERRED — USER REVIEW REQUIRED.** No write to `tech_team_outputs.ph_task` occurred or was attempted. `daily_task` was not modified. Database writes: NONE.

## One next step

Present v006 to Nivarnan for business review — the reported visual defect is resolved and independently verified in a real browser, with two additional real defects found and fixed along the way.
