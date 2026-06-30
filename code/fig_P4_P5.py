# -*- coding: utf-8 -*-
"""Figures: P4 multi-market generality; P5 Bayesian ratchet posterior."""
import os, json
import csv
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
# Write figures to ../figures/ when run from the code/ folder; else write alongside this script
_fig_dir = os.path.join(HERE, "..", "figures")
OUT  = _fig_dir if os.path.isdir(_fig_dir) else HERE

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
})
TEAL  = "#2a7f7f"
AMBER = "#d98a3d"
GREY  = "#9aa0a6"
INK   = "#222222"
RED   = "#b3402e"
BLUE  = "#34618f"
WHITE = "#ffffff"

# ── P4 six-market generality ─────────────────────────────────────────────────
rows = list(csv.DictReader(open(os.path.join(HERE, "P4_markets.csv"), encoding="utf-8")))
def f(x):
    try: return float(x)
    except: return np.nan

# Display order: bottom-to-top (ERCOT/MISO are controls; Ireland is extreme)
ORDER = [
    "ERCOT",
    "MISO",
    "Italy (Terna, DY2027)",
    "ISO-NE",
    "GB (T-4 2029/30)",
    "PJM (this paper)",
    "Ireland/SEM (2029/30)",
]
rows = sorted(rows, key=lambda r: ORDER.index(r["m"]) if r["m"] in ORDER else 99)

# Gate description for each market
GATE = {
    "PJM (this paper)":       "firm forecast gate\n(CIFP, 70% derate, 3-yr fwd)",
    "MISO":                   "41% attrition screen\n(LTLF attrition model)",
    "ISO-NE":                 "gate forming\n(inaugural LLF, 2026)",
    "GB (T-4 2029/30)":       "prequalification\n(T-4 Capacity Market rules)",
    "Ireland/SEM (2029/30)":  "connection mandate\n(mandatory agreement)",
    "Italy (Terna, DY2027)":  "feasibility screen\n(Terna prequalification)",
    "ERCOT":                  "no capacity obligation\n(energy-only; locational energy costs)",
}

fig, ax = plt.subplots(figsize=(9.4, 5.4))
fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.10)

N = len(rows)
BAR_H = 0.74

for i, r in enumerate(rows):
    soc        = r["recovery"] == "socialized"
    energy_only = r["recovery"].lower() == "energy-only"
    bg  = AMBER if soc else ("#c8e0e0" if not energy_only else "#dce4e8")
    ax.barh(i, 1, color=bg, alpha=0.55, height=BAR_H, left=0)

    # Market name — left
    mname = r["m"].replace(" (this paper)", "").replace("(Terna, DY2027)", "(Terna)")
    ax.text(0.01, i, mname,
            va="center", ha="left",
            fontsize=9.6, fontweight="bold", color=INK)

    # Gate description — left-centre column
    gate_txt = GATE.get(r["m"], "")
    ax.text(0.32, i, gate_txt,
            va="center", ha="left",
            fontsize=7.4, color=GREY, style="italic",
            multialignment="left", linespacing=1.3)

    # DC share label — centre
    dc = f(r["dc_share_pct"])
    if not np.isnan(dc):
        yr_note = {"MISO": "(proj. 2030)",
                   "Italy (Terna, DY2027)": "(proj. 2030)"}.get(r["m"], "")
        yr_note2 = {"Ireland/SEM (2029/30)": "(2024, CSO)"}.get(r["m"], yr_note)
        demand_label = {"Ireland/SEM (2029/30)": "of national metered electricity"}.get(r["m"], "of demand")
        ax.text(0.61, i + 0.20,
                f"data centres {dc:.0f}% {demand_label} {yr_note2}",
                va="center", ha="left",
                fontsize=7.5, color=RED)

    # Recovery + mechanism tag — right
    if soc:
        tag      = "SOCIALIZED"
        sub      = "mechanism ON"
        tag_col  = "#7a4a13"
        sub_col  = AMBER
    elif energy_only:
        tag      = "ENERGY-ONLY"
        sub      = "no capacity market (negative control)"
        tag_col  = BLUE
        sub_col  = BLUE
    else:
        tag      = "LOCATIONAL"
        sub      = "mechanism OFF (boundary condition)"
        tag_col  = TEAL
        sub_col  = TEAL

    ax.text(0.98, i + 0.14, tag,
            va="center", ha="right",
            fontsize=8.8, fontweight="bold", color=tag_col)
    ax.text(0.98, i - 0.18, sub,
            va="center", ha="right",
            fontsize=7.2, color=sub_col, style="italic")

