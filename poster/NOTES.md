# Poster build notes — third pass (scale, white space, print production)

Build: `python3 poster/build/build_poster.py && python3 poster/build/render_outputs.py && python3 poster/build/audit_poster.py`
(Python 3.13, matplotlib 3.11, PyMuPDF 1.28, fontTools, segno, zxing-cpp, Playwright driving the
pre-installed Chromium 141 at `/opt/pw-browsers/chromium-1194`). All layout units are PDF points;
charts are matplotlib SVGs with real text (`svg.fonttype = none`) so the PDF text layer carries
every chart label and the size audit can see them.

The earlier passes' build files and NOTES were not in the repository (only the v2 `poster.pdf` was
supplied), so this pass rebuilt the poster from the v2 PDF: text was taken from its text layer,
the two logos were lifted as vector paths, the three sample images were extracted as-is, and the
chart values were re-derived from the manuscript and `Scripts/revised_figures/*.R` (provenance table
below). Layout, palette and wording follow v2 except where this pass asked for changes.

## Deliverables (poster/)
| file | what |
|---|---|
| `poster.pdf` | 72 × 36 in, fonts embedded (print file for printers that accept fonts) |
| `poster_print.pdf` | same page with every glyph converted to filled paths; `pdffonts` lists no fonts |
| `preview.png` | 20 DPI, 1440 × 720 |
| `crop_col1-4.png` | each column at 72 DPI |
| `poster_thumbnail.png` | 150 DPI at ¼ scale (2700 × 1350) for the presenter's phone |
| `alt_text.md` | screen-reader description of every element |
| `out/poster.html`, `out/charts/*.svg`, `out/audit.json`, `out/audit_report.txt` | intermediate HTML, chart sources, audit output |
| `build/` | `charts.py`, `build_poster.py`, `render_outputs.py`, `audit_poster.py` |
| `fonts/`, `images/` | static instances of Inter Tight / Inter / Source Sans 3 (OFL), logo SVGs, sample images |

## Judgement calls (in task order)

### §1 Scale
1. **Column geometry.** Page margin 1.0 in on all sides (text bboxes verified ≥ 72 pt from every
   edge). Columns are 1227 pt (17.0 in) wide with 44 pt gutters; cards have 20 pt padding, so the
   inner width is 1187 pt ≈ 16.5 in. Every chart is set to that inner width.
2. **Header compressed to free vertical space** for the enlarged charts: title 102 pt (was 112),
   the presenter line now sits at the end of the affiliations line (same text, same orange
   semibold), QR reduced to 2.8 in with the URL on three lines. Colour key raised to 32 pt with
   0.5 in (36 pt) swatches; the extra-cardiac tint swatch carries the same dark outline as its bars.
3. **Column 2** charts: IDP-vs-embeddings 16.5 × 5.0 in, CCA 16.5 × 5.0 in, model-selection strip
   two panels of 8.1 × 5.0 in. All tick/category labels 26–27 pt.
4. **Column 3**: hexbin 8.0 × 8.0 in with the `r ≈ 0.05` hero and the three partial-R² tiles stacked
   to its right (the former hexbin caption is folded into the hero subtitle so the stack and the
   square fill the card). Paired R²/LOO chart 16.5 × 6.4 in (13 categories at 27 pt, 34 pt pitch).
   The 7-in request was trimmed by 0.6 in to make the three cards fit the column; the labels are
   unchanged in size. Unique-variance dumbbell 16.5 × 5.0 in.
5. **Column 4 could not take two 6-in charts plus hero, tiles, Conclusions and Limitations** in
   the 1,706 pt available (header + footer leave 23.7 in per column). Following the task's overflow
   order: HR lollipop dropped and replaced by the one-line HR footnote; the four centre bars
   replaced by the one-line leave-one-centre-out text; C-index chart trimmed first (4.2 in — 9 bars
   at 27 pt labels, 29 pt pitch, the legibility floor); tier staircase 4.2 in; Limitations cut to
   three bullets (temporal-proximity point merged into the complete-case bullet). The four result
   tiles sit in a 2 × 2 grid beside the hero so the hero/tile row is 265 pt instead of 340 pt.
   Both column-4 charts therefore fall short of the ≥ 6 in target; everything else in the brief
   is met.
6. **Hero `36.8%`** is a block-level element with its subtitle on the following line;
   `page.get_text()` returns `…very-high-risk people⏎36.8%⏎5-yr CAD incidence…` (one token).
   The `0.770 vs 0.666` subtitle now ends "both combined 0.775".
