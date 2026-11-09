"""RR013 line 3b - confirmatory test of RR003's post-hoc lead "free strokes avoid the entry-initial slot" on the one
delimiter-bearing object RR003 never used: Small London, K (Kr + Kv; RR003 dropped K as a copy of Gr).
Definitions exactly RR003 (entry = units strictly between consecutive 380.001* delimiters on one side, lines read in
order, empty stretches dropped), with RR004 audit A's padded codes (free stroke = no [.:;'!?], first component's
leading digits zero-padded to 3 in {001,002,003,004,009}).
S3 = entries whose first unit is a free stroke. One-sided LOWER tail (deficit). Null: shuffle units within each entry.
R 9999, p = (1 + #null <= obs)/(R + 1). Single test, alpha 0.05.
Gates (computed with no observed S3, from the entry sizes and stroke counts, which the null keeps):
  G1 floor: P0(S3 <= 0) <= 0.05 (exact, product over entries of (1 - s_e/n_e));
  G2 power >= 0.80 at f_rep = 1 - 5/9.5 = 0.474 (RR003's observed deficit), 400 plants: in a null replicate each entry
     whose first unit is a stroke has it swapped with a random non-stroke unit of the same entry with probability f;
     grid f in {0.25, 0.474, 0.75, 1.0} reported;
  G3 negative control: 40 null replicates scored as data, <= 5 rejections at 0.05.
Dead-on-arrival rule (Kryptos I-151): if G1 or G2 fails, the observed S3 is NOT computed; verdict NOT TESTABLE.
Modes: --counts (sizes only), --smoke SEED (gates on a registered shuffle of K standing in for the data), --run.
Usage: python3 rr013_entry_initial_K.py corpus.json out.json MODE [SEED]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, math
SIDES = ['Kr', 'Kv']; R = 9999; PL = 400; F_REP = 1 - 5 / 9.5; FGRID = [0.25, F_REP, 0.75, 1.0]

def is_stroke(u):
    if re.search(r"[.:;'!?]", u): return False
    m = re.match(r'(\d{1,3})(?!\d)', u)
    return bool(m) and m.group(1).zfill(3) in ('001', '002', '003', '004', '009')
def is_delim(u): return u.startswith('380.001')
def entries(corpus):
    out = []
    for s in SIDES:
        seq = [u for k in sorted(k for k in corpus if k[:2] == s) for u in corpus[k]]
        idx = [i for i, u in enumerate(seq) if is_delim(u)]
        for a, b in zip(idx, idx[1:]):
            if b - a > 1: out.append(seq[a + 1:b])
    return out
def s3(es): return sum(1 for e in es if is_stroke(e[0]))
def shuf(es, rng):
    o = []
    for e in es:
        v = list(e); rng.shuffle(v); o.append(v)
    return o
def plant(es, f, rng):
    o = []
    for e in es:
        e = list(e)
        if is_stroke(e[0]) and rng.random() < f:
            ns = [t for t, u in enumerate(e) if not is_stroke(u)]
            if ns: t = rng.choice(ns); e[0], e[t] = e[t], e[0]
        o.append(e)
    return o
def plow(obs, null): return (1 + sum(1 for x in null if x <= obs)) / (len(null) + 1)

def gates(es, rng):
    sizes = [(len(e), sum(is_stroke(u) for u in e)) for e in es]
    floor = math.prod(1 - s / n for n, s in sizes)
    null = [s3(shuf(es, rng)) for _ in range(R)]
    pw = {}
    for f in FGRID:
        pw[round(f, 3)] = sum(plow(s3(plant(shuf(es, rng), f, rng)), null) <= 0.05 for _ in range(PL)) / PL
    neg = sum(plow(s3(shuf(es, rng)), null) <= 0.05 for _ in range(40))
    g = dict(entries=len(es), entries_with_stroke=sum(s > 0 for _, s in sizes), units=sum(n for n, _ in sizes),
             strokes=sum(s for _, s in sizes), expected_S3=round(sum(s / n for n, s in sizes), 3),
             floor_p0=floor, G1_floor_ok=floor <= 0.05, power=pw, G2_power_ok=pw[round(F_REP, 3)] >= 0.80,
             negative_rejections_of_40=neg, G3_negative_ok=neg <= 5,
             null_mean=round(sum(null) / R, 3), null_min=min(null), null_max=max(null))
    g['testable'] = g['G1_floor_ok'] and g['G2_power_ok'] and g['G3_negative_ok']
    return g, null

def main(cp, op, mode, seed=None):
    corpus = json.load(open(cp)); es = entries(corpus)
    if mode == '--counts':
        sizes = [(len(e), sum(is_stroke(u) for u in e)) for e in es]
        out = dict(mode=mode, entries=len(es), sizes=sizes, expected_S3=round(sum(s / n for n, s in sizes), 3),
                   floor_p0=math.prod(1 - s / n for n, s in sizes))
    elif mode == '--smoke':
        rng = random.Random(int(seed)); fake = shuf(es, random.Random(int(seed) + 1))
        g, _ = gates(fake, rng); out = dict(mode=mode, seed=int(seed), note='K entries replaced by one within-entry shuffle', gates=g)
    else:
        rng = random.Random(13013); g, null = gates(es, rng); out = dict(mode=mode, seed=13013, R=R, plants=PL, gates=g)
        if not g['testable']:
            out['verdict'] = 'NOT TESTABLE (dead on arrival: observed S3 not computed)'
        else:
            o = s3(es); p = plow(o, null); out.update(S3=o, p_lower=p, verdict='DETECTED' if p <= 0.05 else 'NOT DETECTED')
    json.dump(out, open(op, 'w'), indent=1); print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main(*sys.argv[1:])
