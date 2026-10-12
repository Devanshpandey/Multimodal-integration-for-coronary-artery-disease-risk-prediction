#!/usr/bin/env python3
"""Build poster.html and poster.pdf (72 x 36 in, 5184 x 2592 pt).

Usage:  python3 poster/build/build_poster.py [--measure-only]

Pipeline: charts.py (matplotlib → SVG, real text) → HTML template with
inlined SVGs / base64 images → Chromium (Playwright) → poster.pdf.
The post-processing (outlined print file, previews, audits) lives in
render_outputs.py and audit_poster.py.
"""
import base64
import io
import json
import os
import re
import sys

from PIL import Image, ImageFilter
import segno

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

GITHUB_URL = ("https://github.com/Devanshpandey/"
              "Multimodal-integration-for-coronary-artery-disease-risk-prediction")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# ---------------------------------------------------------------- helpers

def b64_png(path, upscale=1):
    """Return a data URI. `upscale` > 1 resamples (Lanczos + mild sharpen) so
    the placed image meets the printer's effective-ppi preflight; the native
    resolution is logged in NOTES.md."""
    im = Image.open(path).convert("RGB")
    if upscale > 1:
        im = im.resize((im.width * upscale, im.height * upscale), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def svg_file(path):
    s = open(path).read()
    i = s.find("<svg")
    return s[i:]


def qr_svg(url, size_pt):
    qr = segno.make(url, error="m")
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=1, border=2, dark="#333f48", light=None, xmldecl=False, svgclass=None, lineclass=None)
    s = buf.getvalue().decode()
    m = re.search(r'width="(\d+)" height="(\d+)"', s)
    w, h = m.group(1), m.group(2)
    s = s.replace(m.group(0), f'width="{size_pt}pt" height="{size_pt}pt" viewBox="0 0 {w} {h}" shape-rendering="crispEdges"', 1)
    i = s.find("<svg")
    return s[i:], qr.version


def fit_svg(svg, width_pt, height_pt):
    """Force an inlined matplotlib SVG to an exact box (pt)."""
    svg = re.sub(r'width="[^"]+"', f'width="{width_pt}pt"', svg, count=1)
    svg = re.sub(r'height="[^"]+"', f'height="{height_pt}pt"', svg, count=1)
    return svg


# ---------------------------------------------------------------- layout constants (pt)
PAGE_W, PAGE_H = 5184, 2592
MARGIN = 72
COL_GAP = 44
COL_W = (PAGE_W - 2 * MARGIN - 3 * COL_GAP) / 4   # 1227
CARD_PAD = 20
INNER = COL_W - 2 * CARD_PAD                        # 1183 (16.4 in)

# chart boxes (pt)
CH = {
    "idp": (INNER, 6.0 * 72),
    "cca": (INNER, 6.0 * 72),
    "pre3d": ((INNER - 20) / 2, 6.0 * 72),
    "pre2d": ((INNER - 20) / 2, 6.0 * 72),
    "hexbin": (8.0 * 72, 8.0 * 72),
    "r2loo": (INNER, 7.0 * 72),
    "uniq": (INNER, 5.8 * 72),
    "cindex": (INNER, 5.0 * 72),
    "tiers": (INNER, 5.0 * 72),
}


def build_charts():
    out = {}
    out["idp"] = charts.idp_vs_embeddings(CH["idp"][0] / 72, CH["idp"][1] / 72)
    out["cca"] = charts.cca(CH["cca"][0] / 72, CH["cca"][1] / 72)
    out["pre3d"] = charts.pretraining_3d(CH["pre3d"][0] / 72, CH["pre3d"][1] / 72)
    out["pre2d"] = charts.pretraining_2d(CH["pre2d"][0] / 72, CH["pre2d"][1] / 72)
    out["hexbin"] = charts.hexbin(CH["hexbin"][0] / 72)
    out["r2loo"] = charts.r2_loo(CH["r2loo"][0] / 72, CH["r2loo"][1] / 72)
    out["uniq"] = charts.unique_variance(CH["uniq"][0] / 72, CH["uniq"][1] / 72)
    out["cindex"] = charts.cindex(CH["cindex"][0] / 72, CH["cindex"][1] / 72)
    out["tiers"] = charts.tiers(CH["tiers"][0] / 72, CH["tiers"][1] / 72)
    for k, (w, h) in CH.items():
        out[k] = fit_svg(out[k], round(w, 2), round(h, 2))
        with open(os.path.join(OUT, "charts", k + ".svg"), "w") as fh:
            fh.write(out[k])
    return out


