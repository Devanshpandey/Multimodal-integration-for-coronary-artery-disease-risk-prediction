"""Chart generators for the poster. Every function returns an SVG string whose
width/height are in PDF points (1 in = 72 pt) and whose text stays real text
(svg.fonttype = 'none'), so the PDF text layer carries chart labels and the
text-size audit can see them.

All numbers are hard-coded from the manuscript / the repo's figure scripts;
see poster/NOTES.md for the provenance table.
"""
import io
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "fonts")
for fn in os.listdir(FONT_DIR):
    if fn.endswith(".ttf"):
        font_manager.fontManager.addfont(os.path.join(FONT_DIR, fn))

# ---- palette (identical to v2) -------------------------------------------
C_IMG = "#bf5700"      # imaging (cardiac MRI)
C_EXTRA = "#f2b482"    # extra-cardiac imaging (tint; always drawn with a dark outline)
C_EXTRA_EDGE = "#8a3f00"
C_PRS = "#0072b2"      # genetics (PRS)
C_CLIN = "#8c8c8c"     # clinical / guideline scores
C_COMB = "#333f48"     # combined model
C_INK = "#333f48"
C_GRID = "#d9dde2"
C_RED = "#b22222"

# ---- type sizes (pt) ------------------------------------------------------
TICK = 26
CAT = 27
VAL = 27
AXL = 27
NOTE = 26

plt.rcParams.update({
    "svg.fonttype": "none",
    "font.family": "Source Sans 3",
    "font.size": TICK,
    "axes.edgecolor": C_INK,
    "axes.labelcolor": C_INK,
    "xtick.color": C_INK,
    "ytick.color": C_INK,
    "text.color": C_INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.labelsize": TICK,
    "ytick.labelsize": CAT,
    "axes.labelsize": AXL,
    "axes.linewidth": 1.4,
    "xtick.major.width": 1.4,
    "ytick.major.width": 1.4,
    "xtick.major.size": 8,
    "ytick.major.size": 0,
    "svg.hashsalt": "poster",
})


def text_w(txt, size=CAT, weight="normal"):
    """Width in pt of `txt` set in Source Sans 3 at `size` pt (worst line)."""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family="Source Sans 3", weight=weight)
    return max(TextPath((0, 0), line, size=size, prop=fp).get_extents().width for line in txt.split("\n"))


def left_frac(labels, w_in, size=CAT, pad=18, extra=0):
    """Left axes edge (figure fraction) leaving room for the longest label."""
    w = max(text_w(l, size, "bold") for l in labels) + pad + extra
    return w / (w_in * 72)


def _svg(fig):
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches=None, pad_inches=0)
    plt.close(fig)
    s = buf.getvalue()
    # strip XML prolog / DOCTYPE so the SVG can be inlined in HTML
    i = s.find("<svg")
    return s[i:]


def _fig(w_in, h_in, left, right, bottom, top):
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([left, bottom, right - left, top - bottom])
    ax.xaxis.grid(True, color=C_GRID, linewidth=1.2)
    ax.set_axisbelow(True)
    return fig, ax


