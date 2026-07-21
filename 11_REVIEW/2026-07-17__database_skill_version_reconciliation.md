# Database Skill Version Reconciliation

**What this is:** A file-by-file comparison of the PPC/order_transaction/stock-relevant files that conflict between `Sources/skills 3 (1) (3).zip` (version A) and `Sources/skills_minimal_pack 2 (2).zip` (version B), each checked against live evidence from the primary skills-related MCP (`claude_ai_postgres`).

**Why it exists:** The two skill ZIPs are marked AMBER/unresolved in the source register and must not be selected, merged, or treated as canonical without technical review. This file provides the live-evidence basis for that review — it does not itself constitute approval.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Sources used:** `Sources/skills 3 (1) (3).zip`, `Sources/skills_minimal_pack 2 (2).zip`, `PRIMARY_SKILLS_MCP` (`get_table_definition`, `get_skill`).

---

## `TABLE_ppc.md`

| | Version A (`skills 3`) | Version B (`skills_minimal_pack`) | Live evidence (`PRIMARY_SKILLS_MCP.get_table_definition('ppc')`) |
|---|---|---|---|
| Claim | "Two tables form the core of the PPC ETL data model" (`ppc`, `ppc_performance`) | "Four tables form the PPC data model" (`ppc`, `ppc_performance`, `ppc_etl_change_log`, `ppc_etl_automation_log`) | Matches version B exactly — four tables, same descriptions, same wording |
| `ppc` columns | Missing `record_status`, other detail present in a shorter form | Full column set incl. `record_status`, `record_subtype`, `bidding_strategy` | Matches version B |
| Recommended canonical version | — | **Version B** | |
| Technical-review requirement | Yes — confirm version A is fully superseded before any deletion/archival decision | | |

## `TABLE_order_transaction.md`

| | Version A | Version B | Live evidence |
|---|---|---|---|
| `source`/`source_name` description | "Platform numeric ID" / "Platform: AMAZON / EBAY / SHOPIFY / B&Q / WAYFAIR" | "Channel / platform numeric ID" / "Channel / platform name: ..." | Matches version B wording exactly |
| `market_place` description | "Country name" | "Marketplace country where the order was placed (e.g. UK, Germany, US, France, Italy)" | Matches version B |
| `user_name` description | "User name" | "Portfolio holder (PH) name — the person responsible for managing this listing's portfolio" | Matches version B |
| `shipping_template_price` type | `text` | `double precision` | Not independently re-verified in this pass (column lives on `order_shipping_billing_detail`, not queried live this session) — **version B's type is more plausible for a price field; flag for technical confirmation** |
| ss_name exact-match rule (`=` not `LIKE`, with REPLACEMENT/RESEND suffix examples) | **Absent** | **Present**, word-for-word match to live doc | Matches version B; version A's absence is a real gap — using `LIKE` on `ss_name` per version A's silence risks the exact cross-platform collision the live rule warns about |
| Recommended canonical version | — | **Version B** | |
| Technical-review requirement | Yes | | |

## `SKILL_ppc_stock_lookup.md`

| | Version A | Version B | Live evidence (`get_skill('ppc-stock-lookup')`) |
|---|---|---|---|
| Bridge table name | **`ebay_products`** (22 occurrences; 0 occurrences of `listing_data`) | `listing_data` (14 occurrences; 0 occurrences of `ebay_products`) | Uses `listing_data` exclusively — `ebay_products` does not exist as a table name anywhere in `public.list_objects` output captured this session |
| Mode B ("Ranked & Bulk Lookups" — top-N-by-spend, zero-stock) | Not confirmed present in the excerpt reviewed | Present (2 matches) | Present, extensively — this is the exact pattern this requirement needs |
| Step 2.5 LLM-supervised clean-SKU step | Not confirmed present in the excerpt reviewed | Present (3 matches) | Present, with a documented Python reference stripper and mandatory verify-against-inventory checkpoint |
| Recommended canonical version | — | **Version B**, and note that even version B may lag the live skill slightly (line counts differ: A=511 lines, B=400 lines vs. the live skill's fuller Mode-B text) — **use the live `get_skill` output directly for implementation, treat both ZIP versions as historical reference only** |
| Technical-review requirement | Yes — version A's `ebay_products` table name is a genuine risk if anyone runs SQL from it against the live database; it should be flagged for correction or archival |

## Overall reconciliation status

For the three files this requirement touches, **`skills_minimal_pack 2 (2).zip` is consistently the version that matches live database structure and the live skill registry**; `skills 3 (1) (3).zip` contains superseded/incorrect content for these three files specifically (stale table names, missing rules, older schema). This is evidence, not a merge or deletion decision.

**Status remains `REVIEW_REQUIRED`** — a technical reviewer (Sajeesan or assigned senior developer) must approve before either ZIP's content is copied into `08_SKILLS/` or before `skills 3 (1) (3).zip`'s superseded files are archived. This discovery does not grant that approval; it only supplies the comparison evidence.

**Not reconciled in this pass:** the 3 files unique to version A (`SKILL_threshold_validator.md`, `TABLE_thresholds.md`, `TABLE_weekly_questions_answers.md`) and 6 files unique to version B — out of scope for this requirement, still fully unresolved.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer.

## Status

**REVIEW_REQUIRED.**

## Pass/fail rule

PASS (of this comparison exercise, not of the underlying conflict) if every claim in both versions is checked against live evidence and a recommendation is recorded per file, without deleting, merging, or copying either ZIP. FAIL if any file was copied or archived without reviewer sign-off.

## Known limitations

- `shipping_template_price`'s live type was not independently re-queried this session (it lives on `order_shipping_billing_detail`, not touched by this requirement's SQL needs).
- The live `get_skill` output may itself continue to evolve after this snapshot was taken (2026-07-17); this file is a point-in-time comparison, not a permanent guarantee that version B stays current.

## Next action

Route this file to Sajeesan (or assigned technical reviewer) for a formal decision on archiving/superseding `skills 3 (1) (3).zip`'s three conflicting files; do not copy any skill-ZIP content into `08_SKILLS/` until that decision is recorded.
