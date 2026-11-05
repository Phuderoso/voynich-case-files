# C014 — Expedição 14: The Desert of `s`. Can a vowelless-Latin solver pass its planted test, and does the manuscript then yield more words than meaningless text?

**Status:** pre-registered 2026-11-05 03:35 PT, before any run. Results appended below.
**Approach family:** solver-based decipherment with blind controls (C012 family), repair of C013's failed
vowelless-Latin gate. Not a new family; C015 is due to open one.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
In C013 the vowelless-Latin (abjad-style) solver failed its planted test: the joint 4-gram score prefers
`ss sss ssss` to the true devowelled plaintext, so every decode collapsed to `s` (accuracy 0.14). **With an objective
that penalises a decoded letter-frequency profile far from devowelled Latin, does the solver recover blind planted
vowelless-Latin ciphers (≥ 9/10), and if so, does the manuscript, with herbal pages forced into the sample, yield more
distinct vowelless-Latin dictionary words than meaningless text?**

## Method
- **Solver:** C013's homophonic hill-climber unchanged (each C003 glyph unit → one letter; homophones allowed; word
  spaces kept; 20 restarts × 15,000 single-symbol moves). **New objective**
  `O = S − λ · KL(p_dec ‖ q)`, where S is C013's mean joint 4-gram log10 score, p_dec the decoded letter frequencies
  (spaces excluded), q the letter frequencies of the training text (+0.5 smoothing), KL in log10 units.
- **Language (LV):** Latin with a, e, i, o, u removed (C003 `devowel`, empty words dropped); alphabet = 21 consonant
  letters. Model T = Caesar *De Bello Gallico* (pg218) first half, devowelled; dictionary D = all devowelled word types
  of the whole pg218 (4,042 types), used only for scoring.
- **λ chosen on tuning data only, then frozen:** grid λ ∈ {0, 0.1, 0.3, 1, 3}. Tuning plants = 2 samples × (P1, P2)
  of 1,500 words from Caesar's **second half** (seed 1401). λ = the value with the highest mean tuning accuracy
  (ties → smaller λ). λ = 0 reproduces C013 and is expected to fail (a built-in negative check).
- **Gate (held out, blind):** 5 samples × (P1 one-to-one, P2 homophonic with the 8 most frequent letters split in two)
  of devowelled Descartes, *Meditationes* (pg23306), same seeds as C013. Pass = letter accuracy ≥ 0.80 in ≥ 9 of 10.
  If the gate fails: **not testable**, no verdict.
- **Meaningless nulls (15):** the same 15 texts as C013 (generator default seeds 11–15, C005 matched config seeds
  6011–6015, independent glyph text seeds 510–514), 1,500 words each.
- **Manuscript (5 samples × 1,500 consecutive words, ZL 3b, C003 units, seed 14):** 3 drawn from herbal pages only
  (`$I=H`, 10,903 words) and 2 from the whole text, no overlap. Drawn: herbal f14r–f23r, f52v–f93r (herbal pages
  only), f28r–f37r; whole text f79v–f82r, f105r–f107r.
- **Metric W:** distinct decoded tokens of length ≥ 3 in D. **Bar:** max W over the 15 nulls.
- **Decision:** median manuscript W > bar → provisional, and the script immediately runs a fresh replication set
  (seed 114, 2 herbal + 3 whole-text samples, no word shared with the first set; the herbal text is too short for
  3 more disjoint herbal windows). Reported as "more vowelless-Latin words than meaningless text" only if the
  replication median also beats the bar. Otherwise: "no more vowelless-Latin words than meaningless text under this
  solver".
- **Comparisons:** 1 look. Chance that the median of 5 beats the max of 15 exchangeable nulls = 10/1140 ≈ 0.009.
- **Degeneracy guard (descriptive):** for every run, decoded letter entropy and the share of the most common letter.
- **Compute:** ≤ 8 min on 8 cores (≈ 50 runs); per-run checkpoint `analysis/C014_cache.jsonl` (resumable).
- **Code:** `tools/c014_abjad_solver.py`, committed with this pre-registration (sha256 7a6c51c1…c2f7ee1a).
  Transcription `data/ZL3b-n.txt`, ZL "Version 3b of 13/05/2025", sha256 bf5b6d4a…beccafc.

## Disclosed before the run
A 7-second smoke test (`--smoke`: 300 moves, 1 restart, 2 tuning plants, 2 gate plants, 2 nulls, 1 manuscript
sample) was run only to check the code paths; its output was discarded. With so few moves every decode was
far from converged (accuracy 0.14–0.42), so it carries no information about the outcome. After it, the λ grid was
widened from {0, 0.05, 0.1, 0.2, 0.4} to {0, 0.1, 0.3, 1, 3}, because a back-of-envelope check showed that the
largest old value could not offset the gap between the all-`s` score and the true score (on a 1,500-word Caesar
tuning passage: true −3.73, all-`s` −3.25, a gap of 0.48 log10 units, against an all-`s` KL penalty of 0.83 × λ), and the manuscript sampler was fixed so that samples cannot overlap.

