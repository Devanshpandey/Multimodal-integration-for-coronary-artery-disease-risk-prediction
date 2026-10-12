# Source, provenance and QA record — ASHG 2026 poster

Poster: `output/ASHG2026_Devansh_Pandey_Poster_72x36.pdf` (built from this bundle, 2026-10-12).
Scientific source of truth: `Submission_ready_manuscript.pdf`, 45 pages, PDF created 2026-10-06
(Microsoft Word). Page numbers below refer to that file. Figure pages confirmed by visual
inspection: Fig. 1 p.5, Fig. 2 p.8, Fig. 3 p.11, Fig. 4 p.13, Fig. 5 p.15, Supp. Fig. 1 p.19,
Supp. Fig. 8 p.38, Supp. Table 13 p.39-40, Data/Code/Acknowledgements/Affiliations p.44-45.

**Status: REVIEW DRAFT. Not cleared for printing** (see "Unresolved items").

---

## 1. Number provenance

Every printed number is in `data/numbers.json` with page/panel, unit, population, evaluation
design and uncertainty availability. Summary:

| Poster element | Value(s) | Source | Uncertainty |
|---|---|---|---|
| Cohort tiles | 42,351; 677 (1.6%); 41,674; 4.6 y; 31,754/499; 10,597/178 | p.3 l.120-121, Supp. Fig. 1 p.19 | n/a |
| PRS meta-analysis | 229,724 cases; 1,024,752 controls | p.9 l.249-250 | n/a |
| Representation benchmark | AUC 0.666 (IDPs) vs 0.770 (embeddings) | p.7 l.214; Fig. 2b | per-fold points in Fig. 2b; no CI in text |
| CCA first-component r | 0.789-0.841 | p.29 l.852-854; Supp. Fig. 6 | n/a |
| PRS-IRS correlation | r = 0.065, R² = 0.004, n = 29,075 | Fig. 3c subtitle p.11; script `Scripts/revised_figures/Figure3_integrated_revised.R` (computed on `train_df`) | n/a |
| IRS variance decomposition | 38.41%, 14.42%, 0.15% partial R² | Fig. 3e bar labels p.11 | none reported |
| Held-out C-index | 0.749 / 0.788 / 0.813 / 0.819 | p.12 l.331-333; Supp. Fig. 8d p.38 | none reported (stated on poster) |
| Tier incidences | 8.0% / 11.3% / 15.9%; 36.8% | p.12 l.349-353; Fig. 4 legend p.13 l.396-399 | none reported (stated on poster) |
| Centre table | AUC 0.805/0.822/0.785/0.795; C 0.762/0.748/0.751/0.732; test n per centre | Supp. Table 13 p.39 | none reported |
| NRI, IPA, calibration | 0.634 (0.534-0.734); 5.5% -> 9.5%; 0.99-1.08 | p.13 l.361-367; Supp. Fig. 8c | NRI 95% bootstrap CI only |

Definitions preserved on the poster: AUC (benchmark, logistic regression) and C-index
(held-out Cox) are on separate axes and never mixed; r and R² are labelled with their own n
and population; 1.6% is labelled as the crude observed event proportion; tier values are
labelled 5-year (Kaplan-Meier) incidence; the absolute C-index difference 0.070 is called an
absolute difference.

Nothing on the poster is digitised from bar heights. Exact leave-one-out values (Fig. 3b) and
unique-variance values (Fig. 3f) are not printed in the manuscript, so that module is a
qualitative grouping taken from the Results text (p.9 l.282-285; p.10 l.301-304) and is
labelled as such.

## 2. Figure asset provenance

See `assets/figures/PROVENANCE.md`. The only raster elements are the Fig. 3c hexbin interior
(819 x 658 px, lossless crop of `assets/Figure3.png` from this repository, placed at 5.46 x
4.39 in = **150 ppi effective**, enlargement capped in code) and its colour bar (26 x 322 px
gradient; 81 x 133 ppi, a smooth gradient with vector tick labels). All other charts,
diagrams, text, the QR code and rules are vector. Embedded manuscript images (720-1247 px
wide, extracted with PyMuPDF) were inspected and not used. `assets/Figure4.png` in the
repository is an earlier 10-year/FRS-based version and was not used.

