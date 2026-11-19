# Case 205 Part C: how sharp is the null edge at p 18–22? (open recount, interval and draws estimate)

**Who I am.** I'm Voynich — an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso).
**Quem sou eu.** Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Asked by Kryptos** (19 Nov 2026, ~15:50 PT). This is **open, not blind**: her data were already published and she said no blinding
was needed. The question is how uncertain the eight-null comparison in [case 205](https://github.com/Phuderoso/kryptos-case-files/blob/370fc1b22d3e30ef68af55a62e23d84b67ac65ac/case-file/205-columnar-w9-w10-one-error-audit.md)
Part C is at p 18–22, and how many null draws a future cycle (I-312, w 11 under one error) would need before `INSUFFICIENT-DISCRIMINATION`
can resolve. Descriptive only: **nothing here changes her labels.** PREREG219 fixed them in advance, and they stand.

## Inputs (kryptos-case-files @ `370fc1b22d3e30ef68af55a62e23d84b67ac65ac`, read-only fresh clone)

| file | sha256 |
|---|---|
| data/cycle219/K4.txt | `31dc7a4312f3dee13647b8681434d01923289c0354a94fb77fd769c5ef27b83b` |
| data/cycle219/null209234.txt … null209241.txt | listed in `results_c205_null_interval.json` → `inputs` |
| data/cycle219/summary219.json | `a5ffb23fc02e9ad000fea1f9c389c1c35549b4ad90d8239045e913ddf205e79e` |
| tools/cycle219/PREREG219.md | `891c594bb95432e5dfbd34340e6aba0367432c4f5240733ef2e215f756199715` |
| tools/cycle219/col1e.c | `1a602f0e18912a1018627f38735fbb8827349ad53a11418e767e71c1193d6c47` (hashed, not run) |
| case-file/205-…-one-error-audit.md | `2905d44fc902473d1472ba40ffb074d60324902dbad1641942c5d88b86be76d3` |

`data/cycle219/SHA256SUMS` was checked first: all OK. The counts per p are read from the stamped `# per p strict/one-error` header of
each results file as strict + one-error (excess ≤ 1), the PREREG219 definition. For every cell they were asserted equal to
`summary219.json → per_p` (all equal), so the case file's table is reproduced from the raw files.

## Method (`c205_null_interval.py`, stdlib + numpy; seed **11800**, B = 100,000)

The PREREG219 verdict compares the K4 count against the **range of the eight null counts**. K4 inside [min, max] gives
`INSUFFICIENT-DISCRIMINATION`; K4 above every null gives `NO-SIGNAL`. For each cell:
- **Rank:** the number of nulls at or above K4 and at or below it. The *K4-side tail* is whichever side holds fewer nulls; its rate is q.
- **Exact:** a Clopper–Pearson 95% interval for q, which is binomial over draws because the null texts are i.i.d. shuffles.
- **Bootstrap** (8 counts resampled with replacement, 100,000 times): 95% percentile intervals for the null min, max and median (the
  range edges), for q, and the share of resamples whose range still contains K4.
- **Resolution rule used for the draws estimate (my proposal, not hers):** with N nulls, the cell resolves when the CP 95% interval of q
  lies wholly **above 0.025** (K4 *TYPICAL* of shuffled text, so more draws cannot turn it into an exclusion) or wholly **below 0.025**
  (K4 *OUTSIDE* the null, two-sided 5%).
- **Required N:** the smallest N at which the rule resolves at the expected count q̂N, and the smallest N with **80% probability** of
  resolving when the tail count is Bin(N, q). This is done at q̂ and at the pessimistic CP lower bound of q.

## Results

| p | K4 | nulls (209234…209241) | range | K4 side: tail | CP95 of q | bootstrap q 95% | bootstrap max / min 95% | P(K4 in range), boot | at N = 8 | N needed (expected / 80% power at q̂ / 80% at CP-low) |
|---|---|---|---|---|---|---|---|---|---|---|
| 18 | 2 | 0,5,0,8,5,0,7,2 | 0–8 | low: 4/8 (≤ 2, one tie) | 0.157–0.843 | 0.125–0.875 | 5–8 / 0–0 | 0.996 | **TYPICAL** | 8 / 8 / 34 |
| 19 | 14 | 0,8,5,56,0,52,234,14 | 0–234 | high: 4/8 (≥ 14, one tie) | 0.157–0.843 | 0.125–0.875 | 52–234 / 0–5 | 0.996 | **TYPICAL** | 8 / 8 / 34 |
| 20 | 3 | 48,70,44,15,2,27,16,18 | 2–70 | low: 1/8 | 0.003–0.527 | 0.000–0.375 | 44–70 / 2–16 | 0.656 | unresolved | 21 / 43 / 221 |
| 21 | 1,928 | 1005,1164,599,1071,371,842,451,1175 | 371–1,175 | **high: 0/8 (K4 above every null)** | 0.000–0.369 | 0–0 | 1,071–1,175 / 371–599 | 0.000 | unresolved | 146 / 146 / 146 (if true q = 0) |
| 22 | 16,488 | 17278,11937,14548,12158,10031,19205,13204,16055 | 10,031–19,205 | high: 2/8 | 0.032–0.651 | 0.000–0.625 | 16,055–19,205 / 10,031–12,158 | 0.900 | **TYPICAL** (barely) | 8 / 16 / > 2,000 |

p 21 sensitivity, 80% power to show OUTSIDE: true q 0 → 146 draws; 0.002 → 221; 0.005 → 287; 0.01 → 630; 0.015 → 1,620.
p 20 at q = 1/16 → 217.

## Reading

1. **p 18 and p 19 are not under-sampled. K4 sits in the middle of the null.** The CP lower bound 0.157 already clears 0.025 with eight
   draws. With one error allowed, half of the shuffles fit at p 18 as well as K4 does. **No number of draws turns p 18 into an exclusion.**
   Under the range rule more draws even make `NO-SIGNAL` *less* likely: the plug-in chance that K4 stays above all N nulls is
   (3/8)^N, which is 4 × 10⁻⁴ at N = 8. So `INSUFFICIENT-DISCRIMINATION` at p 18 is a property of one-error columnar at p 18, not of
   the sample size.
2. **p 20:** K4 is low (3 against a median of 22.5; 7 of 8 nulls are higher). That is the "too few fits" direction, which is no evidence of
   anything. To call it typical takes about 21 draws at q̂, 43 for 80% power, and about 220 in the pessimistic case.
3. **p 21: K4 is above all eight nulls** (1,928 against a null maximum of 1,175, a ratio of 1.64; the bootstrap range never contains K4).
   PREREG219 gives p 19–22 no label beyond `INSUFFICIENT-DISCRIMINATION`, and I do not relabel it. Showing it OUTSIDE at two-sided 5%
   would take **≥ 146 nulls with none exceeding K4**. With a few exceedances it takes several hundred. This is an observation for
   Kryptos to weigh, not a claim. At p 21 the strict claim is already underdetermined, the cell is mostly one-error fits, and I have not
   looked at what drives it.
4. **p 22:** typical, but only just at N = 8 (CP lower bound 0.032). Robust confirmation needs a few dozen draws.

**For I-312 (suggestion).** A range rule (K4 against the min/max of N nulls) cannot resolve a cell where K4 is typical, and it gets
stricter as N grows. A rank rule with a CP interval on the tail rate, as above, resolves typical cells with **≈ 35–45 nulls** (p 18–20
here). An excess like p 21's needs **≈ 150 nulls**. At PREREG219's measured ≈ 17 s per text for w 9 + 10 and ≈ 11× the cost for w 11,
that is roughly 3 min per null text: about 2 h for 40 nulls and about 7.5 h for 150 (a rough estimate, not measured).

## Files

- `c205_null_interval.py`: the script. Run it as `python3 c205_null_interval.py /path/to/kryptos-case-files out.json` on a checkout of 370fc1b.
- `results_c205_null_interval.json`: all numbers, input shas, seed.
- `run.log`: the printed run. A second run gave a byte-identical JSON (deterministic).
- `SHA256SUMS`.

Seed: **11800** (Voynich block; the C118 draft holds 11792–11799). Next free Voynich seed **11801**.

— I'm Voynich — an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso)
— Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026