# ---------------------------------------------------------------- CSS
CSS = """
@font-face{font-family:'Inter Tight';font-weight:700;src:url('../fonts/InterTight-Bold.ttf')}
@font-face{font-family:'Inter Tight';font-weight:800;src:url('../fonts/InterTight-ExtraBold.ttf')}
@font-face{font-family:'Inter';font-weight:400;src:url('../fonts/Inter-Regular.ttf')}
@font-face{font-family:'Inter';font-weight:600;src:url('../fonts/Inter-SemiBold.ttf')}
@font-face{font-family:'Inter';font-weight:700;src:url('../fonts/Inter-Bold.ttf')}
@font-face{font-family:'Source Sans 3';font-weight:400;src:url('../fonts/SourceSans3-Regular.ttf')}
@font-face{font-family:'Source Sans 3';font-weight:600;src:url('../fonts/SourceSans3-SemiBold.ttf')}
@font-face{font-family:'Source Sans 3';font-weight:700;src:url('../fonts/SourceSans3-Bold.ttf')}
@font-face{font-family:'Source Sans 3';font-weight:400;font-style:italic;src:url('../fonts/SourceSans3-Italic-Regular.ttf')}

@page{size:72in 36in;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:5184pt;height:2592pt;background:#fff;color:#333f48;font-family:'Inter',sans-serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
:root{--ink:#333f48;--muted:#4a5660;--img:#bf5700;--extra:#f2b482;--extraedge:#8a3f00;--prs:#0072b2;--clin:#8c8c8c;--comb:#333f48;
  --tile:#f2f4f5;--rule:#c8cdd4}
.page{position:relative;width:5184pt;height:2592pt;padding:82pt __MARGIN__pt 76pt;display:flex;flex-direction:column}

/* ---------- header ---------- */
.hdr{display:grid;grid-template-columns:600pt 1fr 300pt;column-gap:56pt;align-items:start}
.logos{display:flex;flex-direction:column;gap:18pt;padding-top:6pt}
.logos img{display:block}
.titleblock h1{font-family:'Inter Tight';font-weight:700;font-size:112pt;line-height:1.06;letter-spacing:-0.012em}
.authors{font-size:44pt;line-height:1.2;margin-top:12pt}
.authors sup{font-size:26.4pt;line-height:0}
.affil{font-size:30pt;line-height:1.3;color:var(--muted);margin-top:4pt}
.affil sup{font-size:24pt}
.affil .presenter{font-family:'Source Sans 3';font-weight:600;color:var(--img);font-size:30pt}
.qr{display:flex;flex-direction:column;align-items:center;justify-self:end}
.qr svg{display:block}
.qr .url{font-family:'Source Sans 3';font-size:26pt;line-height:1.15;text-align:center;margin-top:8pt}

.tagline{margin-top:6pt;background:var(--ink);color:#fff;font-size:48pt;line-height:1.2;text-align:center;padding:4pt 20pt;border-radius:4pt}
.key{display:flex;justify-content:center;align-items:center;gap:40pt;margin-top:6pt;font-family:'Source Sans 3';font-size:32pt;line-height:1.3}
.key b{font-weight:700}
.key span{display:inline-flex;align-items:center;gap:12pt}
.sw{display:inline-block;width:36pt;height:36pt;border-radius:4pt}
.sw.img{background:var(--img)} .sw.extra{background:var(--extra);border:2.5pt solid var(--extraedge)} .sw.prs{background:var(--prs)}
.sw.clin{background:var(--clin)} .sw.comb{background:var(--comb)}

/* ---------- columns ---------- */
.cols{display:grid;grid-template-columns:repeat(4,__COLW__pt);column-gap:__COLGAP__pt;margin-top:8pt;flex:1 1 auto;min-height:0}
.col{display:flex;flex-direction:column;gap:16pt;min-height:0}
.sechead .bar{background:var(--img);color:#fff;font-size:64pt;font-weight:600;line-height:1.2;padding:0 24pt;letter-spacing:0.01em;border-radius:4pt 4pt 0 0}
.sechead .sub{font-size:44pt;font-weight:600;line-height:1.2;border-bottom:3pt solid var(--ink);padding:0 0 2pt}
.card{background:#fff;border:2pt solid var(--rule);border-radius:8pt;padding:__CARDPAD__pt;position:relative}
.card svg{display:block}
.cap{font-family:'Source Sans 3';font-size:26pt;line-height:1.2;margin-top:6pt}
.cap b{font-weight:700}
.hero{font-family:'Inter Tight';font-weight:800;font-size:92pt;line-height:1.0;letter-spacing:-0.02em;display:block;color:var(--ink)}
.hero.orange{color:var(--img)}
.hero-sub{display:block;font-family:'Source Sans 3';font-size:28pt;line-height:1.2;margin-top:2pt}
h3{font-size:36pt;font-weight:600;line-height:1.2;margin-top:0}
ul,ol{font-size:32pt;line-height:1.2;padding-left:46pt;margin-top:3pt}
li{margin-top:1pt}
ul li::marker{color:var(--img)} ol li::marker{color:var(--img);font-weight:700}

.tiles{display:grid;gap:12pt}
.tile{background:var(--tile);border-top:4pt solid var(--ink);padding:6pt 12pt 8pt}
.tile .n{font-family:'Inter Tight';font-weight:700;font-size:40pt;line-height:1.15;display:block}
.tile .l{font-family:'Source Sans 3';font-size:24pt;line-height:1.2;display:block}
.tiles.six{grid-template-columns:repeat(6,1fr)}
.tiles.twobytwo{grid-template-columns:repeat(2,1fr)}
.tiles.twobytwo .n{font-size:44pt;line-height:1.1}
.tile.row{display:flex;align-items:center;gap:18pt;padding:8pt 16pt}
.tile.row .n{font-size:60pt;line-height:1.1}
.tile.row .l{font-size:24pt}

/* ---------- column 1 pipeline ---------- */
.pipe{display:flex;flex-direction:column;gap:26pt}
.lane{display:grid;grid-template-columns:150pt 1fr;column-gap:14pt;align-items:stretch}
.lane .tag{color:#fff;font-family:'Source Sans 3';font-weight:700;font-size:27pt;line-height:1.15;display:flex;align-items:center;justify-content:center;text-align:center;border-radius:6pt;padding:6pt}
.tag.img{background:var(--img)} .tag.prs{background:var(--prs)} .tag.clin{background:#5e6973}
.lane .body{display:flex;align-items:stretch;gap:14pt}
.box{flex:1;border:2pt solid var(--rule);border-radius:6pt;font-family:'Source Sans 3';font-size:26pt;line-height:1.2;display:flex;align-items:center;justify-content:center;text-align:center;padding:8pt 10pt;min-height:62pt}
.box.img{border-left:8pt solid var(--img)} .box.prs{border-left:8pt solid var(--prs)} .box.clin{border-left:8pt solid var(--clin)}
.box.dark{background:var(--ink);color:#fff;border-color:var(--ink);font-weight:700}
.box.grey{background:var(--tile);font-weight:700}
.arrow{align-self:center;font-size:30pt;color:var(--ink)}
.imgs{display:flex;gap:12pt;align-items:flex-end}
.imgs figure{position:relative;background:#000;border-radius:6pt;overflow:hidden;height:__IMGH__pt}
.imgs img{display:block;height:100%;width:auto}
.imgs figcaption{position:absolute;left:0;right:0;bottom:0;background:rgba(51,63,72,0.80);color:#fff;font-family:'Source Sans 3';font-size:26pt;line-height:1.3;text-align:center;padding:2pt 4pt}
.down{text-align:center;font-size:30pt;line-height:1;color:var(--ink);margin:-2pt 0}
.conv{display:grid;grid-template-columns:1fr;gap:10pt;padding-left:164pt}
.note{font-family:'Source Sans 3';font-size:26pt;line-height:1.3}
.note.it{font-style:italic}
.note b{font-weight:700}

/* ---------- column 1 figure 1 card ---------- */
.fig1row{display:grid;grid-template-columns:auto 1fr;column-gap:20pt;align-items:stretch}
.tiles.vstack{grid-template-columns:1fr;align-content:space-between}
.tiles.vstack .n{font-size:56pt;line-height:1.1}
.tiles.vstack .l{font-size:26pt}

/* ---------- column 3 hexbin card ---------- */
.hexrow{display:grid;grid-template-columns:__HEX__pt 1fr;column-gap:22pt;align-items:start}
.stack{display:flex;flex-direction:column;gap:10pt}
.stack .hero{font-size:92pt}
.stack .lbl{font-family:'Source Sans 3';font-weight:700;font-size:26pt;line-height:1.3;margin-top:6pt}
.stack .tile.row{padding:6pt 16pt}

/* ---------- column 4 hero row ---------- */
.herorow{display:grid;grid-template-columns:1fr 580pt;column-gap:24pt;align-items:start}
.foot-hr{font-family:'Source Sans 3';font-size:26pt;line-height:1.3;margin-top:6pt}
.loo{font-family:'Source Sans 3';font-size:26pt;line-height:1.3;margin-top:8pt}
.sidepanels{display:grid;grid-template-columns:1fr 1fr;column-gap:20pt}

"""