def _hbar(ax, labels, values, colors, xmin, xmax, fmt="{:.3f}", bold=None,
          edge=None, height=0.62, label_pad=0.004):
    y = np.arange(len(labels))[::-1]
    for yi, v, c in zip(y, values, colors):
        ec = C_EXTRA_EDGE if c == C_EXTRA else "none"
        if edge is not None:
            ec = edge
        ax.barh(yi, v - xmin, left=xmin, height=height, color=c,
                edgecolor=ec, linewidth=1.8 if ec != "none" else 0)
        ax.text(v + label_pad * (xmax - xmin) / 0.2, yi, fmt.format(v), va="center",
                ha="left", fontsize=VAL, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    if bold:
        for t, b in zip(ax.get_yticklabels(), bold):
            if b:
                t.set_fontweight("bold")
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.tick_params(axis="y", length=0, pad=10)
    return y


# ---------------------------------------------------------------------------
def idp_vs_embeddings(w_in=16.2, h_in=5.0):
    """Fig. 2b: AUC of IDPs vs deep embeddings vs both (logistic models)."""
    labels = ["Conventional IDPs", "Deep embeddings", "Both combined"]
    fig, ax = _fig(w_in, h_in, left_frac(labels, w_in), 0.985, 0.24, 0.97)
    vals = [0.666, 0.770, 0.775]
    cols = [C_CLIN, C_IMG, C_COMB]
    y = _hbar(ax, labels, vals, cols, 0.60, 0.80)
    ax.set_xticks([0.60, 0.65, 0.70, 0.75, 0.80])
    ax.set_xlabel("AUC, CAD classification (axis starts at 0.60)")
    ax.text(0.602, y[1] + 0.45, "embeddings vs IDPs: LR = 414.5, p = 4.1×10⁻⁷⁶",
            fontsize=NOTE, va="center", ha="left")
    ax.text(0.602, y[2] + 0.45, "adding IDPs to embeddings: LR = 45.1, p = 4.6×10⁻⁶",
            fontsize=NOTE, va="center", ha="left")
    return _svg(fig)


def cca(w_in=16.2, h_in=5.0):
    """Fig. 2c / Supp. Fig. 6: canonical correlation of CV1 per cardiac view."""
    labels = ["2-chamber long axis", "3-chamber long axis",
              "4-chamber long axis", "Aortic distensibility"]
    fig, ax = _fig(w_in, h_in, left_frac(labels, w_in), 0.985, 0.24, 0.97)
    vals = [0.812, 0.789, 0.841, 0.816]
    _hbar(ax, labels, vals, [C_IMG] * 4, 0.60, 0.90)
    ax.set_xticks([0.60, 0.70, 0.80, 0.90])
    ax.set_xlabel("Canonical correlation (CV1), embeddings vs IDPs (axis starts at 0.60)")
    return _svg(fig)


def pretraining_3d(w_in=8.0, h_in=5.0):
    """Supp. Fig. 3: AUC of 3D cardiac encoders by pretraining source."""
    labels = ["3D ResNet-18", "MC3-18", "R(2+1)D", "Med3D (selected)"]
    fig, ax = _fig(w_in, h_in, left_frac(labels, w_in), 0.97, 0.33, 0.97)
    vals = [0.608, 0.618, 0.650, 0.681]
    cols = [C_CLIN, C_CLIN, C_CLIN, C_IMG]
    _hbar(ax, labels, vals, cols, 0.50, 0.72)
    ax.set_xticks([0.50, 0.55, 0.60, 0.65, 0.70])
    ax.set_xlabel("AUC, 3D cardiac encoders\nKinetics video (grey) vs Med3D")
    return _svg(fig)


def pretraining_2d(w_in=8.0, h_in=5.0):
    """Supp. Fig. 4b / Supp. Table 3: accuracy of 2D encoders, ImageNet → RadImageNet."""
    labels = ["Liver MRI", "Pancreas MRI", "DXA"]
    fig, ax = _fig(w_in, h_in, left_frac(labels, w_in, extra=70), 0.97, 0.33, 0.97)
    a = [0.50, 0.53, 0.54]
    b = [0.64, 0.63, 0.57]
    y = np.arange(len(labels))[::-1]
    for yi, x0, x1 in zip(y, a, b):
        ax.plot([x0, x1], [yi, yi], color=C_CLIN, linewidth=5, solid_capstyle="round", zorder=1)
        ax.scatter([x0], [yi], s=420, color=C_CLIN, zorder=2)
        ax.scatter([x1], [yi], s=520, color=C_IMG, zorder=3)
        ax.text(x0 - 0.012, yi, f"{x0:.2f}", ha="right", va="center", fontsize=VAL)
        ax.text(x1 + 0.012, yi, f"{x1:.2f}", ha="left", va="center", fontsize=VAL, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0.42, 0.72)
    ax.set_ylim(-0.7, len(labels) - 0.3)
    ax.set_xticks([0.45, 0.50, 0.55, 0.60, 0.65, 0.70])
    ax.tick_params(axis="y", length=0, pad=10)
    ax.set_xlabel("Accuracy, 2D encoders\nImageNet (grey) → RadImageNet")
    return _svg(fig)


# ---------------------------------------------------------------------------
def hexbin(size_in=8.0, n=29075, r=0.046, seed=7):
    """Fig. 3c: imaging risk score vs polygenic risk score.

    NOTE: the participant-level scores are not in the repository, so this is a
    synthetic bivariate-normal rendering with the reported n and Pearson r
    (0.046 in Fig. 3c; 'r ≈ 0.05' in the text). It is labelled as such on the
    poster. Swap in the real Fig. 3c panel if a high-resolution export exists.
    """
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, 2))
    x = z[:, 0]
    y = r * x + np.sqrt(1 - r ** 2) * z[:, 1]
    fig = plt.figure(figsize=(size_in, size_in))
    ax = fig.add_axes([0.16, 0.14, 0.82, 0.84])
    ax.hexbin(x, y, gridsize=34, cmap="Blues", mincnt=1, linewidths=0.2,
              edgecolors="face", extent=(-4.2, 4.2, -4.2, 4.2))
    b = np.polyfit(x, y, 1)
    xs = np.array([-4, 4])
    ax.plot(xs, b[0] * xs + b[1], color=C_RED, linewidth=4)
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(-4.2, 4.2)
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_yticks([-4, -2, 0, 2, 4])
    ax.tick_params(axis="y", length=8)
    ax.yaxis.grid(True, color=C_GRID, linewidth=1.2)
    ax.set_xlabel("Polygenic risk score (SD)")
    ax.set_ylabel("Imaging risk score (SD)")
    ax.text(-4.0, 3.9, f"n = {n:,} · r = {r:.3f} · ρ = 0.057",
            fontsize=NOTE, va="top", ha="left")
    ax.text(4.05, -4.05, "schematic rendering of the reported r",
            fontsize=NOTE, va="bottom", ha="right", style="italic")
    return _svg(fig)


