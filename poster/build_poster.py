#!/usr/bin/env python3
"""Build the ASHG 2026 poster, design v3 (72 x 36 in landscape, single page, vector) with ReportLab.

Usage:  python build_poster.py [--out output/ASHG2026_Devansh_Pandey_Poster_72x36.pdf]

All numbers come from data/numbers.json. Copy lives in this file so budget and layout are
reviewed together. Every figure is vector; the hexbin is a transcribed vector copy of the
manuscript's Fig. 3c (assets/figures/fig3c_hexcells.json). Logos are drawn from
assets/logos/ when the official files are present.
"""
import argparse
import json
import sys
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.colors import white
from reportlab.lib.enums import TA_CENTER

sys.path.insert(0, str(Path(__file__).resolve().parent))
from poster_lib import style as S  # noqa: E402
from poster_lib.text import ST, Column, draw_para, draw_text, string_w, fit_font_size, pstyle, para_height  # noqa: E402
from poster_lib import charts as C  # noqa: E402
from poster_lib.qr import draw_qr  # noqa: E402

ROOT = Path(__file__).resolve().parent
IN = S.IN


def Y(top_in):
    return S.PAGE_H - top_in * IN


def fmt_int(n):
    return f"{n:,}"


TITLE = "Multimodal integration reveals complementary imaging and genetic predictors of coronary artery disease risk"
TAKEHOME = ("Cardiac imaging and polygenic risk capture complementary information about future CAD, "
            "improving risk stratification beyond clinical variables in UK Biobank.")
AUTHORS = ("<b>Devansh Pandey</b><super>1</super>, Liaoyi Xu<super>1</super>, Eucharist Kun<super>1</super>, "
           "Chenfei Li<super>1</super>, Joyce Y. Wang<super>1</super>, Alaa Melek<super>2</super>, "
           "Julie C. DiCarlo<super>3,5</super>, Edward Castillo<super>2</super>, Jagat Narula<super>5</super>, "
           "Charles A. Taylor<super>3,5</super>, Vagheesh M. Narasimhan<super>1,3,6,&#8224;</super>")
# Mapping copied from the manuscript title page; confirmation pending (docs/SOURCE_AND_QA.md, issue 1).
AFFILS = ("<super>1</super>Department of Integrative Biology, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>2</super>Department of Biomedical Engineering, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>3</super>Oden Institute for Computational Engineering and Sciences, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>4</super>University of Texas Health Sciences Center, Houston &nbsp;&middot;&nbsp; "
          "<super>5</super>Department of Internal Medicine, Dell Medical School, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>6</super>Department of Statistics and Data Science, The University of Texas at Austin &nbsp;&middot;&nbsp; "
          "<super>&#8224;</super>Corresponding author &nbsp;&middot;&nbsp; Presenting author in bold")


