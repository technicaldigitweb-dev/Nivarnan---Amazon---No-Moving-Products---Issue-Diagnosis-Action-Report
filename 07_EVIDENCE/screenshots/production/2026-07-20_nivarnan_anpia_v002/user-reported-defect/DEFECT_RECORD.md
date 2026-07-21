# User-Reported Defect Record -- v001 Hosted Table Too Short

**Disclosure:** The task instruction referred to "the supplied screenshot" and asked that it be saved
as `01_v001_hosted_table_too_short.png`. **No image was actually attached to that message** -- only
text. Consistent with this project's standing discipline of never fabricating evidence, no image file
has been created at that path. If a screenshot exists, please attach it in a follow-up message and it
will be saved here immediately; until then, this record documents the defect from the text
description alone, and the v002 fix and its validation rely on real, freshly-captured browser
screenshots (see `07_EVIDENCE/screenshots/production/2026-07-20_nivarnan_anpia_v002/validated/`)
rather than on the unavailable "before" image.

## Reported defect (from the task instruction, verbatim intent)

- The hosted report (v001, as rendered inside the hosted tool's task modal) shows only approximately
  **5 rows** of the data table at once.
- There is excessive surrounding whitespace/height allocation (toolbar, summary cards, banners, etc.)
  that limits how much vertical space is actually left for the table itself.
- The user requires approximately **15 rows** visible in one hosted view without needing to scroll
  the outer page.
- Horizontal and vertical scrolling within the table itself must remain available (this is not a
  request to remove scrolling -- it's a request to make better use of the available vertical space
  before scrolling is needed).

## Root cause (confirmed by inspecting the v007/v001 template CSS)

The `.table-wrap` element's height was not constrained to the viewport at all in v001 (inherited
unchanged from v007) -- the table grew to its natural content height and the *browser/hosted-modal
viewport* was the only thing limiting visible rows, with no deliberate calculation to maximize row
count within that space. Combined with generous card/toolbar padding above the table, this left far
less vertical room for table rows than the available viewport actually allowed.

## Fix approach for v002

A `clamp()`-based `.table-wrap` height, sized from real-browser measurement of row height and a
constrained hosted-modal-style viewport, plus tightened toolbar/summary spacing -- see
`06_VALIDATION/2026-07-20__anpia_v002_ui_validation.md` for the exact values used and the real-browser
row-count measurements that justified them.
