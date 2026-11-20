#!/usr/bin/env python3
"""K090 post-hoc diagnostic (disclosed, not a verdict): which cyclic offsets of the matched-group list give a
wrong-partner p_exact < 0.01/3, per pair, on KFG and OKR. Re-executes tools/k090_kfg_k019_cord_level.py unchanged
except that shift_fpr also records each offset's p and its output goes to analysis/k090_posthoc_shift_full.json.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(HERE, 'k090_kfg_k019_cord_level.py')).read()
src = src.replace("'k090_smoke.json' if SMOKE else 'k090_results.json'", "'k090_posthoc_shift_full.json'")
src = src.replace("        ps.append(exact_null(ch, o)[0])\n    return ps", "        ps.append(exact_null(ch, o)[0])\n    LOG.append(dict(k_list=list(range(1, m)), obs_fake=None, p=[float(x) for x in ps]))\n    return ps")
LOG = []; sys.argv = [__file__, 'run']; g = dict(__file__=os.path.join(HERE, 'k090_kfg_k019_cord_level.py'), __name__='__main__', LOG=LOG)
exec(compile(src, 'k090', 'exec'), g)
out = dict(note='post-hoc, descriptive; first 3 entries = OKR pairs, next 3 = KFG pairs (same order as PAIRS)',
           pairs=['KH0097/KH0586', 'KH0192/KH0470', 'KH0192/KH0469'], alpha_pair=0.01 / 3,
           okr=[dict(offsets_below_alpha=[k for k, p in zip(e['k_list'], e['p']) if p < 0.01 / 3], p=e['p']) for e in LOG[:3]],
           kfg=[dict(offsets_below_alpha=[k for k, p in zip(e['k_list'], e['p']) if p < 0.01 / 3], p=e['p']) for e in LOG[3:6]])
json.dump(out, open(os.path.join(HERE, '..', 'analysis', 'k090_posthoc_shift.json'), 'w'), indent=1)
os.remove(os.path.join(HERE, '..', 'analysis', 'k090_posthoc_shift_full.json'))
print(json.dumps(out)[:3000])
