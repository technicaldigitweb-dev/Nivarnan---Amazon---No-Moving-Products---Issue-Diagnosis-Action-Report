# Evidence: ANPIA Production v001 -- ph_task Publication (Executed)

**Requirement:** REQ-01-D02 -- ANPIA
**Date:** 2026-07-20
**Status:** PUBLISHED. This is the one write action in this project's ph_task work, executed only
after explicit, itemized user approval of every column value.

## 1. Authorization

The user approved all proposed `ph_task` publication values by name (task_name, task_id, team,
developer, phase_level, assigned_user_team, version_level, version_status) and explicitly instructed
execution of the already-prepared guarded script with the exact command shown below. Before running
it, the manifest (`07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json`) was
updated in place to replace every previously LOW/MEDIUM/NONE-confidence value with the user-approved
value, and every field was marked `confidence: HIGH, reviewer_approval_needed: false`.

Note on `version_level`: the user wrote `version_level = v001` in the approval instruction. This was
interpreted as the integer `1` (the production filename's version tag), since `version_level` is an
integer column -- not as a literal string `"v001"`. This interpretation is disclosed here rather than
applied silently.

## 2. Pre-execution checks (all performed fresh, immediately before the write)

- Manifest SHA-256 computed live: `99d2200af974a12ad29b989d28b7a074510a5757218dc32dd22c17515456ec32`.
- HTML checksum re-verified: `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` (matches manifest and the
  expected value given in the approval instruction).
- HTML byte size re-verified: 3,922,120 bytes (matches).
- Live `ph_task` schema re-verified: 18/18 expected columns present.
- ANPIA-only duplicate check (AGE never queried): 0 existing rows for `project_code='ANPIA' AND
  assigned_user='Nivarnan'` -> live-derived action `SAFE_NEW_INSERT`, matching `--expected-action`.

## 3. Execution

```
python 05_IMPLEMENTATION/publish_ph_task_production_report.py \
  --manifest "07_EVIDENCE/publication/2026-07-20_nivarnan_anpia_v001_ph_task_manifest.json" \
  --execute \
  --confirmation-token "PUBLISH_NIVARNAN_ANPIA" \
  --approved-manifest-sha256 "99d2200af974a12ad29b989d28b7a074510a5757218dc32dd22c17515456ec32" \
  --expected-action "SAFE_NEW_INSERT"
```

Result: exit code **0**. `INSERT ... RETURNING id` reported exactly 1 affected row. The script
rereads the inserted row's identity fields inside the same uncommitted transaction before
committing; that check passed and the transaction was committed.

**`WRITE COMMITTED: id=399, project_code=ANPIA, assigned_user=Nivarnan`**

## 4. Independent post-commit verification (separate read-only connection, run after the script exited)

| Field | Verified value |
|---|---|
| id | 399 |
| project_name | No Moving Amazon - No-Moving Products - Issue Diagnosis & Action Report |
| project_code | ANPIA |
| task_name | Amazon No-Moving Products Report — 7/14/30 Day Analysis (confirmed byte-correct: em-dash is U+2014) |
| task_id | NULL |
| team | Technical |
| developer | Satheskanth |
| assigned_user | Nivarnan |
| assigned_user_team | ph_priors |
| phase_level | 1 |
| version_level | 1 |
| version_status | released |
| action_took_by | NULL (correct -- populated only when the end user acts) |
| action_took_date_time | NULL (correct) |
| created_at / updated_at | 2026-07-20T15:44:19.538101+05:30 |
| stored html_content byte length | 3,922,120 (exact match to source file) |
| stored html_content SHA-256 (recomputed independently from the stored bytes) | `4af3de8c5571073dc31de521d0d5844b91530b19c68a75ea8f27bf744d245d66` (exact match) |
| Same-day ANPIA row count after commit (`project_code='ANPIA' AND assigned_user='Nivarnan'`) | **1** |
| Total `ph_task` row count | 283 -> **284** (+1, consistent with exactly one insert) |

## 5. Scope discipline confirmed

- `project_code = 'AGE'` was not queried at any point in this execution.
- `daily_task` was not touched -- the publish script has no code path that references it.
- No credentials were printed at any point (script output contains only role/database/SSL metadata,
  never the password or DSN).
- Full HTML content was never printed -- only size and checksum.

## 6. Conclusion

The ANPIA production v001 report is now published to `tech_team_outputs.ph_task` as row id=399,
with every field verified byte-for-byte against the approved manifest and the source HTML file via
an independent post-commit reread.
