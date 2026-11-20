# K088 · KFG re-audit of K048 (rare-label concordance on the three K019 pairs) with an exact margin-ceiling gate (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration, tool and shuffled-feature smoke pushed as `a272a92` before the real
run; artefacts `44c4bcb`).

## Why
Step 3 of the physical-witness block of the KFG re-audit (K087 did K047). K048 (OKR) asked whether the *rare* marks on
the value-aligned cords of KH0097·KH0586, KH0192·KH0470 and KH0192·KH0469 land on each other more than chance:
H_T = both ends broken (`B`), H_D = both majority knot directions `S`. Its headline: **one powered negative**
(Paris·Lima termination, A = 1, p 0.0458, power 0.945 at the 50 % rare-share plant), one tool-excluded, one not
testable, three degenerate.

Reading K048 again for this port, one thing in its own numbers needs an exact check, not an opinion. Under N1 the
dual-rare count is Hypergeometric(n, n_rare_A, n_rare_B), and A can never exceed min(n_rare_A, n_rare_B). So the
**smallest p the observed margins allow** is

  p_floor = P(X = min(n_rare_A, n_rare_B)) = C(n_A, m)·C(n − n_A, n_B − m) / C(n, n_B), m = min(n_A, n_B).

If p_floor ≥ α, *no* arrangement of the observed labels can be SUPPORTED: the test is not testable by construction,
whatever the plant says. K048's power plant overwrote B to rare on A's rare units, which **raises n_rare_B** (from 1 to
up to 3 on Paris·Lima); it measured how well the engine sees a world with more broken HP ends, not whether the
observed margins could ever reach α. That is a gap in K048's gate list, and this cycle closes it — pre-registered here,
applied identically to the OKR (F0) and to the KFG.

## Disclosed before writing this (all already public; nothing new was computed on the KFG)
- **OKR, from K048's published margins** (`analysis/k048_results.json`): Paris·Lima termination n 87, n_rare 4 / 1 →
  p_floor = 4/87 = 0.0460 ≥ α = 0.00833. KH0192·KH0470 termination n 37, 1 / 3 → p_floor = 3/37 = 0.0811 ≥ α.
  KH0192·KH0469 termination n 36, 3 / 2 → p_floor = 3/630 = 0.00476 < α. So, under the rule below, **K048's Paris·Lima
  "NOT SUPPORTED (powered negative)" becomes NOT TESTABLE (margin ceiling)** and KH0192·KH0470's TOOL EXCLUDED becomes
  NOT TESTABLE (margin ceiling). The smoke run printed exactly these (they are F0 margins, not KFG statistics).
- **KFG termination margins are already public in K087** (labels on the aligned units: KH0097·KH0586 A {K 83, B 4,
  U 2} / B {K 87, B 1, U 1}; KH0192·KH0470 A {K 36, B 1} / B {K 34, B 3}; KH0192·KH0469 A {K 33, B 3} / B {K 34, B 2}).
  So the termination ceiling on the KFG is effectively known in advance (4/89 = 0.0449, 3/37, 3/630). This cycle is
  therefore declared as a **short not-testable-by-construction audit**: what it adds is the exact F0 rebuild, the
  dual-rare counts and knot-direction `S` margins on the KFG, the frozen-rule replication mapping, and the published
  correction of K048. I name the foreknowledge here so nobody mistakes a known ceiling for a discovery.

## Design (K048 frozen; data layer from K087; only the ceiling is new)
- **Data.** KFG db `kfg_20261111.db` (SHA-256 `582e548d…742994d`) and its Excel files (CordGroups), hash-checked;
  OKR `khipu.db` @ `4039ca5` (SHA-256 `607913…c1c4db`) for F0. Tool
  [`tools/k088_kfg_rare_label_ceiling.py`](../tools/k088_kfg_rare_label_ceiling.py).
- **Engine.** `tools/k048_rare_label_concordance.py` imported verbatim (fixture of 27, `attach`, `evaluate`,
  `sensitivity_block`, N1 R 10 000, calibration 1 000, shift FPR, copy-all R 2 000, 50 % rare-share plant 200 × 2 000,
  curve 0.25/0.50/0.75/1.00) and its per-pair loop copied; only its `SEEDS` dict is replaced.
- **KFG layer.** K087's knot-direction port (fixture 7/7) and KFG data layer + physical port copied verbatim (pendants
  `^p\d+$`, R5 mask, CordGroups, KFG leader weights, weighted leader LCS; termination empty/`?`/`None`/`nan` → missing).
- **New code (the only).** `hyper_sf`, `p_floor`, `ceiling_block` (A_max, p_floor, exact hypergeometric p of the
  observed A, whether the gate fires; conditional power at α is **0 by construction** when it fires — no simulation)
  and a fixture of 7 hand-computed cases (4/87, 1/10, 3/630, 3/37, 1/252, two tail identities); the tool stops if any
  differs by > 1e-12.
