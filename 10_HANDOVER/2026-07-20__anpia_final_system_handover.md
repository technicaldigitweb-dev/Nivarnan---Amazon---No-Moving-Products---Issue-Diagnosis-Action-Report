# Final System Handover -- ANPIA

**Date:** 2026-07-20
**System status:** `SYSTEM_COMPLETED`
**Automation status:** `AUTOMATION_BUILT_NOT_ACTIVATED`
**Closure status:** `PASS_WITH_VM_DEPLOYMENT_PENDING`

This is the single, current continuation document for this project. It supersedes
`10_HANDOVER/2026-07-20__anpia_final_project_handover.md` for continuation purposes (that
document is kept as an audit-trail record of the original delivery/closure task; nothing in it
was factually wrong, but this document is the authoritative entry point going forward).

## 1. Project identity

- Project code: `ANPIA`
- Requirement / deliverable: `REQ-01` / `D02`
- Business owner / assigned user: Nivarnan
- Developer: Satheskanth

## 2. Business problem solved

Nivarnan needed a daily view, per Amazon Account (LEDSONE, DCVoltage) + Marketplace (UK,
Germany, France, Italy) + ASIN + resolved SKU, of PPC spend, sales, and current stock, to
diagnose and act on no-moving/attention-worthy products -- previously not available as a single
reliable report.

## 3. User benefit delivered

YES. A validated, self-contained production HTML report was built, browser-verified (18/18
checks, 0 console errors, 0 network requests), calculation-reconciled (0/108 mismatches), and
published to the shared `ph_task` dashboard where Nivarnan and the wider team can view it.

## 4. Final active HTML path

`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`

## 5. Final active HTML checksum

SHA-256: `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`
(re-verified unchanged as of this handover; prior version
`09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` preserved, checksum
`4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`, not active)

## 6. Source-data connection model

Credential-based PostgreSQL connections only, via `05_IMPLEMENTATION/src/anpia_config.py`
(`get_db_config()`), reading `ANPIA_DB_*` from environment variables / a local `.env` file, no
hardcoded fallback, fails closed when incomplete. **Zero MCP dependency** in the production
pipeline (`anpia_daily_pipeline.py`) -- confirmed by direct code inspection, not assumption. See
`06_VALIDATION/2026-07-20__anpia_final_production_architecture_validation.md`.

## 7. ph_task publication model

Credential-based PostgreSQL write (same connection source as reads), via
`05_IMPLEMENTATION/publish_ph_task_production_report.py` (invoked by
`anpia_daily_pipeline.py`). `tech_team_outputs.ph_task` is the **only** production output
table. No MCP involvement in this write path.

## 8. ph_task row and publication evidence

Row `id=399` -- updated in place from v001 to v002 (`version_level` 1->2,
`version_status='released'`), `project_code=ANPIA`, `assigned_user=Nivarnan`. Exactly one
same-day ANPIA row confirmed before and after (total `ph_task` row count unchanged at 284,
confirming an UPDATE not an INSERT). Stored `html_content` checksum independently recomputed
post-commit and matched the v002 source file exactly. Evidence:
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`.

## 9. Manual "update to table" workflow

`05_IMPLEMENTATION/update_to_table.py` -- a thin, fixed-argument wrapper (no free-form text
interpretation) that resolves today's date in Asia/Colombo and invokes
`05_IMPLEMENTATION/anpia_daily_pipeline.py`, the same production pipeline used for every
publication. Default is dry-run; publishing requires `--confirm` plus the exact confirmation
token. Documented operator trigger: `08_SKILLS/anpia-update-to-table/SKILL.md` (the phrase
"update to table"). **Runs the same completed production pipeline and updates `ph_task` only** --
never `daily_task`.

## 10. Daily automation workflow

Full systemd/cron deployment package in `05_IMPLEMENTATION/deployment/`: service, timer,
install/remove/check scripts, cron fallback, README. Same credential-based connection model as
the manual path (zero MCP dependency). Locking (file + PostgreSQL advisory), no-auto-retry
(`Restart=no`), deterministic exit codes, idempotent same-day handling, and post-commit
publication verification are all already implemented in the pipeline itself, not duplicated by
the deployment scripts.

## 11. Daily schedule and timezone

12:00 PM **Asia/Colombo**, daily. `anpia-daily.timer`'s `OnCalendar=*-*-* 12:00:00 Asia/Colombo`,
`Persistent=true` (catches up a missed run), `RandomizedDelaySec=0`. The pipeline additionally
resolves "today" using a fixed `UTC+05:30` offset internally, independent of the host VM's OS
timezone setting.

## 12. Automation activation status

`AUTOMATION_BUILT_NOT_ACTIVATED`. Confirmed directly on this workstation: no crontab, no
systemd, no matching Windows Scheduled Task. No installation script has been run anywhere. Built
and ready for deployment; not activated.

## 13. VM deployment prerequisites

1. Target VM with access granted to the deployment operator.
2. A dedicated, non-root service account (placeholder in shipped files: `anpia-svc`).
3. The real deployment path on that VM (placeholder: `/opt/anpia`).
4. A protected `.env` file at the real target location (placeholder: `/etc/anpia/.env`),
   `chmod 600`, owned by the service account -- populated from `.env.example`'s variable names,
   never committed, never copied into any Markdown or evidence file.
5. The real Python interpreter path, ideally a dedicated virtualenv with `psycopg2-binary`
   installed.
6. Run `./install_anpia_timer.sh` then `./check_anpia_timer.sh` (diagnostic only), then a
   separate, deliberate `systemctl enable --now anpia-daily.timer` step -- only after technical
   and coordinator approval. See `05_IMPLEMENTATION/deployment/README.md` for full detail.

## 14. daily_task separation

`daily_task.tbl_anpia_satheskanth` is classified `SEPARATE_DAILY_WORK_RECORD_TOOL`: a developer
daily completion record, entirely outside the ANPIA production pipeline. No production
dependency, no scheduler dependency, no source-data dependency, no ph_task publication
dependency, no future automatic execution. `update_daily_task_anpia.py` is never called by
`anpia_daily_pipeline.py`, `update_to_table.py`, or any deployment file -- confirmed by direct
code inspection (`06_VALIDATION/2026-07-20__anpia_final_production_architecture_validation.md`).
It is not deleted and not included in any production flow description. Today's row: id=2
(2026-07-20, Satheskanth, ANPIA, REQ-01, D02, DEPLOY, COMPLETE), written via a direct interactive
MCP tool call in an earlier session, not by any script. Evidence:
`07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`.

## 15. GitHub repository

`https://github.com/technicaldigitweb-dev/Nivarnan---Amazon---No-Moving-Products---Issue-Diagnosis-Action-Report.git`
(branch `main`)