def section(k, text):
    """Section heading in the display face with an orange rule."""
    st = pstyle("sec", size=S.SZ_SECTION, font=S.DISPLAY, color=S.INK, leading=S.SZ_SECTION * 1.1)
    h = draw_para(k.c, text, k.x, k.y, k.w, st)
    k.y -= h + 12
    k.c.setStrokeColor(S.BURNT_ORANGE)
    k.c.setLineWidth(6)
    k.c.line(k.x, k.y, k.x + 1.6 * IN, k.y)
    k.y -= 0.35 * IN


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
    c.setFillColor(S.PAPER)
    c.rect(0, 0, S.PAGE_W, S.PAGE_H, stroke=0, fill=1)
    words = {}

    # ================================================================ header band
    band_h = 6.9
    c.setFillColor(S.INK)
    c.rect(0, Y(band_h), S.PAGE_W, band_h * IN, stroke=0, fill=1)
    plate_w, plate_h = 8.0 * IN, 3.4 * IN
    plate_top = 1.0
    for side, cands, label in (("l", ["ut_austin_logo.svg", "ut_austin_logo.png"], "The University of Texas at Austin"),
                               ("r", ["oden_institute_logo.svg", "oden_institute_logo.png"], "Oden Institute for Computational Engineering and Sciences")):
        px = S.MARGIN if side == "l" else S.PAGE_W - S.MARGIN - plate_w
        C.rounded_box(c, px, Y(plate_top + plate_h / IN), plate_w, plate_h, fill=white, r=20)
        res = C.draw_logo(c, px + 0.3 * IN, Y(plate_top + plate_h / IN) + 0.3 * IN, plate_w - 0.6 * IN, plate_h - 0.6 * IN,
                          [ROOT / "assets/logos" / f for f in cands], label)
        qa.setdefault("logos", {})["ut_austin" if side == "l" else "oden"] = res

    title_x = S.MARGIN + plate_w + 0.8 * IN
    title_w = S.PAGE_W - 2 * (S.MARGIN + plate_w + 0.8 * IN)
    tsize = S.SZ_TITLE
    while True:
        tst = pstyle("title", size=tsize, font=S.DISPLAY, color=white, align=TA_CENTER, leading=tsize * 1.08)
        th, tp = para_height(TITLE, title_w, tst)
        if th <= tsize * 1.08 * 2 + 1 or tsize <= 80:
            break
        tsize -= 2
    qa["title_pt"] = tsize
    ty = Y(0.85)
    tp.drawOn(c, title_x, ty - th)
    a_st = pstyle("authors", size=S.SZ_AUTHORS, align=TA_CENTER, color=S.TEXT_ON_INK, leading=S.SZ_AUTHORS * 1.2)
    f_st = pstyle("affil", size=S.SZ_AFFIL, align=TA_CENTER, color=S.TEXT_ON_INK_MUTED, leading=S.SZ_AFFIL * 1.2)
    ay = ty - th - 0.3 * IN
    ah = draw_para(c, AUTHORS, title_x, ay, title_w, a_st)
    fy = ay - ah - 0.18 * IN
    fh = draw_para(c, AFFILS, title_x, fy, title_w, f_st)
    # take-home line across the band bottom
    tk_y = Y(band_h) + 0.55 * IN
    tks = fit_font_size(TAKEHOME, S.FONT_SB, S.PAGE_W - 2 * S.MARGIN - 0.2 * IN, S.SZ_TAKEHOME, 34)
    draw_text(c, TAKEHOME, S.PAGE_W / 2, tk_y, S.FONT_SB, tks, S.HexColor("#F5D4BC"), "c")
    qa["takehome_pt"] = tks
    qa["header_text_bottom_in"] = round((S.PAGE_H - (fy - fh)) / IN, 2)
    words["takehome"] = len(TAKEHOME.split())

    # ============================================================ findings strip
    fs_top = band_h + 0.45
    fs_h = 2.45
    fx = S.MARGIN
    fw = (S.PAGE_W - 2 * S.MARGIN - 2 * 0.9 * IN) / 3
    findings = [
        ("1", "Cardiac MRI carries the imaging signal", f"AUC {rep['auc_embeddings']['value']:.2f} vs {rep['auc_idps']['value']:.2f}",
         "learned embeddings vs conventional phenotypes; long-axis and aortic MRI add most", S.COL_IMAGING),
        ("2", "Imaging and genetic risk barely overlap", f"r = {comp['pearson_r_figure']['value']:.3f}",
         f"imaging risk score vs polygenic score; shared variance {comp['r2_figure']['value'] * 100:.1f}%", S.COL_GENETICS),
        ("3", "Combining them sharpens who is at risk", f"C-index {disc['full']['value']:.3f} vs {disc['clinical']['value']:.3f}",
         f"full vs clinical model; 5-year incidence {strat['tier3_5yr_incidence_pct']['value']:.1f}% in the top tier", S.COL_FULL),
    ]
    head_st = pstyle("fhead", size=S.SZ_FINDING + 4, font=S.FONT_B, color=S.INK, leading=(S.SZ_FINDING + 4) * 1.12)
    sub_st = pstyle("fsub", size=S.SZ_CAPTION, color=S.TEXT_MUTED, leading=S.SZ_CAPTION * 1.15)
    for i, (num, head, big, sub, col) in enumerate(findings):
        x = fx + i * (fw + 0.9 * IN)
        top = Y(fs_top)
        draw_text(c, num, x, top - 84, S.DISPLAY, 96, S.BURNT_ORANGE, "w")
        tx = x + 1.05 * IN
        hh = draw_para(c, head, tx, top - 4, fw - 1.05 * IN, head_st)
        draw_text(c, big, tx, top - hh - 10 - 58, S.DISPLAY, 60, col, "w")
        draw_para(c, sub, tx, top - hh - 10 - 58 - 14, fw - 1.05 * IN, sub_st)
        words[f"finding_{i}"] = len(head.split()) + len(sub.split())
    c.setStrokeColor(S.RULE)
    c.setLineWidth(2)
    c.line(S.MARGIN, Y(fs_top + fs_h), S.PAGE_W - S.MARGIN, Y(fs_top + fs_h))

    # ===================================================================== body
    body_top = fs_top + fs_h + 0.45
    body_bottom = 33.1
    footer_top = 33.5
    gutter = 0.9 * IN
    avail = S.PAGE_W - 2 * S.MARGIN - 2 * gutter
    fr = (0.305, 0.38, 0.315)
    cw = [avail * f for f in fr]
    cx = [S.MARGIN, S.MARGIN + cw[0] + gutter, S.MARGIN + cw[0] + cw[1] + 2 * gutter]
    cols = [Column(c, cx[i], Y(body_top), cw[i], Y(body_bottom)) for i in range(3)]

    # ------------------------------------------------------------- column 1
    k = cols[0]
    section(k, "How the study was built")
    facts = [
        dict(big=fmt_int(coh["n_total"]["value"]), label="UK Biobank participants with cardiac and abdominal MRI, DXA, ECG, genotypes and labs"),
        dict(big=fmt_int(coh["n_cases"]["value"]), label=f"incident CAD cases after the imaging visit ({coh['event_proportion']['value']}% observed event proportion)", color=S.COL_FULL),
        dict(big=f"{coh['median_follow_up_years']['value']} years", label="median follow-up; all risk models target 5-year risk"),
        dict(big="75 / 25", label=f"spatially stratified split: {fmt_int(coh['n_train']['value'])} train ({coh['n_train']['cases']} events) / {fmt_int(coh['n_test']['value'])} held-out ({coh['n_test']['cases']} events)"),
    ]
    x, y, w, h = k.reserve(3.6 * IN)
    C.draw_facts(c, x, y, w, h, facts, cols=2, num_size=60)
    k.space(0.4 * IN)
    k.subhead("Three data streams, one model")
    streams = [
        dict(name="Imaging", sub="8 streams: cardiac cine (3 views), aortic distensibility, blood flow; liver and pancreas MRI; DXA &rarr; CAD-fine-tuned CNN encoders &rarr; 10 PCs per stream (80 total)", color=S.COL_IMAGING),
        dict(name="Genetics", sub=f"CAD GWAS meta-analysis of non-imaged UK Biobank, FinnGen and MVP ({fmt_int(prs['meta_cases']['value'])} cases, {fmt_int(prs['meta_controls']['value'])} controls) &rarr; PRS-CS polygenic score", color=S.COL_GENETICS),
        dict(name="Clinical", sub="Demographics, lifestyle, medication, lipids, 12-lead ECG intervals: imaging-visit measurements, baseline values substituted when unavailable", color=S.COL_CLINICAL),
    ]
    x, y, w, h = k.reserve(8.55 * IN)
    C.draw_confluence(c, x, y, w, h, streams,
                      "Cox time-to-event models (5-year risk) and tree-based classifiers on the combined feature table; imaging centre as a covariate.",
                      "held-out test set keeps the observed event rate; leave-one-centre-out check across four imaging centres.")
    k.space(0.3 * IN)
    m = ("<b>Outcome</b> &nbsp;clinically recognised CAD (myocardial infarction, angina or ischaemic heart disease, "
         "coronary revascularisation) from linked records; prevalent CAD excluded. Cardiac MRI does not image coronary plaque. "
         "Encoders (Med3D 3D ResNet-18 for cardiac MRI; RadImageNet 2D ResNet-50 for liver, pancreas and DXA) were fine-tuned on balanced "
         "case&ndash;control sets from the training partition only; all risk analyses keep the observed event rate. Genetically defined White British participants.")
    words["c1_methods"] = len(m.split())
    k.para(m, ST["caption"], gap=0.3 * IN)
    k.subhead("Learned representations beat conventional phenotypes")
    rows = [
        dict(label="Conventional imaging-derived phenotypes", sub="volumes, ejection fraction, mass, strain, wall thickness, distensibility",
             value=rep["auc_idps"]["value"], color=S.COL_IDP),
        dict(label="Learned imaging embeddings", sub="10 PCs per view; long-axis and aortic distensibility MRI",
             value=rep["auc_embeddings"]["value"], color=S.COL_IMAGING),
    ]
    x, y, w, h = k.reserve(4.0 * IN)
    C.draw_benchmark(c, x, y, w, h, rows, 0.50, 0.85, [0.5, 0.6, 0.7, 0.8], "AUC, representation benchmark (logistic regression)", label_w=w * 0.47)
    cap = (f"Separate from the held-out survival analyses. Leading canonical components of the embeddings align with stroke volume, "
           f"ejection fraction and myocardial mass (canonical correlations {rep['cca_cv1_r']['range'][0]:.2f}&ndash;{rep['cca_cv1_r']['range'][1]:.2f}).")
    words["c1_cap_b"] = len(cap.split())
    k.para(cap, ST["caption"])
    qa["col1_remaining_in"] = round(k.remaining() / IN, 2)

    # ------------------------------------------------------------- column 2
    k = cols[1]
    section(k, "Imaging and genetics see different risk")
    lead = (f"<b>r = {comp['pearson_r_figure']['value']:.3f}.</b> The imaging risk score (ridge Cox model on the 80 imaging PCs, "
            f"five-fold cross-fitted) and the polygenic score share {comp['r2_figure']['value'] * 100:.1f}% of their variance "
            f"(n = {fmt_int(comp['n_figure']['value'])}, training partition). Both predict CAD; they rank different people.")
    words["c2_lead"] = len(lead.split())
    k.para(lead, gap=0.25 * IN)
    x, y, w, h = k.reserve(8.7 * IN)
    hexinfo = C.draw_hexbin_vector(c, x, y, w, h, ROOT / "assets/figures/fig3c_hexcells.json",
                                   "Polygenic risk score (SD)", "Imaging risk score (SD)")
    qa["hexbin_vector"] = hexinfo
    k.space(0.1 * IN)
    cav = ("Low overlap supports complementarity; it does not establish biological independence or show that imaging risk is wholly acquired. "
           f"Genetics explains {comp['irs_variance_decomposition']['genetics_prs_partial_r2_pct']['value']:.2f}% of the imaging risk score; "
           f"demographics explain {comp['irs_variance_decomposition']['demographics_partial_r2_pct']['value']:.1f}%.")
    words["c2_cav"] = len(cav.split())
    k.para(cav, ST["caption"], gap=0.3 * IN)

    k.subhead(f"Held-out discrimination: the full model reaches C-index {disc['full']['value']:.3f}")
    rows = [
        dict(label="Clinical", sub="demographics, lifestyle, medication, lipids, ECG", value=disc["clinical"]["value"], color=S.COL_CLINICAL, marker="circle"),
        dict(label="Clinical + PRS", sub="alternative addition to the baseline", value=disc["clinical_plus_prs"]["value"], color=S.COL_GENETICS, marker="square"),
        dict(label="Clinical + imaging", sub="alternative addition to the baseline", value=disc["clinical_plus_imaging"]["value"], color=S.COL_IMAGING, marker="triangle"),
        dict(label="Clinical + PRS + imaging", sub="full model: both additions", value=disc["full"]["value"], color=S.COL_FULL, marker="diamond"),
    ]
    x, y, w, h = k.reserve(5.6 * IN)
    C.draw_ladder(c, x, y, w, h, rows, 0.70, 0.85, [0.70, 0.75, 0.80, 0.85], "Harrell's C-index, held-out test set, 5-year horizon", label_w=w * 0.33)
    cap = (f"Nested Cox models; n = {fmt_int(coh['n_test']['value'])}, {coh['n_test']['cases']} events. Differences are absolute. "
           f"No confidence intervals reported. Calibration slopes {sup['calibration_slope_range']['value'][0]:.2f}&ndash;{sup['calibration_slope_range']['value'][1]:.2f}.")
    words["c2_cap_d"] = len(cap.split())
    k.para(cap, ST["caption"], gap=0.25 * IN)
    x, y, w, h = k.reserve(2.7 * IN)
    groups = [
        dict(title="Largest loss of explained variance when removed",
             items=[("Long-axis cardiac MRI", S.COL_IMAGING), ("Medication history", S.COL_CLINICAL),
                    ("Polygenic risk score", S.COL_GENETICS), ("Aortic distensibility MRI", S.COL_IMAGING)]),
        dict(title="Little loss after clinical adjustment",
             items=[("Liver MRI", S.COL_IDP), ("Pancreas MRI", S.COL_IDP), ("Whole-body DXA", S.COL_IDP), ("Blood-flow MRI", S.COL_IDP)]),
    ]
    C.draw_chip_groups(c, x, y, w, h, groups)
    qa["col2_remaining_in"] = round(k.remaining() / IN, 2)

    # ------------------------------------------------------------- column 3
    k = cols[2]
    section(k, "Combined models find the highest-risk people")
    intro = ("Sequential stratification of the held-out set: each tier keeps the top third of the previous tier, "
             "with the cut-point recalculated within that tier.")
    words["c3_intro"] = len(intro.split())
    k.para(intro, gap=0.1 * IN)
    tiers = [
        dict(name="Tier 1", rule="top third by clinical-model risk", value=strat["tier1_5yr_incidence_pct"]["value"], color=S.COL_CLINICAL),
        dict(name="Tier 2", rule="within Tier 1, top third by PRS", value=strat["tier2_5yr_incidence_pct"]["value"], color=S.COL_GENETICS),
        dict(name="Tier 3", rule="within Tier 2, top third by imaging risk", value=strat["tier3_5yr_incidence_pct"]["value"], color=S.COL_IMAGING),
    ]
    x, y, w, h = k.reserve(5.6 * IN)
    C.draw_staircase(c, x, y, w, h, tiers, 20, ref=dict(value=coh["event_proportion"]["value"], label=f"{coh['event_proportion']['value']}%"))
    sub = (f"Dashed line: {coh['event_proportion']['value']}% observed event proportion in the full cohort (crude, not a 5-year estimate). "
           f"Within Tier 3, the top within-tier quintile of both PRS and imaging risk reached "
           f"{strat['tier3_top_quintile_both_5yr_incidence_pct']['value']:.1f}% five-year incidence; stratum size and confidence "
           f"interval are not reported.")
    words["c3_subgroup"] = len(sub.split())
    k.para(sub, ST["caption"], gap=0.3 * IN)

    k.subhead("Stable across imaging centres (leave-one-centre-out, within UK Biobank)")
    crow = [dict(name=r["held_out_center"], sub=f"{r['test_cases']} / {fmt_int(r['test_controls'])}", auc=r["auc"], c_index=r["c_index"]) for r in cen["rows"]]
    x, y, w, h = k.reserve(3.7 * IN)
    C.draw_center_dots(c, x, y, w, h, crow, [
        ("auc", "AUC (classifier)", 0.70, 0.85, [0.70, 0.75, 0.80], "circle", S.INK),
        ("c_index", "C-index (Cox)", 0.70, 0.85, [0.70, 0.75, 0.80], "square", S.COL_FULL),
    ])
    cap = ("Rows: held-out centre (test cases / controls). Site-analysis models trained on three centres, tested on the fourth. "
           "Different feature set and validation design from the main held-out analysis; not external validation.")
    words["c3_cap_f"] = len(cap.split())
    k.para(cap, ST["caption"], gap=0.25 * IN)

    nri = sup["continuous_nri_full_vs_clinical"]
    tiles = [
        dict(big=f"{nri['value']:.3f}", label=f"continuous NRI, full vs clinical (95% CI {nri['ci95'][0]:.3f}&ndash;{nri['ci95'][1]:.3f})", color=S.COL_FULL),
        dict(big=f"{sup['ipa_clinical_pct']['value']} to {sup['ipa_full_pct']['value']}%", label="index of prediction accuracy, clinical to full model", color=S.COL_FULL),
        dict(big=f"{sup['calibration_slope_range']['value'][0]:.2f}–{sup['calibration_slope_range']['value'][1]:.2f}", label="calibration slopes, all nested models", color=S.INK),
    ]
    x, y, w, h = k.reserve(1.9 * IN)
    C.draw_stat_tiles(c, x, y, w, h, tiles, big_size=44)
    k.space(0.25 * IN)
    k.subhead("Conclusion")
    concl = ("Selected cardiac imaging (long-axis cine and aortic distensibility MRI) and genome-wide polygenic risk add "
             "partially non-overlapping information to clinical variables, improving discrimination and risk enrichment, "
             "with calibration slopes near 1.")
    words["c3_conclusion"] = len(concl.split())
    k.para(concl, gap=0.2 * IN)
    k.subhead("Limitations")
    lims = [
        "Selected, complete-case, White British UK Biobank sample; absolute risks may not transport.",
        "No fully external validation; site robustness is within one cohort.",
        "No coronary calcium or CT-angiography benchmark; cardiac MRI does not image plaque.",
        "Observational prediction: clinical utility, test ordering and cost-effectiveness untested.",
        "Extreme-risk strata are small and their precision is not reported.",
    ]
    words["c3_limitations"] = sum(len(l.split()) for l in lims)
    lst = pstyle("lim", size=S.SZ_BODY - 5, leading=(S.SZ_BODY - 5) * 1.14, color=S.TEXT)
    for l in lims:
        k.para("&bull;&nbsp; " + l, lst, gap=2)
    qa["col3_remaining_in"] = round(k.remaining() / IN, 2)

    # =================================================================== footer
    c.setStrokeColor(S.INK)
    c.setLineWidth(3)
    c.line(S.MARGIN, Y(footer_top - 0.2), S.PAGE_W - S.MARGIN, Y(footer_top - 0.2))
    fy = Y(footer_top)
    f_h = (S.PAGE_H_IN - 0.75 - footer_top) * IN
    qr_size = 1.5 * IN
    fw_total = S.PAGE_W - 2 * S.MARGIN
    fgap = 0.5 * IN
    fcols = [0.30, 0.22, 0.28, 0.20]
    fws = [(fw_total - 3 * fgap) * f for f in fcols]
    fxs = [S.MARGIN]
    for wdt in fws[:-1]:
        fxs.append(fxs[-1] + wdt + fgap)
    hd = pstyle("fhd", size=S.SZ_CAPTION, font=S.FONT_B, color=S.INK, leading=S.SZ_CAPTION * 1.15)
    code_url = adm["code_url"]
    blocks = [
        ("Data and code",
         f"UK Biobank data are available to approved researchers through application (this work: application {adm['ukb_application']}). "
         f"Analysis and figure code: <font color='{S.hex_of(S.COL_GENETICS)}'>{code_url.replace('https://', '')}</font> "
         "(code only; no participant data or model weights). Genome-wide polygenic risk score; no individual gene-level discovery claims."),
        ("Preprint (earlier version)", f"medRxiv doi:{adm['preprint_doi']}"),
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

    over = [f"column {i + 1}: {col.remaining() / IN:+.2f} in" for i, col in enumerate(cols)]
    if any(col.remaining() < 0 for col in cols):
        raise SystemExit("Body overflow: " + "; ".join(over))
    c.showPage()
    c.save()
    postprocess(out_pdf, qa)
    qa["words"] = words
    qa["words_total_body"] = sum(v for k2, v in words.items() if not k2.startswith("footer"))
    qa["words_total_all"] = sum(words.values())
    return qa


def postprocess(out_pdf: Path, qa: dict):
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
