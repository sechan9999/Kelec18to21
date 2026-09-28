"""20대 보정(오산 복원, 제천 제외) Fit Plot — K21_FitPlot.png 와 같은 형식"""
import pandas as pd, numpy as np
src = open("k21reg.py").read()
exec(src[:src.index("# Step 1.")])                                   # import·스타일
exec(src[src.index("def reg("):src.index("m21, o21 = reg(")])         # reg()
exec(src[src.index("def stat_box("):src.index("diagnostics(m21,")])   # stat_box, diagnostics, fitplot

# Step 1. 20대 보정 자료
p = pd.read_pickle("pe20.pkl").copy(); o = p.district == "오산시"
p.loc[o, "Y1"] -= p.loc[o, "Y2"]; p.loc[o, "L1"] -= p.loc[o, "L2"]         # 오산: 분류 = 최종 - 재확인
p = p[p.district != "제천시"].reset_index(drop=True)                      # 제천: 복원 불가, 제외
p["R_1"] = p.Y1 / (p.Y1 + p.L1); p["R_2"] = p.Y2 / (p.Y2 + p.L2); p["R_1sq"] = p.R_1 ** 2

# Step 2. 회귀와 그림 (21대와 같은 함수)
m, _ = reg(p, "R_2 ~ R_1")
fig, ax = plt.subplots(figsize=(9.6, 6.2)); fitplot(ax, p, m, "Fit Plot for R_2  (20대 보정: 오산 복원, 제천 제외)")
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, frameon=True)
fig.subplots_adjust(left=.07, right=.74, bottom=.17, top=.93); fig.savefig("K20_FitPlot_보정.png", dpi=150)
print(m.params.round(4).to_dict(), round(m.rsquared, 4), round(m.mse_resid, 5), int(m.nobs))
