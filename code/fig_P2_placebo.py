# -*- coding: utf-8 -*-
"""Figure 2: concentration–socialization + placebo.
Two panels: (a) DC causation vs burden — DOM/AEP outliers; (b) ordinary-load placebo — tight 45° line.
Updated: Times New Roman font, consistent color palette, Nature Energy style.
"""
import csv, os
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SCR  = HERE  # data files live alongside this script in the code/ folder
_fig_dir = os.path.join(HERE, "..", "figures")
FIG  = _fig_dir if os.path.isdir(_fig_dir) else HERE

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif":  ["Times New Roman", "DejaVu Serif"],
    "font.size":   10,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})
TEAL  = "#2a7f7f"
AMBER = "#d98a3d"
GREY  = "#9aa0a6"
RED   = "#b3402e"
INK   = "#222222"
SLATE = "#5a6b7b"
GRID  = "#e0e0e0"

# ── Load data ──────────────────────────────────────────────────────────────────
rows = list(csv.reader(open(os.path.join(SCR, "crosszonal_caus_burden.csv"), encoding="utf-8")))
hdr  = rows[0]
data = [dict(zip(hdr, r)) for r in rows[1:]]

def fv(x):
    try: return float(x)
    except: return 0.0

RTO_adj  = 11479.0
RTO_peak = 156373.0
RTO_ord  = RTO_peak - RTO_adj

zones, g, b, o, adj = [], [], [], [], []
for d in data:
    a  = fv(d["adj2026"])
    pk = fv(d["peak2026"])
    zones.append(d["zone"])
    adj.append(a)
    g.append(100 * a / RTO_adj)
    b.append(100 * pk / RTO_peak)
    o.append(100 * (pk - a) / RTO_ord)

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 5.2),
                                gridspec_kw={"wspace": 0.24})
fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.12)

LABEL_ZONES = {"DOM", "AEP", "COMED", "PS", "PL"}

def setup(ax, title, letter):
    mx = 68
    ax.plot([0, mx], [0, mx], ls="--", lw=1.2, color=SLATE, zorder=2)
    ax.set_xlim(0, mx)
    ax.set_ylim(0, mx)
    ax.grid(color=GRID, alpha=0.7, lw=0.5, zorder=1)
    ax.set_xlabel("Burden share — zone peak / RTO coincident peak (%)", fontsize=9)
    # Panel label
    ax.text(0.02, 1.04, f"({letter})", transform=ax.transAxes,
            fontsize=11, fontweight="bold", color=INK, va="bottom")
    ax.set_title(f"  {title}", loc="left", fontsize=10, fontweight="bold", pad=2)
    return mx

# ── Panel (a): data-centre ─────────────────────────────────────────────────────
mx = setup(ax1, "Data-centre load: causation ≠ burden", "a")
ax1.set_ylabel("Causation share — DC adjustment / RTO (%)", fontsize=9)

# Shading: above diagonal = net driver (cause > pay)
ax1.fill_between([0, mx], [0, mx], [mx, mx], color=RED,  alpha=0.04, zorder=1)
ax1.fill_between([0, mx], [0, 0],  [0, mx],  color=TEAL, alpha=0.04, zorder=1)
ax1.text(2, mx * 0.93, "cause > pay",  fontsize=8, color=RED,  fontweight="bold")
ax1.text(mx * 0.62, 3, "pay > cause",  fontsize=8, color=TEAL, fontweight="bold")

OFF_A = {
    "DOM":   ( 0.4,  1.2),   # above-right (large bubble, label clears edge)
    "AEP":   ( 0.6,  1.2),   # above-right
    "COMED": ( 0.8, -2.2),   # below-right
    "PS":    (-0.5,  2.2),   # above-left (separate from PL)
    "PL":    ( 0.7,  2.2),   # above-right (separate from PS)
}
for z, x, y, a in zip(zones, b, g, adj):
    above = y > x
    col   = RED if above else TEAL
    sz    = 38 + a / 5.5
    ax1.scatter(x, y, s=sz, color=col, alpha=0.78,
                edgecolor="white", linewidth=0.5, zorder=5)
    if z in LABEL_ZONES:
        ox, oy = OFF_A.get(z, (0.6, 1.2 if above else -2.2))
        ax1.annotate(z, (x, y), xytext=(x + ox, y + oy),
                     fontsize=8.0, color=INK,
                     arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5))

ax1.text(0.97, 0.05,
         "HHI(causation) = 0.44   HHI(ordinary) = 0.09\n"
         "DOM: 61.6% cause / 16.1% pay = 3.8× gap\n"
         "Paired Wilcoxon p < 0.001; bootstrap 95% CI: ratio [1.9, 5.0]",
         transform=ax1.transAxes, ha="right", va="bottom",
         fontsize=7.8, color=RED, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

# ── Panel (b): placebo ─────────────────────────────────────────────────────────
setup(ax2, "Ordinary load: causation ≈ burden (placebo)", "b")
ax2.set_ylabel("Ordinary-load share — (peak−adj) / (RTO−RTO adj) (%)", fontsize=9)

OFF_B = {
    "DOM":   ( 1.0, -2.6),   # below-right (separate from AEP)
    "AEP":   (-2.5,  1.8),   # above-left
    "COMED": ( 0.5, -2.2),   # below-right
    "PS":    ( 0.6,  1.6),   # above
    "PL":    (-2.0, -1.8),   # left-below
}
for z, x, y in zip(zones, b, o):
    ax2.scatter(x, y, s=42, color=GREY, alpha=0.80,
                edgecolor="white", linewidth=0.5, zorder=5)
    if z in LABEL_ZONES:
        ox, oy = OFF_B.get(z, (0.5, -1.8))
        ax2.annotate(z, (x, y), xytext=(x + ox, y + oy),
                     fontsize=8.0, color=SLATE,
                     arrowprops=dict(arrowstyle="-", color=GREY, lw=0.4))

ax2.text(0.97, 0.05,
         "HHI(ordinary) = 0.09  (diversified)\n"
         "mean |gap| = 0.40 pp vs 5.1 pp (DC)\n"
         "Gap is data-centre-specific, not an\nartefact of pro-rata recovery",
         transform=ax2.transAxes, ha="right", va="bottom",
         fontsize=7.8, color=SLATE,
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

# ── Super-title ────────────────────────────────────────────────────────────────
fig.suptitle(
    "The concentration–socialization gap is specific to forecast data-centre load (2026, official PJM data)",
    fontsize=10.8, fontweight="bold", color=INK, y=0.97)

out = os.path.join(FIG, "Figure_2.pdf")
fig.savefig(out, bbox_inches="tight", facecolor="white")
fig.savefig(out.replace(".pdf", ".png"), bbox_inches="tight", facecolor="white", dpi=180)
fig.savefig(out.replace(".pdf", ".svg"), bbox_inches="tight", facecolor="white")
print("wrote", out)
