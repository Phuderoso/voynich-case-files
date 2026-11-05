"""C026 post-hoc sensitivity (NOT pre-registered; disclosed as such): the C021 loader deletes IVTFF markup with
re.sub('<[^>]*>', ''), so '<->' (text interrupted by a drawing) fuses the words on either side. VCAT's ERRATA E-002
(github.com/noah-chelednik/voynich-data) documents the same defect in their 0.2.3 release. Here '<->' is turned into a
word space before loading and the three C026 looks are rerun with the same seed and gates.
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, random, time, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import c021_bifolium_vocab as T
import c026_transcription_replication as C

def fixed(path):
    tmp = tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt')
    tmp.write(open(path, encoding='utf-8', errors='replace').read().replace('<->', '.')); tmp.close(); return tmp.name

t0 = time.time(); rng = random.Random(C.SEED); R = {'alpha_per_look': C.ALPHA, 'note': "post-hoc: '<->' read as word space"}
it = T.leaves(fixed('data/IT2a-n.txt')); zp = C.leaves_paragraph_only(fixed('data/ZL3b-n.txt'))
for name, fn, data in [('IT_C023', C.look_c023, it), ('ZLpara_C023', C.look_c023, zp), ('IT_C021B', C.look_c021b, it)]:
    R[name] = fn(*data, rng); print(name, R[name], round(time.time() - t0, 1), 's', flush=True)
# the original ZL-based C023 statistic, same fix
zl = T.leaves(fixed('data/ZL3b-n.txt'))
R['ZL_C023'] = C.look_c023(*zl, rng); print('ZL_C023', R['ZL_C023'], flush=True)
json.dump(R, open('analysis/C026_posthoc_drawing_breaks.json', 'w'), indent=1)
