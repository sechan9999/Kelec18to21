"""data18 과 뉴스타파 18대 자료가 다른 곳: 차이가 수개표(부재자 등)와 관련되는지"""
import pandas as pd, numpy as np
m = pd.read_pickle('nec18_merge.pkl')
for a in ['P1', 'M1', 'P2', 'M2', 'vote_all', 'U2']: m[a] = m[a].astype(float)
m['dP1'] = m.P1 - m.분류_박근혜; m['dM1'] = m.M1 - m.분류_문재인; m['dP2'] = m.P2 - m.미분류_박근혜; m['dM2'] = m.M2 - m.미분류_문재인
bad = m[(m[['dP1', 'dM1', 'dP2', 'dM2']] != 0).any(axis=1)]
print('불일치', len(bad), '/', len(m))
print(bad[['시도', 'district', 'dP1', 'dM1', 'dP2', 'dM2', '수개표_박근혜', '수개표_문재인', '분류기개표_박근혜']].head(30).to_string())
print('dP1+dP2 == 수개표_박:', int(((bad.dP1 + bad.dP2) == bad.수개표_박근혜).sum()))
print('P1+P2 == 분류기_박+수개표_박:', int(((bad.P1 + bad.P2) == (bad.분류기개표_박근혜 + bad.수개표_박근혜)).sum()))
print('P1+P2 == 분류기_박:', int(((bad.P1 + bad.P2) == bad.분류기개표_박근혜).sum()))
print('data18 박 합 vs 뉴스타파 분류기 박 합', int((m.P1 + m.P2).sum()), int(m.분류기개표_박근혜.sum()), '| 계_박', int(m.계_박근혜.sum()))
# K 비교
m['K_d'] = (m.P2 / m.M2) / (m.P1 / m.M1); m['K_n'] = (m.미분류_박근혜 / m.미분류_문재인) / (m.분류_박근혜 / m.분류_문재인)
print('K 평균 data18', round(m.K_d.mean(), 4), '뉴스타파', round(m.K_n.mean(), 4), '| 합산', round((m.P2.sum() / m.M2.sum()) / (m.P1.sum() / m.M1.sum()), 4), round((m.미분류_박근혜.sum() / m.미분류_문재인.sum()) / (m.분류_박근혜.sum() / m.분류_문재인.sum()), 4))
m.to_pickle('nec18_merge.pkl')
