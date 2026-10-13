# Source, provenance and QA record — ASHG 2026 poster

Poster: `output/ASHG2026_Devansh_Pandey_Poster_72x36.pdf` (design v3, built 2026-10-13).
Scientific source of truth: `Submission_ready_manuscript.pdf`, 45 pages, PDF created 2026-10-06.
Page numbers refer to that file. Figure pages confirmed visually: Fig. 1 p.5, Fig. 2 p.8,
Fig. 3 p.11, Fig. 4 p.13, Fig. 5 p.15, Supp. Fig. 1 p.19, Supp. Fig. 8 p.38, Supp. Table 13
p.39-40, Data/Code/Acknowledgements/Affiliations p.44-45.

**Status: REVIEW DRAFT. Not cleared for printing** (see §8 "Unresolved items").

---

## 1. Design v3: rationale

Rebuilt from first principles around one visual argument: *two risk axes that barely
correlate, and what happens when you stack them.*

| Element | Decision |
|---|---|
| Reading path | Deep-navy header band (title, authors, take-home) → a three-finding strip with the headline numbers (10-second read) → three columns, each led by one large figure (1-minute read) → captions, conclusion and limitations (3-minute read). |
| Hero figure | The PRS-vs-imaging-risk hexbin, now a **vector transcription** of the manuscript's Fig. 3c (1,261 cells; §3). 9.1 x 7.3 in plot area, the largest single element on the page. |
| Supporting figures | Confluence diagram (three ribbons merging into one model); AUC benchmark bars; C-index ladder with absolute deltas vs the clinical baseline; incidence staircase for the three tiers; two small dot panels for the centre check. All vector. |
| Typography | Fraunces (display serif, OFL) for the title, section heads and large numerals; Source Sans 3 (OFL) for everything else. Two families, consistent weights. |
| Palette | Ink #14213D (band, headings), burnt orange #BF5700 (emphasis, full model), teal #0E9594 (imaging), indigo #4F5BD5 (genetics), slate #6E7B86 (clinical baseline), sand #F4F1EA panels, white page. Density ramp: single hue, pale blue-grey → navy. |
| Palette validation | Run with the dataviz palette checker (light surface, adjacent pairs): lightness band PASS, CVD separation PASS (worst ΔE 15.5 deutan), normal-vision floor PASS (worst ΔE 18.1), contrast ≥ 3:1 PASS. The slate clinical slot is below the chroma floor **by design** (neutral baseline); identity is also carried by marker shape (circle / square / triangle / diamond) and direct labels, and the grayscale render was checked. |
| Branding | Header band runs edge to edge (no bleed allowance; the file has no crop marks). Logo plates are white rounded panels so the official marks sit on white as brand rules usually require. Still placeholders (§8). |

## 2. Number provenance

Every printed number is in `data/numbers.json` with page/panel, unit, population, evaluation
design and uncertainty availability.

| Poster element | Value(s) | Source | Uncertainty |
|---|---|---|---|
| Findings strip | AUC 0.77 vs 0.67; r = 0.065; C-index 0.819 vs 0.749; 15.9% | as below | as below |
| Cohort numerals | 42,351; 677 (1.6%); 4.6 y; 31,754/499; 10,597/178 | p.3 l.120-121, Supp. Fig. 1 p.19 | n/a |
| PRS meta-analysis | 229,724 cases; 1,024,752 controls | p.9 l.249-250 | n/a |
| Representation benchmark | AUC 0.666 vs 0.770 | p.7 l.214; Fig. 2b | per-fold points in Fig. 2b; no CI in text |
| CCA first-component r | 0.79-0.84 | p.29 l.852-854 | n/a |
| PRS-IRS correlation | r = 0.065, shared variance 0.4% (R² = 0.004), n = 29,075 | Fig. 3c subtitle p.11; script computes on `train_df` | n/a |
| IRS variance decomposition | genetics 0.15%, demographics 38.4% (printed 38.41%) | Fig. 3e labels p.11 | none reported |
| Held-out C-index | 0.749 / 0.788 / 0.813 / 0.819; deltas +0.039 / +0.064 / +0.070 by subtraction, labelled absolute | p.12 l.331-333; Supp. Fig. 8d | none reported (stated) |
| Tier incidences | 8.0 / 11.3 / 15.9%; 36.8% (caption only) | p.12 l.349-353; Fig. 4 legend | none reported (stated) |
| Centre panels | AUC and C-index per centre, test n | Supp. Table 13 p.39 | none reported |
| NRI, IPA, calibration | 0.634 (0.534-0.734); 5.5 to 9.5%; 0.99-1.08 | p.13 l.361-367; Supp. Fig. 8c | NRI bootstrap CI only |

Definitions preserved: AUC (benchmark) and C-index (held-out Cox) never share an axis; the
two centre panels (AUC, C-index) have separate axes; 1.6% is labelled the crude observed
event proportion and kept distinct from 5-year incidence; the leave-one-group-out module is
a qualitative grouping from the Results text (p.9 l.282-285; p.10 l.301-304).

## 3. Figure provenance

Full detail in `assets/figures/PROVENANCE.md`. Summary of the hexbin transcription
(`tools/hexbin_transcribe.py`): lattice detected from the edge-map autocorrelation (cell
width 12.01 px, row spacing 15.23 px, half-width offset); per-cell colour = median of an
inscribed disc, fitted line by least squares on red pixels; re-rendering at source size
matches the original crop on 95.1% of pixels (24/255 tolerance), residual at anti-aliased
edges (`qa/hexbin_transcription_compare.png`). Colours are re-mapped monotonically from the
original log-count gradient onto the poster ramp; positions and relative counts are
unchanged. **The poster now contains no raster images** (`pdfimages -list`: 0).

