"""Shared style configuration for the ASHG 2026 poster build (design v3).

Units: PDF points via `IN` (1 in = 72 pt). Page 72 x 36 in.

Palette rationale (validated with the dataviz palette checker, light surface):
  INK  #14213D  deep navy, header band and headings (brand-neutral, pairs with burnt orange)
  ORANGE #BF5700  UT burnt orange: emphasis + "full model"
  IMAGING #0E9594 teal, GENETICS #4F5BD5 indigo, CLINICAL #6E7B86 slate.
  Adjacent-pair checks pass (CVD dE >= 15.5, normal-vision dE >= 18.1, contrast >= 3:1).
  The slate CLINICAL slot is below the chroma floor on purpose: it is the neutral
  baseline against which the other groups are compared, and identity is also carried by
  marker shape and direct labels. UT brand values were not re-verified online (host blocked).
"""
from pathlib import Path
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

IN = 72.0
PAGE_W_IN, PAGE_H_IN = 72.0, 36.0
PAGE_W, PAGE_H = PAGE_W_IN * IN, PAGE_H_IN * IN
MARGIN = 0.75 * IN

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# ---- colours -------------------------------------------------------------
INK = HexColor("#14213D")
INK_SOFT = HexColor("#2B3A5C")
BURNT_ORANGE = HexColor("#BF5700")
ORANGE_TINT = HexColor("#F7E9DE")
WHITE = HexColor("#FFFFFF")
PAPER = HexColor("#FFFFFF")
SAND = HexColor("#F4F1EA")
SAND_DEEP = HexColor("#E9E4D8")
TEXT = HexColor("#1E2A3A")
TEXT_MUTED = HexColor("#5A6675")
TEXT_ON_INK = HexColor("#F2F4F8")
TEXT_ON_INK_MUTED = HexColor("#B9C2D4")
RULE = HexColor("#D5D9DF")
GRID = HexColor("#E6E9EE")

COL_CLINICAL = HexColor("#6E7B86")
COL_GENETICS = HexColor("#4F5BD5")
COL_IMAGING = HexColor("#0E9594")
COL_FULL = BURNT_ORANGE
COL_IDP = HexColor("#A3ACB5")
COL_LINE = HexColor("#8B1A1A")       # fitted line in the hexbin (kept close to the original dark red)

# sequential ramp for the hexbin density (one hue, light -> ink)
HEX_RAMP = [(0.0, (0.90, 0.92, 0.95)), (0.45, (0.47, 0.60, 0.78)), (1.0, (0.078, 0.129, 0.239))]

# ---- type sizes (pt) ------------------------------------------------------
SZ_TITLE = 104
SZ_TAKEHOME = 42
SZ_AUTHORS = 36
SZ_AFFIL = 26
SZ_SECTION = 50
SZ_SUBHEAD = 36
SZ_BODY = 32
SZ_LABEL = 30
SZ_CAPTION = 27
SZ_SMALL = 25
SZ_STAT = 66
SZ_FINDING = 38

FONT = "SourceSans3"
FONT_B = "SourceSans3-Bold"
FONT_I = "SourceSans3-It"
FONT_SB = "SourceSans3-Semibold"
FONT_L = "SourceSans3-Light"
DISPLAY = "Fraunces-Bold"
DISPLAY_SB = "Fraunces-Semibold"


def register_fonts():
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_DIR / "SourceSans3-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_B, str(FONT_DIR / "SourceSans3-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_I, str(FONT_DIR / "SourceSans3-It.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SB, str(FONT_DIR / "SourceSans3-Semibold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_L, str(FONT_DIR / "SourceSans3-Light.ttf")))
    pdfmetrics.registerFont(TTFont(DISPLAY, str(FONT_DIR / "Fraunces-Display-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(DISPLAY_SB, str(FONT_DIR / "Fraunces-Display-Semibold.ttf")))
    addMapping(FONT, 0, 0, FONT)
    addMapping(FONT, 1, 0, FONT_B)
    addMapping(FONT, 0, 1, FONT_I)
    addMapping(FONT, 1, 1, FONT_B)
    pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_B, italic=FONT_I, boldItalic=FONT_B)
    pdfmetrics.registerFontFamily(DISPLAY, normal=DISPLAY, bold=DISPLAY, italic=DISPLAY, boldItalic=DISPLAY)


def hex_of(c: Color) -> str:
    return "#%02X%02X%02X" % (int(c.red * 255), int(c.green * 255), int(c.blue * 255))


def ramp(t, stops=HEX_RAMP):
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(stops[:-1], stops[1:]):
        if t <= t1:
            f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
            return Color(*[a + (b - a) * f for a, b in zip(c0, c1)])
    return Color(*stops[-1][1])
