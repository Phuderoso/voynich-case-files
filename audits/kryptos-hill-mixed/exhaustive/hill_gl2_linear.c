/* Independent method #2 (no SAT, no search over sigma): for each of the 157,248 M in
   GL2(Z/26), the crib equations sigma(p) - M sigma(c) = 0 are a HOMOGENEOUS LINEAR system
   in the unknown letter numbers. Solve its kernel exactly over GF(2) and GF(13), combine by
   CRT, and keep kernel vectors that are injective on the crib letters (a bijection A-Z->Z26
   then always extends). Decrypt form; encrypt form = same set via E = M^-1 (GL2 is closed).
   usage: hill_gl2_linear <97-letter ct> <offset>
   -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static const char *CR1="EASTNORTHEAST",*CR2="BERLINCLOCK";
static int np,pc[20][4],var[26],nv,inv_letter[26];
static int unit(int d){return (d&1)&&(d%13);}
static int kernel(int p,int rows,int A[][26],int K[][26]){ /* returns dim, basis in K */
  int R[24][26]; memcpy(R,A,sizeof(int)*24*26); int piv[26],pr=0; for(int j=0;j<nv;j++)piv[j]=-1;
  for(int j=0;j<nv&&pr<rows;j++){int r=-1;for(int i=pr;i<rows;i++)if(R[i][j]%p){r=i;break;} if(r<0)continue;
    for(int k=0;k<nv;k++){int t=R[r][k];R[r][k]=R[pr][k];R[pr][k]=t;}
    int iv=1; while((R[pr][j]*iv)%p!=1)iv++; for(int k=0;k<nv;k++)R[pr][k]=(R[pr][k]*iv)%p;
    for(int i=0;i<rows;i++)if(i!=pr&&R[i][j]%p){int f=R[i][j];for(int k=0;k<nv;k++)R[i][k]=((R[i][k]-f*R[pr][k])%p+p)%p;}
    piv[j]=pr++;}
  int d=0; for(int f=0;f<nv;f++) if(piv[f]<0){ for(int k=0;k<nv;k++)K[d][k]=0; K[d][f]=1;
    for(int j=0;j<nv;j++) if(piv[j]>=0) K[d][j]=((-R[piv[j]][f])%p+p)%p; d++; }
  return d;}
static int A2[24][26],A13[24][26],K2[26][26],K13[26][26];
int main(int ac,char**av){const char*ct=av[1];int off=atoi(av[2]),pt[97];
  for(int i=0;i<97;i++)pt[i]=-1; for(int i=0;i<13;i++)pt[21+i]=CR1[i]-'A'; for(int i=0;i<11;i++)pt[63+i]=CR2[i]-'A';
  for(int L=0;L<26;L++)var[L]=-1;
  for(int i=off;i+1<97;i+=2) if(pt[i]>=0&&pt[i+1]>=0){int q[4]={ct[i]-'A',ct[i+1]-'A',pt[i],pt[i+1]};
    for(int k=0;k<4;k++){if(var[q[k]]<0){inv_letter[nv]=q[k];var[q[k]]=nv++;} pc[np][k]=var[q[k]];} np++;}
  printf("offset=%d pairs=%d crib_letters=%d\n",off,np,nv);
  long nM=0,hits=0,vecs=0; int maxd=0;
  for(int a=0;a<26;a++)for(int b=0;b<26;b++)for(int c=0;c<26;c++)for(int d=0;d<26;d++){
    if(!unit(((a*d-b*c)%26+26)%26))continue; nM++;
    int rows=0; static int E[24][26]; memset(E,0,sizeof E);
    for(int i=0;i<np;i++){ /* p1 - a c1 - b c2 = 0 ; p2 - c c1 - d c2 = 0 (accumulate) */
      E[rows][pc[i][2]]+=1;E[rows][pc[i][0]]-=a;E[rows][pc[i][1]]-=b;rows++;
      E[rows][pc[i][3]]+=1;E[rows][pc[i][0]]-=c;E[rows][pc[i][1]]-=d;rows++;}
    for(int i=0;i<rows;i++)for(int k=0;k<nv;k++){A2[i][k]=((E[i][k]%2)+2)%2;A13[i][k]=((E[i][k]%13)+13)%13;}
    int d2=kernel(2,rows,A2,K2); int d13=kernel(13,rows,A13,K13);
    /* injective mod 26 needs injective mod 2 is impossible for >2 letters... instead combine */
    /* need 2^d2 * 13^d13 small enough: values distinct on nv letters requires nv<=26 ok */
    if(d13==0||d2==0) continue; /* all-equal residues -> not injective for nv>=3 */
    if(d2>maxd)maxd=d2; if(d13>maxd)maxd=d13;
    long n2=1L<<d2, n13=1; for(int t=0;t<d13;t++)n13*=13; if(n2*n13>50000000){printf("BIG M=[%d,%d,%d,%d] d2=%d d13=%d\n",a,b,c,d,d2,d13);continue;}
    static int v2[26],v13[26]; long found=0;
    for(long s2=0;s2<n2;s2++){ for(int k=0;k<nv;k++){int x=0;for(int t=0;t<d2;t++)if(s2>>t&1)x^=K2[t][k];v2[k]=x;}
      /* mod-2 classes: each class needs distinct mod-13 values; need class sizes <=13 */
      int c0=0;for(int k=0;k<nv;k++)c0+=v2[k]; if(c0>13||nv-c0>13)continue;
      for(long s13=0;s13<n13;s13++){ long r=s13; for(int k=0;k<nv;k++)v13[k]=0;
        for(int t=0;t<d13;t++){int co=r%13;r/=13; if(co)for(int k=0;k<nv;k++)v13[k]=(v13[k]+co*K13[t][k])%13;}
        int seen[26]={0},ok=1; for(int k=0;k<nv&&ok;k++){int val=(v2[k]*13+v13[k]*14)%26; if(seen[val])ok=0; seen[val]=1;}
        if(ok){found++; if(found==1){printf("HIT M=[%d,%d,%d,%d] sigma:",a,b,c,d);for(int k=0;k<nv;k++)printf(" %c%d",'A'+inv_letter[k],(v2[k]*13+v13[k]*14)%26);printf("\n");}}}}
    if(found){hits++;vecs+=found;printf("   M=[%d,%d,%d,%d] numberings=%ld (unit-scaling classes=%.2f)\n",a,b,c,d,found,found/12.0);}
  }
  printf("RESULT invertible_M=%ld consistent_M=%ld numberings=%ld max_kernel_dim=%d\n",nM,hits,vecs,maxd);return 0;}
