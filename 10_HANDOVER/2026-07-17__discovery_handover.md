# Discovery Handover — REQ-AMZ-NMP-001-D01

**What this is:** The closure/handover note for the read-only discovery stage, so another person (or a clean LLM) can continue this project tomorrow without verbal explanation.

**Why it exists:** Project control requires every workday to end with a closure note stating requirement ID, asset path, evidence path, queryability result, blockers, next step, and pass/fail — per `0.1 LLM PROJECT INSTRUCTION.md.docx` §11.

**Business question supported:** Which Amazon UK ASINs are consuming the most PPC spend, and do their recent sales and current UK stock levels justify attention or action?

**Sources used:** All discovery and evidence files listed below.

---

## Daily closure fields

| Field | Value |
|---|---|
| Requirement ID | REQ-AMZ-NMP-001-D01 |
| Asset path | `03_DISCOVERY/2026-07-17__amazon_high_spend_asin_uk_stock_discovery.md` |
| Evidence path | `07_EVIDENCE/database/` (4 files) + `07_EVIDENCE/project/` (2 files) + `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md` |
| GitHub path/commit | N/A — Git not initialized for this project (open question #7) |
| Queryability result | YES — every file created today answers what/why/source/evidence/status/next-step on its own; see Queryability Test below |
| Blockers | 10 open business/technical decisions listed in the discovery file §12 — none are technical blockers to further *discovery*, all block *implementation* |
| Next step | Route open questions to Nivarnan / Sajeesan / coordinator (see below) |
| PASS/FAIL | **PASS** (of the discovery stage) — AMBER overall decision (see discovery file) |

## What was done today

1. Verified no reusable SQL/HTML/ph_task asset already exists in this project — the closest reusable capability is the primary database's own `ppc-stock-lookup` skill.
2. Reviewed and recorded applicable project-control rules from the AIOS skill pack.
3. Reviewed the Nivarnan requirement workbook — confirmed it does **not** contain a PPC-spend report or threshold; this requirement is new, not a rebuild of an existing sheet.
4. Documented `tech_team_outputs.ph_task` publication rules (append-only versioning, `assigned_user_team` routing, `rejected` status semantics) — no write performed.
5. Confirmed, via independent internal evidence (not just assertion), that `mcp__claude_ai_postgres__*` is the correct primary skills-related database for this project, and that the project's `.mcp.json`-configured `ledsone-db` is a different, legitimate, but non-matching operational database — corrected the interpretation of earlier (pre-priority-order) findings rather than discarding them.
6. Verified `public.table_routing_map` gives FULL coverage for PPC, Sales, and Stock domains.
7. Verified live table structure, Amazon UK filters, PPC/sales grain, date coverage, stock freshness, ASIN/SKU cardinality, and empirically demonstrated join-multiplication risk — all via bounded, read-only queries.
8. Determined the latest complete common 30-day window: **2026-06-16 to 2026-07-15**.
9. Cross-checked the two conflicting skill ZIPs' PPC/order_transaction/stock-relevant files against live evidence — found `skills_minimal_pack 2 (2).zip` consistently current, `skills 3 (1) (3).zip` superseded (including a stale table name, `ebay_products`, replaced live by `listing_data`) — recorded as evidence only, not acted on.
10. Listed 10 open questions without guessing answers.

## Who should review what

| Reviewer | What to review |
|---|---|
| Nivarnan (business validator) | "High spend" definition, zero-sales-ASIN treatment, sales-metric choice (revenue/units/orders), one-ASIN-multi-SKU display rule, stock-freshness threshold |
| Sajeesan (technical reviewer) | Skill-ZIP reconciliation sign-off (`11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`), ph_task field values, the `order_status` "Canceled"/"Cancelled" data-quality note |
| Coordinator (Sathees or assigned) | Git initialization decision, numeric KPI target |
| Tamil Selvan (queryability reviewer) | This handover file and the discovery file, for queryability sign-off |

## Queryability test

Using only `03_DISCOVERY/2026-07-17__amazon_high_spend_asin_uk_stock_discovery.md` and its linked evidence files, a clean LLM can determine: what was requested (§ business question), which sources were used (§5–§7, every table source-labelled), which tables/joins were verified (§7, §10), which reporting period was used (§8), what the output will contain (workbook §3 + requirement §2), what evidence proves it (every `07_EVIDENCE/` file linked), what remains unresolved (§12), who reviews it (owner/reviewer fields throughout), and whether it is safe to publish/reuse (no — `database_write_permission`/`production_change_permission` remain NOT APPROVED, and 10 business decisions are open). **Queryability test: PASS.**

## Status

DISCOVERY COMPLETE — AMBER. Awaiting business/technical decisions before design or implementation.

## Pass/fail rule

PASS if this handover lets tomorrow's session (or a different person) resume without asking the creator anything — verified above via the queryability test.

## Known limitations

Same as recorded in the discovery file §12; not repeated here to avoid duplicate truth — see that file directly.

## Next action

Do not proceed into SQL/HTML/automation/ph_task implementation, or into any further PostgreSQL discovery, until the open questions in §12 of the discovery file are answered by the named reviewers.

---

## Addendum — 2026-07-17 — Decision gate

- **Discovery:** technically complete.
- **Current result:** AMBER.
- **Open decisions:** ten (see `04_DESIGN/2026-07-17__amazon_high_spend_asin_decision_register.md` §3 — DEC-BUS-001 through DEC-BUS-005, DEC-TECH-001 through DEC-TECH-003, DEC-CTRL-001, DEC-CTRL-002 — all status OPEN).
- **Design:** not started — design gate closed pending DEC-BUS-001–005, DEC-TECH-001, DEC-CTRL-002.
- **Implementation:** not started — implementation gate closed (depends on design gate).
- **Database writes:** NONE.
- **One next step:** obtain decisions — route the decision register to Nivarnan, Sajeesan, and the coordinator.

---

## Addendum — 2026-07-17 (later same day) — Scope correction and build in progress

- **Scope corrected:** two authoritative user-provided images (`02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png`, `02_SOURCE/evidence/2026-07-17__nivarnan_additional_report_instructions.png`) confirmed the requirement is multi-account (LEDSONE, DCVoltage) / multi-marketplace (UK, Germany, France, Italy) / multi-period (7/14/30 days) / all-combinations (no spend cutoff) — **superseding** the original UK-only, high-spend-filtered scope. Original wording preserved and marked SUPERSEDED in `01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md`, not deleted.
- **New discovery:** `03_DISCOVERY/2026-07-17__multi_account_marketplace_discovery_addendum.md` — AMBER. Account/marketplace/warehouse mapping fully verified; 8 of 15 blue columns fully source-verified; 2 have a documented interim default; 5 remain REVIEW_REQUIRED (Sessions, Page Views, Buy Box %, Conversion Rate, CTR) pending a technical decision on the traffic-data source.
- **Decisions:** 7 of the original 10 decisions now RESOLVED/APPROVED by written instruction (DEC-BUS-001–004, 006–011 in the updated decision register). 3 new decisions added (DEC-TECH-004/005/006) for the 5 REVIEW_REQUIRED columns. DEC-TECH-001 (ph_task metadata) remains OPEN and **blocks ph_task publication**.
- **Build status:** proceeding to design/implementation/validation for the HTML report using verified fields; ph_task publication will **not** be attempted until DEC-TECH-001 is resolved.
- **Database writes:** NONE so far; none will occur without DEC-TECH-001 approval.
- **One next step:** continue to `10_HANDOVER/2026-07-17__amazon_report_build_and_publication_handover.md` for the outcome of the build/validation/publication-gate attempt.
