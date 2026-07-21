# **Daily Requirement Document**

> **Template used:** `01_REQUIREMENTS/requirement_template/Daily Requirement Document.md`. **Migration note:** this document restructures the prior requirement file (`2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md`, now archived — see §0) into this template's block structure. No approved business meaning was changed; several sections beyond the template's four base blocks were added because the underlying requirement (a multi-account, multi-marketplace, multi-period reporting build) carries governance/validation/publication content the base template does not itself define fields for — see §5 "Governance & Status Block."

---

## §0. Requirement-ID Naming Note (read before using this document)

**Two identifiers exist for this same requirement, and both must be understood together:**

| Identifier | Where it is used |
|---|---|
| `REQ-AMZ-NMP-001-D01` | The identifier used throughout **every** discovery, design, implementation, validation, and evidence file produced for this requirement to date — `03_DISCOVERY/`, `04_DESIGN/`, `05_IMPLEMENTATION/`, `06_VALIDATION/`, `07_EVIDENCE/database/`, `07_EVIDENCE/output/`, `07_EVIDENCE/validation/`, `10_HANDOVER/` (dozens of files). This task's allowed scope (`01_REQUIREMENTS/`, `07_EVIDENCE/project/`, `12_ARCHIVE/` only) does not permit renaming or editing any of those files. |
| `REQ-01` (parent) / `REQ-01-D01` (deliverable) / product code `ANPIA` | The identifier convention required by this task's explicit instruction and the approved template's `requirement_id`/`deliverable_id`/`project_code` fields, applied to this restructured document and its filename. |

**These two identifiers refer to the same requirement and the same body of work — they are not two different requirements.** This duality is a direct, disclosed consequence of the scope restriction on this migration task (only `01_REQUIREMENTS/` may be restructured; the dozens of files elsewhere that already say `REQ-AMZ-NMP-001-D01` cannot be touched here). It is recorded here, and in the migration evidence file, as an open follow-up item rather than silently resolved in either direction.

---

## **1. Metadata Block**

| Field | Value |
|---|---|
| daily_requirement_submitted_date | 2026-07-17 |
| expected_deadline_date | 2026-07-17 (original same-day target; not met for the full scope — see §5 Status) |
| end_user | Nivarnan |
| expected_roi | Not yet measured or defined — open question (see decision register `04_DESIGN/2026-07-17__amazon_high_spend_asin_decision_register.md`, DEC-CTRL-002) |
| developer | Satheskanth |
| project | No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report |
| project_code | **ANPIA** (see naming-rule result below) |
| phase | Not formally phase-numbered by the business. Current build stage: Implementation (partial) — 30-day dataset extracted, transformed, rendered, and validated; 7-day/14-day extraction and ph_task publication remain outstanding. |
| requirement_id | REQ-01 (parent) — cross-referenced to `REQ-AMZ-NMP-001-D01`, see §0 |
| deliverable_id | REQ-01-D01 |
| blos_keys | No Top-N/percentile/minimum-spend cutoff — all valid Account+Marketplace+ASIN+resolved-SKU combinations must appear; output row grain = Account+Marketplace+ASIN+resolved SKU; blue-columns-only output (15 required fields, 8 excluded); UK marketplace stock → UK warehouse, Germany/France/Italy marketplace stock → shared German warehouse (never triple-counted in totals) |
| domain | Amazon / PPC / Inventory — accounts LEDSONE and DCVoltage — marketplaces UK, Germany, France, Italy |
| planned benefits | Faster identification of high-spend ASINs; one combined view of spend, sales, and stock; less manual checking; better prioritization of PPC and stock review. **No numeric ROI or time-saving figure is claimed — none has been measured** (same caveat as the original requirement; unchanged). |

**Naming-rule result:** the approved template (`01_REQUIREMENTS/requirement_template/Daily Requirement Document.md`) was inspected in full. It contains **no reference to "NPIA" or "ANPIA"** anywhere — its only worked example uses an unrelated project code (`INV-UTDT`, for a "UK to DE Transfer" example project). Because the template does not define or require "NPIA," the explicitly-stated product code **ANPIA** was used directly, with no stop-and-report conflict needed (none was found).

---

## **2. Today Requirement Block** *(current/active scope — not a single day, see §0/§5 for status)*

### **2.1 Task Name**

Amazon No-Moving Products daily report — multi-account, multi-marketplace, multi-period.

