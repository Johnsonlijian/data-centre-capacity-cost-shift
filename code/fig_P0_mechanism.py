# -*- coding: utf-8 -*-
"""Figure 1: forecast admissibility gate — mechanism diagram.
Re-written R163+ for clean NE submission: no text overflow, no clipping artefacts.
Output: Figure_1_forecast_admissibility_gate_R162.pdf/.png/.svg
"""
from __future__ import annotations
import os
from pathlib import Path
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})

# Palette
INK   = "#1a2332"
MUTED = "#667085"
SLATE = "#5a6b7b"
GATE  = "#2f5e8a"
BLUE  = "#3B5B92"
TEAL  = "#2a7f7f"
OPEN  = "#c24a3a"
AMBER = "#d98a3d"
PAPER = "#F8FAFC"
GATE_BG = "#EAF1F8"
TEAL_BG = "#EAF6F4"
AMBER_BG = "#FBF4EC"

FIG_W, FIG_H = 14.0, 5.8   # inches — wide-format, single-figure NE standard


def arrow(ax, x0, y0, x1, y1, color=MUTED, lw=1.6, head="->"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=head, lw=lw, color=color,
                                connectionstyle="arc3,rad=0.0"))


def rounded_box(ax, x, y, w, h, fc, ec, lw=1.6, ls="-", radius=0.012):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls,
        transform=ax.transAxes, clip_on=False,
    ))


fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

# ── Title + subtitle ──────────────────────────────────────────────────────────
ax.text(0.012, 0.975, "The forecast admissibility gate",
        ha="left", va="top", fontsize=14, fontweight="bold",
        color=INK, transform=ax.transAxes, clip_on=False)
ax.text(0.012, 0.920,
        "How a speculative request stock becomes a binding, socialized capacity cost — before the load is built or its retail incidence decided.",
        ha="left", va="top", fontsize=8.5, color=MUTED,
        transform=ax.transAxes, clip_on=False)

# ══════════════════════════════════════════════════════════════════════════════
#  Pipeline:  [Stack] →→ [GATE] →→ [Obligation] →→ [Wholesale wedge]
#  y-centre of main pipeline
yC = 0.60

# ── Stage 0: speculative stock (three shrinking boxes) ───────────────────────
STACK_ITEMS = [
    ("queue ~70 GW",  0.110),
    ("≈ 3× DOM peak", 0.082),
    ("~2–3 GW/mo",    0.056),
]
X_STACK = 0.082  # centre
ax.text(X_STACK, yC + 0.21, "Speculative\nrequest stock",
        ha="center", va="bottom", fontsize=8.0, fontweight="bold",
        color=SLATE, transform=ax.transAxes, clip_on=False,
        multialignment="center")
for i, (lab, hw) in enumerate(STACK_ITEMS):
    vy = yC + 0.10 - i * 0.062
    rounded_box(ax, X_STACK - hw/2, vy - 0.020, hw, 0.040,
                fc=PAPER, ec=SLATE, lw=0.9)
    ax.text(X_STACK, vy, lab,
            ha="center", va="center", fontsize=7.0, color=INK,
            transform=ax.transAxes, clip_on=False)

# arrow stack → gate
arrow(ax, 0.152, yC, 0.196, yC, color=MUTED, lw=1.4)

# ── Stage 1: THE GATE (trapezoid) ─────────────────────────────────────────────
GX0, GX1 = 0.200, 0.420
GY_HI, GY_LO = 0.175, 0.090   # half-heights on left and right side

gate_poly = Polygon(
    [(GX0, yC + GY_HI), (GX1, yC + GY_LO),
     (GX1, yC - GY_LO), (GX0, yC - GY_HI)],
    closed=True,
    facecolor=GATE_BG, edgecolor=GATE, linewidth=2.2,
    transform=ax.transAxes, clip_on=False,
)
ax.add_patch(gate_poly)

# Gate title above polygon
ax.text((GX0 + GX1) / 2, yC + GY_HI + 0.055,
        "FORECAST ADMISSIBILITY GATE",
        ha="center", va="bottom", fontsize=9.5, fontweight="bold",
        color=GATE, transform=ax.transAxes, clip_on=False)

