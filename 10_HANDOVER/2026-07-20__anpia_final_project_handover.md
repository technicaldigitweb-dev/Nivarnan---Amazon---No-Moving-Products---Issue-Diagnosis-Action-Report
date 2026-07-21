# Final Project Handover -- ANPIA

**Date:** 2026-07-20
**Closure status:** PASS WITH AUTOMATION ACTIVATION PENDING VM ACCESS

## Requirement identity

- Project code: `ANPIA`
- Requirement / deliverable: `REQ-01` / `D02`
- Business owner / assigned user: Nivarnan
- Developer: Satheskanth
- Phase: IMPLEMENTATION / PRODUCTION DELIVERY

## Project purpose

Daily Amazon report (accounts LEDSONE, DCVoltage; marketplaces UK/Germany/France/Italy) showing
PPC spend, sales, and current stock per Account + Marketplace + ASIN + resolved SKU, to support
diagnosis and action on no-moving products.

## Business benefit delivered

YES. A validated, self-contained production HTML report was built, browser-verified (18/18
checks, 0 console errors), calculation-reconciled (0/108 mismatches), published to the shared
`ph_task` dashboard, and recorded in this project's own daily work log. A reusable manual
republish command and a ready (but inactive) scheduled-automation package were also delivered.

## Final production path and checksum

- `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v002.html`
  SHA-256: `2a95437056a88bd16ffa368f8d7bbf8c6d7e9663af0cfb4376c45063ac04acc2`
- Prior version preserved unchanged:
  `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html`
  SHA-256: `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66`
- Both checksums re-verified identical immediately before this Git closure task, and again after
  all security remediation work -- confirming no business output was touched.

## ph_task row

`tech_team_outputs.ph_task` id=399 -- updated in place, `version_level` 1->2,
`version_status='released'`, `project_code=ANPIA`, `assigned_user=Nivarnan`. Exactly one
same-day ANPIA row before and after. Evidence:
`07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`.

## daily_task row

`daily_task.tbl_anpia_satheskanth` id=2 -- `work_date=2026-07-20`, `developer=Satheskanth`,
`project_code=ANPIA`, `requirement_id=REQ-01`, `deliverable_id=D02`, `aios_phase=DEPLOY`,
`status=COMPLETE`. One matching row before/after (0 -> 1). Evidence:
`07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`.

## Manual update capability

`05_IMPLEMENTATION/update_to_table.py` (see `08_SKILLS/anpia-update-to-table/SKILL.md`) drives
`05_IMPLEMENTATION/anpia_daily_pipeline.py`. Safe default: dry-run only; publishing requires an
explicit flag plus confirmation token. Not executed again during this closure task (static
inspection and existing evidence only, per this task's own instruction).

## Automation status

`AUTOMATION_BUILT_NOT_ACTIVATED`. Full systemd/cron package in `05_IMPLEMENTATION/deployment/`,
statically validated, never installed/enabled/started on any machine (confirmed directly on this
workstation: no crontab, no systemd, no matching Windows Scheduled Task). Blocked only on VM
access.

## GitHub repository

`https://github.com/technicaldigitweb-dev/Nivarnan---Amazon---No-Moving-Products---Issue-Diagnosis-Action-Report.git`

## GitHub commit (primary delivery)

`41cf146b65243bc22dd60f7410b94ed33b7d38e0` -- branch `main`, 201 files, 20,842 insertions.
Pushed successfully on the first attempt (remote repository was empty; no force push, no history
rewrite). Local and remote HEAD confirmed identical immediately after push. A small,
documentation-only follow-up commit (this handover, the indexes, README, START-HERE, and the
GitHub publication evidence itself) was added afterward -- see
`07_EVIDENCE/validation/2026-07-20__anpia_git_github_publication_evidence.md` for full detail.

## Evidence index

`07_EVIDENCE/EVIDENCE_INDEX.md`

## Validation index

`06_VALIDATION/VALIDATION_INDEX.md`

## Known limitations

- Real hosted-modal container dimensions unconfirmed -- the v002 row-density fix rests on a
  disclosed, calibrated browser simulation.
- Sessions, Page Views, Buy Box %, Conversion Rate, and CTR lack a single confidently-complete
  live source.
- VM access not yet available -- automation cannot be installed or activated.

## Unresolved governance questions

1. `ph_task` same-day versioning convention: the documented company default (insert-new +
   reject-old) conflicts with the update-in-place approach actually used for row 399, per
   explicit repeated business/technical-owner instruction to keep exactly one active row. See
   `08_SKILLS/ph_task_reference/ph_task_versioning_rules.md`.
2. `daily_task.tbl_anpia_satheskanth` mapping conventions: `aios_phase` value chosen (`DEPLOY`),
   `deliverable_id` format (`D02` vs. the one precedent row's combined `REQ-01-D01`), and
   `developer` casing (`Satheskanth` vs. precedent's lowercase `satheskanth`) all need owner
   standardization.
3. Credential rotation: a real database credential was found in plaintext local files during
   this closure task's pre-push secret scan. It never reached Git history (caught before the
   first commit), but rotation of the underlying credential is recommended and not yet confirmed.
   See `11_REVIEW/2026-07-20__anpia_credential_rotation_required.md`.
4. Two conflicting database skill ZIPs (`Sources/skills 3 (1) (3).zip`,
   `Sources/skills_minimal_pack 2 (2).zip`) remain unresolved -- neither selected as canonical.

None of these block today's delivered business benefit.

## Exact VM deployment prerequisites

1. Target VM with access granted to the deployment operator.
2. A dedicated, non-root service account (placeholder in shipped files: `anpia-svc`).
3. The real deployment path on that VM (placeholder: `/opt/anpia`).
4. A protected `.env` file at the real target location (placeholder: `/etc/anpia/.env`),
   `chmod 600`, owned by the service account, populated from `.env.example`'s variable names --
   never committed, never copied into any Markdown or evidence file.
5. The real Python interpreter path, ideally a dedicated virtualenv with `psycopg2-binary`
   installed.
6. Run `./install_anpia_timer.sh` then `./check_anpia_timer.sh` (diagnostic only), then a
   separate, deliberate `systemctl enable --now anpia-daily.timer` step -- only after technical
   and coordinator approval. See `05_IMPLEMENTATION/deployment/README.md` for full detail.

## Next safe action

Deploy to the approved VM and enable the tested systemd timer after technical and coordinator
approval, once VM access exists. In parallel, route the four unresolved governance questions
above to their respective owners.

## PASS / AMBER / FAIL closure

**PASS WITH AUTOMATION ACTIVATION PENDING VM ACCESS.** All 16 PASS criteria in this task's own
rubric are met: approved GitHub remote verified and unmodified by any unrelated overwrite; secret
scan clean (after disclosed remediation); production checksums unchanged; required implementation
files present; validation and evidence indexes complete; final handover complete; parent-AIOS
candidate documented but not promoted; approved files committed; push succeeded without force;
local and remote commit hashes match; automation remains inactive; VM access is the only
automation-deployment dependency; no database writes occurred during this closure task; working
tree is clean; another developer can continue using repository documentation alone (starting from
`00_PROJECT_CONTROL/START-HERE.md`).

Remaining AMBER items (not FAIL): credential rotation not yet confirmed; `ph_task` versioning
convention unresolved; `daily_task` mapping-convention standardization unresolved; two skill ZIPs
unresolved.
