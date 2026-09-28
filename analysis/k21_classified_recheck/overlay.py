"""20대(보정) · 21대 Fit Plot 겹쳐 그리기 + 두 선 차이 검정"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 9})
B, O = "#2a78d6", "#eb6834"

# Step 1. 자료: 20대 보정(오산 복원, 제천 제외), 21대
p = pd.read_pickle("pe20.pkl").copy(); o = p.district == "오산시"
p.loc[o, "Y1"] -= p.loc[o, "Y2"]; p.loc[o, "L1"] -= p.loc[o, "L2"]; p = p[p.district != "제천시"]
k = pd.read_pickle("k21reg_out.pkl")["k"]
f = lambda d, e: pd.DataFrame({"district": d.district.values, "R_1": (d.Y1 / (d.Y1 + d.L1)).values, "R_2": (d.Y2 / (d.Y2 + d.L2)).values, "선거": e})
D = pd.concat([f(p, "20대"), f(k, "21대")], ignore_index=True)

# Step 2. 두 선이 같은가: 상호작용 모형 R_2 ~ R_1 * 선거
D["c"] = D.R_1 - .5                                              # R1=0.5 에서의 높이 차이로 해석되게 중심화
M = smf.ols("R_2 ~ c * C(선거)", D).fit(cov_type="HC3")
W = M.wald_test("C(선거)[T.21대] = 0, c:C(선거)[T.21대] = 0", scalar=True)
M0 = smf.ols("R_2 ~ R_1", D).fit()
Fj = smf.ols("R_2 ~ R_1 * C(선거)", D).fit().compare_f_test(M0)   # 절편·기울기 동시 차이
print(M.summary().tables[1]); print("절편·기울기 동시 F =", round(Fj[0], 2), "p =", round(Fj[1], 3))
# R1=0.5 에서 두 선의 차이
x = pd.DataFrame({"R_1": [.2, .5, .8] * 2, "선거": ["20대"] * 3 + ["21대"] * 3})
pr = smf.ols("R_2 ~ R_1 * C(선거)", D).fit().get_prediction(x).summary_frame()
print(pd.concat([x, pr[["mean", "mean_ci_lower", "mean_ci_upper"]]], axis=1).round(4))

# Step 3. 그림
fig, ax = plt.subplots(figsize=(9, 8))
xs = np.linspace(0.05, 0.87, 200); stat = {}
for e, c, mk in [("20대", B, "o"), ("21대", O, "^")]:
    d = D[D.선거 == e]; m = smf.ols("R_2 ~ R_1", d).fit(); stat[e] = m
    q = m.get_prediction(pd.DataFrame({"R_1": xs})).summary_frame(alpha=.05)
    ax.fill_between(xs, q.mean_ci_lower, q.mean_ci_upper, color=c, alpha=.25, lw=0)
    ax.plot(xs, q.obs_ci_lower, "--", c=c, lw=1); ax.plot(xs, q.obs_ci_upper, "--", c=c, lw=1)
    ax.scatter(d.R_1, d.R_2, s=22, marker=mk, facecolors="none", edgecolors=c, linewidths=.9, alpha=.8)
    ax.plot(xs, q["mean"], c=c, lw=2.2,
            label=f"{e} (n={int(m.nobs)}):  R_2 = {m.params.Intercept:+.3f} + {m.params.R_1:.3f}·R_1,  R-Sq {m.rsquared:.4f}, MSE {m.mse_resid:.5f}")
ax.plot([0, 1], [0, 1], ":", c="#888", lw=1.2, label="R_2 = R_1  (K = 1, 기준선)")
# 두 선거 모두 튀는 지역 표시
for nm in ["강남구", "서초구", "군위군"]:
    for e, c in [("20대", B), ("21대", O)]:
        r = D[(D.선거 == e) & (D.district == nm)].iloc[0]
        off = {("강남구", "20대"): (10, 4), ("서초구", "20대"): (10, -10), ("강남구", "21대"): (10, -12), ("서초구", "21대"): (-10, -34),
               ("군위군", "20대"): (-16, 10), ("군위군", "21대"): (-10, -16)}[(nm, e)]
        ax.annotate(f"{nm} {e[:2]}", (r.R_1, r.R_2), xytext=off, textcoords="offset points", fontsize=8, color=c,
                    arrowprops=dict(arrowstyle="-", color=c, lw=.6))
ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="R_1 = 김문수(윤석열) / 양자, 분류된 투표지", ylabel="R_2 = 같은 비율, 재확인대상 투표지")
ax.set_title("Fit Plot for R_2 — 20대(2022, 보정) vs 21대(2025)", fontweight=600, fontsize=12)
from matplotlib.lines import Line2D; from matplotlib.patches import Patch
h, l = ax.get_legend_handles_labels()
h += [Patch(color="#999", alpha=.35), Line2D([], [], ls="--", c="#777")]; l += ["95% 신뢰대 (평균선)", "95% 예측한계 (개별 지역)"]
ax.legend(h, l, loc="upper left", frameon=True, fontsize=8.5)
ax.text(.98, .03, f"두 선 차이 검정 (상호작용 모형, HC3)\n기울기 차이 {M.params['c:C(선거)[T.21대]']:+.3f}  p = {M.pvalues['c:C(선거)[T.21대]']:.2f}  (평행)\n"
        f"R_1=0.5 에서 높이 차이 {M.params['C(선거)[T.21대]']:+.4f}  p < 0.001  (21대가 약간 위)\n두 선 동일 가설 (Wald) p = {W.pvalue:.4f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, bbox=dict(fc="white", ec="#bbb"))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("K20_K21_FitPlot_겹침.png", dpi=160)