# Four gate criteria — centred inside the trapezoid
CRITERIA = [
    ("Firmness test",     "ESO/CC-firm load only"),
    ("Utilization derate","70% default, ramp ≥ 36 mo"),
    ("Duplication filter","unsupported dups removed"),
    ("Ramp schedule",     "≥ 36-month in-service"),
]
n = len(CRITERIA)
cx = (GX0 + GX1) / 2 - 0.01   # slightly left of centre (trapezoid is wider left)
for j, (k, sub) in enumerate(CRITERIA):
    yk = yC + 0.090 - j * 0.058
    ax.text(cx, yk,
            f"  {k}",
            ha="center", va="bottom", fontsize=7.2, fontweight="bold",
            color=GATE, transform=ax.transAxes, clip_on=False)
    ax.text(cx, yk - 0.026,
            sub,
            ha="center", va="top", fontsize=6.4, color=SLATE,
            transform=ax.transAxes, clip_on=False)

# note below gate
ax.text((GX0 + GX1) / 2, yC - GY_HI - 0.038,
        "DOM queue ~70 GW  →  16.6 GW admitted",
        ha="center", va="top", fontsize=6.8, style="italic",
        color=OPEN, transform=ax.transAxes, clip_on=False)

# arrow gate → obligation
arrow(ax, GX1 + 0.004, yC, GX1 + 0.046, yC, color=GATE, lw=1.8)

# ── Stage 2: Binding obligation ───────────────────────────────────────────────
OBL_X, OBL_W, OBL_H = 0.468, 0.135, 0.155
OBL_Y = yC - OBL_H / 2
rounded_box(ax, OBL_X, OBL_Y, OBL_W, OBL_H, fc="white", ec=BLUE, lw=1.8)
ax.text(OBL_X + OBL_W / 2, yC + 0.018,
        "Binding capacity\nobligation",
        ha="center", va="center", fontsize=7.8, fontweight="bold",
        color=BLUE, transform=ax.transAxes, clip_on=False,
        multialignment="center")
ax.text(OBL_X + OBL_W / 2, yC - 0.040,
        "priced 3 years\nforward (BRA)",
        ha="center", va="center", fontsize=6.8, color=INK,
        transform=ax.transAxes, clip_on=False,
        multialignment="center")

# arrow obligation → wholesale
arrow(ax, OBL_X + OBL_W + 0.004, yC, OBL_X + OBL_W + 0.046, yC, color=BLUE, lw=1.8)

# ── Stage 3: Wholesale magnitude ─────────────────────────────────────────────
WH_X, WH_W, WH_H = 0.658, 0.148, 0.200
WH_Y = yC - WH_H / 2
rounded_box(ax, WH_X, WH_Y, WH_W, WH_H, fc=TEAL_BG, ec=TEAL, lw=2.0)
ax.text(WH_X + WH_W / 2, yC + 0.052,
        "Wholesale wedge",
        ha="center", va="center", fontsize=7.8, fontweight="bold",
        color=TEAL, transform=ax.transAxes, clip_on=False)
ax.text(WH_X + WH_W / 2, yC + 0.004,
        "USD 21.26 B",
        ha="center", va="center", fontsize=12.0, fontweight="bold",
        color=TEAL, transform=ax.transAxes, clip_on=False)
ax.text(WH_X + WH_W / 2, yC - 0.040,
        "= 45.0% of PJM\ncapacity revenue",
        ha="center", va="center", fontsize=7.0, color=INK,
        transform=ax.transAxes, clip_on=False, multialignment="center")

# arrow wholesale down → socialization boxes
ax.annotate("", xy=(WH_X + WH_W / 2, 0.298),
            xytext=(WH_X + WH_W / 2, WH_Y),
            arrowprops=dict(arrowstyle="-|>", lw=1.4, color=TEAL),
            xycoords="axes fraction", textcoords="axes fraction")

# ── THREE AXES annotation block (right of wholesale) ─────────────────────────
ANN_X = WH_X + WH_W + 0.018
ax.text(ANN_X, yC + 0.100,
        "Three measurement axes:",
        ha="left", va="center", fontsize=7.4, fontweight="bold",
        color=INK, transform=ax.transAxes, clip_on=False)
