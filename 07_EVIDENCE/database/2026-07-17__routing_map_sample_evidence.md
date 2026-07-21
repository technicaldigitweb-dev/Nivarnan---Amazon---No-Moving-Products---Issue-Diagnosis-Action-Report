# Routing Map Sample Evidence

**What this is:** Bounded query evidence from `public.table_routing_map`, queried live on the primary skills-related MCP (`claude_ai_postgres`), for the REQ-AMZ-NMP-001-D01 business question.

**Why it exists:** Per the authority rule, the live routing map is priority #1 evidence for deciding which tables are authoritative for this report — above the approved workbook, skill files, and both conflicting skill ZIPs.

**Business question supported:** Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action?

**Source:** `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__execute_sql`), `public.table_routing_map`.

---

## Query 1 — PPC / spend concepts

```sql
SELECT domain, trigger_keywords, primary_tables, key_identifiers, business_context
FROM public.table_routing_map
WHERE trigger_keywords ILIKE '%PPC%' OR trigger_keywords ILIKE '%spend%' OR business_context ILIKE '%PPC%'
LIMIT 10;
```

**Result (1 row):**
- **domain:** Advertising / PPC
- **trigger_keywords:** spend, acos, roas, ppc, campaign, ad group, advertising spend
- **primary_tables:** `public.ppc`, `public.ppc_performance`, `public.ppc_etl_change_log`, `public.ppc_etl_automation_log`, `public.ppc_etl_targeting_performance_data`
- **key_identifiers:** ref_id, sku, parent_id, child_id
- **business_context:** Four-table PPC data model spanning Amazon, eBay, and Google Ads. Critical rule: eBay's ON_SITE (Advanced/CPC) and COST_PER_SALE (Standard/CPS) campaigns use different pricing models and must never be summed together.

## Query 2 — Stock / inventory concepts

```sql
SELECT domain, trigger_keywords, primary_tables, key_identifiers, business_context
FROM public.table_routing_map
WHERE trigger_keywords ILIKE '%stock%' OR trigger_keywords ILIKE '%inventory%' OR business_context ILIKE '%UK stock%'
LIMIT 10;
```

**Result (1 row):**
- **domain:** Inventory / Stock
- **trigger_keywords:** stock, inventory, warehouse, SKU availability, out of stock, low stock
- **primary_tables:** `public.location_wise_inv_stock`, `public.inv_final_stock`
- **key_identifiers:** sku
- **business_context:** Current live stock snapshots only — no historical point-in-time stock data. `location_wise_inv_stock` is default for country/region-level checks; `inv_final_stock` for warehouse-level. Every stock answer must disclose that figures reflect live data, not the past.

## Query 3 — ASIN / SKU / sales concepts

```sql
SELECT domain, trigger_keywords, primary_tables, key_identifiers, business_context
FROM public.table_routing_map
WHERE trigger_keywords ILIKE '%ASIN%' OR trigger_keywords ILIKE '%SKU%' OR trigger_keywords ILIKE '%sales%'
LIMIT 10;
```

**Result (4 rows, relevant row shown):**
- **domain:** Sales / Orders
- **trigger_keywords:** orders, revenue, sales, completed, transactions, invoice
- **primary_tables:** `public.order_transaction`
- **key_identifiers:** asin, item_id, product_id, sku, order_id
- **business_context:** Master sales/orders table — the central bridge table holding every product identifier (ASIN, item_id, product_id, SKU) and connecting to nearly every other table in the system. One row per order line item across all platforms.

(Other rows returned — Inventory/Stock again, Component SOT/BOM, Amazon Search & Ranking — not relevant to this requirement and not used further.)

---

## Coverage classification

**FULL.** All three business areas this requirement needs (PPC spend, sales, current UK stock) are explicitly routed by the live `public.table_routing_map` to named, existing tables. No metadata-search fallback was required — the routing map itself resolved every area.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

VALIDATED — live query results, reproducible via the SQL above.

## Pass/fail rule

PASS if routing-map coverage is classified using only live query results, not the approved workbook or either skill ZIP (those are lower-priority evidence per the authority rule and are cross-checked separately in the skill-version reconciliation file).

## Known limitations

The routing map itself is a maintained table, not a schema-enforced contract — its `primary_tables` values were spot-verified against live `list_objects`/`get_table_definition` output (see `candidate_table_structure_evidence.md`) rather than trusted blindly.

## Next action

Proceed to verify each routed table's structure, grain, and filters — see `07_EVIDENCE/database/2026-07-17__candidate_table_structure_evidence.md`.
