"""Measured text flow helpers (ReportLab Paragraph on a raw canvas)."""
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from . import style as S


def pstyle(name="body", size=S.SZ_BODY, leading=None, font=S.FONT, color=S.TEXT,
           align=TA_LEFT, space_after=0, space_before=0):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=leading or round(size * 1.24),
                          textColor=color, alignment=align,
                          spaceAfter=space_after, spaceBefore=space_before)


ST = {
    "body": pstyle("body"),
    "body_tight": pstyle("body_tight", leading=S.SZ_BODY * 1.18),
    "caption": pstyle("caption", size=S.SZ_CAPTION, color=S.TEXT_MUTED, leading=S.SZ_CAPTION * 1.22),
    "label": pstyle("label", size=S.SZ_LABEL),
    "small": pstyle("small", size=S.SZ_SMALL, color=S.TEXT_MUTED, leading=S.SZ_SMALL * 1.22),
    "small_dark": pstyle("small_dark", size=S.SZ_SMALL, color=S.TEXT, leading=S.SZ_SMALL * 1.22),
    "section": pstyle("section", size=S.SZ_SECTION, font=S.FONT_B, color=S.INK, leading=S.SZ_SECTION * 1.12),
    "subhead": pstyle("subhead", size=S.SZ_SUBHEAD, font=S.FONT_SB, color=S.INK, leading=S.SZ_SUBHEAD * 1.18),
    "takehome": pstyle("takehome", size=S.SZ_TAKEHOME, font=S.FONT_SB, leading=S.SZ_TAKEHOME * 1.2),
    "authors": pstyle("authors", size=S.SZ_AUTHORS, align=TA_CENTER, leading=S.SZ_AUTHORS * 1.22),
    "affil": pstyle("affil", size=S.SZ_AFFIL, align=TA_CENTER, color=S.TEXT_MUTED, leading=S.SZ_AFFIL * 1.22),
}


def para_height(text, width, st):
    p = Paragraph(text, st)
    _, h = p.wrap(width, 100000)
    return h, p


def draw_para(c, text, x, y_top, width, st=ST["body"]):
    """Draw a wrapped paragraph whose top edge is at y_top. Returns height used."""
    h, p = para_height(text, width, st)
    p.drawOn(c, x, y_top - h)
    return h


def string_w(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)


def draw_text(c, text, x, y, font=S.FONT, size=S.SZ_BODY, color=S.TEXT, anchor="w"):
    """Single-line text at baseline y. anchor in {w, c, e}."""
    c.setFont(font, size)
    c.setFillColor(color)
    if anchor == "w":
        c.drawString(x, y, text)
    elif anchor == "c":
        c.drawCentredString(x, y, text)
    else:
        c.drawRightString(x, y, text)


def fit_font_size(text, font, max_width, start, minimum):
    s = start
    while s > minimum and string_w(text, font, s) > max_width:
        s -= 1
    return s


class Column:
    """Vertical flow cursor for one poster column. Coordinates in points."""

    def __init__(self, c, x, y_top, width, y_bottom):
        self.c, self.x, self.y, self.w, self.y_bottom = c, x, y_top, width, y_bottom

    def space(self, h):
        self.y -= h

    def para(self, text, st=ST["body"], gap=0):
        h = draw_para(self.c, text, self.x, self.y, self.w, st)
        self.y -= h + gap
        return h

    def section(self, text):
        c = self.c
        h = draw_para(c, text, self.x, self.y, self.w, ST["section"])
        self.y -= h + 10
        c.setStrokeColor(S.BURNT_ORANGE)
        c.setLineWidth(5)
        c.line(self.x, self.y, self.x + 2.2 * S.IN, self.y)
        c.setStrokeColor(S.RULE)
        c.setLineWidth(2)
        c.line(self.x + 2.2 * S.IN, self.y, self.x + self.w, self.y)
        self.y -= 28

    def subhead(self, text, gap=10):
        h = draw_para(self.c, text, self.x, self.y, self.w, ST["subhead"])
        self.y -= h + gap

    def reserve(self, h):
        """Reserve a block of height h; returns (x, y_bottom, w, h)."""
        y_bottom = self.y - h
        self.y = y_bottom
        return self.x, y_bottom, self.w, h

    def remaining(self):
        return self.y - self.y_bottom
