# self-test of the stage-2 consistency code on synthetic Gromark / periodic keys (seed 11790)
import random, importlib.util, sys, io, contextlib
src=open('stage2.py').read().split("res={}; detail=[]")[0]
g={}; exec(src,g)
R=random.Random(11790); ok=0; tot=0
for trial in range(200):
    L=R.randrange(2,26); pr=[R.randrange(10) for _ in range(L)]; k=pr[:]
    while len(k)<97: n=len(k); k.append((k[n-L]+k[n-L+1])%10)
    idx=R.sample(range(97),23); d=[k[t] for t in idx]
    a,_=g['gromark_ok'](idx,d,L); tot+=1; ok+=a
    # corrupt one digit: should usually become inconsistent when constraints exceed L
print('Gromark planted consistent: %d/%d'%(ok,tot))
bad=0
for trial in range(200):
    L=R.randrange(2,12); idx=R.sample(range(97),23); d=[R.randrange(10) for _ in idx]
    a,_=g['gromark_ok'](idx,d,L); bad+=a
print('random digits consistent at L 2-11 (expect ~0):',bad,'/200')
ok=0
for trial in range(200):
    P=R.randrange(1,26); per=[R.randrange(10) for _ in range(P)]; idx=R.sample(range(97),23); ok+=g['periodic_ok'](idx,[per[t%P] for t in idx],P)[0]
print('periodic planted consistent: %d/200'%ok)
