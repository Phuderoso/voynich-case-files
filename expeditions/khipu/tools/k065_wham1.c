/* K065 (kernel copied verbatim from K064/K063) - rarity-weighted longest aligned segment with at most one non-matching position (Hamming-1 tolerance), per pair.
   A position on diagonal (i+t, j+t) MATCHES iff A[i+t] == B[j+t] and A[i+t] > 0; it contributes WA[i+t] = -ln f(value) (> 0).
   W = max over diagonals and over segments containing <= 1 non-match of the summed weight of the matching positions in the segment.
   Because all weights are > 0, the optimum on a diagonal is one maximal match run, or two maximal runs separated by exactly one
   non-match (same scan as K062's k062_hamming1.c, with cur += weight instead of cur++). Also returns the segment start (I, J) and
   K = number of matching positions in it. Build: cc -O2 -shared -fPIC -o k065_wham1.so k065_wham1.c
   Pimpolha Voynich, do Phuderoso - AI born 2026-11-04 */
#include <stdint.h>
void wham1(const int64_t *cat, const double *wcat, const int64_t *off, const int64_t *pa, const int64_t *pb, int64_t np,
           double *W, int64_t *I, int64_t *J, int64_t *K) {
  for (int64_t p = 0; p < np; p++) {
    const int64_t *A = cat + off[pa[p]], *B = cat + off[pb[p]]; const double *WA = wcat + off[pa[p]];
    int64_t na = off[pa[p] + 1] - off[pa[p]], nb = off[pb[p] + 1] - off[pb[p]];
    double best = 0.0; int64_t bi = -1, bj = -1, bk = 0;
    for (int64_t d = -(nb - 1); d <= na - 1; d++) {   /* i - j = d */
      int64_t i = d > 0 ? d : 0, j = d > 0 ? 0 : -d;
      double prev = 0.0, cur = 0.0; int64_t prevk = 0, curk = 0, segstart = i, curstart = i;
      for (; i < na && j < nb; i++, j++) {
        if (A[i] == B[j] && A[i] > 0) {
          cur += WA[i]; curk++;
          if (prev + cur > best + 1e-12) { best = prev + cur; bi = segstart; bj = segstart - d; bk = prevk + curk; }
        } else {
          prev = cur; prevk = curk; segstart = curstart; cur = 0.0; curk = 0; curstart = i + 1;
        }
      }
    }
    W[p] = best; I[p] = bi; J[p] = bj; K[p] = bk;
  }
}
