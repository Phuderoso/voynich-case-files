#!/bin/bash
# my run of the PREREG230 invocations (own outputs in ./out). From /workspace/k230-bsk-recount: setsid timeout 1500 bash run_mine.sh
cd /workspace/k230-bsk-recount/w; export OMP_NUM_THREADS=8; B=../bsk230; O=../out; K4=$(cat ../kryptos-main/data/cycle230/k4.txt); s=$(date +%s)
t(){ echo "$1 $(( $(date +%s)-s ))s $(date +%H:%M:%S)" >> $O/time.txt; }
t start
i=0; while read SH; do
  [ -s $O/null${i}_all.txt ] || { $B $SH x alpha.bin 1 0 20 $i 100000 10 6 > $O/null${i}_direct.txt; $B $SH bank.bin themed144.bin 20 $((2*i)) 1 0 100000 10 6 > $O/null${i}_bank.txt; $B $SH all.bin themed144.bin 20 $((2*i)) 1 0 100000 10 6 > $O/null${i}_all.txt; t null$i; }
  i=$((i+1)); done < ../nulls230_mine.txt
$B $K4 bank.bin themed144.bin 1 0 1 0 100000 10 6 > $O/k4_bank.txt; t k4bank
$B $K4 all.bin themed144.bin 1 0 1 0 100000 10 6 > $O/k4_all.txt; t k4all
$B $K4 x alpha.bin 1 0 1 0 100000 10 6 > $O/k4_direct.txt; t k4direct
t end