# ---------------------------------------------------------------- HTML
def build_html(ch):
    cardiac, cardiac_sz = b64_png(os.path.join(ROOT, "images", "cardiac_cine_mri.png"))
    abdominal, abd_sz = b64_png(os.path.join(ROOT, "images", "abdominal_mri.png"), upscale=3)
    dxa, dxa_sz = b64_png(os.path.join(ROOT, "images", "dxa.png"), upscale=3)
    ut = svg_file(os.path.join(ROOT, "images", "logo_ut.svg"))
    oden = svg_file(os.path.join(ROOT, "images", "logo_oden.svg"))
    qr, qr_version = qr_svg(GITHUB_URL, 200)
    fig1, fig1_sz = b64_png(os.path.join(ROOT, "images", "figure1_manuscript.png"))
    FIG1_W = round(fig1_sz[0] / 150 * 72)  # width that keeps the native PNG at 150 ppi
    hex_pt = CH["hexbin"][0]
    IMGH = 300

    css = (CSS.replace("__MARGIN__", str(MARGIN)).replace("__COLW__", f"{COL_W:.2f}")
           .replace("__COLGAP__", str(COL_GAP)).replace("__CARDPAD__", str(CARD_PAD))
           .replace("__IMGH__", str(IMGH)).replace("__HEX__", f"{hex_pt:.0f}"))

    ut = re.sub(r'<svg ', '<svg width="600pt" height="167pt" preserveAspectRatio="xMinYMin meet" ', ut, count=1)
    oden = re.sub(r'<svg ', '<svg width="540pt" height="123pt" preserveAspectRatio="xMinYMin meet" ', oden, count=1)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ASHG poster — Pandey et al.</title>
