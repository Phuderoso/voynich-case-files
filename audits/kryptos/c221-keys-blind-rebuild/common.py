S=('KRYPTOS PALIMPSEST ABSCISSA BERLINCLOCK EASTNORTHEAST BERLIN CLOCK NORTHEAST SHADOW LUCID MEMORY IQLUSION UNDERGRUUND '
   'DESPARATLY LAYERTWO IDBYROWS XLAYERTWO VIRTUALLY INVISIBLE SANBORN SCHEIDT WEBSTER LANGLEY CIA EGYPT CARTER TUTANKHAMUN '
   'CANDLE WORLDCLOCK WELTZEITUHR MENGENLEHREUHR HEXINSIDEHEX 385765N77844W').split()+['38 57 6.5 N 77 8 44 W','KRYPTOSABCDEFGHIJLMNQUVWXZ']+\
  'VIRTUALLYINVISIBLE SHADOWFORCES LUCIDMEMORY DIGETALINTERPRETATIU TISYOURPOSITION SOS RQ'.split()
MORSE={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..',
'M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--',
'Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',
'.':'.-.-.-'}
# ITA2, bits listed b1..b5
ITA_L={'A':'11000','B':'10011','C':'01110','D':'10010','E':'10000','F':'10110','G':'01011','H':'00101','I':'01100','J':'11010',
'K':'11110','L':'01001','M':'00111','N':'00110','O':'00011','P':'01101','Q':'11101','R':'01010','S':'10100','T':'00001','U':'11100',
'V':'01111','W':'11001','X':'10111','Y':'10101','Z':'10001',' ':'00100'}
FIGROW={'1':'Q','2':'W','3':'E','4':'R','5':'T','6':'Y','7':'U','8':'I','9':'O','0':'P','.':'M'}
FIGS='11011'; LTRS='11111'
def ita_bits(s):
    out=[]; mode='L'
    for c in s:
        if c==' ': out.append(ITA_L[' ']); continue
        if c in FIGROW:
            if mode!='F': out.append(FIGS); mode='F'
            out.append(ITA_L[FIGROW[c]])
        else:
            if mode!='L': out.append(LTRS); mode='L'
            out.append(ITA_L[c])
    return out
def b2i(b,lsb_first):  # b is b1..b5 string
    return sum(int(x)<<i for i,x in enumerate(b)) if lsb_first else int(b,2)
def cyc(v,o): L=len(v); return bytes(v[(o+t)%L]%26 for t in range(97))
def all_off(v): return [cyc(v,o) for o in range(len(v))]
def regroup(bits,g):
    M=len(bits); res=[]
    for o in range(M):
        res.append(bytes(int(''.join(bits[(o+g*t+j)%M] for j in range(g)),2)%26 for t in range(97)))
    return res
