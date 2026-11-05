/* K016 weighted LCS over all pairs. out[p] for p over (a<b) in row-major order. */
#include <stdlib.h>
void wlcs_all(int nk, const int *off, const int *len, const long long *v, const double *w, double *out) {
    int maxn = 0; for (int k = 0; k < nk; k++) if (len[k] > maxn) maxn = len[k];
    double *prev = malloc(sizeof(double) * (maxn + 1)), *cur = malloc(sizeof(double) * (maxn + 1));
    long p = 0;
    for (int a = 0; a < nk; a++) for (int b = a + 1; b < nk; b++) {
        const long long *A = v + off[a], *B = v + off[b]; const double *WA = w + off[a]; int na = len[a], nb = len[b];
        for (int j = 0; j <= nb; j++) prev[j] = 0;
        for (int i = 1; i <= na; i++) {
            cur[0] = 0;
            for (int j = 1; j <= nb; j++) {
                double x = prev[j] > cur[j - 1] ? prev[j] : cur[j - 1];
                if (A[i - 1] == B[j - 1]) { double y = prev[j - 1] + WA[i - 1]; if (y > x) x = y; }
                cur[j] = x;
            }
            double *t = prev; prev = cur; cur = t;
        }
        out[p++] = prev[nb];
    }
    free(prev); free(cur);
}
