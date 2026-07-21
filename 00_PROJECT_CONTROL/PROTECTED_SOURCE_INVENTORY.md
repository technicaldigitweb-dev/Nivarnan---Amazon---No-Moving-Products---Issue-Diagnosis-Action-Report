# Protected Source Reference Inventory

**Date:** 2026-07-20
**Purpose:** Enumerate paths treated as protected, read-only reference-only assets --
excluded from Git, never modified, never executed, never imported by production code.
No secret value appears anywhere in this document.

## Protected files

| Relative path | Purpose | Classification | Execution allowed | Git inclusion | SHA-256 (before) | SHA-256 (after) |
|---|---|---|---|---|---|---|
| `Sources/db_access_templates/temp_user.py` | Reference example of a direct `temp_user` PostgreSQL connection script | REFERENCE_ONLY | NO | NO | `6dd2825c266ff94b35ee0cf3372b8a62480736e5f76c0e1df4a2a51dc52a1049` | `6dd2825c266ff94b35ee0cf3372b8a62480736e5f76c0e1df4a2a51dc52a1049` |
| `Sources/db_access_templates/update_table.py` | Reference example of a direct `ph_task.html_content` update script | REFERENCE_ONLY | NO | NO | `9784d14ab8e0646e454a8effe9e049dfdd10a8fb32fe4fd63cfa29a1120ff5bc` | `9784d14ab8e0646e454a8effe9e049dfdd10a8fb32fe4fd63cfa29a1120ff5bc` |
| `Sources/db_access_templates/temp_user_access_report.pdf` | Reference document describing `temp_user` access | REFERENCE_ONLY | NO | NO | `b0c2641ae879e33e898df8b7d109d5a630510031aafd62b3de274babe175a5cd` | `b0c2641ae879e33e898df8b7d109d5a630510031aafd62b3de274babe175a5cd` |

## Reason for exclusion

`temp_user.py` and `update_table.py` were found, via a full-repository secret scan performed
during ANPIA final closure (2026-07-20), to contain a real, live PostgreSQL host and password
as plaintext `os.getenv(..., "<default>")` fallback values. `temp_user_access_report.pdf` is
treated as protected by association (same folder, same subject matter) without its content
being extracted or reproduced anywhere in this project's evidence.

These files are **not modified, not executed, and not imported** by any implementation module
in this project. `05_IMPLEMENTATION/src/db_connection.py`, `anpia_config.py`, and
`anpia_db_connection.py` implement the actual production connection pattern independently,
reading exclusively from environment variables (see
`11_REVIEW/2026-07-20__anpia_credential_rotation_required.md` for the full remediation record).

## Checksum integrity proof

Both checksums were computed with `sha256sum` immediately before remediation work began and
re-verified immediately after all remediation work completed. Before/after values are
identical for all three files (see table above) -- confirming these protected files were never
touched during this task.

## No other protected source paths found

`02_SOURCE/db_access_templates/` does not exist in this project (checked, absent). No other
credential-template, reference-database-script, or connection-example file was found outside
`Sources/db_access_templates/` during the full-repository scan documented in
`07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`.
