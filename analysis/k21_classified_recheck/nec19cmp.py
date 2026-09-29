"""19대 선관위 분류기 통계(구·시·군) vs data19 대조"""
import openpyxl, pandas as pd, numpy as np
g=pd.read_pickle('nec19.pkl')
wv=openpyxl.load_workbook('k18to21_수정본.xlsx',data_only=True)['data19']
h=[c.value.strip() if isinstance(c.value,str) else c.value for c in wv[1]]
D=pd.DataFrame([[c.value for c in wv[r]] for r in range(2,251)],columns=h); D['row']=range(2,251)
SH={'강원도':'강원','경기도':'경기','경상남도':'경남','경상북도':'경북','광주광역시':'광주','대구광역시':'대구','대전광역시':'대전','부산광역시':'부산','서울시':'서울','세종시':'세종','울산시':'울산','인천광역시':'인천','전라남도':'전남','전라북도':'전북','제주도':'제주','충청남도':'충남','충청북도':'충북','경기도 부천시 (4119000000)':'경기'}
D['시도']=D.region2.map(SH)
D['구']=D.district.replace({'여주군':'여주시','진구':'부산진구','청원군':'청주시청원구','울산남구':'남구','울산동구':'동구','울산북구':'북구','울산울주군':'울주군','울산중구':'중구'})
g2=g.copy(); g2.loc[g2.구=='청주시서원구','구']='청주시흥덕구'
num=[c for c in g2.columns if c[0] in 'TCU' and c!='투표구']
g2=g2.groupby(['시도','구'],as_index=False)[num].sum()
m=D.merge(g2,on=['시도','구'],how='outer',indicator=True); print(m._merge.value_counts().to_dict()); print(m[m._merge!='both'][['시도','구','district']].to_string())
m=m[m._merge=='both'].copy()
P=[('M1','C문'),('H1','C홍'),('D1','C안'),('M2','U문'),('H2','U홍'),('D2','U안'),('U2','U무효'),('vote_all','T계'),('U_all','U계')]
for a,b in P:
    d=(m[a].astype(float)-m[b]); print(f'{a:8s} vs {b:5s} 일치 {int((d==0).sum())} / {len(m)}  차이합 {int(d.sum())}')
bad=m[np.any([m[a].astype(float)!=m[b] for a,b in P],axis=0)]
print(bad[['시도','district']+[x for a,b in P[:7] for x in (a,b)]].to_string())
m.to_pickle('nec19_merge.pkl')
