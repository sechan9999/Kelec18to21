"""같은 구·시·군 안: log OR 차이(관내사전-선거일)를 두 투표구분의 R1 격차로 설명할 수 있나"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
w = pd.read_pickle("prewide.pkl")
w["d"] = (w.lR2_pre - w.lR1_pre) - (w.lR2_day - w.lR1_day)     # log(OR_pre / OR_day)
w["gap"] = w.lR1_pre - w.lR1_day                                 # 관내사전이 얼마나 더 진보적인가 (로짓, 음수)
w["dR2"] = w.lR2_pre - w.lR2_day; w["dR1"] = w.gap
print("R1 격차(로짓) 평균", round(w.gap.mean(), 3), "범위", round(w.gap.min(), 2), round(w.gap.max(), 2))
# (a) 재확인표의 차이가 분류표 차이를 얼마나 따라가나 (구·시·군 안 기울기)
m = smf.ols("dR2 ~ dR1", w).fit(cov_type="HC3"); print("구·시·군 안: dR2 ~ dR1", m.params.round(3).to_dict(), "SE", m.bse.round(3).to_dict(), "R2", round(m.rsquared, 3))
# (b) 격차가 0일 때(두 투표구분의 성향이 같다면) 남는 관내사전 효과 = 절편
b0 = m.params.Intercept; se = m.bse.Intercept
print(f"R1 격차 0 일 때 관내사전 효과: log {b0:.3f} (SE {se:.3f}) -> OR비 {np.exp(b0):.3f} [{np.exp(b0 - 1.96 * se):.3f}, {np.exp(b0 + 1.96 * se):.3f}]")
# (c) 실제 평균 격차에서의 차이 = 평균 d
print(f"실제 평균 격차에서: OR비 {np.exp(w.d.mean()):.3f}  (d = gap*(slope-1) + 절편 -> 기울기 {m.params.dR1:.3f})")
# (d) 격차 구간별 평균 d
w["구간"] = pd.qcut(w.gap, 4)
print(w.groupby("구간", observed=True).agg(n=("d", "size"), 평균격차=("gap", "mean"), OR비=("d", lambda s: np.exp(s.mean()))).round(3).to_string())
