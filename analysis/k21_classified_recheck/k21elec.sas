/* 21대선 (2025) 구·시·군 252개 단위 — 20대 k20elec 코드와 같은 구조
   입력: k21elec.xlsx
     sheet k21elec  : region district index L1 Y1 L2 Y2 R1 R2 K R_1 R_2 R_1sq
     sheet k21class : region district class(선거일/관내사전/관외사전/재외) L1 Y1 L2 Y2 R1 R2 K
   Y = 김문수, L = 이재명, 1 = 분류된 투표지, 2 = 재확인대상
   R1 = Y1/(L1+Y1), R2 = Y2/(L2+Y2), K = R2/R1   (세종은 20대처럼 충청남도 '세종시')  */

%let in_dir  = C:\Users\hmo9\OneDrive - CDC\+My_Documents\DASH\project21;
%let out_dir = &in_dir;

PROC IMPORT out=work.k21elec DATAFILE="&in_dir\k21elec.xlsx" DBMS=xlsx REPLACE;
    SHEET="k21elec"; GETNAMES=YES; DATAROW=2;
RUN;
PROC IMPORT out=work.k21class DATAFILE="&in_dir\k21elec.xlsx" DBMS=xlsx REPLACE;
    SHEET="k21class"; GETNAMES=YES; DATAROW=2;
RUN;

proc contents data=k21elec; run;
proc print data=k21elec (obs=10); run;

/* 1. 선형 회귀: Fit Diagnostics + Fit Plot (20대 그림과 같은 형태) */
ods graphics on;
proc reg data=k21elec plots(label)=(diagnostics fit);
    Model R_2 = R_1;
    id district;
run; quit;

/* 2. 2차 회귀 (r clm cli) */
proc reg data=k21elec;
    Model R_2 = R_1sq R_1 / r clm cli;
    output out=k21_quad p=pred r=resid lclm=lclm uclm=uclm lcl=lcl ucl=ucl rstudent=rstud cookd=cookd;
run; quit;

/* 3. 기울기 = 1 검정 (K 가 R1 과 무관하게 일정한가) */
proc reg data=k21elec;
    Model R_2 = R_1;
    Slope1: test R_1 = 1;
run; quit;

/* 4. 시도별 t-검정: K 는 H0: K = 1 로 */
proc sort data=k21elec; by region; run;
proc ttest data=k21elec h0=1; var K; by region; run;
proc ttest data=k21elec; var R1 R2; by region; run;

/* 5. 투표구분(class)별 */
proc sort data=k21class; by class; run;
proc ttest data=k21class h0=1; var K; by class; run;
proc means data=k21class n mean std stderr clm min max; var K R1 R2; class class; run;

/* 6. 분포표·평균표 → 엑셀 */
proc univariate data=k21elec noprint;
    class region; var K;
    output out=k21elec_dist pctlpts=0 1 5 10 25 50 75 90 95 99 100 pctlpre=P_;
run;
proc export data=k21elec_dist outfile="&out_dir\k21Table_&sysdate..xlsx" DBMS=xlsx label REPLACE; sheet='k21_dist'; run;

proc means data=k21elec noprint; var K R1 R2; class region; output out=k21mean; run;
proc export data=k21mean outfile="&out_dir\k21Table_&sysdate..xlsx" DBMS=xlsx label REPLACE; sheet='k21_mean'; run;

proc univariate data=k21class noprint;
    class class; var K;
    output out=k21class_dist pctlpts=0 1 5 10 25 50 75 90 95 99 100 pctlpre=P_;
run;
proc export data=k21class_dist outfile="&out_dir\k21Table_&sysdate..xlsx" DBMS=xlsx label REPLACE; sheet='kclass_dist'; run;
