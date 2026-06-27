from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG_OUT = OUT / "figures"


def check_crosszonal() -> dict[str, float]:
    df = pd.read_csv(DATA / "crosszonal_caus_burden.csv")
    dom = df.loc[df["zone"] == "DOM"].iloc[0]
    aep = df.loc[df["zone"] == "AEP"].iloc[0]
    checks = {
        "dom_causation_share_2026_pct": float(dom["caus_share2026_pct"]),
        "dom_burden_share_2026_pct": float(dom["burden_share2026_pct"]),
        "dom_causation_burden_ratio_2026": float(dom["ratio2026"]),
        "dom_plus_aep_causation_share_2026_pct": float(dom["caus_share2026_pct"] + aep["caus_share2026_pct"]),
    }
    return checks


def check_forecast_instability() -> dict[str, float]:
    df = pd.read_csv(DATA / "forecast_instability.csv")
    v2023 = float(df.loc[df["vintage"] == "2023 LF", "target_2027"].iloc[0])
    v2025 = float(df.loc[df["vintage"] == "2025 LF", "target_2027"].iloc[0])
    v2026_2023 = float(df.loc[df["vintage"] == "2023 LF", "target_2026"].iloc[0])
    v2026_2025 = float(df.loc[df["vintage"] == "2025 LF", "target_2026"].iloc[0])
    return {
        "target_2027_2023_vintage_mw": v2023,
        "target_2027_2025_vintage_mw": v2025,
        "target_2027_revision_pct": (v2025 / v2023 - 1.0) * 100.0,
        "target_2026_revision_pct": (v2026_2025 / v2026_2023 - 1.0) * 100.0,
    }


def plot_crosszonal() -> None:
    df = pd.read_csv(DATA / "crosszonal_caus_burden.csv")
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    x = df["burden_share2026_pct"]
    y = df["caus_share2026_pct"]
    s = 30 + df["adj2026"].clip(lower=0) / 8.0
    ax.scatter(x, y, s=s, alpha=0.75, edgecolor="white", linewidth=0.7)
    lim = max(float(x.max()), float(y.max())) * 1.12
    ax.plot([0, lim], [0, lim], "--", color="#667085", linewidth=1)
    for zone in ["DOM", "AEP", "COMED"]:
        row = df.loc[df["zone"] == zone].iloc[0]
        ax.annotate(zone, (row["burden_share2026_pct"], row["caus_share2026_pct"]), xytext=(5, 5), textcoords="offset points")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("Burden share: zone peak / RTO peak (%)")
    ax.set_ylabel("Causation share: zone adjustment / RTO adjustment (%)")
    ax.set_title("PJM 2026 data-centre capacity adjustment: causation vs burden")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_OUT / "rebuilt_crosszonal_causation_burden.png", dpi=200)
    plt.close(fig)


def plot_forecast_instability() -> None:
    df = pd.read_csv(DATA / "forecast_instability.csv").set_index("vintage")
    years = [2022, 2023, 2024, 2025, 2026, 2027]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for vintage, row in df.iterrows():
        vals = [row.get(f"target_{year}") for year in years]
        ax.plot(years, vals, marker="o", label=vintage)
    ax.set_xlabel("Target delivery year")
    ax.set_ylabel("Large-load adjustment (MW)")
    ax.set_title("Forecast-vintage non-stationarity")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_OUT / "rebuilt_forecast_instability.png", dpi=200)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    checks = {}
    checks.update(check_crosszonal())
    checks.update(check_forecast_instability())
    (OUT / "claim_checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    pd.DataFrame([checks]).to_csv(OUT / "claim_checks.csv", index=False)
    plot_crosszonal()
    plot_forecast_instability()
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
