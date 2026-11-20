# K089 · KFG re-audit of K049 (colour agreement on the five K010 value-block pairs) with the exact margin-ceiling gate (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration, tool and shuffled-colour smoke pushed as `72a18e1` before the real
run; artefacts `4314e5e`).

## Why
K088 closed the physical / rare-mark block of line 6 and named the next stop: K049 on the KFG, with the p_floor gate.
K049 (OKR) asked whether the cords sharing each of K010's five confirmed value blocks also share the **same colour
code** beyond a within-khipu shuffle of B's colours. Its outcome: no pair supported; KH0362·KH0049 tool excluded
(copy-all), KH0128·KH0137 degenerate (`HB` vs `EB`), KH0140·KH0483 degenerate (all `W` on both), KH0304·KH0303 not
testable (3/7, p 0.0173, power 0.065), KH0305·KH0301 tool excluded (4/8, p 0.00470, shift FPR 0.143).

K088's lesson carries over exactly. Under N1 (uniform permutation of B's colours among the n units) A can never exceed
A_max = Σ_c min(n_A(c), n_B(c)) over matchable colour tuples c (`PK` never matches). The **smallest p the margins
allow** is p_floor = P(A = A_max). If p_floor ≥ α, no arrangement of these colours can be SUPPORTED, whatever the
plant says. K088's hypergeometric formula is the two-category case; with several colours the exact distribution is
computed here by dynamic programming over colour classes (all n! permutations counted exactly, n ≤ 12).

## Disclosed before writing this (nothing new on KFG colour)
- **OKR ceilings, from K049's published colour margins** (`analysis/k049_results.json`; exact, printed by the
  smoke's OKR arm, which uses the real and already public OKR colours):
  KH0362·KH0049 A_max 6, **p_floor 1/2**; KH0304·KH0303 A_max 3, **p_floor 2/105 = 0.0190**; KH0305·KH0301 A_max 4,
  **p_floor 1/210 = 0.00476**. With α = 0.01 the gate fires on the first two. So, under the rule below, **K049's
  KH0362·KH0049 TOOL EXCLUDED becomes NOT TESTABLE (margin ceiling)** and KH0304·KH0303's NOT TESTABLE (power) becomes
  NOT TESTABLE (margin ceiling) — a relabel of the reason, not of the reading (both were already unreadable).
  KH0305·KH0301 can reach α by its margins; it stays TOOL EXCLUDED (shift control) on the OKR.
- **KFG values (no colour), checked before this push:** the published K010 block is recovered once on each KFG side
  at the **same starts** as the OKR (46/82, 39/40, 20/20, 41/40) with the same CordGroups/cluster counts
  (2/2, 1/1, 1/2, 2/1). This is K073's value replication seen through the K049 locator. KH0483 is absent (merged into
  KH0140 by the KFG, K068/K073), so **KH0140·KH0483 is NOT TESTABLE (data)** by construction.

## Design (K049 frozen; data layer from K076/K073; only the ceiling is new)
- **Data.** KFG db `kfg_20261111.db` (SHA-256 `582e548d…742994d`) and its Excel files (CordGroups), hash-checked;
  OKR `khipu.db` @ `4039ca5` (SHA-256 `607913…c1c4db`) for A0. Tool
  [`tools/k089_kfg_block_colour_ceiling.py`](../tools/k089_kfg_block_colour_ceiling.py).
- **Engine.** `tools/k049_block_colour_agreement.py` imported verbatim (K046 14-case fixture, `colour_match` — `PK`
  never, `-` ≠ `:`, ordered components, `BY` ≠ `YB` —, `match_matrix`, `null_bank`, `pval`, `locate_side` with the
  leftmost tie-break, `build_units`, `colour_units`, `degeneracy_reason`, `n2_blocks`, `plant_power`) and **its
  per-pair loop copied verbatim** (k049 lines 359–480; only the checkpoint path is a variable). Statistic A = matches on
  the aligned block units; N1 R 10 000; copy-all control (R 2 000); calibration FPR (1 000) and cyclic-shift FPR, gate
  0.08; 25 % copy plant power (200 × R 2 000), bar 0.5; curve 0.10/0.15/0.25/0.40; N2 within `(cluster A, cluster B)`;
  sensitivities `BY` ≡ `YB` and non-zero units.
