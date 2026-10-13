# Source, provenance and QA record — ASHG 2026 poster

Poster: `output/ASHG2026_Devansh_Pandey_Poster_72x36.pdf` (revision 2, built 2026-10-13).
Scientific source of truth: `Submission_ready_manuscript.pdf`, 45 pages, PDF created 2026-10-06
(Microsoft Word). Page numbers below refer to that file. Figure pages confirmed by visual
inspection: Fig. 1 p.5, Fig. 2 p.8, Fig. 3 p.11, Fig. 4 p.13, Fig. 5 p.15, Supp. Fig. 1 p.19,
Supp. Fig. 8 p.38, Supp. Table 13 p.39-40, Data/Code/Acknowledgements/Affiliations p.44-45.

**Status: REVIEW DRAFT. Not cleared for printing** (see §7 "Unresolved items").

---

## 1. Revision 2 changes (response to review)

| Review item | Action taken | Status |
|---|---|---|
| Insert official logos; remove asset-path text from the poster | Logo hosts (`umac.utexas.edu`, `brand.utexas.edu`, `www.oden.utexas.edu`) re-tested on 2026-10-13 and still refused by the network policy. Slots remain reserved (7.5 x 3.3 in each) with only a faint institution name, no file-path text. Drop-in instructions live in `assets/logos/README.md`, not on the poster. | **Open: needs official files** |
| Resolve affiliations; remove "numbering follows the title page" line | Line removed from the poster. The title-page mapping is still what is printed; the conflict with the end-matter list is unchanged and needs the authors' decision (§5, issue 1). | **Open: needs author decision** |
| Tier counts, events, CIs; confirm tertile recalculation | Counts/CIs are not in the manuscript, figure labels, or the code-only repository (no data). Cut-point recalculation **confirmed** from `Scripts/revised_figures/figure5_redesigned.R` lines 256-261: Tier 1 = `quantile(lp_clin, 0.67)` on all; Tier 2 = `quantile(PRS, 0.67)` within Tier 1; Tier 3 = `quantile(IRS, 0.67)` within Tier 2; within-tier quintiles via `make_quintiles`. Poster intro now says "cut-point recalculated within that tier". | Counts/CIs **open**; nesting confirmed |
| 36.8% prominence | Removed the orange callout and large numeral. The figure now appears once, in a caption-size sentence under the tier cards, with "stratum size and confidence interval are not reported" and the 1.6% crude proportion kept as context. | Done |
| Covariate timing | Workflow clinical box now reads "Imaging-visit measurements, with baseline values substituted when unavailable; standardised, imaging centre as covariate" (Methods p.33 l.957-958). | Done |
| Enlarge central evidence; reduce annotation and variance panel | Hexbin plot enlarged from 5.46 to 6.83 in wide (raster cap relaxed from 150 to 120 ppi; see §2). Three stacked statistics replaced by one annotation line: "PRS–imaging risk correlation: r = 0.065; shared variance = 0.4%; n = 29,075." plus one caveat sentence. Variance decomposition reduced to a compact three-bar strip beside the plot. C-index plot enlarged from 6.2 to 7.6 in tall; AUC benchmark from 5.0 to 5.9 in; workflow to 8.0 in; tier cards to 4.5 in. | Done |
| Remove production commentary and manuscript figure references | All "Fig. 2b / 3c / 3d / 3e / 4e / Supp. Fig. 8d / Supp. Table 13" references, "text summary: R² <1%", "values not reproduced" and "Reported ... (Fig. 2b)" wording removed from the poster face; retained here. | Done |
| Wording | "not comparable with the 0.819 above" → "Different feature set and validation design from the main held-out analysis." Conclusion → "improving discrimination and risk enrichment, with calibration slopes near 1." Column headings → "Study design and imaging features" / "Imaging and genetics capture complementary risk" / "Combined models refine CAD risk". | Done |
| Less explanatory text | Body prose 502 → 412 words (515 including footer). | Done |
| Source bundle not attached | `output/poster_source_bundle.zip` (everything except renders) is now delivered alongside the PDF; the same files are on branch `claude/zen-hamilton-90jlcs` under `poster/`. | Done |

## 2. Figure asset provenance

See `assets/figures/PROVENANCE.md`. The only raster elements are the Fig. 3c hexbin interior
(819 x 658 px, lossless crop of `assets/Figure3.png` from this repository) and its colour bar
(26 x 322 px gradient with vector tick labels). In revision 2 the hexbin is placed at
6.83 x 5.48 in = **120 ppi effective** (`HEXBIN_MIN_DPI = 120` in `build_poster.py`). This is
below the 150-ppi target set for the first draft; it was relaxed deliberately to give the
central plot more space, on the grounds that the content is a smooth density (hexagons are
~14 px across, i.e. ~3 mm at this size) with no fine detail that enlargement would blur.
Each hexagon and the fitted line remain crisp at 72-dpi inspection. If the authors prefer
150 ppi, set the constant back and rebuild (plot shrinks to 5.46 in).

