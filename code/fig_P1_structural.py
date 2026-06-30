# -*- coding: utf-8 -*-
"""Figure 4: price-amplification transfer — structural decomposition + GPU MC robustness.
Panel (a): stacked $B bars by delivery year (resource cost teal | transfer amber), with
3-auction total. Panel (b): GPU Monte-Carlo posterior of transfer share, with 4-method band.
"""
import os, json
import numpy as np
import matplotlib as mpl; mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
_fig_dir = os.path.join(HERE, "..", "figures")
OUT  = _fig_dir if os.path.isdir(_fig_dir) else HERE
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
INK   = "#222222"
RED   = "#b3402e"
BLUE  = "#34618f"
WHITE = "#ffffff"

# ── SI S6 data (structural P×Q, average zonal price) ─────────────────────────
YEARS   = ["2025/26",  "2026/27",  "2027/28"]
RES_B   = [0.55,       1.03,       1.73]    # resource cost $B
TRAN_B  = [7.19,       6.24,       4.51]    # inframarginal transfer $B
SHARES  = [92.9,       85.8,       72.3]    # transfer %
CAP_EX  = [False,      True,       True]    # cleared at fixed-$ collar (ER25-1357)

TOTAL_RES  = round(sum(RES_B),  2)   # 3.31
TOTAL_TRAN = round(sum(TRAN_B), 2)   # 17.94
TOTAL_TOT  = TOTAL_RES + TOTAL_TRAN  # 21.25 ≈ 21.26
TOTAL_SH   = TOTAL_TRAN / TOTAL_TOT * 100  # ~84.4%

# ── Figure layout ─────────────────────────────────────────────────────────────
fig, (axL, axR) = plt.subplots(
    1, 2, figsize=(10.0, 4.4),
    gridspec_kw={"width_ratios": [1.0, 0.88]}
)
fig.subplots_adjust(wspace=0.38, left=0.07, right=0.97, top=0.82, bottom=0.14)

# ── Panel (a): stacked vertical bars ─────────────────────────────────────────
x   = np.arange(len(YEARS))
TOT = 3   # index of the "total" pseudo-column
w   = 0.52
x_all  = np.array([0., 1., 2., 3.8])
res_all  = RES_B  + [TOTAL_RES]
tran_all = TRAN_B + [TOTAL_TRAN]
sh_all   = SHARES + [TOTAL_SH]
ce_all   = CAP_EX + [None]

alphas = [0.80, 0.80, 0.80, 0.92]

for i, (xi, rb, tb, sh, ce, al) in enumerate(
        zip(x_all, res_all, tran_all, sh_all, ce_all, alphas)):
    axL.bar(xi, rb, width=w, color=TEAL,  alpha=al, zorder=3)
    axL.bar(xi, tb, width=w, bottom=rb, color=AMBER, alpha=al, zorder=3)

    # Transfer % (white bold, centered in amber segment)
    axL.text(xi, rb + tb/2, f"{sh:.0f}%",
             ha="center", va="center",
             fontsize=(12 if i == TOT else 11),
             fontweight="bold", color=WHITE, zorder=5)

    # Resource $B label inside teal (if tall enough)
    if rb > 0.45:
        axL.text(xi, rb/2, f"${rb:.2f}B",
                 ha="center", va="center",
                 fontsize=7.2, color=WHITE, zorder=5)

    # Cap-exact footnote below bars
    if ce is True:
        axL.text(xi, -0.52, "(cap-exact)",
                 ha="center", va="top", fontsize=7.2, color=AMBER)
    elif ce is False:
        axL.text(xi, -0.52, "(avg. price*)",
                 ha="center", va="top", fontsize=7.2, color=GREY)

# Dashed separator before total column
axL.axvline(3.1, color=GREY, lw=0.7, ls="--", alpha=0.55)

