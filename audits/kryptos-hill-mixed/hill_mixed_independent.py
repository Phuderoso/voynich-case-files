#!/usr/bin/env python3
"""
Independent audit of Kryptos case-file 28 / cycle 29
(Hill 2×2 with arbitrary letter numbering on K4).

Reference (Kryptos): tools/hill_mixed_sat.py
  - one-hot CNF over (σ, M), CaDiCaL, pairwise cardinality
  - product helpers; invertibility filtered AFTER search
  - decrypt form only: σ(P) = M · σ(C)

This reimplementation (different on purpose):
  - Glucose 4.2 (not CaDiCaL) as the primary CDCL engine
  - seqcounter cardinality (not pairwise)
  - invertibility enforced INSIDE the CNF (det one-hot ∈ (Z/26Z)*)
  - BOTH orientations as separate runs:
        decrypt : σ(P) = M · σ(C)
        encrypt : σ(C) = M · σ(P)
    (encrypt with invertible E ≡ decrypt with E^{-1}; both are checked)
  - both pair offsets 0 and 1
  - full 26-letter bijection (no I/J or U/V merge)
  - planted-control fast path: fixed-M Cadical probe before the joint search
  - unit-scaling classes reported (/12)

Cribs (0-indexed, verified against kryptos-case-files):
  EASTNORTHEAST at [21:33], BERLINCLOCK at [63:73] → 11 pairs / offset

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
"""
from __future__ import annotations
import argparse, json, time, sys
from pysat.solvers import Glucose42, Cadical153
from pysat.card import CardEnc, EncType

A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CRIBS = {21: "EASTNORTHEAST", 63: "BERLINCLOCK"}
UNITS = [u for u in range(26) if u % 2 == 1 and u % 13 != 0]


def is_unit(d: int) -> bool:
    return d % 2 == 1 and d % 13 != 0


def crib_map():
    d = {}
    for s, w in CRIBS.items():
        for i, ch in enumerate(w):
            d[s + i] = ch
    return d


def pairs_for(offset: int, n: int = 97):
    pt = crib_map()
    return [(i, i + 1) for i in range(offset, n - 1, 2) if i in pt and i + 1 in pt]


def verify_cribs():
    # Inclusive endpoints: EASTNORTHEAST is 13 letters at 21..33,
    # BERLINCLOCK is 11 letters at 63..73 (Kryptos case-file 28 / Sanborn cribs).
    assert len(CRIBS[21]) == 13 and CRIBS[21] == "EASTNORTHEAST"
    assert len(CRIBS[63]) == 11 and CRIBS[63] == "BERLINCLOCK"
    assert 21 + len(CRIBS[21]) - 1 == 33
    assert 63 + len(CRIBS[63]) - 1 == 73
    for off in (0, 1):
        assert len(pairs_for(off)) == 11


