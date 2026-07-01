# -*- coding: utf-8 -*-
"""Figure 5: cross-market preconditions; Supplementary Figure S2 sensitivity."""
import os
import csv
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figures") if os.path.isdir(os.path.join(HERE, "..", "figures")) else HERE

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

TEAL = "#2a7f7f"
AMBER = "#d98a3d"
GREY = "#7d858c"
INK = "#222222"
RED = "#b3402e"
BLUE = "#34618f"
VIOLET = "#6b5b95"

rows = list(csv.DictReader(open(os.path.join(HERE, "P4_markets.csv"), encoding="utf-8")))

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

GATE = {
    "PJM (this paper)": "firm forecast gate\n(CIFP, 70% derate)",
    "MISO": "41% attrition screen\n(LTLF model)",
    "ISO-NE": "gate forming\n(large-load forecast)",
    "GB (T-4 2029/30)": "prequalification\n(T-4 rules)",
    "Ireland/SEM (2029/30)": "connection mandate\n(capacity agreement)",
    "Italy (Terna, DY2027)": "feasibility screen\n(prequalification)",
    "ERCOT": "no capacity obligation\n(energy-only)",
}

def f(x):
    try:
        return float(x)
    except Exception:
        return np.nan

fig, ax = plt.subplots(figsize=(9.4, 5.65))
fig.subplots_adjust(left=0.02, right=0.98, top=0.89, bottom=0.12)

N = len(rows)
for i, r in enumerate(rows):
    recovery = r["recovery"].strip().lower()
    socialized = recovery == "socialized"
    seasonal = recovery == "seasonal"
    energy_only = recovery == "energy-only"
    if socialized:
        bg = AMBER
    elif seasonal:
        bg = VIOLET
    elif energy_only:
        bg = "#dce4e8"
    else:
        bg = "#c8e0e0"
    ax.barh(i, 1, color=bg, alpha=0.50, height=0.74, left=0)

    mname = r["m"].replace(" (this paper)", "").replace("(Terna, DY2027)", "(Terna)")
    ax.text(0.01, i, mname, va="center", ha="left",
            fontsize=9.6, fontweight="bold", color=INK)

    ax.text(0.31, i, GATE.get(r["m"], ""), va="center", ha="left",
            fontsize=8.2, color=GREY, multialignment="left", linespacing=1.25)

    dc = f(r["dc_share_pct"])
    if not np.isnan(dc):
        demand_label = "metered electricity" if "Ireland" in r["m"] else "demand"
        note = "2024, CSO" if "Ireland" in r["m"] else "2030 projection"
        ax.text(0.59, i + 0.18, f"DCs: {dc:.0f}% of {demand_label} ({note})",
                va="center", ha="left", fontsize=7.2, color=RED)

    if socialized:
        tag = "SOCIALIZED"
        sub = "preconditions present"
        tag_col = "#7a4a13"
        sub_col = AMBER
    elif seasonal:
        tag = "SEASONAL"
        sub = "summer socialized; fall local"
        tag_col = VIOLET
        sub_col = VIOLET
    elif energy_only:
        tag = "ENERGY-ONLY"
        sub = "design comparator"
        tag_col = BLUE
        sub_col = BLUE
    else:
        tag = "LOCATIONAL"
        sub = "boundary condition"
        tag_col = TEAL
        sub_col = TEAL

    ax.text(0.98, i + 0.14, tag, va="center", ha="right",
            fontsize=8.9, fontweight="bold", color=tag_col)
    ax.text(0.98, i - 0.18, sub, va="center", ha="right",
            fontsize=7.9, color=sub_col)

ax.set_yticks([])
ax.set_xticks([])
ax.set_xlim(0, 1)
ax.set_ylim(-0.55, N + 0.15)
ax.text(0.01, 0.975, "Market", fontsize=8.2, color=GREY, fontweight="bold",
        transform=ax.transAxes, va="top")
ax.text(0.31, 0.975, "Admissibility gate", fontsize=8.2, color=GREY, fontweight="bold",
        transform=ax.transAxes, va="top")
ax.text(0.98, 0.975, "Recovery basis", fontsize=8.2, color=GREY, fontweight="bold",
        ha="right", transform=ax.transAxes, va="top")
ax.axhline(N - 0.40, color=GREY, lw=0.5, alpha=0.5)
ax.set_title(
    "Preconditions and boundary conditions across capacity markets; ERCOT is the design comparator",
    loc="left", fontsize=10.0, fontweight="bold")
ax.text(0.5, -0.055,
        "PJM is quantified. MISO is the seasonal boundary test: uniform summer clearing supports the mechanism, "
        "while constrained fall clearing localizes it. Other markets are precondition checks.",
        ha="center", va="top", fontsize=7.7, color=GREY,
        transform=ax.get_xaxis_transform())

fig5_name = "Figure_5"
fig.savefig(os.path.join(OUT, f"{fig5_name}.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, f"{fig5_name}.png"), bbox_inches="tight", dpi=180)
fig.savefig(os.path.join(OUT, f"{fig5_name}.svg"), bbox_inches="tight")
plt.close(fig)
print("wrote", fig5_name)

# Supplementary Figure S2: comparable forecast-revision sensitivity.
revisions = np.array([-21.5, 0.4, -23.2, 14.6, 11.9, 21.3, 35.8])
labels = ["2024\n23->24", "2025\n23->24", "2025\n24->25",
          "2026\n23->24", "2026\n24->25", "2027\n23->24", "2027\n24->25"]
colors = [TEAL if v >= 0 else GREY for v in revisions]

fig, ax = plt.subplots(figsize=(7.2, 3.9))
fig.subplots_adjust(left=0.10, right=0.97, top=0.82, bottom=0.24)
ax.bar(range(len(revisions)), revisions, color=colors, edgecolor=INK, lw=0.45, alpha=0.85)
ax.axhline(0, color=INK, lw=0.8)
ax.axhline(np.mean(revisions), color=AMBER, lw=1.2, ls="--",
           label=f"mean {np.mean(revisions):+.1f}%")
ax.axhline(np.median(revisions), color=BLUE, lw=1.2, ls=":",
           label=f"median {np.median(revisions):+.1f}%")
for i, v in enumerate(revisions):
    va = "bottom" if v >= 0 else "top"
    y = v + (1.2 if v >= 0 else -1.2)
    ax.text(i, y, f"{v:+.1f}%", ha="center", va=va, fontsize=7.8, color=INK)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("Revision (%)")
ax.set_title("Comparable forecast revisions show material non-stationarity, not a significant ratchet",
             loc="left", fontsize=10, fontweight="bold")
ax.text(0.5, -0.30,
        "Comparable 2023-2025 above-embedded vintages only; 2022 total-adjustment vintage excluded from inference. "
        "Five of seven revisions are upward (one-sided sign test p=0.23).",
        transform=ax.transAxes, ha="center", va="top", fontsize=7.7, color=GREY)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.grid(axis="y", color="#e0e0e0", alpha=0.6, lw=0.5)

s2_name = "Supplementary_Figure_S2"
fig.savefig(os.path.join(OUT, f"{s2_name}.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, f"{s2_name}.png"), bbox_inches="tight", dpi=180)
fig.savefig(os.path.join(OUT, f"{s2_name}.svg"), bbox_inches="tight")
plt.close(fig)
print("wrote", s2_name)