# x-axis labels
axL.set_xticks(x_all)
axL.set_xticklabels(YEARS + ["3-auction\ntotal"], fontsize=9.2)
axL.set_xlim(-0.55, 4.22)
axL.set_ylim(-1.5, 23.5)
axL.set_ylabel("USD billions (IMM, restricted-curve)", fontsize=9)

# "amplification" annotation on the total bar
total_h = TOTAL_RES + TOTAL_TRAN
axL.annotate("6.4× amplification\n(revenue / resource cost)",
             xy=(3.8 + w/2 + 0.04, total_h * 0.62),
             xytext=(2.9, total_h * 0.82),
             fontsize=7.5, color=INK, ha="center", va="center",
             arrowprops=dict(arrowstyle="->", color=GREY, lw=0.7))

# "robust 84-86%" note
axL.text(0.01, -0.07, "* 2025/26 at avg. zonal price; robust 84–86% under reserve-margin sensitivity",
         fontsize=6.6, color=GREY, style="italic", ha="left", va="top",
         transform=axL.transAxes)

# Legend
legend_els = [
    Patch(facecolor=TEAL,  alpha=0.82, label="Resource cost of increment"),
    Patch(facecolor=AMBER, alpha=0.82, label="Inframarginal transfer to incumbents"),
]
axL.legend(handles=legend_els, loc="upper right", frameon=False,
           fontsize=8.0, handlelength=1.1)
axL.set_title("(a)   Per-delivery-year P×Q decomposition", loc="left", fontsize=10)

# ── Panel (b): GPU Monte-Carlo posterior ──────────────────────────────────────
mc_path = os.path.join(HERE, "P1_mc_share.npy")
j_path  = os.path.join(HERE, "P1_structural_transfer.json")

if os.path.exists(mc_path) and os.path.exists(j_path):
    share = np.load(mc_path)
    j     = json.load(open(j_path))
    med   = j["mc_share_median_pct"]
    lo, hi = j["mc_share_CI90_pct"]

    # Smooth histogram via moving-average on fine bin counts
    counts, edges = np.histogram(share, bins=400, density=True)
    win = 6
    smooth = np.convolve(counts, np.ones(win)/win, mode="same")
    centers = 0.5 * (edges[:-1] + edges[1:])

    axR.fill_between(centers, smooth, alpha=0.38, color=TEAL, step="mid")
    axR.plot(centers, smooth, color=TEAL, lw=1.2, drawstyle="steps-mid", alpha=0.7)

    axR.axvspan(lo, hi,  color=TEAL,  alpha=0.13, label=f"90% CI [{lo:.0f}, {hi:.0f}]%")
    axR.axvline(med,     color=INK,   lw=2.0, zorder=5, label=f"median {med:.0f}%")
    axR.axvspan(81, 90,  color=AMBER, alpha=0.20, label="4-method band 81–90%")

    axR.set_xlabel("inframarginal-transfer share (%)", fontsize=9)
    axR.set_ylabel("posterior density", fontsize=9)
    axR.set_title("(b)   GPU Monte-Carlo robustness check\n"
                  r"      8$\times$10$^6$ draws over 2025/26 price-reference uncertainty",
                  loc="left", fontsize=9.5)
    axR.yaxis.set_ticks([])
    axR.legend(frameon=False, fontsize=8.2, loc="upper left")
else:
    axR.text(0.5, 0.5, "P1_mc_share.npy not found", transform=axR.transAxes,
             ha="center", va="center")

# ── Super-title ───────────────────────────────────────────────────────────────
fig.suptitle(
    "~84% of the USD 21.26B capacity-market effect is a wealth transfer to incumbents, not a cost of service",
    fontsize=10.8, fontweight="bold", y=0.97)

fig.savefig(os.path.join(OUT, "Figure_4.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "Figure_4.png"), bbox_inches="tight", dpi=180)
fig.savefig(os.path.join(OUT, "Figure_4.svg"), bbox_inches="tight")
print("wrote Figure_4")