class HillMixedCNF:
    """Build a joint CNF for (σ, M) with in-model invertibility."""

    def __init__(self, ct: str, offset: int, orientation: str = "decrypt"):
        assert orientation in ("decrypt", "encrypt")
        self.ct = ct
        self.offset = offset
        self.orientation = orientation
        self.pt = crib_map()
        self.pairs = pairs_for(offset, len(ct))
        self.top = 0
        self.cl = []
        self.s = {L: [self._nv() for _ in range(26)] for L in A}
        self.m = [[self._nv() for _ in range(26)] for _ in range(4)]
        self._build()

    def _nv(self):
        self.top += 1
        return self.top

    def _exactly_one(self, lits):
        enc = CardEnc.equals(
            lits=lits, bound=1, top_id=self.top, encoding=EncType.seqcounter
        )
        self.top = max(self.top, enc.nv)
        self.cl.extend(enc.clauses)

    def _product_onehot(self, m_row_k: int, letter: str):
        """one-hot t[v] <=> m[k]·σ(letter) ≡ v (mod 26)."""
        t = [self._nv() for _ in range(26)]
        self._exactly_one(t)
        mk = self.m[m_row_k]
        sx = self.s[letter]
        for a in range(26):
            for x in range(26):
                # mk=a & sx=x ⇒ t[a*x mod 26]
                self.cl.append([-mk[a], -sx[x], t[(a * x) % 26]])
        return t

    def _eq_sum_to_letter(self, t1, t2, letter: str):
        """Force σ(letter) ≡ t1 + t2 (mod 26)."""
        for i in range(26):
            for j in range(26):
                self.cl.append([-t1[i], -t2[j], self.s[letter][(i + j) % 26]])

    def _build(self):
        for L in A:
            self._exactly_one(self.s[L])
        for v in range(26):
            self._exactly_one([self.s[L][v] for L in A])
        for k in range(4):
            self._exactly_one(self.m[k])

        # --- invertibility inside the model ---
        # det = m0*m3 - m1*m2; build one-hot det via products of one-hots
        # ad[v] <=> m0*m3 ≡ v; bc[v] <=> m1*m2 ≡ v
        ad = [self._nv() for _ in range(26)]
        bc = [self._nv() for _ in range(26)]
        self._exactly_one(ad)
        self._exactly_one(bc)
        for a in range(26):
            for b in range(26):
                self.cl.append([-self.m[0][a], -self.m[3][b], ad[(a * b) % 26]])
                self.cl.append([-self.m[1][a], -self.m[2][b], bc[(a * b) % 26]])
        det = [self._nv() for _ in range(26)]
        self._exactly_one(det)
        for i in range(26):
            for j in range(26):
                # det ≡ ad - bc ≡ ad + (-bc) ≡ ad + (26-j)%26 when bc=j
                self.cl.append([-ad[i], -bc[j], det[(i - j) % 26]])
        # forbid non-units
        for v in range(26):
            if not is_unit(v):
                self.cl.append([-det[v]])

        # --- crib equations ---
        for i, j in self.pairs:
            c1, c2, p1, p2 = self.ct[i], self.ct[j], self.pt[i], self.pt[j]
            if self.orientation == "decrypt":
                # [σp1] = M [σc1]
                self._eq_sum_to_letter(
                    self._product_onehot(0, c1), self._product_onehot(1, c2), p1
                )
                self._eq_sum_to_letter(
                    self._product_onehot(2, c1), self._product_onehot(3, c2), p2
                )
            else:
                # [σc1] = M [σp1]
                self._eq_sum_to_letter(
                    self._product_onehot(0, p1), self._product_onehot(1, p2), c1
                )
                self._eq_sum_to_letter(
                    self._product_onehot(2, p1), self._product_onehot(3, p2), c2
                )

        self.involved = sorted(
            {self.ct[i] for p in self.pairs for i in p}
            | {self.pt[i] for p in self.pairs for i in p}
        )
        self.proj = [v for k in range(4) for v in self.m[k]] + [
            v for L in self.involved for v in self.s[L]
        ]

    def solve(self, cap: int = 24, timeout_s: float = 480.0, engine: str = "glucose"):
        Solver = Glucose42 if engine == "glucose" else Cadical153
        sols = []
        t0 = time.time()
        timed_out = False
        with Solver(bootstrap_with=self.cl) as S:
            # pysat Glucose42 supports conf_budget / prop_budget; use wall clock
            while len(sols) < cap:
                if time.time() - t0 > timeout_s:
                    timed_out = True
                    break
                # interrupt-friendly: short solve loops via assumptions not available;
                # rely on wall clock between solves. For first call, may run long.
                if hasattr(S, "solve_limited"):
                    # Glucose: use conflict budget slices
                    ok = S.solve()
                else:
                    ok = S.solve()
                if not ok:
                    break
                mod = set(l for l in S.get_model() if l > 0)
                M = [next(a for a in range(26) if self.m[k][a] in mod) for k in range(4)]
                sig = {
                    L: next(v for v in range(26) if self.s[L][v] in mod) for L in A
                }
                part = {L: sig[L] for L in self.involved}
                det = (M[0] * M[3] - M[1] * M[2]) % 26
                assert is_unit(det), (M, det)
                sols.append((M, part, sig))
                S.add_clause([-x for x in self.proj if x in mod])
        return {
            "orientation": self.orientation,
            "offset": self.offset,
            "pairs": len(self.pairs),
            "involved": len(self.involved),
            "solutions": len(sols),
            "classes_approx": round(len(sols) / 12.0, 2),
            "timed_out": timed_out,
            "proved_unsat": (not timed_out) and len(sols) == 0,
            "time_s": round(time.time() - t0, 2),
            "engine": engine,
            "samples": [
                {
                    "M": M,
                    "det": (M[0] * M[3] - M[1] * M[2]) % 26,
                    "sigma_part": "".join(f"{L}{part[L]} " for L in sorted(part)),
                }
                for M, part, _ in sols[:3]
            ],
            "found_Ms": [M for M, _, _ in sols],
        }


