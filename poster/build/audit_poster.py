#!/usr/bin/env python3
"""Production checks for poster.pdf / poster_print.pdf. Prints a report and
writes out/audit.json."""
import json
import os
import re
import subprocess
import sys

import pymupdf
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PDF = os.path.join(ROOT, "poster.pdf")
PRINT = os.path.join(ROOT, "poster_print.pdf")
HTML = os.path.join(ROOT, "out", "poster.html")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
GITHUB_URL = ("https://github.com/Devanshpandey/"
              "Multimodal-integration-for-coronary-artery-disease-risk-prediction")

report = {}


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


# 1 -------------------------------------------------------------- pdfinfo / pdffonts
def check_pdf_basics():
    out = {}
    for name, path in (("poster.pdf", PDF), ("poster_print.pdf", PRINT)):
        info = sh(["pdfinfo", path])
        pages = re.search(r"Pages:\s+(\d+)", info).group(1)
        size = re.search(r"Page size:\s+([\d.]+ x [\d.]+) pts", info).group(1)
        fonts = sh(["pdffonts", path]).splitlines()[2:]
        rows = [l.split() for l in fonts if l.strip()]
        out[name] = {
            "pages": int(pages), "page_size_pt": size,
            "n_fonts": len(rows),
            "all_embedded": all(r[-5] == "yes" for r in rows) if rows else True,
            "type3": any("Type 3" in l for l in fonts),
            "fonts": [l for l in fonts],
        }
    report["1_pdf_basics"] = out
    print("\n== 1. pdfinfo / pdffonts")
    for k, v in out.items():
        print(f"{k}: pages={v['pages']} size={v['page_size_pt']} pt fonts={v['n_fonts']} "
              f"all_embedded={v['all_embedded']} type3={v['type3']}")
        for l in v["fonts"]:
            print("   ", l)


# 2 -------------------------------------------------------------- raster audit
def check_images():
    doc = pymupdf.open(PDF)
    page = doc[0]
    rows = []
    for info in page.get_images(full=True):
        xref, w, h = info[0], info[2], info[3]
        for r in page.get_image_rects(xref):
            dpi_x = w / (r.width / 72)
            dpi_y = h / (r.height / 72)
            rows.append({"xref": xref, "px": [w, h], "placed_in": [round(r.width / 72, 2), round(r.height / 72, 2)],
                         "eff_dpi": [round(dpi_x), round(dpi_y)]})
    report["2_images"] = rows
    print("\n== 2. raster images (effective DPI at placed size)")
    print(sh(["pdfimages", "-list", PDF]))
    for r in rows:
        print(f"xref {r['xref']}: {r['px'][0]}x{r['px'][1]} px placed {r['placed_in'][0]}x{r['placed_in'][1]} in → {r['eff_dpi'][0]}x{r['eff_dpi'][1]} dpi")


# 3 -------------------------------------------------------------- text sizes
def check_text_sizes():
    doc = pymupdf.open(PDF)
    page = doc[0]
    spans = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if s["text"].strip():
                    spans.append((round(s["size"], 1), s["font"], s["text"].strip(), [round(v) for v in s["bbox"]]))
    spans.sort(key=lambda t: t[0])
    smallest = spans[:5]
    sizes = sorted(set(s[0] for s in spans))
    # body text = Inter 32 pt bullets; captions = Source Sans 26; chart labels = Source Sans 26/27
    body = [s for s in spans if s[1].startswith("Inter-") and s[0] < 32 and "sup" not in s[1]]
    report["3_text"] = {"min_pt": spans[0][0], "sizes_used": sizes, "five_smallest": smallest,
                        "n_spans": len(spans)}
    print("\n== 3. text sizes (PyMuPDF spans)")
    print("sizes used:", sizes)
    print("min size:", spans[0][0], "pt")
    print("five smallest spans:")
    for s in smallest:
        print(f"   {s[0]} pt  {s[1]:<26} {s[2][:70]!r}")
    print("Inter spans below 32 pt (should only be author superscripts):")
    for s in body:
        print(f"   {s[0]} pt {s[1]} {s[2][:40]!r}")


# 4 -------------------------------------------------------------- distance test (renders only)
def check_renders():
    d = os.path.join(ROOT, "out", "distance_15dpi.png")
    report["4_renders"] = {"distance_15dpi": d, "crops": [os.path.join(ROOT, f"crop_col{i}.png") for i in range(1, 5)]}
    print("\n== 4. distance / collision renders written:", d, "and crop_col1-4.png (inspect visually)")


# 5 -------------------------------------------------------------- QR
def check_qr():
    import zxingcpp
    from PIL import Image
    doc = pymupdf.open(PDF)
    page = doc[0]
    # locate the QR: it is the only vector drawing cluster in the top-right 400 pt
    clip = pymupdf.Rect(4700, 60, 5120, 420)
    pix = page.get_pixmap(dpi=300, clip=clip)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    res = zxingcpp.read_barcodes(img)
    texts = [r.text for r in res]
    ok = texts == [GITHUB_URL]
    # also from the full-page 300 DPI render of the print file
    pixp = pymupdf.open(PRINT)[0].get_pixmap(dpi=300, clip=clip)
    imgp = Image.frombytes("RGB", (pixp.width, pixp.height), pixp.samples)
    texts_p = [r.text for r in zxingcpp.read_barcodes(imgp)]
    report["5_qr"] = {"decoded": texts, "exact_match": ok, "decoded_print_pdf": texts_p}
    print("\n== 5. QR decode (zxing-cpp, 300 DPI render)")
    print("decoded:", texts, "exact match:", ok, "| print file:", texts_p == [GITHUB_URL])