All other charts, the workflow diagram, table, QR code and text are vector.
Embedded manuscript images (720-1247 px wide) were inspected and not used.
`assets/Figure4.png` in the repository is an earlier 10-year/FRS-based version and was not used.

## 3. Number provenance

Every printed number is in `data/numbers.json` with page/panel, unit, population, evaluation
design and uncertainty availability. Summary:

| Poster element | Value(s) | Source | Uncertainty |
|---|---|---|---|
| Cohort tiles | 42,351; 677 (1.6%); 4.6 y; 31,754/499; 10,597/178 | p.3 l.120-121, Supp. Fig. 1 p.19 | n/a |
| PRS meta-analysis | 229,724 cases; 1,024,752 controls | p.9 l.249-250 | n/a |
| Representation benchmark | AUC 0.666 vs 0.770 | p.7 l.214; Fig. 2b | per-fold points in Fig. 2b; no CI in text |
| CCA first-component r | 0.789-0.841 | p.29 l.852-854; Supp. Fig. 6 | n/a |
| PRS-IRS correlation | r = 0.065, R² = 0.004 (printed as 0.4%), n = 29,075 | Fig. 3c subtitle p.11; script computes on `train_df` | n/a |
| IRS variance decomposition | 38.41%, 14.42%, 0.15% partial R² | Fig. 3e labels p.11 | none reported |
| Held-out C-index | 0.749 / 0.788 / 0.813 / 0.819 | p.12 l.331-333; Supp. Fig. 8d | none reported (stated on poster) |
| Tier incidences | 8.0 / 11.3 / 15.9%; 36.8% | p.12 l.349-353; Fig. 4 legend | none reported (stated on poster) |
| Centre table | AUC, C-index and test n per centre | Supp. Table 13 p.39 | none reported |
| NRI, IPA, calibration | 0.634 (0.534-0.734); 5.5% → 9.5%; 0.99-1.08 | p.13 l.361-367; Supp. Fig. 8c | NRI bootstrap CI only |

Definitions preserved: AUC (benchmark) and C-index (held-out Cox) never share an axis; r and
R² carry their own n and population; 1.6% is labelled the crude observed event proportion and
kept distinct from 5-year incidence; 0.070 is called an absolute difference. Nothing is
digitised from bar heights; the leave-one-group-out module is a qualitative grouping from the
Results text (p.9 l.282-285; p.10 l.301-304), labelled "leave-one-group-out".

## 4. Fonts and branding

* Source Sans 3 (SIL OFL 1.1), Regular/Italic/Semibold/Bold, embedded subsets (`pdffonts`:
  4 fonts, all embedded; no base-14 fonts).