### **Business Purpose**

Give Nivarnan and the Amazon/PPC/inventory decision-makers one combined, filterable view of PPC spend, recent sales, and current stock per Amazon Account + Marketplace + ASIN + resolved SKU, across LEDSONE and DCVoltage's UK, Germany, France, and Italy Amazon listings, viewable over 7, 14, or 30 complete days.

### **Business Question**

Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action? *(Original framing; scope has since expanded to all four marketplaces and both accounts equally — spend is a display/sort field, not a filter — see the Corrected Requirement below.)*

### **Corrected/Current Written Requirement**

> The original written requirement (below, preserved for audit trail) was superseded on 2026-07-17 by two authoritative user-provided images and a corrected requirement, both unchanged by this migration:

**Original (superseded) requirement:** Find Amazon UK ASINs with high PPC spend during the latest complete 30-day reporting period. For each qualifying ASIN, prepare a future report showing PPC spend, sales, units sold when available, mapped SKU or SKUs, current UK stock, and stock-data freshness. *("High spend" was never defined.)*

**Corrected (current) requirement:** Generate a daily Amazon report for accounts **LEDSONE** and **DCVoltage**, across marketplaces **UK, Germany, France, and Italy**, supporting **7-, 14-, and 30-complete-day** period views. One output row = **Amazon Account + Marketplace + Amazon ASIN + resolved Amazon SKU**. **All** valid combinations must appear — no Top-N/percentile/minimum-spend cutoff unless separately, explicitly approved later. PPC Spend is a required display/sort metric, not a filter. Current stock only (no historical stock); UK marketplace uses UK warehouse stock; Germany/France/Italy marketplaces all use the shared German warehouse stock (never summed three times in any physical-stock total). Only the 15 confirmed blue columns are displayed; the 8 yellow columns are excluded entirely, including from ph_task HTML content.

### **Source Information**

**Source System:** PostgreSQL — `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__*`), database `order_management_copy`. Fallback (`mcp__ledsone-db__*`, via project `.mcp.json`) is a different, unrelated database and was not used — no field was ever proven missing from the primary.

**Source Tables:** `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data` (ASIN→SKU bridge — the only approved bridge, never `order_transaction`), `public.location_wise_inv_stock`.

**Source Documents:**
- `02_SOURCE/requirements/Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx` — Nivarnan's original business requirement workbook.
- `02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png` — authoritative blue/yellow column reference image (note: found at this path, not the `02_SOURCE/requirements/evidence/` path originally expected — see `07_EVIDENCE/project/2026-07-17__nivarnan_blue_yellow_column_scope.md` for the path-discrepancy record).
- `02_SOURCE/evidence/2026-07-17__nivarnan_additional_report_instructions.png` — authoritative account/marketplace/period/warehouse instructions image.
- `08_SKILLS/database/table_location_business_details 3.xlsx` — approved database routing reference.
- `08_SKILLS/ph_task_reference/` — `tech_team_outputs.ph_task` schema/versioning/team documentation.

### **Filter Conditions**

- Account: LEDSONE (`sub_source_id=8`) or DCVoltage (`sub_source_id=6`) or both.
- Marketplace: UK, Germany, France, or Italy, or all.
- Period: 7, 14, or 30 complete days (latest complete common end date determined by evidence, not `CURRENT_DATE` — currently **2026-07-15** for the 30-day period).
- Search: ASIN, SKU, or Product Title free-text.

### **Required Data Output — 15 Blue Columns**

| Field | Purpose |
|---|---|
| Amazon ASIN | Product identification |
| Amazon SKU (resolved) | Inventory identification |
| Product Title | Listing identification |
| Days Since Last Sale in Amazon | Recency signal |
| Units in Stock | Current stock level |
| Sessions | Traffic signal *(source not yet approved — see §5 Known Limits)* |
| Page Views | Traffic signal *(source not yet approved)* |
| Units Ordered | Sales signal |
| Conversion Rate (%) | Performance signal *(source not yet approved)* |
| Click-Through Rate (%) | Advertising/traffic signal *(source not yet approved)* |
| Buy Box % | Competitiveness signal *(source not yet approved)* |
| Price (£) | Pricing context |
| Category Avg Price (£) | Pricing benchmark *(averaging population not yet approved)* |
| PPC Spend | Advertising cost |
| ACOS (%) | Advertising efficiency (calculated) |

