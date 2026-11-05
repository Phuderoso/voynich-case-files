"""C016 POST-HOC (not counted): D1 sensitivity without the f69r.44-49 single-glyph loci and without one-unit words (null also without one-unit words)."""
import sys, json, numpy as np
sys.path.insert(0,'tools')
from c016_common import *
src,pred=DATASETS['D1_ZL_heldout']
labels,running,_,_=parse(src,pred)
out={}
for name,keep in (('drop_f69r_44_49',lambda p,l,w: not (p=='f69r' and l in {'44','45','46','47','48','49'})),('drop_one_unit_words',lambda p,l,w: len(units(w))>1)):
    lab=[x for x in labels if keep(*x)]; S=Sampler(lab,running)
    if name=='drop_one_unit_words':
        S.src={p:[w for w in S.src[p] if len(units(w))>1] for p in S.src}
    null=S.null_matrix(np.random.default_rng(1690),1999,FEATURES)
    out[name]={'tokens':len(lab)}
    for i,f in enumerate(FEATURES):
        o=float(np.mean([feat(w,f) for _,_,w in lab])); p,d=pval(o,null[:,i])
        out[name][f]={'label_mean':round(o,4),'null_mean':round(float(null[:,i].mean()),4),'p':round(p,4),'dir':d}
json.dump(out,open('analysis/C016_posthoc_D1_sensitivity.json','w'),indent=1); print(json.dumps(out,indent=0))