# 6 -------------------------------------------------------------- contrast
def lum(hexc):
    r, g, b = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


PAIRS = [
    ("ink #333f48 on white", "#333f48", "#ffffff"),
    ("muted affiliations #4a5660 on white", "#4a5660", "#ffffff"),
    ("white on ink tagline/Cox box", "#ffffff", "#333f48"),
    ("white on orange section bar / imaging tag", "#ffffff", "#bf5700"),
    ("white on blue genetics tag", "#ffffff", "#0072b2"),
    ("white on dark-grey clinical tag", "#ffffff", "#5e6973"),
    ("orange presenter / hero on white", "#bf5700", "#ffffff"),
    ("ink on tile #f2f4f5", "#333f48", "#f2f4f5"),
    ("white caption on image overlay (80% ink over black)", "#ffffff", "#29323a"),
    ("extra-cardiac tint #f2b482 vs white (non-text; outlined)", "#f2b482", "#ffffff"),
    ("extra-cardiac outline #8a3f00 vs white", "#8a3f00", "#ffffff"),
]


def check_contrast():
    rows = []
    print("\n== 6. contrast")
    for name, fg, bg in PAIRS:
        c = contrast(fg, bg)
        thr = 3.0 if "non-text" in name or "outline" in name else 4.5
        rows.append({"pair": name, "ratio": round(c, 2), "threshold": thr, "ok": c >= thr})
        print(f"   {c:5.2f}:1  (need {thr})  {'OK ' if c >= thr else 'LOW'}  {name}")
    report["6_contrast"] = rows


# 7 -------------------------------------------------------------- safe margin
def check_margins():
    doc = pymupdf.open(PDF)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    m = 72.0
    worst = {"text": 1e9, "image": 1e9, "vector": 1e9}
    offenders = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if not s["text"].strip():
                    continue
                x0, y0, x1, y1 = s["bbox"]
                d = min(x0, y0, W - x1, H - y1)
                worst["text"] = min(worst["text"], d)
                if d < m:
                    offenders.append(("text", s["text"][:40], round(d, 1)))
    for info in page.get_images(full=True):
        for r in page.get_image_rects(info[0]):
            d = min(r.x0, r.y0, W - r.x1, H - r.y1)
            worst["image"] = min(worst["image"], d)
            if d < m:
                offenders.append(("image", info[0], round(d, 1)))
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.width >= W - 1 and r.height >= H - 1:
            continue  # page background fill
        d = min(r.x0, r.y0, W - r.x1, H - r.y1)
        worst["vector"] = min(worst["vector"], d)
        if d < m - 0.5:
            offenders.append(("vector", [round(v) for v in r], round(d, 1)))
    report["7_margins"] = {"worst_distance_pt": {k: round(v, 1) for k, v in worst.items()}, "offenders": offenders[:20]}
    print("\n== 7. safe margin (1.0 in = 72 pt)")
    print("closest approach to any edge (pt):", {k: round(v, 1) for k, v in worst.items()})
    print("offenders:", offenders[:20] if offenders else "none")


# 8 -------------------------------------------------------------- word count
def check_words():
    from playwright.sync_api import sync_playwright
    js = """() => {
      const words = s => s.trim().split(/\\s+/).filter(w => w.length).length;
      const txt = sel => [...document.querySelectorAll(sel)].map(e => e.innerText).join(' ');
      return {
        body_text_blocks: words(txt('.body-text')),
        pipeline_boxes_and_notes: words(txt('.pipe .box, .pipe .tag, .pipe figcaption, .pipe-card .note')),
        cohort_and_result_tiles: words(txt('.tile')),
        hero_subtitles: words(txt('.hero-sub, .stack .lbl')),
        captions: words(txt('.cap')),
        header: words(txt('.hdr, .tagline, .key')),
        footer: words(txt('footer')),
      }; }"""
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        pg.goto("file://" + HTML, wait_until="load")
        r = pg.evaluate(js)
        b.close()
    body_total = r["body_text_blocks"] + r["pipeline_boxes_and_notes"] + r["cohort_and_result_tiles"] + r["hero_subtitles"]
    r["BODY_TOTAL_excl_header_footer_captions"] = body_total
    report["8_words"] = r
    print("\n== 8. word count")
    for k, v in r.items():
        print(f"   {k}: {v}")


# --------------------------------------------------------------- hero token check
def check_hero_tokens():
    doc = pymupdf.open(PDF)
    txt = doc[0].get_text()
    ok = {t: (t in txt) for t in ("36.8%", "0.770 vs 0.666", "r ≈ 0.05")}
    i = txt.find("36.8%")
    report["hero_tokens"] = {"found": ok, "context_36_8": txt[max(0, i - 40): i + 60].replace("\n", "⏎")}
    print("\n== hero tokens in page.get_text():", ok)
    print("   context:", report["hero_tokens"]["context_36_8"])


if __name__ == "__main__":
    check_pdf_basics()
    check_images()
    check_text_sizes()
    check_renders()
    check_qr()
    check_contrast()
    check_margins()
    check_words()
    check_hero_tokens()
    with open(os.path.join(ROOT, "out", "audit.json"), "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    print("\nwrote out/audit.json")
