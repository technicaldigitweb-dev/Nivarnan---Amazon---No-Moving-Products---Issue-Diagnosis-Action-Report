# Test / Development HTML Outputs -- Superseded by Production Naming Standard

**Status of this index:** Read-only classification. No files were moved, renamed, or deleted. Every
file listed below remains at its original path because one or more evidence, validation, or handover
documents already reference that exact path. Per instruction, files are **not** copied into this
folder -- this README is the proof-of-classification index itself.

**Production naming standard (introduced 2026-07-20):**
`YYYY-MM-DD_username_projectcode_vNNN.html`, produced under `09_OUTPUTS/html/production/`.

None of the files below follow that standard -- they use the earlier development naming convention
(`YYYY-MM-DD__username__amazon_no_moving_report_vNNN.html`) and are development/test iterations of
the report-building pipeline and UI, not production publications. They were never inserted into
`tech_team_outputs.ph_task`.

---

## 2026-07-17__nivarnan__amazon_no_moving_report_v001.html

- **Original path:** `09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v001.html`
- **Status:** TEST / DEVELOPMENT -- explicitly marked **FAILED SAMPLE** at creation time (pre-compaction
  session record). Do not use as a data or UX reference.
- **Prior purpose:** First end-to-end sample output, built before the direct-PostgreSQL rebuild and
  before the compact-dataset architecture existed.
- **SHA-256:** `f6c03af9044aee1f51ab63677d575c017b05bdbf8991127f8a5a94eea606056f`
- **Size:** 288,347 bytes
- **Superseded by:** the full v003-v007 rebuild lineage, and now the production pipeline.
- **Original remains in place:** YES.

## 2026-07-17__nivarnan__amazon_no_moving_report_v002.html

- **Original path:** `09_OUTPUTS/html/2026-07-17__nivarnan__amazon_no_moving_report_v002.html`
- **Status:** TEST / DEVELOPMENT -- real 30-day data, pre-compaction (three independent period
  datasets, not the later single compact-dataset architecture).
- **Prior purpose:** First UI/UX overhaul iteration (client-side CSV export, filter-aware table)
  validated in `06_VALIDATION`/`07_EVIDENCE` docs dated around 2026-07-17.
- **SHA-256:** `16082a35d5f8a81ce67e1eeef399f56534913d7fbae813b802d2fda74c56acf3`
- **Size:** 41,660,279 bytes
- **Superseded by:** v003 (direct-PostgreSQL rebuild) and the compact-dataset architecture in v005+.
- **Original remains in place:** YES.

## 2026-07-20__nivarnan__amazon_no_moving_report_v003.html

- **Original path:** `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v003.html`
- **Status:** TEST / DEVELOPMENT.
- **Prior purpose:** Rebuild using secure direct PostgreSQL access and the row-key grain
  (Account+Marketplace+ASIN+resolved SKU); embedded three independent period datasets (7/14/30-day)
  rather than one compact daily-grain dataset. Known defects at this stage: Sessions/Page Views/
  Conversion Rate/Buy Box metrics incomplete, sticky-column misalignment.
- **SHA-256:** `406f048713bef01d02d69e563c89fd0f9b349fc3d066d39681497b4e867a919f`
- **Size:** 126,852,855 bytes
- **Superseded by:** v004 (traffic dedup, N/A classification, Buy Box scale, Category Avg Price
  outlier fixes).
- **Original remains in place:** YES.

## 2026-07-20__nivarnan__amazon_no_moving_report_v004.html

- **Original path:** `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v004.html`
- **Status:** TEST / DEVELOPMENT.
- **Prior purpose:** Corrected v003's traffic-metric, calculation, and table-layout defects
  (`MAX()`-based traffic dedup, 4-tier missing-data classification, Buy Box x100 fix, Tukey-IQR
  Category Avg Price). Still used three independent period datasets (139 MB), not yet compacted.
- **SHA-256:** `250fc8560241ea7a997adc4d849746b89b190f59b800ad5f0896f4e4d8d5c3d6`
- **Size:** 139,416,832 bytes
- **Superseded by:** v005 (single compact 30-day daily-grain dataset, gzip+Base64 embedded).
- **Original remains in place:** YES.

## 2026-07-20__nivarnan__amazon_no_moving_report_v005.html

- **Original path:** `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v005.html`
- **Status:** TEST / DEVELOPMENT.
- **Prior purpose:** Introduced the compact single-dataset architecture (one 30-day daily-grain
  dataset embedded gzip+Base64, client-side period calculation via `calcProduct()`, browser-native
  `DecompressionStream`). 97.19% size reduction vs. v004. First version to enumerate the full
  ASIN/SKU bridge universe (true zero-activity rows included, not silently dropped).
- **SHA-256:** `2bbf45b5d39c5a5a519b382379dd574302def22b254a1f2c2b1887bb3c68daf3`
- **Size:** 3,915,146 bytes
- **Superseded by:** v006 (fixed long-N/A-text overflow UX defect).
- **Original remains in place:** YES.

## 2026-07-20__nivarnan__amazon_no_moving_report_v006.html

- **Original path:** `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v006.html`
- **Status:** TEST / DEVELOPMENT.
- **Prior purpose:** Fixed v005's reported UX defect (long N/A reason text overflowing table cells;
  compact N/A display with detailed reason moved to tooltip/aria-label). Known defects at this stage:
  ASIN/SKU identity-column values corrupted by the N/A-formatting code path, frozen header cells not
  actually frozen (missing structural CSS class on `<th>`).
- **SHA-256:** `f3a14c1795b1173a6fa6749d4488eb074067f489b7d93fa075c4b334ab250bb6`
- **Size:** 3,921,227 bytes
- **Superseded by:** v007 (identity-column UX correction).
- **Original remains in place:** YES.

## 2026-07-20__nivarnan__amazon_no_moving_report_v007.html

- **Original path:** `09_OUTPUTS/html/2026-07-20__nivarnan__amazon_no_moving_report_v007.html`
- **Status:** TEST / DEVELOPMENT -- **this is the most recently validated development iteration**,
  used as the UX/template baseline for the production build, but it reuses the same underlying
  dataset extraction as v005/v006 (no fresh data pull) and was never inserted into `ph_task`.
- **Prior purpose:** Fixed v006's remaining identity-column defects: all three identity columns
  (ASIN/SKU/Title) frozen, 3-line Product Title display via an inner `.title-text` div, consistent
  row height, sorting removed from identity-column headers only. Fully validated in real Chrome at
  both required viewports.
- **SHA-256:** `60b11a8a077f81db70e77012cf5dd2f45cd2f9983db3e9c61848760e126da192`
- **Size:** 3,922,103 bytes
- **Superseded by:** the first production build,
  `09_OUTPUTS/html/production/2026-07-20_nivarnan_anpia_v001.html` (or the next available production
  version for that day), which reuses this file's validated UX/template but is generated from a
  fresh live data extraction rather than v005's original pull.
- **Original remains in place:** YES.

---

## Why these files are not counted as production versions

None of the files above match the production filename standard
(`YYYY-MM-DD_username_projectcode_vNNN.html`, lowercase username/project code, three-digit version,
under `09_OUTPUTS/html/production/`). They predate that standard, use a different naming convention
entirely, and none was ever the subject of a `ph_task` publication attempt (all `ph_task` work to
date has remained at the dry-run/manifest-preparation stage -- see
`07_EVIDENCE/publication/2026-07-20__anpia_v007_ph_task_upload_manifest.json` and its handover doc).
Production version numbering therefore starts fresh at `v001` for 2026-07-20, independent of these
files' `v001`-`v007` development-cycle numbering.
