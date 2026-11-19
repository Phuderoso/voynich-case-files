/* pi217x.c — Voynich's independent blind re-implementation of PREREG217 Part A (pi stream only).
   Written from PREREG217/PREREG214 text only (gn217.c / check217.py NOT opened).
   Model Q: plaintext p at position i (0-idx), layer letter carved at S[i]; key index t = i (ix0) or S[i] (ix1).
   Forms: Vig c=Y[x(p)+k], variant c=Y[x(p)-k], Beaufort c=Y[k-x(p)]  (x,y = positions in X,Y).
   Hit iff >= 23 of 24 crib seats agree. Exhaustive via two 4-seat blocks (seats 1-4, 14-17; any cell with <=1
   wrong seat has one block fully right); a cell whose block A is fully right is only recorded from block A.
   usage: pi217x direct CT alpha.bin windows.bin [yslice_mod yslice_res]
          pi217x fam CT themed.bin perms.bin windows.bin [row_mod row_res]
   output lines: H mode row dir ix X Y form wid agree */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int P[24], PL[24]; static int CT[97];
static int SIG[3]={1,1,-1}, TAU[3]={1,-1,1};
static int md(int a){a%=26; return a<0?a+26:a;}
static unsigned char *rd(const char*f,long*n){FILE*F=fopen(f,"rb"); if(!F){perror(f);exit(1);} fseek(F,0,2);*n=ftell(F);rewind(F);
  unsigned char*b=malloc(*n); if(fread(b,1,*n,F)!=(size_t)*n)exit(2); fclose(F); return b;}
static int blk[2][4]={{0,1,2,3},{13,14,15,16}};
int main(int argc,char**argv){
  const char*cr="EASTNORTHEASTBERLINCLOCK"; for(int j=0;j<13;j++)P[j]=21+j; for(int j=0;j<11;j++)P[13+j]=63+j;
  for(int j=0;j<24;j++)PL[j]=cr[j]-'A';
  if(argc<5){fprintf(stderr,"usage\n");return 1;}
  const char*ct=argv[2]; if(strlen(ct)!=97){fprintf(stderr,"CT len\n");return 1;} for(int i=0;i<97;i++)CT[i]=ct[i]-'A';
  int direct=!strcmp(argv[1],"direct");
  long na; unsigned char*A=rd(argv[3],&na); int NA=na/26;
  static int INV_dummy; (void)INV_dummy;
  unsigned char*INV=malloc(na); for(int a=0;a<NA;a++)for(int m=0;m<26;m++)INV[a*26+A[a*26+m]]=m;  /* INV[a][letter]=position */
  long nw; unsigned char*W; long long found=0;
  if(direct){
    W=rd(argv[4],&nw); int NW=nw/97; int ym=argc>6?atoi(argv[5]):1, yr=argc>6?atoi(argv[6]):0;
    for(int b=0;b<2;b++){
      /* Y table keyed by y(c_j) on block seats (S=identity) */
      int KEYS=456976; int*cnt=calloc(KEYS+1,sizeof(int)); int*lst=malloc(sizeof(int)*NA); int*key=malloc(sizeof(int)*NA);
      for(int y=0;y<NA;y++){ if(y%ym!=yr){key[y]=-1;continue;} int k=0; for(int m=3;m>=0;m--)k=k*26+INV[y*26+CT[P[blk[b][m]]]]; key[y]=k; cnt[k+1]++; }
      for(int k=0;k<KEYS;k++)cnt[k+1]+=cnt[k]; int*pos=malloc(sizeof(int)*(KEYS+1)); memcpy(pos,cnt,sizeof(int)*(KEYS+1));
      for(int y=0;y<NA;y++) if(key[y]>=0) lst[pos[key[y]]++]=y;
      #pragma omp parallel for schedule(dynamic,64) reduction(+:found)
      for(int x=0;x<NA;x++){ int xv[24]; for(int j=0;j<24;j++)xv[j]=INV[x*26+PL[j]];
        for(int f=0;f<3;f++) for(int w=0;w<NW;w++){ const unsigned char*kw=W+(long)w*97; int k=0;
          for(int m=3;m>=0;m--){int j=blk[b][m]; k=k*26+md(SIG[f]*xv[j]+TAU[f]*kw[P[j]]);}
          for(int q=cnt[k];q<cnt[k+1];q++){ int y=lst[q]; int ag=0, agA=0;
            for(int j=0;j<24;j++){ int ok = INV[y*26+CT[P[j]]]==md(SIG[f]*xv[j]+TAU[f]*kw[P[j]]); ag+=ok; if(j<4)agA+=ok; }
            if(ag>=23 && !(b==1 && agA==4)){
              #pragma omp critical
              printf("H direct -1 0 0 %d %d %d %d %d\n",x,y,f,w,ag);
              found++; } } } }
      free(cnt);free(lst);free(key);free(pos);
    }
  } else {
    long np; unsigned short*R=(unsigned short*)rd(argv[4],&np); int NR=np/(97*2);
    W=rd(argv[5],&nw); int NW=nw/97; int rm=argc>7?atoi(argv[6]):1, rr=argc>7?atoi(argv[7]):0;
    #pragma omp parallel for schedule(dynamic,16) reduction(+:found)
    for(int r=0;r<NR;r++){ if(r%rm!=rr)continue;
      uint64_t*bits=calloc(456976/64+1,8); int*wk=malloc(sizeof(int)*NW); int*ord=malloc(sizeof(int)*NW);
      for(int d=0;d<2;d++){ int S[97]; const unsigned short*row=R+(long)r*97;
        if(d==0) for(int i=0;i<97;i++)S[i]=row[i]; else for(int i=0;i<97;i++)S[row[i]]=i;
        int c[24]; for(int j=0;j<24;j++)c[j]=CT[S[P[j]]];
        for(int ix=0;ix<2;ix++){ int t[24]; for(int j=0;j<24;j++)t[j]= ix? S[P[j]] : P[j];
          for(int b=0;b<2;b++){
            memset(bits,0,(456976/64+1)*8);
            for(int w=0;w<NW;w++){int k=0; for(int m=3;m>=0;m--)k=k*26+W[(long)w*97+t[blk[b][m]]]; wk[w]=k; bits[k>>6]|=1ULL<<(k&63);}
            for(int x=0;x<NA;x++){ int xv[24]; for(int j=0;j<24;j++)xv[j]=INV[x*26+PL[j]];
              for(int y=0;y<NA;y++){ int yv[24]; for(int j=0;j<24;j++)yv[j]=INV[y*26+c[j]];
                for(int f=0;f<3;f++){ int k=0;
                  /* y = SIG*x + TAU*k  ->  k = TAU*(y - SIG*x) */
                  for(int m=3;m>=0;m--){int j=blk[b][m]; k=k*26+md(TAU[f]*(yv[j]-SIG[f]*xv[j]));}
                  if(!((bits[k>>6]>>(k&63))&1))continue;
                  for(int w=0;w<NW;w++){ if(wk[w]!=k)continue; const unsigned char*kw=W+(long)w*97; int ag=0,agA=0;
                    for(int j=0;j<24;j++){int ok= yv[j]==md(SIG[f]*xv[j]+TAU[f]*kw[t[j]]); ag+=ok; if(j<4)agA+=ok;}
                    if(ag>=23 && !(b==1&&agA==4)){
                      #pragma omp critical
                      printf("H fam %d %d %d %d %d %d %d %d\n",r,d,ix,x,y,f,w,ag);
                      found++; } } } } } } } }
      free(bits);free(wk);free(ord);
    }
  }
  fprintf(stderr,"END found=%lld\n",found); return 0; }
