# Requirement Template Migration Evidence

**What this is:** Record of restructuring the project's requirement document into the approved `Daily Requirement Document` template.

**Why it exists:** Per project control, a structural migration must prove business meaning was preserved, no duplicate active requirement remains, and any naming conflict was resolved with evidence, not invention.

**Business question supported:** REQ-01-D01 / cross-referenced `REQ-AMZ-NMP-001-D01` (see the new requirement's §0 for why both identifiers exist).

**Owner/reviewer:** Coordinator: Sathees or assigned coordinator. Technical reviewer: Sajeesan.

---

## Template file used

`01_REQUIREMENTS/requirement_template/Daily Requirement Document.md` — a genuine, pre-existing file (dated 2026-07-06, predating this project's discovery/design/implementation work) inspected in full before writing the new document. Its structure: Metadata Block (table) → Today Requirement Block (Task Name / Business Purpose / Source Information / Filter Conditions / Required Data Output) → Business Logic Block → Data Enrichment Block. It is an illustrative example (worked example: "Get UK Sales Data" for a different project, "UK to DE Transfer", code `INV-UTDT`), not an exhaustive rigid schema — it does not itself define fields for governance/validation/publication content, so a fifth "Governance & Status Block" was added to the new document to hold the additional fields this task's instructions explicitly required (in-scope/out-of-scope work, UI/CSV requirements, data completeness, validation, evidence, security, database-write restriction, ph_task gate, scheduler status, owners, known limits, dependencies, pass/fail rule, status, next step).

## Original requirement path

`01_REQUIREMENTS/2026-07-17__amazon_high_spend_asin_uk_stock_requirement.md` (pre-migration).

## New requirement path

`01_REQUIREMENTS/2026-07-17_satheskanth_REQ-ANPIA_REQ-01-D01.md`.

## Archived/superseded path

`12_ARCHIVE/requirements/2026-07-17__amazon_high_spend_asin_uk_stock_requirement__SUPERSEDED.md` — moved (not deleted), with an explicit superseded notice prepended before the move, pointing to the new active file.

## Product code selected

**ANPIA**, per explicit task instruction.

## Naming-rule result

The template was inspected for any authoritative reference to "NPIA" (the name the user reportedly typed previously) before deciding whether to stop and report a conflict. **No reference to NPIA or ANPIA exists anywhere in the template** — its only example project code is `INV-UTDT`, for an unrelated example project. Because the template does not require or reference NPIA, **no conflict exists to report**, and ANPIA (the explicitly-defined product code) was used directly, per the task's own instruction for this exact scenario ("Use ANPIA... unless an existing authoritative naming file... proves that NPIA is the approved code").

## Sections migrated

All content from the original document's 18 numbered sections was preserved and mapped into the new template's blocks (see the new document's §0–§5 for the full mapping) — including the superseded original written requirement (§2 in the old file), the corrected written requirement (§2A), included/excluded scope, existing assets, duplicate/parallel-truth risk, required evidence, open questions (with their resolved/still-open status preserved exactly), safety rules, reviews, and status. Nothing was dropped; the 18-section numbering was replaced by the template's block structure, with a clear mapping preserved via inline cross-references.

**Content beyond the original requirement doc** was also incorporated, reflecting real project progress since 2026-07-17's initial draft: the multi-account/marketplace discovery addendum, the full design documents, the complete 30-day data extraction (51,348 real rows, zero cutoff), the v001 rejection and v002 rebuild, real validation results (Node.js/V8-executed filter/CSV/performance tests), and the current AMBER status. This is not new business meaning — it is the same requirement's actual current state, now reflected in the templated document instead of being scattered only across `03_DISCOVERY/`, `04_DESIGN/`, `06_VALIDATION/`, and `07_EVIDENCE/`.

## Missing template fields

None — every field the template's Metadata Block defines was populated (using "Not yet measured/defined" or "Not formally phase-numbered" honestly where the project genuinely has no value yet, rather than inventing one).

## Assumptions

- `expected_deadline_date` was set to 2026-07-17 based on this requirement's own history (an original same-day delivery expectation recorded in this project's earlier session); the deadline was not met for the full scope, and this is stated plainly in the new document, not hidden.
- `phase` has no formal number in this project's history (unlike the template's worked example, which uses "Phase-01"); rather than invent a phase number, the current build stage is described in prose.

## Business meaning changed

**NO.** Every approved account (LEDSONE, DCVoltage), marketplace (UK, Germany, France, Italy), period (7/14/30 days), warehouse mapping (UK→UK, Germany/France/Italy→German), row-grain rule, blue/yellow column rule, and safety restriction from the original document is preserved verbatim in meaning in the new document. No scope was added, removed, or reinterpreted.

## Duplicate active requirements

**0.** Exactly one requirement file now exists in `01_REQUIREMENTS/` (excluding the template subfolder): the new templated document. The original is archived, not duplicated in an active location.

## Requirement-ID duality (disclosed, not resolved)

The new document uses `REQ-01` / `REQ-01-D01` / product code `ANPIA` per this task's explicit instruction. Every other artifact this requirement has produced — `03_DISCOVERY/`, `04_DESIGN/`, `05_IMPLEMENTATION/`, `06_VALIDATION/`, `07_EVIDENCE/database/`, `07_EVIDENCE/output/`, `07_EVIDENCE/validation/`, `10_HANDOVER/` (dozens of files) — uses `REQ-AMZ-NMP-001-D01`. This task's allowed scope (`01_REQUIREMENTS/`, `07_EVIDENCE/project/`, `12_ARCHIVE/` only) does not permit renaming or updating any of those files. **This is recorded as a genuine, unresolved cross-reference gap, not silently picked in either direction** — see the new requirement document's §0 for the full explanation, and §"Follow-up candidates" below.

## Follow-up candidates (out of scope to edit here)

- **Project root `README.md`** references the old requirement path 3 times (lines 7, 17, 65) and the `REQ-AMZ-NMP-001-D01` identifier twice — outside this task's allowed scope (`01_REQUIREMENTS/`, `07_EVIDENCE/project/`, `12_ARCHIVE/` only). Reported here as a follow-up candidate, not edited.
- A future task with broader scope should decide whether to (a) rename all `REQ-AMZ-NMP-001-D01` references to align with `REQ-01-D01`/`REQ-ANPIA`, (b) rename this new document's ID to match `REQ-AMZ-NMP-001-D01` instead, or (c) formally adopt both as a documented equivalence — not decided here, since it requires editing files outside this task's scope.

## Reviewer required

Coordinator (Sathees) to confirm the ANPIA product code and the REQ-01/REQ-AMZ-NMP-001-D01 duality resolution path; Sajeesan for the ph_task metadata gap (unchanged from before this migration).

## Next action

Route the requirement-ID duality (§0 of the new document) to the coordinator for a decision; route `README.md`'s stale path references as a follow-up candidate for a future in-scope task.

## Status

**PASS** (of this migration task).

## Pass/fail rule

PASS if: the template was inspected before writing (not assumed); the naming rule was checked and resolved with evidence (not invented); the product code is consistently ANPIA; the new file matches the exact instructed filename; all mandatory template/task-required sections are populated; no approved business meaning was changed; the original is archived with a superseded notice, not deleted or left duplicated as active; only one active requirement document remains; this evidence file exists; and no file outside `01_REQUIREMENTS/`, `07_EVIDENCE/project/`, `12_ARCHIVE/` was modified. **All conditions met.**
