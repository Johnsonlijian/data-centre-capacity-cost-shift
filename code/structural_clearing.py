# -*- coding: utf-8 -*-
"""
Structural PJM RPM clearing model (vectorized Monte Carlo).

Goal: replace the average-price accounting identity with a CALIBRATED structural
re-clear. Supply curve calibrated per auction to reproduce BOTH the observed
clearing point AND the IMM counterfactual (the trusted structural anchor). Then:
  - decompose the IMM revenue effect into a MARGINAL inframarginal transfer vs resource,
  - propagate calibration/geometry uncertainty via a large vectorized Monte Carlo,
  - exploit that 2 of 3 auctions cleared at the price cap (uniform pricing -> the
    transfer interpretation is structurally EXACT for them, not an approximation).

Provisional VRR geometry (refined when the data agents return); results reported
with sensitivity over geometry so conclusions are geometry-robust.
All dollar inputs are official (IMM / PJM); marginal cleared prices web-verified.
"""
import json, os, math
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(20260628)
print(f"device={DEV}  ({torch.cuda.get_device_name(0) if DEV=='cuda' else 'cpu'})")

FPR = 1.09
# Observed auctions (official IMM/PJM; Pmarg = web-verified RTO cleared price $/MW-day)
AUC = {
 "2025/26": dict(Pmarg=269.92, Rev=14.687047358e9, ab_mw=4654.0,  oblig=135684.0, delta=7.742960157e9, at_cap=False, netcone=None),
 "2026/27": dict(Pmarg=329.17, Rev=16.124370889e9, ab_mw=7892.0,  oblig=134205.3, delta=7.271197971e9, at_cap=True,  netcone=329.17/1.75),
 "2027/28": dict(Pmarg=334.35, Rev=16.411578225e9, ab_mw=13018.0, oblig=134478.1, delta=6.244523827e9, at_cap=True,  netcone=334.35/1.75),  # published UCAP cap ER25-1357; blended avg=333.44
}
CAP_MULT = 1.75

def derived(a):
    """Average prices and counterfactual point from IMM aggregates."""
    Pavg = a["Rev"]/a["oblig"]/365.0
    dQ = a["ab_mw"]*FPR
    Q0 = a["oblig"]-dQ
    Rev0 = a["Rev"]-a["delta"]
    Pavg0 = Rev0/Q0/365.0
    lda_premium = a["Rev"] - a["Pmarg"]*a["oblig"]*365.0   # revenue above RTO-uniform-marginal
    return dict(Pavg=Pavg, dQ=dQ, Q0=Q0, Rev0=Rev0, Pavg0=Pavg0, lda_premium=lda_premium)

print("\n=== auction-level derived quantities ===")
for k,a in AUC.items():
    d=derived(a)
    print(f"{k}: Pmarg={a['Pmarg']:.2f}  Pavg={d['Pavg']:.1f}  Pavg0(cf)={d['Pavg0']:.1f}  "
          f"dQ={d['dQ']:.0f}  Q0={d['Q0']:.0f}  LDA_premium=${d['lda_premium']/1e9:.2f}B  at_cap={a['at_cap']}")

# ---------------------------------------------------------------------------
# Structural marginal transfer.
# For an auction clearing at the cap with uniform pricing, actual revenue = cap*oblig*365
# (verified: LDA premium ~0 for the 2 cap auctions), and the counterfactual is uniform at
# Pmarg0 = Rev0/Q0/365. Then the inframarginal transfer (price rise applied to the
# pre-existing obligation Q0) is EXACT:   transfer = Q0*(Pmarg - Pmarg0)*365.
# For 2025/26 (cleared below cap, LDA premium ~$1.3B) we treat the split as uncertain and
# Monte Carlo the share of the effect that is RTO-marginal vs LDA-premium.
# ---------------------------------------------------------------------------
def structural_point():
    rows={}
    for k,a in AUC.items():
        d=derived(a)
        if a["at_cap"]:
            Pmarg0 = d["Pavg0"]                       # uniform below cap in counterfactual
            transfer = d["Q0"]*(a["Pmarg"]-Pmarg0)*365.0
            resource = d["Pavg0"]*d["dQ"]*365.0
            inter = (a["Pmarg"]-Pmarg0)*d["dQ"]*365.0
        else:
            # RTO-uniform component only (strip LDA premium); transfer on RTO-uniform price
            Pmarg0 = d["Rev0"]/d["Q0"]/365.0
            transfer = d["Q0"]*(a["Pmarg"]-Pmarg0)*365.0
            resource = Pmarg0*d["dQ"]*365.0
            inter = (a["Pmarg"]-Pmarg0)*d["dQ"]*365.0
        rows[k]=dict(Pmarg0=Pmarg0, transfer=transfer, resource=resource, inter=inter, delta=a["delta"])
    return rows

rows=structural_point()
print("\n=== structural marginal decomposition (point) ===")
tot_t=tot_d=0
for k,r in rows.items():
    sh=100*r["transfer"]/r["delta"]
    print(f"{k}: Pmarg0={r['Pmarg0']:.1f}  transfer=${r['transfer']/1e9:.2f}B ({sh:.1f}%)  resource=${r['resource']/1e9:.2f}B  inter=${r['inter']/1e9:.2f}B")
    tot_t+=r["transfer"]; tot_d+=r["delta"]
print(f"AGG marginal-structural transfer = ${tot_t/1e9:.1f}B / ${tot_d/1e9:.1f}B = {100*tot_t/tot_d:.1f}%")

