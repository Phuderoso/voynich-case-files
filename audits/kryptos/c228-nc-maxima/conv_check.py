# Convention check ONLY (excess vs stamped value); computes no NC.
import sys,glob,collections,itertools,re
sys.path.insert(0,'/workspace/k209-d2-audit')
from recount209 import perm_maps, excess, N, CRP, CRS, KA
D='/workspace/k228-nc-maxima/kryptos-main/data'
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def idx(a): return {c:i for i,c in enumerate(a)}
A={'AZ':idx(AZ),'KA':idx(KA)}
def texts(c):
    d={}
    for l in open(f'{D}/cycle{c}/texts.tsv'):
        p=l.rstrip('\n').split('\t')
        if p[0] in('label','seed'): continue
        d[p[0] if (c=='219' or p[0].startswith('null') or p[0]=='K4') else 'null'+p[0]]=p[1]
    return d
def hits(c):
    out=[]
    if c=='219':
        for f in sorted(glob.glob(f'{D}/cycle219/null*.txt')+[f'{D}/cycle219/K4.txt']):
            if 'null1_124' not in f and 'nulls219' in f: continue
            for l in open(f):
                if l.startswith('H '):
                    t=l.split(); out.append((t[1],int(t[2]),*map(int,t[3:11]),tuple(map(int,t[11:]))))
    else:
        for f in sorted(glob.glob(f'{D}/cycle{c}/results_*.txt')):
            lab='K4' if f.endswith('results_k4.txt') else 'null'+f.split('results_null')[1][:-4]
            for l in open(f):
                if l.startswith('H '):
                    t=l.split(); out.append((lab,*map(int,t[1:10]),tuple(map(int,t[10].split(',')))))
    return out
def test(c,combos):
    T=texts(c);H=hits(c);cache={}
    res={}
    for al in sorted({h[4] for h in H}):
      sub=[h for h in H if h[4]==al][:3000]
      for pa,ca in combos:
        ok=0
        for lab,w,mode,dr,_al,be,model,p,e,bad,pi in sub:
            k=(w,pi)
            if k not in cache: cache[k]=perm_maps(w,pi)
            sig,inv=cache[k][mode];S=inv if dr else sig
            j=[S[x] for x in CRP];ct=T[lab]
            kv=[((A[ca][ct[j[t]]]+A[pa][CRS[t]])%26) if be else ((A[ca][ct[j[t]]]-A[pa][CRS[t]])%26) for t in range(24)]
            res_=[(j[t] if model else CRP[t])%p for t in range(24)]
            ee,_=excess(res_,kv)
            ok+=(ee==e)
        res[(al,pa,ca)]=(ok,len(sub))
    return res
for c in ['219','220','225']:
    print(c,{k:v for k,v in test(c,[(a,b) for a in('AZ','KA') for b in('AZ','KA')]).items() if v[0]==v[1] or True})
