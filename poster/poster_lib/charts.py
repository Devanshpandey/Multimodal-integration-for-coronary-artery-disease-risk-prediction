"""Vector chart and diagram modules for poster design v3, drawn directly on the ReportLab canvas.

Every function takes a box (x, y_bottom, w, h) in points and draws inside it.
No participant-level data are synthesised. The hexbin is a cell-by-cell vector transcription of
the manuscript's Fig. 3c raster (assets/figures/fig3c_hexcells.json, tools/hexbin_transcribe.py).
"""
import json
import math
from pathlib import Path
from reportlab.lib.colors import Color, white
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER
from . import style as S
from .text import draw_text, draw_para, string_w, pstyle, para_height

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


def draw_marker(c, shape, x, y, r, color, ring=white):
    c.setFillColor(color)
    c.setStrokeColor(ring)
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
        c.drawPath(p, stroke=1, fill=1)


def panel_title(c, x, y_top, w, text, size=S.SZ_SUBHEAD, color=S.INK, font=S.FONT_SB):
    st = pstyle("ptitle", size=size, font=font, color=color, leading=size * 1.15)
    return draw_para(c, text, x, y_top, w, st)


def haxis(c, x0, x1, y, vmin, vmax, ticks, top, label=None, fmt="{:.2f}", grid=True):
    """Horizontal numeric axis with recessive grid lines; returns px(v) mapper."""
    def px(v):
        return x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    if grid:
        c.setStrokeColor(S.GRID)
        c.setLineWidth(1.5)
        for t in ticks:
            c.line(px(t), y, px(t), top)
    c.setStrokeColor(S.TEXT_MUTED)
    c.setLineWidth(2)
    c.line(x0, y, x1, y)
    for t in ticks:
        draw_text(c, fmt.format(t), px(t), y - S.SZ_LABEL * 1.1, S.FONT, S.SZ_LABEL - 2, S.TEXT_MUTED, "c")
    if label:
        draw_text(c, label, (x0 + x1) / 2, y - S.SZ_LABEL * 2.3, S.FONT_SB, S.SZ_LABEL - 2, S.TEXT, "c")
    return px


# --------------------------------------------------------------------------
# big-number facts (editorial numerals)
# --------------------------------------------------------------------------
def draw_facts(c, x, y, w, h, facts, cols=2, num_size=S.SZ_STAT):
    rows = math.ceil(len(facts) / cols)
    cw = w / cols
    rh = h / rows
    lab_st = pstyle("fact", size=S.SZ_CAPTION, color=S.TEXT_MUTED, leading=S.SZ_CAPTION * 1.15)
    for i, f in enumerate(facts):
        cx = x + (i % cols) * cw
        cy_top = y + h - (i // cols) * rh
        ns = num_size
        while string_w(f["big"], S.DISPLAY, ns) > cw - 0.3 * IN and ns > 36:
            ns -= 2
        draw_text(c, f["big"], cx, cy_top - ns * 0.95, S.DISPLAY, ns, f.get("color", S.INK), "w")
        draw_para(c, f["label"], cx, cy_top - ns * 1.08, cw - 0.3 * IN, lab_st)
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.5)
    c.line(x, y, x + w, y)


# --------------------------------------------------------------------------
# confluence diagram: three streams merge into one model
# --------------------------------------------------------------------------
def _band(c, x0, y0, x1, y1, thickness, color, alpha=1.0):
    """S-curved band from (x0,y0) to (x1,y1) with given thickness (filled Bezier ribbon)."""
    t = thickness / 2
    cx0 = x0 + (x1 - x0) * 0.5
    cx1 = x1 - (x1 - x0) * 0.5
    p = c.beginPath()
    p.moveTo(x0, y0 + t)
    p.curveTo(cx0, y0 + t, cx1, y1 + t, x1, y1 + t)
    p.lineTo(x1, y1 - t)
    p.curveTo(cx1, y1 - t, cx0, y0 - t, x0, y0 - t)
    p.close()
    c.setFillColor(Color(color.red, color.green, color.blue, alpha=alpha))
    c.drawPath(p, stroke=0, fill=1)