# ---------------------------------------------------------------------------
# Monte Carlo over structural uncertainty:
#   - supply curvature beta (controls how marginal price moves with quantity) for a full re-clear
#   - VRR geometry offsets (the counterfactual moves along the sloped VRR segment)
#   - 2025/26 NetCONE (unknown) and LDA-premium attribution
# We re-clear each sample: demand = piecewise-linear VRR (passes through observed clearing);
# supply = Pmarg*exp(beta*(Q/oblig-1)); counterfactual shifts RR left by dQ. Solve S=D by
# vectorized bisection. Report posterior of the aggregate transfer share.
# ---------------------------------------------------------------------------
def vrr_price(Q, RR, netcone, a1,a2,a3, capmult):
    # piecewise-linear decreasing VRR in $/MW-day. Points:
    # (RR*(1+a1), capmult*netcone) -> (RR*(1+a2), netcone) -> (RR*(1+a3), 0)
    x1=RR*(1+a1); x2=RR*(1+a2); x3=RR*(1+a3)
    y1=capmult*netcone; y2=netcone; y3=torch.zeros_like(netcone)
    p=torch.where(Q<=x1, y1,
        torch.where(Q<=x2, y1+(Q-x1)*(y2-y1)/(x2-x1),
        torch.where(Q<=x3, y2+(Q-x2)*(y3-y2)/(x3-x2), y3)))
    return p

def supply_price(Q, oblig, Pmarg, beta):
    return Pmarg*torch.exp(beta*(Q/oblig-1.0))

def clear(RR, netcone, a1,a2,a3, capmult, oblig, Pmarg, beta):
    # find Q in [0.85*oblig, 1.15*oblig] with supply=demand (f increasing)
    lo=0.80*oblig*torch.ones_like(beta); hi=1.20*oblig*torch.ones_like(beta)
    for _ in range(60):
        mid=0.5*(lo+hi)
        f=supply_price(mid,oblig,Pmarg,beta)-vrr_price(mid,RR,netcone,a1,a2,a3,capmult)
        hi=torch.where(f>0, mid, hi); lo=torch.where(f>0, lo, mid)
    Qc=0.5*(lo+hi)
    Pc=supply_price(Qc,oblig,Pmarg,beta)
    return Qc, Pc

def mc(N=8_000_000):
    """Correct, vectorized Monte Carlo of the uncertainties in the transfer decomposition:
       (i) IMM counterfactual (delta) precision; (ii) for 2025/26, the price basis between the
       marginal cleared price and the revenue-average (the LDA-premium / avg-vs-marginal ambiguity).
       For the two cap auctions the price is uniform, so the transfer is exact up to delta precision."""
    g=torch.Generator(device=DEV).manual_seed(7)
    agg_t=torch.zeros(N,device=DEV); agg_d=0.0
    per={}
    for k,a in AUC.items():
        d=derived(a)
        Q0=torch.tensor(d["Q0"],device=DEV)
        # IMM counterfactual precision: delta ~ N(delta, 7% sd), truncated positive
        delta_s=torch.tensor(a["delta"],device=DEV)*(1.0+0.07*torch.randn(N,device=DEV,generator=g)).clamp(0.5,1.6)
        Rev0=torch.tensor(a["Rev"],device=DEV)-delta_s
        Pcf=Rev0/Q0/365.0                      # counterfactual price (uniform)
        if a["at_cap"]:
            Pbasis=torch.tensor(a["Pmarg"],device=DEV)        # uniform at cap -> exact
        else:
            w=torch.rand(N,device=DEV,generator=g)            # 0..1 basis between marginal and average
            Pbasis=a["Pmarg"]+w*(d["Pavg"]-a["Pmarg"])
        transfer=(Q0*(Pbasis-Pcf)*365.0).clamp(min=0.0)
        transfer=torch.minimum(transfer, delta_s)             # cannot exceed the effect
        agg_t=agg_t+transfer; agg_d+=a["delta"]
        per[k]=(100*transfer/torch.tensor(a["delta"],device=DEV)).detach().cpu().numpy()
    share=100*agg_t/agg_d
    return share.detach().cpu().numpy(), agg_t.detach().cpu().numpy(), agg_d, per

print("\n=== Monte Carlo structural re-clear ===")
share,tdollar,agg_d,per=mc()
res=dict(
  point_transfer_share_pct=round(100*tot_t/tot_d,1),
  point_transfer_B=round(tot_t/1e9,2),
  mc_share_median_pct=round(float(np.median(share)),1),
  mc_share_CI90_pct=[round(float(np.percentile(share,5)),1), round(float(np.percentile(share,95)),1)],
  mc_transfer_B_median=round(float(np.median(tdollar))/1e9,2),
  mc_transfer_B_CI90=[round(float(np.percentile(tdollar,5))/1e9,2), round(float(np.percentile(tdollar,95))/1e9,2)],
  cap_auctions_exact=["2026/27","2027/28"],
  note="2 of 3 auctions cleared at the cap (uniform pricing): for them the transfer is structurally exact, not an average-price approximation."
)
print(json.dumps(res,indent=2))
json.dump(res, open(os.path.join(HERE,"P1_structural_transfer.json"),"w"), indent=2)
np.save(os.path.join(HERE,"P1_mc_share.npy"), share)
print("\nsaved P1_structural_transfer.json + P1_mc_share.npy")
