"""18–21대 Fit Plot 겹침 — SAS ODS(proc sgplot reg group=) 스타일
입력: overlay4_out.pkl (보수 후보 분자, 구·시·군), 출력: K18_K21_FitPlot_SAS.png"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
plt.rcParams.update({"font.family": ["DejaVu Sans", "NanumGothic"], "axes.unicode_minus": False, "font.size": 10})

# Step 1. 자료와 SAS 기본 그룹 스타일 (GraphData1–4 색, 마커 모양)
D = pd.read_pickle("overlay4_out.pkl")["D"]
STY = {"18대": dict(c="#445694", m="o", lab="18th (Park)"), "19대": dict(c="#A23A2E", m="+", lab="19th (Hong)"),
       "20대": dict(c="#01665E", m="x", lab="20th (Yoon, corrected)"), "21대": dict(c="#543005", m="^", lab="21st (Kim)")}

# Step 2. 선거별 OLS 적합, 95% 신뢰대(CLM)·예측한계(CLI)
fig = plt.figure(figsize=(13.5, 7.8)); ax = fig.add_axes([0.06, 0.17, 0.55, 0.74])
xs = np.linspace(0.0, 0.93, 200); X = pd.DataFrame({"R_1": xs}); rows = []
for e, s in STY.items():
    d = D[D.선거 == e]; m = smf.ols("R_2 ~ R_1", d).fit(); q = m.get_prediction(X).summary_frame(alpha=.05)
    lo, hi = d.R_1.min(), d.R_1.max(); k = (xs >= lo - .01) & (xs <= hi + .01)
    ax.fill_between(xs[k], q.mean_ci_lower[k], q.mean_ci_upper[k], color=s["c"], alpha=.18, lw=0)
    ax.plot(xs[k], q.obs_ci_lower[k], ls=(0, (4, 3)), c=s["c"], lw=.8, alpha=.8); ax.plot(xs[k], q.obs_ci_upper[k], ls=(0, (4, 3)), c=s["c"], lw=.8, alpha=.8)
    kw = dict(s=26, linewidths=.9, alpha=.85)
    if s["m"] in ("+", "x"): ax.scatter(d.R_1, d.R_2, marker=s["m"], c=s["c"], **kw)
    else: ax.scatter(d.R_1, d.R_2, marker=s["m"], facecolors="none", edgecolors=s["c"], **kw)
    ax.plot(xs[k], q["mean"][k], c=s["c"], lw=2.2)
    rows.append((s["lab"], int(m.nobs), m.params.Intercept, m.params.R_1, m.rsquared, m.mse_resid))
ax.plot([0, 1], [0, 1], c="#8C8C8C", lw=.9, ls=(0, (1, 2)))

# Step 3. SAS 축·격자·제목
ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_xticks(np.arange(0, 1.01, .2)); ax.set_yticks(np.arange(0, 1.01, .2))
ax.set_xlabel("R_1", fontsize=11); ax.set_ylabel("R_2", fontsize=11)
for sp in ax.spines.values(): sp.set_color("#000000"); sp.set_linewidth(.8)
ax.tick_params(direction="out", length=4, width=.8)
ax.set_facecolor("white"); ax.grid(False)
fig.suptitle("Fit Plot for R_2 by Election", fontsize=14, fontweight="bold", x=.335, y=.975)
ax.set_title("R_1 = Con/(Con+Dem) classified votes,  R_2 = Con/(Con+Dem) unclassified votes", fontsize=9, color="#333333", pad=6)

# Step 4. 오른쪽 통계 표 (SAS 'Fit Statistics' 상자처럼)
tx = fig.add_axes([0.645, 0.30, 0.34, 0.56]); tx.axis("off")
tx.add_patch(plt.Rectangle((0, 0), 1, 1, transform=tx.transAxes, fill=False, ec="#9E9E9E", lw=.8))
tx.text(.5, .955, "Fit Statistics", ha="center", va="top", fontsize=10, fontweight="bold", transform=tx.transAxes)
hdr = ["Election", "N", "Intercept", "Slope", "R-Square", "MSE"]; xpos = [.04, .30, .47, .62, .78, .94]
for x, h in zip(xpos, hdr): tx.text(x, .87, h, fontsize=8.5, fontweight="bold", transform=tx.transAxes, ha="left" if x < .1 else "right")
tx.plot([.02, .98], [.845, .845], c="#9E9E9E", lw=.6, transform=tx.transAxes)
for i, (lab, n, a, b, r2, mse) in enumerate(rows):
    y = .79 - i * .075; c = STY[list(STY)[i]]["c"]
    tx.text(.04, y, lab.split(" ")[0] + (" *" if "corrected" in lab else ""), fontsize=8.5, color=c, fontweight="bold", transform=tx.transAxes)
    for x, v in zip(xpos[1:], [f"{n}", f"{a:+.4f}", f"{b:.4f}", f"{r2:.4f}", f"{mse:.5f}"]):
        tx.text(x, y, v, fontsize=8.5, ha="right", transform=tx.transAxes)
M = smf.ols("R_2 ~ c * C(선거, Treatment('20대'))", D).fit(cov_type="HC3")
y0 = .79 - 4 * .075 + .01; tx.plot([.02, .98], [y0 + .03, y0 + .03], c="#9E9E9E", lw=.6, transform=tx.transAxes)
tx.text(.04, y0 - .03, "Difference vs 20th (HC3 SE)", fontsize=8.5, fontweight="bold", transform=tx.transAxes)
for i, e in enumerate(["18대", "19대", "21대"]):
    sl, sp_ = M.params[f"c:C(선거, Treatment('20대'))[T.{e}]"], M.pvalues[f"c:C(선거, Treatment('20대'))[T.{e}]"]
    lv, lp = M.params[f"C(선거, Treatment('20대'))[T.{e}]"], M.pvalues[f"C(선거, Treatment('20대'))[T.{e}]"]
    pf = lambda p: "<.0001" if p < 1e-4 else f"{p:.4f}"
    yy = y0 - .10 - i * .115
    tx.text(.04, yy, STY[e]["lab"].split(" ")[0], fontsize=8.5, fontweight="bold", color=STY[e]["c"], transform=tx.transAxes)
    tx.text(.20, yy, f"slope {sl:+.4f}  (p {pf(sp_)})", fontsize=8.3, transform=tx.transAxes)
    tx.text(.20, yy - .05, f"level at R_1 = 0.5  {lv:+.4f}  (p {pf(lp)})", fontsize=8.3, transform=tx.transAxes)

# Step 5. 아래쪽 범례 상자 (SAS 기본 위치)
h = [Line2D([], [], color=s["c"], marker=s["m"], markerfacecolor="none" if s["m"] not in ("+", "x") else s["c"], lw=2.2, ms=7, label=s["lab"]) for s in STY.values()]
h += [Patch(facecolor="#888888", alpha=.3, label="95% Confidence Limits"), Line2D([], [], color="#555555", ls=(0, (4, 3)), lw=.9, label="95% Prediction Limits"),
      Line2D([], [], color="#8C8C8C", ls=(0, (1, 2)), lw=.9, label="R_2 = R_1 (K = 1)")]
lg = fig.legend(handles=h, loc="lower center", bbox_to_anchor=(.335, .015), ncol=4, fontsize=8.8, frameon=True, fancybox=False, edgecolor="#9E9E9E")
fig.text(.645, .26, "* 20th: Osan restored, Jecheon excluded.\nNumerator = conservative candidate in every election\n(Park Geun-hye, Hong Joon-pyo, Yoon Suk-yeol, Kim Moon-soo).\nUnit = district (시·군·구).",
         fontsize=7.6, color="#333333", va="top")
fig.savefig("K18_K21_FitPlot_SAS.png", dpi=170, facecolor="white")
for r in rows: print(r)
