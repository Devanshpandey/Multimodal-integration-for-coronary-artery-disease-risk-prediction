"""Vector chart and diagram modules drawn directly on the ReportLab canvas.

Every function takes a box (x, y_bottom, w, h) in points and draws inside it.
No participant-level data are synthesised; all values come from data/numbers.json.
"""
import math
from pathlib import Path
from reportlab.lib.colors import Color, white, black
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from . import style as S
from .text import draw_text, draw_para, string_w, ST, pstyle, para_height

IN = S.IN


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------
def rounded_box(c, x, y, w, h, fill=None, stroke=None, lw=2, r=18):
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
    c.roundRect(x, y, w, h, r, stroke=1 if stroke is not None else 0, fill=1 if fill is not None else 0)


def arrow(c, x1, y1, x2, y2, color=S.TEXT_MUTED, lw=4, head=18):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)
    ang = math.atan2(y2 - y1, x2 - x1)
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
    p.lineTo(x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def draw_marker(c, shape, x, y, r, color):
    c.setFillColor(color)
    c.setStrokeColor(white)
    c.setLineWidth(3)
    if shape == "circle":
        c.circle(x, y, r, stroke=1, fill=1)
    elif shape == "square":
        c.rect(x - r, y - r, 2 * r, 2 * r, stroke=1, fill=1)
    elif shape == "triangle":
        p = c.beginPath()
        p.moveTo(x, y + r * 1.15)
        p.lineTo(x - r * 1.1, y - r * 0.8)
        p.lineTo(x + r * 1.1, y - r * 0.8)
        p.close()
        c.drawPath(p, stroke=1, fill=1)
    elif shape == "diamond":
        p = c.beginPath()
        p.moveTo(x, y + r * 1.25)
        p.lineTo(x + r * 1.25, y)
        p.lineTo(x, y - r * 1.25)
        p.lineTo(x - r * 1.25, y)
        p.close()
        p.close()
        c.drawPath(p, stroke=1, fill=1)


def panel_title(c, x, y_top, w, text, size=S.SZ_SUBHEAD):
    st = pstyle("ptitle", size=size, font=S.FONT_SB, color=S.CHARCOAL, leading=size * 1.15)
    return draw_para(c, text, x, y_top, w, st)


# --------------------------------------------------------------------------
# Module A: workflow diagram
# --------------------------------------------------------------------------
def draw_workflow(c, x, y, w, h):
    """Three input branches -> representation -> common modelling -> evaluation."""
    col_w = [w * 0.27, w * 0.39, w * 0.28]
    gap = (w - sum(col_w)) / 2
    xs = [x, x + col_w[0] + gap, x + col_w[0] + gap + col_w[1] + gap]
    row_h = (h - 2 * 0.22 * IN) / 3
    rows_y = [y + h - row_h, y + h - 2 * row_h - 0.22 * IN, y + h - 3 * row_h - 0.44 * IN]

    branches = [
        dict(name="Imaging", sub="8 streams: cardiac cine (3 views), aortic distensibility, blood flow; liver, pancreas MRI; DXA",
             col=S.COL_IMAGING, bg=S.HexColor("#E3F3F5"),
             proc="CAD-fine-tuned CNN encoders (Med3D 3D ResNet-18; RadImageNet 2D ResNet-50) &rarr; PCA: 10 components per stream, 80 in total"),
        dict(name="Genetics", sub="Genome-wide genotypes",
             col=S.COL_GENETICS, bg=S.HexColor("#E2EEF4"),
             proc="CAD GWAS meta-analysis of non-imaged UK Biobank, FinnGen and MVP (229,724 cases; 1,024,752 controls) &rarr; PRS-CS polygenic risk score"),
        dict(name="Clinical", sub="Demographics, lifestyle, medication, lipids, 12-lead ECG intervals",
             col=S.COL_CLINICAL, bg=S.HexColor("#EEF0F2"),
             proc="Harmonised covariates measured at the imaging visit (standardised; imaging centre included as a covariate)"),
    ]
    name_st = pstyle("wf_name", size=S.SZ_LABEL + 2, font=S.FONT_B, color=white, leading=(S.SZ_LABEL + 2) * 1.15)
    sub_st = pstyle("wf_sub", size=S.SZ_CAPTION - 1, color=white, leading=(S.SZ_CAPTION - 1) * 1.18)
    proc_st = pstyle("wf_proc", size=S.SZ_CAPTION, color=S.CHARCOAL, leading=S.SZ_CAPTION * 1.2)
    for b, ry in zip(branches, rows_y):
        # input box
        rounded_box(c, xs[0], ry, col_w[0], row_h, fill=b["col"])
        pad = 16
        hh = draw_para(c, b["name"], xs[0] + pad, ry + row_h - pad, col_w[0] - 2 * pad, name_st)
        draw_para(c, b["sub"], xs[0] + pad, ry + row_h - pad - hh - 6, col_w[0] - 2 * pad, sub_st)
        # processing box
        rounded_box(c, xs[1], ry, col_w[1], row_h, fill=b["bg"], stroke=b["col"], lw=3)
        _, p = para_height(b["proc"], col_w[1] - 2 * pad, proc_st)
        ph = p.wrap(col_w[1] - 2 * pad, 10000)[1]
        p.drawOn(c, xs[1] + pad, ry + (row_h - ph) / 2)
        arrow(c, xs[0] + col_w[0] + 4, ry + row_h / 2, xs[1] - 6, ry + row_h / 2, color=b["col"])
        # merge arrows to the modelling box
        arrow(c, xs[1] + col_w[1] + 4, ry + row_h / 2, xs[2] - 6, ry + row_h / 2, color=b["col"])

    # modelling + evaluation box
    mb_h = h
    mb_y = y
    rounded_box(c, xs[2], mb_y, col_w[2], mb_h, fill=S.PANEL_BG2, stroke=S.COL_FULL, lw=4)
    pad = 18
    t_st = pstyle("wf_mt", size=S.SZ_LABEL + 2, font=S.FONT_B, color=S.COL_FULL, leading=(S.SZ_LABEL + 2) * 1.15)
    hh = draw_para(c, "Joint modelling", xs[2] + pad, mb_y + mb_h - pad, col_w[2] - 2 * pad, t_st)
    body = ("Cox time-to-event models (5-year risk) and tree-based classifiers on the combined feature table."
            "<br/><br/><b>Evaluation:</b> participant-level 75 / 25 spatially stratified split; the held-out test set "
            "keeps the observed event rate; leave-one-centre-out check across four imaging centres.")
    draw_para(c, body, xs[2] + pad, mb_y + mb_h - pad - hh - 8, col_w[2] - 2 * pad, proc_st)


# --------------------------------------------------------------------------
# stat tiles
# --------------------------------------------------------------------------
def draw_stat_tiles(c, x, y, w, h, tiles, big_size=S.SZ_STAT, gap=0.18 * IN):
    n = len(tiles)
    tw = (w - gap * (n - 1)) / n
    for i, t in enumerate(tiles):
        tx = x + i * (tw + gap)
        rounded_box(c, tx, y, tw, h, fill=S.PANEL_BG, r=14)
        c.setFillColor(t.get("color", S.COL_FULL))
        c.rect(tx, y + h - 8, tw, 8, stroke=0, fill=1)
        bs = big_size
        while string_w(t["big"], S.FONT_B, bs) > tw - 24 and bs > 30:
            bs -= 2
        draw_text(c, t["big"], tx + tw / 2, y + h - 8 - bs * 1.05, S.FONT_B, bs, t.get("color", S.CHARCOAL), "c")
        st = pstyle("tile", size=S.SZ_CAPTION, color=S.TEXT, align=TA_CENTER, leading=S.SZ_CAPTION * 1.15)
        draw_para(c, t["label"], tx + 10, y + h - 8 - bs * 1.25, tw - 20, st)


# --------------------------------------------------------------------------
# generic horizontal dot plot (used for AUC benchmark and C-index)
# --------------------------------------------------------------------------
def draw_dot_plot(c, x, y, w, h, rows, xmin, xmax, ticks, axis_label, label_w=None,
                  value_fmt="{:.3f}", ref_lines=(), brackets=(), ref_label=None):
    label_w = label_w or w * 0.42
    ax_x0 = x + label_w
    ax_x1 = x + w - 0.25 * IN
    axis_y = y + 0.95 * IN
    top = y + h - 0.2 * IN
    n = len(rows)
    row_h = (top - axis_y - 0.2 * IN) / n

    def px(v):
        return ax_x0 + (v - xmin) / (xmax - xmin) * (ax_x1 - ax_x0)

    # gridlines + ticks
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    for t in ticks:
        c.line(px(t), axis_y, px(t), top)
        draw_text(c, ("{:.2f}".format(t)), px(t), axis_y - S.SZ_LABEL * 1.1, S.FONT, S.SZ_LABEL, S.TEXT_MUTED, "c")
    c.setStrokeColor(S.CHARCOAL)
    c.setLineWidth(2.5)
    c.line(ax_x0, axis_y, ax_x1, axis_y)
    draw_text(c, axis_label, (ax_x0 + ax_x1) / 2, axis_y - S.SZ_LABEL * 2.35, S.FONT_SB, S.SZ_LABEL, S.TEXT, "c")
    for rl in ref_lines:
        c.setStrokeColor(rl.get("color", S.TEXT_MUTED))
        c.setLineWidth(2)
        c.setDash(10, 8)
        c.line(px(rl["x"]), axis_y, px(rl["x"]), top)
        c.setDash()
    # rows
    lab_st = pstyle("dp_lab", size=S.SZ_LABEL, font=S.FONT_SB, color=S.TEXT, leading=S.SZ_LABEL * 1.12)
    sub_st = pstyle("dp_sub", size=S.SZ_CAPTION - 2, color=S.TEXT_MUTED, leading=(S.SZ_CAPTION - 2) * 1.12)
    for i, r in enumerate(rows):
        cy = top - (i + 0.5) * row_h
        # label
        lh, lp = para_height(r["label"], label_w - 0.25 * IN, lab_st)
        sh = 0
        if r.get("sub"):
            sh, sp = para_height(r["sub"], label_w - 0.25 * IN, sub_st)
        total = lh + sh
        lp.drawOn(c, x, cy + total / 2 - lh)
        if r.get("sub"):
            sp.drawOn(c, x, cy - total / 2)
        # lollipop stem
        c.setStrokeColor(r["color"])
        c.setLineWidth(5)
        c.line(ax_x0, cy, px(r["value"]), cy)
        draw_marker(c, r.get("marker", "circle"), px(r["value"]), cy, 16, r["color"])
        draw_text(c, value_fmt.format(r["value"]), px(r["value"]) + 30, cy - S.SZ_LABEL * 0.36, S.FONT_B, S.SZ_LABEL + 2, r["color"], "w")
    # brackets (annotations between rows)
    for b in brackets:
        i0, i1 = b["rows"]
        y0 = top - (i0 + 0.5) * row_h
        y1 = top - (i1 + 0.5) * row_h
        bx = ax_x1 - b.get("inset", 1.6 * IN)
        c.setStrokeColor(S.TEXT_MUTED)
        c.setLineWidth(2)
        c.line(bx, y0, bx, y1)
        c.line(bx - 12, y0, bx, y0)
        c.line(bx - 12, y1, bx, y1)
        st = pstyle("br", size=S.SZ_CAPTION - 2, color=S.TEXT_MUTED, leading=(S.SZ_CAPTION - 2) * 1.12)
        hh, p = para_height(b["text"], b.get("w", 2.6 * IN), st)
        p.drawOn(c, bx + 14, (y0 + y1) / 2 - hh / 2)
    return axis_y


# --------------------------------------------------------------------------
# Module C: hexbin panel (raster interior + vector axes)
# --------------------------------------------------------------------------
def draw_hexbin_panel(c, x, y, w, h, img_path, cb_path, title, min_dpi=150):
    """Places the cropped plot interior and redraws axes. Returns dict with effective dpi."""
    th = panel_title(c, x, y + h, w, title, size=S.SZ_SUBHEAD - 2) if title else 0
    # layout: y-axis label (vertical) + plot + colourbar
    left_pad = 0.95 * IN
    bottom_pad = 1.15 * IN
    cb_w = 0.32 * IN
    cb_gap = 0.35 * IN
    cb_label_w = 0.9 * IN
    plot_w = w - left_pad - cb_w - cb_gap - cb_label_w
    plot_h = h - th - 0.2 * IN - bottom_pad
    # keep aspect of the source (819 x 658)
    src = ImageReader(str(img_path))
    iw, ih = src.getSize()
    scale = min(plot_w / iw, plot_h / ih, IN / min_dpi)   # never enlarge beyond min_dpi effective resolution
    pw, ph = iw * scale, ih * scale
    px0 = x + left_pad + (plot_w - pw) / 2
    py0 = y + bottom_pad + (plot_h - ph) / 2
    c.drawImage(src, px0, py0, pw, ph)
    c.setStrokeColor(S.CHARCOAL)
    c.setLineWidth(2.5)
    c.rect(px0, py0, pw, ph, stroke=1, fill=0)
    # ticks: ggplot default 5% expansion -> frame spans -4.4..4.4 SD
    lo, hi = -4.4, 4.4
    for v in (-4, -2, 0, 2, 4):
        tx = px0 + (v - lo) / (hi - lo) * pw
        ty = py0 + (v - lo) / (hi - lo) * ph
        c.setStrokeColor(S.CHARCOAL)
        c.setLineWidth(2)
        c.line(tx, py0, tx, py0 - 12)
        c.line(px0, ty, px0 - 12, ty)
        lab = ("−" + str(abs(v))) if v < 0 else str(v)
        draw_text(c, lab, tx, py0 - 12 - S.SZ_LABEL * 0.95, S.FONT, S.SZ_LABEL - 2, S.TEXT, "c")
        draw_text(c, lab, px0 - 18, ty - (S.SZ_LABEL - 2) * 0.35, S.FONT, S.SZ_LABEL - 2, S.TEXT, "e")
    draw_text(c, "Polygenic risk score (SD)", px0 + pw / 2, py0 - 12 - S.SZ_LABEL * 2.05, S.FONT_SB, S.SZ_LABEL, S.TEXT, "c")
    c.saveState()
    c.translate(x + 0.3 * IN, py0 + ph / 2)
    c.rotate(90)
    draw_text(c, "Imaging risk score (SD)", 0, 0, S.FONT_SB, S.SZ_LABEL, S.TEXT, "c")
    c.restoreState()
    # colour bar
    cbx = px0 + pw + cb_gap
    cb_h = ph * 0.55
    cby = py0 + (ph - cb_h) / 2
    c.drawImage(ImageReader(str(cb_path)), cbx, cby, cb_w, cb_h)
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    c.rect(cbx, cby, cb_w, cb_h, stroke=1, fill=0)
    for frac, lab in ((1.0, "100"), (0.5, "10"), (0.0, "1")):
        draw_text(c, lab, cbx + cb_w + 10, cby + frac * cb_h - (S.SZ_CAPTION - 2) * 0.35, S.FONT, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    draw_text(c, "Count", cbx, cby + cb_h + 14, S.FONT_SB, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    return dict(placed_w_in=pw / IN, placed_h_in=ph / IN, native_px=(iw, ih), eff_dpi=iw / (pw / IN))


# --------------------------------------------------------------------------
# Module C right: partial R2 bars
# --------------------------------------------------------------------------
def draw_vbars(c, x, y, w, h, bars, ymax, ylabel, title, fmt="{:.2f}%"):
    th = panel_title(c, x, y + h, w, title, size=S.SZ_SUBHEAD - 4)
    top = y + h - th - 0.55 * IN
    axis_y = y + 1.25 * IN
    ax_x0 = x + 1.35 * IN
    ax_x1 = x + w - 0.1 * IN
    n = len(bars)
    slot = (ax_x1 - ax_x0) / n
    bw = slot * 0.6

    def py(v):
        return axis_y + v / ymax * (top - axis_y)

    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    for t in range(0, int(ymax) + 1, 10):  # gridlines every 10 points
        c.line(ax_x0, py(t), ax_x1, py(t))
        draw_text(c, f"{t}%", ax_x0 - 10, py(t) - S.SZ_LABEL * 0.33, S.FONT, S.SZ_LABEL - 4, S.TEXT_MUTED, "e")
    c.setStrokeColor(S.CHARCOAL)
    c.setLineWidth(2.5)
    c.line(ax_x0, axis_y, ax_x1, axis_y)
    lab_st = pstyle("vb", size=S.SZ_CAPTION, color=S.TEXT, align=TA_CENTER, leading=S.SZ_CAPTION * 1.1)
    for i, b in enumerate(bars):
        bx = ax_x0 + i * slot + (slot - bw) / 2
        c.setFillColor(b["color"])
        c.rect(bx, axis_y, bw, max(py(b["value"]) - axis_y, 3), stroke=0, fill=1)
        draw_text(c, fmt.format(b["value"]), bx + bw / 2, py(b["value"]) + 10, S.FONT_B, S.SZ_LABEL - 2, b["color"], "c")
        draw_para(c, b["label"], ax_x0 + i * slot, axis_y - 10, slot, lab_st)
    c.saveState()
    c.translate(x + 0.22 * IN, (axis_y + top) / 2)
    c.rotate(90)
    draw_text(c, ylabel, 0, 0, S.FONT_SB, S.SZ_LABEL - 2, S.TEXT, "c")
    c.restoreState()


# --------------------------------------------------------------------------
# qualitative chips (modality contribution)
# --------------------------------------------------------------------------
def draw_chip_groups(c, x, y, w, h, groups, title):
    th = panel_title(c, x, y + h, w, title, size=S.SZ_SUBHEAD - 4)
    gy_top = y + h - th - 0.15 * IN
    n = len(groups)
    gap = 0.3 * IN
    gw = (w - gap * (n - 1)) / n
    hd_st = pstyle("chip_hd", size=S.SZ_CAPTION + 1, font=S.FONT_SB, color=S.TEXT, leading=(S.SZ_CAPTION + 1) * 1.15)
    chip_st = pstyle("chip", size=S.SZ_CAPTION, color=white, font=S.FONT_SB, leading=S.SZ_CAPTION * 1.1, align=TA_CENTER)
    for i, g in enumerate(groups):
        gx = x + i * (gw + gap)
        rounded_box(c, gx, y, gw, gy_top - y, fill=S.PANEL_BG, r=14)
        hh = draw_para(c, g["title"], gx + 16, gy_top - 12, gw - 32, hd_st)
        cy = gy_top - 12 - hh - 12
        for item, col in g["items"]:
            ch = S.SZ_CAPTION * 1.1 + 18
            rounded_box(c, gx + 16, cy - ch, gw - 32, ch, fill=col, r=10)
            draw_para(c, item, gx + 16, cy - 9, gw - 32, chip_st)
            cy -= ch + 10
        if g.get("note"):
            draw_para(c, g["note"], gx + 16, cy - 4, gw - 32, ST["small"])


# --------------------------------------------------------------------------
# Module E: tier cards
# --------------------------------------------------------------------------
def draw_tier_cards(c, x, y, w, h, tiers):
    n = len(tiers)
    arrow_w = 0.5 * IN
    cw = (w - arrow_w * (n - 1)) / n
    title_st = pstyle("tier_t", size=S.SZ_LABEL + 2, font=S.FONT_B, color=white, leading=(S.SZ_LABEL + 2) * 1.12)
    rule_st = pstyle("tier_r", size=S.SZ_CAPTION, color=S.TEXT, leading=S.SZ_CAPTION * 1.18)
    for i, t in enumerate(tiers):
        cx = x + i * (cw + arrow_w)
        rounded_box(c, cx, y, cw, h, fill=S.PANEL_BG, stroke=t["color"], lw=3, r=16)
        head_h = 0.72 * IN
        c.setFillColor(t["color"])
        p = c.beginPath()
        p.roundRect(cx, y + h - head_h, cw, head_h, 16)
        c.drawPath(p, stroke=0, fill=1)
        c.rect(cx, y + h - head_h, cw, head_h / 2, stroke=0, fill=1)
        draw_para(c, t["title"], cx + 16, y + h - 14, cw - 32, title_st)
        rh = draw_para(c, t["rule"], cx + 16, y + h - head_h - 14, cw - 32, rule_st)
        big = t["big"]
        bs = S.SZ_STAT
        draw_text(c, big, cx + cw / 2, y + 0.95 * IN, S.FONT_B, bs, t["color"], "c")
        draw_text(c, "5-year CAD incidence", cx + cw / 2, y + 0.42 * IN, S.FONT, S.SZ_CAPTION, S.TEXT_MUTED, "c")
        if i < n - 1:
            arrow(c, cx + cw + 6, y + h / 2, cx + cw + arrow_w - 6, y + h / 2, color=S.TEXT_MUTED, lw=4)


# --------------------------------------------------------------------------
# Module F: centre table
# --------------------------------------------------------------------------
def draw_table(c, x, y, w, h, header, rows, col_fracs, aligns=None, zebra=True, header_color=S.CHARCOAL,
               font_size=S.SZ_LABEL):
    n = len(rows) + 1
    rh = h / n
    cws = [f * w for f in col_fracs]
    aligns = aligns or ["w"] * len(header)
    # header
    c.setFillColor(header_color)
    c.rect(x, y + h - rh, w, rh, stroke=0, fill=1)
    cx = x
    for j, (txt, cw) in enumerate(zip(header, cws)):
        ax = cx + 14 if aligns[j] == "w" else (cx + cw / 2 if aligns[j] == "c" else cx + cw - 14)
        draw_text(c, txt, ax, y + h - rh + (rh - font_size * 0.7) / 2, S.FONT_SB, font_size, white, aligns[j])
        cx += cw
    for i, r in enumerate(rows):
        ry = y + h - (i + 2) * rh
        if zebra and i % 2 == 1:
            c.setFillColor(S.PANEL_BG)
            c.rect(x, ry, w, rh, stroke=0, fill=1)
        cx = x
        for j, (txt, cw) in enumerate(zip(r, cws)):
            ax = cx + 14 if aligns[j] == "w" else (cx + cw / 2 if aligns[j] == "c" else cx + cw - 14)
            draw_text(c, str(txt), ax, ry + (rh - font_size * 0.7) / 2, S.FONT_B if j == 0 else S.FONT, font_size, S.TEXT, aligns[j])
            cx += cw
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    c.line(x, y, x + w, y)


# --------------------------------------------------------------------------
# logos
# --------------------------------------------------------------------------
def draw_logo(c, x, y, w, h, candidates, placeholder_label):
    """Draw the first existing logo file (svg, pdf-not-supported, png) scaled into the box.
    If none exists, draw a clearly marked reserved area. Returns ('file', path) or ('placeholder', None)."""
    for p in candidates:
        p = Path(p)
        if not p.exists():
            continue
        if p.suffix.lower() == ".svg":
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPDF
            d = svg2rlg(str(p))
            sc = min(w / d.width, h / d.height)
            d.scale(sc, sc)
            dw, dh = d.width * sc, d.height * sc
            renderPDF.draw(d, c, x + (w - dw) / 2, y + (h - dh) / 2)
            return "file", str(p)
        if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
            img = ImageReader(str(p))
            iw, ih = img.getSize()
            sc = min(w / iw, h / ih)
            c.drawImage(img, x + (w - iw * sc) / 2, y + (h - ih * sc) / 2, iw * sc, ih * sc, mask="auto")
            return "file", str(p)
    # placeholder
    c.setStrokeColor(S.RULE)
    c.setLineWidth(3)
    c.setDash(18, 12)
    c.setFillColor(S.HexColor("#FAFAF8"))
    c.rect(x, y, w, h, stroke=1, fill=1)
    c.setDash()
    st = pstyle("ph", size=S.SZ_CAPTION, color=S.TEXT_MUTED, align=TA_CENTER, leading=S.SZ_CAPTION * 1.2)
    hh, p = para_height(placeholder_label, w - 40, st)
    p.drawOn(c, x + 20, y + (h - hh) / 2)
    return "placeholder", None