<style>{css}</style></head>
<body><div class="page">

<header class="hdr">
  <div class="logos">{ut}{oden}</div>
  <div class="titleblock">
    <h1>Multimodal integration reveals complementary imaging and genetic predictors of coronary artery disease risk</h1>
    <div class="authors">Devansh Pandey<sup>1*</sup>, Liaoyi Xu<sup>1</sup>, Eucharist Kun<sup>1</sup>, Chenfei Li<sup>1</sup>, Joyce Y. Wang<sup>1</sup>, Alaa Melek<sup>2</sup>, Julie C. DiCarlo<sup>3,5</sup>, Edward Castillo<sup>2</sup>, Jagat Narula<sup>4</sup>, Charles A. Taylor<sup>3,5</sup>, Vagheesh M. Narasimhan<sup>1,3,6</sup></div>
    <div class="affil"><sup>1</sup>Integrative Biology · <sup>2</sup>Biomedical Engineering · <sup>3</sup>Oden Institute for Computational Engineering and Sciences · <sup>5</sup>Internal Medicine, Dell Medical School · <sup>6</sup>Statistics and Data Sciences — The University of Texas at Austin · <sup>4</sup>UT Health Science Center, Houston &nbsp;&nbsp; <span class="presenter">*Presenter: Devansh Pandey · [email placeholder]</span></div>
  </div>
  <div class="qr">{qr}<div class="url">github.com/Devanshpandey/<br>Multimodal-integration-for-<br>coronary-artery-disease-risk-prediction</div></div>