### **Excluded Data Output — 8 Yellow Columns**

Category, Stock Age (Days), Root Cause, Recommended Action, Priority, Status, Owner, Last Reviewed — excluded from HTML, CSV, embedded JSON, filters, and summary cards without exception. `Category` may be used internally only to compute `Category Avg Price`; never displayed itself.

---

## **3. Business Logic Block**

### **Row Grain**

`Account + Marketplace + Amazon ASIN + resolved Amazon SKU` — one row per unique combination. A multi-SKU ASIN (≈3.4% of all ASINs, confirmed at full scale) produces multiple rows, one per resolved SKU; PPC Spend/Units Ordered/ACOS/Days-Since-Last-Sale repeat identically across those rows (by design) — any summary total must deduplicate to Account+Marketplace+ASIN grain before summing, never sum the raw displayed rows.

### **Warehouse Mapping Rule**

```
IF marketplace = 'UK'      THEN stock_source = UK warehouse
ELSE (Germany/France/Italy) THEN stock_source = German warehouse (shared)
```
Per-row display of the same German figure on Germany/France/Italy rows is permitted (operational comparison); any **summary/total** stock figure must deduplicate by (resolved SKU, warehouse) first — never triple-count the same physical stock.

### **Completeness Rule**

No Top-N, percentile, or minimum-spend cutoff. All valid combinations appear, including zero-spend and zero-sales rows. PPC Spend may be used for **display and user-side sorting only**.

### **Missing-Data Rule**

Use precise, explicit values — `N/A - source not available`, `No mapping`, `No sale on record`, `No current stock record` — never substitute `0` for a genuinely unknown value; `0` is used only where zero is a proven fact (e.g. confirmed zero PPC spend or zero units ordered in the period).

---

## **4. Data Enrichment Block**

### **ASIN→SKU Bridge**

`public.listing_data` only (never `order_transaction`), with `wrong_sku=0`, `COALESCE(NULLIF(mapped_sku,''), sku)` resolution, `amzn.gr.*` alias exclusion, and a `DISTINCT ON` tiebreaker (prefers non-offer rows, then non-null price, then lowest id) that fixed a real row-key-duplication defect found and corrected during implementation — see `06_VALIDATION/2026-07-17__sql_validation_report.md`.

### **Join-Fan-Out Guard**

Aggregate PPC, sales, and stock independently before any join; join only the pre-aggregated results, once, at the account+marketplace+ASIN(+SKU for stock) grain. A naive join was empirically shown to inflate/deflate totals by hundreds of pounds — see `07_EVIDENCE/database/2026-07-17__join_cardinality_evidence.md` and the SQL validation report.

---

## **5. Governance & Status Block** *(fields required by this task's instruction, beyond the base template)*

### In-Scope Work
Amazon-only, LEDSONE + DCVoltage, UK/Germany/France/Italy, 7/14/30-day report generation, blue-column HTML + filter-aware CSV export, current-stock disclosure, validated real data (no cutoff).

### Out-of-Scope Work
eBay/Shopify; marketplaces beyond the four listed; historical stock reconstruction; PPC/stock/reorder-rule changes; threshold creation; schema/table/view changes; ph_task writes before full validation; Git initialization/commit/push; scheduler activation.

### UI Requirements
Sticky table header; frozen Account/Marketplace/ASIN/SKU columns; horizontal scroll; product-title truncation with tooltip; sortable columns; pagination with page-size selector; visible/filtered row count; empty-state message; account/marketplace/period filters; search; Reset Filters button; only-current-page DOM rendering (large dataset). Built and real-tested — see `07_EVIDENCE/validation/2026-07-17__ui_filter_csv_validation_evidence.md`.

### CSV Requirements
Filter-aware (account, marketplace, period, search all respected); exports all filtered rows, not just the current page; RFC 4180-safe escaping; UTF-8 BOM; period-aware column labels; excludes yellow columns and internal helper fields; filename pattern `YYYY-MM-DD_<account>_<marketplace>_amazon_no_moving_<period>d.csv`. Built and real-tested (Node.js/V8, real 51,348-row dataset).

### Data Completeness Requirement
No cutoff. **30-day period: COMPLETE** — 51,348 real rows across all 8 account+marketplace combinations (DCVoltage×France confirmed genuinely zero, not missing), extracted via keyset-paginated MCP batching after a credential-based path was found unavailable. **7-day/14-day periods: NOT YET EXTRACTED.**