## 4. Fonts and licences

Source Sans 3 (Adobe, SIL OFL 1.1) and Fraunces (Undercase Type, SIL OFL 1.1; static
instances at wght 700/600, opsz 144 generated with fontTools from the Google Fonts variable
file). Licences in `assets/fonts/`. `pdffonts`: 5 TrueType subsets, all embedded.

## 5. Pre-flight issue log (unchanged findings, updated resolutions)

| # | Issue | Finding | Resolution on poster |
|---|---|---|---|
| 1 | Title-page vs end-matter affiliations | Title page: Narula⁵; affiliation 4 unassigned. End matter: Narula = UTHealth Houston; DiCarlo & Taylor also under "Center for Computational Medicine". | Title-page mapping printed. **Needs author decision.** |
| 2 | ">500,000 images" vs 211,755 + 127,053 | Not reconciled in text. | "8 streams"; no image total. |
| 3 | Fig. 3c r = 0.065, n = 29,075 vs text r ≈ 0.05 | Figure computed on the training partition. | Figure values printed, shared variance 0.4%. |
| 4 | Nesting of Clinical+PRS / Clinical+imaging | Alternative additions to one baseline. | Ladder with explicit sub-labels; dashed baseline reference. |
| 5 | Fig. 4a "10-yr" axis; preprint/README say 10-year | Unresolved in manuscript. | Fig. 4a not used; 5-year throughout. |
| 6 | Extreme-subgroup counts/CI | Not reported. | 36.8% in caption only with "not reported". |
| 7 | Site-analysis feature set | ECG and PRS not listed in Methods p.40. | "Different feature set and validation design"; "not external validation". |
| 8 | Logos | Hosts blocked; no author assets. | White plates with faint name; **open**. |
| 9 | Paper URL | medRxiv 10.1101/2025.10.09.25337677 (earlier title); page not fetchable here. | "Preprint (earlier version)" + DOI + QR. **Author to confirm.** |
| 10 | Ethics/consent | Only UKB application number in manuscript. | Nothing invented. |
| 11 | Abstract publication status | Unknown. | Flagged. |
| 12 | Genes | No gene-level findings. | Footer statement. |
| 13 | Encoders | Fine-tuned for CAD. | "CAD-fine-tuned"; never "unsupervised". |
| 14 | Combined IDP+embedding AUC | Not printed. | Not printed. |
| 15 | Author spellings | Checked p.1. | Match. |
| 16 | Tier stratification population | Script builds tiers on `d_full`; manuscript says held-out. | Poster follows manuscript. **Author to confirm.** |
| 17 | Covariate timing | Methods p.33. | "imaging-visit measurements, baseline values substituted when unavailable". |

## 6. QA results (`qa/qa_report.json`, design v3)

| Check | Result |
|---|---|
| Page | 1 page, MediaBox 5184 x 2592 pt = 72 x 36 in landscape; TrimBox = CropBox = MediaBox; no bleed, no crop marks (header band to the edge relies on an untrimmed 72 x 36 sheet) |
| Fonts | 5 TrueType subsets embedded (`emb = yes`, `uni = yes`) |
| Raster images | **0** (hexbin is vector; no logos yet) |
| Text | `pdftotext` recovers the title and all key numbers |
| Links | GitHub code URL and preprint URL annotations present; QR decodes (OpenCV) to the medRxiv URL |
| Overflow | Build asserts non-negative remaining space (col 1: 0.22 in, col 2: 0.46 in, col 3: 0.20 in) |
| Visual inspection | 20-dpi overview and 72-dpi tiles of header, findings strip, each column and footer; defects found in the first v3 render (card text overflow, clipped ladder deltas, axis-label and row-label collisions, missing arrow glyph in the display face) fixed and re-rendered |
| Grayscale | Checked: hex ramp stays monotone; groups distinguishable by marker shape, bar position and direct labels |
| Word budget | 385 words of body prose; 488 including footer |
| Type sizes (pt) | title 104 (Fraunces), take-home 42, authors 36, affiliations 26, findings 42/60, sections 50, subheads 36, body 32, plot labels 28-34, captions 27, footer 25 |
| Cap heights | title ≈ 1.0 in (Fraunces cap ≈ 0.70 em), sections 0.49 in, body 0.30 in, captions 0.25 in |
| Tagged PDF | **Not tagged**; XMP metadata and `/Lang en-US`; descriptions in `docs/ALT_TEXT.md` |
| PDF/X, CMYK | Not attempted; RGB master |
| File size | 0.11 MB |

**ASHG one-inch lettering.** Only the title meets it literally; the supporting hierarchy
(25-60 pt) is readable at 3 ft on a 6-ft poster but not literally one inch. Flag before
approval rather than declaring compliance.

## 7. Reproducibility

`make` (= `python build_poster.py && python qa_checks.py`). To regenerate the hexbin cell
list from the figure crop: `python tools/hexbin_transcribe.py` (writes `hexcells.json` and
the comparison image into the working directory; copy to `assets/figures/` and `qa/`).

## 8. Unresolved items (block print clearance)

1. **Official logos** into `assets/logos/` (see its README); confirm brand hex values.
2. **Affiliation mapping** (issue 1).
3. **Tier stratum sizes, events and CIs**, and confirmation that tiers were built on the
   held-out partition (issues 6, 16).
4. **Paper link** (issue 9).
5. **Abstract publication status** and any **ethics/consent wording** to display.
