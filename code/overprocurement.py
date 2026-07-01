#!/usr/bin/env python3
"""Asymmetric over-procurement risk / ratepayer-written option.
The manuscript does not convert attrition rates into a dollar exposure."""
import csv, os, statistics as st
SCR = os.path.dirname(os.path.abspath(__file__))  # data files live alongside this script

# ---------- TEST 1: non-stationarity under comparable IMM Table 5 vintages ----------
# The 2022 LF row is a total-adjustment historical anchor. The comparable
# above-embedded data-centre vintages start in 2023, so inference uses 2023+.
years=[2023,2024,2025,2026,2027]
vint={"2023 LF":[2231,3393,4654,6594,8300],
      "2024 LF":[None,2664,4673,7557,10064],
      "2025 LF":[None,None,3591,8453,13668]}
revs=[]
vnames=list(vint)
for ti in range(len(years)):
    col=[(vn,vint[vn][ti]) for vn in vnames if vint[vn][ti] is not None]
    for k in range(len(col)-1):
        a=col[k][1]; b=col[k+1][1]
        revs.append((years[ti],col[k][0],col[k+1][0],b-a,(b/a-1)*100))
ups=[r for r in revs if r[3]>0]; downs=[r for r in revs if r[3]<0]
print("=== TEST 1: forecast non-stationarity (comparable 2023+ vintages) ===")
print(f"consecutive-vintage revisions: {len(revs)} total; UP {len(ups)}, DOWN {len(downs)}, flat {len(revs)-len(ups)-len(downs)}")
print(f"mean revision: {st.mean([r[4] for r in revs]):+.1f}% ; median {st.median([r[4] for r in revs]):+.1f}%")
print("=> material non-stationarity at auction-relevant horizons; not a statistically significant upward ratchet.")
print("   (The manuscript excludes the non-comparable 2022 total-adjustment row from inference.)")
try:
    from scipy.stats import binomtest, ttest_1samp
    pct_revs=[r[4] for r in revs]
    bt=binomtest(len(ups), len(revs), 0.5, alternative='greater')  # H1: P(up) > 0.5
    tt=ttest_1samp(pct_revs, 0, alternative='greater')             # H1: mean revision > 0
    print(f"Sign test (H1: upward revisions dominate): p={bt.pvalue:.4f}  => p = {bt.pvalue:.2f}")
    print(f"One-sample t-test (H1: mean revision > 0): t={tt.statistic:.3f}, p={tt.pvalue:.4f}  => p = {tt.pvalue:.2f}")
    print("Key two-vintage revisions: 2026 target +28%; 2027 target +65%.")
except ImportError:
    print("(scipy not available; install with: pip install scipy)")

# ---------- TEST 2: dynamic concentration / gap time-path (B-9b 2026/2030/2046) ----------
rows=list(csv.reader(open(os.path.join(SCR,"crosszonal_caus_burden.csv"),encoding="utf-8")))
hdr=rows[0]; D=[dict(zip(hdr,r)) for r in rows[1:]]
def fnum(x):
    try: return float(x)
    except: return 0.0
print("\n=== TEST 2: dynamic gap (does concentration predict the gap over 2026-2046?) ===")
for yr in ("2026","2030","2046"):
    gs=[fnum(d[f"caus_share{yr}_pct"])/100 for d in D]
    hhi=sum(g*g for g in gs)
    dom_g=fnum(D[0][f"caus_share{yr}_pct"]); dom_b=fnum(D[0][f"burden_share{yr}_pct"])
    print(f"  {yr}: HHI(causation)={hhi:.3f} ; DOM gap = {dom_g:.1f}% cause vs {dom_b:.1f}% bear (ratio {dom_g/dom_b:.1f}x)")
print("  => gap is largest when causation is most concentrated (2026), moderates as it diffuses; HHI tracks the gap.")

# ---------- TEST 3: speculative over-procurement / ratepayer-written option ----------
print("\n=== TEST 3: materialization-risk asymmetry (no dollar exposure claim) ===")
# Materialization-risk parameters (regulators' OWN estimates):
miso_attrition=0.41          # MISO: Projected = Expected x (1-0.41) -> 41% of announced won't materialize
dom_queue_to_firm=16.6/70.0  # DOM ~70 GW queue -> 16.6 GW firm survives the gate (~76% never reaches firm)
print(f"MISO regulator's attrition on announced capacity: {miso_attrition*100:.0f}% won't materialize.")
print(f"DOM queue->firm survival: {dom_queue_to_firm*100:.0f}% (i.e. ~{(1-dom_queue_to_firm)*100:.0f}% of queued never reaches firm).")
print("The manuscript does not multiply these attrition rates by PJM dollars.")
print("Reason: realized shortfalls are not yet observed, so dollar exposure is not identifiable ex ante.")
print("ASYMMETRY (the option): capacity is paid 3 yr forward; if load is late/cancelled there is NO ratepayer clawback")
print("  of payments already made -> ratepayers write large loads a free option on capacity. This is ORTHOGONAL to")
print("  the allocation/cross-subsidy question (it applies even if every zone paid its exact causation share).")
