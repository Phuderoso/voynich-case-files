#!/usr/bin/env python3
"""replica_c232.py -- ADAPTER (declared in PREREG_REPLICA_c232.md before running) that runs the UNCHANGED i342_subsample.py
(sha256 5185d776f4ce4e60a79bdd337323b908c70367428ce44c94b10c6c2382b348ad, verified before import) on Kryptos's fresh c232 nulls.
Why an adapter: the tool hard-codes 16 nulls (assert), the c229 half-sets and the c229 seeds. The c232 Y-line format, the 8 file types,
the SHA256SUMS layout (./R/...) are identical, so nothing in the estimators, draws, bootstrap, Holm, distance or label code is touched.
The adapter only (1) restricts load() to one 16-null replica set, (2) sets HALF_A / HALF_B to its first / last 8 seeds, (3) sets new seeds.
usage: replica_c232.py {gates|real} SET RDIR OUTDIR [--i-froze-prereg]      SET in {RA, RB}"""
import sys, os, hashlib, json, time, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); TOOL = os.path.join(HERE, 'i342_subsample.py')
SHA = '5185d776f4ce4e60a79bdd337323b908c70367428ce44c94b10c6c2382b348ad'
assert hashlib.sha256(open(TOOL, 'rb').read()).hexdigest() == SHA, 'tool changed'
spec = importlib.util.spec_from_file_location('i342_subsample', TOOL); T = importlib.util.module_from_spec(spec)
sys.modules['i342_subsample'] = T; spec.loader.exec_module(T)
SETS = dict(RA=list(range(209609, 209625)), RB=list(range(209625, 209641)))
SEEDS = dict(RA=dict(primary=11861, fresh=11862, halfA=11863, halfB=11864, gate_P0=11869, gate_P1=11870, gate_THIN=11871),
             RB=dict(primary=11865, fresh=11866, halfA=11867, halfB=11868, gate_P0=11872, gate_P1=11873, gate_THIN=11874))
mode, S, rdir, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
nulls = SETS[S]; T.HALF_A, T.HALF_B = nulls[:8], nulls[8:]; T.SEEDS = SEEDS[S]
_load = T.load
def load_set(rd, with_nc):
    C = _load(rd, with_nc); import numpy as np
    return T.sub(C, np.flatnonzero(np.isin(C['seed'], nulls)))
T.load = load_set
os.makedirs(out, exist_ok=True)
if __name__ == '__main__':
    print(f'[adapter] set {S} nulls {nulls[0]}-{nulls[-1]} seeds {T.SEEDS} tool sha {SHA[:8]}', flush=True)
    if mode == 'gates':
        t0 = time.time(); res = T.run_gates(rdir, 200, 8); ok, L = T.summarize_gates(res)
        open(out + '/gates_output.txt', 'w').write('\n'.join(L) + f'\n(set {S}, elapsed {time.time()-t0:.0f}s, tool sha256 {SHA}, adapter sha256 '
                                                   f'{hashlib.sha256(open(__file__, "rb").read()).hexdigest()})\n')
    else:
        if '--i-froze-prereg' not in sys.argv: sys.exit('refusing: real mode needs --i-froze-prereg')
        print(json.dumps(T.run_real(rdir, out, 8, False)['tests'], indent=1, default=float))
