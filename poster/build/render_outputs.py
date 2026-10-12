#!/usr/bin/env python3
"""Derive the print file and the preview images from poster.pdf.

- poster_print.pdf : every glyph converted to a filled path (no fonts left in
  the file), page size unchanged. Ghostscript is not available in the build
  container, so this is done with PyMuPDF (text trace) + fontTools (glyph
  outlines from the embedded subset fonts).
- preview.png (20 DPI), crop_col1-4.png (72 DPI), poster_thumbnail.png
  (150 DPI at 1/4 scale = 2700 x 1350 px).
"""
import io
import os
import re
import sys

import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SRC = os.path.join(ROOT, "poster.pdf")
PRINT = os.path.join(ROOT, "poster_print.pdf")

MARGIN = 72
COL_GAP = 44
COL_W = (5184 - 2 * MARGIN - 3 * COL_GAP) / 4


class ShapePen(BasePen):
    """fontTools pen that emits PyMuPDF Shape drawing calls.
    BasePen converts TrueType quadratic segments to cubics for us."""

    def __init__(self, shape, matrix, glyphset):
        super().__init__(glyphSet=glyphset)
        self.shape = shape
        self.m = matrix  # (a, b, c, d, e, f): x' = a x + c y + e ; y' = b x + d y + f
        self.cur = None
        self.start = None

    def _p(self, pt):
        a, b, c, d, e, f = self.m
        x, y = pt
        return pymupdf.Point(a * x + c * y + e, b * x + d * y + f)

    def _moveTo(self, pt):
        self.cur = self.start = self._p(pt)

    def _lineTo(self, pt):
        q = self._p(pt)
        self.shape.draw_line(self.cur, q)
        self.cur = q

    def _curveToOne(self, p1, p2, p3):
        q1, q2, q3 = self._p(p1), self._p(p2), self._p(p3)
        self.shape.draw_bezier(self.cur, q1, q2, q3)
        self.cur = q3

    def _closePath(self):
        if self.cur is not None and self.start is not None and self.cur != self.start:
            self.shape.draw_line(self.cur, self.start)
        self.cur = self.start

    def _endPath(self):
        self.cur = self.start


