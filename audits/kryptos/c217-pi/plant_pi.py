"""Gate P analogue (own plants, seed 11789): 20 plants on pi windows, 8 direct / 6 bank / 6 all.bin.
Random window, form, X, Y, ix, row, dir; K1-K3 English 97-letter window with cribs; odd ids: one carved crib letter replaced.
Tool run on Y-slice (Y mod 1000 = planted Y mod 1000) for direct, row-slice (row mod 2000) for families.
Pass: a hit at the planted (row,dir,ix,X,Y,form,window) whose decrypt differs from the planted plaintext in <=1 letter."""
import random, numpy as np, subprocess, json
R=random.Random(11789)
A=np.fromfile('inputs/alpha.bin',dtype=np.uint8).reshape(-1,26); T=np.fromfile('inputs/themed144.bin',dtype=np.uint8).reshape(-1,26)
B={'bank':np.fromfile('inputs/bank.bin',dtype=np.uint16).reshape(-1,97),'all':np.fromfile('inputs/all.bin',dtype=np.uint16).reshape(-1,97)}
W=np.fromfile('pi_windows.bin',dtype=np.uint8).reshape(-1,97)
eng=''.join(c for c in open('inputs/k123_eng.txt').read().upper() if c.isalpha())
SIG=[1,1,-1];TAU=[1,-1,1]
CR=[(21,'EASTNORTHEAST'),(63,'BERLINCLOCK')]
def inv(a): v=[0]*26; [v.__setitem__(int(a[m]),m) for m in range(26)]; return v
def enc(pt,X,Y,f,k,S,ix):
    xi=inv(X); ct=[None]*97
    for i,p in enumerate(pt):
        t=i if ix==0 else S[i]; y=(SIG[f]*xi[ord(p)-65]+TAU[f]*int(k[t]))%26; ct[S[i]]=chr(65+int(Y[y]))
    return ''.join(ct)
def dec(ct,X,Y,f,k,S,ix):
    yi=inv(Y); out=[]
    for i in range(97):
        t=i if ix==0 else S[i]; y=yi[ord(ct[S[i]])-65]; x=(SIG[f]*(y-TAU[f]*int(k[t])))%26; out.append(chr(65+int(X[x])))
    return ''.join(out)
res=[]; npass=0
for pid in range(20):
    mode='direct' if pid<8 else ('bank' if pid<14 else 'all')
    w=R.randrange(len(W)); f=R.randrange(3); ix=R.randrange(2); d=R.randrange(2)
    if mode=='direct': AL=A; S=list(range(97)); row=-1; ix_rep=0; d=0
    else:
        AL=T; row=R.randrange(len(B[mode])); r=[int(v) for v in B[mode][row]]
        S=r if d==0 else [r.index(i) for i in range(97)]
    x=R.randrange(len(AL)); y=R.randrange(len(AL))
    st=R.randrange(len(eng)-97); pt=list(eng[st:st+97])
    for o,s in CR: pt[o:o+len(s)]=list(s)
    pt=''.join(pt); ct=list(enc(pt,AL[x],AL[y],f,W[w],S,ix))
    corrupt=None
    if pid%2==1:
        seat=R.randrange(24); i=21+seat if seat<13 else 63+seat-13; q=S[i]
        ct[q]=R.choice([c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c!=ct[q]]); corrupt=seat+1
    ct=''.join(ct)
    if mode=='direct': cmd=['./pi217x','direct',ct,'inputs/alpha.bin','pi_windows.bin','1000',str(y%1000)]
    else: cmd=['./pi217x','fam',ct,'inputs/themed144.bin',f'inputs/{mode}.bin','pi_windows.bin','2000',str(row%2000)]
    out=subprocess.run(cmd,capture_output=True,text=True).stdout.split('\n')
    hits=[l.split() for l in out if l.startswith('H ')]
    ok=False
    for h in hits:
        hr,hd,hix,hx,hy,hf,hw=map(int,h[2:9])
        if (hr,hx,hy,hf,hw)==(row,x,y,f,w) and (mode=='direct' or (hd,hix)==(d,ix)):
            dd=dec(ct,AL[x],AL[y],f,W[w],S,0 if mode=='direct' else ix); nd=sum(a!=b for a,b in zip(dd,pt))
            if nd<=1: ok=True
    npass+=ok
    res.append(dict(pid=pid,mode=mode,row=row,dir=d,ix=ix,X=x,Y=y,form=f,wid=w,corrupt_seat=corrupt,hits_in_slice=len(hits),pass_=ok))
    print(res[-1],flush=True)
print('GATE P (own plants, seed 11789): %d/20 pass (bar >= 19/20)'%npass)
json.dump(res,open('plants_pi.json','w'),indent=1)
