# HTML Validation Report — v003 — ANPIA Rebuild (REQ-01-D02)

**What this is:** Validation of `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html`, generated from the real, direct-PostgreSQL common daily dataset.

---

## File identity

Path: `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html`. Size: 126,852,855 bytes. v001 and v002 were not overwritten (both remain unchanged on disk). This is the next available version number.

## Structure

Built from the existing, previously-validated (2026-07-17) v002 template's client-side logic, reused unmodified — period switching, account/marketplace filters, search, reset, sort, pagination, page-size selector, sticky/frozen columns, RFC 4180-safe CSV export with UTF-8 BOM. Only the embedded `DATASETS`/`PERIOD_RANGES` data and the row-formatting rules (`anpia_html_generator.py`) are new for v003.

## Real, browser-engine (Node.js/V8) execution testing

Full detail in `07_EVIDENCE/validation/2026-07-20__ui_filter_csv_validation_evidence.md`. Summary: parses in 1.24s at full 126.9MB scale; row counts match the Python-side build exactly (53,843 × 3 periods); account/marketplace filters produce correct, independently-verifiable counts (including the expected DCVoltage×France=0 case); summary-card dedup totals match the independent Python reconciliation to the penny for all three periods; sort (69ms) and full CSV generation (157ms) both fast at full scale.

## Period switching

**PASS.** All three periods (7/14/30) share the identical 53,843-row population (the full bridge dimension, per the completeness fix), differing only in date-window-scoped additive/derived values — confirmed via the `PERIOD_RANGES` object and per-period row inspection.

## Yellow-field exclusion

**PASS.** No yellow field is a property of any actual row object (verified via `Object.prototype.hasOwnProperty` checks on real parsed row data, not a text grep). A plain-text grep of the file does match the inert `YELLOW_FORBIDDEN` JS array declaration (self-documentation listing the forbidden names) — investigated and confirmed this is not actual column/row data, the same category of false positive documented in D01's own v002 validation.

## Stock/snapshot correctness

**PASS by construction**, consistent with the common-dataset validation report — stock is joined once per final row via the warehouse-mapping rule (UK marketplace → `UK` location; Germany/France/Italy → `Germany` location, both confirmed as the actual, clean literal values in `location_wise_inv_stock`), never summed across days or across marketplace rows in any total.

## Ratio correctness

**PASS.** Conversion Rate, CTR, ACOS all recalculated from period-summed base totals (never averaged daily percentages); Buy Box % uses the disclosed sessions-weighted-average compromise (Amazon's own feed does not expose raw won/eligible counts at this grain) — documented in the field classification and design docs, not silently approximated without disclosure.

## Live stock disclosure statement

Present in the template (`These stock figures are based on live data, not past records.`), unchanged from v002, carried into v003.

## Credentials exposed

**NONE** — confirmed via direct pattern scan of the full embedded JSON and a CSV sample.

## Browser performance

All measured in-memory operations (parse, filter, sort, CSV generation) complete in well under 3 seconds even at full 126.9MB / 53,843-row-×3-period scale. **Network download time of a 126.9MB file was not and cannot be measured in this environment** — same disclosed, unresolved delivery-question caveat as v002 (which was 41.7MB); v003 is materially larger because it correctly includes the full zero-activity-inclusive row population for all three periods, not because of any inefficiency.

## Status

**PASS**, with one disclosed, unresolved production-delivery question (file size) carried forward from v002 and now larger — not a validation failure, a business/infrastructure decision for the coordinator.

## One next step

Route the file-size delivery question to the coordinator (Sathees or assigned) — options include gzip/br compression at serve time, pagination server-side instead of embedding all rows, or accepting the current size for an internal tool with a fast network path. Not decided by this task.
