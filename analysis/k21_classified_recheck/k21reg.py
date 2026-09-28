"""SAS proc reg (Fit Diagnostics / Fit Plot) 를 21대선 구·시·군 자료로 재현
출력: k21elec.xlsx (SAS 입력용), K21_회귀_결과.xlsx, K21_FitDiagnostics.png, K21_FitPlot.png, K20_K21_FitPlot_비교.png"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib, warnings
from scipy import stats
matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 8})
BLUE, LINE = "#1f4e9c", "#6b7fa8"

# Step 1. 21대 투표구 → 구·시·군 합산 (제외 행 빼고), 세종은 20대처럼 충남 '세종시'
d = pd.read_excel("ALL17.xlsx", "투표구별"); d = d[d.판독방식 != "제외"].copy()
d.loc[d.시도명 == "세종특별자치시", "구시군명"] = "세종시"
d["시도명"] = d.시도명.replace({"세종특별자치시": "충청남도"})
C = ["분류_이재명", "분류_김문수", "재확인_이재명", "재확인_김문수"]
k = d.groupby(["시도명", "구시군명"], sort=False)[C].sum().reset_index()
k.columns = ["region", "district", "L1", "Y1", "L2", "Y2"]          # SAS 변수명(20대와 같게: Y=국힘, L=민주)
k["R1"] = k.Y1 / (k.Y1 + k.L1); k["R2"] = k.Y2 / (k.Y2 + k.L2); k["K"] = k.R2 / k.R1
k["R_1"], k["R_2"], k["R_1sq"] = k.R1, k.R2, k.R1 ** 2
k.insert(2, "index", range(1, len(k) + 1))
# 투표구분별(class) 자료: 선거일 / 관내사전 / 관외사전 / 재외
t = d.groupby(["시도명", "구시군명", "구분"], sort=False)[C].sum().reset_index()
t.columns = ["region", "district", "class", "L1", "Y1", "L2", "Y2"]
t = t[(t.L2 + t.Y2 > 0) & (t.L1 + t.Y1 > 0)]
t["R1"] = t.Y1 / (t.Y1 + t.L1); t["R2"] = t.Y2 / (t.Y2 + t.L2); t["K"] = t.R2 / t.R1

# Step 2. 20대 (pe20 = SAS k20elec 와 같은 249 단위, 비교용)
p = pd.read_pickle("pe20.pkl").copy()
p["R1"] = p.Y1 / (p.Y1 + p.L1); p["R2"] = p.Y2 / (p.Y2 + p.L2)

# Step 3. proc reg: 선형 / 2차 (r clm cli) + 영향 통계
def reg(df, f):
    m = smf.ols(f, df).fit(); inf = m.get_influence(); pr = m.get_prediction().summary_frame(alpha=.05)
    o = pd.DataFrame({"Predicted": m.fittedvalues, "Residual": m.resid, "StdErrPred": pr.mean_se,
                      "CLM_lo": pr.mean_ci_lower, "CLM_hi": pr.mean_ci_upper, "CLI_lo": pr.obs_ci_lower, "CLI_hi": pr.obs_ci_upper,
                      "Student": inf.resid_studentized_internal, "RStudent": inf.resid_studentized_external,
                      "Leverage": inf.hat_matrix_diag, "CooksD": inf.cooks_distance[0]})
    return m, o
m21, o21 = reg(k, "R_2 ~ R_1"); q21, oq21 = reg(k, "R_2 ~ R_1sq + R_1")
m20, o20 = reg(p.assign(R_1=p.R1, R_2=p.R2), "R_2 ~ R_1")

def stat_box(ax, m, x, y, fs=7.5):
    s = [("Observations", f"{int(m.nobs)}"), ("Parameters", f"{len(m.params)}"), ("Error DF", f"{int(m.df_resid)}"),
         ("MSE", f"{m.mse_resid:.4f}"), ("R-Square", f"{m.rsquared:.4f}"), ("Adj R-Square", f"{m.rsquared_adj:.4f}")]
    txt = "\n".join(f"{a:<14s}{b:>8s}" for a, b in s)
    ax.text(x, y, txt, transform=ax.transAxes, family="DejaVu Sans Mono", fontsize=fs, va="top",
            bbox=dict(boxstyle="square", fc="white", ec="#999"))

# Step 4. Fit Diagnostics 3×3 (SAS 배치 그대로)
def diagnostics(m, o, y, title, fn):
    n, pp = int(m.nobs), len(m.params)
    fig, A = plt.subplots(3, 3, figsize=(10, 8.6)); fig.suptitle(title, fontweight=600, fontsize=11)
    sc = dict(s=12, facecolors="none", edgecolors=BLUE, linewidths=.8)
    ax = A[0, 0]; ax.scatter(o.Predicted, o.Residual, **sc); ax.axhline(0, c="#888", lw=.8); ax.set(xlabel="Predicted Value", ylabel="Residual")
    ax = A[0, 1]; ax.scatter(o.Predicted, o.RStudent, **sc); [ax.axhline(v, c="#888", lw=.8) for v in (-2, 0, 2)]; ax.set(xlabel="Predicted Value", ylabel="RStudent")
    ax = A[0, 2]; ax.scatter(o.Leverage, o.RStudent, **sc); [ax.axhline(v, c="#888", lw=.8) for v in (-2, 2)]
    ax.axvline(2 * pp / n, c="#888", lw=.8); ax.set(xlabel="Leverage", ylabel="RStudent")
    ax = A[1, 0]; (qx, qy), (sl, ic, _) = stats.probplot(o.Residual, dist="norm"); ax.scatter(qx, qy, **sc)
    ax.plot(qx, ic + sl * qx, c="#888", lw=.8); ax.set(xlabel="Quantile", ylabel="Residual")
    ax = A[1, 1]; ax.scatter(o.Predicted, y, **sc); lo, hi = min(o.Predicted.min(), y.min()), max(o.Predicted.max(), y.max())
    ax.plot([lo, hi], [lo, hi], c="#888", lw=.8); ax.set(xlabel="Predicted Value", ylabel="R_2")
    ax = A[1, 2]; ax.vlines(np.arange(1, n + 1), 0, o.CooksD, color=BLUE, lw=.8); ax.axhline(4 / n, c="#888", lw=.8)
    ax.set(xlabel="Observation", ylabel="Cook's D", ylim=(0, None))
    ax = A[2, 0]; r = o.Residual; ax.hist(r, bins=12, color="#c9d3e6", ec="#333", weights=np.ones(n) * 100 / n)
    xs = np.linspace(r.min() - r.std(), r.max() + r.std(), 200); bw = (r.max() - r.min()) / 12
    ax.plot(xs, stats.norm.pdf(xs, r.mean(), r.std()) * bw * 100, c=LINE, lw=1.2)
    ax.plot(xs, stats.gaussian_kde(r)(xs) * bw * 100, c="#b0b8c8", lw=1); ax.set(xlabel="Residual", ylabel="Percent")
    # Residual-Fit spread (두 개의 작은 축)
    A[2, 1].axis("off"); bb = A[2, 1].get_position()
    a1 = fig.add_axes([bb.x0, bb.y0, bb.width * .47, bb.height]); a2 = fig.add_axes([bb.x0 + bb.width * .53, bb.y0, bb.width * .47, bb.height], sharey=a1)
    pl = (np.arange(1, n + 1) - .5) / n
    a1.scatter(pl, np.sort(o.Predicted - o.Predicted.mean()), **sc); a1.text(.05, .95, "Fit–Mean", transform=a1.transAxes, va="top", fontsize=8); a1.set_xlabel("Proportion Less")
    a2.scatter(pl, np.sort(o.Residual), **sc); a2.text(.05, .95, "Residual", transform=a2.transAxes, va="top", fontsize=8); plt.setp(a2.get_yticklabels(), visible=False)
    A[2, 2].axis("off"); stat_box(A[2, 2], m, .12, .75)
    fig.tight_layout(rect=(0, 0, 1, .97))
    # tight_layout 후 spread 축 위치 다시 맞춤
    bb = A[2, 1].get_position(); a1.set_position([bb.x0, bb.y0, bb.width * .47, bb.height]); a2.set_position([bb.x0 + bb.width * .53, bb.y0, bb.width * .47, bb.height])
    fig.savefig(fn, dpi=150); plt.close(fig)

# Step 5. Fit Plot (적합선 + 95% 신뢰대 + 95% 예측한계)
def fitplot(ax, df, m, title, box=True):
    xs = pd.DataFrame({"R_1": np.linspace(df.R_1.min(), df.R_1.max(), 200)}); xs["R_1sq"] = xs.R_1 ** 2
    pr = m.get_prediction(xs).summary_frame(alpha=.05)
    ax.fill_between(xs.R_1, pr.mean_ci_lower, pr.mean_ci_upper, color="#b9c6de", alpha=.7, label="95% Confidence Limits", lw=0)
    ax.plot(xs.R_1, pr["mean"], c=LINE, lw=2, label="Fit")
    ax.plot(xs.R_1, pr.obs_ci_lower, "--", c="#6d7fd8", lw=.9, label="95% Prediction Limits"); ax.plot(xs.R_1, pr.obs_ci_upper, "--", c="#6d7fd8", lw=.9)
    ax.scatter(df.R_1, df.R_2, s=22, facecolors="none", edgecolors=BLUE, linewidths=1)
    ax.set(xlabel="R_1", ylabel="R_2", xlim=(0, 1), ylim=(0, 1)); ax.set_title(title, fontweight=600, fontsize=11)
    ax.plot([0, 1], [0, 1], ":", c="#aaa", lw=.8)        # K=1 기준선 (R2 = R1)
    if box: stat_box(ax, m, 1.02, .75)

diagnostics(m21, o21, k.R_2, "Fit Diagnostics for R_2  (21대, 구·시·군)", "K21_FitDiagnostics.png")
fig, ax = plt.subplots(figsize=(9.6, 6.2)); fitplot(ax, k, m21, "Fit Plot for R_2  (21대)")
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, frameon=True); fig.subplots_adjust(left=.07, right=.74, bottom=.17, top=.93); fig.savefig("K21_FitPlot.png", dpi=150); plt.close(fig)
# 20대 vs 21대, 선형·2차 비교
fig, A = plt.subplots(1, 3, figsize=(16, 5.6))
fitplot(A[0], p.assign(R_1=p.R1, R_2=p.R2), m20, "20대 (2022) 선형", box=False)
fitplot(A[1], k, m21, "21대 (2025) 선형", box=False)
fitplot(A[2], k, q21, "21대 (2025) 2차 R_2 = R_1sq + R_1", box=False)
for ax, m in zip(A, [m20, m21, q21]):
    b = m.params; eq = "R_2 = " + " + ".join(f"{b[c]:.3f}·{c.replace('Intercept','1')}" for c in b.index).replace("·1 ", " ").replace("+ -", "- ")
    ax.text(.03, .97, f"{eq}\nR-Square {m.rsquared:.4f}  MSE {m.mse_resid:.5f}  n {int(m.nobs)}", transform=ax.transAxes, va="top", fontsize=8,
            bbox=dict(fc="white", ec="#ccc"))
A[1].legend(loc="upper center", bbox_to_anchor=(.5, -.12), ncol=3); fig.tight_layout(); fig.savefig("K20_K21_FitPlot_비교.png", dpi=150); plt.close(fig)

# Step 6. proc ttest / means / univariate by region, by class
def ttest(df, by):
    rows = []
    for g, z in list(df.groupby(by, sort=False)) + [("전체", df)]:
        for v in ["K", "R1", "R2"]:
            x = z[v]; n = len(x); se = x.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan; tc = stats.t.ppf(.975, n - 1) if n > 1 else np.nan
            r = dict(그룹=g, 변수=v, N=n, Mean=x.mean(), StdDev=x.std(ddof=1), StdErr=se, CL_lo=x.mean() - tc * se, CL_hi=x.mean() + tc * se, Min=x.min(), Max=x.max())
            if v == "K" and n > 1:                          # SAS 기본(H0: 평균=0) 대신 의미 있는 H0: K=1
                r["t(H0:K=1)"] = (x.mean() - 1) / se; r["p"] = 2 * stats.t.sf(abs(r["t(H0:K=1)"]), n - 1)
            rows.append(r)
    return pd.DataFrame(rows)
def pctl(df, by, v="K"):
    P = [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
    return pd.DataFrame([{by: g, "N": len(z), **{f"P_{q}": np.percentile(z[v], q) for q in P}} for g, z in list(df.groupby(by, sort=False)) + [("전체", df)]])
T_reg, T_cls = ttest(k, "region"), ttest(t, "class")
D_reg, D_cls = pctl(k, "region"), pctl(t, "class")

# Step 7. 계수표
def coef(m, nm):
    ci = m.conf_int()
    return pd.DataFrame({"모형": nm, "변수": m.params.index, "추정값": m.params.values, "SE": m.bse.values, "t": m.tvalues.values, "p": m.pvalues.values,
                         "95%하한": ci[0].values, "95%상한": ci[1].values, "R²": m.rsquared, "Adj R²": m.rsquared_adj, "MSE": m.mse_resid, "N": int(m.nobs)})
CO = pd.concat([coef(m20, "20대 선형 R_2=R_1"), coef(m21, "21대 선형 R_2=R_1"), coef(q21, "21대 2차 R_2=R_1sq+R_1")])
# 기울기 = 1 검정 (K가 R1과 무관하게 일정한가)
slope1 = {e: ((m.params["R_1"] - 1) / m.bse["R_1"]) for e, m in [("20대", m20), ("21대", m21)]}

OUT = k.join(o21.add_prefix("lin_")).join(oq21[["Predicted", "Residual", "CLM_lo", "CLM_hi", "CLI_lo", "CLI_hi", "RStudent", "CooksD"]].add_prefix("quad_"))
with pd.ExcelWriter("k21elec.xlsx") as w: k.to_excel(w, sheet_name="k21elec", index=False); t.to_excel(w, sheet_name="k21class", index=False)
with pd.ExcelWriter("K21_회귀_결과.xlsx") as w:
    CO.to_excel(w, sheet_name="회귀계수", index=False); OUT.to_excel(w, sheet_name="관측별_r_clm_cli", index=False)
    T_reg.to_excel(w, sheet_name="ttest_region", index=False); T_cls.to_excel(w, sheet_name="ttest_class", index=False)
    D_reg.to_excel(w, sheet_name="k21_dist", index=False); D_cls.to_excel(w, sheet_name="kclass_dist", index=False)
pd.to_pickle(dict(k=k, t=t, CO=CO, T_reg=T_reg, T_cls=T_cls, o21=o21, slope1=slope1), "k21reg_out.pkl")

pd.set_option("display.width", 220)
print(CO.round(4).to_string(index=False)); print("기울기=1 z:", {a: round(b, 2) for a, b in slope1.items()})
print("RStudent |>3|:", k.join(o21)[o21.RStudent.abs() > 3][["region", "district", "R1", "R2", "K", "RStudent", "CooksD"]].round(3).to_string(index=False))
print(T_reg[T_reg.변수 == "K"].round(3).to_string(index=False)); print(T_cls[T_cls.변수 == "K"].round(3).to_string(index=False))
