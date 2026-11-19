# Regenerate PREREG219 nulls: random.Random(seed).shuffle of the K4 letter list, seeds 209234-209241.
import random,sys,hashlib
k4=open(sys.argv[1]).read().strip()
assert len(k4)==97
pub="OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"  # public K4 transcription
print("anchor K4 == public transcription:",k4==pub, file=sys.stderr)
out=["K4\t"+k4]
for s in range(209234,209242):
    l=list(k4); random.Random(s).shuffle(l); out.append(f"null{s}\t"+"".join(l))
open("inputs/texts_mine.tsv","w").write("\n".join(out)+"\n")