- **α and correction.** α = 0.05/6 = 0.00833 (Bonferroni over 3 pairs × 2 fields, frozen from K048; degenerate fields
  still spend their slot). Holm would not change any ceiling verdict: degenerate fields are never rejected, so the most a
  field could face under Holm is 0.05/5 = 0.01 (if KH0192·KH0469 termination, floor 0.00476, were rejected first),
  still below the floors 0.0449–0.0811 where the gate fires. Bonferroni stays the rule; BH is not used (K048's family
  is FWER).
- **Seeds.** N1 6473, calibration 6474, power 6475, N2 6476, sensitivities 6477; the K048 engine derives its copy-all
  seed as power + 100 = **6575** (disclosed; later cycles must skip 6575). Next free **6478**.

## Gates (cycle EXCLUDED if any fails)
G0 hashes (OKR, KFG, every xlsx); K048 fixture 27/27; KFG knot fixture 7/7; ceiling fixture 7/7; **F0**: the K048
engine on the OKR reproduces K048's published (n, n_rare_A, n_rare_B, A) for all six pair-fields exactly; **K019
consistency on KFG**: 13/89, 14/37, 15/36.

## Decision rules (per pair-field, two tracks, written before the run)
- **Track A — frozen K048 rules** (DEGENERATE → TOOL EXCLUDED → NOT TESTABLE (power/n) → SUPPORTED iff p < α → NOT
  SUPPORTED), on KFG vs K048's published OKR verdict, mapped as in K087: both unreadable → REPLICATED (not readable on
  either); same readable verdict → REPLICATED; OKR readable, KFG different → CHANGED (correction); OKR unreadable, KFG
  readable → CHANGED (now readable).
- **Track B — K048 + ceiling gate (the K088 rule; this is the verdict of record).** Order: cycle exclusion →
  DEGENERATE → **NOT TESTABLE (margin ceiling) iff p_floor ≥ α** → then the frozen K048 rules. Applied to the OKR
  margins (F0) and to the KFG margins; KFG vs OKR-with-ceiling mapped as above. Any OKR field whose track-B verdict
  differs from K048's published verdict is listed as a **correction of K048** and published as such.
- **Headline.** READABLE iff some KFG pair-field is SUPPORTED or NOT SUPPORTED under track B; otherwise NOT READABLE.
  A SUPPORTED field would be a KFG-only rare-mark witness needing held-out confirmation. No decipherment either way.

## What this cannot decide
Recorder coding of `B` vs `U` vs `K` (Ascher, Urton, Pereyra/HP), breakage between recordings, and a shared S-knot
habit are all named in K048 and stand. A ceiling verdict says the *instrument* cannot speak at this α with these few
rare marks; it says nothing about same object vs copy.

