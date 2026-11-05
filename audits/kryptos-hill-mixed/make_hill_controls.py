import random
from kryptos_text import K4
A="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
pre="THEPATHLEADSTOWARDTHE"; mid="ANDTHENONTOTHESTONEWALLBYTHEO"; post="WHEREAMESSAGEISBURIEDXX"
pt=pre+"EASTNORTHEAST"+mid+"BERLINCLOCK"+post
assert len(pre)==21 and len(mid)==29 and len(pt)==97, (len(pre),len(mid),len(pt))
def unit(d): return d%2==1 and d%13!=0
for n,(seed,off) in enumerate([(1,0),(2,1)],1):
    r=random.Random(seed); perm=list(range(26)); r.shuffle(perm); sig=dict(zip(A,perm)); inv={v:k for k,v in sig.items()}
    while True:
        D=[r.randrange(26) for _ in range(4)]
        if unit(D[0]*D[3]-D[1]*D[2]): break
    # D is the DECRYPTION matrix; encryption E = D^-1
    det=(D[0]*D[3]-D[1]*D[2])%26; di=pow(det,-1,26)
    E=[(D[3]*di)%26,(-D[1]*di)%26,(-D[2]*di)%26,(D[0]*di)%26]
    ct=list(pt)
    for i in range(off,96,2):
        x,y=sig[pt[i]],sig[pt[i+1]]
        ct[i]=inv[(E[0]*x+E[1]*y)%26]; ct[i+1]=inv[(E[2]*x+E[3]*y)%26]
    ct="".join(ct); open(f"hctl_{n}.txt","w").write(ct)
    print(f"control {n}: offset={off} D={D} sigma={''.join(f'{L}{sig[L]} ' for L in A)}\n  ct={ct}")
for n in (1,2,3):
    r=random.Random(100+n); l=list(K4); r.shuffle(l); open(f"hnull_{n}.txt","w").write("".join(l))
