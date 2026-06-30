# -*- coding: utf-8 -*-
"""
R167 Phase 5 (partial) — Bayesian hierarchical model of the PJM data-centre forecast RATCHET.
Replaces the descriptive "10/12 upward" with a fitted posterior of the per-vintage upward drift.

Data: IMM Table 5 — above-embedded adjustment (MW) for each TARGET year as forecast in successive
forecast VINTAGES. For a fixed target year, successive vintages revise the forecast; a systematic
positive drift across vintages is the 'ratchet'.

Model (hierarchical, robust):
    log F[v,t] = alpha[t] + g * vidx[v] + eps,  eps ~ Student-t(nu, 0, sigma)
  alpha[t]: target-year level (fixed effects);  g: common per-vintage drift (the ratchet, in log-MW/vintage);
  Priors: alpha[t]~N(log(mean_t),1.5), g~N(0,0.5), log sigma~N(-2,1), nu~Exp(1/30)+2.
Posterior via emcee (CPU). Report posterior of g (and exp(g)-1 = % drift per vintage), P(g>0),
and the implied 3-vintage cumulative over-forecast.
"""
import os, json, numpy as np
import emcee
from scipy import stats

HERE=os.path.dirname(os.path.abspath(__file__))
np.random.seed(20260628)

years=[2022,2023,2024,2025,2026,2027]
vint={"2022 LF":[897,1643,2344,3061,3885,4166],
      "2023 LF":[None,2231,3393,4654,6594,8300],
      "2024 LF":[None,None,2664,4673,7557,10064],
      "2025 LF":[None,None,None,3591,8453,13668]}
vnames=list(vint); vidx={vn:i for i,vn in enumerate(vnames)}
# build observation list (vidx, tidx, logF)
obs=[]
for vn in vnames:
    for ti,val in enumerate(vint[vn]):
        if val is not None: obs.append((vidx[vn], ti, np.log(val)))
obs=np.array(obs); T=len(years)
mean_logt=np.array([np.mean([np.log(vint[vn][ti]) for vn in vnames if vint[vn][ti] is not None]) for ti in range(T)])
print(f"N obs={len(obs)}  targets={T}  vintages={len(vnames)}")

def unpack(p):
    alpha=p[:T]; g=p[T]; logsig=p[T+1]; lognu=p[T+2]
    return alpha,g,logsig,lognu
def logprior(p):
    alpha,g,logsig,lognu=unpack(p)
    lp=0.0
    lp+=np.sum(stats.norm.logpdf(alpha,mean_logt,1.5))
    lp+=stats.norm.logpdf(g,0,0.5)
    lp+=stats.norm.logpdf(logsig,-2,1.0)
    nu=np.exp(lognu)
    lp+=stats.expon.logpdf(nu,scale=30)+lognu  # jacobian
    if not np.isfinite(lp): return -np.inf
    return lp
def loglike(p):
    alpha,g,logsig,lognu=unpack(p)
    sig=np.exp(logsig); nu=np.exp(lognu)+2.0
    mu=alpha[obs[:,1].astype(int)]+g*obs[:,0]
    r=(obs[:,2]-mu)/sig
    return np.sum(stats.t.logpdf(r,nu)-np.log(sig))
def logpost(p):
    lp=logprior(p)
    return lp+loglike(p) if np.isfinite(lp) else -np.inf

ndim=T+3; nw=64
p0=np.column_stack([np.tile(mean_logt,(nw,1))+0.1*np.random.randn(nw,T),
                    0.1*np.random.randn(nw), -2+0.3*np.random.randn(nw), np.log(20)+0.3*np.random.randn(nw)])
sampler=emcee.EnsembleSampler(nw,ndim,logpost)
state=sampler.run_mcmc(p0,1500,progress=False); sampler.reset()
sampler.run_mcmc(state,6000,progress=False)
chain=sampler.get_chain(discard=1000,thin=10,flat=True)
g=chain[:,T]
drift_pct=100*(np.exp(g)-1)   # % per vintage
cum3=100*(np.exp(3*g)-1)      # cumulative over 3 vintages
res=dict(
 n_obs=len(obs),
 g_logMW_per_vintage_median=round(float(np.median(g)),4),
 drift_pct_per_vintage_median=round(float(np.median(drift_pct)),1),
 drift_pct_per_vintage_CI95=[round(float(np.percentile(drift_pct,2.5)),1),round(float(np.percentile(drift_pct,97.5)),1)],
 P_drift_gt_0=round(float(np.mean(g>0)),4),
 cum_3vintage_pct_median=round(float(np.median(cum3)),0),
 cum_3vintage_pct_CI95=[round(float(np.percentile(cum3,2.5)),0),round(float(np.percentile(cum3,97.5)),0)],
 acceptance=round(float(np.mean(sampler.acceptance_fraction)),3),
)
print(json.dumps(res,indent=2))
json.dump(res,open(os.path.join(HERE,"P5_bayes_ratchet.json"),"w"),indent=2)
np.save(os.path.join(HERE,"P5_drift_pct.npy"),drift_pct)
print("saved P5_bayes_ratchet.json + P5_drift_pct.npy")
