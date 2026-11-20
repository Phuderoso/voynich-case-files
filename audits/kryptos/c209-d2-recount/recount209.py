#!/usr/bin/env python3
"""Independent D2 / D3 recount for Kryptos case 209 (cycle 223), Voynich desk.
Written from the PREREG223 prose (Statistics section) + the hit-line format documented in col21.c's header.
Every hit line is re-verified: j[0..23] recomputed from pi/mode/dir, key values and the excess<=1 test recomputed here.
Units (per text, per period p):
  R      raw configurations at excess<=1 (count of hit lines)
  D2     distinct (alphabet, form, model, p, j[0..23])                       -- PREREG223 primary collapsed unit
  D3map  distinct (alphabet, form, model, p, residue[0..23], keyvalue[0..23]) -- PREREG223 'crib map' (descriptive)
  D3read distinct (w, alphabet, form, model, p, partial reading)             -- Voynich-desk width x reading family:
         column orders whose crib-derived key yields the same 97-letter partial decrypt ('?' where undetermined) are one.
usage: recount209.py OUTDIR_OR_FILES... > counts.tsv
"""
import sys, os, glob, hashlib, collections, json
N=97
KA="KRYPTOSABCDEFGHIJLMNQUVWXZ"
CRP=list(range(21,34))+list(range(63,74))
CRS="EASTNORTHEASTBERLINCLOCK"
AI=[{chr(65+i):i for i in range(26)},{c:i for i,c in enumerate(KA)}]
INV=[[chr(65+i) for i in range(26)],list(KA)]

def perm_maps(w,pi):
    rows=(N+w-1)//w
    col_at=[0]*w
    for c in range(w): col_at[pi[c]]=c
    out=[]
    for mode in (0,1):
        sig=[0]*N; q=0
        if mode==1:
            for k in range(w):
                c=col_at[k]
                for r in range(rows):
                    cell=r*w+c
                    if cell<N: sig[cell]=q; q+=1
        else:
            for r in range(rows):
                for k in range(w):
                    cell=r*w+col_at[k]
                    if cell<N: sig[cell]=q; q+=1
        inv=[0]*N
        for i in range(N): inv[sig[i]]=i
        out.append((sig,inv))
    return out

def excess(res,kv):
    cls=collections.defaultdict(collections.Counter)
    for r,v in zip(res,kv): cls[r][v]+=1
    bad=[]
    for r,c in cls.items():
        if len(c)>2: return 2,None
        if len(c)==2:
            if min(c.values())>=2: return 2,None
            bad.append(r)
    if len(bad)>1: return 2,None
    return (1 if bad else 0), cls

def process(ct, lines):
    """returns dict p -> dict of sets / counts; raises on any verification failure"""
    st=collections.defaultdict(lambda:{'R':0,'D2':set(),'D3map':set(),'D3read':set()})
    cache={}
    for ln in lines:
        a,b=ln.split('|'); f=a.split(); j_pr=list(map(int,b.split()))
        w,mode,dr,al,be,model,p,e,bad=map(int,f[2:11]); pi=tuple(map(int,f[11:]))
        assert len(pi)==w and len(j_pr)==24
        key=(w,pi)
        if key not in cache: cache[key]=perm_maps(w,pi)
        sig,inv=cache[key][mode]; S=inv if dr else sig
        j=[S[x] for x in CRP]
        assert j==j_pr, ('j mismatch',ln)
        kv=[]
        for t in range(24):
            x=AI[al][ct[j[t]]]; y=AI[al][CRS[t]]
            kv.append((x+y)%26 if be else (x-y)%26)
        res=[(j[t] if model else CRP[t])%p for t in range(24)]
        ee,cls=excess(res,kv)
        assert ee==e and ee<=1, ('excess mismatch',ln,ee)
        d=st[p]; d['R']+=1
        d['D2'].add((al,be,model,p,tuple(j)))
        d['D3map'].add((al,be,model,p,tuple(res),tuple(kv)))
        # partial reading: residue classes with a unique majority value are determined
        kres={}
        for r,c in cls.items():
            mc=c.most_common()
            if len(mc)==1 or mc[0][1]>mc[1][1]: kres[r]=mc[0][0]
        rd=[]
        for i in range(N):
            r=(S[i] if model else i)%p
            if r in kres:
                x=AI[al][ct[S[i]]]; k=kres[r]
                rd.append(INV[al][(x-k)%26 if be==0 else (k-x)%26])
            else: rd.append('?')
        d['D3read'].add((w,al,be,model,p,''.join(rd)))
    return st

if __name__=='__main__':
    texts=dict(l.rstrip('\n').split('\t') for l in open(sys.argv[1]))  # label \t ct
    outdir=sys.argv[2]; periods=list(map(int,sys.argv[3].split(',')))
    labs=sys.argv[4].split(',') if len(sys.argv)>4 else list(texts)
    print('text\t'+'\t'.join(f'p{p}_{u}' for p in periods for u in ('R','D2','D3map','D3read')))
    for lab in labs:
        files=sorted(glob.glob(os.path.join(outdir,lab,'*.raw')))
        lines=[l for fn in files for l in open(fn) if l.startswith('H ')]
        st=process(texts[lab],lines)
        row=[lab]
        for p in periods:
            d=st.get(p,{'R':0,'D2':(),'D3map':(),'D3read':()})
            row+= [str(d['R']),str(len(d['D2'])),str(len(d['D3map'])),str(len(d['D3read']))]
        print('\t'.join(row),flush=True)
