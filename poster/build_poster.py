#!/usr/bin/env python3
"""Build the ASHG 2026 poster (72 x 36 in landscape, single page, vector) with ReportLab.

Usage:  python build_poster.py [--out output/ASHG2026_Devansh_Pandey_Poster_72x36.pdf]

Every number is read from data/numbers.json; copy is defined in this file so that the
word budget and layout can be reviewed together. Figures are drawn as vector objects
(poster_lib/charts.py); the only raster elements are the Fig. 3c hexbin interior and its
colour bar (see assets/figures/PROVENANCE.md) and, if supplied, PNG logos.
"""
import argparse
import json
import sys
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import white

sys.path.insert(0, str(Path(__file__).resolve().parent))
from poster_lib import style as S  # noqa: E402
from poster_lib.text import ST, Column, draw_para, draw_text, string_w, fit_font_size, pstyle, para_height  # noqa: E402
from poster_lib import charts as C  # noqa: E402
from poster_lib.qr import draw_qr  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402

ROOT = Path(__file__).resolve().parent
IN = S.IN


def Y(top_in):
    """Convert 'inches from the top edge' to a PDF y coordinate (points)."""
    return S.PAGE_H - top_in * IN


def fmt_int(n):
    return f"{n:,}"


# ==========================================================================
# POSTER COPY (word-budgeted). Numbers are injected from numbers.json.
# ==========================================================================
TITLE = "Multimodal integration reveals complementary imaging and genetic predictors of coronary artery disease risk"
TAKEHOME = ("Cardiac imaging and polygenic risk capture complementary information about future CAD, "
            "improving risk stratification beyond clinical variables in UK Biobank.")
AUTHORS = ("<b>Devansh Pandey</b><super>1</super>, Liaoyi Xu<super>1</super>, Eucharist Kun<super>1</super>, "
           "Chenfei Li<super>1</super>, Joyce Y. Wang<super>1</super>, Alaa Melek<super>2</super>, "
           "Julie C. DiCarlo<super>3,5</super>, Edward Castillo<super>2</super>, Jagat Narula<super>5</super>, "
           "Charles A. Taylor<super>3,5</super>, Vagheesh M. Narasimhan<super>1,3,6,&#8224;</super>")
AFFILS = ("<super>1</super>Department of Integrative Biology, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>2</super>Department of Biomedical Engineering, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>3</super>Oden Institute for Computational Engineering and Sciences, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>4</super>University of Texas Health Sciences Center, Houston &nbsp;&middot;&nbsp; "
          "<super>5</super>Department of Internal Medicine, Dell Medical School, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>6</super>Department of Statistics and Data Science, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>&#8224;</super>Corresponding author &nbsp;&middot;&nbsp; Presenting author in bold. "
          "Affiliation numbering follows the manuscript title page.")


