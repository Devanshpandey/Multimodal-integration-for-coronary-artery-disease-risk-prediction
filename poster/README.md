# ASHG 2026 poster: build bundle

Single-page, 72 x 36 in (landscape) academic poster for
*Multimodal integration reveals complementary imaging and genetic predictors of coronary artery disease risk*.
Everything on the page is generated from code; all numbers come from `data/numbers.json`.

## One-command build

```bash
cd poster
pip install -r requirements.txt      # ReportLab, pikepdf, qrcode, svglib, pypdf, opencv (QA only)
make                                  # = python build_poster.py && python qa_checks.py
```

Outputs (in `output/`):

| File | What it is |
|---|---|
| `ASHG2026_Devansh_Pandey_Poster_72x36.pdf` | 5184 x 2592 pt single page, MediaBox = TrimBox, no bleed, fonts embedded, vector text and charts |
| `ASHG2026_Devansh_Pandey_Poster_preview.png` | 40-dpi raster preview (2880 x 1440 px) |

`qa/qa_report.json` is rewritten on every build (geometry, fonts, image ppi, links, QR decode,
number presence, cap heights, word counts). `qa/grayscale_preview.png` is the colour-vision check.

System tools used by the QA step: `pdffonts`, `pdfimages`, `pdftoppm` (poppler-utils).

## Layout of the bundle

```
poster/
  build_poster.py        page assembly + all poster copy (word-budgeted)
  qa_checks.py           automated checks, preview renders
  poster_lib/style.py    page size, margins, palette, type scale, font registration
  poster_lib/text.py     measured paragraph flow (Column cursor)
  poster_lib/charts.py   vector modules: workflow diagram, dot plots, bars, tier cards, table, logo slots
  poster_lib/qr.py       vector QR code
  data/numbers.json      source-of-truth manifest (value, unit, population, page/panel, uncertainty)
  assets/fonts/          Source Sans 3 (SIL OFL 1.1, licence included)
  assets/figures/        Fig. 3c hexbin interior + colour bar crops (see PROVENANCE.md)
  assets/logos/          EMPTY: drop official UT Austin / Oden Institute files here (see README.md inside)
  docs/SOURCE_AND_QA.md  provenance, issue log, QA results, unresolved items
  docs/ALT_TEXT.md       accessible descriptions of every visual module
```

## Editing

* Change a number: edit `data/numbers.json` (keep the `source` field accurate) and rebuild.
* Change copy: edit the string constants / `k.para(...)` calls in `build_poster.py`.
* Change sizes: `poster_lib/style.py`. The build aborts if any column overflows the body area.
* Insert logos: see `assets/logos/README.md`; rebuild. The build records whether a slot is a
  placeholder (`qa/build_report.json` -> `logos`).

## Status

This is a **review draft**, not a cleared print file: the two institutional logo slots are
placeholders and the author-affiliation mapping needs confirmation (details in
`docs/SOURCE_AND_QA.md`, section "Unresolved items").
