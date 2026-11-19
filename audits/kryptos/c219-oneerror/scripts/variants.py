# Scoring variants for the K4 p<=18 hits, to bracket ambiguity in "mean log10 quadgram over runs of known letters"
# and in the undetermined class (1-1 split between two crib seats).
import json,re,numpy as np,collections
AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"; KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ"
qg=np.fromfile('/workspace/k4c219/w/qg.bin',dtype=np.float32)
SEAT=list(range(21,34))+list(range(63,74)); CRIB="EASTNORTHEAST"+"BERLINCLOCK"
ct=[l.rstrip('\n').split('\t')[1] for l in open('inputs/texts_mine.tsv') if l.startswith('K4\t')][0]
def q4(s): return qg[((AZ.index(s[0])*26+AZ.index(s[1]))*26+AZ.index(s[2]))*26+AZ.index(s[3])]
def sc(P):
    v=[q4(P[i:i+4]) for i in range(len(P)-3) if '?' not in P[i:i+4]]; return round(float(np.mean(v)),4),len(v)
def run_means(P):
    ms=[sc(m.group())[0] for m in re.finditer(r'[A-Z]{4,}',P)]; return round(float(np.mean(ms)),4),len(ms)
def perm(w,mode,rank):
    order=[0]*w
    for c,r in enumerate(rank): order[r]=c
    rows=-(-97//w); cells=[]
    if mode=='COL': cells=[r*w+order[a] for a in range(w) for r in range(rows) if r*w+order[a]<97]
    else: cells=[r*w+order[a] for r in range(rows) for a in range(w) if r*w+order[a]<97]
    pos=[0]*97
    for q,c in enumerate(cells): pos[c]=q
    inv=[0]*97
    for i in range(97): inv[pos[i]]=i
    return pos,inv
out=[]
for x in json.load(open('out/hits_p_le18.json')):
    if x['text']!='K4': continue
    A=AZ if x['alpha']=='AZ' else KRY; bf=x['form']=='Beaufort'; p=x['p']; mB=x['model']=='B'
    pos,inv=perm(x['w'],x['mode'],x['rank']); S=inv if x['dir'] else pos
    def key_of(s,t):
        a=A.index(ct[S[s]]); b=A.index(CRIB[t]); return (a+b)%26 if bf else (a-b)%26
    cls=collections.defaultdict(list)
    for t,s in enumerate(SEAT): cls[(S[s] if mB else s)%p].append((s,key_of(s,t)))
    def decrypt(key):
        P=''
        for i in range(97):
            r=(S[i] if mB else i)%p
            if r not in key: P+='?'; continue
            a=A.index(ct[S[i]]); P+= A[(key[r]-a)%26] if bf else A[(a-key[r])%26]
        return P
    base={r:collections.Counter(k for _,k in v).most_common(1)[0][0] for r,v in cls.items() if r not in x['ambiguous_classes']}
    P=decrypt(base); assert P==x['plain']
    v={'primary_all4grams_known':sc(P),'mean_of_run_means':run_means(P)}
    Q=list(P)
    for s,c in zip(SEAT,CRIB): Q[s]=c
    v['crib_letters_forced']=sc(''.join(Q))
    for r in x['ambiguous_classes']:
        for s,k in cls[r]:
            kk=dict(base); kk[r]=k; v[f'class{r}_trust_seat{s}']=sc(decrypt(kk)); v[f'class{r}_trust_seat{s}_plain']=decrypt(kk)
    out.append(dict(rank=x['rank'],dir=x['dir'],mode=x['mode'],form=x['form'],model=x['model'],alpha=x['alpha'],variants=v))
print(json.dumps(out,indent=1))
