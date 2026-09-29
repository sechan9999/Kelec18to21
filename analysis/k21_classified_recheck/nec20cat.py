"""data20 (분류+미분류) vs 공개 최종득표 유형 분류와 20대 K 민감도"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
S = pd.read_pickle("nec20.pkl"); m = S["m"].copy()
m = m[~((m["index"] == 250) & (m.district_n == "청주시서원구"))]          # data20 흥덕 = 흥덕+서원 → 공개도 합쳐 비교
hd = S["N"][S["N"].district.isin(["청주시서원구", "청주시흥덕구"])][["L1", "Y1"]].sum()
m.loc[m["index"] == 250, ["L1_n", "Y1_n"]] = hd.values
m["dL"] = (m.L1_d + m.L2) - m.L1_n; m["dY"] = (m.Y1_d + m.Y2) - m.Y1_n
m["rel"] = (m.dL.abs() + m.dY.abs()) / (m.L1_n + m.Y1_n)
def cat(r):
    if r.dL == 0 and r.dY == 0: return "A 완전 일치"
    if r.rel < 0.005: return "B 0.5% 미만 차이"
    if r.L1_d == r.L1_n and r.Y1_d == r.Y1_n: return "C 분류 열 = 최종득표 (오산형)"
    if r.L1_d + r.Y1_d == r.vote_all_d: return "D 분류 합 = 총투표 (제천형)"
    return "E 0.5% 이상 차이"
m["cat"] = m.apply(cat, axis=1); print(m.cat.value_counts().sort_index().to_dict())
print(m[m.cat.str[0].isin(["C", "D", "E"])][["index", "district_d", "L1_d", "L2", "L1_n", "dL", "Y1_d", "Y2", "Y1_n", "dY", "rel", "cat"]].sort_values("rel", ascending=False).round(3).to_string(index=False))
# 민감도: 현재 논문 기준(오산 복원, 제천 제외) vs E·C·D 모두 제외
m["K"] = (m.Y2 / m.L2) / (m.Y1_d / m.L1_d)
o = m.district_d == "오산시"; m.loc[o, "Y1_d"] = m.loc[o, "Y1_n"] - m.loc[o, "Y2"]; m.loc[o, "L1_d"] = m.loc[o, "L1_n"] - m.loc[o, "L2"]
m["K"] = (m.Y2 / m.L2) / (m.Y1_d / m.L1_d); m["R_1"] = m.Y1_d / (m.Y1_d + m.L1_d); m["R_2"] = m.Y2 / (m.Y2 + m.L2)
for lab, d in [("논문 기준 (오산 복원, 제천 제외)", m[m.district_d != "제천시"]), ("0.5% 이상 차이 모두 제외", m[m.cat.str[0].isin(["A", "B"])]), ("완전 일치만", m[m.cat.str[0] == "A"])]:
    f = smf.ols("R_2 ~ R_1", d).fit()
    print(f"{lab}: n {len(d)}, K 평균 {d.K.mean():.4f}, 중앙값 {d.K.median():.4f}, 합산 {(d.Y2.sum() / d.L2.sum()) / (d.Y1_d.sum() / d.L1_d.sum()):.4f}, 적합 {f.params.Intercept:.4f} + {f.params.R_1:.4f}·R1, R² {f.rsquared:.4f}")
m.to_pickle("nec20_cat.pkl")
