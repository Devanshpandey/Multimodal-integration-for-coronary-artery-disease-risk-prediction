# Accessible descriptions of the poster's visual modules (design v3)

These descriptions are a fallback for readers of the digital PDF. The PDF produced by
`build_poster.py` is **not tagged** (ReportLab does not emit a structure tree), so this
text is not embedded as `/Alt` attributes. The PDF does carry searchable text in reading
order (header band, findings strip, column 1, column 2, column 3, footer), document
language `en-US`, and XMP title/author/description metadata.

## Header band (deep navy, full width)
Title in a serif display face, white. Eleven authors with numbered affiliations (presenter
Devansh Pandey in bold; corresponding author Vagheesh M. Narasimhan marked with a dagger).
Two white plates at the left and right ends are reserved for the UT Austin and Oden
Institute logos and currently show only a faint institution name. The band ends with the
take-home sentence in a warm peach tone: "Cardiac imaging and polygenic risk capture
complementary information about future CAD, improving risk stratification beyond clinical
variables in UK Biobank."

## Findings strip
Three numbered statements across the width, each with a headline number in its group colour:
1. "Cardiac MRI carries the imaging signal", AUC 0.77 vs 0.67 (teal).
2. "Imaging and genetic risk barely overlap", r = 0.065 (indigo).
3. "Combining them sharpens who is at risk", C-index 0.819 vs 0.749 (burnt orange).

## Column 1: How the study was built

**Four large numerals.** 42,351 participants; 677 incident CAD cases (1.6% observed event
proportion); 4.6 years median follow-up with a 5-year risk horizon; 75/25 split
(31,754 training with 499 events; 10,597 held-out with 178 events).

**Confluence diagram, "Three data streams, one model".** Three coloured source cards on the
left (Imaging, teal; Genetics, indigo; Clinical, slate), each with a short description,
connected by curved ribbons in the same colours that converge on a single orange-outlined
box, "Joint models": Cox time-to-event models (5-year risk) and tree-based classifiers on
the combined feature table, imaging centre as a covariate; an "Evaluation" line at the
bottom notes the held-out test set keeps the observed event rate and a leave-one-centre-out
check across four imaging centres.

**Representation benchmark, two horizontal bars.** AUC axis 0.50 to 0.85. Conventional
imaging-derived phenotypes (grey) 0.666; learned imaging embeddings (teal) 0.770.

## Column 2: Imaging and genetics see different risk

**Hero hexbin plot (vector).** Density of participants by polygenic risk score (x, SD units,
-4 to 4) against imaging risk score (y, SD units). About 1,260 hexagonal cells form a
roughly circular cloud centred on the origin, coloured on a single-hue ramp from pale
blue-grey (1 participant) to deep navy (100 or more), with a dark red fitted line that is
almost flat and rises very slightly. Lead sentence above: r = 0.065; the two scores share
0.4% of their variance (n = 29,075, training partition). Caption below: low overlap
supports complementarity but does not establish biological independence; genetics explains
0.15% of the imaging risk score, demographics 38.4%.

**C-index ladder.** Four horizontal lollipops on an axis from 0.70 to 0.85 with a dashed
reference line at the clinical value: Clinical 0.749 (slate circle); Clinical + PRS 0.788
(indigo square, "alternative addition to the baseline", +0.039); Clinical + imaging 0.813
(teal triangle, same label, +0.064); Clinical + PRS + imaging 0.819 (orange diamond, "full
model: both additions", +0.070). Caption: nested Cox models, held-out test set, differences
are absolute, no confidence intervals reported, calibration slopes 0.99 to 1.08.

**Chip panel.** "Largest loss of explained variance when removed": long-axis cardiac MRI,
medication history, polygenic risk score, aortic distensibility MRI. "Little loss after
clinical adjustment": liver MRI, pancreas MRI, whole-body DXA, blood-flow MRI.

## Column 3: Combined models find the highest-risk people

**Incidence staircase.** Three rising bars of 5-year CAD incidence: Tier 1 (slate, top third
by clinical-model risk) 8.0%; Tier 2 (indigo, within Tier 1, top third by PRS) 11.3%;
Tier 3 (teal, within Tier 2, top third by imaging risk) 15.9%. A dashed line at 1.6% marks
the crude observed event proportion of the full cohort. Caption adds that the top
within-tier quintile of both PRS and imaging risk inside Tier 3 reached 36.8%, with
stratum size and confidence interval not reported.

**Centre robustness, two small dot panels.** Rows: Reading (71 / 7,607), Cheadle
(409 / 21,942), Bristol (82 / 3,307), Newcastle (115 / 8,740). AUC (navy circles):
0.805, 0.822, 0.785, 0.795. C-index (orange squares): 0.762, 0.748, 0.751, 0.732. Both
axes run 0.70 to 0.85. Caption: site-analysis models, different feature set and validation
design, not external validation.

**Three stat tiles.** Continuous NRI 0.634 (95% CI 0.534 to 0.734), full vs clinical; index
of prediction accuracy 5.5 to 9.5%; calibration slopes 0.99 to 1.08.

**Conclusion and limitations.** Short conclusion paragraph and five bullet limitations.

## Footer
Data and code (UK Biobank application 65439; GitHub code repository, code only; genome-wide
PRS with no gene-level discovery claims), a QR code and DOI for the earlier medRxiv preprint,
acknowledgements, and disclosures.
