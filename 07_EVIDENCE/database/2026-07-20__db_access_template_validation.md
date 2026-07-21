# Database Access Template Validation — ANPIA

**Purpose:** Read-only validation of the three approved database-access reference files, to determine their suitability as references for the ANPIA direct-PostgreSQL implementation.

**Scope:** `Sources/db_access_templates/temp_user.py`, `Sources/db_access_templates/update_table.py`, `Sources/db_access_templates/temp_user_access_report.pdf`. Read-only inspection only — no file was modified, no script was executed, no database or MCP connection was attempted, no `.env` was created.

**Secret-handling rule applied throughout:** no host, port, database name, username, password, token, or connection string is reproduced anywhere in this document. Only redacted presence labels are used.

---

## Files inspected

| # | Path | Size (bytes) | Last modified (UTC) |
|---|---|---|---|
| 1 | `Sources/db_access_templates/temp_user.py` | 1,921 | 2026-07-20T04:46:22Z |
| 2 | `Sources/db_access_templates/update_table.py` | 2,588 | 2026-07-20T04:45:00Z |
| 3 | `Sources/db_access_templates/temp_user_access_report.pdf` | 20,830 | 2026-07-08T10:07:12Z |

## File integrity checks

SHA-256 was computed before and after inspection for all three files. **All three matched exactly (before = after)** — this task's own read-only actions modified nothing.

**Separate, important disclosure (not a checksum failure, a cross-session finding):** both Python files' `Last modified` timestamps are from earlier **today** (2026-07-20), and their content now differs materially from what was read and evidenced in this project's own prior session earlier today (`07_EVIDENCE/database/2026-07-20__direct_credential_access_validation.md`), which found both files fully remediated — env-var-only credential loading, explicit `RuntimeError` on a missing variable, no hardcoded fallback value, and an explicit `REMEDIATION NOTE (2026-07-16)` documenting that real credentials had previously been embedded and were removed. **That remediated content, and the remediation note itself, are no longer present in the current file content.** The files currently on disk are shorter (matching the sizes above) and use a different, earlier-style pattern: `os.getenv(NAME, "<value>")` **with a real literal value as the fallback default** for host, port, database name, username, and password. This is disclosed here as a factual, time-stamped observation — see Security Risks below for the resulting finding.

---

## temp_user.py classification

- **Connection type:** DIRECT_POSTGRESQL
- **Connection mechanism:** psycopg2 (`psycopg2.connect(**DB_CONFIG)`)
- **Credential source:** MIXED (`os.getenv(NAME, <hardcoded fallback>)` — environment variable takes precedence if set, otherwise a literal value embedded in the source file is used)
- **Connection fields present:** host YES · port YES · database YES · username YES · password YES · SSL mode NO (no `sslmode` key in `DB_CONFIG`) · MCP endpoint NO

## temp_user.py operations

CREATE (`CREATE TABLE IF NOT EXISTS tech_team_outputs.sample_table`), INSERT (parameterized, `%s` placeholder, with `RETURNING`). No UPDATE, DELETE, ALTER, DROP, GRANT, or REVOKE. No explicit transaction control — `conn.autocommit = True` is set; each statement commits immediately and independently (not atomic as a pair).

## temp_user.py safety findings

Parameterized SQL: YES (the `INSERT` uses `%s`). String-formatted SQL: NO. Hardcoded secrets: **YES — see Security Risks.** Autocommit: YES. Explicit BEGIN/COMMIT: NO. Rollback handling: NO (autocommit means no rollback path exists; a failure between the two statements leaves the table created but the row uninserted, non-atomic). Exception handling: YES (`InsufficientPrivilege`, `OperationalError`, generic `Exception`, each printed). Connection close: YES (`finally: conn.close()`). Cursor close: YES, but only reached inside the try block's success path. Secret logging: exception messages are printed unredacted (`print("Could not connect:", e)` etc.) — psycopg2 does not normally embed the password in this text, but nothing in the script actively guards against it either (see Security Risks).

## update_table.py classification

Same connection type, mechanism, and credential-field presence as temp_user.py (DIRECT_POSTGRESQL / psycopg2 / MIXED credential source / host, port, database, username, password all present, SSL mode and MCP endpoint absent). **The `DB_CONFIG` structure and its fallback values appear identical to temp_user.py's** — both files show the same pattern and, on visual comparison, the same literal fallback values (not reproduced here).

## update_table.py target and operations