def outline_pdf(src, dst):
    doc = pymupdf.open(src)
    page = doc[0]
    page_h = page.rect.height

    # embedded subset fonts. Chromium embeds several subsets of the same face
    # (same BaseFont, different glyph numbering), so each span is matched to
    # the subset whose ToUnicode map reproduces the span's characters.
    def parse_tounicode(xref):
        key, val = doc.xref_get_key(xref, "ToUnicode")
        if key != "xref":
            return {}
        cmap = doc.xref_stream(int(val.split()[0])).decode("latin-1")
        m = {}
        for block in re.findall(r"beginbfchar(.*?)endbfchar", cmap, flags=re.S):
            for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                m[int(src, 16)] = int(dst[:4], 16)
        for block in re.findall(r"beginbfrange(.*?)endbfrange", cmap, flags=re.S):
            for lo, hi, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", block):
                lo, hi, d = int(lo, 16), int(hi, 16), int(dst[:4], 16)
                for g in range(lo, hi + 1):
                    m[g] = d + (g - lo)
        return m

    subsets = []   # (basefont, glyphset, glyph order, unitsPerEm, gid->unicode)
    for info in page.get_fonts(full=True):
        xref, basefont = info[0], info[3]
        name, ext2, ftype2, data = doc.extract_font(xref)
        tt = TTFont(io.BytesIO(data))
        subsets.append((basefont.split("+")[-1], tt.getGlyphSet(), tt.getGlyphOrder(),
                        tt["head"].unitsPerEm, parse_tounicode(xref)))

    def pick_subset(span):
        base = span["font"].split("+")[-1]
        best, best_score = None, -1
        for sub in subsets:
            if sub[0] != base:
                continue
            score = sum(1 for uni, gid, _, _ in span["chars"] if sub[4].get(gid) == uni)
            if score > best_score:
                best, best_score = sub, score
        if best is None:
            raise RuntimeError("no embedded font for " + span["font"])
        return best, best_score == len(span["chars"])

    trace = page.get_texttrace()
    n_glyphs = 0
    n_inexact = 0
    shape = page.new_shape()
    for span in trace:
        if span["type"] != 0:       # 0 = fill; nothing else is used on this poster
            continue
        (base, gs, order, upem, _), exact = pick_subset(span)
        if not exact:
            n_inexact += 1
        size = span["size"]
        dx, dy = span["dir"]           # writing direction (unit vector), y down
        s = size / upem
        # glyph space (y up) → page space (y down, origin top-left):
        # x' = ox + s*(dx*x + dy*y)   ; y' = oy + s*(dy*x - dx*y)  (rotation by dir, then flip)
        for uni, gid, origin, bbox in span["chars"]:
            if gid < 0 or gid >= len(order):
                continue
            gname = order[gid]
            ox, oy = origin
            mat = (s * dx, s * dy, s * dy, -s * dx, ox, oy)
            pen = ShapePen(shape, mat, gs)
            gs[gname].draw(pen)
            n_glyphs += 1
        shape.finish(color=None, fill=span["color"], fill_opacity=span.get("opacity", 1.0),
                     even_odd=False)
    shape.commit()

    # strip the original text objects from the (single, cleaned) content stream
    page.clean_contents()
    xrefs = page.get_contents()
    for cx in xrefs:
        stream = doc.xref_stream(cx)
        new = re.sub(rb"\bBT\b.*?\bET\b", b"", stream, flags=re.S)
        doc.update_stream(cx, new)
    # drop the font dictionary from the page resources
    key, val = doc.xref_get_key(page.xref, "Resources")
    if key == "xref":
        rx = int(val.split()[0])
        doc.xref_set_key(rx, "Font", "null")
    else:
        doc.xref_set_key(page.xref, "Resources/Font", "null")
    doc.save(dst, garbage=4, deflate=True, clean=True)
    doc.close()
    print("spans without an exact subset match:", n_inexact)
    return n_glyphs


def previews(src):
    doc = pymupdf.open(src)
    page = doc[0]
    out = {}
    pix = page.get_pixmap(matrix=pymupdf.Matrix(20 / 72, 20 / 72))
    pix.save(os.path.join(ROOT, "preview.png"))
    out["preview.png"] = (pix.width, pix.height)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(37.5 / 72, 37.5 / 72))  # 150 DPI at 1/4 scale
    pix.save(os.path.join(ROOT, "poster_thumbnail.png"))
    out["poster_thumbnail.png"] = (pix.width, pix.height)
    top, bottom = 520, 2400
    for i in range(4):
        x0 = MARGIN + i * (COL_W + COL_GAP) - 12
        clip = pymupdf.Rect(x0, top, x0 + COL_W + 24, bottom)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), clip=clip)
        pix.save(os.path.join(ROOT, f"crop_col{i + 1}.png"))
        out[f"crop_col{i + 1}.png"] = (pix.width, pix.height)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(15 / 72, 15 / 72))
    pix.save(os.path.join(ROOT, "out", "distance_15dpi.png"))
    out["out/distance_15dpi.png"] = (pix.width, pix.height)
    return out


def pixel_diff(a, b, dpi=20):
    """Mean absolute pixel difference between two PDFs rendered at `dpi`."""
    import numpy as np
    pa = pymupdf.open(a)[0].get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72))
    pb = pymupdf.open(b)[0].get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72))
    A = np.frombuffer(pa.samples, dtype=np.uint8).reshape(pa.height, pa.width, pa.n).astype(int)
    B = np.frombuffer(pb.samples, dtype=np.uint8).reshape(pb.height, pb.width, pb.n).astype(int)
    d = np.abs(A - B)
    return float(d.mean()), float((d.max(axis=2) > 64).mean())


if __name__ == "__main__":
    n = outline_pdf(SRC, PRINT)
    print("outlined glyphs:", n)
    print("previews:", previews(SRC))
    print("print-vs-source pixel diff (mean abs, frac>64):", pixel_diff(SRC, PRINT))
