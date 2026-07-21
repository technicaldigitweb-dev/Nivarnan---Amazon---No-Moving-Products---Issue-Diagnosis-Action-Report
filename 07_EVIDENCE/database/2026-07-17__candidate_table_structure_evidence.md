# Candidate Table Structure Evidence

**What this is:** Column-level, grain-level, and filter-level verification of every table this requirement touches, sourced live from the primary skills-related MCP (`claude_ai_postgres`).

**Why it exists:** Per Step 6/Step 3 of the discovery instructions, no candidate table may be relied on by name alone — structure must be confirmed live before use.

**Business question supported:** REQ-AMZ-NMP-001-D01 (Amazon UK high-spend ASINs, sales, current UK stock).

**Source:** `PRIMARY_SKILLS_MCP` — `get_table_definition`, `get_object_details`, `execute_sql` against `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.location_wise_inv_stock`, `public.inv_final_stock`, `public.listing_data`.

---

## `public.ppc` (Metadata / Dimension) — MCP: PRIMARY_SKILLS_MCP

| Column | Type | Notes |
|---|---|---|
| ppc_etl_id | bigint | PK |
| source | tinyint | 1=Amazon, 2=eBay, 3=Google |
| source_name | varchar | AMAZON / EBAY / SHOPIFY (label only; source=3 is actually Google Ads) |
| marketplace_id | tinyint | |
| market_place | varchar | e.g. UK, Germany, US |
| sub_source_id | tinyint | |
| ss_name | varchar | Account name |
| parent_id | varchar(255) | Campaign ID (meaning shifts by record_main_type) |
| child_id | varchar(255) | '0' for top-level rows |
| record_main_type | varchar(15) | campaign / ad_group / ad / asset_group / asset |
| record_subtype | varchar(30) | Amazon: SP/SD/SB; eBay: ON_SITE/COST_PER_SALE/OFF_SITE |
| record_name | varchar(255) | Entity display name |
| record_status | varchar(20) | active / paused / archived etc. |
| bidding_strategy | varchar(10) | Auto/Manual (Amazon) |
| bid | decimal(5,2) | Budget (campaign) or bid (ad_group) |

**Role in report:** metadata join to exclude Amazon SB (Sponsored Brands) campaigns for ASIN-scoped spend ranking (SB cannot be attributed to a specific ASIN — see below).

## `public.ppc_performance` (Fact) — MCP: PRIMARY_SKILLS_MCP

Live column list confirmed via `get_object_details` (matches skill-documented schema exactly):

| Column | Type |
|---|---|
| performance_data_id | bigint |
| date | date |
| source | bigint (1=Amazon, 2=eBay, 3=Google) |
| source_name | text |
| marketplace_id | bigint |
| marketplace | text |
| sub_source_id | bigint |
| ss_name | text |
| ref_id | text — ASIN (Amazon), item_id (eBay) |
| sku | text — Amazon only; '0' for others |
| record_type | text — ad / product / asset / campaign |
| record_id | text |
| parent_id | text |
| child_id | text |
| impressions | bigint |
| clicks | bigint |
| sales | double precision |
| orders | double precision |
| spend | double precision |
| category_name | text |
| user_name | text |

**Grain:** For Amazon (source=1), one row per **ad** per **date** (`record_type = 'ad'` is the only Amazon grain available).

**Verified indexes:** `(source, date)`, `(parent_id, record_type, date)`, `(ref_id, source) WHERE ref_id <> '0'`, `(child_id, record_type, date)` — confirms the table is designed to be queried exactly this way.

**Role in report:** PPC spend source.

## `public.order_transaction` — MCP: PRIMARY_SKILLS_MCP

| Column | Type | Notes |
|---|---|---|
| order_item_info | bigint | PK |
| order_id | text | Invoice ID |
| item_id | text | eBay item ID |
| asin | text | Amazon ASIN |
| product_id | text | Shopify product ID |
| sku | text | Internal SKU |
| item_price | numeric | Reference only — **not** revenue |
| quantity | bigint | Units |
| order_status | text | Cancelled / Completed / Deleted / Hold / Inprogress / New / Pending / Refunded — **live data also contains "Canceled" (single-L), an undocumented variant, see Step 9 note below** |
| order_date | timestamp | |
| order_total | double precision | **The correct revenue field** — never `item_price * quantity` |
| source_name | text | AMAZON / EBAY / SHOPIFY / B&Q / WAYFAIR |
| market_place | text | Order marketplace country |
| fba_sales | boolean | Amazon only |
| ss_name | text | Store account |
| user_name | text | PH holder |

**Grain:** one row per order line item.