**Targets `tech_team_outputs.ph_task` directly** — its only executed operation is a parameterized `UPDATE ... SET html_content = %s, updated_at = now() WHERE id = %s`. Does not CREATE or ALTER the table (a `CREATE TABLE IF NOT EXISTS` and a commented-out `DROP TABLE IF EXISTS` for `tech_team_outputs.ph_task` appear only inside a trailing triple-quoted **docstring** documenting the table's DDL for reference — neither is executed code). No duplicate check before the UPDATE.

## update_table.py transaction and verification findings

Transaction: **YES** — `with conn: with conn.cursor() as cur:` provides an implicit transaction (commit on clean exit, rollback on exception) — the safer of the two scripts' patterns. Rollback on failure: YES (via the same context-manager behavior). Post-write verification: **NO** — the script checks only `cur.rowcount`; no follow-up `SELECT` confirms the stored value. Can write to unrelated tables: not as currently written (the SQL text is hardcoded to `ph_task`), but the connecting role's *granted privileges* (per the PDF) extend to INSERT/UPDATE/DELETE/CREATE on all 4 tables in `tech_team_outputs`, not just `ph_task` — so the privilege boundary, not the script's own code, is what currently prevents unrelated writes. Assumes broad privileges: **YES relative to a strict "write only to ph_task" goal** — see PDF summary below.

---

## PDF classification

**PRIVILEGE_AUDIT_ONLY.** Generated from live PostgreSQL system catalogs (`pg_database`, `pg_namespace`, `information_schema.role_table_grants`), per the document's own footer. No credential value (host/port/user/password/token) appears anywhere in the extracted text — confirmed by direct inspection of the extracted content.

## Audited privilege summary

- **Audited role:** the role literally named in the PDF, matching the `user` field used by both scripts (redacted here per the secret-handling rule — reported only as USER_PRESENT elsewhere in this document; the PDF's own role label is not a secret and is stated in the document title, but is not repeated numerically here to keep this evidence self-consistent with the redaction rule applied to the two scripts).
- **Database access:** can connect to exactly one database; three others explicitly have `CONNECT` revoked from `PUBLIC` and were never separately granted.
- **Schema access:** exactly two schemas are usable — one with `USAGE` only (no `CREATE`), one with both `USAGE` and `CREATE`. The remaining 18 schemas listed in the report (including `daily_task`, `staging_ai`, `business_intelligence`, `validation`, `raw_data`, etc.) grant **no** access at all.
- **Public-schema read privilege:** SELECT YES across all 37 tables present at report time; INSERT/UPDATE/DELETE/CREATE all NO. **Read-only, as required.**
- **tech_team_outputs privilege:** SELECT/INSERT/UPDATE/DELETE all YES across all 4 tables present at report time, plus CREATE (new tables become owned by this role). **Broader than "write access only to `ph_task`"** — it is schema-wide across all current and role-created tables in that one schema, not scoped to the single `ph_task` table.
- **CREATE privilege:** YES, but only within the one write-enabled schema — not database-wide, not on the read-only schema.
- **ALTER privilege:** not covered by this report (no ALTER column/section exists in the document) — **NOT DOCUMENTED**, not assumed either way.
- **DROP capability:** not covered by this report — **NOT DOCUMENTED**.
- **DELETE capability:** YES, scoped to the same write-enabled schema's 4 tables; NO on the read-only schema.
- **GRANT/REVOKE capability:** not covered by this report — **NOT DOCUMENTED**. The role is explicitly stated as non-superuser, which is a general constraint but not a direct statement about GRANT/REVOKE on owned objects.
- **Excessive-privilege warning:** the document itself contains no explicit excessive-privilege warning language — it is a neutral factual audit. The schema-wide (vs. table-scoped) write privilege is this validation's own assessment against the ANPIA project's stated least-privilege goal, not a warning raised by the PDF itself.
- **Report date:** not explicitly stated as a "generated on" date within the extracted text; the file's own last-modified timestamp (2026-07-08) is used above as the closest available dating evidence, disclosed as such rather than invented.
- **Content type:** privilege audit only — no credentials of any kind are present in this document.

---

## Cross-file consistency

- Both Python files use the **same connection type** (DIRECT_POSTGRESQL via psycopg2) — consistent.
- Both files' `DB_CONFIG` structures point to what appears to be the **same PostgreSQL environment and the same credential set** (identical key structure and, on comparison, identical literal fallback values) — consistent with each other, but see the integrity-check disclosure above regarding how this compares to the earlier-remediated version read in a prior session today.
- The PDF's audited role name **matches** the `user` field used by both scripts.
- `temp_user.py`, despite its name, is **not** primarily a read script — its actual code performs CREATE + INSERT (write operations) against `tech_team_outputs`, consistent with what the PDF says that schema permits.
- `update_table.py` is, as its name suggests, **specifically a `ph_task` write script** — its only operation is the `ph_task` UPDATE.
- The privilege report **supports** every operation both scripts perform (CREATE, INSERT, UPDATE all fall within the `tech_team_outputs` grants documented in the PDF); neither script attempts an operation the PDF says is unavailable to this role.

---

## Project suitability

- **temp_user.py: SUITABLE_WITH_SECURITY_FIXES.** The exception-handling and connection-close pattern is a reasonable skeleton, but the file currently contains real hardcoded fallback credential values (critical, must be removed before reuse) and lacks explicit transaction control (relies on autocommit, non-atomic across its two statements).
- **update_table.py: SUITABLE_WITH_SECURITY_FIXES.** Has the better transaction pattern of the two (`with conn:` implicit commit/rollback) — worth reusing structurally — but shares the same hardcoded-credential issue, and lacks a post-write verification `SELECT`.
- **temp_user_access_report.pdf: PARTIAL_PRIVILEGE_EVIDENCE.** Clearly documents database/schema/table-level SELECT/INSERT/UPDATE/DELETE/CREATE access for the audited role, sufficient to confirm the read-only-public / write-enabled-tech_team_outputs shape — but does not cover ALTER, DROP, or GRANT/REVOKE capability at all, so it cannot fully confirm least-privilege on those specific dimensions.

**Addressing the required decision points:** direct PostgreSQL extraction is structurally supported by both scripts' connection mechanism (psycopg2, matches this project's `05_IMPLEMENTATION/src/db_connection.py`). Read-only access to `public` is confirmed by the PDF. Write access is **not** scoped to `ph_task` alone — it is schema-wide within `tech_team_outputs`, which does not meet a strict least-privilege bar even though it is still contained to a single, intentionally write-enabled schema. Secure runtime credential loading is **not** demonstrated by the current file content (hardcoded fallback present) — this project's own `05_IMPLEMENTATION/src/db_connection.py` (env-var-only, no fallback) is the safer pattern to actually use, informed by these files' *structure* rather than their current literal content. Transaction safety is adequate in `update_table.py`, inadequate (autocommit, non-atomic) in `temp_user.py`. Post-write verification is absent from `update_table.py`.

---

## Security risks

- **PLAINTEXT_CREDENTIALS_PRESENT** — both `temp_user.py` and `update_table.py` currently contain real, live-looking connection values (host, port, database, username, password) as literal fallback defaults. Not reproduced anywhere in this document.
- **HARDCODED_CONNECTION_VALUES** — same finding, both files.
- **AUTOCOMMIT_ENABLED** — `temp_user.py` only.
- **MISSING_ROLLBACK** — `temp_user.py` (autocommit removes any rollback path across its two statements).
- **MISSING_POST_WRITE_SELECT** — `update_table.py` (relies on `rowcount` only).
- **EXCESSIVE_PRIVILEGE** — the audited role's `tech_team_outputs` grant is schema-wide (CREATE + full CRUD on all tables in that schema), broader than a strict "write only to `ph_task`" goal.
- **SECRET_LOGGING_RISK** — `temp_user.py` prints raw exception text on connection/permission failure without redaction; `update_table.py` has no exception handling around its `UPDATE` at all, so a failure would propagate as an unhandled traceback.
- **UNRELATED_TABLE_WRITE_RISK** — a consequence of the schema-wide grant: any future edit to either script (or a third script written against the same role) could write to any of `tech_team_outputs`'s other tables without requiring any new grant.
- Not found: NON_PARAMETERIZED_SQL (both scripts' data-bearing statements are parameterized).

**CLEAN_REFERENCE_PATTERN does not apply to either file as a whole**, given the hardcoded-credential finding — but `update_table.py`'s `with conn:` transaction idiom specifically is a clean, reusable pattern in isolation.

## Recommended safe usage

Use both files **only** for their structural patterns (psycopg2 usage, parameterized SQL, `with conn:` transaction idiom, exception-type differentiation) — never for their current literal `DB_CONFIG` values. This project's own `05_IMPLEMENTATION/src/db_connection.py` (rewritten 2026-07-20, env-var-only, no hardcoded fallback, redacted error text, read-only server-side cursor support) is the version that should actually be used for any live connection, not these two template files as-is.

## Prohibited usage

Do not run either script as-is. Do not copy `DB_CONFIG`'s current literal values into any other file, chat message, log, or evidence document. Do not commit either file to Git in its current state (no repository exists yet in this project, but this applies the moment one is initialized).

## Reviewer required

Sajeesan (technical reviewer) — to confirm whether the hardcoded fallback values currently in these two files were an intentional, approved reversion, or an unintended regression that should be re-remediated and, if the underlying password is real and live, rotated.

## Status

**AMBER** — per this task's own stop condition ("scripts are usable only after security remediation"). This validation task itself completed cleanly (all checks performed, all checksums matched, no file modified, no connection attempted, no secret exposed in this evidence) — the AMBER reflects the *state of the files being validated*, not a failure of this validation task.

## Pass/fail rule

This task's own PASS conditions (all three files inspected; no file modified; checksums match before/after; connection type classified; credential pattern classified; SQL operations identified; PDF privileges summarized; cross-file consistency checked; suitability decided; evidence fully redacted; no DB/MCP connection attempted; no credential exposed) are **all met** — the overall **AMBER** status reflects the explicit stop-condition override ("scripts are usable only after security remediation"), which takes precedence over a plain PASS per this task's own rules.

## One next step

Escalate the hardcoded-credential finding to Sajeesan immediately (separately from routine task follow-up) to determine whether the exposed value is a live, real credential requiring rotation — do not wait for the next scheduled ANPIA work session.