- **KFG layer (verbatim from K076, lines 43–106).** Pendants `^p\d+$` in pendant order, KFG `value` with R5
  multi-number pendants masked to 0 (K072/K073 port), colour = K074 primary coding (first `/`-segment, trailing
  `(a-b)` removed) split on `:` `-` `%` `^` (stored order), CordGroups from each xlsx (K071 parser) as the cluster key
  (ungrouped khipu → no key → N2 not applicable, disclosed).
- **New code (the only).** `exact_null` (exact N1 distribution of A by DP), `ceiling` (A_max, p_floor as a fraction,
  exact p of the observed A, exact null mean; conditional power at α is 0 by construction when the gate fires) and a
  fixture: 7 hand cases (incl. the K049 KH0362 shape 1/2, K088's 4/87 and 3/630, derangements 9/24) plus 40 random
  inventories (n ≤ 7) checked against brute-force enumeration of all permutations. The tool stops if any differs.
- **α and correction.** α = 0.05/5 = 0.01 (Bonferroni over the five named pairs, frozen from K049; the KH0140·KH0483
  slot is still spent). Holm on the KFG p is printed as a descriptive sensitivity: its first step is the same 0.01,
  so the ceiling is exact for any first rejection; a field could face 0.0125 only after another rejection.
- **Seeds.** N1 **6478**, calibration **6479**, power **6480**, N2 + sensitivities **6481**, copy-all **6482** (no
  derived seed). A0 reuses K049's own 4949–4953 on the OKR to rebuild its numbers (not new draws). Next free **6483**.

## Gates (cycle EXCLUDED if any fails)
**G0** hashes (OKR, KFG, every xlsx); K046 fixture 14/14; ceiling fixture (7 + 40 brute-force); **A0 values**: K049's
sequence builder recovers the K010 starts on the OKR; **A0 full**: the copied K049 loop on the OKR with seeds
4949–4953 reproduces `k049_results.json` **exactly** for every pair (n, A, verdict, degeneracy reason, p, null mean,
colour counts, copy-all A/p/passed, calibration and shift FPR, power and curve, N2 p).

## Decision rules (per pair, two tracks, written before the run)
- **Track A — frozen K049 rules** on KFG: DEGENERATE → TOOL EXCLUDED (copy-all fails, or calibration / shift FPR >
  0.08) → SUPPORTED iff p < 0.01 → NOT TESTABLE (power < 0.5) → NOT SUPPORTED.
- **Track B — K049 + ceiling gate (verdict of record).** DEGENERATE → **NOT TESTABLE (margin ceiling) iff p_floor ≥
  α** → then the frozen rules. Applied to the OKR (A0 data) and to the KFG.
- **Mapping KFG vs OKR (same track):** both unreadable → **REPLICATED (not readable on either)**; same readable verdict
  (SUPPORTED / NOT SUPPORTED) → **REPLICATED**; OKR readable, KFG different → **CHANGED (correction)**; OKR unreadable,
  KFG readable → **CHANGED (now readable)**; pair khipu missing on KFG or block not recovered → **NOT TESTABLE (data)**.
- **CORRECTED (of K049):** any OKR pair whose track-B verdict differs from K049's published verdict is listed and
  published as a correction of K049 (expected, from the disclosure above: KH0362·KH0049 and KH0304·KH0303 relabels).
- **Headline.** READABLE iff some KFG pair is SUPPORTED or NOT SUPPORTED under track B; otherwise NOT READABLE.
  A SUPPORTED pair would be colour agreement beyond frequency chance on a value block — not proof of the same object,
  not a decipherment; it would need the recorder caveat and a held-out look.

## What this cannot decide
K049's confounds stand: recorder coding (Ascher, Urton, Pereyra/HP) and the KFG team's colour harmonisation can make
equality unreadable or manufacture it (K074: OKR↔KFG colour concordance 0.811); a faithful copy would also agree; a
negative does not prove different objects. A ceiling verdict speaks about the instrument at this α with these margins,
not about the cords.

## Disclosed, not verdicts
N2 within-group p, `BY` ≡ `YB`, non-zero units, the plant power and curve, the exact p of each observed A, the Holm
column, the colour inventories per side, the census (museum / aliases).

## Smoke (plumbing only)
`run --smoke` shuffles every KFG colour within its khipu (K076's smoke shuffle) and uses small R; OKR colours are real
there (already public). Gates G0, fixtures (14 + 7 + 40), A0 values and the KFG block location passed; the smoke's
KFG statistics are shuffled noise and were not kept (smoke output deleted).

## Output
`analysis/k089_results.json`, log `analysis/k089_run.log`. Run from `expeditions/khipu/`:
`timeout 600 python3 tools/k089_kfg_block_colour_ceiling.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (run 20 Nov 2026 ~01:51 PT, America/Vancouver; 2.3 s; [`analysis/k089_results.json`](../analysis/k089_results.json), [log](../analysis/k089_run.log))
Run after the pre-registration, tool and smoke were published as `72a18e1` (connector `push_files`); the tool on disk
was byte-identical to the pushed one. Artefacts `4314e5e`. Nothing was cut by the wall.

**Gates (all pass).** G0 hashes (OKR, KFG, 695 xlsx); K046 fixture 14/14; ceiling fixture 7/7 hand cases + 40/40
random inventories equal to brute-force enumeration; **A0 values** (K010 starts 46/82, 39/40, 0/0, 20/20, 41/40);
**A0 full**: the copied K049 loop on the OKR with K049's seeds reproduces `k049_results.json` with **zero mismatches**
on all five pairs (n, A, verdicts, degeneracy reasons, p, null means, colour counts, copy-all, FPRs, power and curve,
N2 p). KFG layer: 695 khipus with pendants, 694 grouped, 2 588 R5 pendants masked (= K073/K076).

| Pair | n | A (KFG) | null mean | p (N1, R 10 000) | **A_max · p_floor (exact)** | copy-all | FPR perm / shift | power 25 % | Track A (frozen K049) | **Track B (with ceiling)** | OKR K049 → with ceiling | Mapping |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KH0362·KH0049 | 12 | 6 | 5.50 | 0.496 | 6 · **1/2 ≥ α** | **fail** (A 12, p 0.093) | 0 / 0 | 0.00 | TOOL EXCLUDED | **NOT TESTABLE (margin ceiling)** | TOOL EXCLUDED → **NOT TESTABLE (ceiling 1/2)** | REPLICATED (not readable on either) |
| KH0128·KH0137 | 10 | 0 | — | — | — | (p 1.00) | — | — | DEGENERATE (`HB` vs `EB`) | DEGENERATE | DEGENERATE | REPLICATED (not readable on either) |
| KH0140·KH0483 | — | — | — | — | — | — | — | — | NOT TESTABLE (data) | **NOT TESTABLE (data)** | DEGENERATE (all `W`, 12/12) | NOT TESTABLE (data): KH0483 merged into KH0140 by the KFG |
| KH0304·KH0303 | 7 | 3 | 0.85 | 0.0195 | 3 · **2/105 = 0.0190 ≥ α** | pass (A 7, p 0.0005) | 0 / 0 | 0.03 | NOT TESTABLE (power) | **NOT TESTABLE (margin ceiling)** | NOT TESTABLE → **NOT TESTABLE (ceiling 2/105)** | REPLICATED (not readable on either) |
| KH0305·KH0301 | 8 | 4 | 1.00 | 0.0060 | 4 · 1/210 = 0.00476 < α | pass (A 8, p 0.0010) | 0.003 / **0.143** | 0.03 | TOOL EXCLUDED | **TOOL EXCLUDED** (shift) | TOOL EXCLUDED (unchanged) | REPLICATED (not readable on either) |

**Same colours, recoded order.** On every pair the KFG colour inventory equals the OKR one up to the order of
mottled components (OKR `KB:W`, `GG:AB`, `CB:W`, `KB:MB`, `AB:W`, `GG:AB:W` → KFG `W:KB`, `AB:GG`, `W:CB`,
`MB:KB`, `W:AB`, `W:AB:GG`), none of which has a matching partner on either database, so no match is created or lost. Matching cords are the
same ones K049 listed: KH0362·KH0049 the six `AB`=`AB` (values 1856, 974, 1146, 1095, 849, 790); KH0304·KH0303 `W`
(22, 156) and `AB` (13); KH0305·KH0301 `W` (8, 57), `AB` (1), `GG` (3). n is unchanged (no `no_colour` units).
The Monte Carlo p moved only by seed (0.500 → 0.496, 0.0173 → 0.0195, 0.00470 → 0.00600); the exact p of the observed
A is 1/2, 2/105 and 1/210 on both databases.

**Mapping.** Track A: 4/4 testable pairs REPLICATED (not readable on either); KH0140·KH0483 NOT TESTABLE (data).
Track B (verdict of record): the same, **4/4 REPLICATED (not readable on either) + 1 NOT TESTABLE (data)**.
**Corrections of K049 (published here, relabels of unreadable verdicts):** KH0362·KH0049 TOOL EXCLUDED → **NOT
TESTABLE (margin ceiling, p_floor 1/2)**; KH0304·KH0303 NOT TESTABLE (power) → **NOT TESTABLE (margin ceiling,
p_floor 2/105)**. No verdict becomes readable and no positive result changes.

### Why the ceiling is the honest reading here
- **KH0362·KH0049.** Urton's side has a single non-`AB` cord, so A can only be 5 or 6 and P(A = 6) = 1/2 exactly
  (the `MB` cord must land on one of the six non-`AB` cords of KH0049). K049 blamed the copy-all control; the real cause
  is the inventory: no arrangement of these colours can get below p = 1/2.
- **KH0304·KH0303.** Two `W` and two `AB` on each side give at most 2 + 1 = 3 matches, reached with probability
  2/105 = 0.0190 — almost double α. The observed 3 is that maximum; "power 0.03" was a symptom, the ceiling is the cause.
- **KH0305·KH0301** is the only pair whose margins can reach α (1/210), and its observed 4 is that maximum (exact
  p 0.00476 < 0.01). It is still not interpretable: one of seven cyclic offsets of B's colours is as extreme as the real
  alignment (shift FPR 1/7 > 0.08), on both databases. Colour runs along the block can produce this agreement without
  the cord-to-cord correspondence. Holm (descriptive) would reject it at its first step (0.0060 < 0.01); the shift gate
  decides, as pre-registered.

### Disclosed, not verdicts
- **Every readable pair sits at its inventory maximum.** On KH0362·KH0049, KH0304·KH0303 and KH0305·KH0301 the
  observed A equals A_max (6, 3, 4) on both databases — every possible colour match is realised. A joint probability
  across pairs (1/2 · 2/105 · 1/210 ≈ 4.5 × 10⁻⁵ under independent N1) is **post hoc** and is not a result; it is a
  candidate for a pre-registered pooled test with a shift-aware null (line 6), named here so it cannot be smuggled in.
- **N2 within (cluster A, cluster B)** — CordGroups keys on KFG, same partitions as OKR: KH0362·KH0049 (8+4) p 0.251;
  KH0304·KH0303 (4+3) p 0.0437; KH0305·KH0301 (4+4) p 0.0117. Agreement shrinks once colour blocks inside groups are
  respected.
- **`BY` ≡ `YB`:** no `BY`/`YB` on the units; p 0.507 / 0.0195 / 0.0052 (the last not interpreted). Non-zero units
  identical to the primary (blocks have no zeros). Plant curves (0.10/0.15/0.25/0.40): KH0362·KH0049 all 0;
  KH0304·KH0303 0.01/0.01/0.08/0.22; KH0305·KH0301 0.03/0.03/0.03/0.14.
- **KFG census:** KH0362 UR122 (Museum of World Culture 1938.45.0228, Nazca) · KH0049 AS038/HP036 (MNAAHP 3550, Costa
  Sur); KH0128 UR1114/AS114 (Berlin VA16148) · KH0137 UR1123/AS123 (Berlin VA47085); KH0304 UR067 · KH0303 UR066
  (Puruchuco Museum s/n · 4a); KH0305 UR068 · KH0301 UR064 (Puruchuco Museum 2 · #3). KH0140 now carries the aliases
  AS125, UR247 (VA42610), 16 pendants, 3 groups; the shared block sits at its start.

**Headline: NOT READABLE, replicated; K049 corrected (two relabels).** On both databases the colour witness on the
five K010 value blocks cannot speak at α = 0.01: one pair is degenerate, one is resolved away by the KFG merge, two are
capped below α by their own colour margins, and the only pair whose margins can reach α fails the shift control.
This does not touch K010/K073's value correspondences, says nothing about same object vs copy, and reads no khipu.
No decipherment.

### Next (line 9)
K046–K049 (line 6 colour + physical block) is fully re-audited on KFG. Next: the K020 family with 1 000 null corpora
and bar intervals (K085/K086 bars 74.8–82.6 across seeds), or a pre-registered pooled colour test with a shift-aware
null on the K010 / K073 value blocks (the "all at maximum" observation above), with the p_floor gate from the start.
Seeds 6478–6482 used; next free **6483**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
