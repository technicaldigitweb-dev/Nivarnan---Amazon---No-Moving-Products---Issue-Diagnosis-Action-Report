# v005 File Size and Performance Validation

---

## File size

| File | Size (bytes) | Size (MB) |
|---|---|---|
| v004 (3 independent period datasets embedded) | 139,416,832 | 133.0 MB |
| v005 (1 compact 30-day dataset, gzip+base64 embedded) | 3,915,146 | 3.73 MB |
| **Absolute reduction** | **135,501,686** | **129.2 MB** |
| **Percentage reduction** | | **97.19%** |

**Target met with large margin:** required <50MB, stretch target <25MB — v005 is **3.73MB**, well under both.

## Size breakdown

| Component | Size |
|---|---|
| Uncompressed compact JSON (DATES/ACCOUNTS/MARKETPLACES/TITLES/FEED_COVERAGE/PRODUCTS, one 30-day dataset) | 67,463,812 bytes (64.3 MB) |
| Gzip-compressed binary (level 9) | 2,917,789 bytes (2.78 MB) |
| Base64-encoded (embedded form) | 3,890,388 bytes (3.71 MB) |
| HTML/CSS/JavaScript shell (everything except the embedded payload) | ~24,758 bytes |
| **Final v005 file** | **3,915,146 bytes** |

## Compression method chosen — measured, not assumed

Both approaches were built and measured per instruction, not assumed:

- **A. Plain compact JSON embedded directly:** would have produced a ~67.5MB file — smaller than v004's 139.4MB (thanks to the compact positional-array structure alone) but still far above the 25MB stretch target.
- **B. Gzip-compressed, Base64-embedded:** 3.89MB payload — **94.2% smaller than the uncompressed compact JSON**, and the clear winner.

**Chosen: B — gzip (level 9) + Base64.** Decompression uses the browser-native `DecompressionStream('gzip')` Web API (no external library, no CDN, no build tooling required in the browser) — available in Chrome/Edge 80+, Firefox 113+, Safari 16.4+.

## Why compression works this well

The compact daily-grain data is highly repetitive: most of the 53,843 products × 30 days × 9 metrics = 14.5M+ daily values are `0` (PPC/sales metrics for inactive products) or `null` (traffic metrics for the ~93% of rows outside feed coverage or never tracked — see the coverage findings from the v004 work). Gzip's dictionary-based compression handles this repetition extremely efficiently.

## Decompression overhead (measured, real execution)

| Step | Time |
|---|---|
| File read | 27 ms |
| Base64 decode + gzip decompression (`DecompressionStream`) | 577 ms |
| JSON parse | 476 ms |
| **Total data-ready time** | **~1,080 ms** |

This is a one-time cost at page load, shown to the user via the loading indicator (see UI validation evidence) — well within acceptable range for an internal reporting tool.

## Calculation performance (real execution, full 53,843-product universe)

| Operation | Time |
|---|---|
| 7-day period calculation (all products) | 122 ms |
| 14-day period calculation (all products) | 79 ms |
| 30-day period calculation (all products) | 52 ms |
| Sort (30-day array, full sort by PPC Spend) | 7 ms |
| Filter (Account=LEDSONE + Marketplace=UK) | 3 ms |
| CSV generation (30-day array, all 53,843 rows, 17 columns incl. Account/Marketplace) | 284 ms |

**Total end-to-end (file read → decompress → parse → calculate all 3 periods → sort → filter → CSV) measured in one run: 1,838 ms** — under 2 seconds for the entire pipeline at full scale.

## Real-browser validation

**NOT PERFORMED** — no browser automation tool (Playwright/Puppeteer) and no installed browser were available in this environment to launch without approval, per instruction ("Do not download or install a browser without approval"). All performance figures above are real Node.js/V8 execution against the actual embedded payload and the actual JavaScript logic extracted from the generated file — not simulated — but visual rendering, actual click-driven interaction, and DOM paint timing were not observed in a real browser. DOM structure and CSS arithmetic were verified instead (see the UI/CSV evidence file).

## Status

**PASS** for file size (well under target) and all measurable performance. **Real-browser visual confirmation remains an explicit, disclosed gap**, consistent with the same limitation noted in the v004 task.
