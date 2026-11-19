/* Voynich desk, independent recount for Kryptos PREREG219 Part C (one crib error, columnar w9/w10 x periodic tableau key).
   Written from the PREREG text; conventions (grid, COL/ROW, dir, model, alphabets) matched to the family definition.
   Enumeration: Heap's algorithm over the read order (order[k] = column read k-th); excess computed by full counting.
   usage: v1e CT w label PMAX PPRINT    -> "X" hit lines (excess<=1 and p<=PPRINT, or excess 0) and a "T" totals line. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define L 97
static const char *KRY="KRYPTOSABCDEFGHIJLMNQUVWXZ";
static const char *CRIB1="EASTNORTHEAST", *CRIB2="BERLINCLOCK";
int seat[24]; int ptl[24];
long cnt[23][3];
int main(int argc,char**argv){
  const char*ct=argv[1]; int w=atoi(argv[2]); const char*lab=argv[3]; int PMAX=atoi(argv[4]),PPR=atoi(argv[5]);
  if(strlen(ct)!=L) return 1;
  for(int i=0;i<13;i++){seat[i]=21+i;ptl[i]=CRIB1[i];}
  for(int i=0;i<11;i++){seat[13+i]=63+i;ptl[13+i]=CRIB2[i];}
  int idx[2][128]; for(int i=0;i<26;i++){idx[0]['A'+i]=i; idx[1][(int)KRY[i]]=i;}
  int order[16],c[16]; for(int i=0;i<w;i++){order[i]=i;c[i]=0;}
  int rows=(L+w-1)/w; long nperm=0;
  int k=0;
  while(1){
    nperm++;
    for(int mode=0;mode<2;mode++){
      int pos[L],inv[L],q=0; /* pos[plain cell] = layer position */
      if(mode==1){ for(int a=0;a<w;a++) for(int r=0;r<rows;r++){int cell=r*w+order[a]; if(cell<L) pos[cell]=q++;} }
      else       { for(int r=0;r<rows;r++) for(int a=0;a<w;a++){int cell=r*w+order[a]; if(cell<L) pos[cell]=q++;} }
      for(int i=0;i<L;i++) inv[pos[i]]=i;
      for(int dir=0;dir<2;dir++){
        int cp[24]; for(int t=0;t<24;t++) cp[t]= dir? inv[seat[t]] : pos[seat[t]];
        for(int al=0;al<2;al++) for(int bf=0;bf<2;bf++){
          int kv[24]; for(int t=0;t<24;t++){int x=idx[al][(int)ct[cp[t]]], y=idx[al][ptl[t]]; kv[t]= bf? (x+y)%26 : (x-y+26)%26;}
          for(int model=0;model<2;model++) for(int p=1;p<=PMAX;p++){
            static int h[40][26]; int sz[40]; memset(sz,0,sizeof(int)*p); 
            for(int r=0;r<p;r++) memset(h[r],0,sizeof(h[r]));
            for(int t=0;t<24;t++){int r=(model?cp[t]:seat[t])%p; h[r][kv[t]]++; sz[r]++;}
            int ex=0; for(int r=0;r<p;r++){int m=0; for(int v=0;v<26;v++) if(h[r][v]>m) m=h[r][v]; ex+=sz[r]-m;}
            if(ex>2) ex=2; cnt[p][ex]++;
            if(ex==0 || (ex==1 && p<=PPR)){
              printf("X %s %d %d %d %d %d %d %d %d",lab,w,mode,dir,al,bf,model,p,ex);
              int rank[16]; for(int a=0;a<w;a++) rank[order[a]]=a;  /* rank of column c */
              for(int a=0;a<w;a++) printf(" %d",rank[a]); printf("\n");
            }
          }
        }
      }
    }
    /* Heap's algorithm, iterative */
    while(k<w && c[k]>=k){c[k]=0;k++;}
    if(k>=w) break;
    int sw = (k%2==0)?0:c[k]; int t=order[sw]; order[sw]=order[k]; order[k]=t; c[k]++; k=1;
    if(0) break;
  }
  printf("T %s w%d perms %ld",lab,w,nperm);
  for(int p=1;p<=PMAX;p++) printf(" p%d=%ld/%ld",p,cnt[p][0],cnt[p][1]); printf("\n");
  return 0;
}
