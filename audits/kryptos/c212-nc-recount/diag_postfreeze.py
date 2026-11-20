# POST-FREEZE diagnostics (not part of the frozen rule); still before any case 212 file is opened.
import sys; sys.argv=['x']
import numpy as np, glob
import nc_recount as n
texts = dict(l.rstrip('\n').split('\t') for l in open(f'{n.WORK}/texts.tsv'))
def allscore(P):
    sc=[float(n.qg[n.qi(*[ord(c)-65 for c in P[i:i+4]])]) for i in range(94) if '?' not in P[i:i+4]]
    return sum(sc)/len(sc), len(sc)
res={}
for lab in texts:
    files=sorted(glob.glob(f'{n.WORK}/out/{lab}/*.raw')); seen=set(); best_first=None; best_all=None; best_all49=None
    for fn in files:
        for ln in open(fn):
            if not ln.startswith('H '): continue
            p,d2,known,out,P=n.hit(texts[lab],ln)
            if p not in (20,21): continue
            if d2 not in seen:
                seen.add(d2); nc=out['overlap'][0]
                if nc is not None: best_first=nc if best_first is None else max(best_first,nc)
            a,_=allscore(P); best_all=a if best_all is None else max(best_all,a)
            if known>=49: best_all49=a if best_all49 is None else max(best_all49,a)
    res[lab]=(best_first,best_all,best_all49)
nl=[v for k,v in res.items() if k!='K4']
print('K4 first-hit-rep maxNC',res['K4'][0],'| K4 all-window best (incl cribs)',res['K4'][1],' known>=49:',res['K4'][2])
print('nulls first-hit-rep maxNC',max(v[0] for v in nl if v[0] is not None),'| nulls all-window best',max(v[1] for v in nl),' known>=49:',max(v[2] for v in nl if v[2] is not None))
srt=sorted([v[0] for v in nl if v[0] is not None],reverse=True)[:5]; print('top5 null maxNC (any-hit)',srt)
