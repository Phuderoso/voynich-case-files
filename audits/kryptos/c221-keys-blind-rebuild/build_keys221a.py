#!/usr/bin/env python3
"""Blind rebuild of keys221a.bin from the prose of PREREG221 (kryptos-case-files 823ed97) only.
Format inferred from keys218.bin (input named by PREREG221): 97 bytes per window, values 0..25, no header.
Variants: see AMBIGUITIES.md.  usage: build_keys221a.py VARIANT OUT"""
import sys
from common import *
k218=open('../tools/cycle218/keys218.bin','rb').read()
K218={k218[i:i+97] for i in range(0,len(k218),97)}
# keys217.bin is not committed at 823ed97 -> cannot drop against it (A4)

def morse_bits(s): return ''.join(MORSE[c].replace('.','0').replace('-','1') for c in s if c in MORSE)
def fam_windows(s, ig_order='b1first', case_outer=False):
    """yield (family, window) for one string in PREREG221 list order IT, IG, MC, MV, MB, EB, EN"""
    codes=ita_bits(s)
    for lsb in (True, False):                                   # IT: b1=LSB table, then bit-reversed
        for w in all_off([b2i(b,lsb) for b in codes]): yield 'IT',w
    bits=list(''.join(b if ig_order=='b1first' else b[::-1] for b in codes))
    for g in (4,8):                                              # IG (chunk B, only for dedup)
        for w in regroup(bits,g): yield 'IG',w
    for w in all_off([len(MORSE[c]) for c in s if c in MORSE]): yield 'MC',w
    for w in all_off([int('1'+MORSE[c].replace('.','0').replace('-','1'),2) for c in s if c in MORSE]): yield 'MV',w
    mb=list(morse_bits(s))
    for g in (4,5,8):
        for w in regroup(mb,g): yield 'MB',w
    up=list(s.encode('cp037')); lo=list(s.lower().encode('cp037'))
    nib=[x for b in up for x in (b>>4,b&15)]
    pairs=[bytes((16*nib[(o+2*t)%len(nib)]+nib[(o+2*t+1)%len(nib)])%26 for t in range(97)) for o in range(len(nib))]
    if not case_outer:
        for w in all_off(up): yield 'EB',w
        for w in all_off(lo): yield 'EB',w
        for w in all_off(nib): yield 'EN',w
        for w in pairs: yield 'EN',w
    else:  # 218-style: upper-case block (EB up, EN) then lower-case EB
        for w in all_off(up): yield 'EB',w
        for w in all_off(nib): yield 'EN',w
        for w in pairs: yield 'EN',w
        for w in all_off(lo): yield 'EB',w

def build(variant):
    ig = 'b5first' if variant=='V2' else 'b1first'
    stream=[]
    if variant=='V4':   # family-major in prose order
        per={}
        for s in S:
            for f,w in fam_windows(s,ig): per.setdefault(f,[]).append(w)
        stream=[(f,w) for f in ('IT','IG','MC','MV','MB','EB','EN') for w in per[f]]
    else:
        stream=[(f,w) for s in S for f,w in fam_windows(s,ig,case_outer=(variant=='V3'))]
    seen=set(K218); out=[]; cnt={}
    for f,w in stream:
        if w in seen: continue
        seen.add(w); cnt[f]=cnt.get(f,0)+1
        if f!='IG': out.append(w)
    return b''.join(out), cnt

if __name__=='__main__':
    v,o=sys.argv[1],sys.argv[2]
    data,cnt=build(v)
    open(o,'wb').write(data)
    print(v, len(data)//97, cnt)
