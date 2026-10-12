# Accessible descriptions of the poster's visual modules

These descriptions are a fallback for readers of the digital PDF. The PDF produced by
`build_poster.py` is **not tagged** (ReportLab does not emit a structure tree), so this
text is not embedded as `/Alt` attributes. The PDF does carry searchable text in reading
order (header, take-home strip, column 1, column 2, column 3, footer), document language
`en-US`, and XMP title/author/description metadata.

## Header
Title, eleven authors with numbered affiliations (presenter Devansh Pandey in bold;
corresponding author Vagheesh M. Narasimhan marked with a dagger), and two reserved
logo areas (UT Austin, Oden Institute) that currently hold placeholder text.

## Take-home strip
One sentence on a pale orange band with a burnt-orange left bar: "Cardiac imaging and
polygenic risk capture complementary information about future CAD, improving risk
stratification beyond clinical variables in UK Biobank."

## Column 1

**Stat tiles (4).** 42,351 participants; 677 incident CAD cases (1.6% observed event
proportion); 4.6-year median follow-up with a 5-year risk horizon; 75/25 split into
training (31,754; 499 events) and held-out test (10,597; 178 events).

**Multimodal workflow diagram.** Three coloured input boxes on the left, Imaging (teal),
Genetics (blue), Clinical (grey), each with an arrow to a processing box: imaging goes
through CAD-fine-tuned CNN encoders (Med3D 3D ResNet-18, RadImageNet 2D ResNet-50) and
PCA to 10 components per stream (80 in total); genetics goes through a CAD GWAS
meta-analysis (229,724 cases; 1,024,752 controls) to a PRS-CS polygenic score; clinical
data become harmonised covariates. All three feed a single orange-outlined "Joint
modelling" box: Cox time-to-event models (5-year risk) and tree-based classifiers,
evaluated with a participant-level 75/25 spatially stratified split and a
leave-one-centre-out check.

**Representation benchmark dot plot.** Horizontal lollipop chart, AUC axis from 0.50 to
0.85. Conventional imaging-derived phenotypes (grey circle) at 0.666; learned imaging
embeddings (teal triangle) at 0.770. Caption notes this is the Fig. 2b benchmark, separate
from the held-out Cox analyses.

## Column 2

**Hexbin panel (raster, from the manuscript figure).** Scatter density of polygenic risk
score (x, standard-deviation units, -4 to 4) against imaging risk score (y, same units).
A roughly circular blue cloud centred at the origin with a nearly flat dark-red fitted
line sloping very slightly upward. Colour bar: count per hexagon on a log scale from 1
to 100. To the right, three large figures: r = 0.065 (Pearson correlation), R² = 0.004
(shared variance), n = 29,075 (training-partition participants), with a note that PRS is
flat across imaging-risk quintiles and that low overlap does not prove biological
independence.

**Partial R² bar chart.** Three vertical bars for variance of the imaging risk score
explained by demographics (age, sex) 38.41%, clinical risk factors 14.42% and genetics
(PRS) 0.15%; y-axis 0 to 45%.

**Chip panel.** Two grey boxes. "Largest loss of explained variance when removed": long-axis
cardiac MRI, medication history, polygenic risk score, aortic distensibility MRI. "Little
loss after adjustment for clinical variables": liver MRI, pancreas MRI, whole-body DXA,
blood-flow MRI. Labelled as a qualitative grouping from the manuscript text.

**Held-out C-index dot plot.** Four horizontal lollipops on a C-index axis from 0.50 to
0.85: Clinical 0.749 (grey circle); Clinical + PRS 0.788 (blue square, labelled
"alternative addition to the clinical baseline"); Clinical + imaging 0.813 (teal
triangle, same label); Clinical + PRS + imaging (full) 0.819 (orange diamond, "both
additions"). Caption: nested Cox models, held-out test set, no confidence intervals
reported; calibration slopes 0.99 to 1.08.

## Column 3

**Tier cards.** Three equal cards connected by arrows. Tier 1 (grey): top third by
clinical-model risk, 8.0% 5-year CAD incidence. Tier 2 (blue): within Tier 1, top third
by PRS, 11.3%. Tier 3 (teal): within Tier 2, top third by imaging risk score, 15.9%.

**Secondary subgroup callout.** Orange-outlined box: 36.8% five-year Kaplan-Meier
incidence for participants in Tier 3 who are in the top quintile of both PRS and imaging
risk (quintiles defined within the tier); subgroup size and confidence interval not
reported; the full-cohort observed event proportion of 1.6% is given as crude context.

**Leave-one-centre-out table.** Columns: held-out centre, test cases / controls, AUC,
C-index. Reading 71 / 7,607, 0.805, 0.762. Cheadle 409 / 21,942, 0.822, 0.748. Bristol
82 / 3,307, 0.785, 0.751. Newcastle 115 / 8,740, 0.795, 0.732.

**Supporting stat tiles (3).** Continuous NRI 0.634 (95% CI 0.534 to 0.734), full vs
clinical; index of prediction accuracy 5.5% to 9.5%; calibration slopes 0.99 to 1.08.

**Conclusion and limitations.** Short conclusion paragraph and five bullet limitations
(selected White British complete-case sample; no external validation; no coronary calcium
benchmark; observational prediction; small extreme-risk strata).

## Footer
Data and code (UK Biobank application 65439; GitHub code repository, code only; genome-wide
PRS with no gene-level discovery claims), a QR code and DOI for the earlier medRxiv preprint,
acknowledgements (TACC, fellowships), and disclosures (C.A.T. HeartFlow and Ebenbuild).
