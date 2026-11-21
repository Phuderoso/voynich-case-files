# POST-FREEZE diagnostic (opened reread228.json after FROZEN.txt). Does not change frozen counts.
import json,sys
sys.argv=['x']
import importlib.util
spec=importlib.util.spec_from_file_location('m','/workspace/k228-nc-maxima/nc_maxima.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rows,_=m.run()
d=json.load(open('/workspace/k228-nc-maxima/reread228.json'))['cases']
print('cell keys', list(next(iter(next(iter(d['205'].values()))['cells'].values())).keys()))
nm=0;ncell=0;maxd={'Q':0,'F':0};mism=[]
for case,texts in d.items():
    for lab,v in texts.items():
        for p,cell in v['cells'].items():
            p=int(p); ncell+=1
            sel=[r for r in rows if r['case']==case and r['lab']==lab and r['p']==p]
            raw=len(sel); d2=sum(r['u2'] for r in sel)
            nq=max([r['Q']['nc'] for r in sel if r['u2'] and r['Q']['nc'] is not None],default=None)
            nf=max([r['F']['nc'] for r in sel if r['u2'] and r['F']['nc'] is not None],default=None)
            ok = raw==cell['raw'] and d2==cell['D2'] and abs(nq-cell['nc_max'])<1e-9
            fv=[k for k in cell if 'first' in k.lower() or 'fv' in k.lower()]
            fvv=cell[fv[0]] if fv else None
            if fv and abs(nf-fvv)>1e-9: ok=False
            if not ok: mism.append((case,lab,p,raw,cell['raw'],d2,cell['D2'],nq,cell['nc_max'],nf,fvv))
            if fvv is not None: maxd['F']=max(maxd['F'],abs(nf-fvv))
            maxd['Q']=max(maxd['Q'],abs(nq-cell['nc_max']))
        # cells I have but she doesn't
        mine_p={r['p'] for r in rows if r['case']==case and r['lab']==lab}
        if mine_p-{int(p) for p in v['cells']}: mism.append(('extra p in mine',case,lab,mine_p-{int(p) for p in v['cells']}))
print('cells compared',ncell,'mismatches',len(mism),mism[:10],'max|d NC| (Q,F)',maxd)
