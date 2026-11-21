#!/bin/bash
# my run of the PREREG231 invocations + replica (own outputs in ./out). From /workspace/vc231: setsid bash run_mine.sh
cd /workspace/vc231/w; export OMP_NUM_THREADS=8; B=../bsk230; mkdir -p ../out/fresh ../out/replica ../out/plants; s=$(date +%s)
t(){ echo "$1 $(( $(date +%s)-s ))s $(date +%H:%M:%S)" >> ../out/time.txt; }
t start
# gate P: plants from her plants231.tsv (an input; hash 11f93579), same invocations as run231.sh
while IFS=$'\t' read id fam q d xi yi form typ size ct pt; do
  if [ $fam = direct ]; then $B $ct x alpha.bin 1 0 86731 $xi 100000 10 6 > ../out/plants/$id.txt
  else nr=$([ $fam = bank ] && echo 165065 || echo 165782); a=$(( q>50 ? q-50 : 0 )); b=$(( q+51<nr ? q+51 : nr ))
    dd if=$fam.bin of=../out/plants/$id.bin bs=194 skip=$a count=$((b-a)) status=none; echo $a > ../out/plants/$id.off
    $B $ct ../out/plants/$id.bin themed144.bin 1 0 1 0 100000 10 6 > ../out/plants/$id.txt; fi
done < ../src/plants231.tsv; t plants
for SET in fresh replica; do
  if [ $SET = fresh ]; then F=../src/nulls231.txt; else F=../nulls_replica.txt; fi
  i=0; while read SH; do
    $B $SH bank.bin themed144.bin 20 $i 1 0 100000 10 6 > ../out/$SET/null${i}_bank.txt
    $B $SH all.bin themed144.bin 20 $i 1 0 100000 10 6 > ../out/$SET/null${i}_all.txt
    t ${SET}BA$i; i=$((i+1)); done < $F
  i=0; while read SH; do
    if [ $i -lt 8 ]; then $B $SH x alpha.bin 1 0 5 $i 100000 10 6 > ../out/$SET/null${i}_direct.txt; t ${SET}D$i; fi
    i=$((i+1)); done < $F
done
t end
