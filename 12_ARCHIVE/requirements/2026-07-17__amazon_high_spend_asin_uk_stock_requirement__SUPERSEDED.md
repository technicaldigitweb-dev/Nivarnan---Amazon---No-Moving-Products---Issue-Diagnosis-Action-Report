# Daily Requirement Document

> **ARCHIVED / SUPERSEDED (2026-07-17, restructured migration) — NOT THE ACTIVE REQUIREMENT.**
> This file has been restructured into the approved template and moved to `12_ARCHIVE/requirements/`. The single active requirement document is now:
> `01_REQUIREMENTS/2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md`
> No approved business meaning was changed during migration — this file is retained for audit trail only. See `07_EVIDENCE/project/2026-07-17__requirement_template_migration_evidence.md` for the full migration record.

## 1. Metadata

- requirement_id: REQ-AMZ-NMP-001-D01
- requirement_date: 2026-07-17
- project_name: Amazon - No-Moving Products - Issue Diagnosis & Action Report
- project_user: Nivarnan
- assigned_subfolder: `C:\Users\LED237\Documents\Projects\Nivarnan - Amazon - No-Moving Products - Issue Diagnosis & Action Report`
- parent_domain: Amazon / PPC / Inventory
- coordinator: Sathees or assigned coordinator
- technical_reviewer: Sajeesan or assigned senior developer
- queryability_reviewer: Tamil Selvan or assigned reviewer
- business_validator: Nivarnan or assigned Amazon business owner
- status: REQUIREMENT_DRAFT
- database_write_permission: NOT APPROVED
- production_change_permission: NOT APPROVED

## 2. Written Requirement

> **SUPERSEDED — MULTI-ACCOUNT AND MULTI-MARKETPLACE SCOPE CONFIRMED BY USER EVIDENCE (2026-07-17).** The paragraph below was the original written requirement and is preserved for audit trail. It has been superseded by two authoritative user-provided images (`02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png`, `02_SOURCE/evidence/2026-07-17__nivarnan_additional_report_instructions.png`) and the corrected requirement in §2A below. It is no longer the current scope.

Find Amazon UK ASINs with high PPC spend during the latest complete 30-day reporting period. For each qualifying ASIN, prepare a future report showing PPC spend, sales, units sold when available, mapped SKU or SKUs, current UK stock, and stock-data freshness.

"High spend" is not defined in this document.

## 2A. Corrected Written Requirement (current, supersedes §2)

Generate a daily Amazon report for accounts **LEDSONE** and **DCVoltage**, across marketplaces **UK, Germany, France, and Italy**, supporting **7-, 14-, and 30-complete-day** period views. One output row = **Amazon Account + Marketplace + Amazon ASIN + resolved Amazon SKU**. **All** valid account/marketplace/ASIN/SKU combinations in scope must appear — no Top-N, percentile, or minimum-spend cutoff unless a later written instruction explicitly approves one. PPC Spend is a required display/sort metric, not a filter. Current stock only (no historical stock); UK marketplace uses UK warehouse stock, Germany/France/Italy marketplaces all use the shared German warehouse stock (not summed three times in any physical-stock total). Only the 15 confirmed blue columns (see `07_EVIDENCE/project/2026-07-17__nivarnan_blue_yellow_column_scope.md`) are displayed; the 8 yellow columns are excluded entirely, including from ph_task HTML content.

Full detail: `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`, `04_DESIGN/2026-07-17__amazon_multi_account_marketplace_report_design.md`.

## 3. Business Question

Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action?

## 4. Who Benefits

Nivarnan and the Amazon, PPC, and inventory decision-makers responsible for reviewing advertising spend, sales performance, and stock availability.

## 5. Expected Benefit

- Faster identification of high-spend ASINs.
- One combined view of spend, sales, and stock.
- Less manual checking.
- Better prioritization of PPC and stock review.

No numeric ROI or time-saving figure is claimed here — none has been measured.

## 6. Included Scope

> **"UK only" and "latest complete 30-day PPC period" (singular) below are SUPERSEDED — MULTI-ACCOUNT AND MULTI-MARKETPLACE SCOPE CONFIRMED BY USER EVIDENCE.** Corrected scope: Amazon only; accounts LEDSONE and DCVoltage; marketplaces UK, Germany, France, Italy; periods 7/14/30 complete days (all three supported, not just 30); sales during the same period; current stock (UK→UK warehouse, Germany/France/Italy→German warehouse); ASIN-to-SKU mapping; account+marketplace+period filters; future HTML output; future ph_task publication after approval.

