"""Blind recount of PREREG216 Part A stage 2 (Voynich desk). Written from PREREG216/PREREG214 text only;
check216.py / summary216.json NOT opened.
Per line: re-derive the 24 crib digits from (perm,dir,X,Y,form) and compare with the C line.
Drop the failing seat (s23) / try each leave-one-out (s24). Exact consistency mod 10 (= mod 2 and mod 5 by elimination) with
 Gromark k_n = k_{n-L} + k_{n-L+1} (mod 10), primer k_0..k_{L-1}, L 1..25, and periodic digits P 1..25,
 key index = plaintext position i (ix 0) or carved position S[i] (ix 1)."""
import numpy as np, sys, json, re
K4=open('../c217-pi/inputs/k4.txt').read().strip()
I='../c217-pi/inputs/'
ALPHA=np.fromfile(I+'alpha.bin',dtype=np.uint8).reshape(-1,26); TH=np.fromfile(I+'themed144.bin',dtype=np.uint8).reshape(-1,26)
FAM={'bank':np.fromfile(I+'bank.bin',dtype=np.uint16).reshape(-1,97),'all':np.fromfile(I+'all.bin',dtype=np.uint16).reshape(-1,97)}
CRIB='EASTNORTHEASTBERLINCLOCK'; POS=list(range(21,34))+list(range(63,74))
def inv(a): v=[0]*26; [v.__setitem__(int(a[m]),m) for m in range(26)]; return v
def digits(S,X,Y,form):
    xi,yi=inv(X),inv(Y); out=[]
    for j,i in enumerate(POS):
        x=xi[ord(CRIB[j])-65]; y=yi[ord(K4[S[i]])-65]
        out.append([(y-x)%26,(x-y)%26,(y+x)%26][form])   # Vig c=Y[x+k], variant c=Y[x-k], Beaufort c=Y[k-x]
    return out
def gromark_rows(L,n):  # coefficient vector (mod 10) of k_n over the primer
    rows=[]
    for t in range(n):
        if t<L: v=[0]*L; v[t]=1
        else: v=[(a+b)%10 for a,b in zip(rows[t-L],rows[t-L+1])]
        rows.append(v)
    return rows
GR={L:gromark_rows(L,97) for L in range(2,26)}  # L=1 skipped: recurrence k_n=k_{n-1}+k_n is circular (ambiguity noted)
def solvable_mod(M,b,p):
    M=[[x%p for x in r]+[bb%p] for r,bb in zip(M,b)]; ncol=len(M[0])-1; r=0
    for c in range(ncol):
        piv=next((i for i in range(r,len(M)) if M[i][c]),None)
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; iv=pow(M[r][c],-1,p); M[r]=[(x*iv)%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]: f=M[i][c]; M[i]=[(a-f*bb)%p for a,bb in zip(M[i],M[r])]
        r+=1
    ok=all(any(row[:ncol]) or row[ncol]==0 for row in M)
    return ok, ncol-r
def gromark_ok(idx,d,L):
    M=[GR[L][t] for t in idx]; o2,f2=solvable_mod(M,d,2); 
    if not o2: return False,0
    o5,f5=solvable_mod(M,d,5); return (o5, (2**f2)*(5**f5) if o5 else 0)
def periodic_ok(idx,d,P):
    seen={}
    for t,v in zip(idx,d):
        if seen.setdefault(t%P,v)!=v: return False,0
    return True,10**(P-len(seen))
res={}; detail=[]
for scope in ['direct','bank','all']:
    lines=[l for l in open(f'inputs/k4_{scope}.txt') if l.startswith('S ')]
    mism=0; cnt={}
    for ln in lines:
        kv=dict(re.findall(r'(\w+)=(\S+)',ln)); perm=int(kv['perm']); d=int(kv['dir']); X=int(kv['X']); Y=int(kv['Y']); f=int(kv['form']); bad=int(kv['bad'])
        kC=[int(v) for v in kv['k'].split(',')]
        if perm<0: S=list(range(97)); AX,AY=ALPHA[X],ALPHA[Y]
        else:
            r=[int(v) for v in FAM[scope][perm]]; S=r if d==0 else [r.index(i) for i in range(97)]; AX,AY=TH[X],TH[Y]
        kD=digits(S,AX,AY,f)
        if kD!=kC: mism+=1
        drops=[bad] if bad>=0 else list(range(24))
        nd=sum(v>9 for v in kD)
        hits={}
        for ix in (0,1):
            if perm<0 and ix==1: continue    # direct: S = identity, ix 1 == ix 0
            tix=[POS[j] if ix==0 else S[POS[j]] for j in range(24)]
            for model,rng in (('G',range(2,26)),('P',range(1,26))):
                for L in rng:
                    best=None
                    for dr in drops:
                        keep=[j for j in range(24) if j!=dr]
                        if any(kD[j]>9 for j in keep): continue
                        ok,ns=(gromark_ok if model=='G' else periodic_ok)([tix[j] for j in keep],[kD[j] for j in keep],L)
                        if ok: best=ns if best is None else min(best,ns)
                    if best is not None: hits[(model,L,ix)]=best
        detail.append(dict(scope=scope,line=ln.strip(),rederive_match=kD==kC,consistent={f'{m}{L}/ix{ix}':n for (m,L,ix),n in sorted(hits.items())}))
        for (m,L,ix) in hits: cnt.setdefault((m,L,ix),0); cnt[(m,L,ix)]+=1
        for (m,L) in {(m,L) for (m,L,ix) in hits}: cnt.setdefault((m,L,'any'),0); cnt[(m,L,'any')]+=1
        if any(m=='G' and 22<=L<=25 for (m,L,ix) in hits): cnt.setdefault(('G','22-25','any'),0); cnt[('G','22-25','any')]+=1
        if any(m=='G' and 22<=L<=25 for (m,L,ix) in hits) and any(m=='P' and L==25 for (m,L,ix) in hits): cnt.setdefault(('G22-25&P25','','any'),0); cnt[('G22-25&P25','','any')]+=1
    res[scope]=dict(lines=len(lines),rederive_mismatch=mism,counts={f'{m}{L}/ix{ix}':v for (m,L,ix),v in sorted(cnt.items(),key=str)})
    print(scope,'lines',len(lines),'re-derive mismatches',mism)
    for key in ['G22/ix0','G22/ix1','G22/ixany','G23/ix0','G23/ix1','G23/ixany','G24/ix0','G24/ix1','G24/ixany','G25/ix0','G25/ix1','G25/ixany','G22-25/ixany','P25/ix0','P25/ix1','P25/ixany','G22-25&P25/ixany']:
        print('  ',key,res[scope]['counts'].get(key,0))
    lowG=[k for k in res[scope]['counts'] if k.startswith('G') and k[1:].split('/')[0].isdigit() and int(k[1:].split('/')[0])<=21]
    lowP=[k for k in res[scope]['counts'] if k.startswith('P') and int(k[1:].split('/')[0])<=24]
    print('   any Gromark L<=21 consistent:',lowG,' any periodic P<=24:',lowP)
json.dump(dict(summary=res,lines=detail),open('stage2_recount.json','w'),indent=1)