def fixed_M_probe(ct, offset, M, orientation="decrypt") -> bool:
    """Cadical probe with M fixed (alphabet constraint propagation via SAT)."""
    pt = crib_map()
    pairs = pairs_for(offset, len(ct))
    top = [0]

    def nv():
        top[0] += 1
        return top[0]

    s = {L: [nv() for _ in range(26)] for L in A}
    cl = []

    def exactly_one(lits):
        enc = CardEnc.equals(lits=lits, bound=1, top_id=top[0], encoding=EncType.seqcounter)
        top[0] = max(top[0], enc.nv)
        cl.extend(enc.clauses)

    for L in A:
        exactly_one(s[L])
    for v in range(26):
        exactly_one([s[L][v] for L in A])
    a, b, c, d = M
    for i, j in pairs:
        c1, c2, p1, p2 = ct[i], ct[j], pt[i], pt[j]
        if orientation == "decrypt":
            src1, src2, dst1, dst2 = c1, c2, p1, p2
        else:
            src1, src2, dst1, dst2 = p1, p2, c1, c2
        for x in range(26):
            for y in range(26):
                cl.append([-s[src1][x], -s[src2][y], s[dst1][(a * x + b * y) % 26]])
                cl.append([-s[src1][x], -s[src2][y], s[dst2][(c * x + d * y) % 26]])
    with Cadical153(bootstrap_with=cl) as S:
        return bool(S.solve())


def load_ct(src: str) -> str:
    if src == "K4":
        from kryptos_text import K4
        return K4
    return open(src).read().strip()


def main():
    verify_cribs()
    ap = argparse.ArgumentParser()
    ap.add_argument("texts", nargs="+")
    ap.add_argument("--timeout", type=float, default=480.0)
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--offsets", default="0,1")
    ap.add_argument("--orientations", default="decrypt,encrypt")
    ap.add_argument("--engine", default="glucose", choices=["glucose", "cadical"])
    ap.add_argument("--prefer-M", default="", help="probe this M first (e.g. 7,24,14,15)")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    offsets = [int(x) for x in args.offsets.split(",")]
    orientations = [x.strip() for x in args.orientations.split(",") if x.strip()]
    prefer = [int(x) for x in args.prefer_M.split(",")] if args.prefer_M else None

    results = []
    for src in args.texts:
        ct = load_ct(src)
        assert len(ct) == 97, (src, len(ct))
        for orient in orientations:
            for off in offsets:
                print(f"=== {src} {orient} offset={off} ===", flush=True)
                probe = None
                if prefer is not None:
                    t0 = time.time()
                    ok = fixed_M_probe(ct, off, prefer, orient)
                    probe = {
                        "M": prefer,
                        "ok": ok,
                        "time_s": round(time.time() - t0, 3),
                    }
                    print(f"   prefer-M probe {prefer}: {ok} ({probe['time_s']}s)", flush=True)

                cnf = HillMixedCNF(ct, off, orient)
                r = cnf.solve(cap=args.cap, timeout_s=args.timeout, engine=args.engine)
                r["text"] = src
                r["prefer_M_probe"] = probe
                print(
                    f"{src} {orient} offset={off} sols={r['solutions']} "
                    f"classes~{r['classes_approx']} proved_unsat={r['proved_unsat']} "
                    f"timeout={r['timed_out']} time={r['time_s']}s engine={r['engine']}",
                    flush=True,
                )
                for s in r["samples"]:
                    print(f"   M={s['M']} det={s['det']} sigma_part={s['sigma_part']}", flush=True)
                    # cross-check sample with fixed-M Cadical
                    ok = fixed_M_probe(ct, off, s["M"], orient)
                    print(f"   fixed-M Cadical cross-check: {ok}", flush=True)
                    s["cadical_crosscheck"] = ok
                results.append(r)

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(results, f, indent=2)
        print("wrote", args.json_out, flush=True)


if __name__ == "__main__":
    main()
