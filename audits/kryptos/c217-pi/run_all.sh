#!/bin/bash
cd "$(dirname "$0")"; K4=$(tr -d '\n' < inputs/k4.txt); N0=$(tr -d '\n' < null0.txt); mkdir -p out
for t in k4:$K4 null0:$N0; do n=${t%%:*}; c=${t#*:}
  ( time ./pi217x direct $c inputs/alpha.bin pi_windows.bin ) > out/${n}_direct.txt 2> out/${n}_direct.log
  for fam in bank all; do ( time ./pi217x fam $c inputs/themed144.bin inputs/$fam.bin pi_windows.bin ) > out/${n}_$fam.txt 2> out/${n}_$fam.log; done
done
echo DONE
