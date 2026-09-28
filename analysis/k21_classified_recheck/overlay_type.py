"""21대 관내사전·선거일 Fit Plot (구·시·군 단위) + 20대 전체·21대 전체 적합선 겹침"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 9})
B, O, A, G = "#2a78d6", "#eb6834", "#1baf7a", "#555555"

# Step 1. 21대 구·시·군 × 투표구분 (k21elec.xlsx 의 k21class 시트와 같은 자료)
t = pd.read_pickle("k21reg_out.pkl")["t"]
t = t.assign(R_1=t.R1, R_2=t.R2)
# Step 2. 20대 전체 (오산 복원·제천 제외), 21대 전체
p = pd.read_pickle("pe20.pkl").copy(); o = p.district == "오산시"
p.loc[o, "Y1"] -= p.loc[o, "Y2"]; p.loc[o, "L1"] -= p.loc[o, "L2"]; p = p[p.district != "제천시"]
p = p.assign(R_1=p.Y1 / (p.Y1 + p.L1), R_2=p.Y2 / (p.Y2 + p.L2))
k = pd.read_pickle("k21reg_out.pkl")["k"]
fit = lambda d: smf.ols("R_2 ~ R_1", d).fit()
m20, m21 = fit(p), fit(k)

# Step 3. 관내사전 vs 선거일 차이 검정 (같은 구·시·군이 두 번 들어가므로 구·시·군 군집 SE)
T2 = t[t["class"].isin(["관내사전", "선거일"])].copy(); T2["c"] = T2.R_1 - .5
T2["pre"] = (T2["class"] == "관내사전").astype(float)
T2["gid"] = pd.factorize(T2.region + T2.district)[0]
MI = smf.ols("R_2 ~ c * pre", T2).fit(cov_type="cluster", cov_kwds={"groups": T2.gid})
print(MI.params.round(4).to_dict()); print(MI.pvalues.round(4).to_dict())

# Step 4. 그림: 두 패널
fig, AX = plt.subplots(1, 2, figsize=(15, 7.4), sharey=True)
xs = np.linspace(0.04, 0.9, 200); X = pd.DataFrame({"R_1": xs}); X5 = pd.DataFrame({"R_1": [.5]}); res = {}
for ax, g, c in [(AX[0], "관내사전", O), (AX[1], "선거일", A)]:
    d = t[t["class"] == g]; m = fit(d); res[g] = m
    q = m.get_prediction(X).summary_frame(alpha=.05)
    ax.fill_between(xs, q.mean_ci_lower, q.mean_ci_upper, color=c, alpha=.25, lw=0)
    ax.plot(xs, q.obs_ci_lower, "--", c=c, lw=1); ax.plot(xs, q.obs_ci_upper, "--", c=c, lw=1)
    ax.scatter(d.R_1, d.R_2, s=20, facecolors="none", edgecolors=c, linewidths=.9, alpha=.85)
    ax.plot(xs, q["mean"], c=c, lw=2.4)
    ax.plot(xs, m21.predict(X), c=G, lw=1.4, ls="-.")                 # 21대 전체
    ax.plot(xs, m20.predict(X), c=B, lw=1.6)                           # 20대 전체
    ax.plot([0, 1], [0, 1], ":", c="#999", lw=1.1)
    ax.legend([Line2D([], [], c=c, lw=2.4), Line2D([], [], c=c, ls="--"), Line2D([], [], c=G, ls="-.", lw=1.4),
               Line2D([], [], c=B, lw=1.6), Line2D([], [], c="#999", ls=":")],
              [f"21대 {g} (n={int(m.nobs)}): R_2 = {m.params.Intercept:+.3f} + {m.params.R_1:.3f}·R_1,  R-Sq {m.rsquared:.4f}",
               f"95% 예측한계 ({g})",
               f"21대 전체: {m21.params.Intercept:+.3f} + {m21.params.R_1:.3f}·R_1",
               f"20대 전체 (보정): {m20.params.Intercept:+.3f} + {m20.params.R_1:.3f}·R_1",
               "R_2 = R_1 (K = 1)"], loc="upper left", fontsize=8.3)
    ax.text(.98, .03, f"평균 K = {d.K.mean():.3f}\nR_1=0.5 에서 R_2 = {m.predict(X5)[0]:.3f}\n"
            f"(21대 전체 {m21.predict(X5)[0]:.3f}, 20대 전체 {m20.predict(X5)[0]:.3f})", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9, bbox=dict(fc="white", ec="#bbb"))
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="R_1 = 김문수 / 양자, 분류된 투표지"); ax.set_title(f"21대 {g}", fontweight=600, fontsize=12, color=c)
    ax.spines[["top", "right"]].set_visible(False)
AX[0].set_ylabel("R_2 = 같은 비율, 재확인대상 투표지")
dpre, ppre, dsl, psl = MI.params["pre"], MI.pvalues["pre"], MI.params["c:pre"], MI.pvalues["c:pre"]
fig.suptitle(f"Fit Plot for R_2 — 21대 투표구분별 (구·시·군 단위)     관내사전 - 선거일:  R_1=0.5 높이 {dpre:+.3f} (p {'< 0.001' if ppre < .001 else f'= {ppre:.3f}'}),  "
             f"기울기 {dsl:+.3f} (p {'< 0.001' if psl < .001 else f'= {psl:.3f}'})", fontsize=11, fontweight=600)
fig.text(.5, .005, "※ 20대 자료(pe20res)에는 투표구분별 분류/재확인 값이 없어 20대는 구·시·군 전체 적합선만 기준으로 표시", ha="center", fontsize=8.5, color="#555")
fig.tight_layout(rect=(0, .02, 1, .95)); fig.savefig("K21_투표구분별_FitPlot.png", dpi=160)
for g, m in res.items(): print(g, int(m.nobs), m.params.round(4).to_dict(), round(m.rsquared, 4), round(m.mse_resid, 5))
