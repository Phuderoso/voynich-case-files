"""LA003 - feasibility gates for KI-RO deficit arithmetic (line A) and a second numeral reading (line B).
No randomness. Usage: python3 la003_feasibility.py ins.json corpus.json out.json
ins.json = lineara.xyz 9c81beb (Node-converted, see LA001); corpus.json = Navarre-AI/linear-a e4cb48b.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, math
from fractions import Fraction as Fr
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from la002_disjoint_replication import VAL, SENS, ERASED
WORD = re.compile(r'^[A-Z*][A-Z0-9*₂₃+\-]*')
DIG = re.compile(r'^\d+$')
SEPS = {'𐄁', '—', ERASED}
DAMAGE = set('[]?')

def lines(ws):
    cur = []
    for t in ws:
        if t == '\n': yield cur; cur = []
        else: cur.append(t)
    yield cur

def value(tokens):
    """Sum of numerals in a token run; returns (value, unreadable list)."""
    v = Fr(0); bad = []
    for t in tokens:
        if DIG.match(t): v += int(t)
        elif t in VAL: v += VAL[t]
        elif t in SENS: v += SENS[t]; bad.append('uncertain:' + t)
        elif t in SEPS or WORD.match(t): pass
        else: bad.append(t)
    return v, bad

def main(ins_p, cor_p, out_p):
    ins = json.load(open(ins_p)); cor = json.load(open(cor_p))
    sides = []
    for k in sorted(ins):
        ws = ins[k].get('transliteratedWords') or []
        if 'KI-RO' not in ws: continue
        has_kuro = 'KU-RO' in ws
        kiro = []
        for ln in lines(ws):
            if 'KI-RO' not in ln: continue
            i = ln.index('KI-RO'); tail = ln[i + 1:]
            nums = [t for t in tail if DIG.match(t) or t in VAL or t in SENS]
            v, bad = value(tail)
            dmg = any(c in t for t in ln for c in DAMAGE)
            kiro.append(dict(tail=tail, numeric=bool(nums), value=str(v), unreadable=bad, damage=dmg))
        kuro_dmg = any(any(c in t for t in ln for c in DAMAGE) for ln in lines(ws) if 'KU-RO' in ln)
        usable = has_kuro and not kuro_dmg and any(x['numeric'] and not x['damage'] and not x['unreadable'] for x in kiro)
        sides.append(dict(doc=k, has_kuro=has_kuro, kuro_damage=kuro_dmg, kiro=kiro,
                          usage='numeric' if any(x['numeric'] for x in kiro) else 'header/no numeral', usable=usable))
    n = sum(s['usable'] for s in sides)
    floor = 1 / math.factorial(n) if n else 1.0
    gateA = dict(n_usable=n, usable=[s['doc'] for s in sides if s['usable']], floor_best_case=floor,
                 pass_n=n >= 4, verdict='run power curve' if n >= 4 else 'NOT TESTABLE')
    # Line B: provenance of numerals in Navarre-AI records
    B = {}
    roles = sorted({s['role'] for r in cor.values() for s in r.get('signs', [])})
    for sid in ['HT 39', 'HT 122a']:
        r = cor.get(sid, {})
        nums = [hex(ord(c)) for c in r.get('unicode_text', '') if 0x10107 <= ord(c) <= 0x10133]
        B[sid] = dict(sources=r.get('sources'), sign_roles_present=sorted({s['role'] for s in r.get('signs', [])}),
                      numerals_in_unicode_text=len(nums), numeral_sign_entries=sum(1 for s in r.get('signs', []) if s['role'] == 'numeral'),
                      words=r.get('words'), word_source=r.get('word_source'))
    indep = any(v['numeral_sign_entries'] for v in B.values())
    gateB = dict(corpus_sign_roles=roles, independent_numerals=indep,
                 verdict='compare readings' if indep else 'NOT TESTABLE (numerals only via lineara.xyz unicode_text)')
    out = dict(gateA=gateA, sides=sides, gateB=gateB, lineB=B)
    print('GATE A', json.dumps(gateA)); print('GATE B', json.dumps(gateB))
    json.dump(out, open(out_p, 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main(*sys.argv[1:4])