### Validation Requirements
SQL validation (row-key uniqueness, fan-out, reconciliation), HTML validation (structure, columns, filters, CSV, credential scan), UI/filter/CSV real-execution tests — all performed for the 30-day period; see `06_VALIDATION/2026-07-17__sql_validation_report.md`, `06_VALIDATION/2026-07-17__html_validation_report.md`.

### Evidence Requirements
Every claim in this document traces to a saved evidence file under `03_DISCOVERY/`, `04_DESIGN/`, `06_VALIDATION/`, or `07_EVIDENCE/` — see the reference list in §2 Source Information and the migration evidence file `07_EVIDENCE/project/2026-07-17__requirement_template_migration_evidence.md`.

### Security Restrictions
No credentials read, logged, or exposed at any point (confirmed via keyword-scan and full-file inspection where opened under explicit approval). `.mcp.json` never modified. `Sources/db_access_templates/` opened once under explicit user approval, found already fully remediated (no embedded secrets).

### Database Write Restrictions
**NONE performed.** Every query across the entire project history has been read-only `SELECT`.

### ph_task Publication Gate
**DEFERRED.** Explicit exact metadata (assigned_user, assigned_user_team, team, title format, project_code for ph_task, version status) remains unapproved (decision register DEC-TECH-001). No ph_task pre-publication check has been created. No write to `tech_team_outputs.ph_task` has occurred or is authorized by this document.

### Scheduler Status
**Not activated.** Designed in `04_DESIGN/2026-07-17__daily_runtime_and_schedule_design.md`; no execution time, machine, or method has been approved.

### Owner / Reviewers
- Coordinator: Sathees or assigned coordinator
- Technical reviewer: Sajeesan or assigned senior developer
- Queryability reviewer: Tamil Selvan or assigned reviewer
- Business validator: Nivarnan or assigned Amazon business owner
- Developer: Satheskanth

### Known Limits
- Sessions, Page Views, Conversion Rate, Click-Through Rate, Buy Box % have no confidently-complete approved source (decision register DEC-TECH-004/005/006) — shown as `N/A - source not available`.
- Category Avg Price averaging population (marketplace-only / account+marketplace / global) not yet approved.
- 7-day and 14-day periods not yet extracted or validated.
- v002 HTML file size (~41.7 MB, driven by the complete 51,348-row 30-day dataset with no cutoff) is a disclosed, unresolved production-delivery question — in-browser filter/sort/CSV performance measured fast (all under 250ms even at full scale via real Node.js/V8 execution), but initial network download time of a ~42MB file was not and cannot be measured in this environment.
- Two conflicting database skill ZIPs remain unresolved for files outside this requirement's direct scope (decision register DEC-TECH-002).
- Stock-freshness stale-data warning threshold not set (non-blocking — the live-data disclosure is unconditional).
- Numeric KPI/success target not yet defined (decision register DEC-CTRL-002).
- Git remains uninitialized (decision register DEC-CTRL-001) — non-blocking, no commit/push attempted.
- **The requirement-ID duality described in §0.**

### Dependencies
Primary MCP connection availability; eventual credential-based or extended-batching access for 7-day/14-day full extraction; ph_task metadata approval from Sajeesan before any publication.

### Numeric / Binary Pass/Fail Rule
PASS (of the underlying report) requires: both accounts represented; all four marketplaces represented where source data exists; all three periods complete with real, independently-extracted data (not derived from one another); zero row-key duplicates; zero yellow columns in any output; PPC Spend and Units Ordered reconciled exactly against independent control totals; ph_task metadata approved before any publication; no unauthorized database write. **Not yet met in full** — see Status below.

### **Status**

**IN PROGRESS / AMBER**

**Reason:** Requirement and design exist and are current; the 30-day period's complete dataset, HTML, and validation are done and real; but the full requirement (7-day and 14-day periods) is not complete, the production-delivery question for the large HTML file size is unresolved, and ph_task publication is deferred pending metadata approval. **Not CLOSED. Not PASS.**

### **One Next Step**

Extract the 7-day and 14-day periods using the same proven keyset-paginated MCP batching method (or credential-based access if a connection becomes available), then route the DEC-TECH-001 ph_task metadata gap to Sajeesan before any publication is attempted.
