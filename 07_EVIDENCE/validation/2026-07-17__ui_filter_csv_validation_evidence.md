# UI / Filter / CSV Validation Evidence

**What this is:** Real, executed test results for the 10 required test scenarios, run in an actual Node.js/V8 JavaScript engine (the same engine Chrome uses) against the real, complete 30-day dataset extracted from the generated v002 HTML — not simulated or reasoned about statically.

**Why it exists:** Per instruction, filter/search/CSV/performance behavior must be validated before any pre-publication check.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Technical reviewer: Sajeesan. Queryability reviewer: Tamil Selvan.

**Method:** The client-side filter/CSV/sort functions (`applyFilters`, `csvEscape`, `slugify`) were extracted verbatim from `templates/amazon_no_moving_report_template_v002.html` and executed under Node.js v22.19.0 against the actual 51,348-row dataset parsed out of the real generated HTML file — real V8 execution, real data, real timings.

---

## TEST 1 — Account=LEDSONE, Marketplace=UK

**Expected:** Only LEDSONE UK rows. **Result:** 14,643 rows returned; `every` row has `Account==='LEDSONE'` and `Marketplace==='UK'` — **TRUE** for both. Execution time: 5ms. **PASS.**

## TEST 2 — Account=DCVoltage, Marketplace=Germany

**Expected:** Only DCVoltage Germany rows. **Result:** 3,861 rows; all match both conditions. Execution time: 2ms. **PASS.**

## TEST 3 — Account=All, Marketplace=France

**Expected:** Both accounts' France data. **Actual, correctly reflecting real business data:** 5,630 rows, **only `LEDSONE`** present (`distinctAccounts: ["LEDSONE"]`) — because DCVoltage has zero France rows (confirmed fact from discovery, re-confirmed here in the real report data). This is the correct, honest behavior, not a bug — the filter did not incorrectly show 0 DCVoltage rows as if they existed. **PASS** (with the caveat that "both accounts" only applies where both actually have data).

## TEST 4 — Account=LEDSONE, Marketplace=All

**Expected:** LEDSONE across all marketplaces. **Result:** 30,645 rows, `distinctMarketplaces: ["France","Germany","Italy","UK"]` — all four present. Execution time: 3ms. **PASS.**

## TEST 5 — Search by ASIN

**Search term:** a real ASIN drawn from the dataset (`B07DRMT8BF`). **Result:** 1 matching row, confirmed containing the search term. Execution time: 35ms. **PASS.**

## TEST 6 — Search by SKU

**Search term:** a real resolved SKU from the dataset (`CL3RBMAPK`). **Result:** 15 matching rows (this SKU is shared across multiple ASINs/marketplaces, a real and expected outcome given SKU reuse). Execution time: 27ms. **PASS.**

## TEST 7 — Search by Product Title fragment

**Search term:** a real word fragment from a product title (`"8"`, incidentally a common character in titles). **Result:** 20,426 matching rows — correctly broad because a single-character/common fragment matches many titles; demonstrates the search is working against real title text at scale, not a bug. Execution time: 20ms. **PASS.**

## TEST 8 — Period switching (30 → 14 → 7)

**Result:** period "30" = 51,348 rows (real, complete); periods "7" and "14" = 0 rows each, **honestly empty** because those periods were not extracted this session (see `07_EVIDENCE/database/2026-07-17__mcp_batched_extraction_evidence.md`) — **not** faked/derived from the 30-day set, which was the specific defect that caused v001 to be rejected. Selecting 7 or 14 in the UI will show the empty-state message, not wrong data. **PARTIAL PASS** — mechanism proven correct; full pass requires the 7-day/14-day extraction (pending).

## TEST 9 — Pagination + CSV exports all filtered rows

Using the LEDSONE/UK filter (14,643 rows): page size 50 renders only 50 rows to the simulated DOM (`page1_rendered_rows: 50`), while the CSV export contains all 14,643 filtered rows (`csv_row_count_check: 14643`, `csv_exports_all_not_just_page: true`). CSV generation time: 45ms. **PASS.**

## TEST 10 — Yellow-column exclusion in CSV

**Initial naive substring scan incorrectly flagged "Category"** — investigated and found to be a **false positive**: the legitimate blue column "Category Avg Price (£)" contains "Category" as a substring. Re-verified with an **exact field-name match** against the real 17-column CSV header: **zero exact matches** for any of the 8 excluded yellow columns (Category, Stock Age (Days), Root Cause, Recommended Action, Priority, Status, Owner, Last Reviewed). **PASS** (corrected). CSV size for this export: 6,167,460 bytes (~6.2 MB for 14,643 rows).

## Full-dataset performance (all 51,348 rows, no filter)

| Operation | Real measured time (Node.js/V8) |
|---|---|
| `JSON.parse` of the full 30-day dataset (~41MB) | 243ms |
| Filter (empty filter, full pass-through) | 6ms |
| Sort by PPC Spend, descending | 75ms |

**Finding:** contrary to the earlier speculative concern in `07_EVIDENCE/output/2026-07-17__report_generation_evidence_v002.md` (written before this test was run), actual filter/sort/search/CSV operations are fast — all under 100ms even across the full 51,348-row dataset. The real, disclosed size concern is narrower than initially framed: it is specifically the **initial network download** of a ~41.7MB file (not measurable in this sandboxed environment, dependent on the end user's connection), not the in-browser JS processing, which performs well.

## Owner/reviewer

Technical reviewer: Sajeesan. Queryability reviewer: Tamil Selvan.

## Status

**PASS** for 9 of 10 scenarios at full marks; TEST 8 partial (mechanism correct, data pending for 2 of 3 periods).

## Pass/fail rule

PASS if every scenario is executed against real data with a real JS engine (not reasoned about statically) and results are reported exactly as measured, including a corrected false positive. Met.

## Known limitations

- Network download time of the 41.7MB file was not and cannot be measured in this environment.
- 7-day/14-day period filter/search/CSV behavior cannot be fully validated until those periods are extracted.
- No real browser (Chrome/Firefox/Edge) was used — Node.js/V8 executes the same JS engine core as Chrome, but full-browser behaviors (DOM rendering, sticky/frozen CSS, actual scrolling) were not tested end-to-end in a rendered browser window.

## Next action

Re-run TEST 8 fully once 7-day/14-day extraction completes. Consider a real-browser manual check of sticky headers/frozen columns/CSS rendering before final business sign-off.
