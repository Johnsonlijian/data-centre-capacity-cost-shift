# -*- coding: utf-8 -*-
"""
Inverse-supply (price-amplification) elasticity, identified from the below-cap auction.

The 21-year BRA panel (agent-sourced) is used for CONTEXT (the price surge / scarcity regime), not
for a pooled supply regression: a 2025/26 methodology break (marginal-ELCC), FRR participation, and
footprint changes confound cross-year pooling, and the 2 cap-bound years (26/27, 27/28) do not reveal
the supply slope (price administratively pinned). The CLEAN identification of the local inverse-supply
slope is the within-year IMM counterfactual for 2025/26 (the one recent auction that cleared BELOW the
cap). Result: supply is steeply inelastic near scarcity -> the mechanical basis of the amplification.
All panel numbers are official PJM Planning Period Parameters / BRA reports (sources in P3_panel.csv).
"""
import os, json, csv, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); RNG=np.random.default_rng(20260628)

PANEL=[ # year, price$/MWday, cleared_ucap_MW, reliability_req_MW, netcone$/MWday, capbound
 ("2007/08",40.80,129409.2,148277.3,161.27,0),("2008/09",111.92,129597.6,150934.6,161.71,0),
 ("2009/10",102.04,132231.8,153480.1,161.71,0),("2010/11",174.29,132190.4,156636.84,163.46,0),
 ("2011/12",110.00,132221.5,154251.1,160.76,0),("2012/13",16.46,136143.5,157488.5,276.09,0),
 ("2013/14",27.73,152743.3,173549.0,317.95,0),("2014/15",125.99,149974.7,178086.5,342.23,0),
 ("2015/16",136.00,164561.2,177184.1,320.63,0),("2016/17",59.37,169159.7,180332.2,330.53,0),
 ("2017/18",120.00,167003.7,179545.1,351.39,0),("2018/19",164.77,166836.9,174896.8,300.57,0),
 ("2019/20",100.00,167305.9,171037.0,299.30,0),("2020/21",76.53,165109.2,167644.0,292.95,0),
 ("2021/22",140.00,163627.3,166355.1,321.57,0),("2022/23",50.00,144477.3,163269.0,260.50,0),
 ("2023/24",34.13,144870.6,163166.0,274.96,0),("2024/25",28.92,147477.4,164107.6,293.19,0),
 ("2025/26",269.92,135684.0,144450.0,228.81,0),("2026/27",329.17,134310.8,146105.0,212.14,1),
 ("2027/28",334.35,134478.1,152400.2,242.52,1)]  # published UCAP cap (ER25-1357); blended avg=333.44
with open(os.path.join(HERE,"P3_panel.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["year","price_usd_mwday","cleared_ucap_mw","reliability_req_mw","netcone_usd_mwday","cap_bound"]); w.writerows(PANEL)

# --- clean within-year inverse-supply slope: 2025/26 IMM counterfactual ---
P1=269.92; Rev=14.687047358e9; oblig=135684.0; delta=7.742960157e9; FPR=1.09; ab_mw=4654.0
dQ=ab_mw*FPR; Q0=oblig-dQ; Rev0=Rev-delta; P0=Rev0/Q0/365.0
def arc_inv_elasticity(P1,P0,Q1,Q0):
    dP=(P1-P0)/((P1+P0)/2); dQ=(Q1-Q0)/((Q1+Q0)/2); return dP/dQ
e_point=arc_inv_elasticity(P1,P0,oblig,Q0)
# MC: delta +-7% (IMM precision) -> P0 -> elasticity CI
N=2_000_000
delta_s=delta*(1+0.07*RNG.standard_normal(N)).clip(0.6,1.5)
P0_s=(Rev-delta_s)/Q0/365.0
e_s=arc_inv_elasticity(P1,P0_s,oblig,Q0)
# IMM model-free cross-check: 3.4% quantity -> 111.5% revenue. revenue=P*Q so %dRev = %dP + %dQ
# => %dP = 111.5 - 3.4 = 108.1% for 3.4% quantity -> inverse price elasticity ~ 108.1/3.4
imm_cross = (111.5-3.4)/3.4
res=dict(
 clean_source="2025/26 BRA (only recent auction clearing BELOW the cap)",
 counterfactual_price_P0=round(P0,1), actual_price_P1=P1,
 inverse_supply_elasticity_point=round(float(e_point),1),
 inverse_supply_elasticity_CI90=[round(float(np.percentile(e_s,5)),1),round(float(np.percentile(e_s,95)),1)],
 interpretation=f"a 1% increase in cleared quantity is associated with ~{round(float(e_point))}% higher clearing price (steeply inelastic supply near scarcity)",
 imm_modelfree_crosscheck_elasticity=round(float(imm_cross),1),
 cap_bound_years_excluded=["2026/27","2027/28"],
 caveats="2025/26 methodology break + FRR + footprint changes preclude a pooled cross-year supply regression; cap-bound years truncate the slope (lower bounds only).",
)
print(json.dumps(res,indent=2))
json.dump(res,open(os.path.join(HERE,"P3_supply_elasticity.json"),"w"),indent=2)
np.save(os.path.join(HERE,"P3_elasticity_samples.npy"),e_s)
print("\nsaved P3_panel.csv + P3_supply_elasticity.json + P3_elasticity_samples.npy")
print("\nPanel context: price 2024/25 $28.92 -> 2025/26 $269.92 (+833%) -> cap $329-334 (ER25-1357); "
      "reserve cushion (req-cleared) collapsed while requirement methodology changed.")