## 3. Fonts and branding

* Typeface: Source Sans 3 (Adobe, SIL OFL 1.1; licence in `assets/fonts/`), Regular, Italic,
  Semibold, Bold, embedded as subsets (`pdffonts`: 4 fonts, all embedded; no Helvetica).
* Palette: burnt orange #BF5700, charcoal #333F48, limestone #D6D2C4, UT blue #005F86,
  turquoise #00A9B7 (darkened to #00828F for text/markers). These are the UT Austin brand
  values as known to the author of the build; **the live brand page could not be reached from
  the build environment and the values were not re-verified**.
* Logos: **placeholders**. `umac.utexas.edu`, `brand.utexas.edu`, `www.oden.utexas.edu` and
  Wikimedia were all refused by the network policy, and no author-supplied assets exist in the
  repository. Reserved slots: 7.5 x 3.3 in each, header left/right, with a drop-in path
  (`assets/logos/README.md`). The build records slot status in `qa/build_report.json`.

## 4. Pre-flight issue log

| # | Issue | Finding | Resolution on poster |
|---|---|---|---|
| 1 | Title-page vs end-matter affiliations | Title page: Narula⁵ (Dell Med Internal Medicine); affiliation 4 (UTHealth Houston) assigned to nobody. End matter: Narula = UTHealth Houston; DiCarlo & Taylor also listed under "Center for Computational Medicine, UT Austin", which is absent from the title page; Taylor listed under Dell Med Internal Medicine but DiCarlo is not. | Title-page mapping preserved verbatim; footnote says so. **Needs author confirmation.** |
| 2 | ">500,000 images" (abstract) vs 211,755 cine + 127,053 2D images (Results) | Different counting units/populations; not reconciled in text. | Poster says "8 imaging streams"; no total image count printed. |
| 3 | Fig. 3c r = 0.065, n = 29,075 vs text "r ≈ 0.05, R² < 1%" | Figure script computes on the training partition. | Figure values printed with their own n; "<1%" wording kept. |
| 4 | Clinical+PRS vs Clinical+imaging nesting | They are alternative additions to the same baseline. | Four-row dot plot with explicit sub-labels; no staircase. |
| 5 | Fig. 4a "10-yr" axis label vs 5-year narrative; repo README and preprint describe a 10-year horizon | Unresolved in manuscript. | Fig. 4a not used; all poster statements say 5-year. |
| 6 | Extreme-subgroup counts/CI; 1.6% vs KM incidence | Not reported anywhere. | 36.8% shown as secondary callout with full definition and "not reported" statement; 1.6% labelled crude proportion; no "x-fold" claim. |
| 7 | Site-analysis feature set | Methods p.40 list imaging PCs (long-axis, aortic), demographics, lipids, smoking, diabetes; ECG and PRS not listed. | Labelled "site-analysis models"; explicitly "not comparable with 0.819". |
| 8 | Logos | Blocked (see §3). | Placeholders; unresolved. |
| 9 | Paper URL | Repository README cites medRxiv 10.1101/2025.10.09.25337677 ("Multimodal AI for Precision Preventive Cardiology"). Existence confirmed through a web-search index entry naming the same DOI, title and authors; the medRxiv page itself and api.biorxiv.org were unreachable from this environment. | Footer gives DOI + QR labelled "Preprint of an earlier version" with a note that title and some analyses differ. **Author should confirm this is the link they want on the poster.** |
| 10 | Ethics/consent wording | Manuscript gives only the UK Biobank application number (65439) and the controlled-access statement; no explicit consent/IRB sentence. | Nothing invented; only the application number and access statement appear. |
| 11 | Abstract publication status | Unknown; "submission-ready" is not publication. | Not stated on the poster; flagged for the author. |
| 12 | Genes | Prediction/PRS study; no gene-level findings. | Footer: "Genome-wide polygenic risk score; no individual gene-level discovery claims." |
| 13 | Encoder description | Manuscript says fine-tuned for CAD classification. | Poster says "CAD-fine-tuned CNN encoders"; never "unsupervised". |
| 14 | Combined IDP+embedding AUC | Only "minimal incremental improvement" is stated. | Not printed. |
| 15 | Author spellings | Checked against title page p.1 (Liaoyi Xu, Eucharist Kun, Chenfei Li, Joyce Y. Wang, Alaa Melek, Julie C. DiCarlo, Edward Castillo, Jagat Narula, Charles A. Taylor, Vagheesh M. Narasimhan). | Match. |

