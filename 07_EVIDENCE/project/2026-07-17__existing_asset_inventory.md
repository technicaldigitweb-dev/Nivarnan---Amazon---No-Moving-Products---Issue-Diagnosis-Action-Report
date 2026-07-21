# Existing Asset Inventory

**What this is:** A record of everything already in the project (as of 2026-07-17) that could be reused, extended, or merged for REQ-AMZ-NMP-001-D01, per Skill 04 (Existing Asset First).

**Why it exists:** Project control mandates a documented existing-asset search before any new asset is created — reuse, extend, merge, then create, in that order.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Sources used:** Full project folder listing (`00_PROJECT_CONTROL` through `12_ARCHIVE`, excluding `Sources/`), primary MCP `list_skills`/`get_skill`.

**Evidence produced:** File listing below, cross-checked against the discovery checklist.

---

## Project folders as of this discovery (excluding `Sources/`)

```
.claude/settings.local.json
.mcp.json
00_PROJECT_CONTROL/source_references/  (AIOS instructions ZIP, aios_architecture.md)
01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md
02_SOURCE/2026-07-17__source_register.md
02_SOURCE/requirements/  (Nivarnan workbook)
07_EVIDENCE/project/  (folder inventory, structure-creation evidence, source-mapping evidence)
08_SKILLS/database/  (table_location_business_details 3.xlsx)
08_SKILLS/ph_task_reference/  (3 files)
README.md
```

`03_DISCOVERY/`, `04_DESIGN/`, `05_IMPLEMENTATION/`, `06_VALIDATION/`, `09_OUTPUTS/`, `10_HANDOVER/`, `11_REVIEW/`, `12_ARCHIVE/` were empty prior to this task.

## Checklist against Step 1 requirements

| Asset type | Found? | Detail |
|---|---|---|
| Existing Amazon PPC/spend report | **No** | No SQL, HTML, or report file exists anywhere in the project outside `Sources/`. |
| Existing ASIN-to-SKU mapping query | **No** local file, but a **verified live capability exists** on the primary MCP: the `listing_data` table plus the `ppc-stock-lookup` skill's documented resolution logic (§ Step 2/2.5 in that skill). This is a reusable *capability*, not a saved SQL asset in this project. |
| Existing stock lookup query | Same as above — no saved SQL in this project, but the `ppc-stock-lookup` skill (primary MCP) fully documents the query pattern, including the exact "top N by spend + stock" (Mode B) shape this requirement needs. |
| Existing 30-day sales query | **No** local file. `order_transaction`'s table definition (primary MCP) documents the correct revenue query pattern (`SUM(COALESCE(order_total,0))`, `order_status='Completed'`), but no project-local saved query exists. |
| Existing HTML output template | **No** — `09_OUTPUTS/html/` is empty. |
| Existing ph_task publisher | **No** — no insert/update script or automation exists anywhere in the project. |
| Previous prompts/outputs for this exact business problem | **No** — this is the first requirement and first discovery pass recorded under `01_REQUIREMENTS/` and `03_DISCOVERY/` for this project subfolder. |

## Conclusion

No project-local file can be reused or extended for the SQL/HTML/publishing implementation — none exists. However, the **primary MCP's own skill library already contains a validated, maintained method** (`ppc-stock-lookup`, `text-to-sql-single`, `text-to-sql-multi`) for exactly this class of question ("top ASINs by spend + stock"). This is the asset to *extend from* when implementation begins — not build parallel/duplicate logic. It is external to this project folder (lives in the primary database's skill registry) but is the closer, more current match than either locally-stored skill ZIP (see `07_EVIDENCE/project/2026-07-17__duplicate_risk_review.md` and `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`).

## Owner/reviewer

Coordinator: Sathees or assigned coordinator.

## Status

VALIDATED.

## Pass/fail rule

PASS if every category in Step 1 was explicitly checked and the result (found / not found) is recorded, not assumed.

## Known limitations

Only this project's own folders were searched — no GitHub repository, n8n/OpenFlow workflow export, or external documentation store was checked (none is configured as an approved source for this project; see Open Questions in the discovery file for the GitHub decision still outstanding).

## Next action

When implementation begins, start from the primary MCP's `ppc-stock-lookup` skill (Mode B pattern) rather than authoring new SQL from scratch.
