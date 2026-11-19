"""Anchor gate: pi first 700 digits (integer part included) from 3 independent sources,
then pi windows k_t=(10a+b+s) mod 26 for offsets 0..399, s in {0,-1}; compare with keys217.bin."""
import mpmath, hashlib, numpy as np, json, sys
N=700
# 1) mpmath
mpmath.mp.dps=N+20
d_mp=mpmath.nstr(mpmath.pi,N+10,strip_zeros=False).replace('.','')[:N]
# 2) Machin formula, pure integers
def arctan_inv(x,one):
    s=t=one//x; x2=x*x; n=1; sign=-1
    while t:
        t//=x2; n+=2; s+=sign*(t//n); sign=-sign
    return s
one=10**(N+30)
pi_m=4*(4*arctan_inv(5,one)-arctan_inv(239,one))
d_machin=str(pi_m)[:N]
# 3) published list OEIS A000796 b-file
pub=''.join(l.split()[1] for l in open('inputs/oeis_b000796.txt') if l.strip() and not l.startswith('#'))[:N]
ok=d_mp==d_machin==pub
print('pi digits 700: mpmath==Machin==OEIS A000796:',ok)
print('first 50:',d_mp[:50]); print('sha256(700 digits):',hashlib.sha256(d_mp.encode()).hexdigest())
if not ok: sys.exit('ANCHOR FAIL: digit sources disagree')
D=[int(c) for c in d_mp]
W={}
for off in range(400):
    for s in (0,-1):
        W[(off,s)]=bytes(((10*D[off+2*t]+D[off+2*t+1]+s)%26) for t in range(97))
# compare against keys217.bin via keys217.tsv ids
kb=open('inputs/keys217.bin','rb').read(); assert len(kb)%97==0
rows=[l.rstrip('\n').split('\t') for l in open('inputs/keys217.tsv')][1:]
ids={}
for r in rows:
    if r[1]=='pi': ids[(int(r[2]),int(r[3]))]=int(r[0])
mism=[];missing=[]
for k,v in W.items():
    if k not in ids: missing.append(k); continue
    i=ids[k]
    if kb[i*97:(i+1)*97]!=v: mism.append(k)
print('offset0 s=0 window:',list(W[(0,0)][:12]),'... keys217 id',ids.get((0,0)),'match',(0,0) not in mism and (0,0) not in missing)
print('offset0 s=-1 window:',list(W[(0,-1)][:12]),'... keys217 id',ids.get((0,-1)),'match',(0,-1) not in mism and (0,-1) not in missing)
print('pi windows in my set: %d; distinct: %d; absent from keys217.tsv: %d; byte mismatches: %d'%(len(W),len(set(W.values())),len(missing),len(mism)))
if missing: print('absent (dedup across streams?):',missing[:20])
open('pi700.txt','w').write(d_mp+'\n')
with open('pi_windows.bin','wb') as f, open('pi_windows.tsv','w') as g:
    g.write('wid\toffset\tshift\n'); i=0
    for off in range(400):
        for s in (0,-1):
            f.write(W[(off,s)]); g.write(f'{i}\t{off}\t{s}\n'); i+=1
print('sha256 pi_windows.bin:',hashlib.sha256(open('pi_windows.bin','rb').read()).hexdigest())
