#!/bin/bash
# Voynich's run of the PREREG236 invocations (runA.sh / runP.sh semantics), own outputs in ../out. Run from /workspace/vc236/w:
#   setsid bash ../audit/run_mine236.sh PART   (PART = P | K4 | N)   every gn217 call wrapped in 'timeout 600'
export OMP_NUM_THREADS=8; cd /workspace/vc236/w; O=../out; mkdir -p $O/P $O/A; s=$(date +%s)
t(){ echo "$1 $(( $(date +%s)-s ))s $(date +%H:%M:%S)" >> $O/time.txt; }
G(){ timeout 600 ./gn217 "$@"; echo "rc=$?" >&2; }
case $1 in
P) while IFS=$'\t' read -r id scope ct qi dr ix x y f w seat pt; do
     if [ "$scope" = direct ]; then G "$ct" x alpha.bin alpha.bin keys236.bin 1000 $((y%1000)) 100000 > $O/P/p$id.txt
     else G "$ct" $scope.bin themed144.bin themed144.bin keys236.bin 2000 $((qi%2000)) 100000 > $O/P/p$id.txt; fi
   done < plants236.tsv; t P;;
K4) K4=$(cat k4.txt)
   G $K4 x alpha.bin alpha.bin keys236.bin 1 0 100000 > $O/A/k4_direct.txt; t k4_direct
   G $K4 bank.bin themed144.bin themed144.bin keys236.bin 1 0 100000 > $O/A/k4_bank.txt; t k4_bank
   G $K4 all.bin themed144.bin themed144.bin keys236.bin 1 0 100000 > $O/A/k4_all.txt; t k4_all;;
N) while IFS=$'\t' read -r seed tx sha; do
     G $tx x alpha.bin alpha.bin keys236.bin 1 0 100000 > $O/A/null${seed}_direct.txt
     G $tx bank.bin themed144.bin themed144.bin keys236.bin 10 0 100000 > $O/A/null${seed}_bank_r10.txt
     G $tx all.bin themed144.bin themed144.bin keys236.bin 10 0 100000 > $O/A/null${seed}_all_r10.txt; t null$seed
   done < nulls236.tsv;;
esac
