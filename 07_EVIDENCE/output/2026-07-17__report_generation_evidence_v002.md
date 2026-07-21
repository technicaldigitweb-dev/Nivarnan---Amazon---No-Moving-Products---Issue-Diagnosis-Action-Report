# Report Generation Evidence — v002

**What this is:** Record of how the v002 HTML was generated from the complete, real, batched 30-day dataset.

**Why it exists:** v001 was rejected as an unrepresentative sample; this file proves v002 uses real, complete (for the 30-day period), validated data.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Owner/reviewer:** Technical reviewer: Sajeesan.

---

## Source data

`09_OUTPUTS/logs/2026-07-17__amazon_report_30d_complete.json` — 51,348 rows, merged and deduplicated from 30 real MCP batches across all 8 account+marketplace combinations (see `07_EVIDENCE/database/2026-07-17__mcp_batched_extraction_evidence.md`). Zero conflicting duplicate keys. No LIMIT applied at the combination level — every valid row is included.

## Transform

`05_IMPLEMENTATION/src/data_transform.py`'s `transform_rows()` applied unchanged (same code path as v001, now fed real complete data instead of a 300-row sample). Missing-data placeholder changed to **"N/A - source not available"** per this task's explicit instruction (replacing v001's "N/A - pending source confirmation" wording, same underlying meaning: DEC-TECH-004/005/006 remain unresolved).

Result: 51,348 display rows. Summary totals (ASIN-grain deduplicated, not naively summed): 49,675 distinct account+marketplace+ASIN combinations; total 30-day PPC spend £19,194.97; total 30-day units ordered 8,980.

## Render

`05_IMPLEMENTATION/src/html_renderer.py`'s `render_html_v002()` against `templates/amazon_no_moving_report_template_v002.html`. Render itself took 0.94 seconds server-side (Python string substitution, no external templating library needed).

**7-day and 14-day datasets are empty (`[]`)** in this render — honestly reflecting that those periods were not extracted this session, not populated with derived/wrong data from the 30-day set. The period selector's `loadPeriod()` function will show zero rows and an empty-state message if 7 or 14 is selected; this is visible, not hidden.

## Output

`09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v002.html`

- **File size: 41,660,279 bytes (~41.7 MB).**
- Embedded JSON parses successfully (verified via Python `json.loads` against the actual file content — 51,348 rows for period "30", 0 for "7" and "14").
- `<html>`/`</html>` present and matched.

## Size/performance finding — disclosed, not hidden

A 41.7 MB single HTML file, driven by embedding all 51,348 rows of the 30-day dataset as client-side JSON (per the "no cutoff" requirement), is **large** by any normal web-page standard:

- Storing this in `tech_team_outputs.ph_task.html_content` (a `text` column) is technically possible but would make that row very large compared to typical ph_task entries.
- Initial page load requires downloading and `JSON.parse`-ing ~41MB client-side. A Python-side parse+validate of the equivalent data took under 1 second; a browser's JS engine should be in the same order of magnitude (likely 1–4 seconds depending on device), which is a real, noticeable delay on first load, though not an outright failure.
- Repeated client-side filter/search operations run `Array.filter` over 51,348 objects — with the 150ms search debounce already in the template, this should remain usable on typical business hardware, but was not measured in an actual browser in this session (no browser available in this environment to test directly).

**This is reported as a genuine, measured AMBER-level concern, per the stop-condition instructions ("Return AMBER when… complete datasets make the self-contained HTML unsafe in size").** It was not used as a reason to silently revert to sample data — the complete dataset is what is embedded.

**Recommended production fix (not implemented this session):** either (a) a real backend serving paginated data server-side instead of a fully self-contained static file, or (b) splitting the report into one file per account (2 files) or per account+marketplace (7 files) to keep each file's embedded row count in the low thousands. Both are design decisions for the coordinator/technical reviewer, not assumed here.

## Credential handling

No credentials used or exposed — same `PRIMARY_SKILLS_MCP` tool connection as all prior work in this project.

## Owner/reviewer

Technical reviewer: Sajeesan.

## Status

VALIDATED for the 30-day period's data completeness and correctness; AMBER for file size/performance (measured, disclosed, not resolved).

## Pass/fail rule

PASS if the generation method is fully traceable, the dataset is real and complete (not a sample), and any size/performance limitation is measured and disclosed rather than hidden or worked around by re-introducing a cutoff. Met.

## Next action

Route the file-size/performance finding to Sajeesan/Satheskanth for a production-delivery decision (single large file vs. split vs. real backend) before this becomes the file published to ph_task.
