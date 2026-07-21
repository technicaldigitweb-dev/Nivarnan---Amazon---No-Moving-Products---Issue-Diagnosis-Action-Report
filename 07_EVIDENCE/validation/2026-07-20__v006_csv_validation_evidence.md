# v006 CSV Validation Evidence

**What this is:** Real Node.js execution of v006's actual CSV generation logic, confirming the compact on-screen `N/A` display does not affect the exported file.

---

## Column structure

Confirmed via real execution: CSV header = `account,marketplace,asin,sku,title,daysSinceLastSale,currentStock,sessions,pageViews,units,conversionRate,buyBox,spend,ctr,acos,currentPrice,categoryAvgPrice` — **17 columns**: Account + Marketplace + all 15 visible report columns, exactly as required.

## Full reason text preserved (not shortened to "N/A")

Sampled real rows with an N/A classification and confirmed the CSV cell contains the **full** reason, e.g.:

```
DCVoltage,Germany,B07C7G69F8,12IP6715,"12 V POWERSUPPLY 300 W ...",809,399,N/A — source outside reporting date coverage,N/A — source outside reporting date coverage,0,N/A — source outside reporting date coverage,N/A — source outside reporting date coverage,0,N/A - not available for this product,N/A - not available for this product,7.89,19.14
```

The on-screen table shows only `N/A` for these same cells (per the UX fix) — the CSV export path (`csvValue()`) never calls the display-shortening `fmt()` function; it reads the raw calculated value directly, satisfying "the full missing-data reason may remain in CSV... Do not shorten CSV unavailable values to ambiguous blank cells."

## Null static fields

`null` values (e.g., unavailable Days Since Last Sale) export as the explicit string `N/A - not available for this product`, never an empty/ambiguous cell.

## Filtering / period / row-limit behavior

Unchanged from the already-validated v005 mechanism: CSV reads from the `filtered` array (respecting active Account/Marketplace/search filters and the selected period), exports **all** matching rows — confirmed by generating the CSV for the full unfiltered 30-day dataset: **53,843 rows**, not limited to the 50-row current page.

## Performance

238 ms to generate the full 53,843-row, 17-column CSV — consistent with v005's already-validated performance.

## Security

No credential strings found in the generated CSV content (scanned for the real host, password, and `ANPIA_DB_*` variable names — zero matches).

## Status

**PASS.**
