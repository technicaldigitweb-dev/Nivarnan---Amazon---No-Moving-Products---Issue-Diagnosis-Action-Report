# Handover: ph_task Publication Preparation for ANPIA v007

**Requirement:** REQ-01-D02 (cross-ref REQ-AMZ-NMP-001-D01)
**Date:** 2026-07-20
**Status:** Preparation complete. Publication **DEFERRED -- USER REVIEW REQUIRED**. Database writes
performed: **ZERO**.

## 1. What was done

1. Inspected `tech_team_outputs.ph_task` structurally and by row-convention, entirely read-only
   (session-level `SET TRANSACTION READ ONLY`).
2. Built a safe-by-default publication-preparation script,
   `05_IMPLEMENTATION/prepare_ph_task_v007_upload.py`, that validates the v007 HTML and a manifest
   of proposed values, checks for duplicates live, and prints a full non-secret dry-run report. It
   never writes unless both `--execute` and the exact `--confirm-publication-token
   PUBLISH_ANPIA_V007` are supplied -- and even then, this script version does not call `INSERT` (an
   intentional extra safety margin; see validation doc section 1).
3. Built a manifest, `07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json`,
   documenting every proposed column value with its source, confidence, and whether reviewer approval
   is needed.
4. Ran the full dry-run and all 8 required safety-gate failure tests -- all passed (failed safely,
   or in the token-only case, correctly no-op'd).
5. On final re-verification, discovered and disclosed a material finding: an existing `ph_task` row
   (id=56, `project_code='AGE'`, `developer='Narthanan'`) is topically near-identical to this report
   ("Amazon UK No-Moving Products Report", assigned to Nivarnan, `version_status='released'`).
   Corrected the manifest's `recommended_action` from `SAFE_NEW_INSERT` to `BLOCKED_AMBIGUOUS`
   accordingly.

## 2. What is NOT done (by design)

- **No row has been inserted into `ph_task`.** Publication remains deferred.
- `Sources/db_access_templates/*` were not modified (checksums re-verified unchanged).
- `daily_task` was not touched by this task.
- No credentials were printed, logged, or hardcoded anywhere in the script, manifest, or these
  documents.

## 3. Open questions for human reviewers

These must be resolved before any publication attempt:

1. **Project identity (the key blocker):** Should this v007 report be published as a *new*
   `project_code = 'ANPIA'` row, independent of the existing `AGE`-project "Amazon UK No-Moving
   Products Report" (id=56, released 2026-07-02)? Or should this work instead be recorded as a new
   version against that existing row/lineage, to avoid two parallel tracking histories for what may
   be the same underlying business report (broadened from UK-only to UK/DE/FR/IT)? Recommend
   involving both Nivarnan (business owner of both) and Narthanan (developer of the AGE-project
   version) in this decision, alongside Sajeesan (technical).
2. **`version_status` value:** No live value represents "deferred / pending review." A reviewer who
   owns the `ph_task` convention must decide whether to introduce a new value, reuse an existing one
   with a caveat recorded elsewhere, or withhold row creation until publication is actually approved.
3. **`assigned_user_team`:** Unproven for Nivarnan in the ANPIA context (left `null`). Note the
   AGE-project rows for the same user use `ph_priors` -- informative but not proof for this project.
4. **`task_id` pattern, `team` value, `version_level` starting point:** All flagged `MEDIUM`
   confidence / `reviewer_approval_needed: true` in the manifest -- see manifest for full rationale
   on each.

## 4. Files produced in this task

- `05_IMPLEMENTATION/prepare_ph_task_v007_upload.py` -- the safe-by-default script.
- `07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json` -- the corrected
  manifest.
- `07_EVIDENCE/publication/2026-07-20__ph_task_final_dry_run_output.txt` -- captured dry-run output.
- `03_DISCOVERY/2026-07-20__ph_task_schema_and_value_inspection.md`
- `06_VALIDATION/2026-07-20__ph_task_upload_script_validation.md`
- `07_EVIDENCE/validation/2026-07-20__ph_task_read_only_inspection_evidence.md`
- `07_EVIDENCE/validation/2026-07-20__ph_task_dry_run_evidence.md`
- This handover document.

## 5. Recommended next step

Route the open question in section 3.1 to Nivarnan, Narthanan, and Sajeesan before doing anything
else with `ph_task`. Do not run the script with `--execute` until that is resolved and this script is
extended to actually perform the INSERT (it currently does not, by design, in this version).