## Limits stated in advance
Letter-level substitution, kept word spaces, left-to-right reading, one abjad-style language, one dictionary. A
frequency penalty helps only if the cipher is a simple substitution; it would mislead for verbose or syllabic codes.
Short consonant skeletons are dense in any string, so the bar is expected to be generous (as Hebrew's was in C013).

## Results (run 2026-11-05, 03:34:57–03:37:39 PT, after the pre-registration commit 250c3775; `tools/c014_abjad_solver.py`, 2 min 42 s on 8 cores; `analysis/C014_results.json`, per-run cache `analysis/C014_cache.jsonl`)

One run, no reruns. Transcription: ZL 3b (`data/ZL3b-n.txt`, "Version 3b of 13/05/2025", sha256 bf5b6d4a…beccafc).

### 1. Tuning (Caesar second half, 4 plants per λ)
| λ | Mean accuracy | Share of the most common decoded letter |
|---|---|---|
| 0 (C013) | 0.145 | 1.00 (all `s`) |
| 0.1 | 0.145 | 1.00 (all `s`) |
| 0.3 | 0.145 | 1.00 (all `s`) |
| 1 | 0.979 | 0.16–0.18 |
| **3 (chosen)** | **1.000** | 0.15–0.16 |

The penalty does what it was built for: from λ = 1 the `sss` collapse is gone, and on held-in-author text the
solver reads every plant correctly. λ = 0 reproduced C013's failure (the built-in negative check).

### 2. Gate (held out: devowelled Descartes, blind, λ = 3 frozen)
| Plant | Accuracies (5 samples) | Passing (≥ 0.80) |
|---|---|---|
| P2 homophonic | 0.833, 0.834, 0.842, 0.842, 0.882 | 5/5 |
| P1 one-to-one | 0.747, 0.749, 0.749, 0.759, 0.764 | 0/5 |
| **Total** | | **5/10 — gate failed (needs 9/10)** |

**Verdict: vowelless Latin is still not testable** under this solver. No verdict on the manuscript.

### Why the gate failed (disclosed)
The collapse is repaired (most common decoded letter 0.18–0.24 in gate runs, not 1.0), but accuracy fell from 1.00
on Caesar to 0.75–0.88 on Descartes. The model and the tuning plants came from the same author; the gate text did not.
A Caesar 4-gram model of a 21-letter consonant skeleton does not know Descartes' vocabulary well enough to tell
some consonants apart once the vowels are gone. The P1 decodes swap whole letters consistently
(for example `h`→`d`, so *hunc* `hnc` becomes `dnc`; and `q`→`s`, `d`→`t`, so *quod* `qd` becomes `st`), giving about 0.75. The P2 decodes split those letters
across two symbols and land just above 0.80. The tuning design overstated held-out performance. A repair must tune
on a different author than the model, and train the model on more than one author. That is a design change and needs
its own pre-registration.

### Descriptive only (not a verdict: the gate failed)
- **Bar from 15 meaningless texts:** W 49–129. Generator default 67–88, matched generator 49–76, independent glyph text
  103–129. Bar = 129. Short consonant skeletons (`snt`, `trm`, `ntr`) are dense in any string, as expected.
- **Manuscript:** herbal f14r–f23r 109, herbal f52v–f93r 95, herbal f28r–f37r 100; whole-text f79v–f82r 82,
  f105r–f107r 87. Median 95, below the bar of 129, and below even the independent-glyph nulls. The herbal samples sit
  a little above the two non-herbal ones (95–109 vs 82–87), still under the bar. Decodes look like
  `prttm nnttm nntm r sctts srtttm`, with long runs of `t`, `r`, `m`.
- **Planted W (gate):** 138–190, well above the bar, even at 75–88 % letter accuracy. A correct reading of a real
  vowelless-Latin text would have cleared the bar, so the bar itself is not out of reach.
- **Degeneracy guard:** decoded letter entropy 2.39–2.99 bits for nulls, 2.55–2.88 for the manuscript, 2.94–3.33 for
  the plants; no run collapsed at λ = 3.

### What this does and does not show
- It shows that C013's `sss` trap is a property of the joint 4-gram objective and that a letter-frequency penalty
  removes it (λ ≥ 1).
- It does not give a verdict on vowelless Latin: the solver still fails its held-out gate (5/10) because of the
  model's domain, not the collapse.
- The herbal pages, sampled for the first time in the solver family, were run, but because the gate failed their
  numbers are descriptive only.
- Comparisons: 1 look, not carried out (gate failed).
- Not tested: vowelless Latin with a multi-author model, other abjad languages, verbose or syllabic ciphers,
  anagrams, right-to-left reading.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
