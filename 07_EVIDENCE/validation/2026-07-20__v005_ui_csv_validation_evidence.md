# v005 UI/CSV Validation Evidence

**What this is:** Real Node.js/V8 execution results for v005's UI logic, layout structure, and CSV export, honestly scoped to what this environment can verify.

---

## Table column visibility

**Account and Marketplace confirmed absent from `VISIBLE_COLUMNS`** (the array driving table headers/cells) — verified by direct inspection of the generated file: the literal strings `"Account"` and `"Marketplace"` appear zero times as column-label entries. They remain available internally (`r.accountIdx`/`r.marketplaceIdx`, resolved via `DATA.ACCOUNTS`/`DATA.MARKETPLACES`) for filtering, row identity, and CSV export.

**Visible column order confirmed** (15 columns, matches the required order exactly): Amazon ASIN, Amazon SKU, Product Title, Days Since Last Sale, Units in Stock, Sessions, Page Views, Units Ordered, Conversion Rate (%), Buy Box (%), PPC Spend, Click-Through Rate (%), ACOS (%), Price, Category Avg Price.

## Frozen columns

**ASIN and SKU only** — `col-asin`/`col-sku` CSS classes, `--left-asin: 0px`, `--left-sku: 115px` (= `--w-asin`, confirmed correct cumulative offset by direct inspection, same verification method as v004's layout validation). **Product Title is explicitly not frozen** (`title-cell` class has no `position: sticky`) — confirmed by CSS inspection.

## Account/Marketplace filters

Both filter `<select>` elements are populated dynamically from `DATA.ACCOUNTS`/`DATA.MARKETPLACES` at load time (`populateFilterOptions()`) — confirmed working via the filter test in the Node.js execution run (`Account=LEDSONE + Marketplace=UK` → 15,778 rows, matching the same figure independently confirmed in v004).

## Account/Marketplace in CSV

**Confirmed present** — `downloadCsv()`'s column list explicitly prepends `Account` and `Marketplace` (resolved from `DATA.ACCOUNTS[r.accountIdx]`/`DATA.MARKETPLACES[r.marketplaceIdx]`) ahead of the 15 visible columns, for exactly the reason required (available for filtering/analysis in the exported file even though hidden from the on-screen table).

## Only current page rendered

`render()` slices `filtered` to the current page (`pageSize` rows) before writing to `innerHTML` — confirmed unchanged from the already-validated v004 pagination pattern; the full 53,843-row array is held in memory but never rendered as DOM rows at once.

## Real execution results

| Check | Result |
|---|---|
| Sort (30-day, full array) | 7 ms |
| Filter (Account + Marketplace combined) | 3 ms |
| CSV generation (all 53,843 rows, 17 columns) | 284 ms, 21,565,233 characters |
| CSV includes Account/Marketplace | YES |
| CSV free of credential strings | YES |
| Yellow fields in row data | NONE |
| No credential strings anywhere in decompressed payload | YES |

## Formula section

Collapsed `<details>`/`<summary>` element confirmed present (`Calculation Formulas` heading, content hidden by default per the `<details>` element's native browser behavior — no JavaScript required for the collapse/expand itself). **Scanned for forbidden technical terms** (`PostgreSQL`, `schema`, `listing_data`, `ppc_performance`, `order_transaction`, `amz_traffic_by_asin`, `pipeline`, `SQL`, `database`) across the entire generated file, excluding the embedded data payload itself — **zero matches**. Content is limited to the six required formulas and their plain-language meanings, exactly as specified, nothing additional.

## Loading indicator / error handling

`#loadingIndicator` is visible by default (before JavaScript executes) and hidden only after successful decompression+parse; `#appBody` is hidden by default and shown only on success. A `try/catch` around the entire `init()` async function displays a plain-language error message in `#errorBanner` (mentioning only "a recent version of Chrome, Edge, Firefox, or Safari" — no technical decompression jargon) if decompression or parsing fails, rather than leaving a blank page. **Not visually confirmed in a real browser** (no browser available) — confirmed by code-path inspection and successful Node.js execution of the same async function.

## Real-browser validation

**NOT TESTED.** No browser automation tool or installed/approved browser was available in this environment. This is disclosed explicitly per the task's own instruction ("If no real browser is available: report browser visual validation as NOT TESTED; do not claim full browser PASS") — DOM structure and CSS arithmetic were validated instead, as an alternative, weaker form of assurance.

## Status

**PASS** for everything verifiable via real code execution and structural inspection. **Real-browser visual/interactive confirmation: NOT TESTED**, explicitly disclosed, not claimed as passed.