- Amazon only
- ~~UK only~~ — superseded, see above
- ~~latest complete 30-day PPC period~~ — superseded, see above (7/14/30 all supported)
- sales during the same period
- current UK stock snapshot
- ASIN-to-SKU mapping
- future HTML output
- future ph_task publication after approval

## 7. Excluded Scope

> **"non-UK marketplaces" below is SUPERSEDED** — Germany, France, and Italy are now in scope (see §6). eBay/Shopify remain excluded (Amazon only).

- eBay or Shopify
- ~~non-UK marketplaces~~ — superseded, see §6 (Germany/France/Italy now in scope; still excludes marketplaces beyond UK/Germany/France/Italy)
- historical stock reconstruction
- PPC changes
- stock changes
- reorder-rule changes
- threshold creation
- schema/table/view changes
- ph_task writes during discovery
- full automation before validation
- Top-N/percentile/minimum-spend cutoff (unless a later written instruction explicitly approves one)
- Category, Stock Age (Days), Root Cause, Recommended Action, Priority, Status, Owner, Last Reviewed columns (the 8 yellow columns) in any output

## 8. Existing Assets

**Authoritative mapped project control:**
- `00_PROJECT_CONTROL/source_references/AIOS GPT Project intructions, prompts and skill files-20260619T091849Z-3-001.zip` — AIOS GPT project instructions, prompts, and skill-authoring standards.
- `00_PROJECT_CONTROL/source_references/aios_architecture.md` — AIOS full architecture reference (MySQL/PostgreSQL tiers, execution loop, capability registry).

**Authoritative requirement source:**
- `02_SOURCE/requirements/Amazon - No-Moving Products - Issue Diagnosis & Action Report-Nivarnan-v001.xlsx` — Nivarnan's business requirement workbook for this project.

**Approved database routing reference:**
- `08_SKILLS/database/table_location_business_details 3.xlsx` — confirmed "Table Routing Map" documentation.

**Approved ph_task reference:**
- `08_SKILLS/ph_task_reference/` — schema, versioning, and assigned-team documentation for `tech_team_outputs.ph_task`.

**Other recorded facts:**
- `Sources/` remains the preserved original intake location; nothing has been moved or deleted from it.
- `02_SOURCE/2026-07-17__source_register.md` contains the mapped source register; the approved requirement workbook copy lives in `02_SOURCE/requirements/`.
- The two skill ZIPs (`Sources/skills 3 (1) (3).zip`, `Sources/skills_minimal_pack 2 (2).zip`) remain unresolved and cannot yet be treated as canonical — see §9.
- `Sources/db_access_templates/` remains restricted; not opened beyond a keyword-count scan, not copied anywhere.
- `.mcp.json` remains at the project root and unchanged; only its top-level key names have been read.

## 9. Duplicate and Parallel-Truth Risk

- Ten overlapping filenames between the two skill ZIPs contain conflicting content (different CRC-32/size), per `07_EVIDENCE/project/2026-07-17__source_mapping_evidence.md`.
- Neither skill ZIP is a strict superset of the other (each has files the other lacks).
- The live routing-map (`08_SKILLS/database/table_location_business_details 3.xlsx`) and confirmed metadata/evidence must take priority over either unresolved skill ZIP during discovery.
- No third merged skill pack may be created without technical review.
- Existing queries, reports, templates, and publishers must be checked before creating any new asset.

**Status: AMBER — technical-review item.** The two database skill ZIPs (`Sources/skills 3 (1) (3).zip` and `Sources/skills_minimal_pack 2 (2).zip`) have unresolved, conflicting overlapping content and neither has been selected, merged, or copied as canonical. This must be resolved by technical review before either is relied upon.

## 10. Required Evidence

- project-control rule summary
- source inventory
- routing-map evidence
- table and column evidence
- Amazon UK filter evidence
- reporting-date evidence
- ASIN/SKU cardinality evidence
- stock freshness evidence
- skill-version reconciliation
- duplicate-risk report
- SQL validation evidence
- HTML validation evidence
- ph_task validation evidence
- handover and closure
- Git commit after repository approval

## 11. Reusable Asset Expected

A documented reporting capability that retrieves validated Amazon UK PPC spend, sales, and current-stock information and produces a queryable HTML report without duplicating business truth.