**Role in report:** sales revenue/units source.

## `public.location_wise_inv_stock` — MCP: PRIMARY_SKILLS_MCP (live `get_object_details`)

| Column | Type | Nullable |
|---|---|---|
| id | bigint | YES |
| sku | text | YES |
| stock | bigint | YES |
| location | text | YES — known values: UK, Germany, US |
| updated_at | timestamp without time zone | YES |

**Indexes:** `(sku, location)`, `(location)`.

**Grain:** current live snapshot, one row per SKU per location (see `join_cardinality_evidence.md` for the small number of exceptions found).

**Role in report:** current UK stock source (default table per the `ppc-stock-lookup` skill — used unless a specific warehouse is named, which this requirement does not).

## `public.inv_final_stock` — MCP: PRIMARY_SKILLS_MCP

Warehouse-level stock (sku, stock, warehouse_name, warehouse_location). **Not used** for this report — the requirement asks for UK stock generally, not a named warehouse, so `location_wise_inv_stock` is the correct default per the skill's table-selection rule. **No date/freshness column exists on this table at all** (confirmed in its definition) — noted for completeness, not a gap for this requirement since it isn't the table in use.

## `public.listing_data` — MCP: PRIMARY_SKILLS_MCP

| Column | Type | Notes |
|---|---|---|
| ref_id | text | ASIN (Amazon) / item_id (eBay) / variant_id (Shopify) |
| sku | text | Listing SKU as synced from channel |
| mapped_sku | text | Correct inventory SKU when it differs from `sku`; NULL if same |
| which_channel | integer | 1=Amazon, 2=eBay, 3=Shopify, 16=B&Q |
| market_place | text | |
| sub_source | bigint | |
| wrong_sku | bigint | 0=valid — **must always filter `wrong_sku = 0`** |
| is_parent / is_child | bigint | Parent rows have no sellable SKU — exclude for stock lookups |

**Role in report:** the only correct ASIN→SKU bridge for a PPC-sourced report (explicitly documented: "Never use `order_transaction` as a bridge for PPC/traffic → stock — `listing_data` is the only correct SKU resolver for this path").

---

## Amazon UK filter — verified values

| Filter | Table | Column | Confirmed value | Evidence |
|---|---|---|---|---|
| Amazon | `ppc_performance` | `source` | `1` | table definition + live query (§ below) |
| Amazon | `order_transaction` | `source_name` | `'AMAZON'` | table definition + live query |
| UK | `ppc_performance` | `marketplace` | `'UK'` | live query, 7,957,930 rows |
| UK | `order_transaction` | `market_place` | `'UK'` | live query |
| UK | `location_wise_inv_stock` | `location` | `'UK'` | live query, 43,738 rows |

```sql
SELECT source, source_name, marketplace, COUNT(*) AS row_count, MIN(date) AS min_date, MAX(date) AS max_date
FROM public.ppc_performance
WHERE source = 1 AND marketplace = 'UK'
GROUP BY source, source_name, marketplace;
-- → source=1, source_name=AMAZON, marketplace=UK, row_count=7,957,930, min_date=2025-01-01, max_date=2026-07-16
```

## Sponsored Brands (SB) exclusion rule

Per the `ppc` table definition (live, primary MCP): Amazon does not provide ad-level data for SB campaigns — only one ASIN gets mapped to an SB campaign that actually covers multiple ASINs. **For any ASIN/SKU-scoped question (this requirement is exactly that), SB rows must be excluded** (`p.record_subtype <> 'SB'`, joined via `public.ppc`). This was applied in the join-multiplication test — see `join_cardinality_evidence.md`.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED — all columns and filters confirmed via live `get_table_definition`/`get_object_details`/`execute_sql`, cross-checked against each other and found consistent.

## Pass/fail rule

PASS if every column and filter value used in the eventual report SQL can be traced to a live query result in this file, not to the workbook or either skill ZIP alone.

## Known limitations

- `order_transaction.order_status` contains an undocumented "Canceled" (single-L) variant alongside the documented "Cancelled" — a data-quality inconsistency, not a schema gap. Must be handled explicitly (both spellings) if cancellations are ever excluded from a sales metric — see open question in the discovery file.
- `ppc.source_name = 'SHOPIFY'` for `source = 3` is a legacy/incorrect label — `source = 3` actually means Google Ads in this table. Not relevant to this Amazon-only requirement but worth flagging so it isn't mis-copied into a future Google Ads task.

## Next action

Use this structure to determine PPC/sales date coverage and stock freshness — see `07_EVIDENCE/database/2026-07-17__data_freshness_evidence.md`.
