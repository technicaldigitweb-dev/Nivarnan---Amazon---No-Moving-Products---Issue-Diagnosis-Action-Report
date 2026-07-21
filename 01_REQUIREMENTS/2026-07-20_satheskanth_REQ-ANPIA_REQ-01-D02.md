# **Daily Requirement Document**

> **Template used:** `01_REQUIREMENTS/requirement_template/Daily Requirement Document.md` — the same template used for D01. **Continuation note:** this document is **not** a rebuild of D01. It is a continuation deliverable that carries forward D01's incomplete commitments (7-day/14-day extraction, full period validation, database publication) into 2026-07-20. D01 (`2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md`) remains unmodified and unarchived — it is the historical record of 2026-07-17's work, not superseded.

---

## §0. Requirement-ID Naming Note (carried forward from D01, unchanged)

Two identifiers exist for this same underlying requirement:

| Identifier | Where it is used |
|---|---|
| `REQ-AMZ-NMP-001-D01` | Used throughout every discovery, design, implementation, validation, and evidence file produced to date (`03_DISCOVERY/`, `04_DESIGN/`, `05_IMPLEMENTATION/`, `06_VALIDATION/`, `07_EVIDENCE/database/`, `07_EVIDENCE/output/`, `07_EVIDENCE/validation/`, `10_HANDOVER/`). This task's allowed scope (`01_REQUIREMENTS/`, `07_EVIDENCE/project/` only) does not permit renaming those files. |
| `REQ-01` (parent) / `REQ-01-D02` (this deliverable) / product code `ANPIA` | The identifier convention required by the approved template's `requirement_id`/`deliverable_id`/`project_code` fields, applied to this document. |

This duality is unresolved (same open item as D01 §0) and is not decided by this document. It is repeated here so D02 does not silently drop a known-open item.

---

## **1. Metadata Block**

| Field | Value |
|---|---|
| daily_requirement_submitted_date | 2026-07-20 |
| expected_deadline_date | 2026-07-20 |
| end_user | Nivarnan |
| expected_roi | Not yet measured or defined — carried forward from D01 (decision register DEC-CTRL-002, unchanged by this document) |
| developer | Satheskanth |
| project | No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report |
| project_code | ANPIA |
| phase | Not formally phase-numbered by the business. Current build stage: Implementation continuation — 30-day dataset was extracted, transformed, rendered, and validated on 2026-07-17; 7-day/14-day extraction, full period validation, and ph_task publication are today's (2026-07-20) committed work. |
| requirement_id | REQ-01 (parent) — cross-referenced to `REQ-AMZ-NMP-001-D01`, see §0 |
| deliverable_id | REQ-01-D02 |
| previous_deliverable_id | REQ-01-D01 (2026-07-17) |
| blos_keys | Same as D01, unchanged: no Top-N/percentile/minimum-spend cutoff; output row grain = Account+Marketplace+ASIN+resolved SKU; blue-columns-only output (15 required fields, 8 excluded); UK marketplace stock → UK warehouse, Germany/France/Italy marketplace stock → shared German warehouse (never triple-counted) |
| domain | Amazon / PPC / Inventory — accounts LEDSONE and DCVoltage — marketplaces UK, Germany, France, Italy |
| planned benefits | Same as D01 (faster identification, one combined view, less manual checking, better prioritization) — no numeric ROI or time-saving figure is claimed for D02 either; unchanged limitation. |

---

## **2. Today Requirement Block**

### **2.1 Task Name**

Amazon No-Moving Products daily report — completion of 7/14/30-day multi-period delivery and database publication (continuation of D01).

### **Business Purpose**

Complete the benefit that D01 committed to but did not fully deliver on 2026-07-17: give Nivarnan and the Amazon/PPC/inventory decision-makers a working, validated, three-period (7/14/30-day) report, published to the approved database table, covering LEDSONE and DCVoltage across UK, Germany, France, and Italy.

### **Continuation Reference to D01**

- **D01 (2026-07-17) planned benefit was NOT fully delivered.** Status recorded in D01 §5: `IN PROGRESS / AMBER`, explicitly "Not CLOSED. Not PASS."
- **What D01 completed:** requirement/design finalized; SQL implementation built with a real defect (row-key duplication) found and fixed; the complete 30-day dataset (51,348 rows, all 8 account+marketplace combinations, zero cutoff) was extracted via keyset-paginated MCP batching; a rebuilt v002 HTML report was produced and validated (reconciliation exact match, real Node.js/V8-executed UI/filter/CSV tests).
- **What D01 left pending, carried into D02:**
  - 7-day dataset: not extracted.
  - 14-day dataset: not extracted.
  - Period selector: mechanism built and structurally correct, but only the 30-day period has real data behind it — 7-day/14-day switching has not been validated against real data.
  - Database publication to `tech_team_outputs.ph_task`: deferred (D01 §5 — ph_task Publication Gate), explicitly not attempted.
