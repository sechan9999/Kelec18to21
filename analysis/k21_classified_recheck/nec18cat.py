"""data18 vs 뉴스타파 차이 유형 분류 (nec18cmp.py → nec18diff.py 다음에 실행)"""
import pandas as pd, numpy as np
m = pd.read_pickle('nec18_merge.pkl')
m['sP'] = m.dP1 + m.dP2; m['sM'] = m.dM1 + m.dM2
def cat(r):
    if (r[['dP1', 'dM1', 'dP2', 'dM2']] == 0).all(): return 'A 일치'
    if r.sP == 0 and r.sM == 0: return 'B 분류↔미분류 옮김'
    if r.sP > 0 and r.sM > 0 and r.sP <= r.수개표_박근혜 + 5 and r.sM <= r.수개표_문재인 + 5: return 'C 수개표 일부·전부 포함'
    return 'D 기타'
m['cat'] = m.apply(cat, axis=1); print(len(m), m.cat.value_counts().to_dict())
b = m[m.cat.str.startswith('B')]; print('B 최대 이동', int(b[['dP1', 'dM1']].abs().max().max()))
d = m[m.cat.str.startswith('D')]; print('D 최대', int(d[['dP1', 'dM1', 'dP2', 'dM2']].abs().max().max())); print(d[['시도', 'district', 'dP1', 'dM1', 'dP2', 'dM2']].to_string())
c = m[m.cat.str.startswith('C')]; print('C 포함비율 중앙값', round(float((c.sP / c.수개표_박근혜).median()), 3))
x = pd.read_pickle('pe18_out.pkl')['x'][['index', '박근혜', '문재인']]; y = m.merge(x, on='index')
print('공개 = 뉴스타파 계:', int(((y.박근혜 == y.계_박근혜) & (y.문재인 == y.계_문재인)).sum()), '/', len(y))
m.to_pickle('nec18_merge.pkl')