def draw_confluence(c, x, y, w, h, streams, model_text, eval_text):
    """streams: list of dict(name, sub, color). Left source cards -> ribbons -> merge box -> evaluation."""
    n = len(streams)
    card_w = w * 0.34
    card_gap = 0.18 * IN
    card_h = (h - card_gap * (n - 1)) / n
    merge_x = x + w * 0.60
    merge_w = w * 0.40
    band_th = card_h * 0.42
    # merge box spans the middle band region
    mb_h = h * 0.74
    mb_y = y + (h - mb_h) / 2
    name_st = pstyle("cf_name", size=S.SZ_LABEL + 4, font=S.FONT_B, color=white, leading=(S.SZ_LABEL + 4) * 1.12)
    sub_st = pstyle("cf_sub", size=S.SZ_CAPTION - 1, color=white, leading=(S.SZ_CAPTION - 1) * 1.16)
    # ribbons first (behind)
    for i, s in enumerate(streams):
        cy = y + h - i * (card_h + card_gap) - card_h / 2
        ty = mb_y + mb_h - (i + 0.5) * (mb_h / n)
        _band(c, x + card_w - 6, cy, merge_x + 8, ty, band_th, s["color"], alpha=0.85)
    # source cards
    for i, s in enumerate(streams):
        cy_b = y + h - (i + 1) * card_h - i * card_gap
        rounded_box(c, x, cy_b, card_w, card_h, fill=s["color"], r=16)
        pad = 18
        hh = draw_para(c, s["name"], x + pad, cy_b + card_h - pad, card_w - 2 * pad, name_st)
        draw_para(c, s["sub"], x + pad, cy_b + card_h - pad - hh - 4, card_w - 2 * pad, sub_st)
    # merge box
    rounded_box(c, merge_x, mb_y, merge_w, mb_h, fill=S.ORANGE_TINT, stroke=S.COL_FULL, lw=4, r=18)
    pad = 20
    t_st = pstyle("cf_mt", size=S.SZ_LABEL + 4, font=S.FONT_B, color=S.COL_FULL, leading=(S.SZ_LABEL + 4) * 1.12)
    b_st = pstyle("cf_mb", size=S.SZ_CAPTION, color=S.TEXT, leading=S.SZ_CAPTION * 1.2)
    hh = draw_para(c, "Joint models", merge_x + pad, mb_y + mb_h - pad, merge_w - 2 * pad, t_st)
    hh2 = draw_para(c, model_text, merge_x + pad, mb_y + mb_h - pad - hh - 6, merge_w - 2 * pad, b_st)
    # evaluation strip inside the merge box bottom
    e_st = pstyle("cf_ev", size=S.SZ_CAPTION, color=S.TEXT, leading=S.SZ_CAPTION * 1.2)
    eh, ep = para_height("<b>Evaluation</b> &nbsp;" + eval_text, merge_w - 2 * pad, e_st)
    c.setStrokeColor(S.COL_FULL)
    c.setLineWidth(1.5)
    c.line(merge_x + pad, mb_y + pad + eh + 10, merge_x + merge_w - pad, mb_y + pad + eh + 10)
    ep.drawOn(c, merge_x + pad, mb_y + pad)


# --------------------------------------------------------------------------
# vector hexbin (transcribed cells) with recolouring to the poster ramp
# --------------------------------------------------------------------------
def _t_of_rgb(rgb, lo=(224, 224, 224), hi=(44, 95, 138)):
    """Position along the original ggplot gradient (grey88 -> #2C5F8A), 0..1, by projection."""
    a = lo
    v = [hi[i] - lo[i] for i in range(3)]
    d = [rgb[i] - a[i] for i in range(3)]
    t = sum(d[i] * v[i] for i in range(3)) / sum(v[i] * v[i] for i in range(3))
    return max(0.0, min(1.0, t))


