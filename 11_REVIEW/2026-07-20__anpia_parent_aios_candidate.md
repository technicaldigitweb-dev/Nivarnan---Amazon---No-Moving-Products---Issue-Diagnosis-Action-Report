# Parent-AIOS Candidate: Reusable Report Publication and Safe Daily Automation Pattern

**Date:** 2026-07-20
**Status:** Candidate only -- **not approved parent truth, not promoted.**

## Candidate title

Reusable Self-Contained Report Publication and Safe Daily Automation Pattern

## Source subfolder

ANPIA project root (this repository)

## Problem solved

Safely generates, validates, versions, and publishes a large self-contained business report with
both a manual (on-demand) and a scheduled (future automation) execution mode -- without ever
risking a duplicate active row, a partial write, or a credential leak.

Concretely, the pattern bundles:

1. A fresh-extraction-only build discipline (never reuse a prior run's data for the next
   version).
2. A pre-write structural + duplicate-state re-verification immediately before any database
   write (not just at the start of a session).
3. An atomic, self-guarding write construction (`INSERT/UPDATE ... WHERE NOT EXISTS ...
   RETURNING ...`) that achieves duplicate-race protection and immediate reread verification
   without requiring explicit multi-call transaction control from the underlying tool.
4. A manifest-checksum-plus-confirmation-token double gate before any write executes.
5. A runtime (not source-literal) credential-leak scanner for generated report content.
6. A disabled-by-default deployment package (systemd preferred, cron fallback) that is built,
   validated, and documented, but never installed or enabled by the same task that builds it.

## Evidence path

- `05_IMPLEMENTATION/anpia_daily_pipeline.py` (full pattern implementation)
- `05_IMPLEMENTATION/publish_ph_task_production_report.py` (row-identity triple-check write gate)
- `07_EVIDENCE/validation/2026-07-20__anpia_v002_publication_evidence.md`
- `07_EVIDENCE/validation/2026-07-20__anpia_daily_task_publication_evidence.md`
- `07_EVIDENCE/validation/2026-07-20__anpia_pre_git_secret_remediation_evidence.md`
- `05_IMPLEMENTATION/deployment/README.md`

## Reuse reason

Applicable to any other daily/weekly self-contained HTML (or similarly large single-artifact)
reporting system that publishes into a shared table like `tech_team_outputs.ph_task`, especially
where: (a) the underlying tool lacks native multi-statement transaction control, (b) more than
one project/developer could plausibly write to the same table on the same day, and (c) eventual
unattended scheduling is a known future requirement but not yet approved.

## KPI or proxy KPI

- Zero calculation mismatches (this project: 0/108).
- Exactly one active daily publication per project/day (enforced by the identity-key duplicate
  check, not by convention).
- Reproducible manual execution (dry-run always safe; publish requires explicit flag +
  confirmation token).
- Scheduler-ready deployment package present but inert until explicitly activated.
- No credential exposure at any stage (source, evidence, or Git history).

## Owner / reviewer

Coordinator, technical reviewer, and queryability reviewer (see `README.md` "Reviewers").

## Duplicate-risk check

Candidate only; not checked against other existing parent-AIOS patterns as part of this task
(out of scope for a project-level closure). No claim is made that this is the only or first
instance of this pattern.

## Recommended next action

Review for reuse after VM deployment proves one successful scheduled run of the ANPIA automation
package -- promoting a pattern to parent AIOS before it has ever run unattended in production
would be premature. Do not promote this candidate into parent AIOS as part of this task.
