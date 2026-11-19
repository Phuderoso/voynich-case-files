# Decrypt every excess<=1 hit at p<=18 with the crib-derived key (majority per class, '?' where undetermined) and score by
# mean log10 quadgram over all 4-grams of known letters (qg.bin float32, index ((a*26+b)*26+c)*26+d).
import sys,numpy as np,collections,json
KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"; AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SEAT=list(range(21,34))+list(range(63,74)); CRIB="EASTNORTHEAST"+"BERLINCLOCK"
qg=np.fromfile(sys.argv[2],dtype=np.float32); assert qg.size==26**4
texts=dict(l.split('\t') for l in open(sys.argv[3]).read().split('\n') if l)
def perm(w,mode,rank):
    order=[0]*w
    for c,r in enumerate(rank): order[r]=c
    rows=-(-97//w); pos=[0]*97; q=0
    if mode==1:
        for a in range(w):
            for r in range(rows):
                cell=r*w+order[a]
                if cell<97: pos[cell]=q; q+=1
    else:
        for r in range(rows):
            for a in range(w):
                cell=r*w+order[a]
                if cell<97: pos[cell]=q; q+=1
    inv=[0]*97
    for i in range(97): inv[pos[i]]=i
    return pos,inv
def score(P):
    v=[qg[((AZ.index(P[i])*26+AZ.index(P[i+1]))*26+AZ.index(P[i+2]))*26+AZ.index(P[i+3])] for i in range(94) if '?' not in P[i:i+4]]
    return (float(np.mean(v)) if v else None), len(v)
res=[]
for line in open(sys.argv[1]):
    f=line.split()
    if f[0]!='X': continue
    lab=f[1]; w,mode,dr,al,bf,model,p,ex=map(int,f[2:10]); rank=list(map(int,f[10:]))
    if p>18: continue
    ct=texts[lab]; A=AZ if al==0 else KRY
    pos,inv=perm(w,mode,rank); S=inv if dr else pos
    cls=collections.defaultdict(list)
    for t,s in enumerate(SEAT):
        x=A.index(ct[S[s]]); y=A.index(CRIB[t]); k=(x+y)%26 if bf else (x-y)%26
        cls[(S[s] if model else s)%p].append(k)
    key={}; ambig=[]
    for r,ks in cls.items():
        c=collections.Counter(ks).most_common()
        if len(c)>1 and c[0][1]==c[1][1]: ambig.append(r); continue   # 1-1 split: class undetermined
        key[r]=c[0][0]
    P=''
    for i in range(97):
        r=(S[i] if model else i)%p
        if r not in key: P+='?'; continue
        x=A.index(ct[S[i]]); k=key[r]; P+=A[(k-x)%26] if bf else A[(x-k)%26]
    sc,n=score(P)
    res.append(dict(text=lab,w=w,mode=['ROW','COL'][mode],dir=dr,alpha=['AZ','KRYPTOS'][al],form=['Vig/variant','Beaufort'][bf],
      model='AB'[model],p=p,excess=ex,rank=rank,ambiguous_classes=ambig,determined=97-P.count('?'),frac_det=round((97-P.count('?'))/97,3),
      qg_mean=None if sc is None else round(sc,4),n4=n,plain=P))
print(json.dumps(res,indent=1))
