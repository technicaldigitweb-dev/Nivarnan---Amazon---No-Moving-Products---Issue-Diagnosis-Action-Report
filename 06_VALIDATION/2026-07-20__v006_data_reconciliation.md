# v006 Data Reconciliation (vs. v005)

**What this is:** Confirmation that the v006 presentation-layer fix changed no business calculation, per the task's explicit instruction ("Do not change validated business calculations unless a reconciliation proves that an existing value is wrong").

---

## Method

v006 reuses the **exact same embedded compressed dataset as v005**, byte-for-byte — confirmed by direct string comparison of the extracted `B64_GZIP_DATA` payload from both files: `B64_PAYLOAD_IDENTICAL_TO_V005: true`. v006's `calcProduct()` function is unchanged from v005 (same source lines, same formulas, same missing-data classification logic) — only the rendering/formatting layer (`fmt()`, `render()`, CSS, header markup) was modified.

## Result

| Comparison | Result |
|---|---|
| Products compared | 53,843 |
| Periods compared | 7, 14, 30 |
| Fields compared per row | 12 (Sessions, Page Views, Units Ordered, Conversion Rate, Buy Box, PPC Spend, CTR, ACOS, Units in Stock, Price, Category Avg Price, Days Since Last Sale) |
| Total value comparisons | 1,938,348 |
| **Mismatches** | **0** |

## Why zero mismatches were expected, and confirmed

This is not a coincidental match between two independent calculations — it is the same JavaScript function, executed against the same data, in both files. The reconciliation exists to prove that the presentation-layer edits (which touched `render()`, `fmt()`, header generation, and CSS) did **not** accidentally alter `calcProduct()`, `periodRange()`, or the embedded dataset itself. Direct source comparison confirms `calcProduct()` is byte-identical between v005 and v006's `<script>` blocks.

## Missing-data classification unchanged

Confirmed: the same four values (`'N/A — source outside reporting date coverage'`, `'N/A — no matching traffic source row'`, a confirmed `0`, or a real number) are produced by v006 for every product/period — the presentation fix changes only how these values are *displayed* (compact `N/A` + tooltip instead of the full string inline), never the underlying classification decision.

## Status

**PASS.**
