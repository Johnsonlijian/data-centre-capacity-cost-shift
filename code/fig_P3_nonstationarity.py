# -*- coding: utf-8 -*-
"""Figure 3: forecast non-stationarity / upward ratchet.
Two panels: (a) above-embedded MW by target year across four forecast vintages;
            (b) per-cycle upward revision for the two BRA-committed target years.
Updated: Times New Roman, consistent palette, Nature Energy style.
"""
import os
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
_fig_dir = os.path.join(HERE, "..", "figures")
FIG = _fig_dir if os.path.isdir(_fig_dir) else HERE

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
BLUE  = "#34618f"
INK   = "#222222"
GRID  = "#e0e0e0"

# ── IMM Table 5: large-load adjustment (MW) by target year × forecast vintage ─
# Above-embedded (2023+); total adjustments (2022 LF)
YEARS = [2022, 2023, 2024, 2025, 2026, 2027]
VINT  = {
    "2022 LF": [897,  1643, 2344, 3061, 3885,  4166],
    "2023 LF": [None, 2231, 3393, 4654, 6594,  8300],
    "2024 LF": [None, None, 2664, 4673, 7557, 10064],
    "2025 LF": [None, None, None, 3591, 8453, 13668],
}
COLORS = {
    "2022 LF": GREY,
    "2023 LF": BLUE,
    "2024 LF": AMBER,
    "2025 LF": RED,
}
# Escalation: 2023 LF → 2025 LF for target years 2026 and 2027
ESC = {
    2026: (VINT["2023 LF"][4], VINT["2025 LF"][4]),  # 6594 → 8453 (+28%)
    2027: (VINT["2023 LF"][5], VINT["2025 LF"][5]),  # 8300 → 13668 (+65%)
}

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.4),
                                gridspec_kw={"width_ratios": [1.3, 1.0], "wspace": 0.30})
fig.subplots_adjust(left=0.07, right=0.97, top=0.83, bottom=0.14)

# ── Panel (a): vintage lines ───────────────────────────────────────────────────
for k, vals in VINT.items():
    xs = [y for y, v in zip(YEARS, vals) if v is not None]
    ys = [v for v in vals if v is not None]
    ax1.plot(xs, ys, marker="o", lw=2.0, ms=5.5, color=COLORS[k],
             label=k, zorder=3 + list(VINT).index(k))

ax1.set_xlabel("Target (delivery) year", fontsize=9)
ax1.set_ylabel("Large-load adjustment (MW)", fontsize=9)
ax1.set_title("(a)   The forecast is a moving target", loc="left", fontsize=10)
ax1.set_xlim(2021.5, 2027.8)
ax1.set_ylim(0, 15500)
ax1.set_xticks(YEARS)
ax1.grid(color=GRID, alpha=0.6, lw=0.5)
ax1.legend(frameon=False, title="Forecast vintage", title_fontsize=8, fontsize=8.5,
           loc="upper left")

# Annotate the 2027 jump
ax1.annotate("2027: 8,300 → 13,668 MW\n(+65% across two cycles)",
             xy=(2027, 13668), xytext=(2024.3, 13100),
             fontsize=8, color=RED,
             arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2))

# Shade region where the BRA commits the load
ax1.axvspan(2026.5, 2027.5, color=AMBER, alpha=0.10, zorder=1)
ax1.text(2027.1, 400, "BRA\ncommits", ha="center", fontsize=7.2, color=AMBER, style="italic")

# ── Panel (b): revision bars ────────────────────────────────────────────────────
bra_labels = ["2025/26\n(target yr 2026)", "2026/27\n(target yr 2027)"]
revisions   = [100 * (ESC[2026][1] / ESC[2026][0] - 1),
               100 * (ESC[2027][1] / ESC[2027][0] - 1)]

bars = ax2.bar([0, 1], revisions, color=[AMBER, RED], width=0.52, alpha=0.85,
               edgecolor=INK, lw=0.5)

for i, (rev, (v0, v1)) in enumerate(zip(revisions, [ESC[2026], ESC[2027]])):
    ax2.text(i, rev + 1.5, f"+{rev:.0f}%",
             ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
    ax2.text(i, rev / 2, f"{v0:,}→{v1:,} MW",
             ha="center", va="center", fontsize=6.5, color="white")

ax2.set_xticks([0, 1])
ax2.set_xticklabels(bra_labels, fontsize=9)
ax2.set_ylabel("Upward revision, 2023 LF to 2025 LF (%)", fontsize=9)
ax2.set_ylim(0, 84)
ax2.set_title("(b)   Vintage escalation for\nthe two BRA-committed target years", loc="left", fontsize=10)
ax2.grid(axis="y", color=GRID, alpha=0.6, lw=0.5)

# Source note
ax2.text(0.5, -0.16,
         "Source: IMM Table 5 (above-embedded vintages, 2023–2025).\n"
         "Of 12 consecutive-vintage revisions, 10 are upward (sign test p=0.02; runs test p=0.43, consistent with independence).",
         transform=ax2.transAxes, ha="center", va="top",
         fontsize=7.2, color=GREY, style="italic")

# ── Super-title ────────────────────────────────────────────────────────────────
fig.suptitle(
    "The admitted forecast ratchets upward: a non-stationary, asymmetrically revised commitment",
    fontsize=10.8, fontweight="bold", y=0.97)

out = os.path.join(FIG, "Figure_3.pdf")
fig.savefig(out, bbox_inches="tight", facecolor="white")
fig.savefig(out.replace(".pdf", ".png"), bbox_inches="tight", facecolor="white", dpi=180)
fig.savefig(out.replace(".pdf", ".svg"), bbox_inches="tight", facecolor="white")
print("wrote", out)
