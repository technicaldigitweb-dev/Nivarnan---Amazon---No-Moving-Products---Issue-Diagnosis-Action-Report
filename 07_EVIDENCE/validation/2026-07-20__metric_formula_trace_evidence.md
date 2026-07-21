# Metric Formula Trace Evidence — v004

**What this is:** Row-level trace of real data through source → aggregation → formula → HTML result, per REQ-01-D02's v004 fix instructions. Selected across REAL, TRUE_ZERO, OUTSIDE_COVERAGE, and NO_MATCH classifications, both accounts (where available), multiple marketplaces, and all three periods.

**A real defect was found during this evidence-gathering exercise, not before:** the first Buy Box % trace showed **10000.0%** for a case that should have been 100%. Investigated immediately — see "Buy Box % scale defect" below.

---

## Buy Box % scale defect (found and fixed during trace evidence gathering)

**Found:** `amz_traffic_by_asin.buyBoxPercentage` is stored already on a **0–100 scale** (live-verified: `MIN=0.0, MAX=100.0`, sample rows showing `100.0` meaning 100%, not `1.0`). `anpia_period_aggregation.derive_ratios()` computed `bb_weighted_num / bb_weight_denom * 100` — the trailing `× 100` double-applied the percentage conversion (the weighted numerator already carried the 0–100 scale), producing values up to 10000.0 for a true 100% Buy Box rate.

**Fix:** removed the erroneous `× 100` in `derive_ratios()`. Re-verified across the full 30-day dataset: 3,625 numeric Buy Box values, `MIN=0`, `MAX=100`, **100% within the valid 0–100 range** after the fix (was previously reaching 10000.0 before).

## Trace rows

### REAL example (7-day, LEDSONE, Germany)
- ASIN `B07BFQNJ39` / SKU `WCVCBS+RPR44WH`
- Source: `amz_traffic_by_asin` has a matching daily row within 2026-07-13..2026-07-19 for this ASIN/account/marketplace.
- Aggregated period values: Sessions=2, Units Ordered=1, Buy Box=100.0 (raw source value, sessions-weighted with only one contributing day).
- Formula: Conversion Rate = 1 ÷ 2 × 100 = **50.0%**.
- HTML result: Sessions=2, Conversion Rate=50.00%, Buy Box=100.00%.
- **PASS.**

### TRUE_ZERO example (7-day, LEDSONE, France)
- ASIN `B015RLJ1CE` / SKU `CRFF100GB`
- Source: feed covers the account/marketplace for this period; this ASIN has appeared in the feed's full history (confirmed tracked) but has zero matching rows within this specific 7-day window.
- Aggregated: Sessions=0, Units Ordered=0, Buy Box=0.
- Formula: Conversion Rate = 0 units ÷ 0 sessions → sessions=0 but units also 0 → business convention: **0.00%** (not N/A, since both are confirmed, not unknown).
- HTML result: Sessions=0, Conversion Rate=0.00%, Buy Box=0.00%.
- **PASS.**

### OUTSIDE_COVERAGE example (7/14/30-day, DCVoltage, Germany — identical across all 3 periods)
- ASIN `B07C7G69F8` / SKU `12IP6715`
- Source: DCVoltage's traffic feed for Germany stopped 2026-04-22 — zero overlap with any of the 3 reporting windows.
- HTML result (all 3 periods): Sessions = `N/A — source outside reporting date coverage`, Conversion Rate = same reason (propagated, not recalculated from a missing number), Buy Box = same reason.
- **PASS** — precise reason shown, not the old generic string.

### NO_MATCH example (7/14/30-day, LEDSONE, Germany — identical across all 3 periods)
- ASIN `B018OUTQ84` / SKU `LDMST64E274`
- Source: LEDSONE Germany's feed is current and covers this window, but this specific ASIN has **never once** appeared in `amz_traffic_by_asin`'s full history for this account/marketplace (confirmed via the ever-tracked-ASIN set, not merely "no row this period").
- HTML result (all 3 periods): Sessions = `N/A — no matching traffic source row`.
- **PASS** — correctly distinguished from the DCVoltage case above (different underlying cause, different displayed reason).

### 30-day edge case (LEDSONE, Germany) — a genuine, correctly-handled ambiguity
- ASIN `B076361WV8` / SKU `12MIP20360`: Sessions=0 (REAL — a matching row was found with a recorded value of 0), but Units Ordered=1 (from `order_transaction`, independent of the traffic feed).
- Formula: Conversion Rate = 1 ÷ 0 → undefined. Business rule: Sessions is a confirmed real 0, but Units Ordered is nonzero, so this is a genuine data anomaly (a sale without a matching session record), not a "confirmed zero-activity" case — correctly shows **N/A** (not `0.00%`, not a fabricated large percentage), since dividing a real unit by a confirmed-zero denominator is undefined, not zero.
- **PASS** — correct, safe handling of a real edge case, not silently papered over.

## Reconciliation cross-check (dedup summary totals, unaffected by the Buy Box fix since Buy Box isn't summed into spend/units totals)

30-day: £19,985.29 / 9,003 units (dedup) — unchanged from the pre-Buy-Box-fix figure, confirming the fix was correctly isolated to the Buy Box calculation only, with no side effect on spend/units totals.

## Status

**PASS**, with one real, significant defect found and fixed during this exact evidence-gathering step (Buy Box ×100 double-application) — documented transparently, consistent with this project's established practice of investigating rather than assuming correctness.
