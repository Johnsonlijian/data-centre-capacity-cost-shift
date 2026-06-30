#!/usr/bin/env python3
"""Mechanism 3 (FERC-orthogonal): marginal-load price amplification / inframarginal transfer.
Decompose the IMM revenue effect into (a) resource cost of the incremental capacity and
(b) the residual price-amplification borne on infra-marginal capacity (a load->generator transfer).
All from the IMM's own published numbers + the clearing-price identity. Audit before integrating."""
# IMM published, per delivery year: actual RPM revenue, above-embedded effect (Delta), above-embedded MW, RTO obligation MW
Y = {
 "2025/26": dict(actual=14687047358, delta=7742960157, ab_mw=4654,  rto_mw=135684.0, imm_pct_rev=1.115),
 "2026/27": dict(actual=16124370889, delta=7271197971, ab_mw=7892,  rto_mw=134205.3, imm_pct_rev=None),
 "2027/28": dict(actual=16411578225, delta=6244523827, ab_mw=13018, rto_mw=134478.1, imm_pct_rev=None),
}
FPR=1.09  # forecast pool requirement (~ reserve margin) to convert peak-load MW -> UCAP obligation MW
tot_delta=tot_resource=0.0
print(f"{'DY':8s} {'price$/MWd':>10s} {'incrUCAP_MW':>11s} {'resourceB':>9s} {'priceEffB':>9s} {'ampl':>5s} {'%transfer':>9s}")
for dy,d in Y.items():
    price_day = d['actual']/d['rto_mw']/365.0           # blended avg $/MW-day (realized)
    incr_ucap = d['ab_mw']*FPR                            # incremental UCAP obligation
    resource = incr_ucap*price_day*365.0                  # resource cost of incremental capacity
    price_eff = d['delta']-resource                       # residual = inframarginal price amplification
    ampl = d['delta']/resource
    pct = price_eff/d['delta']*100
    tot_delta+=d['delta']; tot_resource+=resource
    print(f"{dy:8s} {price_day:10.2f} {incr_ucap:11.0f} {resource/1e9:9.3f} {price_eff/1e9:9.3f} {ampl:5.1f} {pct:8.1f}%")
print(f"\nAGGREGATE: delta ${tot_delta/1e9:.2f}B ; resource cost ${tot_resource/1e9:.2f}B ; "
      f"price-amplification ${ (tot_delta-tot_resource)/1e9:.2f}B = {(tot_delta-tot_resource)/tot_delta*100:.0f}% of the cost; "
      f"amplification {tot_delta/tot_resource:.1f}x")
print("\nSensitivity (FPR=1.0 lower bound on incremental UCAP -> larger transfer share):")
tr=sum(d['delta']-(d['ab_mw']*1.0*d['actual']/d['rto_mw']/365.0*365.0) for d in Y.values())
print(f"  FPR=1.00: price-amplification = {tr/tot_delta*100:.0f}% of total")
print("\nCross-check (IMM's own words, 2025/26): a ~3.4% quantity shift (4,654/135,684) drove a +111.5% revenue rise")
print(f"  quantity +{4654/135684*100:.1f}% vs revenue +111.5% -> the steep administrative VRR curve amplifies a marginal")
print("  load increment into a price rise applied to ALL cleared capacity (an inframarginal transfer to incumbents).")
print("ORTHOGONALITY: distinct from WHO-pays (cross-zone allocation) and WHETHER-load-appears (over-procurement);")
print("  this is WHAT-KIND-of-cost: most of the wedge is a load->generator wealth transfer, not capacity resource cost.")
print("  FERC EL25-49 addresses load-to-load cost causation; it does not address this load->generator price transfer.")
