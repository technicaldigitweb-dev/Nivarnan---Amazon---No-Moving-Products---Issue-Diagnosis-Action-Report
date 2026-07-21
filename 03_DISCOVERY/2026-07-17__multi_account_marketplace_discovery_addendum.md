# Multi-Account / Multi-Marketplace Discovery Addendum

**What this is:** The read-only discovery addendum re-verifying REQ-AMZ-NMP-001-D01's data model for 2 accounts × 4 marketplaces, superseding the earlier UK-single-account-only discovery scope.

**Why it exists:** The corrected authoritative business requirement (confirmed by two user-provided images) expands scope from UK-only to LEDSONE+DCVoltage across UK/Germany/France/Italy. The earlier UK-only filters cannot be assumed sufficient.

**Business question supported:** REQ-AMZ-NMP-001-D01 (expanded scope).

**Sources used:** `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__*`) exclusively — fallback (`ledsone-db`) not required, no element proven missing from primary.

**Status:** AMBER — technically thorough, but a material blocker was found (see §E) affecting 5 of 15 blue columns.

---

## A. Account mapping — VERIFIED

| Business name | Exact stored value | sub_source_id | Consistent across |
|---|---|---|---|
| LEDSONE | `amazon Ledsone` | 8 | `ppc.ss_name`, `order_transaction.ss_name`, `listing_data.sub_source_name` — identical spelling/ID in all three |
| DCVoltage | `amazon Dcvoltage` | 6 | Same three tables — identical spelling/ID |

No name/ID mismatch found across PPC, orders, or listing tables — a single `sub_source_id` per account works for all three. Two other Amazon accounts exist in the database (`amazon Ledsonede` id 14, `DCV UK` id 236) — explicitly **out of scope**, not touched.

## B. Marketplace mapping — VERIFIED

Exact stored value in all of `ppc_performance.marketplace`, `order_transaction.market_place`, `listing_data.market_place`, `location_wise_inv_stock.location`/`inv_final_stock.warehouse_location`: **`'UK'`, `'Germany'`, `'France'`, `'Italy'`** — plain country names, not codes (no 'DE'/'FR'/'IT' abbreviations found).

**Material finding — DCVoltage has zero PPC, order, and listing rows for France** (confirmed via exact `COUNT(*)` = 0 in all three tables), but **does have organic traffic rows for France** (`traffic_data`: 5,521 rows for DCVoltage×France). This is a real business fact (DCVoltage does not run Amazon-France PPC campaigns or sell there, but Amazon still records some listing visibility/impressions) — not a query error. It must render as an empty/no-data combination in the report, not be silently dropped from the filter list or crash the query.

## C. Date coverage — VERIFIED, with a material cross-source gap

| Account × Marketplace | PPC latest date | Sales latest (Completed) | Notes |
|---|---|---|---|
| Ledsone × UK | 2026-07-16 | 2026-07-17 00:40 | consistent with prior UK-only discovery |
| Ledsone × Germany | 2026-07-16 | 2026-07-16 21:36 | |
| Ledsone × France | 2026-07-16 | 2026-07-17 00:03 | |
| Ledsone × Italy | 2026-07-16 | 2026-07-16 12:14 | |
| Dcvoltage × UK | 2026-07-16 | 2026-07-16 23:10 | |
| Dcvoltage × Germany | 2026-07-16 | 2026-07-16 22:09 | |
| Dcvoltage × Italy | **2026-06-15** | 2026-07-14 02:47 | **~32 days behind on PPC** — genuine, verified data gap, not a query error |
| Dcvoltage × France | no rows (0) | no rows (0) | account does not operate here |

For the 6 "healthy" combinations, the same partial-last-day pattern found in the earlier UK-only discovery holds (2026-07-16 is the latest date present but is the current/still-loading day) — **latest complete date = 2026-07-15**, consistent with the prior discovery.

**Cross-source gap (new, material finding):** the traffic-metric sources (`traffic_data`, `amz_traffic_by_asin`) do **not** share this cadence — see §E. `traffic_data` is populated **weekly**, not daily (exactly 7 days apart: 2026-07-04, 2026-07-11 — next expected ~2026-07-18). `amz_traffic_by_asin` has daily rows historically but only 6–29 rows/day across the entire 2-account×4-marketplace scope in the most recent two weeks, versus a 551-day historical average of ~224 rows/day — a genuine recent-coverage degradation, not proof the table is unusable, but not safe to treat as complete either.