- **Reason recorded in D01:** delayed by a Claude session usage limit and an MCP bulk-data-fetch limitation (a single unbounded query timed out; the working fix — keyset-paginated batching — takes materially more steps than a single query would, which consumed the remaining time before 7-day/14-day extraction could start). D01 explicitly recorded this as a tool/session limitation, not a database or business-logic defect.

**This document (D02) does not restate any of the above as complete. It carries these exact pending items forward as today's commitments.**

### **Business Question**

Same as D01 (unchanged): which Amazon ASINs across LEDSONE/DCVoltage's UK/Germany/France/Italy listings are consuming PPC spend, and do their recent sales and current stock justify attention — now viewable and validated across all three committed reporting windows, with the result published where the business can access it.

### **Source Information**

Unchanged from D01: PostgreSQL `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__*`), database `order_management_copy`; tables `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.listing_data`, `public.location_wise_inv_stock`. No new source system introduced for D02.

### **Filter Conditions**

Unchanged from D01: Account (LEDSONE `sub_source_id=8` / DCVoltage `sub_source_id=6` / both), Marketplace (UK/Germany/France/Italy/all), Period (7/14/30 complete days), free-text Search (ASIN/SKU/Product Title).

---

## **3. Today's Business Commitment**

**The pending benefit from 2026-07-17 (D01) will be completed and delivered on 2026-07-20 (D02).**

Today's committed outputs (commitments for 2026-07-20 — **not yet complete as of this document's creation**):

1. Generate the complete 7-day report.
2. Generate the complete 14-day report.
3. Generate or refresh the complete 30-day report.
4. Validate all three reporting windows independently.
5. Ensure the HTML period selector switches between real 7-, 14-, and 30-day datasets.
6. Validate Account and Marketplace filters.
7. Validate the selected-period and filter-aware CSV downloader.
8. Publish the final validated HTML to the approved database table today.
9. Verify the database publication after writing.
10. Complete evidence, handover, and closure documentation.

None of the above outputs are being executed by this document. This document records the commitment only — see §16 for confirmation that report generation and database publication were not performed while creating this requirement.

---

## **4. Report Scope** *(unchanged from D01)*

**Accounts:** LEDSONE, DCVoltage.
**Marketplaces:** UK, Germany, France, Italy.
**Reporting windows:** Last 7 complete days; last 14 complete days; last 30 complete days — each independently extracted, not derived from another.
**Row grain:** Account + Marketplace + Amazon ASIN + resolved Amazon SKU.
**Warehouse mapping:** UK marketplace → UK warehouse stock; Germany/France/Italy marketplace → German warehouse stock (shared, never triple-counted).
**Stock disclosure:** the final HTML must state — *"These stock figures are based on live data, not past records."*

---

## **5. Required Output — 15 Blue Columns** *(unchanged from D01)*

| Field | Purpose |
|---|---|
| Account | Account identification |
| Marketplace | Marketplace identification |
| Amazon ASIN | Product identification |
| Amazon SKU | Inventory identification |
| Product Title | Listing identification |
| Days Since Last Sale in Amazon | Recency signal |
| Units in Stock | Current stock level |
| Sessions | Traffic signal *(source not yet approved — DEC-TECH-004/005/006, unresolved, carried from D01)* |
| Page Views | Traffic signal *(source not yet approved)* |
| Units Ordered | Sales signal |
| Conversion Rate (%) | Performance signal *(source not yet approved)* |
| Click-Through Rate (%) | Advertising/traffic signal *(source not yet approved)* |
| Buy Box % | Competitiveness signal *(source not yet approved)* |
| Price (£) | Pricing context |
| Category Avg Price (£) | Pricing benchmark *(averaging population not yet approved)* |
| PPC Spend | Advertising cost |
| ACOS (%) | Advertising efficiency (calculated) |

### **Excluded — 8 Yellow Columns** *(unchanged from D01)*

Category, Stock Age (Days), Root Cause, Recommended Action, Priority, Status, Owner, Last Reviewed — must not appear in visible HTML, hidden HTML, embedded JSON, CSV export, filters, summary cards, or the database-published HTML, without exception.

---

## **6. UI and CSV Requirements** *(unchanged in principle from D01; validation must now cover all three periods)*

Required controls: Account filter, Marketplace filter, Period selector (7/14/30 days), Search, Reset Filters, Download CSV, Sorting, Pagination, page-size selector.

Changing the selected period must update: report rows, date range, summary cards, column labels, metric values, CSV content, CSV filename.

CSV must export all rows matching the selected period, account, marketplace, search text, and active filters — all filtered rows, not only the visible page.

D01 built and real-tested this mechanism against the 30-day dataset only (`07_EVIDENCE/validation/2026-07-17__ui_filter_csv_validation_evidence.md`). D02 commits to validating the same mechanism against real 7-day and 14-day data, not assuming the 30-day result generalizes.

---

## **7. Data Retrieval Requirement** *(unchanged rule from D01, restated for D02's extraction work)*

The system must fetch complete real data. Do not use sample-only data, arbitrary row limits, Top-N filtering, PPC minimum thresholds, or one 30-day dataset reused for all periods.

