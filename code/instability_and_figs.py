#!/usr/bin/env python3
"""Forecast-vintage instability (IMM Table 5) + two new figures:
 Fig A: cross-zonal causation vs burden scatter (all PJM zones)
 Fig B: forecast escalation of the data-centre adjustment across vintages
Outputs diagnostic cross-zonal and forecast-instability figures.
"""
import csv, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

SCR = os.path.dirname(os.path.abspath(__file__))  # data files live alongside this script
_out_dir = os.path.join(SCR, "..", "figures")
OUT = _out_dir if os.path.isdir(_out_dir) else SCR
os.makedirs(OUT, exist_ok=True)
C={"ink":"#243447","muted":"#667085","grid":"#D0D5DD","blue":"#3B5B92","teal":"#2A9D8F",
   "orange":"#F4A261","amber":"#E9A23B","red":"#E76F51","red_dark":"#B84936","green_dark":"#17766B","open":"#C24A3A","slate":"#5A6B7B"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none","pdf.fonttype":42,"savefig.dpi":300,"figure.dpi":140})

# ---- IMM Table 5: large-load adjustment (MW) by target year, across forecast vintages ----
# rows = vintage; cols = target year 2022..2027 (2022 vintage = 'Adjustments'; 2023-25 = 'Above Embedded')
years=[2022,2023,2024,2025,2026,2027]
vint={
 "2022 LF":[897,1643,2344,3061,3885,4166],
 "2023 LF":[None,2231,3393,4654,6594,8300],
 "2024 LF":[None,None,2664,4673,7557,10064],
 "2025 LF":[None,None,None,3591,8453,13668],
}
# escalation metric for target years 2026, 2027 (2023->2025 above-embedded vintages)
esc={}
for ty,idx in [(2026,4),(2027,5)]:
    v23=vint["2023 LF"][idx]; v25=vint["2025 LF"][idx]
    esc[ty]=(v23,v25,v25/v23)
with open(os.path.join(SCR,"forecast_instability.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["vintage"]+[f"target_{y}" for y in years])
    for k,v in vint.items(): w.writerow([k]+[("" if x is None else x) for x in v])
print("Escalation (2023 LF -> 2025 LF, above-embedded):")
for ty,(a,b,r) in esc.items(): print(f"  target {ty}: {a} -> {b} MW  ({r:.2f}x, +{100*(r-1):.0f}%)")

# ---- load cross-zonal data ----
rows=list(csv.reader(open(os.path.join(SCR,"crosszonal_caus_burden.csv"),encoding="utf-8")))
hdr=rows[0]; data=[]
for r in rows[1:]:
    d=dict(zip(hdr,r)); data.append(d)
def f(x):
    try: return float(x)
    except: return 0.0

# ============ FIGURE A: cross-zonal scatter ============
fig,ax=plt.subplots(figsize=(8.2,6.6))
xs=[f(d["burden_share2026_pct"]) for d in data]
ys=[f(d["caus_share2026_pct"]) for d in data]
names=[d["zone"] for d in data]
mx=max(max(xs),max(ys))*1.12
ax.plot([0,mx],[0,mx],ls="--",lw=1.3,color=C["slate"])
ax.text(mx*0.62,mx*0.66,"causation = burden\n(no cross-subsidy)",rotation=38,fontsize=8,color=C["slate"],ha="center")
ax.fill_between([0,mx],[0,mx],[mx,mx],color=C["red"],alpha=0.05)
ax.fill_between([0,mx],[0,0],[0,mx],color=C["teal"],alpha=0.05)
ax.text(mx*0.16,mx*0.92,"NET DRIVERS\n(cause > pay)",fontsize=8.5,color=C["red_dark"],fontweight="bold",ha="left",va="top")
ax.text(mx*0.62,mx*0.10,"NET PAYERS\n(pay > cause)",fontsize=8.5,color=C["green_dark"],fontweight="bold",ha="left")
for d,x,y in zip(data,xs,ys):
    a=f(d["adj2026"])
    sz=40+ a/6.0
    col=C["red_dark"] if y>x else C["teal"]
    ax.scatter(x,y,s=sz,color=col,alpha=0.75,edgecolor="white",linewidth=0.6,zorder=5)
    if d["zone"] in ("DOM","AEP","COMED","PS","PL","ATSI","APS","BGE","PECO"):
        dx,dy=(0.4,0.8)
        ax.annotate(d["zone"],(x,y),xytext=(x+dx,y+dy),fontsize=7.6,color=C["ink"])
ax.set_xlabel("Burden share — zone peak / RTO peak (%)  [how cost is socialized]")
ax.set_ylabel("Causation share — zone large-load adjustment / RTO (%)  [where the load is]")
ax.set_title("Two zones drive 80% of PJM's data-centre capacity adjustment;\ncost is socialized across all 22 (2026, official PJM data)",fontsize=10.5,fontweight="bold",color=C["ink"])
ax.set_xlim(0,mx); ax.set_ylim(0,mx)
ax.grid(color=C["grid"],alpha=0.6); ax.spines[["top","right"]].set_visible(False)
ax.text(0.98,0.02,"DOM 61.6% cause / 16.1% pay (3.8x); 20 of 22 zones pay more than they cause.\nBubble area ∝ zone adjustment MW. Source: PJM Table B-9b + 2026 Load Report.",
        transform=ax.transAxes,ha="right",va="bottom",fontsize=7,color=C["muted"])
fig.savefig(os.path.join(OUT,"Figure_A_crosszonal_causation_burden.png"),bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(OUT,"Figure_A_crosszonal_causation_burden.pdf"),bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(OUT,"Figure_A_crosszonal_causation_burden.svg"),bbox_inches="tight",facecolor="white")
plt.close(fig)

# ============ FIGURE B: forecast escalation ============
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12.4,5.4),gridspec_kw={"width_ratios":[1.25,1.0],"wspace":0.26})
cols={"2022 LF":C["grid"],"2023 LF":C["blue"],"2024 LF":C["amber"],"2025 LF":C["red"]}
for k,v in vint.items():
    xs2=[y for y,val in zip(years,v) if val is not None]
    ys2=[val for val in v if val is not None]
    ax1.plot(xs2,ys2,marker="o",lw=2.0,color=cols[k],label=k)
ax1.set_xlabel("Target (delivery) year"); ax1.set_ylabel("Large-load adjustment (MW)")
ax1.set_title("a  The forecast is a moving target",fontsize=10.5,fontweight="bold",color=C["ink"])
ax1.legend(frameon=False,title="forecast vintage",fontsize=8)
ax1.grid(color=C["grid"],alpha=0.6); ax1.spines[["top","right"]].set_visible(False)
ax1.annotate("2027: 8,300 → 13,668 MW\n(+65% over two cycles)",xy=(2027,13668),xytext=(2023.2,12200),
             fontsize=8,color=C["red_dark"],arrowprops=dict(arrowstyle="-|>",color=C["red_dark"],lw=1.2))
# panel b: per-cycle revision for delivery years used by the BRAs
ax2.bar(["2026\n(BRA 25/26)","2027\n(BRA 26/27)"],[esc[2026][2]*100-100,esc[2027][2]*100-100],
        color=[C["amber"],C["red"]],width=0.55)
for i,ty in enumerate([2026,2027]):
    ax2.text(i,esc[ty][2]*100-100+1.5,f"+{esc[ty][2]*100-100:.0f}%",ha="center",fontsize=9,fontweight="bold",color=C["ink"])
ax2.set_ylabel("Upward revision of the data-centre\nadjustment, 2023→2025 vintages (%)")
ax2.set_title("b  Revised by tens of % before the auction commits it",fontsize=10.0,fontweight="bold",color=C["ink"])
ax2.set_ylim(0,75); ax2.grid(axis="y",color=C["grid"],alpha=0.6); ax2.spines[["top","right"]].set_visible(False)
ax2.text(0.5,-0.22,"The 3-year-forward capacity commitment is locked against a non-stationary forecast.\nSource: IMM Table 5 (above-embedded vintages).",transform=ax2.transAxes,ha="center",va="top",fontsize=7.4,color=C["muted"])
fig.savefig(os.path.join(OUT,"Figure_B_forecast_instability.png"),bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(OUT,"Figure_B_forecast_instability.pdf"),bbox_inches="tight",facecolor="white")
fig.savefig(os.path.join(OUT,"Figure_B_forecast_instability.svg"),bbox_inches="tight",facecolor="white")
plt.close(fig)
print("\nWrote Figure A (cross-zonal) and Figure B (instability) to", OUT)