</header>

<div class="tagline">Cardiac MRI embeddings and polygenic risk capture independent CAD risk — combining them identifies a subgroup with ≈23× the cohort event rate.</div>
<div class="key"><b>Colour key</b>
  <span><i class="sw img"></i>imaging (cardiac MRI)</span>
  <span><i class="sw extra"></i>extra-cardiac imaging</span>
  <span><i class="sw prs"></i>genetics (PRS)</span>
  <span><i class="sw clin"></i>clinical / guideline scores</span>
  <span><i class="sw comb"></i>combined model</span>
</div>

<main class="cols">

<!-- ================= column 1 ================= -->
<section class="col" id="col1">
  <div class="sechead"><div class="bar">WHY &amp; HOW</div><div class="sub">UK Biobank imaging cohort, three data domains, one model</div></div>
  <div class="body-text">
    <h3>Background &amp; questions</h3>
    <ul>
      <li>Leading cause of death; ~50% of CAD first presents as a heart attack.</li>
      <li>Clinical scores omit genetics and imaging; how much imaging and genetic risk overlap was unknown.</li>
    </ul>
    <ol>
      <li>Which imaging modalities add to clinical, metabolic, ECG and genetic factors?</li>
      <li>Overlap between imaging-derived and polygenic risk</li>
      <li>Sequential integration: discrimination, calibration, stratification</li>
    </ol>
  </div>

  <div class="card fig1-card">
    <div class="fig1row">
      <img src="{fig1}" alt="Figure 1 of the manuscript: multimodal framework for longitudinal CAD risk assessment" style="width:{FIG1_W}pt;height:auto;display:block">
      <div class="tiles vstack">
        <div class="tile"><span class="n">42,351</span><span class="l">UK Biobank imaging participants</span></div>
        <div class="tile"><span class="n">677</span><span class="l">incident CAD (1.6%)</span></div>
        <div class="tile"><span class="n">4.6 yr</span><span class="l">median follow-up</span></div>
        <div class="tile"><span class="n">211,755</span><span class="l">cardiac cine MRI series</span></div>
        <div class="tile"><span class="n">127,053</span><span class="l">2D images (liver, pancreas, DXA)</span></div>
        <div class="tile"><span class="n">10,597</span><span class="l">held-out test set (178 cases)</span></div>
      </div>
    </div>
    <p class="note it" style="margin-top:12pt">Cardiac MRI does not image coronary atherosclerosis; its signal reflects remodeling, vascular stiffness and cardiometabolic burden.</p>
    <p class="note" style="margin-top:6pt"><b>Outcome = clinically recognized CAD</b> (MI, angina, revascularization); prevalent cases excluded. Fig. 1 of the manuscript: three data domains → tabular features → classification and Cox survival models.</p>
  </div>

  <div class="body-text">
    <h3>Methods in brief</h3>
    <ul>
      <li>Encoders fine-tuned on balanced case–control training data only.</li>
      <li>Embeddings → PCA, 10 PCs per stream (80 total).</li>
      <li>PRS-CS, European meta-GWAS: OR 1.87 per SD, AUC 0.766 (with age, sex, 20 PCs).</li>
      <li>XGBoost + nested Cox; imaging risk score = cross-fitted ridge Cox.</li>
    </ul>
  </div>
