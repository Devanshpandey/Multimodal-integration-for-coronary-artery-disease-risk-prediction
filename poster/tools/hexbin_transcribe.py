"""Transcribe the Fig. 3c hexbin raster (819x658 crop) into a vector cell list.
Outputs hexcells.json: lattice params, per-cell colour, regression line endpoints, fidelity score."""
import numpy as np, json
from PIL import Image, ImageDraw
im = np.asarray(Image.open('/home/user/Multimodal-integration-for-coronary-artery-disease-risk-prediction/poster/assets/figures/fig3c_hexbin_plotarea.png').convert('RGB')).astype(float)
H, W, _ = im.shape
lum = im.mean(axis=2)
red = (im[:,:,0] > 90) & (im[:,:,1] < 60) & (im[:,:,2] < 60)
hexmask = (lum < 229) & ~red           # hex fills (grey88=224 and darker); gridlines ~235; white 255
# ---- lattice from 2D autocorrelation of the edge map (peaks at (w,0) and (w/2, dy_row))
gx=np.abs(np.diff(lum,axis=1,prepend=lum[:,:1])); gy=np.abs(np.diff(lum,axis=0,prepend=lum[:1,:]))
e=(gx+gy); e[red]=0; e[np.roll(red,1,0)]=0; e[np.roll(red,1,1)]=0
sub=e[H//2-200:H//2+200, W//2-200:W//2+200]; sub=sub-sub.mean()
F=np.fft.fft2(sub); ac=np.fft.fftshift(np.real(np.fft.ifft2(F*np.conj(F)))); cy,cx=np.array(ac.shape)//2
def refine1d(vals, i):
    y0,y1,y2=vals[i-1],vals[i],vals[i+1]; den=y0-2*y1+y2
    return i + (0.5*(y0-y2)/den if abs(den)>1e-9 else 0)
rowac=ac[cy, cx:cx+40]; wi=8+int(np.argmax(rowac[8:20])); w_px=refine1d(rowac, wi)
colac=ac[cy-30:cy+31, cx+int(round(w_px/2))]; di=int(np.argmax(colac[30+8:30+25]))+8; dy_row=refine1d(colac, 30+di)-30
dx_row=w_px/2
print(f"lattice: w={w_px:.3f} px, dy_row={dy_row:.3f} px, hex height={dy_row/0.75:.2f} px")
# ---- phase search: offset maximising within-cell uniformity (inscribed disc samples)
r = 0.30*w_px
angs = np.linspace(0, 2*np.pi, 12, endpoint=False)
def cells(x0, y0):
    out=[]
    nrows = int(H/dy_row)+2; ncols=int(W/w_px)+2
    for j in range(-1, nrows):
        yc = y0 + j*dy_row
        off = (j % 2)*dx_row
        for i in range(-1, ncols):
            xc = x0 + off + i*w_px
            if 0<=xc<W and 0<=yc<H: out.append((i,j,xc,yc))
    return out
def uniformity(x0,y0):
    cs = cells(x0,y0); tot=0; n=0
    for i,j,xc,yc in cs:
        xs = np.clip((xc + r*np.cos(angs)).astype(int),0,W-1); ys=np.clip((yc + r*np.sin(angs)).astype(int),0,H-1)
        px = im[ys,xs]; m = ~red[ys,xs]
        if m.sum()<6: continue
        if hexmask[ys,xs][m].mean()<0.5: continue
        tot += px[m].std(axis=0).sum(); n+=1
    return tot/n if n>=300 else 1e9
best=None
for x0 in np.arange(0, w_px, 0.5):
    for y0 in np.arange(0, dy_row, 0.5):
        u = uniformity(x0,y0)
        if best is None or u<best[0]: best=(u,x0,y0)
u,x0,y0 = best
print(f"phase: x0={x0:.2f} y0={y0:.2f} uniformity={u:.2f}")
# ---- sample colours
rr = 0.40*w_px
yy, xx = np.mgrid[0:H, 0:W]
cell_list=[]
for i,j,xc,yc in cells(x0,y0):
    m = ((xx-xc)**2 + (yy-yc)**2 <= rr*rr)
    px = im[m & ~red]; nred = int((m & red).sum()); nall=int(m.sum())
    if nall==0: continue
    if px.shape[0] < 0.25*nall:
        cell_list.append(dict(i=i,j=j,x=xc,y=yc,rgb=None,covered=True)); continue
    col = np.median(px,axis=0)
    if col.min() > 236 and col.mean()>240:   # white or gridline
        continue
    cell_list.append(dict(i=i,j=j,x=float(xc),y=float(yc),rgb=[int(v) for v in col],covered=False))
# fill covered cells from neighbours
known = {(c['i'],c['j']):c for c in cell_list if not c['covered']}
for c in cell_list:
    if c['covered']:
        nb=[]
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
            k=known.get((c['i']+di,c['j']+dj))
            if k: nb.append(k['rgb'])
        c['rgb'] = [int(v) for v in np.mean(nb,axis=0)] if nb else None
cell_list=[c for c in cell_list if c['rgb'] is not None]
# ---- regression line: fit to red pixel centres
ys_r, xs_r = np.nonzero(red)
A = np.vstack([xs_r, np.ones_like(xs_r)]).T
slope, icpt = np.linalg.lstsq(A, ys_r, rcond=None)[0]
xmin, xmax = xs_r.min(), xs_r.max()
# thickness: vertical extent of red at centre column
colr = red[:, (xmin+xmax)//2]; thick = int(colr.sum())
line = dict(x1=float(xmin), y1=float(slope*xmin+icpt), x2=float(xmax), y2=float(slope*xmax+icpt), thickness_px=thick)
print("line", line, "cells", len(cell_list))
# ---- fidelity: re-render and compare
def hexpoly(xc,yc,w):
    hh = (dy_row/0.75)/2  # half of vertex-to-vertex height
    return [(xc, yc-hh), (xc+w/2, yc-hh/2), (xc+w/2, yc+hh/2), (xc, yc+hh), (xc-w/2, yc+hh/2), (xc-w/2, yc-hh/2)]
canvas = Image.new('RGB', (W,H), (255,255,255)); d = ImageDraw.Draw(canvas)
for c in cell_list: d.polygon(hexpoly(c['x'],c['y'],w_px+0.6), fill=tuple(c['rgb']))
d.line([(line['x1'],line['y1']),(line['x2'],line['y2'])], fill=(139,0,0), width=thick)
canvas.save('hex_vector_render.png')
ren = np.asarray(canvas).astype(float)
diff = np.abs(ren-im).max(axis=2)
mask_eval = ~((lum>229)&(np.abs(ren-im).max(axis=2)<30))  # ignore background agreement trivially? keep all
agree = (diff < 24).mean(); agree_nonwhite = (diff[hexmask] < 24).mean()
print(f"fidelity: {agree*100:.1f}% of all pixels within 24/255; {agree_nonwhite*100:.1f}% of hex pixels")
json.dump(dict(W=W,H=H,w_px=w_px,dy_row=dy_row,x0=x0,y0=y0,cells=cell_list,line=line,
               fidelity_all=agree,fidelity_hex=agree_nonwhite,axis_range=[-4.4,4.4]), open('hexcells.json','w'))
# side-by-side
sbs = Image.new('RGB',(W*2+10,H),(255,0,255)); sbs.paste(Image.open('/home/user/Multimodal-integration-for-coronary-artery-disease-risk-prediction/poster/assets/figures/fig3c_hexbin_plotarea.png').convert('RGB'),(0,0)); sbs.paste(canvas,(W+10,0)); sbs.save('hex_compare.png')