7. **Fig. 3 blood-flow MRI colour.** v2 coloured blood-flow MRI with the extra-cardiac tint; it is
   a cardiac MRI stream, so it now carries the cardiac orange to match the key.
8. **Column 1 cohort tiles.** "211,755 cardiac cine MRI + 127,053 2D images" split into two tiles
   so both numbers are set at the same 40 pt size (six tiles in the row).

### §2 Simplification
9. **Fig. 3f dumbbell.** The manuscript's panel shows four separate bars per group — alone,
   + ECG, + metabolic, + baseline — each a *single* adjustment (not cumulative). The coloured dot
   therefore shows the lowest of the three single adjustments, which is always "+ Baseline"
   (values from `Figure3_integrated_revised.R`: LA 0.237 → 0.099, AD 0.163 → 0.055, PRS 0.068 →
   0.051, BF 0.112 → 0.020, liver 0.096 → 0.005, pancreas 0.088 → 0.008, DXA 0.036 → 0.004).
   The axis label says "after baseline adjustment" rather than "after ECG + metabolic + baseline"
   so the chart does not claim a joint adjustment the manuscript does not report. Liver, pancreas
   and DXA are bracketed "≈ 0 after adjustment".
10. **Pipeline.** Three lanes + converging row; box text 26 pt, ≤ 6 words per box; sample images
    4.2 in tall (cardiac 6.1 in wide, abdominal 4.2 in, DXA 3.3 in). No XGBoost box; "XGBoost +
    nested Cox" stays in Methods in brief. The italic "Cardiac MRI does not image coronary
    atherosclerosis…" line is 26 pt directly under the pipeline.
11. **Sample-image resolution (flag).** The abdominal (288 × 288 px) and DXA (272 × 346 px)
    sources inherited from v2 are small: at the requested ≥ 3 in width their native resolution is
    69 and 83 ppi. They are resampled 3× (Lanczos + light unsharp mask) before embedding so the
    printer preflight sees 207 and 249 ppi; the *native* detail is still that of the 288/272-px
    originals. Replace `poster/images/abdominal_mri.png` and `dxa.png` with higher-resolution
    crops (≥ 650 px wide) if available and rebuild. The cardiac frame (1210 × 824 px) is native
    198 ppi.
12. **Hexbin is synthetic (flag).** Participant-level imaging/polygenic scores are not in the
    repository, so Fig. 3c is reproduced as a bivariate-normal sample with the reported n = 29,075
    and r = 0.046 (ρ = 0.057 printed from the manuscript). It is labelled "schematic rendering of
    the reported r" on the poster. Swap in a high-resolution export of the real panel if one exists.

### §3 Column structure
13. Limitations moved to column 4 under Conclusions, same h3/bullet formatting. Column 1 is
    Background & questions → pipeline → cohort tiles → Methods in brief; the spare height went
    into the pipeline images.

### §4 Wording
14. All eight requested edits applied verbatim (column-4 caption "among the strongest independent
    predictors (HR ≈ 2.1 per SD)"; "discrimination is stable across the four UK Biobank imaging
    centres (site-level robustness, not external validation)"; background bullet rewritten;
    question 1 includes "metabolic"; PRS bullet carries "(with age, sex, 20 PCs)"; "(combined
    0.775)" on the hero subtitle). The "Clinical" lane tag uses #5e6973 instead of the key grey so
    its white text reaches 5.6 : 1.

### §5 Production
15. **Outlines.** Ghostscript is not installable in the build container, so `poster_print.pdf` is
    produced by `render_outputs.py`: each glyph in the PDF text trace is drawn as a filled path
    from the embedded subset font (fontTools), the `BT…ET` text objects are stripped from the
    content stream and the font resources removed. Verified: 8,393 glyphs outlined, `pdffonts`
    empty, page size unchanged, 0.24% of pixels differ from `poster.pdf` at 20 DPI (anti-aliasing
    of hinted text vs paths).
16. **Word count.** Body text in the strict sense (Background, questions, Methods, Conclusions,
    Limitations) is 187 words. Including pipeline box labels (78), tile labels (69) and the hero
    subtitles (59) it is 393. Captions (190), header (122) and footer (210) are excluded. Nothing
    was cut to reach 300 because that would remove content; trim the tile and pipeline labels if
    the stricter reading is intended.

