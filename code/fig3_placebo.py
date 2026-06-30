#!/usr/bin/env python3
"""Figure 3 v2: concentration-socialization law + PLACEBO panel.
(a) data-centre causation g vs burden b -> gap (DOM/AEP off the 45 line)
(b) ordinary-load o vs burden b -> no gap (on the 45 line). Falsification."""
import csv, os
import matplotlib.pyplot as plt
import numpy as np
SCR = os.path.dirname(os.path.abspath(__file__))  # data files live alongside this script
_out_dir = os.path.join(SCR, "..", "figures")
OUT = _out_dir if os.path.isdir(_out_dir) else SCR
C={"ink":"#243447","muted":"#667085","grid":"#D0D5DD","teal":"#2A9D8F","red_dark":"#B84936","slate":"#5A6B7B","grey":"#9AA5B1"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none","pdf.fonttype":42,"savefig.dpi":300,"figure.dpi":140})
rows=list(csv.reader(open(os.path.join(SCR,"crosszonal_caus_burden.csv"),encoding="utf-8")))
hdr=rows[0]; D=[dict(zip(hdr,r)) for r in rows[1:]]
def f(x):
    try: return float(x)
    except: return 0.0
RTO_adj=11479.0; RTO_peak=156373.0; RTO_ord=RTO_peak-RTO_adj
zones=[]; g=[]; b=[]; o=[]; adj=[]
for d in D:
    a=f(d['adj2026']); pk=f(d['peak2026'])
    zones.append(d['zone']); adj.append(a)
    g.append(100*a/RTO_adj); b.append(100*pk/RTO_peak); o.append(100*(pk-a)/RTO_ord)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12.4,5.7),gridspec_kw={"wspace":0.22})
def setup(ax,title,letter):
    mx=68
    ax.plot([0,mx],[0,mx],ls="--",lw=1.2,color=C["slate"])
    ax.set_xlim(0,mx); ax.set_ylim(0,mx)
    ax.grid(color=C["grid"],alpha=0.5); ax.spines[["top","right"]].set_visible(False)
    ax.text(0,1.04,letter,transform=ax.transAxes,fontsize=12,fontweight="bold",color="#111827")
    ax.text(0.06,1.04,title,transform=ax.transAxes,fontsize=10,fontweight="bold",color=C["ink"])
    ax.set_xlabel("Burden share — zone peak / RTO (%)")

# panel a: data-centre
setup(ax1,"Data-centre load: causation ≠ burden","a")
ax1.set_ylabel("Causation share — DC adjustment / RTO (%)")
for z,x,y,a in zip(zones,b,g,adj):
    col=C["red_dark"] if y>x else C["teal"]
    ax1.scatter(x,y,s=40+a/6,color=col,alpha=0.78,edgecolor="white",linewidth=0.6,zorder=5)
    if z in ("DOM","AEP","COMED","PS","PL"):
        ax1.annotate(z,(x,y),xytext=(x+0.8,y+1.2),fontsize=7.4,color=C["ink"])
ax1.text(0.97,0.06,"HHI = 0.44 (concentrated)\nmean |gap| = 5.1 pp; DOM 3.8×",transform=ax1.transAxes,ha="right",fontsize=7.6,color=C["red_dark"],fontweight="bold")

# panel b: ordinary load (placebo)
setup(ax2,"Ordinary load: causation ≈ burden (placebo)","b")
ax2.set_ylabel("Ordinary-load share — (peak−adj) / RTO (%)")
for z,x,y in zip(zones,b,o):
    ax2.scatter(x,y,s=44,color=C["grey"],alpha=0.8,edgecolor="white",linewidth=0.6,zorder=5)
    if z in ("DOM","AEP","COMED","PS","PL"):
        ax2.annotate(z,(x,y),xytext=(x+0.8,y-1.6),fontsize=7.4,color=C["slate"])
ax2.text(0.97,0.06,"HHI = 0.09 (diversified)\nmean |gap| = 0.4 pp; ratio ≈ 1",transform=ax2.transAxes,ha="right",fontsize=7.6,color=C["slate"],fontweight="bold")

fig.suptitle("The concentration–socialization gap is specific to forecast data-centre load (2026, official PJM data)",fontsize=10.5,fontweight="bold",color="#111827",y=1.02)
for ext in ("png","pdf","svg"):
    fig.savefig(os.path.join(OUT,f"Figure_3_concentration_socialization_R160_v1legacy.{ext}"),bbox_inches="tight",facecolor="white")
print("Figure 3 (placebo v1 legacy) rebuilt — canonical figure is from fig_P2_placebo.py")
