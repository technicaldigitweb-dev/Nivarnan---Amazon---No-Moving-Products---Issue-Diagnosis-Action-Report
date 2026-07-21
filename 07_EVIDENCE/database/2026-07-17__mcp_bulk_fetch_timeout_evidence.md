# MCP Bulk Fetch Timeout Evidence

**What this is:** Record of the primary MCP connection timing out on a bulk multi-account/marketplace period-dataset query, and the resulting connection-path decision.

**Why it exists:** Per project control, a failure must be recorded with cause and decision, not silently retried or hidden.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Owner: Satheskanth. Technical reviewer: Sajeesan.

---

- **requirement_id:** REQ-AMZ-NMP-001-D01
- **Attempted task:** full multi-account (LEDSONE, DCVoltage), multi-marketplace (UK, Germany, France, Italy) 7-day-period dataset retrieval, via the same aggregation-and-join query already proven correct for the 30-day/300-row sample (`05_IMPLEMENTATION/sql/main_report.sql`).
- **Connection used:** `PRIMARY_SKILLS_MCP` (`mcp__claude_ai_postgres__execute_sql`).
- **Result:** **TIMEOUT.** The tool call was moved to a background task after 120s, then failed after a further 300s with no response: *"MCP server 'claude.ai postgres' tool 'execute_sql' sent no response or progress for 300s; aborting."*
- **Likely cause:** query size and transfer volume exceed practical MCP bulk-fetch limits for this connection/tool — consistent with the already-documented finding that a single 30-day/300-row result (~169,000 characters) was already near the tool's per-call response-size ceiling (see `07_EVIDENCE/output/2026-07-17__report_generation_evidence.md`). A 7-day window scoped to "no cutoff, all combinations" still touches the full ~49,700+ ASIN bridge before any period-specific filtering reduces it, so the underlying join/aggregation work is comparable in size to the 30-day case regardless of the shorter date window — this is a transport/practical-limit issue, not evidence the SQL logic itself is wrong.
- **Database writes:** NONE.
- **Schema changes:** NONE.
- **Credentials exposed:** NO.
- **Decision:** MCP is retained for bounded checks only (discovery, schema inspection, bounded samples, query-plan debugging, row-count checks, validation spot checks) going forward for this requirement. Bulk/full-dataset extraction requires a different connection path.
- **Selected replacement:** secure credential-based direct PostgreSQL extraction (`05_IMPLEMENTATION/src/db_connection.py`, already built).
- **Owner:** Satheskanth.
- **Technical reviewer:** Sajeesan.
- **Status:** APPROVED CONNECTION-PATH CHANGE (MCP → credential-based for bulk extraction).
- **Next action:** attempt credential-based extraction — see `07_EVIDENCE/database/2026-07-17__credential_environment_check.md` for the result of that attempt.

## Pass/fail rule

PASS if the timeout is recorded with its exact cause classification (transport/practical-limit, not a SQL-logic defect) and a replacement connection path is decided without retrying the same heavy query. Met.

## Known limitations

The precise practical size ceiling for this MCP connection's bulk transfer was not formally measured (e.g. via a binary search on `LIMIT`) — only observed as "300 rows succeeds, an uncapped ~13,000+ PPC-spend-bearing-ASIN query times out." Sufficient to justify the connection-path decision; not a precise threshold.
