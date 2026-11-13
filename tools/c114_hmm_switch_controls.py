#!/usr/bin/env python3
"""C114 (F-HMM step 3, descriptive): is C113's 'stickier than slots' unusual? The C113 statistic and null, unchanged
(SW = posterior-weighted switch rate of the best-of-3 2-state HMM, C111 fit_hmm; null N-SLOT = C109 shuffle_slot, HMM re-fitted),
applied to one 15,000-token half of every control text: 7 voweled natural texts, 5 abjad texts (2 Hebrew + 3 devowelled),
3 generator texts (primary: C083 cell 0 = generator default; sensitivity: feasible cells 33 and 49).
Descriptive by design (Kryptos's review, 13 Nov 2026): with R = NNULL replicates the p floor 1/(R+1) cannot clear any Holm level,
so no per-control p is used; the read-out is the raw difference D = SW - null mean, the null sd (if sd < 1e-3 the null is
degenerate and z is not reported) and the floor line.
Gate G-DIR (the null must be able to register 'stickier'): Latin Descartes half 1 with 20 % of words written in a disjoint copy
alphabet must give D <= -0.05 and SW below all NNULL of its slot replicates; fail -> NOT TESTABLE.
Voynich reference values are C113's (not recomputed): T D = -0.0719; half 1 D = -0.1410; half 2 D = -0.0028.
Pre-registered in case-file/C114-hmm-switch-controls.md. Seed 11776 (main), 11777-11779 generator seeds; next free 11780.
Run: timeout 600 python3 tools/c114_hmm_switch_controls.py   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
import c083_generator_grid as C
from c004_generator_sweep import generate
from c108_sukhotin_alternation import encode, flat, chars, halves, VOWELS
from c109_sukhotin_slot_null import slot_keys, shuffle_slot
from c113_hmm_switch_slot_null import sw_of, hash_name

SEED, NNULL, QPLANT, GLINES = 11776, 10, 0.20, 3400
GEN = [('GEN_cell0_default', 0, 11777), ('GEN_cell33', 33, 11778), ('GEN_cell49', 49, 11779)]
VREF = dict(T=0.1506 - 0.2225, h1=0.0920 - 0.2330, h2=0.2093 - 0.2121)   # C113_results.json + per-half null means from C113_checkpoint.jsonl

def _job(job):
    name, rep, words = job
    ids, wid, inv = encode(words); rng = np.random.default_rng(np.random.SeedSequence([SEED, hash_name(name), rep]))
    if rep > 0: ids = shuffle_slot(ids, slot_keys(words), rng)
    return name, rep, sw_of(ids, wid, len(inv), rng)

def build():
    rng = np.random.default_rng(SEED); nat = B.nat_texts(); texts, cls = {}, {}
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    for k in nat:
        texts[k] = chars(flat(halves(nat[k])[0])); cls[k] = 'voweled' if k in VOWELS else ('abjad' if k.startswith('Hebrew') or k.endswith('_devowel') else 'other')
    w = chars(flat(halves(nat['Latin_Descartes'])[0]))
    texts['PLANT_twoalpha'] = [tuple('#' + u for u in x) if rng.random() < QPLANT else x for x in w]; cls['PLANT_twoalpha'] = 'gate'
    grid = C.grid(); gen = {}
    for name, ci, s in GEN:
        cfg = {'text.lines_to_create': GLINES} if ci == 0 else dict(C.tocfg(grid[ci]), **{'text.lines_to_create': GLINES})
        L = generate(cfg, s); H = halves(L) if L else []
        gen[name] = dict(cell=ci, seed=s, n=sum(map(len, L)) if L else 0, ok=bool(H))
        if H: texts[name] = [tuple(T.units(x)) for x in flat(H[0])]; cls[name] = 'generator'
    return texts, cls, gen

def main():
    from multiprocessing import Pool
    t0 = time.time(); texts, cls, gen = build(); print('built', {k: len(v) for k, v in texts.items()}, gen, round(time.time() - t0, 1), flush=True)
    order = ['PLANT_twoalpha'] + [k for k in texts if k != 'PLANT_twoalpha']
    jobs = [(k, r, texts[k]) for r in range(NNULL + 1) for k in order]
    res = {}; fck = open('analysis/C114_checkpoint.jsonl', 'w')
    with Pool(8) as P:
        for name, rep, (sw, ll, A) in P.imap_unordered(_job, jobs):
            res[(name, rep)] = sw; fck.write(json.dumps([name, rep, sw, ll, A]) + '\n'); fck.flush()
            if rep == 0: print('obs', name, round(sw, 4), A, round(time.time() - t0, 1), flush=True)
    R = dict(seed=SEED, NNULL=NNULL, qplant=QPLANT, glines=GLINES, gen=gen, voynich_ref_C113=VREF, floor=1 / (NNULL + 1), texts={})
    for k in order:
        obs = res[(k, 0)]; Tn = np.array([res[(k, r)] for r in range(1, NNULL + 1)]); sd = float(Tn.std(ddof=1))
        d = dict(cls=cls[k], SW=round(obs, 4), null_mean=round(float(Tn.mean()), 4), null_sd=round(sd, 5), null_min=round(float(Tn.min()), 4),
                 null_max=round(float(Tn.max()), 4), D=round(obs - float(Tn.mean()), 4), rel=round((obs - float(Tn.mean())) / float(Tn.mean()), 3),
                 z=None if sd < 1e-3 else round((obs - float(Tn.mean())) / sd, 1), below_all=bool(obs < Tn.min()), above_all=bool(obs > Tn.max()))
        R['texts'][k] = d; print(k, d, flush=True)
    g = R['texts']['PLANT_twoalpha']; R['gate'] = dict(D=g['D'], below_all=g['below_all'], ok=bool(g['D'] <= -0.05 and g['below_all']))
    ctrl = {k: v for k, v in R['texts'].items() if v['cls'] in ('voweled', 'abjad', 'generator')}
    V = {}
    for ref in ('T', 'h1', 'h2'):
        m = sorted(k for k, v in ctrl.items() if v['D'] <= VREF[ref])
        V[ref] = dict(D_voynich=round(VREF[ref], 4), n_controls_as_sticky=f'{len(m)}/{len(ctrl)}', which=m,
                      by_class={c: sum(ctrl[k]['cls'] == c for k in m) for c in ('voweled', 'abjad', 'generator')})
    V['primary_label'] = 'NOT TESTABLE' if not R['gate']['ok'] else ('UNUSUAL IN PANEL' if not V['T']['which'] else
                         'SHARED WITH ' + '+'.join(c for c, n in V['T']['by_class'].items() if n))
    V['generator_primary_cell0_D'] = ctrl.get('GEN_cell0_default', {}).get('D')
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C114_results.json', 'w'), indent=1, default=float); print(R['gate'], V, R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        texts, cls, gen = build(); print({k: (len(v), cls[k]) for k, v in texts.items()}, gen)
    else: main()