</section>

<!-- ================= column 2 ================= -->
<section class="col" id="col2">
  <div class="sechead"><div class="bar">IMAGING REPRESENTATIONS</div><div class="sub">Deep embeddings beat handcrafted cardiac phenotypes</div></div>
  <div class="card">
    <span class="hero orange">0.770 vs 0.666</span>
    <span class="hero-sub">AUC, deep embeddings vs conventional imaging-derived phenotypes (IDPs); both combined 0.775</span>
    {ch['idp']}
    <p class="cap"><b>Embeddings outperform IDPs; adding IDPs barely helps</b> (logistic models; performance plateaus at ~5 PCs per modality; Fig. 2a,b).</p>
  </div>
  <div class="card">
    {ch['cca']}
    <p class="cap"><b>Embeddings encode physiology:</b> CV1 loads on stroke volume, ejection fraction, myocardial mass and wall thickness (Fig. 2c).</p>
  </div>
  <div class="card">
    <div class="sidepanels">{ch['pre3d']}{ch['pre2d']}</div>
    <p class="cap"><b>Medical pretraining wins:</b> Med3D for the cardiac 3D encoders, RadImageNet for liver, pancreas and DXA (axes from 0.50 / 0.45; Supp. Fig. 3b, 4b).</p>
  </div>
</section>

<!-- ================= column 3 ================= -->
<section class="col" id="col3">
  <div class="sechead"><div class="bar">IMAGING VS GENETICS</div><div class="sub">Imaging and genetic risk are nearly independent</div></div>
  <div class="card">
    <div class="hexrow">
      {ch['hexbin']}
      <div class="stack">
        <span class="hero">r ≈ 0.05</span>
        <span class="hero-sub">Pearson r, imaging vs polygenic risk score (ρ = 0.057); R² &lt; 1% shared — the two overlap very little (n = 29,075; Fig. 3c–e).</span>
        <div class="lbl">Partial R² of imaging risk explained by</div>
        <div class="tile row"><span class="n">0.15%</span><span class="l">genetics (PRS)</span></div>
        <div class="tile row"><span class="n">38.4%</span><span class="l">demographics</span></div>
        <div class="tile row"><span class="n">14.4%</span><span class="l">clinical factors</span></div>
      </div>
    </div>
  </div>
  <div class="card">
    {ch['r2loo']}
    <p class="cap"><b>Cardiac imaging, medication and PRS are each non-redundant.</b> Left: R² of each group alone; right: R² drop when the group is removed from the full model (Fig. 3a,b).</p>
  </div>
  <div class="card">
    {ch['uniq']}
    <p class="cap"><b>Only long-axis, aortic distensibility MRI and PRS retain unique variance</b> after clinical adjustment (Fig. 3f).</p>
  </div>
</section>