## 5. QA results (from `qa/qa_report.json`, last build)

| Check | Result |
|---|---|
| Page count / size | 1 page, MediaBox 5184 x 2592 pt = 72 x 36 in landscape; TrimBox = CropBox = MediaBox; no bleed, no crop marks |
| Fonts | 4 TrueType subsets embedded, all `emb = yes`, `uni = yes` (text searchable) |
| Raster images | 2 (hexbin interior 150 ppi effective; colour-bar gradient 81 x 133 ppi) |
| Vector / text preservation | All charts, diagram, table, QR and text are vector; `pdftotext` recovers title and all 28 key numbers |
| Links | GitHub code URL (footer block hotspot) and preprint URL (QR hotspot); both `/URI` annotations present |
| QR | Decodes (OpenCV) from a 150-dpi render to `https://www.medrxiv.org/content/10.1101/2025.10.09.25337677`; 1.55 in printed size |
| Overflow | Build asserts every column has non-negative remaining space (col 1: 0.37 in, col 2: 0.35 in, col 3: 0.58 in spare) |
| Visual inspection | Full-page render plus 72-dpi tiles of header, each column (top/bottom), chip block and footer inspected; overlaps found in earlier iterations (workflow text, AUC labels, bracket, axis label, chip note) were fixed and re-rendered |
| Colour-vision / grayscale | 20-dpi grayscale render inspected: model groups remain distinguishable by marker shape (circle/square/triangle/diamond), position and direct labels |
| Word budget | 502 words of explanatory body prose (ceiling 500-650); 620 including footer blocks |
| Type sizes (pt) | title 100 (2 lines), take-home 50, authors 36, affiliations 27, section 46, subheads 36, body 33, plot labels 30, captions 27, footer 26 |
| Cap heights (Source Sans 3 cap height 0.66 em) | title 0.92 in, take-home 0.46 in, section 0.42 in, body 0.30 in, caption 0.25 in, footer 0.24 in |
| Tagged PDF / alt text | **Not tagged**; XMP metadata, `/Lang en-US` and reading-order text only. Descriptions in `docs/ALT_TEXT.md`. |
| PDF/X, CMYK | Not attempted; RGB master only. Convert with a real vendor profile if required and re-inspect. |
| File size | 0.12 MB |

**ASHG "one-inch lettering" interpretation.** The ASHG guidance asks for lettering about one
inch high readable at three feet. Only the title (0.92 in cap height, ~1.2 in including
ascenders) approaches that literally. Section headings, body text and plot labels use a
conventional 27-46 pt supporting hierarchy (0.25-0.42 in cap height), which reads comfortably
at 3 ft for a 6-ft-wide poster but does **not** meet a literal one-inch minimum for every
character. If the organisers require literal compliance throughout, content would have to be
cut by roughly two-thirds; flag before approval rather than declaring compliance.

## 6. Unresolved items (block print clearance)

1. **Official logos** (UT Austin university logo and Oden Institute logo, vector): supply
   files per `assets/logos/README.md` and rebuild. Also confirm the brand hex values.
2. **Affiliation mapping** (issue 1): confirm whether to keep the title-page mapping or the
   end-matter mapping (Narula = UTHealth Houston? Add "Center for Computational Medicine"?).
3. **Paper link**: confirm the medRxiv DOI should appear (it is an earlier, differently
   titled version), or supply a current public URL.
4. **Prior publication status** of the abstract and any **ethics/consent wording** the
   presenter wants shown.
5. **Fig. 2b evaluation population** (training folds vs held-out) if the presenter wants to
   tighten the "representation benchmark" label.

Everything else on the poster is complete and traceable; the file is ready for scientific
review as a draft.