Status: PLANNED.

## 12. Queryability Requirement

A clean LLM must be able to determine:
- what was requested;
- which sources were used;
- which tables and joins were verified;
- which reporting period was used;
- what the output contains;
- what evidence proves it;
- what remains unresolved;
- who reviews it;
- whether it is safe to publish or reuse.

## 13. Open Questions

1. ~~What qualifies as high spend: Top N, threshold, percentile, or another rule?~~ **RESOLVED by §2A** — no cutoff; all valid combinations appear; PPC spend is a display/sort field only.
2. ~~Should spend-with-zero-sales ASINs be included?~~ **RESOLVED by §2A** — all combinations appear regardless of spend or sales.
3. ~~Should sales include revenue, units, orders, or every supported measure?~~ **RESOLVED by the confirmed blue-column list** (`07_EVIDENCE/project/2026-07-17__nivarnan_blue_yellow_column_scope.md`) — Units Ordered only; Sales Revenue explicitly excluded pending separate written confirmation.
4. ~~How should one ASIN mapped to multiple SKUs be shown?~~ **RESOLVED by §2A** — one row per account+marketplace+ASIN+resolved SKU (decision register DEC-BUS-004, redefined and APPROVED 2026-07-17).
5. What stock-freshness age is acceptable (stale-data warning threshold)? — still OPEN; the mandatory "live data, not past records" disclosure is separate and does not require this threshold to be set.
6. Which ph_task user, team, title, status, and versioning values are required? — still OPEN; **gates ph_task publication** (decision register DEC-TECH-001).
7. Should Git be initialized, and which remote repository should be used? — still OPEN; non-blocking as long as no commit/push is attempted.
8. What numeric KPI or time-saving target should be used? — still OPEN.
9. Which version of each conflicting database skill file should be canonical? — still OPEN (technical sign-off required, decision register DEC-TECH-002); for the 3 files relevant to this requirement, live evidence favors `skills_minimal_pack 2 (2).zip` — see `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`.
10. **NEW** — Sessions/Page Views/Buy Box %/Conversion Rate source (two candidates, neither confidently complete — see `07_EVIDENCE/database/2026-07-17__blue_field_source_mapping.md` note A). OPEN.
11. **NEW** — Click-Through Rate source (three candidates — see blue-field source mapping note C). OPEN.
12. **NEW** — Category Avg Price averaging population/scope (no rule found anywhere — see blue-field source mapping note D). OPEN.

No answers are guessed or invented here.

## 14. Safety Rules

- Read-only discovery first.
- No production/database writes.
- No table, schema, view, or function creation.
- No ph_task insert or update without explicit approval.
- No business-rule creation.
- No credential exposure.
- No work outside the project root.
- No parent-AIOS promotion.
- Stop when joins, filters, freshness, skill authority, or publication rules remain unsafe.

## 15. Reviews

- Coordinator review: required.
- Queryability review: required.
- Technical review: required for skill reconciliation, SQL, credentials, and publication.
- Business validation: required for high-spend logic and final acceptance.

## 16. Requirement-Readiness Rule

PASS only when:
1. The requirement file exists.
2. Business intent is preserved.
3. Included and excluded scope are explicit.
4. Mapped sources are recorded.
5. Conflicting skills are explicitly marked AMBER.
6. Evidence requirements are listed.
7. Safety restrictions are listed.
8. Owners and reviewers are recorded.
9. Open questions are not answered by invention.
10. README is updated.
11. No database action occurred.
12. No credential was exposed.

Otherwise FAIL.

## 17. Status

REQUIREMENT_DRAFT → **scope corrected 2026-07-17** to multi-account/multi-marketplace per §2A. Discovery addendum complete (`03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md`). Design/implementation in progress. Still awaiting: ph_task metadata approval (Q6), stock-freshness threshold (Q5), Git decision (Q7), KPI (Q8), skill-ZIP sign-off (Q9), and the three field-source decisions (Q10–Q12).

**Note:** this file's name (`...amazon_high_spend_asin_uk_stock_requirement.md`) reflects the original UK-only, high-spend-filtered scope and is retained unchanged to preserve the audit trail/evidence path history — the content, not the filename, is authoritative going forward.

## 18. One Next Step

Route the still-open questions in §13 (items 5–12) to Nivarnan/Sajeesan/coordinator; proceed with implementation for all VERIFIED/PARTIAL fields in the interim.