## 16. Latest Git commit

As of this handover's creation, the latest known remote `main` HEAD is
`b42d6d2a8509ca28f9565557a5b8b8840821d572` (see
`07_EVIDENCE/validation/2026-07-20__anpia_git_github_publication_evidence.md` for the full push
history). This verification/documentation-correction task adds one further commit on top of that
-- see the corresponding Git evidence entry for the exact hash, confirmed to match both local and
remote HEAD after push.

## 17. Validation index

`06_VALIDATION/VALIDATION_INDEX.md` (includes
`06_VALIDATION/2026-07-20__anpia_final_production_architecture_validation.md`, the code-level
proof underlying this handover's connection-model claims)

## 18. Evidence index

`07_EVIDENCE/EVIDENCE_INDEX.md`

## 19. Known limitations

- Real hosted-modal container dimensions unconfirmed -- the v002 row-density fix rests on a
  disclosed, calibrated browser simulation, not a direct measurement of the real hosted tool.
- Sessions, Page Views, Buy Box %, Conversion Rate, and CTR lack a single confidently-complete
  live source.
- `ph_task` same-day versioning convention: the documented company default (insert-new +
  reject-old) conflicts with the update-in-place approach actually used for row 399, per explicit
  repeated business/technical-owner instruction. See
  `08_SKILLS/ph_task_reference/ph_task_versioning_rules.md`.
- `daily_task.tbl_anpia_satheskanth` mapping conventions (`aios_phase` value, `deliverable_id`
  format, `developer` casing) differ from the one 2026-07-17 precedent row -- flagged for owner
  standardization, not a functional blocker (and not a production concern at all, since
  `daily_task` is outside the production pipeline).
- Credential rotation: a real database credential was found in plaintext local files during an
  earlier closure task's pre-push secret scan. It never reached Git history. Rotation is
  recommended and not yet confirmed. See
  `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`.
- Two conflicting database skill ZIPs (`Sources/skills 3 (1) (3).zip`,
  `Sources/skills_minimal_pack 2 (2).zip`) remain unresolved.
- VM access not yet available -- automation cannot be installed or activated.

None of these block today's delivered business benefit, and none required a system rebuild --
this handover corrects documentation, not implementation.

## 20. Exact next action after VM access

1. Provision the VM and grant the deployment operator access.
2. Create the dedicated service account and confirm the real deployment path.
3. Place a protected `.env` at the real target location (`chmod 600`), populated from
   `.env.example`.
4. Update `05_IMPLEMENTATION/deployment/systemd/anpia-daily.service`'s placeholders
   (`User=`, `Group=`, `WorkingDirectory=`, `EnvironmentFile=`, `ANPIA_PYTHON_BIN`) with real
   values.
5. Run `./install_anpia_timer.sh`, then `./check_anpia_timer.sh` to verify the calendar spec and
   unit syntax.
6. Obtain technical and coordinator approval, then run
   `sudo systemctl enable --now anpia-daily.timer` as a separate, deliberate step.

## 21. PASS/AMBER/FAIL status

**`PASS_WITH_VM_DEPLOYMENT_PENDING`.** The completed system is not incomplete -- it is fully
built, verified, and correctly inactive pending an external dependency (VM access) outside this
project's control. All PASS criteria for this verification task are met: implementation verified
credential-based end to end; `ph_task` confirmed as the only production write target; `daily_task`
confirmed outside the production pipeline; zero MCP production dependency; no rebuild performed;
v001/v002 checksums unchanged; automation package verified complete; scheduler confirmed
inactive; documentation conflicts found and corrected (not rewritten wholesale); this handover is
complete; the queryability test (Section 14 of the source task) passes for all 15 required
questions using only README, START-HERE, and this handover; secret scan clean; zero database
writes performed by this task.

Remaining AMBER items (not FAIL, all listed in Section 19 above): credential rotation
unconfirmed; scheduler not yet deployed (VM access pending); `ph_task`/`daily_task` governance
conventions open where already documented; two skill ZIPs unresolved.
