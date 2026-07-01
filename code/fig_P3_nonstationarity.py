# -*- coding: utf-8 -*-
"""Figure 3: forecast non-stationarity under comparable vintages."""
import os
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures") if os.path.isdir(os.path.join(HERE, "..", "figures")) else HERE

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
RED = "#b3402e"
BLUE = "#34618f"
INK = "#222222"
GRID = "#e0e0e0"

YEARS = [2022, 2023, 2024, 2025, 2026, 2027]
VINT = {
    "2022 LF (total)": [897, 1643, 2344, 3061, 3885, 4166],
    "2023 LF": [None, 2231, 3393, 4654, 6594, 8300],
    "2024 LF": [None, None, 2664, 4673, 7557, 10064],
    "2025 LF": [None, None, None, 3591, 8453, 13668],
}
COLORS = {
    "2022 LF (total)": GREY,
    "2023 LF": BLUE,
    "2024 LF": AMBER,
    "2025 LF": RED,
}

comparable_revs = [
    (2024, "2023->2024", -21.5),
    (2025, "2023->2024", 0.4),
    (2025, "2024->2025", -23.2),
    (2026, "2023->2024", 14.6),
    (2026, "2024->2025", 11.9),
    (2027, "2023->2024", 21.3),
    (2027, "2024->2025", 35.8),
]
two_cycle = {
    2026: (6594, 8453),
    2027: (8300, 13668),
}

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(10.6, 4.45),
    gridspec_kw={"width_ratios": [1.34, 1.0], "wspace": 0.30}
)
fig.subplots_adjust(left=0.07, right=0.97, top=0.82, bottom=0.16)

for k, vals in VINT.items():
    xs = [y for y, v in zip(YEARS, vals) if v is not None]
    ys = [v for v in vals if v is not None]
    ls = "--" if k.startswith("2022") else "-"
    alpha = 0.55 if k.startswith("2022") else 0.98
    ax1.plot(xs, ys, marker="o", lw=1.8, ms=5.2, ls=ls,
             color=COLORS[k], label=k, alpha=alpha)

ax1.annotate("Comparable above-embedded\nvintages start in 2023",
             xy=(2023, 2231), xytext=(2021.9, 7600),
             fontsize=8.0, color=BLUE,
             arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.9))
ax1.annotate("2027: 8,300 -> 13,668 MW\n(+65% over two vintages)",
             xy=(2027, 13668), xytext=(2024.35, 13100),
             fontsize=8.0, color=RED,
             arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0))
ax1.axvspan(2025.5, 2027.5, color=AMBER, alpha=0.08, zorder=0)
ax1.text(2026.55, 500, "auction-relevant\nhorizon", ha="center",
         fontsize=7.5, color=AMBER, style="italic")

ax1.set_xlabel("Target delivery year", fontsize=9)
ax1.set_ylabel("Large-load adjustment (MW)", fontsize=9)
ax1.set_title("(a) Forecast quantity moves across vintages", loc="left", fontsize=10)
ax1.set_xlim(2021.5, 2027.8)
ax1.set_ylim(0, 15500)
ax1.set_xticks(YEARS)
ax1.grid(color=GRID, alpha=0.6, lw=0.5)
ax1.legend(frameon=False, title="Forecast vintage", title_fontsize=8, fontsize=8.0,
           loc="upper left")

labels = ["2026\n2023->2025", "2027\n2023->2025"]
revisions = [100 * (two_cycle[2026][1] / two_cycle[2026][0] - 1),
             100 * (two_cycle[2027][1] / two_cycle[2027][0] - 1)]
bars = ax2.bar([0, 1], revisions, color=[AMBER, RED], width=0.52,
               edgecolor=INK, lw=0.5, alpha=0.86)
for i, (rev, (v0, v1)) in enumerate(zip(revisions, [two_cycle[2026], two_cycle[2027]])):
    ax2.text(i, rev + 1.8, f"+{rev:.0f}%", ha="center", va="bottom",
             fontsize=11, fontweight="bold", color=INK)
    ax2.text(i, rev / 2, f"{v0:,} -> {v1:,} MW",
             ha="center", va="center", fontsize=7.1, color="white")

all_revs = np.array([r[2] for r in comparable_revs])
ax2.axhline(0, color=INK, lw=0.7)
ax2.set_xticks([0, 1])
ax2.set_xticklabels(labels, fontsize=9)
ax2.set_ylabel("Two-vintage revision (%)", fontsize=9)
ax2.set_ylim(-6, 72)
ax2.set_title("(b) Material revisions before commitment", loc="left", fontsize=10)
ax2.grid(axis="y", color=GRID, alpha=0.6, lw=0.5)
ax2.text(0.5, -0.18,
         "Comparable consecutive revisions, 2023-2025: 5 up / 2 down;\n"
         "mean +5.6%, median +11.9%; sign test p=0.23.",
         transform=ax2.transAxes, ha="center", va="top",
         fontsize=7.6, color=GREY, style="italic")

fig.suptitle(
    "The admitted forecast is materially non-stationary before capacity is committed",
    fontsize=10.8, fontweight="bold", y=0.97)

name = "Figure_3"
out = os.path.join(FIG, f"{name}.pdf")
fig.savefig(out, bbox_inches="tight", facecolor="white")
fig.savefig(out.replace(".pdf", ".png"), bbox_inches="tight", facecolor="white", dpi=180)
fig.savefig(out.replace(".pdf", ".svg"), bbox_inches="tight", facecolor="white")
print("wrote", out)
