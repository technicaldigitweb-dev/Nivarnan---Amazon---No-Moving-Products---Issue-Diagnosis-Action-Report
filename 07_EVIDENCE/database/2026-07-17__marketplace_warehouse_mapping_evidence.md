# Marketplace-to-Warehouse Mapping Evidence

**What this is:** Live-query evidence confirming the exact UK/Germany warehouse stock values and that the marketplace-to-warehouse business rule (UK→UK; Germany/France/Italy→Germany) is technically implementable as stated.

**Why it exists:** This rule directly controls which physical stock figure is joined to France/Italy rows — getting it wrong would silently misreport stock for two of the four marketplaces.

**Business question supported:** REQ-AMZ-NMP-001-D01, current UK/Germany/France/Italy stock display.

**Source:** `PRIMARY_SKILLS_MCP` — `execute_sql`/`get_object_details` against `public.location_wise_inv_stock`, `public.inv_final_stock`.

---

## Warehouse location values

```sql
SELECT DISTINCT location FROM public.location_wise_inv_stock ORDER BY location;
-- → Germany, UK, US

SELECT DISTINCT warehouse_location FROM public.inv_final_stock ORDER BY warehouse_location;
-- → Germany, UK, US
```

**Confirmed:** only three stock-warehouse pools exist in the entire database: `'UK'`, `'Germany'`, `'US'`. **There is no separate France or Italy warehouse value at all** — this independently confirms (from the database side, not just the user's image) that France and Italy marketplace rows have no dedicated stock source and must use the German pool, exactly as instructed.

## Applied mapping

| Marketplace | Warehouse stock source |
|---|---|
| UK | `location='UK'` |
| Germany | `location='Germany'` |
| France | `location='Germany'` (shared — no France warehouse exists) |
| Italy | `location='Germany'` (shared — no Italy warehouse exists) |

## Shared-stock double-counting risk

Because Germany, France, and Italy rows all resolve to the **same** `location='Germany'` stock query for a given SKU, a naive `SUM(stock)` across a physical-stock summary that includes all three marketplace rows would count the same physical units three times. Per instruction, any **overall/summary physical-stock total** must deduplicate by resolved SKU + warehouse (`Germany`) before summing — it must not sum three marketplace-row stock values as if they were three independent pools. Per-marketplace-row **display** (showing the same German stock figure on the Germany row, the France row, and the Italy row) is explicitly permitted by instruction for operational comparison — only the aggregate/summary total must avoid triple-counting.

## Stock schema (reconfirmed, unchanged from UK-only discovery)

`public.location_wise_inv_stock`: `sku` (text), `stock` (bigint), `location` (text), `updated_at` (timestamp) — freshness column present. `public.inv_final_stock`: warehouse-level breakdown, **no** `updated_at` column (unchanged finding from prior discovery) — not used for this report since the requirement is location-level (UK vs Germany-shared), not warehouse-name-level.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED.

## Pass/fail rule

PASS if the warehouse mapping is confirmed by an independent database query (not merely re-stated from the user's image), and the double-counting risk is explicitly documented with its scope (summary totals only, not per-row display). Met.

## Known limitations

Duplicate-row and update-recency figures for the German stock pool specifically (as opposed to UK, already measured in the prior discovery) were not separately re-measured in this pass — the mechanism (one row generally per SKU per location, small number of exceptions) is expected to hold structurally but should be spot-checked during SQL validation for the Germany location specifically.

## Next action

Implement the stock join as: `CASE WHEN marketplace='UK' THEN 'UK' ELSE 'Germany' END` as the warehouse-lookup key, joined once per `(account, marketplace, resolved_sku)`, with any summary total deduplicated by `(resolved_sku, warehouse_location)` before summing.
