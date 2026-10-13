#!/usr/bin/env python3
"""Automated QA for the built poster: geometry, fonts, images, links, QR, text, previews."""
import json, subprocess, sys, re
from pathlib import Path
import pypdf, cv2, numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent
PDF = ROOT / "output" / "ASHG2026_Devansh_Pandey_Poster_72x36.pdf"
rep = json.loads((ROOT / "qa" / "build_report.json").read_text())
r = pypdf.PdfReader(str(PDF)); p = r.pages[0]
mb = [float(v) for v in p.mediabox]; tb = [float(v) for v in p.trimbox]
rep["geometry"] = {"pages": len(r.pages), "mediabox_pt": mb, "trimbox_pt": tb,
                   "size_in": [(mb[2]-mb[0])/72, (mb[3]-mb[1])/72], "ok": len(r.pages)==1 and mb==[0,0,5184,2592] and tb==mb}
fonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True).stdout
rows = [l.split() for l in fonts.splitlines()[2:] if l.strip()]
rep["fonts"] = {"table": fonts, "all_embedded": all(x[3] == "yes" for x in rows), "count": len(rows)}
imgs = subprocess.run(["pdfimages", "-list", str(PDF)], capture_output=True, text=True).stdout
rep["images"] = {"table": imgs, "min_ppi": min(int(l.split()[-4]) for l in imgs.splitlines()[2:] if l.strip())}
links = []
for a in p.get("/Annots", []) or []:
    a = a.get_object()
    if "/A" in a and "/URI" in a["/A"]:
        links.append(a["/A"]["/URI"])
rep["links"] = links
text = p.extract_text()
rep["text"] = {"chars": len(text), "has_title": "Multimodal integration reveals" in text,
               "numbers_present": {k: (k in text) for k in ["42,351", "677", "0.666", "0.770", "0.065", "0.4%", "29,075",
                                                            "0.749", "0.788", "0.813", "0.819", "8.0%", "11.3%", "15.9%", "36.8%",
                                                            "0.805", "0.822", "0.785", "0.795", "0.762", "0.748", "0.751", "0.732",
                                                            "0.634", "65439", "38.41%", "14.42%", "0.15%"]}}
# previews
subprocess.run(["pdftoppm", "-r", "40", "-png", "-singlefile", str(PDF), str(ROOT/"output"/"ASHG2026_Devansh_Pandey_Poster_preview")], check=True)
subprocess.run(["pdftoppm", "-r", "20", "-png", "-singlefile", "-gray", str(PDF), str(ROOT/"qa"/"grayscale_preview")], check=True)
# QR decode from a 150-dpi render of the footer
subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", "-x", str(int(21.4*150)), "-y", str(int(33.4*150)), "-W", str(int(3.2*150)), "-H", str(int(2.4*150)), str(PDF), str(ROOT/"qa"/"qr_crop")], check=True)
img = cv2.imread(str(ROOT/"qa"/"qr_crop.png"))
img = cv2.copyMakeBorder(img, 60, 60, 60, 60, cv2.BORDER_CONSTANT, value=(255, 255, 255))
data, pts, _ = cv2.QRCodeDetector().detectAndDecode(img)
if not data:
    big = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    data, pts, _ = cv2.QRCodeDetector().detectAndDecode(big)
rep["qr"] = {"decoded": data, "ok": data == "https://www.medrxiv.org/content/10.1101/2025.10.09.25337677"}
# cap-height of major lettering (Source Sans 3 cap height = 0.660 em)
cap = 0.660
rep["cap_heights_in"] = {"title": round(rep["title_pt"]*cap/72, 2), "takehome": round(rep["takehome_pt"]*cap/72, 2),
                         "section": round(46*cap/72, 2), "body": round(33*cap/72, 2), "caption": round(27*cap/72, 2), "footer": round(26*cap/72, 2)}
rep["file_size_mb"] = round(PDF.stat().st_size/1e6, 2)
(ROOT/"qa"/"qa_report.json").write_text(json.dumps(rep, indent=2))
print(json.dumps({k: rep[k] for k in ["geometry", "links", "qr", "cap_heights_in", "file_size_mb"]}, indent=2))
print("fonts embedded:", rep["fonts"]["all_embedded"], "| min image ppi:", rep["images"]["min_ppi"])
print("missing numbers:", [k for k, v in rep["text"]["numbers_present"].items() if not v])