AXES_ITEMS = [
    ("Causation and burden",   "Concentrated cause, socialized burden"),
    ("Materialization risk",   "Non-stationary forecast, no clawback"),
    ("Price amplification",    "~84% inframarginal transfer"),
]
for i, (sec, desc) in enumerate(AXES_ITEMS):
    yi = yC + 0.045 - i * 0.060
    ax.text(ANN_X, yi,
            sec, ha="left", va="center", fontsize=7.2, fontweight="bold",
            color=GATE, transform=ax.transAxes, clip_on=False)
    ax.text(ANN_X, yi - 0.025,
            desc, ha="left", va="center", fontsize=6.5, color=SLATE,
            transform=ax.transAxes, clip_on=False)

# ══════════════════════════════════════════════════════════════════════════════
#  BOTTOM ROW: accountability boundary + two boxes
# ── Accountability divider ────────────────────────────────────────────────────
DIV_X = 0.390
BROW_Y = 0.085    # bottom of bottom row
BROW_H = 0.175    # height of bottom row

ax.plot([DIV_X, DIV_X], [BROW_Y - 0.012, BROW_Y + BROW_H + 0.012],
        ls=":", lw=1.5, color=OPEN, transform=ax.transAxes, clip_on=False)
ax.text(DIV_X, BROW_Y - 0.038,
        "accountability boundary",
        ha="center", va="top", fontsize=6.8, style="italic",
        color=OPEN, transform=ax.transAxes, clip_on=False)

# ── Left: OPEN retail allocation ─────────────────────────────────────────────
OPN_X = 0.010; OPN_W = DIV_X - 0.025; OPN_H = BROW_H
rounded_box(ax, OPN_X, BROW_Y, OPN_W, OPN_H,
            fc="white", ec=OPEN, lw=1.6, ls="--")
ax.text(OPN_X + OPN_W / 2, BROW_Y + OPN_H - 0.022,
        "OPEN: retail allocation",
        ha="center", va="top", fontsize=8.0, fontweight="bold",
        color=OPEN, transform=ax.transAxes, clip_on=False)
OPEN_LINES = [
    "zone → LSE settlement: confidential",
    "cross-class allocation: pending",
    "household incidence: NOT point-identifiable",
]
for i, line in enumerate(OPEN_LINES):
    ax.text(OPN_X + 0.012, BROW_Y + OPN_H - 0.058 - i * 0.038,
            line, ha="left", va="top", fontsize=7.0, color=INK,
            transform=ax.transAxes, clip_on=False)

# arrow OPEN ← socialized (pointing right-to-left = records don't flow here)
arrow(ax, DIV_X - 0.010, BROW_Y + OPN_H / 2 + 0.008,
         DIV_X + 0.018, BROW_Y + OPN_H / 2 + 0.008,
      color=OPEN, lw=1.3, head="<-")

# ── Right: socialized by consumption ─────────────────────────────────────────
SOC_X = DIV_X + 0.028; SOC_W = 0.620; SOC_H = BROW_H
rounded_box(ax, SOC_X, BROW_Y, SOC_W, SOC_H, fc=AMBER_BG, ec=AMBER, lw=1.6)
ax.text(SOC_X + SOC_W / 2, BROW_Y + SOC_H - 0.022,
        "Socialized by consumption (pro-rata)",
        ha="center", va="top", fontsize=8.0, fontweight="bold",
        color=AMBER, transform=ax.transAxes, clip_on=False)
SOC_LINES = [
    "DOM causes 61.6%  /  bears 16.1%  →  3.8× causation–burden gap",
    "84% of effect is inframarginal transfer to incumbents (not cost of service)",
    "Household-dollar incidence not derivable from wholesale record alone",
]
for i, line in enumerate(SOC_LINES):
    ax.text(SOC_X + 0.012, BROW_Y + SOC_H - 0.058 - i * 0.038,
            line, ha="left", va="top", fontsize=7.0, color=INK,
            transform=ax.transAxes, clip_on=False)

# ══════════════════════════════════════════════════════════════════════════════
fig.tight_layout(pad=0.2)
NAME = "Figure_1_forecast_admissibility_gate_R162" if "review_packages" in str(HERE) else "Figure_1"
for ext in ["pdf", "png", "svg"]:
    fig.savefig(FIGURES / f"{NAME}.{ext}", bbox_inches="tight",
                facecolor="white", dpi=300 if ext == "png" else None)
    print(f"wrote {NAME}.{ext}")
plt.close(fig)