def draw_hexbin_vector(c, x, y, w, h, cells_json, xlab, ylab, legend_ticks=((0.022, "1"), (0.478, "10"), (0.944, "100")),
                       recolor=True):
    """Draw the transcribed hexbin into box; axes in SD units (-4.4..4.4 frame). Returns plot rect."""
    d = json.loads(Path(cells_json).read_text())
    W, H = d["W"], d["H"]
    left = 1.05 * IN
    bottom = 1.15 * IN
    cb_w = 0.36 * IN
    cb_zone = 1.5 * IN
    pw_avail = w - left - cb_zone
    ph_avail = h - bottom - 0.1 * IN
    scale = min(pw_avail / W, ph_avail / H)
    pw, ph = W * scale, H * scale
    px0 = x + left
    py0 = y + bottom + (ph_avail - ph) / 2

    def X(px):
        return px0 + px / W * pw

    def Yp(py):
        return py0 + (H - py) / H * ph
    # background + grid at ticks
    c.setFillColor(white)
    c.rect(px0, py0, pw, ph, stroke=0, fill=1)
    lo, hi = d["axis_range"]
    c.setStrokeColor(S.GRID)
    c.setLineWidth(1.2)
    for v in (-4, -2, 0, 2, 4):
        tx = px0 + (v - lo) / (hi - lo) * pw
        ty = py0 + (v - lo) / (hi - lo) * ph
        c.line(tx, py0, tx, py0 + ph)
        c.line(px0, ty, px0 + pw, ty)
    # cells
    hw = (d["w_px"] / 2) / W * pw + 0.35
    hh = (d["dy_row"] / 0.75 / 2) / H * ph + 0.35
    c.setLineWidth(0.5)
    for cell in d["cells"]:
        rgb = cell["rgb"]
        col = S.ramp(_t_of_rgb(rgb)) if recolor else Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
        cx, cy = X(cell["x"]), Yp(cell["y"])
        p = c.beginPath()
        p.moveTo(cx, cy + hh)
        p.lineTo(cx + hw, cy + hh / 2)
        p.lineTo(cx + hw, cy - hh / 2)
        p.lineTo(cx, cy - hh)
        p.lineTo(cx - hw, cy - hh / 2)
        p.lineTo(cx - hw, cy + hh / 2)
        p.close()
        c.setFillColor(col)
        c.setStrokeColor(col)
        c.drawPath(p, stroke=1, fill=1)
    # fitted line
    ln = d["line"]
    c.setStrokeColor(S.COL_LINE)
    c.setLineWidth(ln["thickness_px"] / H * ph)
    c.setLineCap(1)
    c.line(X(ln["x1"]), Yp(ln["y1"]), X(ln["x2"]), Yp(ln["y2"]))
    c.setLineCap(0)
    # frame + ticks
    c.setStrokeColor(S.TEXT_MUTED)
    c.setLineWidth(2)
    c.rect(px0, py0, pw, ph, stroke=1, fill=0)
    for v in (-4, -2, 0, 2, 4):
        tx = px0 + (v - lo) / (hi - lo) * pw
        ty = py0 + (v - lo) / (hi - lo) * ph
        c.line(tx, py0, tx, py0 - 10)
        c.line(px0, ty, px0 - 10, ty)
        lab = ("−" + str(abs(v))) if v < 0 else str(v)
        draw_text(c, lab, tx, py0 - 10 - S.SZ_LABEL * 0.95, S.FONT, S.SZ_LABEL - 2, S.TEXT_MUTED, "c")
        draw_text(c, lab, px0 - 16, ty - (S.SZ_LABEL - 2) * 0.35, S.FONT, S.SZ_LABEL - 2, S.TEXT_MUTED, "e")
    draw_text(c, xlab, px0 + pw / 2, py0 - 10 - S.SZ_LABEL * 2.1, S.FONT_SB, S.SZ_LABEL + 2, S.TEXT, "c")
    c.saveState()
    c.translate(x + 0.32 * IN, py0 + ph / 2)
    c.rotate(90)
    draw_text(c, ylab, 0, 0, S.FONT_SB, S.SZ_LABEL + 2, S.TEXT, "c")
    c.restoreState()
    # colour bar (log-scale count)
    cbx = px0 + pw + 0.35 * IN
    cb_h = ph * 0.5
    cby = py0 + (ph - cb_h) / 2
    n = 60
    for i in range(n):
        t0 = i / n
        c.setFillColor(S.ramp(t0) if recolor else Color(*[(224 + (hi_ - 224) * t0) / 255 for hi_ in (44, 95, 138)]))
        c.rect(cbx, cby + t0 * cb_h, cb_w, cb_h / n + 0.6, stroke=0, fill=1)
    c.setStrokeColor(S.RULE)
    c.setLineWidth(1.2)
    c.rect(cbx, cby, cb_w, cb_h, stroke=1, fill=0)
    for t0, lab in legend_ticks:
        draw_text(c, lab, cbx + cb_w + 10, cby + t0 * cb_h - (S.SZ_CAPTION - 2) * 0.35, S.FONT, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    draw_text(c, "participants", cbx, cby + cb_h + 36, S.FONT_SB, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    draw_text(c, "per cell", cbx, cby + cb_h + 10, S.FONT_SB, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    return dict(plot_w_in=pw / IN, plot_h_in=ph / IN, cells=len(d["cells"]), fidelity=d.get("fidelity_all"))


# --------------------------------------------------------------------------
# C-index ladder (four models, deltas vs clinical)
# --------------------------------------------------------------------------
def draw_ladder(c, x, y, w, h, rows, vmin, vmax, ticks, axis_label, label_w=None):
    label_w = label_w or w * 0.36
    ax_x0 = x + label_w
    ax_x1 = x + w - 2.9 * IN
    axis_y = y + 1.0 * IN
    top = y + h - 0.15 * IN
    n = len(rows)
    row_h = (top - axis_y - 0.15 * IN) / n
    px = haxis(c, ax_x0, ax_x1, axis_y, vmin, vmax, ticks, top, axis_label)
    base = rows[0]["value"]
    c.setStrokeColor(S.COL_CLINICAL)
    c.setLineWidth(2)
    c.setDash(8, 8)
    c.line(px(base), axis_y, px(base), top)
    c.setDash()
    lab_st = pstyle("ld_lab", size=S.SZ_LABEL + 2, font=S.FONT_SB, color=S.TEXT, leading=(S.SZ_LABEL + 2) * 1.12)
    sub_st = pstyle("ld_sub", size=S.SZ_CAPTION - 2, color=S.TEXT_MUTED, leading=(S.SZ_CAPTION - 2) * 1.12)
    for i, r in enumerate(rows):
        cy = top - (i + 0.5) * row_h
        lh, lp = para_height(r["label"], label_w - 0.25 * IN, lab_st)
        sh, sp = (para_height(r["sub"], label_w - 0.25 * IN, sub_st) if r.get("sub") else (0, None))
        total = lh + sh
        lp.drawOn(c, x, cy + total / 2 - lh)
        if sp:
            sp.drawOn(c, x, cy - total / 2)
        c.setStrokeColor(r["color"])
        c.setLineWidth(6)
        c.setLineCap(1)
        c.line(ax_x0, cy, px(r["value"]), cy)
        c.setLineCap(0)
        draw_marker(c, r.get("marker", "circle"), px(r["value"]), cy, 17, r["color"])
        draw_text(c, "{:.3f}".format(r["value"]), ax_x1 + 0.25 * IN, cy - (S.SZ_LABEL + 2) * 0.36, S.FONT_B, S.SZ_LABEL + 4, r["color"], "w")
        if i > 0:
            dlt = r["value"] - base
            draw_text(c, "+{:.3f}".format(dlt), ax_x1 + 1.6 * IN, cy - (S.SZ_CAPTION - 2) * 0.36, S.FONT, S.SZ_CAPTION - 2, S.TEXT_MUTED, "w")
    draw_text(c, "vs clinical", ax_x1 + 1.6 * IN, top + 4, S.FONT, S.SZ_CAPTION - 4, S.TEXT_MUTED, "w")


# --------------------------------------------------------------------------
# incidence staircase (tiers)
# --------------------------------------------------------------------------
def draw_staircase(c, x, y, w, h, tiers, ymax, ref=None):
    left = 1.6 * IN
    bottom = 2.3 * IN
    ax_x0, ax_x1 = x + left, x + w - 0.2 * IN
    axis_y = y + bottom
    top = y + h - 0.3 * IN
    n = len(tiers)
    slot = (ax_x1 - ax_x0) / n
    bw = slot * 0.62

    def py(v):
        return axis_y + v / ymax * (top - axis_y)
    c.setStrokeColor(S.GRID)
    c.setLineWidth(1.5)
    for t in range(0, int(ymax) + 1, 5):
        c.line(ax_x0, py(t), ax_x1, py(t))
        draw_text(c, f"{t}%", ax_x0 - 12, py(t) - S.SZ_LABEL * 0.33, S.FONT, S.SZ_LABEL - 4, S.TEXT_MUTED, "e")
    c.setStrokeColor(S.TEXT_MUTED)
    c.setLineWidth(2)
    c.line(ax_x0, axis_y, ax_x1, axis_y)
    if ref:
        c.setStrokeColor(S.TEXT_MUTED)
        c.setLineWidth(2)
        c.setDash(8, 8)
        c.line(ax_x0, py(ref["value"]), ax_x1, py(ref["value"]))
        c.setDash()
        draw_text(c, ref["label"], ax_x1, py(ref["value"]) + 8, S.FONT_SB, S.SZ_CAPTION - 3, S.TEXT_MUTED, "e")
    rule_st = pstyle("st_rule", size=S.SZ_CAPTION, color=S.TEXT, leading=S.SZ_CAPTION * 1.15, align=TA_CENTER)
    for i, t in enumerate(tiers):
        bx = ax_x0 + i * slot + (slot - bw) / 2
        c.setFillColor(t["color"])
        c.roundRect(bx, axis_y, bw, py(t["value"]) - axis_y, 6, stroke=0, fill=1)
        c.setFillColor(t["color"])
        c.rect(bx, axis_y, bw, 8, stroke=0, fill=1)
        draw_text(c, f"{t['value']:.1f}%", bx + bw / 2, py(t["value"]) + 14, S.DISPLAY, 48, t["color"], "c")
        draw_text(c, t["name"], bx + bw / 2, axis_y - S.SZ_LABEL * 1.15, S.FONT_B, S.SZ_LABEL, t["color"], "c")
        draw_para(c, t["rule"], ax_x0 + i * slot, axis_y - S.SZ_LABEL * 1.35, slot, rule_st)
        if i < n - 1:
            ax_ = bx + bw + 6
            arrow(c, ax_, axis_y - S.SZ_LABEL * 0.8, ax_ + slot - bw - 12, axis_y - S.SZ_LABEL * 0.8, color=S.RULE, lw=3, head=12)
    c.saveState()
    c.translate(x + 0.3 * IN, (axis_y + top) / 2)
    c.rotate(90)
    draw_text(c, "5-year CAD incidence", 0, 0, S.FONT_SB, S.SZ_LABEL - 2, S.TEXT, "c")
    c.restoreState()


# --------------------------------------------------------------------------
# centre robustness: two small dot panels (AUC, C-index), separate axes
# --------------------------------------------------------------------------
def draw_center_dots(c, x, y, w, h, rows, panels):
    """rows: list of dict(name, auc, c_index, n). panels: [(key, title, vmin, vmax, ticks, marker)]"""
    label_w = w * 0.30
    gap = 0.9 * IN
    pw = (w - label_w - gap * (len(panels) - 1)) / len(panels)
    axis_y = y + 0.95 * IN
    top = y + h - 0.7 * IN
    n = len(rows)
    row_h = (top - axis_y - 0.1 * IN) / n
    lab_st = pstyle("cd_lab", size=S.SZ_LABEL, font=S.FONT_SB, color=S.TEXT, leading=S.SZ_LABEL * 1.1)
    sub_st = pstyle("cd_sub", size=S.SZ_CAPTION - 3, color=S.TEXT_MUTED, leading=(S.SZ_CAPTION - 3) * 1.1)
    for i, r in enumerate(rows):
        cy = top - (i + 0.5) * row_h
        txt = f"{r['name']} <font size={S.SZ_CAPTION - 4} color='{S.hex_of(S.TEXT_MUTED)}'>{r['sub']}</font>"
        lh, lp = para_height(txt, label_w, lab_st)
        lp.drawOn(c, x, cy - lh / 2)
    for k, (key, title, vmin, vmax, ticks, marker, color) in enumerate(panels):
        x0 = x + label_w + k * (pw + gap)
        x1 = x0 + pw
        draw_text(c, title, x0, top + 14, S.FONT_SB, S.SZ_LABEL - 2, S.TEXT, "w")
        px = haxis(c, x0, x1, axis_y, vmin, vmax, ticks, top, None)
        for i, r in enumerate(rows):
            cy = top - (i + 0.5) * row_h
            c.setStrokeColor(S.GRID)
            draw_marker(c, marker, px(r[key]), cy, 14, color)
            draw_text(c, "{:.3f}".format(r[key]), px(r[key]) + 26, cy - S.SZ_CAPTION * 0.36, S.FONT, S.SZ_CAPTION - 2, S.TEXT, "w")


# --------------------------------------------------------------------------
# benchmark bars (AUC, two rows)
# --------------------------------------------------------------------------
def draw_benchmark(c, x, y, w, h, rows, vmin, vmax, ticks, axis_label, label_w=None):
    label_w = label_w or w * 0.5
    ax_x0 = x + label_w
    ax_x1 = x + w - 1.2 * IN
    axis_y = y + 1.0 * IN
    top = y + h - 0.1 * IN
    n = len(rows)
    row_h = (top - axis_y - 0.1 * IN) / n
    px = haxis(c, ax_x0, ax_x1, axis_y, vmin, vmax, ticks, top, axis_label)
    lab_st = pstyle("bm_lab", size=S.SZ_LABEL + 1, font=S.FONT_SB, color=S.TEXT, leading=(S.SZ_LABEL + 1) * 1.12)
    sub_st = pstyle("bm_sub", size=S.SZ_CAPTION - 2, color=S.TEXT_MUTED, leading=(S.SZ_CAPTION - 2) * 1.12)
    for i, r in enumerate(rows):
        cy = top - (i + 0.5) * row_h
        lh, lp = para_height(r["label"], label_w - 0.25 * IN, lab_st)
        sh, sp = para_height(r["sub"], label_w - 0.25 * IN, sub_st)
        lp.drawOn(c, x, cy + (lh + sh) / 2 - lh)
        sp.drawOn(c, x, cy - (lh + sh) / 2)
        bh = row_h * 0.46
        c.setFillColor(r["color"])
        c.roundRect(ax_x0, cy - bh / 2, px(r["value"]) - ax_x0, bh, 5, stroke=0, fill=1)
        c.rect(ax_x0, cy - bh / 2, 6, bh, stroke=0, fill=1)
        draw_text(c, "{:.3f}".format(r["value"]), px(r["value"]) + 14, cy - (S.SZ_LABEL + 2) * 0.36, S.FONT_B, S.SZ_LABEL + 2, r["color"], "w")


# --------------------------------------------------------------------------
# chip groups
# --------------------------------------------------------------------------
def draw_chip_groups(c, x, y, w, h, groups, title=None):
    th = panel_title(c, x, y + h, w, title) if title else 0
    gy_top = y + h - th - (0.15 * IN if title else 0)
    n = len(groups)
    gap = 0.3 * IN
    gw = (w - gap * (n - 1)) / n
    hd_st = pstyle("chip_hd", size=S.SZ_CAPTION + 1, font=S.FONT_SB, color=S.TEXT, leading=(S.SZ_CAPTION + 1) * 1.15)
    chip_st = pstyle("chip", size=S.SZ_CAPTION, color=white, font=S.FONT_SB, leading=S.SZ_CAPTION * 1.1, align=TA_CENTER)
    for i, g in enumerate(groups):
        gx = x + i * (gw + gap)
        rounded_box(c, gx, y, gw, gy_top - y, fill=S.SAND, r=14)
        hh = draw_para(c, g["title"], gx + 16, gy_top - 12, gw - 32, hd_st)
        cy = gy_top - 12 - hh - 10
        ch = S.SZ_CAPTION * 1.1 + 16
        cols = 2 if len(g["items"]) > 3 else 1
        cw = (gw - 32 - (cols - 1) * 10) / cols
        for k, (item, col) in enumerate(g["items"]):
            cx = gx + 16 + (k % cols) * (cw + 10)
            cyy = cy - (k // cols) * (ch + 8)
            rounded_box(c, cx, cyy - ch, cw, ch, fill=col, r=10)
            draw_para(c, item, cx, cyy - 8, cw, chip_st)


# --------------------------------------------------------------------------
# small stat tiles
# --------------------------------------------------------------------------
def draw_stat_tiles(c, x, y, w, h, tiles, big_size=52, gap=0.2 * IN):
    n = len(tiles)
    tw = (w - gap * (n - 1)) / n
    lab_st = pstyle("tile", size=S.SZ_CAPTION - 1, color=S.TEXT_MUTED, align=TA_CENTER, leading=(S.SZ_CAPTION - 1) * 1.12)
    for i, t in enumerate(tiles):
        tx = x + i * (tw + gap)
        rounded_box(c, tx, y, tw, h, fill=S.SAND, r=14)
        bs = big_size
        while string_w(t["big"], S.DISPLAY, bs) > tw - 24 and bs > 30:
            bs -= 2
        draw_text(c, t["big"], tx + tw / 2, y + h - bs * 1.05, S.DISPLAY, bs, t.get("color", S.INK), "c")
        draw_para(c, t["label"], tx + 10, y + h - bs * 1.25, tw - 20, lab_st)


# --------------------------------------------------------------------------
# logos
# --------------------------------------------------------------------------
def draw_logo(c, x, y, w, h, candidates, placeholder_label):
    """Draw the first existing logo file scaled into the box; else a quiet reserved plate."""
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
            renderPDF.draw(d, c, x + (w - d.width * sc) / 2, y + (h - d.height * sc) / 2)
            return "file", str(p)
        if p.suffix.lower() in (".png", ".jpg", ".jpeg"):
            img = ImageReader(str(p))
            iw, ih = img.getSize()
            sc = min(w / iw, h / ih)
            c.drawImage(img, x + (w - iw * sc) / 2, y + (h - ih * sc) / 2, iw * sc, ih * sc, mask="auto")
            return "file", str(p)
    st = pstyle("ph", size=S.SZ_SMALL, color=S.HexColor("#A9B0BC"), align=TA_CENTER, leading=S.SZ_SMALL * 1.2)
    hh, p = para_height(placeholder_label, w - 40, st)
    p.drawOn(c, x + 20, y + (h - hh) / 2)
    return "placeholder", None