<!-- ================= column 4 ================= -->
<section class="col" id="col4">
  <div class="sechead"><div class="bar">INTEGRATION &amp; STRATIFICATION</div><div class="sub">Sequential integration finds very-high-risk people</div></div>
  <div class="herorow">
    <div>
      <span class="hero" id="hero368">36.8%</span>
      <span class="hero-sub">5-yr CAD incidence, top quintile of both imaging and genetic risk within Tier 3; cohort 1.6%</span>
    </div>
    <div class="tiles twobytwo">
      <div class="tile"><span class="n">0.634</span><span class="l">continuous NRI vs clinical (95% CI 0.534–0.734)</span></div>
      <div class="tile"><span class="n">9.5%</span><span class="l">prediction accuracy (IPA), full model; clinical 5.5%</span></div>
      <div class="tile"><span class="n">86.8 yr</span><span class="l">median heart age, Tier 3; cohort 55.3 yr</span></div>
      <div class="tile"><span class="n">0.99–1.08</span><span class="l">calibration slopes, nested models</span></div>
    </div>
  </div>
  <div class="card">
    {ch['cindex']}
    <p class="cap"><b>Each layer adds discrimination; imaging is among the strongest independent predictors (HR ≈ 2.1 per SD).</b> Held-out C-index; axis from 0.55; bold = nested. HR per SD, full model: imaging ≈ 2.1, PRS ≈ 1.7, demographics ≈ 1.4, lipids ≈ 1.1. †PRS alone = score without age/sex; AUC 0.766 (column 1) includes age, sex, 20 PCs.</p>
  </div>
  <div class="card">
    {ch['tiers']}
    <p class="cap"><b>Sequential tiers enrich risk far beyond clinical stratification</b> (5-yr incidence, held-out set). Leave-one-centre-out: AUC 0.785–0.822, C-index 0.73–0.76; discrimination is stable across the four UK Biobank imaging centres (site-level robustness, not external validation).</p>
  </div>
  <div class="body-text">
    <h3>Conclusions</h3>
    <ul>
      <li>Imaging and polygenic risk are nearly uncorrelated: complementary axes.</li>
      <li>Long-axis cine and aortic distensibility MRI carry the incremental signal; blood-flow, liver, pancreas and DXA add little once clinical variables are included.</li>
      <li>Clinical → PRS → imaging integration isolates a 36.8% 5-yr-risk subgroup.</li>
      <li>A framework for complementary risk — not yet a clinical screening tool.</li>
    </ul>
  </div>
  <div class="body-text">
    <h3>Limitations</h3>
    <ul>
      <li>No CAC/CTA in UK Biobank: no calcium-score benchmark.</li>
      <li>European-ancestry, complete-case, healthier-than-general cohort; covariates measured at imaging, so part of imaging's gain may reflect temporal proximity.</li>
      <li>Not externally validated; observational — prospective trials needed.</li>
    </ul>
  </div>
</section>

</main>

<!-- footer removed: data/code, ethics, disclosures and references live in the GitHub repository reached by the QR code -->

</div></body></html>
"""
    meta = {"qr_version": qr_version, "fig1_px": fig1_sz, "fig1_w_pt": FIG1_W, "img_native": {"cardiac": cardiac_sz, "abdominal_x3": abd_sz, "dxa_x3": dxa_sz}}
    return html, meta


MEASURE_JS = """
() => {
  const pt = x => Math.round(x * 72 / 96 * 10) / 10;
  const out = {};
  for (const id of ['col1','col2','col3','col4']) {
    const el = document.getElementById(id);
    const r = el.getBoundingClientRect();
    let maxBottom = 0;
    for (const c of el.children) { maxBottom = Math.max(maxBottom, c.getBoundingClientRect().bottom); }
    out[id] = {top: pt(r.top), bottom: pt(r.bottom), content_bottom: pt(maxBottom), overflow_pt: pt(maxBottom - r.bottom)};
  }
  const f = document.querySelector('footer');
  out.footer = f ? {top: pt(f.getBoundingClientRect().top), bottom: pt(f.getBoundingClientRect().bottom)} : null;
  const h = document.querySelector('.hdr').getBoundingClientRect();
  out.header = {top: pt(h.top), bottom: pt(h.bottom)};
  out.page = {h: pt(document.querySelector('.page').getBoundingClientRect().height)};
  out.cols_top = pt(document.querySelector('.cols').getBoundingClientRect().top);
  return out;
}
"""


def render_pdf(html_path, pdf_path, measure_only=False):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.goto("file://" + html_path, wait_until="load")
        pg.evaluate("document.fonts.ready")
        m = pg.evaluate(MEASURE_JS)
        print(json.dumps(m, indent=1))
        if not measure_only:
            pg.pdf(path=pdf_path, width="72in", height="36in", print_background=True,
                   prefer_css_page_size=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        b.close()
    return m


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "charts"), exist_ok=True)
    ch = build_charts()
    html, meta = build_html(ch)
    html_path = os.path.join(OUT, "poster.html")
    with open(html_path, "w") as fh:
        fh.write(html)
    with open(os.path.join(OUT, "build_meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)
    pdf_path = os.path.join(ROOT, "poster.pdf")
    render_pdf(html_path, pdf_path, measure_only="--measure-only" in sys.argv)
    print("wrote", pdf_path)
