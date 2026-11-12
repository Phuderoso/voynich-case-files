# C109 — Expedição 109: the door with fixed hinges (alternation beyond slots)
*Does the two-class alternation found in C108 survive when every glyph is kept in its slot (same word length, same position), or is it all slot grammar?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Pre-registration (written and committed before any Voynich or generator statistic of this cycle was computed)

**Why.** C108 (F-VC step 1) found Voynich within-word Sukhotin alternation E 0.205–0.208, inside the voweled range, but its
null (shuffle inside each word) destroys positional slots as well as phonotactics, and the slot-based Timm–Schinner generator
reached 0.12–0.20. C108's registered next step (a) is this cycle. Prior work credited as in C108 (Sukhotin 1962; Guy 1991).

**Data, units, controls, halves.** Exactly as C108: `data/ZL3b-n.txt`, `data/IT2a-n.txt` (sha256 in `data/MANIFEST.md`),
EVA glyph units (`c003::units`), voweled controls Latin/Italian/Spanish/Finnish, abjad controls Hebrew (unpointed) and
devowelled Latin/Italian/Spanish, 15,000-token halves, Timm–Schinner generator defaults 3,400 lines, seeds 11738–11741.

**Statistic.** A as in C108 (share of within-word adjacent non-identical unit pairs in different Sukhotin classes).
**Null N2 (slot-preserving):** each unit is permuted only among tokens of the half with the same (word length in units,
position in word). This keeps every word length, every per-slot unit distribution and the unit multiset; it breaks only the
dependence between neighbouring units in a word. Sukhotin is **re-fitted** on every shuffle; NSH = 200.
**E_slot = A − mean(A_N2)**; p = (1 + #{A_N2 ≥ A})/(1 + NSH).

**Hypotheses (α = 0.05).**
- **H1** (alternation beyond slots): all four Voynich halves p < α/4 → **RESIDUAL**; none → **NO RESIDUAL** (C108's alternation
  is explained by slot structure at this N); else **SPLIT**.
- **H2 / H3 / H4**: Voynich E_slot vs the voweled, abjad and generator E_slot ranges (min–max over halves): INSIDE / ABOVE /
  BELOW / STRADDLE. H4 needs ≥ 6 generator halves, else NOT TESTABLE.

**Gates.** G1 FPR: 20 slot-shuffled voweled halves vs a fresh N2 null (NSH 100): ≤ 2/20 at α. G2 power: in a slot-shuffled
voweled half, restore the true spelling of 30 % of words: ≥ 16/20. G1 or G2 fail → all H **NOT TESTABLE**. G4: voweled and
abjad E_slot ranges must not overlap, else H2/H3 **NOT SEPARABLE**.

**Reading rule (fixed now).** H1 NO RESIDUAL → "the C108 alternation is slot structure, not neighbour dependence". H1 RESIDUAL
with H2 INSIDE → "neighbour alternation beyond slots at voweled strength"; with H2 BELOW and H3 INSIDE/ABOVE → "a weaker,
abjad-level residual". H4 says whether the generator matches. Descriptive only: the share of C108's E removed by slots,
1 − E_slot/E_C108. **No claim that any glyph is a vowel**, whatever the result: a slot-keeping null still allows syllable-like
patterns from a non-phonetic code.

**Seeds.** 11737 main, 11738–11741 generator; next free **11742**.

**Code.** `tools/c109_sukhotin_slot_null.py` (imports C108's encoder and Sukhotin fit unchanged), committed with this
pre-registration. Smoke test before commit (`smoke` mode): slot preservation asserted on Latin Caesar half 1 (lengths and
per-slot multisets for lengths 3 and 5), and one test on that half with NSH 20 (A 0.820, E_slot +0.226, V `aeiouy`); no Voynich
or generator statistic computed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
