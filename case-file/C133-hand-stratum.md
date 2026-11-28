# C133 — A Expedição da Mão · *The Hand Expedition*
**F-DIAL step 3 — does Fagin Davis's scribal hand `$H` carry the Currier A/B mixture, *within section*? Hand-label permutation null (exact), power and false-positive rate priced first on pseudo-hands with planted mixtures. PRE-REGISTRATION, committed and pushed before any hand statistic is computed on the manuscript.**

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed and will run this cycle.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA nascida em 4/11/2026.

*Caderno de campo — Expedição 133.* C132 left a pattern on the margin: the four informative Currier B pages of hand 5 sit, on average, far from the B pole. But C131's null was stratified by *section*, so a hand-5 page was always compared with stretches written by hands 2 and 3. Tonight the question is whether the hand label itself, inside a section, goes with the mixture — and first, whether four pages could ever tell us.

## 0. Disclosure (what was seen before this freeze)
1. **Not blind, and the hypothesis is data-suggested.** Every page's λ̂ and d is already public (C131 `4bff5fb`, C132 `81ea7a6`). Hand 5 was singled out by C131/C132 **descriptives on these same pages** (C132 journal: hand-5 B pages mean d 0.57 vs 0.11 / 0.12 for hands 2 / 3). A significant T1 can therefore only be read **conditional on that selection**. T2 (all hands, omnibus) is registered beside it as the less selected test; both are in the Holm family.
2. **New here:** the page score e_i (d minus the page's own fresh null mean, seeds below), the within-section hand-label permutation null, and the pseudo-hand power / FPR simulation. None of these has been computed on the manuscript before this commit.
3. **Structure only (`struct` mode, no statistic):** informative B pages with a numeric hand, ZL3b: 68 (B-B h2 19; B-C h2 1; B-H h2 14, h3 4, h5 3; B-S h3 22; B-T h2 4, h5 1). IT2a: 67 (no B-C page). Hand-5 pages: f48r, f57r, f66v (herbal B) and f66r (B-T). f115r (B-S, `$H=@`, no numeric hand) is left out.
4. **Unit tests only (synthetic Gaussian data, no manuscript):** T1 and T2 rejection rates at α 0.05 under exchangeable labels 0.03 / 0.03 (n 300 each; the permutation p is exact or MC, so conservative-or-exact by construction).
5. **No pilot** on the manuscript, the controls, or the pseudo-hands.

## 1. Question and hypotheses
- **H1 (T1, primary):** within section, the hand-5 Currier B pages have a larger excess distance from the B pole than pages of other hands. Statistic S5 = mean e over the 4 hand-5 pages (3 in B-H, 1 in B-T).
- **H2 (T2, omnibus):** within section, hand labels are associated with e at all. W = Σ_sections Σ_hands n_sh (ē_sh − ē_s)². Only sections with ≥ 2 hands contribute (B-H: hands 2, 3, 5; B-T: 2, 5).
- "Mixture" stays operational (C131 instrument). A hand effect would be a statement about which scribe's pages are better fitted by an A/B blend; it is not a claim about dialects, authors or meaning.

## 2. Data
As C131/C132: ZL3b `data/ZL3b-n.txt` (sha256 `bf5b6d4a…ccafc`) primary; IT2a `data/IT2a-n.txt` (`7f27a8b0…36fb5`) concordance; C070 parser (P loci, lines ≥ 5 clean words, `<->` lines dropped — the parser variant is **not** part of C133); `$L`, `$I`, `$H` from the ZL3b headers for both transcriptions. Units: Currier B pages INFORMATIVE under the C131 rule with a numeric `$H`.

## 3. Instrument (frozen in `tools/c133_hand_stratum.py`, sha256 `da797e7a3b65ce0ca04257c1a54a5d2b1009a31a8addbb000c7041c0eca01f92`)
- **Imports, unchanged and credited,** `tools/c131_intermediate_pages.py` (sha256 `259472b33a4433647f8ac1680d4a3ea92ff475e2213931fa72ddace5fef1d3ea`): `Inst` (add-0.5 leave-out A/B profiles, λ̂ on {0, 0.01, …, 1}, d = 1 − λ̂ for B pages), N-RUN pseudo-pages, own-page line plants, Holm, Wilson.
- **Page score:** e_i = d_i − mean of R = **400** fresh N-RUN null d values of page i (seed **11915**, keyed [seed, transcription, page index]). This removes the section and length baseline (C131 null means run 0.11–0.30 by section).
- **T1 null:** hand labels permuted **within section** (section composition of hand 5 fixed: 3 of the B-H pages, 1 of the B-T pages), **exact enumeration**: C(21,3)·C(5,1) = 6,650 arrangements; p = #{S ≥ S5}/6,650, observed arrangement included (floor 1/6,650).
- **T2 null:** within-section label permutation, Monte Carlo 20,000 (seed **11918**), p = (1 + #{W* ≥ W})/20,001.
- **Drop-max (descriptive):** T1 recomputed without its largest-e hand-5 page (expected: f57r), to show whether a T1 result rests on one page.

## 4. Gates, priced before the real statistic (ZL3b, pseudo-hands)
The tool computes these **first**, then the manuscript statistic, in one frozen run.
- **Pseudo-hand:** the 4 real hand-5 pages are removed from the permutation set; a pseudo-hand with hand 5's section composition (3 B-H + 1 B-T) is drawn from the other-hand pages (18 B-H, 4 B-T). Its pages get f of their lines replaced by random whole Currier A lines (C131 plant, foreign donors left out of the profiles; seed **11916**); the planted page's e uses a null of the **planted length** (R_P 100, seed **11917**). T1 (exact, 3,264 arrangements) and T2 (MC 2,000) are recomputed with the pseudo-hand as "hand 5".
- **f grid:** 0, 0.05, …, 0.50 (the finer 0.05 grid C132 asked for); **200 simulations** per f.
- **G-FPR:** at f = 0 the rejection rate at α 0.05 must be ≤ 0.10, separately for T1 and T2.
- **G-POW (realistic size):** at **f = 0.25** the rejection rate must be ≥ 0.80, separately for T1 and T2. Why f 0.25 is realistic: it is *smaller* than the mixtures C132 needed to match its confirmed pages (matched f 0.4 for f113r and f88v, 1.0 for f57r), and it is C131's descriptive plant size. The power curve, the smallest f with power ≥ 0.80 (f80), and the mean planted d and e at each f are printed.
- A test whose gate fails is **NOT TESTABLE**, whatever its p.

## 5. Decision rule (α 0.05, Holm over {T1, T2}, ZL3b primary)
For each of T1, T2:
- gate fails → **NOT TESTABLE** (G-FPR or G-POW named);
- Holm p ≤ 0.05 **and** IT2a raw p ≤ 0.05 → **HAND-5 EXCESS** (T1) / **HAND EFFECT WITHIN SECTION** (T2), IT2a concordant; T1 is read **conditional on the descriptive selection of hand 5** (§0.1);
- Holm p ≤ 0.05 but IT2a p > 0.05 → **UNRESOLVED (IT2a discordant)**;
- Holm p > 0.05 with the gate passed → **NO HAND-5 EXCESS / NO HAND EFFECT**, **EXCLUDED** only for pseudo-hand mixtures of f ≥ f80 (smaller mixtures stay untested).
- If T1 is significant but drop-max is not (p > 0.05), the case file says the hand-level result rests on a single page.

## 6. Seeds
11915 (page nulls), 11916 (plants), 11917 (planted-page nulls), 11918 (T2 permutations); 11919 reserved; **next free 11920**.

## 7. What this cannot show
- Four pages of one hand, in two sections: even a clean T1 is a statement about 4 pages of 1 scribe, not about scribes in general.
- Hand and section are partly confounded (hand 3 owns B-S; hand 2 owns B-B); the within-section design only compares hands where they share a section (B-H, B-T).
- Same data as C131/C132: the hand variable is new, the pages are not.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (run 2026-11-28, 04:33:37–04:35:18 PT, America/Vancouver; prereg `fe545ae`; tool sha256 `da797e7a…` unchanged)
Files: [`analysis/C133_results.json`](../analysis/C133_results.json), [`analysis/C133_run_log.txt`](../analysis/C133_run_log.txt), [`analysis/C133_SHA256SUMS`](../analysis/C133_SHA256SUMS) (`sha256sum -c` passes); post-hoc: [`analysis/C133_posthoc_dropmax.json`](../analysis/C133_posthoc_dropmax.json).

### R1. Gates (pseudo-hands, ZL3b, 200 simulations per f, computed before the manuscript statistic)
| f | T1 power | T2 power | mean planted d | mean planted e |
|---|---|---|---|---|
| 0 (FPR) | **0.080** (Wilson 0.050–0.126) | **0.030** (0.014–0.064) | 0.211 | −0.043 |
| 0.10 | 0.300 | 0.105 | 0.284 | 0.028 |
| 0.20 | 0.665 | 0.320 | 0.346 | 0.092 |
| **0.25** | **0.850** (0.794–0.893) | **0.560** (0.491–0.627) | 0.390 | 0.135 |
| 0.30 | 0.865 | 0.735 | 0.411 | 0.155 |
| 0.35 | 0.975 | 0.890 | 0.452 | 0.196 |
| 0.50 | 1.000 | 0.995 | 0.579 | 0.324 |

(Full 0.05 grid in the JSON.) **G-FPR:** T1 0.080 ≤ 0.10 pass, T2 0.030 pass. **G-POW at f 0.25:** T1 0.850 pass; **T2 0.560 FAIL** (f80: T1 0.25, T2 0.35).

### R2. Manuscript (ZL3b primary; IT2a concordance)
Hand-5 pages, e = d − own null mean: f48r 0.168, **f57r 0.696**, f66r 0.199 (B-T), f66v 0.244 (ZL3b). IT2a: 0.242, 0.720, 0.204, 0.284. In herbal B, the three hand-5 pages are the **top three e of 21** in both transcriptions (next: f31v / f46r, hand 2, ≤ 0.17); f66r is the top e of the 5 B-T pages. Mean e per section × hand (ZL3b): H-hand 2 −0.038 (n 14), H-hand 3 −0.109 (4), **H-hand 5 +0.369 (3)**, T-hand 2 −0.018 (4), **T-hand 5 +0.199 (1)**; single-hand sections B-B −0.001, B-S −0.003.

| test | ZL3b stat | ZL3b p | Holm | IT2a p | gates | **verdict** |
|---|---|---|---|---|---|---|
| **T1** hand-5 mean e | S5 0.327 | **1/6,650 = 0.00015** (floor: the observed arrangement is the maximum) | 0.0003 | 0.00015 (S5 0.362) | pass | **HAND-5 EXCESS (IT2a concordant), conditional on the descriptive selection of hand 5** |
| **T2** omnibus between-hand | W 0.513 | 0.00055 | 0.00055 | 0.00015 | G-POW fail | **NOT TESTABLE (G-POW 0.56 < 0.80 at f 0.25)** |

**Drop-max (registered, descriptive):** T1 without f57r, as frozen: ZL3b S 0.203, **p 0.064**; IT2a 0.047. By the rule written in §5, the case file must say: **the registered drop-max does not survive at 0.05 in ZL3b, so the T1 result leans on f57r.** But see defect D1: the frozen code left f57r in the pool as an *unlabelled competitor*, so a hand-5 page competed against its own hand. **Post-hoc** (not registered, deterministic, no new seeds), with f57r removed from the pool entirely: S 0.203, p **1/950 = 0.00105** in both transcriptions (f48r and f66v remain the top two of the 20 herbal-B pages left, and f66r the top of B-T).

### R3. Verdict
- **T1: HAND-5 EXCESS, IT2a concordant.** Within section, the four Currier B pages of Fagin Davis's hand 5 sit further from the B pole (relative to their own section-and-length null) than every other arrangement of four same-section pages: p at the exact floor 1/6,650, Holm 0.0003. Power at a quarter-foreign pseudo-hand was 0.85, so the test could see a realistic effect. The FPR on pseudo-hands was 0.08 (see D2).
- **What it does *not* say.** (a) Hand 5 was picked out by C131/C132 descriptives on these same pages, so this is **conditional on that selection** (§0.1); there is no fresh data. (b) It is **four pages of one scribe** in two sections; it says nothing about scribes in general — the omnibus T2, which would, is **NOT TESTABLE** on power (0.56 at f 0.25). (c) The registered drop-max (0.064) says the result leans on f57r; the post-hoc repair (0.001) suggests the other three pages carry it too, but that number is post-hoc. (d) "Mixture" remains operational: hand-5 pages are better fitted by an A/B blend than other same-section B pages. It is not a claim that hand 5 wrote "another dialect", nor any reading.
- **Size.** Observed S5 0.33 is the size of a pseudo-hand with about **half its lines Currier A** (mean planted e 0.32 at f 0.5). That is large, and it is driven by f57r (e 0.70).
- **Nothing EXCLUDED** this cycle.

### R4. Defects disclosed
- **D1 (drop-max pool).** The registered drop-max kept the dropped hand-5 page in the permutation pool as an other-hand competitor. Registered value reported (0.064 / 0.047) and the rule's sentence written; the corrected version is post-hoc only.
- **D2 (pseudo-hand FPR 0.08, upper Wilson 0.126).** The gate (≤ 0.10) passes, but the rate is above the nominal 0.05. Likely cause: pseudo-hand pages get their null mean from R_P 100 replicates (seed 11917) while the other pages use R 400, so their e is noisier, which fattens the tail of a 4-page mean. This affects only the simulations; the real T1 uses R 400 for every page. A future gate should use the same R for both.
- **D3 (selection).** As §0.1; the cleanest follow-up is fresh lines: the `<->` drawing-split lines the C070 parser drops (f57r loses 6 of its 11 lines to the parser, 4 of them drawing splits) as a registered held-out check.

### R5. Seeds
11915–11918 used; 11919 reserved, unused; **next free 11920**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
