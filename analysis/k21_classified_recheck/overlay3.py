"""19대·20대(보정)·21대 Fit Plot 겹침 + 시도별 OR 비교 — 분자는 보수 후보(홍준표·윤석열·김문수)"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib, warnings
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 9})
COL = {"19대": "#1baf7a", "20대": "#2a78d6", "21대": "#eb6834"}

# Step 1. 세 선거 구·시·군 자료 (보수 후보 분자)
S19 = pd.read_pickle("pe19_out.pkl"); p19 = S19["p"]; x19 = S19["x"]
p20 = pd.read_pickle("pe20.pkl").copy(); o = p20.district == "오산시"
p20.loc[o, "Y1"] -= p20.loc[o, "Y2"]; p20.loc[o, "L1"] -= p20.loc[o, "L2"]; p20 = p20[p20.district != "제천시"]
k = pd.read_pickle("k21reg_out.pkl")["k"]
mk = lambda sd, d, y1, l1, y2, l2, e: pd.DataFrame({"시도": sd, "단위": d, "Y1": y1, "L1": l1, "Y2": y2, "L2": l2, "선거": e})
D = pd.concat([mk(p19.시도.values, p19.district.values, p19.H1.values, p19.M1.values, p19.H2.values, p19.M2.values, "19대"),
               mk(p20.시도.values, p20.district.values, p20.Y1.values, p20.L1.values, p20.Y2.values, p20.L2.values, "20대"),
               mk(k.region.values, k.district.values, k.Y1.values, k.L1.values, k.Y2.values, k.L2.values, "21대")], ignore_index=True)
D["시도"] = D.시도.replace({"세종특별자치시": "충청남도"})
D["R_1"] = D.Y1 / (D.Y1 + D.L1); D["R_2"] = D.Y2 / (D.Y2 + D.L2); D["c"] = D.R_1 - .5

# Step 2. 선거별 적합과 차이 검정 (20대 기준, HC3)
fits = {e: smf.ols("R_2 ~ R_1", D[D.선거 == e]).fit() for e in COL}
M = smf.ols("R_2 ~ c * C(선거, Treatment('20대'))", D).fit(cov_type="HC3")
for e, m in fits.items():
    print(f"{e}: n {int(m.nobs)} R_2 = {m.params.Intercept:+.4f} + {m.params.R_1:.4f} R_1 | R2 {m.rsquared:.4f} MSE {m.mse_resid:.5f} | R1=0.5 에서 {m.params.Intercept + .5 * m.params.R_1:.3f}")
print(M.summary().tables[1])
# 19대 민감도: 공개값과 2% 이상 다른 14곳 제외
bad = set(x19[x19.rel >= .02].district)
m19s = smf.ols("R_2 ~ R_1", D[(D.선거 == "19대") & ~D.단위.isin(bad)]).fit()
print(f"19대 (14곳 제외): n {int(m19s.nobs)} R_2 = {m19s.params.Intercept:+.4f} + {m19s.params.R_1:.4f} R_1 | R2 {m19s.rsquared:.4f}")

# Step 3. 전국·시도 OR (구·시·군 군집 델타법)
def lor_ci(df):
    A, B, C, Dd = (df[c].astype(float) for c in ("Y2", "L2", "Y1", "L1"))
    lor = np.log(A.sum()) - np.log(B.sum()) - np.log(C.sum()) + np.log(Dd.sum()); n = len(df)
    z = A / A.sum() - B / B.sum() - C / C.sum() + Dd / Dd.sum()
    se = np.sqrt(n / (n - 1) * (z ** 2).sum()) if n > 1 else np.nan; t = stats.t.ppf(.975, max(n - 1, 1))
    K = (A.sum() / (A.sum() + B.sum())) / (C.sum() / (C.sum() + Dd.sum()))
    return pd.Series(dict(OR=np.exp(lor), lo=np.exp(lor - t * se), hi=np.exp(lor + t * se), K=K, n=n))
P = D.groupby(["선거", "시도"]).apply(lor_ci).reset_index()
N = D.groupby("선거").apply(lor_ci)
print("\n전국"); print(N.round(4).to_string())
W = P.pivot(index="시도", columns="선거", values="OR"); print("\n시도 OR"); print(W.round(3).sort_values("21대").to_string())
print("\n시도 OR 상관 (log):", np.corrcoef(np.log(W.dropna().values.T)).round(2).tolist())

# Step 4. 그림: 왼쪽 겹친 Fit Plot, 오른쪽 시도별 OR
fig, (ax, bx) = plt.subplots(1, 2, figsize=(16, 7.2), gridspec_kw={"width_ratios": [1.15, 1]})
xs = np.linspace(0.02, 0.9, 200); X = pd.DataFrame({"R_1": xs})
for e, c in COL.items():
    d = D[D.선거 == e]; m = fits[e]; q = m.get_prediction(X).summary_frame(alpha=.05)
    ax.scatter(d.R_1, d.R_2, s=14, facecolors="none", edgecolors=c, linewidths=.8, alpha=.75, marker={"19대": "s", "20대": "o", "21대": "^"}[e])
    ax.fill_between(xs, q.mean_ci_lower, q.mean_ci_upper, color=c, alpha=.25, lw=0)
    ax.plot(xs, q["mean"], c=c, lw=2.3, label=f"{e} (n={int(m.nobs)}): {m.params.Intercept:+.3f} + {m.params.R_1:.3f}·R_1, R-Sq {m.rsquared:.4f}")
ax.plot([0, 1], [0, 1], ":", c="#888", lw=1.2, label="R_2 = R_1 (K = 1)")
ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="R_1 = 보수 후보 / (보수+민주), 분류된 투표지", ylabel="R_2 = 같은 비율, 미분류(재확인) 투표지")
ax.set_title("Fit Plot for R_2 — 19대(홍준표)·20대(윤석열, 보정)·21대(김문수)", fontweight=600, fontsize=11)
ax.legend(loc="upper left", fontsize=8.5)
b1 = M.params["c:C(선거, Treatment('20대'))[T.19대]"]; p1 = M.pvalues["c:C(선거, Treatment('20대'))[T.19대]"]
h1 = M.params["C(선거, Treatment('20대'))[T.19대]"]
ax.text(.98, .03, f"20대 대비 19대: 기울기 {b1:+.3f} (p = {p1:.2f}), R_1=0.5 높이 {h1:+.3f} (p < 0.001)\n"
        f"20대 대비 21대: 기울기 {M.params[chr(99)+':C(선거, Treatment('+chr(39)+'20대'+chr(39)+'))[T.21대]']:+.3f}, 높이 {M.params['C(선거, Treatment('+chr(39)+'20대'+chr(39)+'))[T.21대]']:+.3f}",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, bbox=dict(fc="white", ec="#bbb"))
order = W.sort_values("21대").index.tolist(); yy = np.arange(len(order))
for j, (e, c) in enumerate(COL.items()):
    z = P[P.선거 == e].set_index("시도").reindex(order)
    off = (j - 1) * .25
    bx.errorbar(z.OR, yy + off, xerr=[z.OR - z.lo, z.hi - z.OR], fmt="o", c=c, ms=5, lw=1.2, capsize=0, label=f"{e} (전국 {N.loc[e, 'OR']:.2f})")
bx.axvline(1, c="#888", ls=":", lw=1.2); bx.set_xlim(0.8, 2.2)
bx.text(.99, .995, "제주는 구·시·군 2곳뿐이라 구간이 넓음(20대 상한 3.46, 축 밖)", transform=bx.transAxes, ha="right", va="top", fontsize=8, color="#666")
bx.set_yticks(yy); bx.set_yticklabels([s.replace("특별자치도", "").replace("광역시", "").replace("특별시", "").replace("도", "") if s.endswith("도") or "광역" in s or "특별" in s else s for s in order])
bx.set(xlabel="OR = (미분류 보수/민주) ÷ (분류 보수/민주), 95% 구간"); bx.set_title("시도별 OR (세종은 충남에 포함)", fontweight=600, fontsize=11)
bx.legend(loc="lower right", fontsize=9)
for a in (ax, bx): a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("K19_K20_K21_겹침.png", dpi=150)
pd.to_pickle(dict(D=D, P=P, N=N, fits={e: (m.params, m.rsquared, m.mse_resid, int(m.nobs)) for e, m in fits.items()},
                  M=(M.params, M.pvalues), m19s=(m19s.params, m19s.rsquared, int(m19s.nobs)), bad=sorted(bad)), "overlay3_out.pkl")
