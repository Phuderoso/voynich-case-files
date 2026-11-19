import json,re,numpy as np
I='../c217-pi/inputs/'; FAM={'bank':np.fromfile(I+'bank.bin',dtype=np.uint16).reshape(-1,97),'all':np.fromfile(I+'all.bin',dtype=np.uint16).reshape(-1,97)}
POS=list(range(21,34))+list(range(63,74))
D=json.load(open('stage2_recount.json'))
for scope in ['direct','bank','all']:
    for name,sel in [('G22-25 (any ix)',lambda k:k.startswith('G') and 22<=int(k[1:].split('/')[0])<=25),('P25 (any ix)',lambda k:k.startswith('P25/'))]:
        lines=0; maps=set()
        for r in D['lines']:
            if r['scope']!=scope or not any(sel(k) for k in r['consistent']): continue
            lines+=1; kv=dict(re.findall(r'(\w+)=(\S+)',r['line'])); p=int(kv['perm']); d=int(kv['dir'])
            if p<0: S=tuple(POS)
            else:
                row=[int(v) for v in FAM[scope][p]]; Sf=row if d==0 else [row.index(i) for i in range(97)]; S=tuple(Sf[i] for i in POS)
            maps.add((S,kv['X'],kv['Y'],kv['form']))
        print(f'{scope:6s} {name:16s} lines {lines:3d}  distinct effective crib maps (S on crib seats, X, Y, form) {len(maps)}')
