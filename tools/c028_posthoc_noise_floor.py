"""C028 post-hoc (disclosed, NOT pre-registered): the TV a truly binomial sample of K=1000 types reaches by sampling noise
alone, using the binomial fitted to each corpus. Seed 28029. — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import json, random
from c027_word_length_binomial import tv_binom
R = json.load(open('analysis/C028_results.json')); rng = random.Random(28029); out = {}
import sys, os; sys.path.insert(0, 'tools'); import c003_position_rigidity as T
from c027_word_length_binomial import fixed
V = [w for l in T.voynich(fixed('data/ZL3b-n.txt')) for w in l]; L = [len(T.units(w)) for w in set(V)]
_, N = tv_binom(L); p = (sum(L) / len(L) - 1) / N
tvs = sorted(tv_binom([1 + sum(rng.random() < p for _ in range(N)) for _ in range(1000)])[0] for _ in range(500))
out['voynich_fit'] = {'N': N, 'p': p, 'noise_floor_tv_mean': sum(tvs) / 500, 'tv_2.5': tvs[12], 'tv_97.5': tvs[487],
                      'observed_voynich_tv_mean': R['Voynich_ZL3b']['tv_mean']}
print(json.dumps(out, indent=1)); json.dump(out, open('analysis/C028_posthoc_noise_floor.json', 'w'), indent=1)