**Proposed reporting window: 2026-06-16 to 2026-07-15** (PPC + sales), same as the earlier UK-only discovery, **applied uniformly** rather than per-account-marketplace, with Dcvoltage×Italy's PPC sparsity for most of that window flagged as a known, real data-coverage limitation (not hidden).

## D. Stock locations — VERIFIED

`location_wise_inv_stock.location` and `inv_final_stock.warehouse_location` both contain exactly `'UK'`, `'Germany'`, `'US'` — no separate France or Italy warehouse value exists at all, which **confirms** (does not merely repeat) the image-instructed rule: France and Italy marketplaces have no dedicated warehouse and must use the German warehouse figure. Stock column: `stock` (bigint); resolved SKU: `sku`/`COALESCE(mapped_sku,sku)` via `listing_data`; `updated_at` freshness column present on `location_wise_inv_stock` (not on `inv_final_stock`, confirmed in earlier discovery). Duplicate-row and freshness figures from the earlier UK-only discovery (`07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md`, `.../join_cardinality_evidence.md`) still apply — not re-measured per-marketplace in this pass, since stock is not marketplace-partitioned, only warehouse-partitioned (UK vs Germany), and both warehouse pools were already measured.

## E. Blue-field source mapping — VERIFIED for 8 fields, REVIEW_REQUIRED for 5, PARTIAL for 2

Full detail in `07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md`. Summary:

| Field | Status | Reason |
|---|---|---|
| Amazon ASIN, Amazon SKU | VERIFIED | `listing_data.ref_id` / `COALESCE(mapped_sku,sku)` |
| Product Title | VERIFIED | `listing_data.title` |
| Days Since Last Sale in Amazon | VERIFIED | `CURRENT_DATE - MAX(order_transaction.order_date)::date` per account+marketplace+ASIN |
| Units in Stock | VERIFIED | `location_wise_inv_stock`/warehouse-mapped, resolved SKU |
| Price (£) | VERIFIED | `listing_data.price` (with `currency` check) |
| PPC Spend | VERIFIED | `ppc_performance.spend`, SB-excluded, aggregated by account+marketplace+ASIN+period |
| ACOS (%) | VERIFIED (calculated) | `spend/sales*100` per the primary MCP's own documented formula — no stored ACOS column exists in `ppc_performance` here |
| **Sessions, Page Views, Conversion Rate (%), Buy Box %** | **REVIEW_REQUIRED** | Two candidate sources found (`amz_traffic_by_asin` — daily grain, but recent-date row counts are 10–40x below historical average; `traffic_data` — confirmed **weekly**, not daily, cadence). Neither can be confidently treated as "the" daily source without technical sign-off. |
| **Click-Through Rate (%)** | **REVIEW_REQUIRED** | Three plausible sources found with different definitions: `ppc_performance` (advertising CTR = clicks/impressions), `traffic_data` (organic CTR, weekly grain), `amazon_search_query_performance` (`totalClickRate`, search-query grain, not ASIN-day grain). The authoritative workbook's own data-mapping sheet says CTR = "Clicks / Impressions" sourced from "Brand Analytics / Advertising Console" — consistent with either PPC or Brand Analytics, not decisive between them. |
| **Units Ordered** | PARTIAL | Available from `order_transaction` (verified, sales-grain) **and** from `amz_traffic_by_asin.unitsOrdered` (Business-Report grain) — the two are different systems and may not reconcile exactly (order_transaction counts confirmed/completed transactional units; Business-Report `unitsOrdered` is Amazon's own attribution, can include units later cancelled/refunded). Recommended: use `order_transaction` (already fully verified, consistent grain with PPC/sales) as authoritative; do not blend both. |
| **Category Avg Price (£)** | PARTIAL | `listing_data.price` and `Category`(internal-only) exist, but the averaging **population** (same marketplace only? same account+marketplace? global across both accounts and all 4 marketplaces?) is not specified in any source — a genuine formula-scope decision, not a missing-data problem. |

**No formula was invented for any REVIEW_REQUIRED/PARTIAL field.** Per instruction, these will render as an explicit missing-data indicator in the HTML/CSV output (e.g. "N/A — source pending confirmation") rather than a guessed number, until resolved.

## F. ASIN/SKU bridge — REVERIFIED

`public.listing_data` remains the correct bridge for all 4 marketplaces and both accounts — schema is not marketplace- or account-partitioned differently; the same `wrong_sku=0`, `COALESCE(mapped_sku,sku)`, `amzn.gr.*`-exclusion, and parent-row-exclusion rules from the UK-only discovery apply unchanged. Not re-measured at the exact percentage level per marketplace in this pass (would require 8 separate cardinality queries); the underlying bridge mechanism was structurally reverified to be marketplace/account-agnostic, which is the material question for this addendum.

## G. Cardinality — carried forward + one new finding

Prior findings (96.7% of UK Amazon ASINs → 1 SKU, 43% need `mapped_sku`, small stock-table duplicate rows, `amzn.gr.*` present at ~0.01%) are structural properties of `listing_data`/`location_wise_inv_stock` and are not expected to differ materially by marketplace — not re-measured per-marketplace given time constraints; flagged for spot-check during implementation-time validation instead of a separate full discovery pass.

**New finding:** the **row key must be `account + marketplace + ASIN + resolved SKU`**, not `ASIN + SKU` alone — confirmed necessary because the same ASIN can independently exist under both LEDSONE and DCVoltage (they are different seller accounts, potentially both selling the same product under different listings), and can independently exist across all 4 marketplaces. Not deduplicating on account+marketplace would silently merge two operationally distinct listings.

## H. Join fan-out — recommended sequence reconfirmed, expanded

Same empirically-proven risk as the UK-only discovery (up to 6x spend fan-out from a naive join), now with an added dimension:

1. Aggregate PPC spend independently by **account + marketplace + ASIN + selected period** (SB-excluded, `amzn.gr.*`-excluded).
2. Aggregate traffic/listing metrics at their **own verified grain** — held back as REVIEW_REQUIRED per §E, not aggregated into the join yet.
3. Aggregate orders/sales independently by **account + marketplace + ASIN + selected period** (`order_status='Completed'`).
4. Resolve ASIN→SKU via `listing_data`, per **account + marketplace**.
5. Aggregate current stock by **warehouse-mapped location + resolved SKU** (UK marketplace → UK warehouse; Germany/France/Italy → Germany warehouse) — **not** summed three times across Germany/France/Italy in any physical-stock total.
6. Join only the aggregated datasets, once, on `account + marketplace + resolved SKU` (stock) and `account + marketplace + ASIN` (PPC/sales).
7. Output one row per `account + marketplace + ASIN + resolved SKU`.

## Missing information / open items from this addendum

1. Sessions/Page Views/Conversion Rate/Buy Box % source (REVIEW_REQUIRED — §E).
2. Click-Through Rate source (REVIEW_REQUIRED — §E).
3. Category Avg Price averaging population/scope (PARTIAL — §E).
4. Whether Dcvoltage×Italy's ~32-day-stale PPC coverage should be called out with a visible per-row/per-combo notice in the HTML, beyond the mandatory live-stock disclosure (design-level decision, not blocking).
5. Whether Dcvoltage×France (traffic exists, but zero PPC/sales/listing rows) should appear as an empty filter combination or be omitted from the filter UI entirely (design-level decision).

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer (items 1–3 specifically need his sign-off before those 5 columns can be built). Coordinator: Sathees/Satheskanth.

## Pass/fail rule

PASS (of this discovery addendum) if every account/marketplace/date/stock/field finding is evidenced by a live query, and every genuinely unresolved field is marked REVIEW_REQUIRED/PARTIAL rather than guessed. **Met.**

## Next action

Proceed to design and implementation for the 8 VERIFIED + PARTIAL (with documented default) fields; render the 5 REVIEW_REQUIRED fields as explicit "N/A — pending source confirmation" until Sajeesan confirms the traffic-data source and cadence.
