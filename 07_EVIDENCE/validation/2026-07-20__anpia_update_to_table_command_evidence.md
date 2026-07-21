# Evidence: "update to table" Command Wrapper -- Dry-Run Execution

**Script:** `05_IMPLEMENTATION/update_to_table.py`
**Skill:** `08_SKILLS/anpia-update-to-table/SKILL.md`
**Database writes performed by this evidence:** ZERO

## 1. Execution

```
python 05_IMPLEMENTATION/update_to_table.py
```

(No flags -- default behavior is dry-run, matching the pipeline's own safe default.)

Output:

```
update_to_table -- ANPIA manual publication command
======================================================================
Resolved report date (Asia/Colombo): 2026-07-20
Mode: DRY-RUN (default -- pass --confirm --confirmation-token PUBLISH_NIVARNAN_ANPIA to publish)

Invoking: <python> anpia_daily_pipeline.py --report-date 2026-07-20 --trigger-source command --dry-run

[... full pipeline step sequence, all OK ...]
RESULT: DRY_RUN_COMPLETE
EXIT_CODE: 0
======================================================================
PIPELINE EXIT CODE: 0
```

The wrapper correctly resolved "today" as 2026-07-20 in Asia/Colombo (matching the real calendar
date at test time) and correctly invoked the central pipeline with `--trigger-source command`
(distinguishing an operator-command run from `manual` or `scheduled` runs in the structured log).

## 2. Version determination on a real production day

Since local files `2026-07-20_nivarnan_anpia_v001.html` and `v002.html` already exist (the real,
approved production deliverables from this task), `determine_version()` correctly computed the next
available local version as **v003** and correctly identified `action=UPDATE_EXISTING_ROW` against
live row id=399. This is the expected, correct behavior for a genuine next run on this date --
**not** something this task requested as a real deliverable, so the resulting test artifact
(`2026-07-20_nivarnan_anpia_v003.html`) was deleted after the dry-run completed (see Section 4 of
`07_EVIDENCE/validation/2026-07-20__anpia_automation_dry_run_evidence.md` for the equivalent
cleanup rationale). This confirms the command wrapper is fully functional and ready for a future
real "update to table" invocation, without this validation pass itself creating an unrequested v003
publication.

## 3. Fixed-argument-only behavior confirmed

`update_to_table.py`'s `argparse` definition accepts exactly two flags (`--confirm`,
`--confirmation-token`) and passes a hardcoded argument list through to the pipeline
(`--report-date <resolved date>`, `--trigger-source command`, plus `--dry-run` or
`--publish`/`--confirmation-token` depending on `--confirm`). No code path in the script parses,
evaluates, or otherwise interprets free-form text as instructions -- confirmed by code review, and
demonstrated by the fact that passing an unsupported flag (e.g. `--dry-run`, which the wrapper does
not define) fails with argparse's own `unrecognized arguments` error rather than being silently
absorbed or interpreted.

## 4. Conclusion

The "update to table" command wrapper is functional, safe-by-default, and ready for future use per
the SKILL.md operator instructions. Zero database writes occurred during this validation.
