# UI/Filter/CSV Validation Evidence — ANPIA Rebuild (REQ-01-D02)

**What this is:** Real Node.js/V8 execution testing of v003's embedded client-side logic against the actual generated file, superseding the earlier same-day version of this file (which recorded this as not applicable, since no v003 HTML existed at that time).

**Method (unchanged from D01's established approach):** the actual v003 HTML file is read from disk and its embedded `DATASETS`/`PERIOD_RANGES` JSON and the same filter/sort/summary/CSV-escape functions used by the real page are re-executed in Node.js — not simulated, not hand-verified.

---

## File under test

`09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html` — 126,852,855 bytes.

## Extraction robustness note (disclosed, not hidden)

The first extraction attempt in the test script failed with a `JSON.parse` error. Root-caused (not blamed on the HTML): the test script's boundary-detection logic searched for a literal `;\n` sequence to find the end of the embedded JSON, which is fragile against (a) the file's `\r\n` line endings (Python's default text-mode write on Windows) and (b) an inline trailing comment on the `PERIOD_RANGES` line. Fixed by replacing the marker-search approach with a proper brace/bracket-depth scanner that correctly handles quoted strings, escapes, and trailing content — the same category of "test-script bug, not application bug" already documented in D01's validation report. Re-run after the fix passed.

## Test results

| Check | Result |
|---|---|
| HTML parses without error | YES (1,238 ms for 126.9MB) |
| Row counts match the Python-side build | YES — 7d: 53,843, 14d: 53,843, 30d: 53,843 (exact match) |
| Period ranges correct | YES — 7d: 2026-07-13→2026-07-19, 14d: 2026-07-06→2026-07-19, 30d: 2026-06-20→2026-07-19 |
| Yellow fields present in row data | **NONE** — confirmed clean via property-existence check on real row objects, not a text-substring grep (a substring grep on the file does match the inert `YELLOW_FORBIDDEN` JS array declaration itself — investigated and confirmed to be self-documentation only, never used as actual column data; same category of false positive as D01's "Category Avg Price" finding) |
| Account filter (LEDSONE + UK, 30d) | 15,778 rows |
| Marketplace filter (DCVoltage + Germany, 30d) | 3,967 rows |
| DCVoltage + France (expected empty) | **0 rows** — confirmed, consistent with the established finding that DCVoltage has no France listings |
| Summary-card dedup total (30d) | £19,985.29 / 9,003 units — **matches the Python-side reconciliation exactly** |
| Summary-card dedup total (14d) | £8,801.49 / 3,905 units — matches exactly |
| Summary-card dedup total (7d) | £4,284.48 / 1,802 units — matches exactly |
| CSV escaping produces valid output | YES |
| CSV contains no credential strings | YES |
| Full `DATASETS` JSON contains no credential strings | YES |
| Sort performance (30d array, full sort by PPC Spend) | 69 ms |
| Full CSV generation (30d array, all rows, all columns) | 157 ms, 21,394,831 characters |

## Browser performance assessment

All in-memory operations (parse, filter, sort, summary-card computation, full CSV generation) complete in low milliseconds to low seconds even at the full 53,843-row × 3-period scale — consistent with D01's finding that client-side JS performance is not the constraint. **The 126.9MB file size (up from v002's already-flagged 41.7MB, since v003 correctly includes all three periods' full zero-activity-inclusive row population) is the disclosed delivery concern** — initial network download time was not and cannot be measured in this environment, same caveat as D01.

## No yellow fields in CSV

Confirmed by construction: `columnsForPeriod()` in the (unmodified, reused) v002 template JS never includes any yellow-field name, and the CSV export only ever iterates `columns` — verified via the same Node-executed CSV-generation test above.

## No credentials exposed

Confirmed via direct pattern scan of the extracted `DATASETS` JSON and a CSV sample — zero matches for the real host/password/etc. strings.

## Status

**PASS.**

## One next step

None outstanding for this validation. See the handover for the file-size delivery question, which remains an open, disclosed business decision (not a validation failure).
