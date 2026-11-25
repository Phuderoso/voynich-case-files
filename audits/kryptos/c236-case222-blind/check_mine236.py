"""Voynich's own checker for Kryptos case 222 (PREREG236), written blind (her check236.py not opened).
usage: check_mine236.py CT perms.bin|x Xalpha.bin Yalpha.bin keys.bin gn217_output.txt
For every 'H' line: rebuild S (identity / family row / inverse), decrypt all 97 letters under model Q
(c = Y[x(p)+k] Vig, Y[x(p)-k] variant, Y[k-x(p)] Beaufort, key at plaintext index ix 0 or carved index ix 1),
recount the 24 crib seats (EASTNORTHEAST 22-34, BERLINCLOCK 64-74, 1-based) and compare with the printed agree.
Prints one TSV line per H line: fields, my_agree, printed_agree, match, pt97. Last line: 'S nH mismatches T-line'."""
import sys, struct
N = 97
POS = list(range(21, 34)) + list(range(63, 74)); CR = 'EASTNORTHEAST' + 'BERLINCLOCK'
def rec(fn, n): b = open(fn, 'rb').read(); return [b[i:i + n] for i in range(0, len(b), n)]
def main(ct, pf, xf, yf, kf, outf):
    C = [ord(c) - 65 for c in ct.strip()]; assert len(C) == N
    XA, YA = rec(xf, 26), rec(yf, 26); K = open(kf, 'rb').read()
    PB = None if pf == 'x' else open(pf, 'rb').read()
    nH = mm = 0; tline = ''
    for l in open(outf):
        if l.startswith('T '): tline = l.strip(); continue
        if not l.startswith('H '): continue
        d = {a: int(b) for a, b in (kv.split('=') for kv in l.split()[1:])}
        if d['perm'] < 0: S = list(range(N))
        else:
            P = list(struct.unpack('<97h', PB[d['perm'] * 194:(d['perm'] + 1) * 194]))
            if d['dir'] == 0: S = P
            else:
                S = [0] * N
                for i, v in enumerate(P): S[v] = i
        X, Y = XA[d['X']], YA[d['Y']]; yinv = [0] * 26
        for i, v in enumerate(Y): yinv[v] = i
        kw = K[d['w'] * N:(d['w'] + 1) * N]; pt = []
        for i in range(N):
            k = kw[i] if d['ix'] == 0 else kw[S[i]]; yy = yinv[C[S[i]]]
            xx = (yy - k) % 26 if d['form'] == 0 else (yy + k) % 26 if d['form'] == 1 else (k - yy) % 26
            pt.append(chr(65 + X[xx]))
        pt = ''.join(pt); ag = sum(pt[p] == c for p, c in zip(POS, CR)); nH += 1; ok = ag == d['agree']; mm += not ok
        print('\t'.join(str(d[k]) for k in ('perm', 'dir', 'ix', 'X', 'Y', 'form', 'w')) + f"\t{ag}\t{d['agree']}\t{int(ok)}\t{pt}")
    print(f'S nH={nH} mismatches={mm} {tline}')
if __name__ == '__main__': main(*sys.argv[1:7])
