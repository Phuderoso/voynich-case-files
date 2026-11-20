#!/usr/bin/env python3
"""Rank rule of PREREG223 applied to counts_voynich.tsv: p_up=(1+#{null>=K4})/(M+1), p_low with <=, null median/95th pct."""
import sys, statistics
rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
hdr=rows[0]; data={r[0]:list(map(int,r[1:])) for r in rows[1:]}
k4=data.pop('K4'); M=len(data)
print(f"M={M} nulls")
print("stat\tK4\tnull_min\tnull_median\tnull_p95\tnull_max\t#null>=K4\tp_up\t#null<=K4\tp_low")
for i,h in enumerate(hdr[1:]):
    v=sorted(x[i] for x in data.values()); K=k4[i]
    ge=sum(x>=K for x in v); le=sum(x<=K for x in v)
    p95=v[int(round(0.95*(M-1)))]
    print(f"{h}\t{K}\t{v[0]}\t{statistics.median(v)}\t{p95}\t{v[-1]}\t{ge}\t{(1+ge)/(M+1):.4f}\t{le}\t{(1+le)/(M+1):.4f}")