def build(out_pdf: Path, qa: dict):
    N = json.loads((ROOT / "data" / "numbers.json").read_text())
    coh, prs, rep, comp, disc, strat, cen, sup, adm = (N[k] for k in (
        "cohort", "prs", "representation_benchmark", "complementarity", "discrimination_heldout",
        "stratification_heldout", "center_robustness", "supporting", "admin"))

    S.register_fonts()
    c = canvas.Canvas(str(out_pdf), pagesize=(S.PAGE_W, S.PAGE_H), pageCompression=1,
                      initialFontName=S.FONT, initialFontSize=S.SZ_BODY)
    c.setTitle(TITLE)
    c.setAuthor("Devansh Pandey et al.")
    c.setSubject("ASHG 2026 poster, 72 x 36 in")
    c.setCreator("build_poster.py (ReportLab)")
    c.setKeywords("coronary artery disease; polygenic risk; cardiac MRI; multimodal; UK Biobank")
    # white background (explicit)
    c.setFillColor(white)
    c.rect(0, 0, S.PAGE_W, S.PAGE_H, stroke=0, fill=1)

    words = {}

    # ----------------------------------------------------------------- header
    logo_w, logo_h = 7.5 * IN, 3.3 * IN
    logo_top = 1.15
    ut = C.draw_logo(c, S.MARGIN, Y(logo_top + logo_h / IN), logo_w, logo_h,
                     [ROOT / "assets/logos/ut_austin_logo.svg", ROOT / "assets/logos/ut_austin_logo.png"],
                     "Reserved: official UT Austin university logo (vector). Insert approved asset, see assets/logos/README.md")
    od = C.draw_logo(c, S.PAGE_W - S.MARGIN - logo_w, Y(logo_top + logo_h / IN), logo_w, logo_h,
                     [ROOT / "assets/logos/oden_institute_logo.svg", ROOT / "assets/logos/oden_institute_logo.png"],
                     "Reserved: official Oden Institute logo (vector). Insert approved asset, see assets/logos/README.md")
    qa["logos"] = {"ut_austin": ut, "oden": od}

    title_x = S.MARGIN + logo_w + 0.6 * IN
    title_w = S.PAGE_W - 2 * (S.MARGIN + logo_w + 0.6 * IN)
    # title: fit to two lines
    tsize = S.SZ_TITLE
    while True:
        tst = pstyle("title", size=tsize, font=S.FONT_B, color=S.CHARCOAL, align=TA_CENTER, leading=tsize * 1.1)
        th, tp = para_height(TITLE, title_w, tst)
        if th <= tsize * 1.1 * 2 + 1 or tsize <= 80:
            break
        tsize -= 2
    qa["title_pt"] = tsize
    ty = Y(0.95)
    tp.drawOn(c, title_x, ty - th)
    ay = ty - th - 0.35 * IN
    ah = draw_para(c, AUTHORS, title_x, ay, title_w, ST["authors"])
    fy = ay - ah - 0.22 * IN
    fh = draw_para(c, AFFILS, title_x, fy, title_w, ST["affil"])
    header_bottom_in = (S.PAGE_H - (fy - fh)) / IN
    qa["header_bottom_in"] = round(header_bottom_in, 2)

    # ----------------------------------------------------------- take-home strip
    strip_top = max(6.3, header_bottom_in + 0.3)
    strip_h = 1.5
    sx, sy = S.MARGIN, Y(strip_top + strip_h)
    sw = S.PAGE_W - 2 * S.MARGIN
    c.setFillColor(S.PANEL_BG2)
    c.rect(sx, sy, sw, strip_h * IN, stroke=0, fill=1)
    c.setFillColor(S.BURNT_ORANGE)
    c.rect(sx, sy, 0.28 * IN, strip_h * IN, stroke=0, fill=1)
    lab = "Take-home"
    draw_text(c, lab, sx + 0.6 * IN, sy + strip_h * IN / 2 - S.SZ_TAKEHOME * 0.35, S.FONT_B, S.SZ_TAKEHOME, S.BURNT_ORANGE, "w")
    lw = string_w(lab, S.FONT_B, S.SZ_TAKEHOME) + 0.9 * IN
    tk_w = sw - 0.6 * IN - lw - 0.4 * IN
    tks = fit_font_size(TAKEHOME, S.FONT_SB, tk_w, S.SZ_TAKEHOME, 44)
    draw_text(c, TAKEHOME, sx + 0.6 * IN + lw, sy + strip_h * IN / 2 - tks * 0.35, S.FONT_SB, tks, S.CHARCOAL, "w")
    qa["takehome_pt"] = tks
    words["takehome"] = len(TAKEHOME.split())

    # ------------------------------------------------------------------ body
    body_top = strip_top + strip_h + 0.5
    body_bottom = 33.15
    footer_top = 33.55
    gutter = 0.9 * IN
    avail = S.PAGE_W - 2 * S.MARGIN - 2 * gutter
    fr = (0.29, 0.345, 0.365)
    cw = [avail * f for f in fr]
    cx = [S.MARGIN, S.MARGIN + cw[0] + gutter, S.MARGIN + cw[0] + cw[1] + 2 * gutter]
    cols = [Column(c, cx[i], Y(body_top), cw[i], Y(body_bottom)) for i in range(3)]
    # faint column separators
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    for i in (1, 2):
        xx = cx[i] - gutter / 2
        c.line(xx, Y(body_top), xx, Y(body_bottom))

    # ============================== COLUMN 1 =================================
    k = cols[0]
    k.section("Study design and imaging information")
    q = ("Clinical risk scores use a small set of traditional variables. We asked which imaging modalities add "
         "predictive information for incident coronary artery disease (CAD) once clinical, metabolic, "
         "electrocardiogram (ECG) and genetic risk are accounted for, and how imaging-derived and polygenic "
         "risk relate when measured in the same people.")
    words["c1_question"] = len(q.split())
    k.para(q, gap=0.3 * IN)

    tiles = [
        dict(big=fmt_int(coh["n_total"]["value"]), label="participants, UK Biobank imaging cohort", color=S.CHARCOAL),
        dict(big=fmt_int(coh["n_cases"]["value"]), label=f"incident CAD cases ({coh['event_proportion']['value']}% observed event proportion)", color=S.COL_FULL),
        dict(big=f"{coh['median_follow_up_years']['value']} y", label="median follow-up; 5-year risk horizon", color=S.CHARCOAL),
        dict(big="75 / 25", label=f"training {fmt_int(coh['n_train']['value'])} ({coh['n_train']['cases']} events) / held-out test {fmt_int(coh['n_test']['value'])} ({coh['n_test']['cases']} events)", color=S.CHARCOAL),
    ]
    x, y, w, h = k.reserve(2.3 * IN)
    C.draw_stat_tiles(c, x, y, w, h, tiles, big_size=58)
    k.space(0.35 * IN)

    k.subhead("Multimodal workflow")
    x, y, w, h = k.reserve(7.2 * IN)
    C.draw_workflow(c, x, y, w, h)
    k.space(0.25 * IN)
    m = ("<b>Outcome:</b> clinically recognised CAD from linked hospital and death records (myocardial infarction, "
         "angina or ischaemic heart disease, coronary revascularisation); first event after the imaging visit, "
         "prevalent CAD excluded. Cardiac MRI does not image coronary plaque or calcium. "
         "Encoders were fine-tuned on balanced case&ndash;control sets drawn from the training partition only; every "
         "risk analysis keeps the observed event rate. The polygenic risk score (PRS) was chosen on the training "
         "partition. Analyses are restricted to genetically defined White British participants.")
    words["c1_methods"] = len(m.replace("<b>", "").replace("</b>", "").split())
    k.para(m, ST["caption"], gap=0.4 * IN)

    k.subhead("Learned imaging representations outperform conventional phenotypes")
    rows = [
        dict(label="Conventional imaging-derived phenotypes (IDPs)",
             sub="volumes, ejection fraction, mass, strain, wall thickness, distensibility",
             value=rep["auc_idps"]["value"], color=S.COL_IDP, marker="circle"),
        dict(label="Learned imaging embeddings (10 PCs per view)",
             sub="long-axis and aortic distensibility MRI, CAD-fine-tuned encoders",
             value=rep["auc_embeddings"]["value"], color=S.COL_IMAGING, marker="triangle"),
    ]
    x, y, w, h = k.reserve(5.0 * IN)
    C.draw_dot_plot(c, x, y, w, h, rows, 0.50, 0.85, [0.5, 0.6, 0.7, 0.8], "AUC (representation benchmark, logistic regression)",
                    label_w=w * 0.50)
    cap = ("Reported representation benchmark (Fig. 2b), separate from the held-out Cox analyses. Leading canonical "
           f"components of the embeddings align with stroke volume, ejection fraction and myocardial mass "
           f"(first-component canonical correlations {rep['cca_cv1_r']['range'][0]:.2f}&ndash;{rep['cca_cv1_r']['range'][1]:.2f}), "
           "and the embeddings retain additional predictive signal.")
    words["c1_cap_b"] = len(cap.split())
    k.para(cap, ST["caption"])
    qa["col1_remaining_in"] = round(k.remaining() / IN, 2)

    # ============================== COLUMN 2 =================================
    k = cols[1]
    k.section("Imaging and genetics contribute complementary information")
    intro = ("An imaging risk score (IRS; ridge-penalised Cox model on the 80 imaging principal components, "
             "five-fold cross-fitted) and the PRS both predict CAD, yet they barely overlap.")
    words["c2_intro"] = len(intro.split())
    k.para(intro, gap=0.3 * IN)

    # --- hexbin + callouts
    k.subhead("Weak PRS&ndash;imaging risk correlation; shared variance &lt;1%")
    blk_h = 6.1 * IN
    x, y, w, h = k.reserve(blk_h)
    hex_w = w * 0.50
    info = C.draw_hexbin_panel(c, x, y, hex_w, h, ROOT / "assets/figures/fig3c_hexbin_plotarea.png",
                               ROOT / "assets/figures/fig3c_colorbar.png", "")
    qa["hexbin"] = info
    rx = x + hex_w + 0.3 * IN
    rw = w - hex_w - 0.3 * IN
    big_st = pstyle("big", size=62, font=S.FONT_B, color=S.CHARCOAL, leading=66)
    lab_st = pstyle("biglab", size=S.SZ_CAPTION, color=S.TEXT_MUTED, leading=S.SZ_CAPTION * 1.15)
    yy = y + h - 0.1 * IN
    for big, lab in ((f"r = {comp['pearson_r_figure']['value']:.3f}", "Pearson correlation, PRS vs IRS (Fig. 3c)"),
                     (f"R² = {comp['r2_figure']['value']:.3f}", "shared variance (text summary: R² &lt;1%)"),
                     (f"n = {fmt_int(comp['n_figure']['value'])}", "participants in the plotted training-partition data")):
        hh = draw_para(c, big, rx, yy, rw, big_st)
        yy -= hh
        hh = draw_para(c, lab, rx, yy, rw, lab_st)
        yy -= hh + 0.28 * IN
    note = ("PRS distribution is flat across imaging-risk quintiles (Fig. 3d). Weak overlap supports complementarity; "
            "it does not establish biological independence or show that imaging risk is wholly acquired.")
    words["c2_hex_note"] = len(note.split())
    draw_para(c, note, rx, yy, rw, ST["caption"])
    k.space(0.35 * IN)

    # --- partial R2 bars + chips side by side
    blk_h = 6.35 * IN
    x, y, w, h = k.reserve(blk_h)
    bars_w = w * 0.42
    vd = comp["irs_variance_decomposition"]
    bars = [dict(label="Demographics (age, sex)", value=vd["demographics_partial_r2_pct"]["value"], color=S.COL_CLINICAL),
            dict(label="Clinical risk factors", value=vd["clinical_risk_factors_partial_r2_pct"]["value"], color=S.COL_CLINICAL),
            dict(label="Genetics (PRS)", value=vd["genetics_prs_partial_r2_pct"]["value"], color=S.COL_GENETICS)]
    C.draw_vbars(c, x, y, bars_w, h, bars, 45, "Partial R² (%)", "What explains the imaging risk score? (Fig. 3e)")
    gx = x + bars_w + 0.35 * IN
    gw = w - bars_w - 0.35 * IN
    groups = [
        dict(title="Largest loss of explained variance when removed",
             items=[("Long-axis cardiac MRI", S.COL_IMAGING), ("Medication history", S.COL_CLINICAL),
                    ("Polygenic risk score", S.COL_GENETICS), ("Aortic distensibility MRI", S.COL_IMAGING)]),
        dict(title="Little loss after adjustment for clinical variables",
             items=[("Liver MRI", S.COL_IDP), ("Pancreas MRI", S.COL_IDP), ("Whole-body DXA", S.COL_IDP), ("Blood-flow MRI", S.COL_IDP)],
             note="Qualitative grouping from the manuscript text (Fig. 3b, 3f); values not reproduced."),
    ]
    C.draw_chip_groups(c, gx, y, gw, h, groups, "Which feature groups carry non-redundant information?")
    k.space(0.4 * IN)

    # --- C-index dot plot
    k.subhead(f"Held-out discrimination: full model {disc['full']['value']:.3f} vs clinical {disc['clinical']['value']:.3f} "
              f"(absolute C-index difference {disc['abs_difference_full_minus_clinical']['value']:.3f})")
    rows = [
        dict(label="Clinical", sub="baseline: demographics, lifestyle, medication, lipids, ECG", value=disc["clinical"]["value"], color=S.COL_CLINICAL, marker="circle"),
        dict(label="Clinical + PRS", sub="alternative addition to the clinical baseline", value=disc["clinical_plus_prs"]["value"], color=S.COL_GENETICS, marker="square"),
        dict(label="Clinical + imaging", sub="alternative addition to the clinical baseline", value=disc["clinical_plus_imaging"]["value"], color=S.COL_IMAGING, marker="triangle"),
        dict(label="Clinical + PRS + imaging (full)", sub="both additions", value=disc["full"]["value"], color=S.COL_FULL, marker="diamond"),
    ]
    x, y, w, h = k.reserve(6.2 * IN)
    C.draw_dot_plot(c, x, y, w, h, rows, 0.50, 0.85, [0.5, 0.6, 0.7, 0.8], "Harrell's C-index, held-out test set (5-year horizon)",
                    label_w=w * 0.40)
    cap = (f"Nested Cox models on the held-out test set (n = {fmt_int(coh['n_test']['value'])}; {coh['n_test']['cases']} events; "
           "Supp. Fig. 8d). No confidence intervals are reported for these C-indices. "
           f"Calibration slopes {sup['calibration_slope_range']['value'][0]:.2f}&ndash;{sup['calibration_slope_range']['value'][1]:.2f} across all four models.")
    words["c2_cap_d"] = len(cap.split())
    k.para(cap, ST["caption"])
    qa["col2_remaining_in"] = round(k.remaining() / IN, 2)

    # ============================== COLUMN 3 =================================
    k = cols[2]
    k.section("Integrated risk stratification and robustness")
    intro = ("Sequential stratification of the held-out set (Fig. 4e): each tier keeps the top third of the previous tier, "
             "ranked by one risk dimension at a time.")
    words["c3_intro"] = len(intro.split())
    k.para(intro, gap=0.3 * IN)
    tiers = [
        dict(title="Tier 1", rule="Top third by clinical-model risk", big=f"{strat['tier1_5yr_incidence_pct']['value']:.1f}%", color=S.COL_CLINICAL),
        dict(title="Tier 2", rule="Within Tier 1: top third by PRS", big=f"{strat['tier2_5yr_incidence_pct']['value']:.1f}%", color=S.COL_GENETICS),
        dict(title="Tier 3", rule="Within Tier 2: top third by imaging risk score", big=f"{strat['tier3_5yr_incidence_pct']['value']:.1f}%", color=S.COL_IMAGING),
    ]
    x, y, w, h = k.reserve(3.5 * IN)
    C.draw_tier_cards(c, x, y, w, h, tiers)
    k.space(0.25 * IN)
    # subgroup callout
    x, y, w, h = k.reserve(2.25 * IN)
    C.rounded_box(c, x, y, w, h, fill=S.PANEL_BG2, stroke=S.COL_FULL, lw=3, r=16)
    big = f"{strat['tier3_top_quintile_both_5yr_incidence_pct']['value']:.1f}%"
    draw_text(c, big, x + 0.3 * IN, y + h - 0.3 * IN - 60, S.FONT_B, 64, S.COL_FULL, "w")
    bw = string_w(big, S.FONT_B, 64) + 0.6 * IN
    sub = ("<b>Secondary subgroup:</b> within Tier 3, participants in the top quintile of <i>both</i> PRS and imaging risk "
           "(quintiles defined within the tier), 5-year Kaplan&ndash;Meier incidence. Subgroup size and confidence "
           "interval are not reported, so this small stratum needs cautious interpretation. "
           f"Context: the observed event proportion in the full cohort is {coh['event_proportion']['value']}% (crude, not a 5-year estimate).")
    words["c3_subgroup"] = len(sub.split())
    draw_para(c, sub, x + bw, y + h - 0.22 * IN, w - bw - 0.25 * IN, ST["caption"])
    k.space(0.4 * IN)

    # --- centre table
    k.subhead("Leave-one-centre-out evaluation within UK Biobank (not external validation)")
    header = ["Held-out centre", "Test cases / controls", "AUC", "C-index"]
    trows = [[r["held_out_center"], f"{r['test_cases']} / {fmt_int(r['test_controls'])}", f"{r['auc']:.3f}", f"{r['c_index']:.3f}"] for r in cen["rows"]]
    x, y, w, h = k.reserve(2.9 * IN)
    C.draw_table(c, x, y, w, h, header, trows, [0.30, 0.34, 0.18, 0.18], aligns=["w", "c", "c", "c"])
    k.space(0.12 * IN)
    cap = ("Site-analysis models trained on three centres and tested on the fourth (Supp. Table 13). The site feature set "
           f"is not identical to the main full model, so these values are not comparable with the {disc['full']['value']:.3f} above.")
    words["c3_cap_f"] = len(cap.split())
    k.para(cap, ST["caption"], gap=0.28 * IN)

    # --- supporting tiles
    k.subhead("Calibration, reclassification and accuracy (held-out)")
    nri = sup["continuous_nri_full_vs_clinical"]
    tiles = [
        dict(big=f"{nri['value']:.3f}", label=f"continuous NRI, full vs clinical (95% CI {nri['ci95'][0]:.3f}&ndash;{nri['ci95'][1]:.3f})", color=S.COL_FULL),
        dict(big=f"{sup['ipa_clinical_pct']['value']}% → {sup['ipa_full_pct']['value']}%", label="index of prediction accuracy, clinical → full", color=S.COL_FULL),
        dict(big=f"{sup['calibration_slope_range']['value'][0]:.2f}&ndash;{sup['calibration_slope_range']['value'][1]:.2f}".replace("&ndash;", "–"), label="calibration slopes, all nested models", color=S.CHARCOAL),
    ]
    x, y, w, h = k.reserve(1.95 * IN)
    C.draw_stat_tiles(c, x, y, w, h, tiles, big_size=50)
    k.space(0.12 * IN)
    cap = ("Full-model net benefit was highest at 5&ndash;30% threshold probabilities (decision-curve analysis). "
           "Continuous NRI is not the share of people correctly reclassified, and net benefit is not demonstrated patient benefit.")
    words["c3_cap_sup"] = len(cap.split())
    k.para(cap, ST["caption"], gap=0.28 * IN)

    # --- conclusion + limitations
    k.subhead("Conclusion")
    concl = ("Selected cardiac imaging (long-axis cine and aortic distensibility MRI) and genome-wide polygenic risk add "
             "partially non-overlapping information to clinical variables, improving held-out discrimination, calibration "
             "and enrichment of high-incidence subgroups in this cohort.")
    words["c3_conclusion"] = len(concl.split())
    k.para(concl, gap=0.22 * IN)
    k.subhead("Limitations")
    lims = [
        "Selected, complete-case, White British UK Biobank sample; absolute risks may not transport to other settings.",
        "No fully external validation; site robustness is within one cohort.",
        "No coronary calcium or CT-angiography benchmark; cardiac MRI does not image plaque.",
        "Observational prediction: clinical utility, test ordering and cost-effectiveness remain untested.",
        "Extreme-risk strata are small and their precision is not reported.",
    ]
    words["c3_limitations"] = sum(len(l.split()) for l in lims)
    lst = pstyle("lim", size=S.SZ_BODY - 3, leading=(S.SZ_BODY - 3) * 1.18, color=S.TEXT)
    for l in lims:
        k.para("&bull;&nbsp; " + l, lst, gap=6)
    qa["col3_remaining_in"] = round(k.remaining() / IN, 2)

    # ------------------------------------------------------------------ footer
    c.setStrokeColor(S.RULE)
    c.setLineWidth(2)
    c.line(S.MARGIN, Y(footer_top - 0.2), S.PAGE_W - S.MARGIN, Y(footer_top - 0.2))
    fy = Y(footer_top)
    f_h = (S.PAGE_H_IN - 0.75 - footer_top) * IN
    qr_size = 1.55 * IN
    fw_total = S.PAGE_W - 2 * S.MARGIN
    fgap = 0.5 * IN
    fcols = [0.30, 0.23, 0.27, 0.20]
    fws = [(fw_total - 3 * fgap) * f for f in fcols]
    fxs = [S.MARGIN]
    for wdt in fws[:-1]:
        fxs.append(fxs[-1] + wdt + fgap)
    hd = pstyle("fhd", size=S.SZ_CAPTION, font=S.FONT_B, color=S.CHARCOAL, leading=S.SZ_CAPTION * 1.15)
    code_url = adm["code_url"]
    blocks = [
        ("Data and code",
         f"UK Biobank data are available to approved researchers through application (this work: application {adm['ukb_application']}); "
         f"they are not public. Analysis and figure code: <font color='{S.hex_of(S.UT_BLUE)}'>{code_url.replace('https://', '')}</font> "
         "(code only; no participant data or model weights). Genome-wide polygenic risk score; no individual gene-level discovery claims."),
        ("Preprint of an earlier version",
         f"medRxiv doi:{adm['preprint_doi']}<br/>(title and some analyses differ from this version; scan for the record)"),
        ("Acknowledgements",
         "Computing: Texas Advanced Computing Center (Director's Discretionary Fund). D.P.: Outstanding Graduate Research "
         "Fellowship, The Graduate School, UT Austin. V.M.N.: Allen Discovery Center program (Paul G. Allen Frontiers Group, "
         "Paul G. Allen Family Foundation) and Good Systems Fellowship for Ethical AI, UT Austin."),
        ("Disclosures",
         "C.A.T. founded HeartFlow, Inc. and serves on the boards of HeartFlow, Inc. and Ebenbuild GmbH. "
         "The other authors declare no competing interests."),
    ]
    for i, (title, body) in enumerate(blocks):
        x = fxs[i]
        wdt = fws[i]
        hh = draw_para(c, title, x, fy, wdt, hd)
        if i == 1:
            draw_qr(c, adm["preprint_url"], x, fy - hh - 8 - qr_size, qr_size)
            draw_para(c, body, x + qr_size + 0.25 * IN, fy - hh - 8, wdt - qr_size - 0.25 * IN, ST["small"])
            c.linkURL(adm["preprint_url"], (x, fy - hh - 8 - qr_size, x + qr_size, fy - hh - 8), relative=0)
        else:
            draw_para(c, body, x, fy - hh - 8, wdt, ST["small"])
        if i == 0:
            c.linkURL(code_url, (x, fy - f_h, x + wdt, fy), relative=0)
        words[f"footer_{i}"] = len(body.split())

    for i, col in enumerate(cols):
        if col.remaining() < 0:
            raise SystemExit(f"Column {i + 1} overflows the body area by {-col.remaining() / IN:.2f} in")
    c.showPage()
    c.save()
    postprocess(out_pdf, qa)
    qa["words"] = words
    qa["words_total_body"] = sum(v for k2, v in words.items() if not k2.startswith("footer"))
    qa["words_total_all"] = sum(words.values())
    return qa


