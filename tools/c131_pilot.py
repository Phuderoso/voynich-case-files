"""C131 controls-only design pilot (seeds 11904-11905, R 50, 5 plants/page). No manuscript page is scored.
The first pilot run used a scattered-line pool null (lines drawn without replacement from all other pages of the stratum);
that pseudo() was replaced by N-RUN before the freeze (see case-file/C131 section 0). -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, time; sys.path.insert(0,'tools')
import c131_intermediate_pages as C
C.R = 50; C.NPL = 5
tmpl = C.ms_pages(C.FILES[0][1]); t=time.time()
for ci,(name,fa,fb) in enumerate(C.CTRL):
    P,use = C.ctrl_pages(tmpl,fa,fb)
    I,res,NULL = C.run_set(P,name,11904,11905,ci)
    inf=[p for p,r in res.items() if r['status']=='INFORMATIVE']
    k=sum(res[p]['p']<=0.05 for p in inf)
    pw={f:sum(res[p][f'plant_{f}']['hits'] for p in inf)/(5*len(inf)) for f in C.FS}
    import numpy as np
    print(name, 'flagged',k,'/',len(inf), 'power',pw, 'mean d',np.mean([res[p]['d'] for p in inf]), 'null d', np.mean([res[p]['null_d_mean'] for p in inf]), f'{time.time()-t:.1f}s', flush=True)