## Provenance table (every number on the poster)
| poster | value | source |
|---|---|---|
| cohort, cases, follow-up | 42,351; 677 (1.6%); 4.6 yr | manuscript p.3, p.18, Supp. Fig. 1 |
| cine series / 2D images | 211,755 / 127,053 | p.3 |
| held-out set | 10,597 (178 cases) | Supp. Fig. 1 |
| PRS | OR 1.87/SD (95% CI 1.80–1.94), AUC 0.766, age/sex/20 PCs; 229,724 cases / 1,024,752 controls | p.9, Supp. Fig. 7 |
| embeddings vs IDPs | AUC 0.770 vs 0.666; combined 0.775; LR 414.5 (p 4.1×10⁻⁷⁶), LR 45.1 (p 4.6×10⁻⁶) | p.7 (AUCs); LR statistics inherited from v2 (Fig. 2b annotation; not in the text) |
| plateau | ~5 PCs per modality | Fig. 2a legend |
| CCA CV1 | 2CH 0.812, 3CH 0.789, 4CH 0.841, AD 0.816 | p.29–30 |
| 3D pretraining AUC | ResNet-18 0.608, MC3-18 0.618, R(2+1)D 0.650, Med3D 0.681 | Supp. Fig. 3 / p.6 (0.650, 0.681 in text; 0.608, 0.618 from the figure) |
| 2D accuracy | liver 0.50→0.64, pancreas 0.53→0.63, DXA 0.54→0.57 | p.6, p.27, Supp. Table 3 |
| r, ρ, n | r ≈ 0.05 (0.046), ρ 0.057, n 29,075 | p.10, Fig. 3c annotation |
| partial R² of IRS | PRS 0.15%, demographics 38.4%, clinical 14.4% | Fig. 3e (38.41 / 14.42 / 0.15) |
| R² alone, LOO change | 13 groups | `Scripts/revised_figures/Figure3_integrated_revised.R` (`r2_data`, `loo_data`) |
| unique variance | alone / + Baseline | same script (`other_data`, `PRS_data`) |
| C-index | 0.621, 0.722, 0.725, 0.749, 0.772, 0.788, 0.789, 0.813, 0.819 | p.12 (0.749/0.788/0.813/0.819), Supp. Fig. 8d (rest) |
| HR per SD | imaging ≈ 2.1, demographics ≈ 1.4, PRS ≈ 1.7, lipids ≈ 1.1 | Supp. Fig. 8b (read from the plot; the text gives only the ordering) |
| tiers | 1.6, 8.0, 11.3, 15.9, 36.8% | p.12, Fig. 4e |
| ≈23× | 36.8 / 1.6 = 23.0 | arithmetic |
| NRI | 0.634 (0.534–0.734) | p.13 |
| IPA | 5.5% → 9.5% | p.13, Supp. Fig. 8c |
| heart age | 55.3 → 86.8 yr | Supp. Fig. 8a |
| calibration slopes | 0.99–1.08 | p.13 |
| centres | AUC 0.785–0.822, C-index 0.732–0.762 | p.14, Supp. Table 13 |
| outcome codes | ICD-10 I20–I25; ICD-9 410/412/414; OPCS-4 K40–K50, K75 | p.18 |
| UKB application | 65439 | inherited from v2 (not in the manuscript text) |

## Remaining placeholders
- Presenter e-mail (`[email placeholder]`, header).
- `[Previously published: JOURNAL, DATE — remove if not applicable]` (footer, orange).
- No preprint DOI is on the poster; add one to the footer "Data & code" sentence if it exists.
- Two low-resolution sample images and the synthetic hexbin (items 11 and 12 above).

## Audit summary (from `audit_poster.py`)
- `pdfinfo`: 1 page, 5184 × 2592 pt for both PDFs. `pdffonts`: 16 subset CID TrueType fonts, all
  embedded, no Type 3 in `poster.pdf`; none in `poster_print.pdf`.
- Rasters: cardiac 1210 × 824 px at 6.12 × 4.17 in = 198 ppi; abdominal 864 × 864 px at 4.17 in =
  207 ppi (3× resample of 288 px); DXA 816 × 1038 px at 3.27 × 4.17 in = 249 ppi (3× of 272 px).
  QR and logos are vector.
- Text: minimum 24 pt (affiliation superscripts); body 32 pt; chart ticks 26 pt, categories 27 pt.
- QR decodes (zxing-cpp, 300 DPI) to the GitHub URL exactly, from both PDFs.
- Contrast: every text/background pair ≥ 4.59 : 1; the extra-cardiac tint is 1.8 : 1 against white
  and is therefore always drawn with the #8a3f00 outline (7.5 : 1).
- Safe margin: nearest text/vector to any edge = 72.0 pt.
