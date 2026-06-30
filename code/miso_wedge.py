#!/usr/bin/env python3
"""Bounded MISO second-market capacity-cost wedge (reduced-form, clearly labelled).
Method: data-centre capacity obligation (DC peak x (1+PRM)) x MISO seasonal PRA clearing price.
This is a cost-attribution illustration bounded by auction-price volatility, NOT an IMM-style
price counterfactual. Demonstrates the concentration-socialization structure recurs in a 2nd market.
"""
# --- MISO 2025/26 PRA seasonal Auction Clearing Prices ($/MW-day), primary source (PRA results 2025-05-29) ---
acp = {"summer":666.50, "fall":91.60, "winter":33.20, "spring":69.88}  # fall = North subregion (DC-heavy); fall-South USD 74.09 not applied
days = {"summer":92, "fall":91, "winter":90, "spring":92}
annual_per_mw = sum(acp[s]*days[s] for s in acp)
print(f"MISO 2025/26 annual capacity cost per MW (4-season) = ${annual_per_mw:,.0f}/MW-yr")
print(f"  (summer alone: ${acp['summer']*days['summer']:,.0f}/MW; summer ACP uniform across all 10 zones)")

# --- Data-centre capacity obligation (MISO LTLF Fig 13: projected DC capacity after 41% attrition) ---
# Source: MISO Dec 2024 LTLF Fig 13 — "projected" = "expected" × (1 − 41% attrition)
PRM = 0.092   # MISO 2025/26 planning reserve margin ~9.2%; use as obligation uplift
dc_cap = {2030: 7.0, 2040: 22.0}   # GW, from MISO LTLF Fig 13 (projected capacity, post-attrition)
for yr, gw in dc_cap.items():
    oblig_mw = gw * 1000 * (1 + PRM)
    cost_2526 = oblig_mw * annual_per_mw
    # lower bound: 2026/27 PRA prices fell ~42% → scale by 0.58 as lower illustration
    cost_low  = cost_2526 * 0.58
    print(f"\n{yr}: DC projected capacity (LTLF Fig 13) {gw} GW -> obligation ~{oblig_mw:,.0f} MW")
    print(f"   reduced-form annual capacity cost @2025/26 prices = ${cost_2526/1e9:.2f}B/yr (upper)")
    print(f"   lower illustration @ -42% (2026/27 price drop)    = ${cost_low/1e9:.2f}B/yr (lower)")
    print(f"   range: ~${cost_low/1e9:.1f}–{cost_2526/1e9:.1f}B/yr")

# --- Concentration (primary MISO LTLF facts) ---
print("\nConcentration (MISO LTLF Dec 2024 + analysis):")
print("  - DC growth concentrated in northern LRZs 1,2,3,6 (LRZ1 alone +4 GW DC); LRZs 1/6/9 lead total growth.")
print("  - Central MISO absorbs ~58% of data-centre ENERGY growth by 2046 (industry analysis of MISO forecast).")
print("  - DC = ~1/5 of MISO demand by 2030, ~1/4 by 2040; DC energy +149-241 TWh by 2044 (42-80 by 2030).")
print("\nSocialization (PRA primary): summer 2025/26 cleared UNIFORMLY at $666.50/MW-day across all 10 LRZs")
print("  -> the capacity price does NOT localize to the high-DC northern zones; cost is socialized footprint-wide.")