# Fig. 3a/b data (Scripts/revised_figures/Figure3_integrated_revised.R)
R2_ROWS = [
    # label, R² alone, relative change (%) when removed, colour
    ("Long-axis cardiac MRI", 0.237157, -13.929790, C_IMG),
    ("Medication", 0.180086, -10.613794, C_CLIN),
    ("Aortic distensibility MRI", 0.162828, -7.908534, C_IMG),
    ("Baseline covariates", 0.161890, -6.114735, C_CLIN),
    ("Blood-flow MRI", 0.112434, -0.654914, C_IMG),
    ("Liver MRI", 0.096386, -0.238650, C_EXTRA),
    ("Pancreas MRI", 0.088265, -0.330359, C_EXTRA),
    ("Lipids", 0.071645, -3.519219, C_CLIN),
    ("Polygenic risk score", 0.067548, -9.614460, C_PRS),
    ("ECG", 0.046793, -2.277529, C_CLIN),
    ("Blood pressure", 0.037717, -0.698111, C_CLIN),
    ("DXA", 0.036446, -0.483912, C_EXTRA),
    ("Diabetes", 0.029889, -1.858552, C_CLIN),
]


def r2_loo(w_in=16.2, h_in=7.0):
    """Fig. 3a (left) and 3b (right), sharing the category axis."""
    fig = plt.figure(figsize=(w_in, h_in))
    n = len(R2_ROWS)
    y = np.arange(n)[::-1]
    labels = [r[0] for r in R2_ROWS]
    cols = [r[3] for r in R2_ROWS]
    lf = left_frac(labels, w_in)
    wL = (0.985 - lf - 0.085) / 2
    axL = fig.add_axes([lf, 0.19, wL, 0.80])
    axR = fig.add_axes([lf + wL + 0.085, 0.19, wL, 0.80])
    for ax in (axL, axR):
        ax.xaxis.grid(True, color=C_GRID, linewidth=1.2)
        ax.set_axisbelow(True)
        ax.set_ylim(-0.6, n - 0.4)
        ax.tick_params(axis="y", length=0, pad=10)
    # left: R² alone
    for yi, r, c in zip(y, R2_ROWS, cols):
        ec = C_EXTRA_EDGE if c == C_EXTRA else "none"
        axL.barh(yi, r[1], height=0.66, color=c, edgecolor=ec, linewidth=1.8 if ec != "none" else 0)
        axL.text(r[1] + 0.006, yi, f"{r[1]:.2f}", va="center", ha="left", fontsize=VAL, fontweight="bold")
    axL.set_yticks(y)
    axL.set_yticklabels(labels)
    axL.set_xlim(0, 0.30)
    axL.set_xticks([0, 0.1, 0.2, 0.3])
    axL.set_xlabel("R², group modelled alone")
    # right: relative change when removed (negative)
    for yi, r, c in zip(y, R2_ROWS, cols):
        ec = C_EXTRA_EDGE if c == C_EXTRA else "none"
        axR.barh(yi, r[2], height=0.66, color=c, edgecolor=ec, linewidth=1.8 if ec != "none" else 0)
        axR.text(r[2] - 0.3, yi, f"{r[2]:.1f}%", va="center", ha="right", fontsize=VAL, fontweight="bold")
    axR.set_yticks(y)
    axR.set_yticklabels([""] * n)
    axR.set_xlim(-17.5, 0)
    axR.set_xticks([-15, -10, -5, 0])
    axR.set_xlabel("Change in R² when the group is removed (%)")
    axR.spines["left"].set_visible(False)
    axR.spines["right"].set_visible(True)
    axR.yaxis.tick_right()
    return _svg(fig)