## Disclosed, not verdicts
With-leaders and non-zero-value-unit sensitivities (K048's `sensitivity_block`), N2 within-group p, the 50 % plant
power and curve, the exact hypergeometric p of each observed A.

## Smoke (plumbing only)
`--smoke` shuffles every KFG physical feature within its khipu (K087's smoke shuffle) and uses small R; output
`analysis/k088_smoke.json`. Gates G0, fixtures (27 + 7 + 7), F0 6/6 and alignment 13/89, 14/37, 15/36 passed in
3.1 s. Its KFG numbers are meaningless by design and are not used for any decision.

## Output
`analysis/k088_results.json`, log `analysis/k088_run.log`. Run from `expeditions/khipu/`:
`timeout 600 python3 tools/k088_kfg_rare_label_ceiling.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (run 19 Nov 2026 ~21:48 PT, America/Vancouver; 4.2 s; [`analysis/k088_results.json`](../analysis/k088_results.json), [log](../analysis/k088_run.log))
Run after the pre-registration, tool and smoke were published as `a272a92` (connector `push_files`). Artefacts `44c4bcb`.

**Gates:** G0 hashes pass; K048 fixture 27/27; KFG knot fixture 7/7; ceiling fixture 7/7; **F0 6/6** (the K048 engine
on the OKR reproduces K048's (n, n_rare_A, n_rare_B, A) exactly); KFG alignment 13/89, 14/37, 15/36 (= K019/K076/K087).

| Pair · field | n | rare A / B | A (dual-rare) | null mean | p (N1) | p_floor (exact) | copy-all | FPR perm / shift | power 50 % | Track A (frozen K048) | **Track B (with ceiling)** | K048 on OKR → with ceiling |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KH0097·KH0586 termination | 89 | 4 / 1 | 1 | 0.045 | 0.0449 | **0.0449 ≥ α** | pass (A 4, p 0.0005) | 0 / 0 | 0.975 | NOT SUPPORTED | **NOT TESTABLE (margin ceiling)** | NOT SUPPORTED → **NOT TESTABLE (ceiling, 4/87 = 0.0460)** |
| KH0097·KH0586 knot dir | 82 | 18 / 0 | 0 | — | — | — | — | — | — | DEGENERATE (B all `Z`) | DEGENERATE | DEGENERATE |
| KH0192·KH0470 termination | 37 | 1 / 3 | 0 | 0.078 | 1.000 | **0.0811 ≥ α** | **fail** (A 1, p 0.025) | 0 / 0 | 0.00 | TOOL EXCLUDED | **NOT TESTABLE (margin ceiling)** | TOOL EXCLUDED → **NOT TESTABLE (ceiling, 3/37)** |
| KH0192·KH0470 knot dir | 27 | 0 / 6 | 0 | — | — | — | — | — | — | DEGENERATE (A no `S`) | DEGENERATE | DEGENERATE |
| KH0192·KH0469 termination | 36 | 3 / 2 | 0 | 0.166 | 1.000 | 0.00476 < α | pass (A 3, p 0.0005) | 0.001 / 0.034 | 0.035 | NOT TESTABLE (power) | NOT TESTABLE (power) | NOT TESTABLE (unchanged) |
| KH0192·KH0469 knot dir | 21 | 0 / 2 | 0 | — | — | — | — | — | — | DEGENERATE (A all `Z`) | DEGENERATE | DEGENERATE |

Labels on the usable units are exactly K087's (termination A {K 83, B 4, U 2} / B {K 87, B 1, U 1}; KH0192·KH0470
A {K 36, B 1} / B {K 34, B 3}; KH0192·KH0469 A {K 33, B 3} / B {K 34, B 2}); knot-direction margins equal K048's OKR
ones (KH0097 18 `S` / KH0586 0; KH0192 0 `S` on both Berlin alignments; KH0470 6, KH0469 2). The only data change from
the OKR is again n 87 → 89 on Paris·Lima (two coded `K` ends): A stays 1, the single dual-`B` unit is the same
zero-value cord (group pair 10, positions 7 / 9), p 0.0458 → 0.0449. The permutation p equals the exact floor, as it
must when A = A_max.

**Mapping.** Track A (frozen K048 rules): Paris·Lima termination **REPLICATED** (NOT SUPPORTED on both), the other five
REPLICATED (not readable on either). Track B (verdict of record): **6/6 REPLICATED (not readable on either)**.
**Corrections of K048 (published here):** Paris·Lima termination NOT SUPPORTED → **NOT TESTABLE (margin ceiling)**;
KH0192·KH0470 termination TOOL EXCLUDED → **NOT TESTABLE (margin ceiling)** (both unreadable before and after; the reason
changes from a gate failure to a property of the data).

### Why the ceiling is the honest reading
With one broken HP end on the aligned units, the dual-`B` count can be 0 or 1. P(A = 1) = 4/89: the best possible
arrangement of these labels — the one HP break sitting on one of the four Paris breaks, which is what we observe — is
already the most extreme outcome and still sits at p 0.045, five times α. A "powered negative" there is impossible:
the 0.975 plant power describes a world where B carries three broken ends, not this one. So the observed A = 1 is not
evidence *against* shared breaks; it is the top of a scale too short to reach α. The same holds on KH0192·KH0470
(one Ascher `B`; best case 3/37). Only KH0192·KH0469 has margins that *could* reach α (both HP-side `B`s on Ascher
`B`s: 3/630), and there the observed A is 0 and the plant power 0.035.

### Disclosed, not verdicts
With leaders: Paris·Lima termination n 102, 4 / 1, A 1, p 0.040; Berlin termination A 0, p 1.0 (n 51 each); Berlin knot
direction with leaders becomes non-degenerate (one Ascher leader `S`): KH0192·KH0470 A 1, p 0.21; KH0192·KH0469 A 1,
p 0.30. Non-zero-value units: every termination field degenerates (the Paris·Lima dual-`B` is the zero-value cord).
N2 within-group: Paris·Lima p 0.142, Berlin p 1.0. Plant curve (0.25/0.50/0.75/1.00): Paris·Lima 0.03/0.98/1.00/1.00;
KH0192·KH0470 0/0/0/0; KH0192·KH0469 0/0.06/0.06/1.00. One of 29 circular shifts on KH0192·KH0469 reached p 0.0053
(shift FPR 0.034 ≤ 0.08, gate passes).

**Headline: NOT READABLE, replicated; K048 corrected.** On both databases, for these three pairs, the rare-mark witness
cannot speak at α = 0.05/6: three fields are degenerate, two are capped below α by their own margins, one lacks power.
K048's "one powered negative" was a gate gap, now closed with an exact rule. This overturns no positive result and says
nothing about same object vs copy. No decipherment.

### Next (line 9)
The physical / rare-mark block of the K019 pairs (K046–K048) is fully re-audited on KFG. Next: the K020 family with
1 000 null corpora and bar intervals (K085/K086 bars vary 74.8–82.6 across seeds), or K049 (colour on the five K010
value-block pairs) on KFG; any future rare-label or small-margin test carries the p_floor gate from the start.
Seeds 6473–6477 used (+ derived 6575); next free **6478**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
