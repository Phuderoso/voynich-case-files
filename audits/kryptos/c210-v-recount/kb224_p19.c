/* Cycle 224 (PREREG224, I-323): typewriter keyboard ciphers, one crib error tolerated.
   Transposition model as cases 200-208: layer letter at plaintext position i is carved at S[i]; S = row (dir 0) or inverse (dir 1);
   'x' = identity. Crib seats POS (0-based 21-33, 63-73). Carved letter at seat j: C[cp[j]].
   G: keyboard row / colA / colB preserving substitution, any key: hit <=> <= 1 seat whose carved letter is outside the crib letter's class.
   V: vector shift on the (row, colA) 3x10 torus, key (dr,dc) per residue class, periodic p 1-24, key index ix 0 = POS[j], ix 1 = cp[j].
   Q: c = Y[x+k] (f0 Vig) / Y[x-k] (f1 variant) / Y[k-x] (f2 Beaufort); X,Y in kb224.bin (18), pairs with both in {AZ,KA} skipped.
   errors(p) = sum over residue classes (n - max multiplicity); hit <=> errors <= 1. Primitive p = hit at p and at no proper divisor.
   usage: kb224 CT perms.bin|x kb224.bin geo224.txt rowstride rowoff models(GVQ) maxprint maxprintp [qg.bin]
   With qg.bin (float32 26^4 log10 quadgrams): every V / Q hit is decrypted with its crib-derived key (majority per residue class,
   '?' where no seat) and scored (mean over quadgrams without '?'); 'C' lines = known >= 49 and score >= -6.0; 'B' = best per model/p.
   output: 'H ...' lines (hits with primitive p <= maxprintp, at most maxprint), 'S model p hits exact prim' lines, 'T ...' line. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N 97
#define NP 24
static const char *C1="EASTNORTHEAST",*C2="BERLINCLOCK";
static int POS[24],PT[24];
static int nA; static unsigned char A[32][26],AI[32][26];
static int GEO[4][26][3];
/* groups per p: seat order and sizes (non-singleton only) */
typedef struct { int ng; int sz[24]; int st[24]; int seat[24]; } Grp;
static void mkgrp(const int*t,int p,Grp*g){ int used[24]={0}; g->ng=0; int k=0;
  for(int a=0;a<24;a++){ if(used[a])continue; int s=0,st=k; for(int b=a;b<24;b++) if(!used[b] && t[b]%p==t[a]%p){used[b]=1; g->seat[k++]=b; s++;}
    if(s>=2){ g->st[g->ng]=st; g->sz[g->ng]=s; g->ng++; } else k--; } }
static inline int errs(const Grp*g,const int*v){ int e=0;
  for(int q=0;q<g->ng;q++){ int s=g->sz[q]; const int*sd=g->seat+g->st[q];
    if(s==2){ e+= v[sd[0]]!=v[sd[1]]; }
    else { int mx=1; for(int a=0;a<s;a++){int m=0; for(int b=0;b<s;b++) m+= v[sd[a]]==v[sd[b]]; if(m>mx)mx=m;} e+=s-mx; }
    if(e>1) return 2; }
  return e; }
static unsigned char* rd(const char*fn,long*n,int rec){FILE*f=fopen(fn,"rb");if(!f){perror(fn);exit(1);}fseek(f,0,SEEK_END);long s=ftell(f);rewind(f);
  unsigned char*b=malloc(s);if(fread(b,1,s,f)!=(size_t)s)exit(1);fclose(f);*n=s/rec;return b;}
static long long SH[3][NP+1][3]; /* model, p, {hits, exact, prim} ; G uses p index = partition*4+layout (0..11) */
static long long printed=0, maxprint, maxpp;
static float *QG=NULL; static double BEST[3][NP+1]; static long long NCAND[3][NP+1];
static void score_hit(int model,const int*C,const int*S,int ix,int p,const int*t,const int*v,int lay,int x,int y,int f,const char*cfg){
  int kv[NP],kc[NP]; for(int r=0;r<p;r++){kv[r]=-1;kc[r]=0;}
  for(int j=0;j<24;j++){ int r=t[j]%p, m=0; for(int b=0;b<24;b++) if(t[b]%p==r && v[b]==v[j]) m++; if(m>kc[r]){kc[r]=m;kv[r]=v[j];} }
  char out[N+1]; int known=0;
  for(int i=0;i<N;i++){ int r=(ix==0?i:S[i])%p, c=C[S[i]]; out[i]='?'; if(kv[r]<0) continue;
    if(model==1){ int tr=(GEO[lay][c][0]-kv[r]/10+3)%3, tc=(GEO[lay][c][1]-kv[r]%10+10)%10; for(int z=0;z<26;z++) if(GEO[lay][z][0]==tr&&GEO[lay][z][1]==tc){out[i]='A'+z;known++;break;} }
    else { int yv=AI[y][c], k=kv[r]; int xv= f==0?(yv-k+26)%26: f==1?(yv+k)%26:(k-yv+26)%26; out[i]='A'+A[x][xv]; known++; } }
  out[N]=0; double sm=0; int nq=0;
  for(int i=0;i+3<N;i++){ if(out[i]=='?'||out[i+1]=='?'||out[i+2]=='?'||out[i+3]=='?') continue; sm+=QG[(((out[i]-65)*26+out[i+1]-65)*26+out[i+2]-65)*26+out[i+3]-65]; nq++; }
  double sc= nq? sm/nq : -99;
  if(sc>BEST[model][p]){
    #pragma omp critical
    { if(sc>BEST[model][p]){ BEST[model][p]=sc; printf("B %s p=%d known=%d qg=%.3f pt=%s\n",cfg,p,known,sc,out);} } }
  if(known>=49 && sc>=-6.0){
    #pragma omp critical
    { NCAND[model][p]++; printf("C %s p=%d known=%d qg=%.3f pt=%s\n",cfg,p,known,sc,out);} } }
