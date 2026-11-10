/* K062 - longest aligned run with at most one non-matching position (Hamming-1 tolerance), per pair.
   A position on diagonal (i+t, j+t) MATCHES iff A[i+t] == B[j+t] and A[i+t] > 0. T = max over diagonals and segments
   containing <= 1 non-match of the number of matching positions in the segment. Also returns (i, j) start of the best
   segment in A and B and the number of non-matches inside it (0 or 1).  Build: cc -O2 -shared -fPIC -o k062_hamming1.so k062_hamming1.c
   Pimpolha Voynich, do Phuderoso - AI born 2026-11-04 */
#include <stdint.h>
void ham1(const int64_t *cat, const int64_t *off, const int64_t *pa, const int64_t *pb, int64_t np,
          int64_t *T, int64_t *I, int64_t *J) {
  for (int64_t p = 0; p < np; p++) {
    const int64_t *A = cat + off[pa[p]], *B = cat + off[pb[p]];
    int64_t na = off[pa[p] + 1] - off[pa[p]], nb = off[pb[p] + 1] - off[pb[p]];
    int64_t best = 0, bi = -1, bj = -1;
    for (int64_t d = -(nb - 1); d <= na - 1; d++) {   /* i - j = d */
      int64_t i = d > 0 ? d : 0, j = d > 0 ? 0 : -d;
      int64_t prev = 0, cur = 0, segstart = i;  /* segstart: first index (in A) of the prev run */
      int64_t curstart = i;
      for (; i < na && j < nb; i++, j++) {
        if (A[i] == B[j] && A[i] > 0) {
          cur++;
          if (prev + cur > best) { best = prev + cur; bi = segstart; bj = segstart - d; }
        } else {
          prev = cur; segstart = curstart; cur = 0; curstart = i + 1;
        }
      }
    }
    T[p] = best; I[p] = bi; J[p] = bj;
  }
}
