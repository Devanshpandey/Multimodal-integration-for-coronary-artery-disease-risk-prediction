"""Vector QR code drawing (modules drawn as rectangles on the canvas)."""
import qrcode
from reportlab.lib.colors import black, white


def draw_qr(c, data, x, y, size, quiet=2, fg=black, bg=white, ec=qrcode.constants.ERROR_CORRECT_M):
    q = qrcode.QRCode(error_correction=ec, border=0)
    q.add_data(data)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    cell = size / (n + 2 * quiet)
    c.setFillColor(bg)
    c.rect(x, y, size, size, stroke=0, fill=1)
    c.setFillColor(fg)
    for r in range(n):
        for col in range(n):
            if m[r][col]:
                c.rect(x + (col + quiet) * cell, y + size - (r + 1 + quiet) * cell, cell, cell, stroke=0, fill=1)
    return n, cell