# Axes cosmetics
ax.set_yticks([])
ax.set_xticks([])
ax.set_xlim(0, 1)
ax.set_ylim(-0.55, N + 0.15)   # extra headroom above top row for column headers

# Column header labels — in axes fraction; sit above all bars with clear separation
ax.text(0.01, 0.975, "Market",             fontsize=8.0, color=GREY, fontweight="bold",
        transform=ax.transAxes, va="top")
ax.text(0.32, 0.975, "Admissibility gate", fontsize=8.0, color=GREY, fontweight="bold",
        transform=ax.transAxes, va="top")
ax.text(0.98, 0.975, "Cost recovery",      fontsize=8.0, color=GREY, fontweight="bold",
        ha="right", transform=ax.transAxes, va="top")

# Divider line below headers, above Ireland bar — in data coords
ax.axhline(N - 0.40, color=GREY, lw=0.5, ls="-", alpha=0.5)

ax.set_title(
    "The concentration-socialization mechanism recurs across six capacity markets; ERCOT (energy-only) is the negative control",
    loc="left", fontsize=10.0, fontweight="bold")

# Footer note — y in axes fraction; keep small so bbox_inches="tight" doesn't add blank space
ax.text(0.5, -0.04,
        "All six capacity markets use sloped administrative demand curves. Recovery basis drives mechanism presence; "
        "MISO localizes (boundary condition); ERCOT energy-only is the negative control. Price levels not equated (Methods).",
        ha="center", va="top", fontsize=7.5, style="italic",
        transform=ax.get_xaxis_transform())

fig.savefig(os.path.join(OUT, "Figure_5.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Figure_5.png"), bbox_inches="tight", dpi=180)
fig.savefig(os.path.join(OUT, "Figure_5.svg"), bbox_inches="tight")
plt.close(fig)
print("wrote Figure_5")

# ── P5 Bayesian ratchet ────────────────────────────────────────────────────────
d = np.load(os.path.join(HERE, "P5_drift_pct.npy"))
j = json.load(open(os.path.join(HERE, "P5_bayes_ratchet.json")))
med = j["drift_pct_per_vintage_median"]
lo, hi = j["drift_pct_per_vintage_CI95"]
P = j["P_drift_gt_0"]

fig, ax = plt.subplots(figsize=(6.6, 3.9))
ax.hist(d, bins=80, color=BLUE, alpha=0.55, density=True, ec="white", lw=0.2)
ax.axvspan(lo, hi, color=BLUE, alpha=0.12, label=f"95% CrI [{lo:.0f}, {hi:.0f}]%")
ax.axvline(med, color=INK, lw=1.6, label=f"median {med:.0f}%/vintage")
ax.axvline(0, color=RED, lw=1.2, ls="--",
           label=f"no drift (P[drift>0]={P:.3f})")
ax.set_xlabel("fitted upward drift of the data-centre forecast (% per vintage)")
ax.set_ylabel("posterior density")
ax.set_title("Bayesian ratchet: the forecast drifts up +23%/vintage (P=0.998)",
             loc="left", fontsize=10)
ax.legend(frameon=False, fontsize=8)
fig.savefig(os.path.join(OUT, "Supplementary_Figure_S2.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Supplementary_Figure_S2.png"), bbox_inches="tight", dpi=180)
fig.savefig(os.path.join(OUT, "Supplementary_Figure_S2.svg"), bbox_inches="tight")
plt.close(fig)
print("wrote Supplementary_Figure_S2")
