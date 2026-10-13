# Figure asset provenance

## Fig. 3c hexbin (poster hero figure)

Source: `assets/Figure3.png` in this repository (3200 x 4000 px PNG; same values as the
manuscript's Fig. 3c: r = 0.065, rho = 0.057, R2 = 0.004, n = 29,075).

Step 1 (design v1-v2): lossless crop of the interior of panel c's plot frame,
`fig3c_hexbin_plotarea.png` (819 x 658 px), and of the colour bar, `fig3c_colorbar.png`.

Step 2 (design v3): **vector transcription** of the crop with `tools/hexbin_transcribe.py`:

* The hexagon lattice was detected from the 2-D autocorrelation of the edge map:
  cell width 12.01 px, row spacing 15.23 px (pointy-top hexagons, 20.3 px tall; the
  vertical stretch reflects the different pixel scales of the two axes), alternate rows
  offset by half a width. The lattice phase was chosen by maximising within-cell colour
  uniformity.
* Each cell's colour was read as the median of the pixels inside an inscribed disc
  (pixels of the red fitted line excluded; the few cells fully hidden under the line take
  the mean of their neighbours). Cells whose median is background white were left empty.
  Result: 1,261 filled cells, stored in `fig3c_hexcells.json` with pixel coordinates.
* The fitted line was recovered by least squares on the red pixels (end points at the
  first and last red column; stroke 8 px).
* Fidelity check: re-rendering the transcription at the original pixel size and comparing
  it with the crop gives 95.1% of all pixels (91.3% of hex pixels) within 24/255 per
  channel; the residual is anti-aliased cell edges. Side-by-side image:
  `qa/hexbin_transcription_compare.png`.
* On the poster each cell is drawn as a vector polygon. Colours are **re-mapped
  monotonically**: each cell's position along the original ggplot gradient
  (grey88 -> #2C5F8A, log10 count) is projected and then rendered on the poster's single-hue
  ramp (pale blue-grey -> navy). The log-scale colour-bar ticks (1, 10, 100) are placed at
  the positions measured on the original colour bar (t = 0.022, 0.478, 0.944). No cell
  value, position or count is altered; only the colour map changes.

The raster crops are kept for reference; the poster no longer embeds any raster image.

## Not used
`assets/Figure4.png` in the repository is an earlier 10-year/FRS-based version. Embedded
manuscript images (720-1247 px wide, extracted with PyMuPDF) were inspected and not used.