If a single MCP query cannot return the complete dataset: use bounded batch extraction, deterministic keyset pagination, checkpoint every successful batch, reconcile expected vs. fetched row counts, do not silently skip failed ranges — the same method proven for D01's 30-day extraction (`07_EVIDENCE/database/2026-07-17__mcp_batched_extraction_evidence.md`).

Credential-based access may be used only when separately approved and securely available (unchanged from D01 — no credential source was found available during D01; this is not re-decided here).

---

## **8. Database Publication Requirement** *(new commitment — deferred throughout D01, committed for D02)*

**Target:** `tech_team_outputs.ph_task`.

Publication rules for D02:
- Publication only after all three periods (7/14/30-day) pass validation.
- Use the approved publication connection method.
- Do not use incomplete or sample HTML.
- Do not publish the failed v001 output.
- Use a transaction; rollback on failure.
- Verify the stored HTML after publication.
- Verify metadata.
- Verify no duplicate active output.
- Record publication evidence.
- Do not expose credentials.

**This document does not perform the database publication.** It records the commitment only. D01's decision register item DEC-TECH-001 (exact ph_task metadata: assigned_user, assigned_user_team, team, title format, project_code for ph_task, version status) remains unapproved as of this document's creation and must be resolved with Sajeesan before D02's publication step can proceed.

---

## **9. Status**

**Status:** IN-PROGRESS

**Benefit status:** COMMITTED FOR DELIVERY ON 2026-07-20

**Previous benefit status:** NOT DELIVERED ON 2026-07-17

**Reason:** The earlier work was delayed by Claude session limits and MCP bulk-data-fetch limitations. The remaining 7-day and 14-day extraction, full period validation, and database publication are carried forward into today's D02 requirement.

---

## **10. Pass/Fail Rule**

**PASS for REQ-01-D02 only when:**

1. Complete 7-day data is generated.
2. Complete 14-day data is generated.
3. Complete 30-day data is generated or refreshed.
4. All three periods are independently calculated.
5. Expected and fetched row counts reconcile.
6. Both accounts are supported.
7. All four marketplaces are supported where source data exists.
8. Warehouse mapping is correct.
9. No material join fan-out exists.
10. The final HTML is user-friendly.
11. Period switching works.
12. Account and marketplace filters work.
13. CSV download respects the selected period and active filters.
14. No yellow fields appear.
15. No credentials appear.
16. Final validation passes.
17. The validated HTML is published to the approved database table.
18. The stored database output is verified.
19. Evidence and handover files are complete.
20. The business owner can use the final output.

**FAIL if:** only sample data is produced; one or more periods are missing; period switching uses the wrong dataset; reconciliation fails; incomplete HTML is published; database publication is not verified; credentials are exposed.

**As of this document's creation: none of the above 20 conditions have been executed or verified. This document records the requirement only.**

---

## **11. Reviewers**

- Developer: Satheskanth
- Coordinator: Sathees / assigned coordinator
- Technical reviewer: Sajeesan
- Queryability reviewer: Tamil Selvan
- Business validator: Nivarnan / domain owner

---

## **12. Known Risks** *(carried forward from D01 §5 Known Limits, plus D02-specific risks)*

- Sessions, Page Views, Conversion Rate, Click-Through Rate, Buy Box % still have no confidently-complete approved source (DEC-TECH-004/005/006) — unresolved, will affect all three periods identically, not just today's new extraction.
- Category Avg Price averaging population not yet approved.
- v002 HTML file size (~41.7 MB for the 30-day dataset alone) is unresolved; adding 7-day and 14-day datasets to the same file will increase this further — network download time has not been measured and is a delivery risk for today's commitment.
- ph_task metadata (DEC-TECH-001) is unapproved — this directly blocks commitment item 8 (database publication) until resolved with Sajeesan; if not resolved today, publication cannot proceed regardless of report-generation progress.
- The same MCP bulk-fetch limitation that constrained D01 applies again to today's 7-day and 14-day extraction — keyset-paginated batching is the proven mitigation but is time-consuming; if today's session is again limited, D02 may itself remain incomplete and require a further continuation deliverable (D03).
- Requirement-ID duality (§0) remains unresolved.
- Git remains uninitialized (DEC-CTRL-001) — unchanged, non-blocking.

---

## **13. Duplicate-Truth Check**

- D01 (`2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md`) remains the historical 2026-07-17 requirement — **not modified, not archived, not overwritten** by this task.
- D02 (this document) is the active 2026-07-20 continuation requirement.
- D02 does not claim any of D01's pending work (7-day, 14-day, publication) as already complete.
- Only D02 represents today's (2026-07-20) commitment; D01 continues to represent 2026-07-17's actual (partial) outcome.
- No conflicting product code or requirement ID was introduced — same `ANPIA` / `REQ-01` parent as D01; deliverable ID advanced from `-D01` to `-D02`.

---

## **14. One Next Step**

Begin the 7-day and 14-day dataset extraction using the same proven keyset-paginated MCP batching method as D01's 30-day extraction, then route the DEC-TECH-001 ph_task metadata gap to Sajeesan in parallel so it does not block today's publication commitment once all three periods validate.
