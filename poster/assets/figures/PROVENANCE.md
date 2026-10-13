# Figure asset provenance

| File | Source | Processing | Native pixels | Placed size on poster | Effective DPI |
|---|---|---|---|---|---|
| `fig3c_hexbin_plotarea.png` | `assets/Figure3.png` in this repository (3200 x 4000 px PNG, 200 dpi metadata; same values as manuscript Fig. 3c: r = 0.065, rho = 0.057, R2 = 0.004, n = 29,075) | Lossless crop of the interior of panel c's plot frame (hexagonal bins + fitted line only). No resampling, no colour change. Axis ticks/labels are re-drawn as vector text by the poster build using the ggplot2 default 5 % axis expansion (frame spans -4.4 to +4.4 SD). | 819 x 658 | 6.83 x 5.48 in | 120 (deliberate cap, see docs/SOURCE_AND_QA.md §2) |
| `fig3c_colorbar.png` | same | Lossless crop of the `Count` colour bar gradient (log10 scale, 1 to 100). Tick labels re-drawn as vector text. | 26 x 322 | see `qa/qa_report.json` | n/a (gradient) |

The repository copy of Figure 4 (`assets/Figure4.png`) is an earlier 10-year/FRS-based version and was NOT used.
Embedded manuscript images (extracted with PyMuPDF) are 720-1247 px wide and were not used on the poster.
