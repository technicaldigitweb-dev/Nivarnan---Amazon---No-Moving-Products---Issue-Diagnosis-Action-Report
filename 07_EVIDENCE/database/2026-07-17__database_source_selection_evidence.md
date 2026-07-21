# Database Source Selection Evidence

**What this is:** Evidence record of which PostgreSQL MCP connection was used for each part of the REQ-AMZ-NMP-001-D01 discovery, why, and what was found on each.

**Why it exists:** Two live PostgreSQL MCP connections are available in this session. Mid-discovery, the user redirected connection priority — this file documents that redirection, the verification performed, and which connection actually supplied each piece of evidence, so a future reviewer does not have to reconstruct it from chat history.

**Business question supported:** Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action? (REQ-AMZ-NMP-001-D01)

**Sources used:** `mcp__claude_ai_postgres__*` tools (primary), `mcp__ledsone-db__*` tools (fallback, configured via project `.mcp.json`).

---

## 1. Primary skills-related MCP identity

- **Tool prefix:** `mcp__claude_ai_postgres__*` — a pre-authorized claude.ai connector, already present in this session's tool list before this task began (not newly added by the user's request).
- **Tool count:** 13 tools confirmed (`list_skills`, `get_skill`, `get_table_definition`, `list_table_definitions` [implicit via error message], `execute_sql`, `explain_query`, `analyze_db_health`, `analyze_query_indexes`, `analyze_workload_indexes`, `get_top_queries`, `get_object_details`, `list_objects`, `list_schemas`) — matches the "approximately 13 tools" description given.
- **Claimed endpoint:** `https://mcp.vintageinterior.co.uk/mcp` — **this cannot be independently confirmed from inside the tool-calling sandbox.** The literal backing URL of an MCP connector is a platform-level binding, not exposed to the model through any tool call. Confidence on the endpoint string itself: **PARTIAL**.
- **Confidence on tool identity/relevance: CONFIRMED**, based on independent internal evidence (not just the user's claim):
  - `get_table_definition` example names (`ppc`, `order_transaction`, `inv_final_stock`, `listing_data`) exactly match the table names referenced throughout the project's two unresolved skill ZIPs (`TABLE_ppc.md`, `TABLE_order_transaction.md`, `TABLE_inv_final_stock.md`) and the approved routing workbook.
  - `list_skills` returned a skill literally named `ppc-stock-lookup`, matching `SKILL_ppc_stock_lookup.md` in both skill ZIPs.
  - `list_schemas` returned `tech_team_outputs`, `staging_ai`, `governance`, `blos`, `business_intelligence` — schema names that exactly match terminology used throughout `00_PROJECT_CONTROL/source_references/` (AIOS architecture doc, `0.1 LLM PROJECT INSTRUCTION.md.docx` RED/AMBER work classifications) and `08_SKILLS/ph_task_reference/` (`tech_team_outputs.ph_task`).
  - `order_transaction`'s documented eBay sub-source list includes `vintageinterior` (sub_source id 41) — a real seller-account name in this company's live data, consistent with (though not proof of) the claimed `vintageinterior.co.uk` domain.
  - `public.table_routing_map` exists here and its `Advertising / PPC`, `Sales / Orders`, and `Inventory / Stock` domain rows route to exactly the tables this business question needs.
- **Intended role:** PRIMARY (per user instruction, and independently justified by the evidence above).

## 2. Fallback project MCP identity

- **Tool prefix:** `mcp__ledsone-db__*`, configured via the project root `.mcp.json` (server name `ledsone-db`), confirmed present and unchanged throughout this project (checksum `69c55f9bafa405570a950550915ecb79b11266b52018b2e64f67c34118c3ff22`).
- **Confidence: CONFIRMED** — this is the project's own documented database access method (see `README.md` → Database Access Method, `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` §8).
- **Intended role:** FALLBACK, used only for a data element proven missing from the primary.

## 3. Checks performed on primary

- `list_schemas` — 16 user schemas including `public`, `tech_team_outputs`.
- `list_objects(public, table)` — confirmed `table_routing_map`, `ppc`, `ppc_performance`, `order_transaction`, `location_wise_inv_stock`, `inv_final_stock`, `listing_data` all exist.
- `execute_sql` against `public.table_routing_map` with ILIKE keyword filters for PPC/spend, stock/inventory, ASIN/SKU/sales — see `07_EVIDENCE/database/2026-07-17__routing_map_sample_evidence.md`.
- `get_table_definition` for `ppc` (covers `ppc`+`ppc_performance`+2 log tables), `order_transaction`, `inv_final_stock`, `listing_data`.
- `get_skill('ppc-stock-lookup')` — full skill text retrieved, directly matches this business question (Mode B: "top N ASINs/SKUs by spend with their stock").
- `get_object_details` for `location_wise_inv_stock` and `ppc_performance` — live column/index metadata, cross-checked against the skill-documented schema (exact match).
- Bounded `execute_sql` queries (all with explicit filters/LIMIT/GROUP BY, no unbounded scans) for: Amazon UK PPC row counts and date range, Amazon UK order_status distribution and date range, UK/DE/US stock row counts and update timestamps, daily PPC/sales row-count trend (last 10 days), ASIN→SKU cardinality, `amzn.gr.*` prevalence, `mapped_sku` population rate, and a join-fan-out demonstration query.

## 4. Elements present in primary

All required elements were found and verified live on the primary MCP:

| Element | Status | Evidence file |
|---|---|---|
| Routing map | Present, FULL coverage for PPC/Sales/Stock | routing_map_sample_evidence.md |
| PPC spend, Amazon UK filter, date coverage | Present | candidate_table_structure_evidence.md, data_freshness_evidence.md |
| Sales revenue/units, Amazon UK filter, date coverage | Present | candidate_table_structure_evidence.md, data_freshness_evidence.md |
| UK stock, SKU, freshness timestamp | Present | data_freshness_evidence.md |
| ASIN→SKU bridge (`listing_data`) | Present | join_cardinality_evidence.md |

## 5. Elements missing in primary

**None proven missing.** No TABLE_MISSING, COLUMN_MISSING, ROWS_MISSING, DATE_COVERAGE_MISSING, BRIDGE_MISSING, or FRESHNESS_MISSING condition was found on the primary MCP for any element this business question requires. The fallback MCP was therefore **not needed** for any report field.

## 6. Fallback reason

Not applicable for data sourcing — no proven gap. The fallback (`ledsone-db`) **was** queried earlier in this session, before the source-priority order was confirmed by the user. See §7 below for the corrected interpretation of that earlier work.

## 7. Correcting the prior audit note (per instruction)

Before the user supplied the connection-priority order, this discovery session queried `mcp__ledsone-db__*` first and found:
- No `public.table_routing_map`.
- No `public.ppc`, `public.ppc_performance`, `public.order_transaction`, or `public.location_wise_inv_stock` (only `public.migrations` exists in that connection's `public` schema).
- A structurally different, legitimately-organized operational database (schemas: `accounting`, `amazon_campaigns`, `order_management`, `inventory`, etc.) that documents real Ledsone business data but under a different table-naming convention than the project's routing workbook and skill ZIPs describe.

**Corrected interpretation (per instruction, not stated as previously written):**
- `ledsone-db` was queried before the approved source-priority order was established.
- Its findings are **not authoritative** for the PPC/Sales/Stock data areas covered by the primary skills-related MCP (`claude_ai_postgres`) — those areas are now fully covered, live-verified, on the primary.
- `ledsone-db` **remains an approved fallback** for any future data element proven missing from the primary.
- `ledsone-db` is **not invalid** — it is a real, correctly-configured operational database for this company; it is simply a different physical database than the one the project's AIOS documentation (routing workbook, skill ZIPs, ph_task schema) was written against.

**Label:** `SUPERSEDED AS PRIMARY-SOURCE EVIDENCE — RETAINED AS POSSIBLE FALLBACK EVIDENCE`

No `ledsone-db` findings were carried forward into any report-field conclusion in this discovery. All PPC/Sales/Stock conclusions in `03_DISCOVERY/2026-07-17__amazon_high_spend_asin_uk_stock_discovery.md` are sourced exclusively from `PRIMARY_SKILLS_MCP` (`claude_ai_postgres`).

## 8. Source conflicts

None found between primary and fallback for any field actually used, because no fallback data was used in any conclusion. The two databases were not combined or compared field-by-field beyond the schema-existence check in §7.

## 9. Cross-database join implications

Not required for this discovery — all needed data exists on the primary. If a future task needs both databases combined, recommended approach: **NOT_SAFE_TO_JOIN** by direct SQL (they are two separate PostgreSQL instances/connections with no cross-database FDW confirmed) — would require `APPLICATION_LAYER_JOIN` or `CONTROLLED_EXPORT_JOIN` with an explicitly mapped common business key (e.g. SKU), datatype normalization, and duplicate/missing-key risk assessment before any such join is attempted. This is a recommendation for a future task, not something built here.

## 10. Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer (per REQ-AMZ-NMP-001-D01 metadata). Queryability reviewer: Tamil Selvan or assigned reviewer.

## 11. Status

DRAFT — VALIDATED by live query evidence for the primary MCP; endpoint-string claim remains PARTIAL confidence (platform-level detail, not independently verifiable by this agent).

## 12. Pass/fail rule

PASS if: primary MCP identity is evidenced (not merely asserted), every table/finding is source-labelled, no fallback data was used without a proven-missing justification, and the safety checklist below is clean.

## 13. Safety checklist

- **Database writes:** NONE — every query executed was `SELECT`/read-only.
- **`.mcp.json` changed:** NO — checksum confirmed unchanged (`69c55f9bafa405570a950550915ecb79b11266b52018b2e64f67c34118c3ff22`) before and after this task.
- **Restricted files opened:** NONE — `Sources/db_access_templates/` was not opened.
- **Credentials exposed:** NONE — no connection string, password, host, or token was read or printed from any MCP configuration; only tool names, schema names, table names, and business data (spend/sales/stock figures, which are not credentials) were retrieved.

## 14. Known limitations

- The literal endpoint URL `https://mcp.vintageinterior.co.uk/mcp` could not be independently verified from within this agent's sandbox; only the tool's identity and behavior were verified.
- `ledsone-db` was not exhaustively mapped against `claude_ai_postgres` field-by-field; only enough was checked to establish they are different physical databases.

## 15. Next action

Proceed to use `claude_ai_postgres` (labelled `PRIMARY_SKILLS_MCP` throughout) as the sole source for the REQ-AMZ-NMP-001-D01 discovery conclusions; retain this file as the audit trail for why `ledsone-db` findings were superseded rather than discarded.
