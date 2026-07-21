# v004 CSV Validation Evidence

**What this is:** Verification that CSV export exactly matches the corrected v004 displayed dataset.

---

## Method

CSV generation logic is unchanged from the already-validated v002/v003 mechanism (RFC 4180 escaping, UTF-8 BOM, filter-aware, all-filtered-rows-not-just-current-page) — only the underlying row data and column set changed for v004. Re-executed the actual `csvEscape`/column-mapping logic from the generated file against the real 30-day dataset (53,843 rows, all 17 columns).

## Results

| Check | Result |
|---|---|
| CSV generation completes without error | YES — 231ms for 53,843 rows × 17 columns |
| CSV values match displayed dataset for Sessions | YES — same source object property, no separate CSV-specific transformation exists that could diverge |
| CSV values match displayed dataset for Page Views | YES — same source |
| CSV values match displayed dataset for Conversion Rate | YES — numeric values and precise N/A strings both pass through unchanged (no formula re-evaluation at CSV-export time, single source of truth) |
| CSV values match displayed dataset for CTR | YES |
| CSV values match displayed dataset for Buy Box | YES — post-fix numeric values (0–100 range) confirmed in the CSV sample |
| CSV values match displayed dataset for ACOS | YES |
| CSV values match displayed dataset for Category Avg Price | YES — post-outlier-fix values (e.g. £12.62 not the old raw-average style figures) confirmed present |
| Active filters respected | YES — CSV export always reads from `filtered`, the same array driving the visible table, never `allRows` |
| All filtered rows exported, not just current page | YES — confirmed by construction (`filtered.map(...)`, no `.slice()` applied before CSV generation) |
| Formulas exported as values, not spreadsheet formulas | YES — plain numbers/strings only, no `=`-prefixed content, no formula syntax anywhere in the generator |
| Precise N/A classifications preserved in CSV | YES — the exact strings (`N/A — source outside reporting date coverage`, `N/A — no matching traffic source row`) appear verbatim in the CSV sample, not collapsed to a generic value |
| No helper fields exported | YES — only the 17 approved display columns are included; internal fields (`sessions_class`, raw `sub_source_id`, etc.) are never part of the column set |
| No yellow fields exported | YES — confirmed via the same yellow-field property check used for the HTML validation |
| No credentials in CSV | Investigated the same "5435" false-positive numeric-substring match as the HTML check — confirmed coincidental, not a real credential; no match for the real host, password, or `ANPIA_DB_*` names |

## Filename pattern

Unchanged from v002/v003: `YYYY-MM-DD_<account>_<marketplace>_amazon_no_moving_<period>d.csv` — confirmed present in the generator code, not modified for v004.

## Status

**PASS.**
