# Duplicate & Parallel-Truth Risk Review

**What this is:** The Skill 05 (Duplicate Truth Prevention) risk assessment for REQ-AMZ-NMP-001-D01, covering both the local skill-ZIP conflict and the two-database discovery.

**Why it exists:** Project control forbids creating a new source of truth without proving no existing source already covers it, and forbids silently picking between two conflicting sources.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Sources used:** `Sources/skills 3 (1) (3).zip`, `Sources/skills_minimal_pack 2 (2).zip`, primary MCP live schema/skill output, `ledsone-db` schema output.

---

## Risk 1 — Two conflicting local skill ZIPs

**Level: AMBER (partial overlap, resolved by live evidence for the files this requirement needs; unresolved for the rest).**

Ten overlapping filenames between `Sources/skills 3 (1) (3).zip` and `Sources/skills_minimal_pack 2 (2).zip` contain conflicting content (different CRC-32/size — see `07_EVIDENCE/project/2026-07-17__source_mapping_evidence.md` §6). For the three files this requirement actually depends on (`TABLE_ppc.md`, `TABLE_order_transaction.md`, `SKILL_ppc_stock_lookup.md`), this discovery cross-checked both versions against **live** primary-MCP output and found `skills_minimal_pack 2 (2).zip` consistently closer to (in most respects matching) the live schema/skill text, while `skills 3 (1) (3).zip` contains superseded content (an older 2-table PPC model missing `ppc_etl_change_log`/`ppc_etl_automation_log`; a stale bridge-table name `ebay_products` that does not exist in the live database, where the current name is `listing_data`). Full detail in `11_REVIEW/2026-07-17__database_skill_version_reconciliation.md`.

**Decision applied:** neither ZIP was merged, copied, or treated as canonical. Live MCP output (priority #2 in the authority rule) was used directly for every conclusion in this discovery — the ZIP comparison was used only as a discovery lead and cross-check, per instruction. **No new skill file or merged pack was created.**

**Remaining unresolved:** the 3 files unique to `skills 3 (1) (3).zip` (`SKILL_threshold_validator.md`, `TABLE_thresholds.md`, `TABLE_weekly_questions_answers.md`) and the 6 files unique to `skills_minimal_pack 2 (2).zip` were not touched by this requirement and remain fully unreconciled — status unchanged from `REVIEW_REQUIRED` in the source register.

## Risk 2 — Two live PostgreSQL databases with overlapping table names

**Level: RED avoided by verification, now GREEN for this requirement's scope.**

`ledsone-db` (fallback, via `.mcp.json`) and `claude_ai_postgres` (primary skills MCP) are **two distinct physical databases**. They are not duplicate truth in the traditional sense (one document contradicting another) — they are genuinely different systems, one of which (`ledsone-db`) does not contain the tables this project's own documentation (routing workbook, skill ZIPs, ph_task schema) was written against. Treating `ledsone-db`'s different `amazon_campaigns`/`order_management`/`inventory` schema as if it were the same business concept as `public.ppc`/`order_transaction`/`location_wise_inv_stock` would have been a parallel-truth error. This was caught and corrected — see `07_EVIDENCE/database/2026-07-17__database_source_selection_evidence.md` §7 for the full correction record, labelled `SUPERSEDED AS PRIMARY-SOURCE EVIDENCE — RETAINED AS POSSIBLE FALLBACK EVIDENCE`.

**No PPC/sales/stock conclusion in this discovery mixes data from both databases.** All are sourced exclusively from `claude_ai_postgres`, labelled `PRIMARY_SKILLS_MCP` throughout.

## Risk 3 — New asset creation

No new SQL file, HTML template, skill file, or PostgreSQL object was created during this discovery. All findings are recorded as markdown evidence/discovery documentation only, per Skill 08 (Evidence First) and Skill 04 (Existing Asset First) — reuse of the primary MCP's existing `ppc-stock-lookup` skill is recommended for the eventual implementation, not a new equivalent.

## Owner/reviewer

Technical reviewer: Sajeesan or assigned senior developer. Coordinator: Sathees or assigned coordinator.

## Status

VALIDATED for Risk 2 and Risk 3 (fully resolved for this requirement's scope). AMBER/open for the remainder of Risk 1 (skill-ZIP files unrelated to this requirement).

## Pass/fail rule

PASS if every duplicate-risk finding states which source was preferred and why, with evidence — not a silent choice.

## Known limitations

The 9 skill-ZIP files not touched by this requirement remain genuinely unreconciled; a future requirement touching thresholds, weekly Q&A, returns, or messaging tables would need to repeat this reconciliation exercise for those files specifically.

## Next action

Carry the `SUPERSEDED AS PRIMARY-SOURCE EVIDENCE` label and the skill-ZIP reconciliation status forward into any future requirement that touches PPC, order_transaction, or stock data in this project.
