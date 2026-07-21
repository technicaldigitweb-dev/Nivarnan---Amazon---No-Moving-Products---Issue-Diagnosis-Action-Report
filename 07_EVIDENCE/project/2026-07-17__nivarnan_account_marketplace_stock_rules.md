# Nivarnan Account/Marketplace/Stock Rules — Evidence

**What this is:** Verified record of what the user-provided "Additional Report Instructions" image proves about accounts, marketplaces, periods, filters, and the marketplace-to-warehouse stock mapping.

**Why it exists:** These are business rules with direct implementation impact (row scope, filter set, and which physical stock pool is joined per marketplace) and must not be invented or silently reinterpreted.

**Business question supported:** REQ-AMZ-NMP-001-D01.

**Source-image path:** `02_SOURCE/evidence/2026-07-17__nivarnan_additional_report_instructions.png` (also visible, cropped, within `02_SOURCE/evidence/2026-07-17__nivarnan_report_column_reference.png`, rows 16–21 — the two images corroborate each other).

**Path discrepancy note:** same as recorded in `2026-07-17__nivarnan_blue_yellow_column_scope.md` — found at `02_SOURCE/evidence/`, not the originally-specified `02_SOURCE/requirements/evidence/`; not duplicated.

**Confirmed via:** direct visual inspection of both images.

---

## What the image proves

A dedicated "Additional Instructions" panel with 5 confirmed instruction blocks:

1. **"Report should get generated daily with 7/14/30 Days filter."**
2. **"For Amazon both account (LEDSone, DCVoltage) and UK, German, France, Italy marketplaces"**
3. **"Only get blue colour filled datas only." vs. "Not this"** (reinforces the column-scope rule in the companion evidence file).
4. **"(Units in Stock) UK market place - UK warehouse stock level / German, France, Italy market place - German warehouse stock level"**
5. **"Account wise, Market place wise filters should be there."**

## Confirmed requirements

- **Accounts:** exactly two — LEDSONE and DCVoltage (spelled "LEDSone" and "DCVoltage" in the image; case will be normalized against actual stored database values during discovery, not assumed from image capitalization).
- **Marketplaces:** exactly four — UK, Germany ("German" in the image), France, Italy.
- **Periods:** daily generation, with a 7/14/30-day filter — confirms three period options must be supported, consistent with the task instruction.
- **Column scope:** blue columns only (corroborates the companion evidence file).
- **Stock warehouse mapping:**
  - UK marketplace → UK warehouse stock level.
  - Germany marketplace → German warehouse stock level.
  - France marketplace → German warehouse stock level.
  - Italy marketplace → German warehouse stock level.
- **Filters required:** account-wise and marketplace-wise filters must exist in the output.

This independently confirms every element of the task instruction's Section 3 (accounts/marketplaces/periods/filters) and Section 4 (marketplace-to-warehouse mapping) — the image is the direct source of that business rule, not an invention.

## Excluded scope

- No marketplace beyond UK/Germany/France/Italy is in scope.
- No account beyond LEDSONE/DCVoltage is in scope.
- The image does not authorize a France-specific or Italy-specific warehouse stock source — both explicitly use the German warehouse figure per instruction block 4.
- The image says nothing about PPC/traffic/order data following the warehouse mapping — per the task instruction (Section 4), only the stock source follows this shared-warehouse rule; France and Italy PPC/traffic/order/sales metrics remain their own marketplace's metrics.

## Unresolved interpretation

- The image does not state whether shared German stock, when displayed on three separate marketplace rows (Germany/France/Italy) for the same SKU, should be flagged as "shared" in the UI, or simply repeated as-is per row. The task instruction addresses the **totals** side of this ("must not be summed three times as three separate physical stock pools") but does not mandate a specific per-row UI treatment beyond that. Treated as a design-level detail, not a blocking gap — see the design document's stock-logic section.
- The image's period instruction ("7/14/30 Days filter") does not specify a default/initial view. The task instruction allows a 30-day default when the workbook supports it; the reference image's own example data is all labelled "(30d)", which supports 30 days as a reasonable default.

## Owner/reviewer

Business validator: Nivarnan. Coordinator: Satheskanth (developer) / Sathees (coordinator).

## Status

VALIDATED — confirmed by direct image inspection, corroborated across both images.

## Pass/fail rule

PASS if every account/marketplace/period/warehouse claim in this file is traceable to a directly-observed image element. **PASS.**

## Next action

Use this file as the authoritative basis for the account/marketplace mapping discovery (`07_EVIDENCE/database/2026-07-17__account_marketplace_filter_evidence.md`) and the warehouse mapping discovery (`07_EVIDENCE/database/2026-07-17__marketplace_warehouse_mapping_evidence.md`).