# Fig. 3f data (Figure3_integrated_revised.R): unique variance alone and after the
# single strongest adjustment ('+ Baseline'); see NOTES.md for the interpretation.
UNIQUE_ROWS = [
    ("Long-axis cardiac MRI", 0.237157, 0.237157 - 0.138022, C_IMG),
    ("Aortic distensibility MRI", 0.162828, 0.162828 - 0.107761, C_IMG),
    ("Polygenic risk score", 0.067548, 0.067548 - 0.016412, C_PRS),
    ("Blood-flow MRI", 0.112434, 0.112434 - 0.091996, C_IMG),
    ("Liver MRI", 0.096386, 0.096386 - 0.091256, C_EXTRA),
    ("Pancreas MRI", 0.088265, 0.088265 - 0.080601, C_EXTRA),
    ("DXA", 0.036446, 0.036446 - 0.032364, C_EXTRA),
]


def unique_variance(w_in=16.2, h_in=5.0):
    fig, ax = _fig(w_in, h_in, left_frac([r[0] for r in UNIQUE_ROWS], w_in), 0.86, 0.24, 0.97)
    n = len(UNIQUE_ROWS)
    y = np.arange(n)[::-1]
    for yi, (lab, a, b, c) in zip(y, UNIQUE_ROWS):
        ax.plot([b, a], [yi, yi], color=C_CLIN, linewidth=5, solid_capstyle="round", zorder=1)
        ax.scatter([a], [yi], s=460, color=C_CLIN, zorder=2)
        ec = C_EXTRA_EDGE if c == C_EXTRA else "none"
        ax.scatter([b], [yi], s=560, color=c, edgecolor=ec, linewidth=1.8, zorder=3)
        ax.text(a + 0.006, yi, f"{a:.2f}", ha="left", va="center", fontsize=VAL)
        ax.text(b - 0.006, yi, f"{b:.2f}", ha="right", va="center", fontsize=VAL, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in UNIQUE_ROWS])
    ax.set_xlim(-0.03, 0.27)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xticks([0, 0.1, 0.2])
    ax.tick_params(axis="y", length=0, pad=10)
    ax.set_xlabel("Unique variance (R²): grey = alone · coloured = after baseline adjustment")
    # bracket for liver / pancreas / DXA (rows 4-6 → y = 2,1,0)
    xb = 0.255
    ax.plot([xb, xb], [-0.35, 2.35], color=C_INK, linewidth=2, clip_on=False)
    ax.plot([xb - 0.006, xb], [-0.35, -0.35], color=C_INK, linewidth=2, clip_on=False)
    ax.plot([xb - 0.006, xb], [2.35, 2.35], color=C_INK, linewidth=2, clip_on=False)
    ax.text(xb + 0.008, 1.0, "≈ 0 after\nadjustment", va="center", ha="left",
            fontsize=NOTE, clip_on=False)
    return _svg(fig)


