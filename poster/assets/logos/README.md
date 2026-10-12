# Institutional logo assets (NOT included)

The build environment could not reach `umac.utexas.edu`, `brand.utexas.edu` or
`www.oden.utexas.edu` (outbound connections to those hosts are blocked by the
network policy), and no official assets were supplied by the author. The poster
therefore reserves two clearly marked areas in the header. **A placeholder cannot
pass final QA.**

To finish the header, obtain the official files and drop them here with these names
(the build picks the first that exists, SVG preferred, then PNG):

| Slot (header) | Expected file names | Where to get the official asset |
|---|---|---|
| Left, 7.5 in x 3.3 in | `ut_austin_logo.svg` / `ut_austin_logo.png` | UT Austin Brand Center, academic (university) logo, full-colour or burnt-orange-on-white version: https://umac.utexas.edu/brand-center/visual-identity/ (download requires a UT EID) |
| Right, 7.5 in x 3.3 in | `oden_institute_logo.svg` / `oden_institute_logo.png` | Oden Institute branding page: https://www.oden.utexas.edu/connect/branding/ |

Then rebuild (`make` or `python build_poster.py`). Record the source URL, file name and
download date in `docs/SOURCE_AND_QA.md` (section "Logo provenance").

Rules applied by the build: logos are scaled proportionally into the slot (never
stretched), placed on the white background, with at least 0.35 in clear space from the
title block. Check the institution's own clear-space and minimum-size rules after
inserting the files. Do not use an athletics mark, a redrawn or screenshot logo, or a
raster below ~300 ppi at the placed size.
