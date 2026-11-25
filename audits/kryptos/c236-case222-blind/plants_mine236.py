"""Gate P recovery, Voynich's rule (blind): plant id recovered iff some H line of its slice has the planted perm, X, Y, form and
window bytes (and dir, ix for families; ix is immaterial for direct), its agree re-derived by check_mine236.py matches,
and its 97-letter decrypt differs from the planted plaintext in <= 1 letter. Prints per plant + total + Wilson 95% interval."""
import sys, math, subprocess
K = open('keys236.bin', 'rb').read(); ok_n = 0; rows = [l.rstrip('\n').split('\t') for l in open('plants236.tsv')]
for pid, scope, ct, qi, dr, ix, x, y, f, w, seat, pt in rows:
    pf, xa = ('x', 'alpha.bin') if scope == 'direct' else (scope + '.bin', 'themed144.bin')
    out = subprocess.run([sys.executable, '../audit/check_mine236.py', ct, pf, xa, xa, 'keys236.bin', f'../out/P/p{pid}.txt'],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    kw = K[int(w) * 97:(int(w) + 1) * 97]; ok = False; n = 0
    for l in out[:-1]:
        t = l.split('\t'); n += 1
        same = (int(t[0]) == int(qi) and int(t[3]) == int(x) and int(t[4]) == int(y) and int(t[5]) == int(f)
                and K[int(t[6]) * 97:(int(t[6]) + 1) * 97] == kw and (scope == 'direct' or (int(t[1]) == int(dr) and int(t[2]) == int(ix))))
        if same and t[9] == '1' and sum(a != b for a, b in zip(t[10], pt)) <= 1: ok = True
    ok_n += ok; print(pid, scope, 'seat', seat, 'lines', n, out[-1].split()[2], 'PASS' if ok else 'FAIL')
z = 1.959964; n = len(rows); p = ok_n / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
print(f'recovered {ok_n}/{n} Wilson95 {c - h:.3f}-{c + h:.3f}')