* Palette: burnt orange #BF5700, charcoal #333F48, UT blue #005F86, turquoise #00A9B7
  (#00828F for text/markers). UT brand values as known to the build author; **not re-verified
  against the live brand page** (blocked).
* Logos: placeholders (see §1).

## 5. Pre-flight issue log

| # | Issue | Finding | Resolution on poster |
|---|---|---|---|
| 1 | Title-page vs end-matter affiliations | Title page: Narula⁵ (Dell Med Internal Medicine); affiliation 4 (UTHealth Houston) assigned to nobody. End matter: Narula = UTHealth Houston; DiCarlo & Taylor also under "Center for Computational Medicine, UT Austin" (absent from title page); Taylor under Dell Med Internal Medicine but DiCarlo not. | Title-page mapping printed; explanatory footnote removed per review. **Needs author decision.** |
| 2 | ">500,000 images" (abstract) vs 211,755 + 127,053 (Results) | Different counting units; not reconciled. | "8 streams"; no image total printed. |
| 3 | Fig. 3c r = 0.065, n = 29,075 vs text "r ≈ 0.05, R² < 1%" | Figure computed on the training partition. | Figure values printed; R² shown as 0.4%. |
| 4 | Clinical+PRS vs Clinical+imaging nesting | Alternative additions to the same baseline. | Four-row dot plot with explicit sub-labels. |
| 5 | Fig. 4a "10-yr" axis vs 5-year narrative; repo README and preprint describe 10-year | Unresolved in manuscript. | Fig. 4a not used; poster says 5-year throughout. |
| 6 | Extreme-subgroup counts/CI; 1.6% vs KM incidence | Not reported. | 36.8% demoted to a caption sentence with "not reported"; no fold-change claim. |
| 7 | Site-analysis feature set | Methods p.40 list imaging PCs (long-axis, aortic), demographics, lipids, smoking, diabetes; ECG and PRS not listed. | "Site-analysis models ... Different feature set and validation design from the main held-out analysis." |
| 8 | Logos | Blocked. | Placeholders; unresolved. |
| 9 | Paper URL | Repo README cites medRxiv 10.1101/2025.10.09.25337677 ("Multimodal AI for Precision Preventive Cardiology"); confirmed via a search-index entry; page not fetchable here. | Footer: "Preprint (earlier version)" + DOI + QR. **Author to confirm.** |
| 10 | Ethics/consent wording | Only the UKB application number and access statement exist in the manuscript. | Nothing invented. |
| 11 | Abstract publication status | Unknown. | Not stated; flagged. |
| 12 | Genes | No gene-level findings. | "Genome-wide polygenic risk score; no individual gene-level discovery claims." |
| 13 | Encoders | Fine-tuned for CAD classification. | "CAD-fine-tuned"; never "unsupervised". |
| 14 | Combined IDP+embedding AUC | Not printed in manuscript. | Not printed. |
| 15 | Author spellings | Checked against p.1. | Match. |
| 16 | Tier stratification population (new) | Manuscript and Fig. 4e say held-out set. In `figure5_redesigned.R` the tier thresholds are computed on `d_full` (from `fit3_full$data`, fitted on `full_df`), while `run_fig5.R` passes both `full_df` and `test_df`; which frame produced the published 8.0/11.3/15.9/36.8% cannot be confirmed from code alone. | Poster follows the manuscript ("held-out set"). **Author to confirm** the stratification was run on the held-out partition. |
| 17 | Covariate timing (new) | Methods p.33: imaging-visit values, baseline substituted when missing. | Workflow text corrected. |

## 6. QA results (`qa/qa_report.json`, revision 2)

| Check | Result |
|---|---|
| Page count / size | 1 page, MediaBox 5184 x 2592 pt = 72 x 36 in landscape; TrimBox = CropBox = MediaBox; no bleed, no crop marks |
| Fonts | 4 TrueType subsets embedded, all `emb = yes`, `uni = yes` |
| Raster images | 2 (hexbin 120 ppi effective, see §2; colour-bar gradient 81 x 133 ppi) |
| Vector / text | All charts, diagram, table, QR and text vector; `pdftotext` recovers the title and all 28 key numbers |
| Links | GitHub code URL and preprint URL `/URI` annotations present |
| QR | Decodes (OpenCV) from a 150-dpi render to the medRxiv URL; 1.55 in printed |
| Overflow | Build asserts non-negative remaining space (col 1: 0.15 in, col 2: 0.16 in, col 3: 0.29 in) |
| Visual inspection | 20-dpi overview and 72-dpi tiles of header, each column and footer inspected after every change |
| Grayscale | Model groups distinguishable by marker shape, position and direct labels |
| Word budget | 412 words of body prose; 515 including footer |
| Type sizes (pt) | title 100, take-home 50, authors 36, affiliations 27, sections 46, subheads 36, body 33, plot labels 30-33, captions 27, footer 26 |
| Cap heights | title 0.92 in, take-home 0.46 in, section 0.42 in, body 0.30 in, caption 0.25 in |
| Tagged PDF / alt text | **Not tagged**; XMP metadata and `/Lang en-US` only. Descriptions in `docs/ALT_TEXT.md`. |
| PDF/X, CMYK | Not attempted; RGB master. |

**ASHG "one-inch lettering" interpretation.** Only the title approaches one inch literally. The
supporting hierarchy (27-46 pt) reads at 3 ft for a 6-ft poster but does not meet a literal
one-inch minimum for every character; flag before approval rather than declaring compliance.

## 7. Unresolved items (block print clearance)

1. **Official logos** (UT Austin university logo, Oden Institute logo; vector): drop into
   `assets/logos/` and rebuild. Confirm palette hex values.
2. **Affiliation mapping** (issue 1): title-page vs end-matter; decide for Narula, DiCarlo, Taylor.
3. **Tier stratum sizes, event counts and CIs** for Tiers 1-3 and the 36.8% cell (issue 6), and
   confirmation that stratification was run on the held-out partition (issue 16). If counts
   arrive, add them to `data/numbers.json` and to the tier cards.
4. **Paper link** (issue 9): confirm the earlier-version medRxiv DOI, or supply a current URL.
5. **Prior publication status** of the abstract; any **ethics/consent wording** to display.
