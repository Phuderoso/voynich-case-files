import json,csv
d=json.load(open('her/summary229.json'))
rows={int(r['nq']):r for r in csv.DictReader(open('counts_by_nq.tsv'),delimiter='\t')}
f=lambda x: None if x=='NA' else round(float(x),3)
bad=0
for k,v in d['null_by_nq'].items():
    q=int(k); r=rows[q]; mine=(int(r['N_bin']),int(r['pass_bin']),f(r['max_NC']))
    if mine!=tuple(v): bad+=1; print('NULL DIFF',q,mine,v)
for k,v in d['k4_by_nq'].items():
    q=int(k); r=rows[q]; mine=(int(r['K4_N']),int(r['K4_pass']),f(r['K4_max_NC']))
    if mine!=tuple(v): bad+=1; print('K4 DIFF',q,mine,v)
print('her null bins',len(d['null_by_nq']),'her K4 bins',len(d['k4_by_nq']),'my bins',len(rows),'diffs',bad)
print('my null bins missing from hers:',sorted(set(rows)-{int(k) for k in d['null_by_nq']}))
print('floor10 which',d['null_floor']['10']['which'],'hits',d['null_floor']['10']['hits'],'distinct',d['null_floor']['10']['distinct_texts'])