# ---------------------------------------------------------------------------
CINDEX_ROWS = [
    ("PRS alone†", 0.621, C_PRS, False),
    ("SCORE2", 0.722, C_CLIN, False),
    ("Pooled Cohort Equations", 0.725, C_CLIN, False),
    ("Clinical", 0.749, C_CLIN, True),
    ("Imaging alone", 0.772, C_IMG, False),
    ("Clinical + PRS", 0.788, C_COMB, True),
    ("PRS + Imaging", 0.789, C_COMB, False),
    ("Clinical + Imaging", 0.813, C_COMB, True),
    ("Full: Clinical + PRS + Imaging", 0.819, C_COMB, True),
]


def cindex(w_in=16.2, h_in=5.0):
    """Supp. Fig. 8d: C-index ablation and guideline scores on the held-out set."""
    labels = [r[0] for r in CINDEX_ROWS]
    fig, ax = _fig(w_in, h_in, left_frac(labels, w_in), 0.985, 0.17, 0.985)
    vals = [r[1] for r in CINDEX_ROWS]
    cols = [r[2] for r in CINDEX_ROWS]
    bold = [r[3] for r in CINDEX_ROWS]
    _hbar(ax, labels, vals, cols, 0.55, 0.85, bold=bold, height=0.7)
    ax.set_xticks([0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85])
    ax.set_xlabel("")  # axis title carried by the caption to save height
    return _svg(fig)


TIERS = [
    ("Overall\ncohort", 1.6, C_CLIN),
    ("Tier 1\nclinical", 8.0, C_CLIN),
    ("Tier 2\n+ PRS", 11.3, C_PRS),
    ("Tier 3\n+ imaging", 15.9, C_IMG),
    ("Top quintile\nof both, Tier 3", 36.8, C_COMB),
]


def tiers(w_in=16.2, h_in=5.5):
    """Fig. 4e: 5-year CAD incidence under sequential stratification (held-out set)."""
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([0.075, 0.27, 0.80, 0.71])
    ax.yaxis.grid(True, color=C_GRID, linewidth=1.2)
    ax.set_axisbelow(True)
    x = np.arange(len(TIERS))
    for xi, (lab, v, c) in zip(x, TIERS):
        ax.bar(xi, v, width=0.62, color=c)
        ax.text(xi, v + 0.8, f"{v:.1f}%", ha="center", va="bottom", fontsize=VAL, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([t[0] for t in TIERS])
    ax.tick_params(axis="x", length=0, pad=8)
    ax.set_ylim(0, 42)
    ax.set_yticks([0, 10, 20, 30, 40])
    ax.set_ylabel("5-yr incidence (%)")
    # ≈23× bracket beside (to the right of) the top bar
    xb = x[-1] + 0.46
    ax.plot([xb, xb], [1.6, 36.8], color=C_INK, linewidth=2.2, clip_on=False)
    for yy in (1.6, 36.8):
        ax.plot([xb, xb + 0.06], [yy, yy], color=C_INK, linewidth=2.2, clip_on=False)
    ax.text(xb + 0.10, 19.2, "≈23×\nthe cohort\nevent rate", va="center", ha="left",
            fontsize=NOTE, fontweight="bold", clip_on=False)
    return _svg(fig)


ALL = {
    "idp_vs_embeddings": idp_vs_embeddings,
    "cca": cca,
    "pretraining_3d": pretraining_3d,
    "pretraining_2d": pretraining_2d,
    "hexbin": hexbin,
    "r2_loo": r2_loo,
    "unique_variance": unique_variance,
    "cindex": cindex,
    "tiers": tiers,
}

if __name__ == "__main__":
    out = os.path.join(HERE, "..", "out", "charts")
    os.makedirs(out, exist_ok=True)
    for k, f in ALL.items():
        s = f()
        with open(os.path.join(out, k + ".svg"), "w") as fh:
            fh.write(s)
        print(k, len(s))
