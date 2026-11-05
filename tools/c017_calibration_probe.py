"""C017 calibration probe (design-only; pseudo-labels from running text, no real label feature computed).
Compares unblocked vs size-blocked page permutation, raw vs studentized contrast, 400 unplanted draws at tau_design.
Output pasted in analysis/C017_calibration_probe.txt. Usage: timeout 600 python3 tools/c017_calibration_probe.py"""
import sys; sys.path.insert(0,'tools')
from c017_common import *; from c016_common import Planter
import numpy as np
for name in ['ZL','IT']:
    D=use_blocked(Design(FILES[name],1999,1),1999,5); P=Planter(D.pool); A=D.g==1
    print(name, [(int(b), int(((size_blocks(D.k)==b)&A).sum()), int(((size_blocks(D.k)==b)&~A).sum())) for b in np.unique(size_blocks(D.k))])
    for f,tau in [('o_init',0.1),('len',0.5),('y_fin',0.1),('q_init',0.1),('gallows',0.1)]:
        rng=np.random.default_rng(98); pr=[];pt=[]
        for _ in range(400):
            e=D.excess(plant(D,P,D.pseudo(rng),f,A,0.0,tau,rng),f); pr.append(D.contrast_test(e)[1]); pt.append(D.t_test(e)[1])
        pr=np.array(pr);pt=np.array(pt)
        print(name,f,'raw',(pr<=.05).mean(),(pr<=.0035).mean(),'stud',(pt<=.05).mean(),(pt<=.0035).mean(),flush=True)