def postprocess(out_pdf: Path, qa: dict):
    """Set TrimBox = MediaBox (no bleed), document language and XMP metadata with pikepdf."""
    import pikepdf
    with pikepdf.open(str(out_pdf), allow_overwriting_input=True) as pdf:
        page = pdf.pages[0]
        page.TrimBox = page.MediaBox
        page.CropBox = page.MediaBox
        pdf.Root.Lang = pikepdf.String("en-US")
        with pdf.open_metadata() as meta:
            meta["dc:title"] = TITLE
            meta["dc:creator"] = ["Devansh Pandey", "Liaoyi Xu", "Eucharist Kun", "Chenfei Li", "Joyce Y. Wang", "Alaa Melek",
                                  "Julie C. DiCarlo", "Edward Castillo", "Jagat Narula", "Charles A. Taylor", "Vagheesh M. Narasimhan"]
            meta["dc:description"] = "ASHG 2026 poster (72 x 36 in). " + TAKEHOME
        pdf.save(str(out_pdf))
    qa["pdf_boxes"] = {"MediaBox": [float(v) for v in page.MediaBox], "TrimBox": [float(v) for v in page.TrimBox]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "output" / "ASHG2026_Devansh_Pandey_Poster_72x36.pdf"))
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    qa = {}
    build(out, qa)
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "qa" / "build_report.json").write_text(json.dumps(qa, indent=2))
    print(json.dumps(qa, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
