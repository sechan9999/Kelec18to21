"""18대 뉴스타파(선관위) 분류기 운영결과(구·시·군 251행) vs data18 대조"""
import pandas as pd, numpy as np, openpyxl
N = pd.read_pickle('nec18.pkl')
wv = openpyxl.load_workbook('k18to21_수정본.xlsx', data_only=True)['data18']
h = [c.value for c in wv[1]]; D = pd.DataFrame([[c.value for c in wv[r]] for r in range(2, 251)], columns=h); D['row'] = range(2, 251)
SH = {'대전광역시': '대전', '부산광역시': '부산', '서울시': '서울', '세종시': '세종', '울산시': '울산', '인천광역시': '인천', '전라남도': '전남', '전라북도': '전북', '제주도': '제주', '충청남도': '충남', '충청북도': '충북'}
D['시도'] = D.region2.map(lambda s: SH.get(s, s)); D['구'] = D.district.replace({'진구': '부산진구', '울산남구': '남구', '울산동구': '동구', '울산북구': '북구', '울산울주군': '울주군', '울산중구': '중구'})
N2 = N.copy(); N2['구'] = N2.구시군명.where(~N2.구시군명.str.startswith('부천시'), '부천시'); N2['시도'] = N2.시도명
num = [c for c in N.columns[3:30]]
N2 = N2.groupby(['시도', '구'], as_index=False)[num].sum()
m = D.merge(N2, on=['시도', '구'], how='outer', indicator=True); print(m._merge.value_counts().to_dict())
print(m[m._merge != 'both'][['시도', '구', 'district']].to_string())
m = m[m._merge == 'both'].copy()
P = [('P1', '분류_박근혜'), ('M1', '분류_문재인'), ('P2', '미분류_박근혜'), ('M2', '미분류_문재인'), ('U2', '미분류_무효'), ('vote_all', '분류기개표_계'), ('U_all', '미분류_계')]
for a, b in P:
    d = m[a].astype(float) - m[b]; print(f'{a:8s} vs {b:10s} 일치 {int((d == 0).sum())}/{len(m)} 차이합 {int(d.sum())}')
d = m.U_all.astype(float) - m.미분류_계; print(m.loc[d != 0, ['district', 'U_all', '미분류_계', '미분류_기타후보', 'U2']].head(8).to_string())
m.to_pickle('nec18_merge.pkl')
