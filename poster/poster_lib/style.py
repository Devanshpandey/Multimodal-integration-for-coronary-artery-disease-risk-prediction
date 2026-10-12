"""Shared style configuration for the ASHG 2026 poster build.

All physical units are expressed in PDF points via the `IN` constant (1 in = 72 pt).
Colours: UT Austin primary palette values (burnt orange #BF5700, charcoal #333F48,
limestone #D6D2C4) and secondary accents (#005F86 blue, #00A9B7 turquoise) are taken
from the UT brand guide as known to the author of this script; the live brand page
could not be reached from the build environment, so VERIFY against
https://brand.utexas.edu before final printing (see docs/SOURCE_AND_QA.md).
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
BURNT_ORANGE = HexColor("#BF5700")
CHARCOAL = HexColor("#333F48")
LIMESTONE = HexColor("#D6D2C4")
UT_BLUE = HexColor("#005F86")
UT_TURQUOISE = HexColor("#00A9B7")
WHITE = HexColor("#FFFFFF")
TEXT = CHARCOAL
TEXT_MUTED = HexColor("#5B6770")
RULE = HexColor("#C9CED2")
PANEL_BG = HexColor("#F6F5F2")
PANEL_BG2 = HexColor("#FBF3EC")

# scientific group colours (stable across all modules)
COL_CLINICAL = HexColor("#6E7B86")      # neutral grey
COL_GENETICS = UT_BLUE                  # blue
COL_IMAGING = HexColor("#00828F")       # darker turquoise for contrast on white
COL_IMAGING_LIGHT = UT_TURQUOISE
COL_FULL = BURNT_ORANGE                 # burnt orange
COL_IDP = HexColor("#9CA7B0")

# ---- type sizes (pt) ------------------------------------------------------
SZ_TITLE = 100
SZ_TAKEHOME = 50
SZ_AUTHORS = 36
SZ_AFFIL = 27
SZ_SECTION = 46
SZ_SUBHEAD = 36
SZ_BODY = 33
SZ_BODY_LEAD = 41
SZ_LABEL = 30          # plot labels / ticks
SZ_CAPTION = 27
SZ_SMALL = 26          # references / disclosures
SZ_STAT = 64           # big numbers in stat tiles

FONT = "SourceSans3"
FONT_B = "SourceSans3-Bold"
FONT_I = "SourceSans3-It"
FONT_SB = "SourceSans3-Semibold"
FONT_L = "SourceSans3-Light"


def register_fonts():
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_DIR / "SourceSans3-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_B, str(FONT_DIR / "SourceSans3-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_I, str(FONT_DIR / "SourceSans3-It.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_SB, str(FONT_DIR / "SourceSans3-Semibold.ttf")))
    pdfmetrics.registerFont(TTFont(FONT_L, str(FONT_DIR / "SourceSans3-Light.ttf")))
    # <b>/<i> mapping for Paragraph markup
    addMapping(FONT, 0, 0, FONT)
    addMapping(FONT, 1, 0, FONT_B)
    addMapping(FONT, 0, 1, FONT_I)
    addMapping(FONT, 1, 1, FONT_B)
    pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_B, italic=FONT_I, boldItalic=FONT_B)


def hex_of(c: Color) -> str:
    return "#%02X%02X%02X" % (int(c.red * 255), int(c.green * 255), int(c.blue * 255))