static void rec(int model,int p,int e,int prim){ 
  #pragma omp atomic
  SH[model][p][0]++;
  if(e==0){
  #pragma omp atomic
  SH[model][p][1]++;}
  if(prim){
  #pragma omp atomic
  SH[model][p][2]++;} }
int main(int argc,char**argv){
  if(argc<10){fprintf(stderr,"usage\n");return 1;}
  int C[N]; for(int i=0;i<N;i++)C[i]=argv[1][i]-'A';
  for(int j=0;j<13;j++){POS[j]=21+j;PT[j]=C1[j]-'A';} for(int j=0;j<11;j++){POS[13+j]=63+j;PT[13+j]=C2[j]-'A';}
  long na; unsigned char*KB=rd(argv[3],&na,26); nA=na; for(int a=0;a<nA;a++)for(int i=0;i<26;i++){A[a][i]=KB[a*26+i];AI[a][KB[a*26+i]]=i;}
  FILE*gf=fopen(argv[4],"r"); for(int l=0;l<4;l++){char nm[32]; if(fscanf(gf,"%31s",nm)!=1)exit(1); for(int x=0;x<26;x++) if(fscanf(gf," %d,%d,%d",&GEO[l][x][0],&GEO[l][x][1],&GEO[l][x][2])!=3)exit(1);} fclose(gf);
  int rs=atoi(argv[5]),ro=atoi(argv[6]); const char*models=argv[7]; maxprint=atol(argv[8]); maxpp=atol(argv[9]);
  for(int m=0;m<3;m++)for(int p=0;p<=NP;p++)BEST[m][p]=-99;
  if(argc>10){ long nq; QG=(float*)rd(argv[10],&nq,4); if(nq!=26*26*26*26){fprintf(stderr,"qg size\n");return 1;} }
  int doG=!!strchr(models,'G'),doV=!!strchr(models,'V'),doQ=!!strchr(models,'Q');
  int direct=!strcmp(argv[2],"x"); long np=1; short*Perm=NULL; if(!direct){long b; Perm=(short*)rd(argv[2],&b,2*N); np=b;}
  int AZ=nA-2,KA=nA-1;
  long long rows=0,cfgV=0,cfgQ=0;
  Grp G0[NP+1]; for(int p=1;p<=NP;p++) mkgrp(POS,p,&G0[p]);
  #pragma omp parallel for schedule(dynamic,64) reduction(+:rows,cfgV,cfgQ)
  for(long q=ro;q<np;q+=rs){ int cp[24],cc[24],SF[N];
    if(direct){ for(int j=0;j<24;j++){cp[j]=POS[j];} for(int i=0;i<N;i++)SF[i]=i; }
    rows++;
    for(int dir=0;dir<(direct?1:2);dir++){
      if(!direct){ short*P=Perm+q*N; int inv[N]; for(int i=0;i<N;i++)inv[P[i]]=i; for(int i=0;i<N;i++) SF[i]= dir==0?P[i]:inv[i]; for(int j=0;j<24;j++) cp[j]=SF[POS[j]]; }
      for(int j=0;j<24;j++) cc[j]=C[cp[j]];
      long qq= direct?-1:q;
      if(doG) for(int m=0;m<3;m++) for(int l=0;l<4;l++){ int e=0; for(int j=0;j<24;j++) e+= GEO[l][cc[j]][m]!=GEO[l][PT[j]][m];
        if(e<=1){ rec(0,m*4+l,e,1);
          #pragma omp critical
          { if(printed<maxprint){printed++; printf("H G perm=%ld dir=%d part=%d lay=%d err=%d\n",qq,dir,m,l,e);} } } }
      Grp G1[NP+1]; if(doV||doQ){ if(!direct) for(int p=1;p<=NP;p++) mkgrp(cp,p,&G1[p]); }
      for(int ix=0;ix<(direct?1:2);ix++){ Grp*GG= (ix==0||direct)?G0:G1;
        if(doV) for(int l=0;l<4;l++){ int v[24]; cfgV++;
          for(int j=0;j<24;j++){ int dr=(GEO[l][cc[j]][0]-GEO[l][PT[j]][0]+3)%3, dc=(GEO[l][cc[j]][1]-GEO[l][PT[j]][1]+10)%10; v[j]=dr*10+dc; }
          int hm=0,ee[NP+1]; for(int p=1;p<=NP;p++){ ee[p]=errs(&GG[p],v); if(ee[p]<=1) hm|=1<<p; }
          if(hm) for(int p=1;p<=NP;p++) if(hm>>p&1){ int prim=1; for(int d=1;d<p;d++) if(p%d==0 && (hm>>d&1)) prim=0; rec(1,p,ee[p],prim);
            if(QG){ char cfg[96]; snprintf(cfg,96,"V perm=%ld dir=%d ix=%d lay=%d",qq,dir,ix,l); score_hit(1,C,SF,ix,p,(ix==0||direct)?POS:cp,v,l,0,0,0,cfg); }
            if(prim && p<=maxpp){
            #pragma omp critical
            { if(printed<maxprint){ printed++;
                /* Voynich recount: also emit the crib-derived plaintext for p=19 V hits. */
                char out[N+1]; int known=0;
                if(p==19){
                  const int*t=(ix==0||direct)?POS:cp;
                  int kv[NP],kc[NP]; for(int r=0;r<p;r++){kv[r]=-1;kc[r]=0;}
                  for(int j=0;j<24;j++){ int r=t[j]%p, m=0; for(int b=0;b<24;b++) if(t[b]%p==r && v[b]==v[j]) m++; if(m>kc[r]){kc[r]=m;kv[r]=v[j];} }
                  for(int i=0;i<N;i++){ int r=(ix==0?i:SF[i])%p, c=C[SF[i]]; out[i]='?'; if(kv[r]<0) continue;
                    int tr=(GEO[l][c][0]-kv[r]/10+3)%3, tc=(GEO[l][c][1]-kv[r]%10+10)%10;
                    for(int z=0;z<26;z++) if(GEO[l][z][0]==tr&&GEO[l][z][1]==tc){out[i]='A'+z;known++;break;} }
                  out[N]=0;
                } else { out[0]=0; }
                printf("H V perm=%ld dir=%d ix=%d lay=%d p=%d err=%d known=%d pt=%s\n",qq,dir,ix,l,p,ee[p],known,out);
              } } } } }
        if(doQ) for(int x=0;x<nA;x++) for(int y=0;y<nA;y++){ if((x==AZ||x==KA)&&(y==AZ||y==KA)) continue;
          int xp[24],yc[24]; for(int j=0;j<24;j++){xp[j]=AI[x][PT[j]]; yc[j]=AI[y][cc[j]];}
          for(int f=0;f<3;f++){ int k[24]; cfgQ++;
            for(int j=0;j<24;j++) k[j]= f==0?(yc[j]-xp[j]+26)%26: f==1?(xp[j]-yc[j]+26)%26:(yc[j]+xp[j])%26;
            int hm=0,ee[NP+1]; for(int p=1;p<=NP;p++){ ee[p]=errs(&GG[p],k); if(ee[p]<=1) hm|=1<<p; }
            if(hm) for(int p=1;p<=NP;p++) if(hm>>p&1){ int prim=1; for(int d=1;d<p;d++) if(p%d==0 && (hm>>d&1)) prim=0; rec(2,p,ee[p],prim);
              if(QG){ char cfg[96]; snprintf(cfg,96,"Q perm=%ld dir=%d ix=%d X=%d Y=%d form=%d",qq,dir,ix,x,y,f); score_hit(2,C,SF,ix,p,(ix==0||direct)?POS:cp,k,-1,x,y,f,cfg); }
              if(prim && p<=maxpp){
              #pragma omp critical
              { if(printed<maxprint){printed++; printf("H Q perm=%ld dir=%d ix=%d X=%d Y=%d form=%d p=%d err=%d\n",qq,dir,ix,x,y,f,p,ee[p]);} } } } } } } } }
  for(int m=0;m<12;m++) if(doG) printf("S G part=%d lay=%d hits=%lld exact=%lld\n",m/4,m%4,SH[0][m][0],SH[0][m][1]);
  for(int p=1;p<=NP;p++){ if(doV) printf("S V p=%d hits=%lld exact=%lld prim=%lld\n",p,SH[1][p][0],SH[1][p][1],SH[1][p][2]);
                          if(doQ) printf("S Q p=%d hits=%lld exact=%lld prim=%lld\n",p,SH[2][p][0],SH[2][p][1],SH[2][p][2]); }
  if(QG) for(int m=1;m<3;m++) for(int p=1;p<=NP;p++) printf("N model=%c p=%d best=%.3f cand=%lld\n","GVQ"[m],p,BEST[m][p],NCAND[m][p]);
  printf("T rows=%lld cfgV=%lld cfgQ=%lld printed=%lld\n",rows,cfgV,cfgQ,printed);
  return 0; }
