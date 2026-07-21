# Direct Credential Access Validation — ANPIA Rebuild (REQ-01-D02)

**What this is:** Record of secure credential transfer and live direct-PostgreSQL connection testing for the ANPIA rebuild, superseding the earlier same-day version of this file which recorded the credential source as unavailable.

**What changed since the earlier version:** the user explicitly authorized reading the real connection values from `Sources/db_access_templates/temp_user.py` (which, per a separate validation task earlier today, currently contains real hardcoded fallback credentials) and transferring them into a protected local `.env`. That authorization is the only thing that changed — the reference files themselves were not modified.

---

## Credential transfer mechanism

Values were extracted via a **static AST parse** of `temp_user.py` (`ast.parse`, never `import`, never `exec`, never running `main()`), reading only the literal default arguments to `os.getenv(NAME, "<default>")` inside the `DB_CONFIG` dict. This is a one-time local utility script (kept outside the project, in the session scratchpad — not part of the ANPIA codebase) that never printed, logged, or returned any value — only booleans confirming each field (`host`/`port`/`dbname`/`user`/`password`) was found, and a final `SUCCESS`/`INCOMPLETE` status.

**Result:** `FIELDS_PRESENT: {host: True, port: True, dbname: True, user: True, password: True}`, `ENV_WRITE_STATUS: SUCCESS`.

## .env

Created at the project root (`.env`, 7 lines: 5 credential fields + `ANPIA_DB_SSLMODE=prefer` + a comment header). **Not placed under `07_EVIDENCE`, `09_OUTPUTS`, or any shared folder.** Confirmed present via file-existence and line-count check only (`wc -l` — 7 lines) — its content was never displayed. No `.env.bak`, `.env.txt`, or other stray copy exists anywhere in the project (confirmed via recursive filename search).

**SSL mode note:** neither `temp_user.py` nor `update_table.py` specifies an explicit `sslmode` in their `DB_CONFIG` dict — `prefer` (psycopg2's own default) was used, consistent with the fully-remediated version of these files read earlier today, which also defaulted to `"prefer"`.

## .env.example

Already existed (created in a prior task today) with the six `ANPIA_DB_*` variable names and empty values — re-verified unchanged, no real value present.

## .gitignore

Updated to explicitly add `.env.*` and `!.env.example` (preserving the existing `.env`/`.env.local`/`.env.*.local` rules from the prior task) — matches the task's exact requested pattern set. No Git repository exists yet in this project (unchanged, longstanding fact) — this rule is in place ahead of any future `git init`.

## Credential-loading mechanism (production code)

`05_IMPLEMENTATION/src/anpia_config.py` — parses `.env` manually (no external dependency), populates `os.environ` only for keys not already set (real environment always wins), never prints/logs any value. `05_IMPLEMENTATION/src/anpia_db_connection.py` — `get_connection()` uses `anpia_config.get_db_config()` exclusively (no hardcoded fallback anywhere), sets the session read-only (`conn.set_session(readonly=True, autocommit=False)`), and redacts the password from any connection-error text before re-raising.

## Credential scan result (before connecting)

**CLEAN.** Full repository scan (Python, Markdown, JSON, HTML, JS, CSV, JSONL) for the literal credential values and for generic `password=<value>` patterns, excluding `.env` and the three reference files (their existing, already-documented plaintext state is a separate, known issue — not counted here): **zero matches.**

## Direct connection result

**SUCCESS.** `get_connection()` from `anpia_db_connection.py` connected successfully using the transferred `.env` values.

## Bounded validation queries (results, redacted per instruction)

| Check | Result |
|---|---|
| Connection succeeded | YES |
| Expected environment matched (`current_database()` = `order_management_copy`, the publicly-known database name used throughout this project's evidence — not a secret) | YES |
| SSL active (`current_setting('ssl')`) | **NO** — connection succeeded over a non-SSL session despite `sslmode=prefer`; either the server does not offer SSL or this is a trusted private network path. Disclosed honestly, not hidden. |
| Role verified (`current_user` = the role named in the privilege-audit PDF) | YES |
| `SELECT 1` | OK |
| PostgreSQL server version | 18 |

## Database role

Matches the role audited in `temp_user_access_report.pdf` (same role referenced by both scripts) — not reprinted here per the redaction rule.

## Effective source read privileges

Live-verified via `has_table_privilege(current_user, ...)` for all 7 candidate source tables: `public.ppc`, `public.ppc_performance`, `public.order_transaction`, `public.location_wise_inv_stock`, `public.inv_final_stock`, `public.listing_data`, `public.amz_traffic_by_asin` — **SELECT=YES, INSERT=NO, UPDATE=NO, DELETE=NO on every one.** Exactly matches the PDF's documented "public — read-only" summary, now independently confirmed live.

## ph_task privileges (inspected only — no write attempted)

`has_table_privilege(current_user, 'tech_team_outputs.ph_task', ...)` → **SELECT=YES, INSERT=YES, UPDATE=YES, DELETE=YES.** Matches the PDF exactly. **No write was performed or attempted against this table at any point.**

## Excess privilege result

**AMBER — confirmed excessive relative to strict least privilege**, consistent with the prior validation task's finding: `tech_team_outputs` grants CREATE plus full CRUD schema-wide (not scoped to `ph_task` alone). Role attributes independently confirmed clean otherwise: `rolsuper=false, rolcreatedb=false, rolcreaterole=false, rolreplication=false, rolbypassrls=false`.

## Database writes performed

**NONE.** Every query this session was read-only `SELECT` (including metadata/privilege-catalog queries). The connection itself was opened read-only (`conn.set_session(readonly=True)`).

## Final reference-file checksums (recomputed at end of this task)

All three unchanged — see `07_EVIDENCE/database/2026-07-20__common_daily_dataset_extraction_evidence.md` for the full before/after table (recorded once there to avoid duplication; identical result applies to this credential-access step, which ran inside the same overall task).

## Status

**PASS** for this credential-access and connection-validation step, with one disclosed **AMBER** finding (excess `tech_team_outputs` privilege scope, unchanged from the prior validation task, not something this task can or should remediate — grant changes were explicitly out of scope).

## Reviewer required

Sajeesan — same open item as the prior validation task: confirm whether the `tech_team_outputs` schema-wide grant should be narrowed to `ph_task` specifically.

## One next step

Proceed to the common-daily-dataset extraction (see `07_EVIDENCE/database/2026-07-20__common_daily_dataset_extraction_evidence.md`), which this connection was then used for.
