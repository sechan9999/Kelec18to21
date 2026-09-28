"""21대 K 를 당선인(이재명) 분자로: R1 = 이/(이+김) 분류표, R2 = 이/(이+김) 재확인표"""
import pandas as pd, numpy as np
src = open("k21reg.py").read()
exec(src[:src.index("# Step 1.")])
exec(src[src.index("def reg("):src.index("m21, o21 = reg(")])
exec(src[src.index("def stat_box("):src.index("diagnostics(m21,")])

# Step 1. 구·시·군 자료 (k21reg 와 같은 252곳), 분자만 이재명으로
S = pd.read_pickle("k21reg_out.pkl"); k = S["k"].copy(); t = S["t"].copy()
for df in (k, t):
    df["R_1"] = df.L1 / (df.L1 + df.Y1); df["R_2"] = df.L2 / (df.L2 + df.Y2); df["K"] = df.R_2 / df.R_1
k["R_1sq"] = k.R_1 ** 2

# Step 2. 전국·투표구분별 (합산)
def nat(z):
    r1 = z.L1.sum() / (z.L1 + z.Y1).sum(); r2 = z.L2.sum() / (z.L2 + z.Y2).sum()
    return pd.Series(dict(R1=r1, R2=r2, K=r2 / r1, OR=(z.L2.sum() / z.Y2.sum()) / (z.L1.sum() / z.Y1.sum())))
N = pd.concat([nat(k).rename("전체")] + [nat(t[t["class"] == g]).rename(g) for g in ["관내사전", "선거일", "관외사전"]], axis=1).T
print("전국 (이재명 분자)"); print(N.round(4).to_string())

# Step 3. 회귀 R_2 = a + b R_1 (이재명 분자) 와 김문수 분자 비교
m, o = reg(k, "R_2 ~ R_1"); q, _ = reg(k, "R_2 ~ R_1sq + R_1")
kk = S["k"]; mk, _ = reg(kk.assign(R_1=kk.R1, R_2=kk.R2), "R_2 ~ R_1")
print(f"\n이재명 분자: R_2 = {m.params.Intercept:.4f} + {m.params.R_1:.4f} R_1, R2 {m.rsquared:.4f}, MSE {m.mse_resid:.5f}")
print(f"김문수 분자: R_2 = {mk.params.Intercept:.4f} + {mk.params.R_1:.4f} R_1, R2 {mk.rsquared:.4f}")
print(f"2차: R_1sq {q.params.R_1sq:.3f} (t {q.tvalues.R_1sq:.2f})")
print("평균 K (구·시·군 단순평균):", round(k.K.mean(), 4), "| K<1 인 곳", int((k.K < 1).sum()), "/", len(k), "| K 범위", round(k.K.min(), 3), round(k.K.max(), 3))

# Step 4. 시도별 K (합산)
P = k.groupby("region").apply(lambda z: nat(z)).sort_values("R1"); print("\n시도별 (이재명 분자)"); print(P.round(3).to_string())

# Step 5. 그림: 왼쪽 Fit Plot (이재명 분자), 오른쪽 R1 에 따른 K (두 분자)
fig, A = plt.subplots(1, 2, figsize=(15.5, 6.4))
fitplot(A[0], k, m, "Fit Plot for R_2  (21대, 당선인 이재명 분자)", box=False); stat_box(A[0], m, .03, .97)
A[0].set(xlabel="R_1 = 이재명 / (이재명+김문수), 분류된 투표지", ylabel="R_2 = 같은 비율, 재확인대상 투표지")
A[0].legend(loc="lower right", fontsize=8.5)
ax = A[1]
ax.scatter(k.R_1, k.K, s=20, facecolors="none", edgecolors="#2a78d6", linewidths=.9, label=f"이재명 분자  (평균 K {k.K.mean():.3f})")
ax.scatter(kk.R1, kk.K, s=20, marker="^", facecolors="none", edgecolors="#eb6834", linewidths=.9, label=f"김문수 분자  (평균 K {kk.K.mean():.3f})")
ax.axhline(1, c="#888", ls=":", lw=1.2); ax.set(xlim=(0, 1), ylim=(0.55, 1.35), xlabel="R_1 (각 분자 후보의 분류표 양자 비율)", ylabel="K = R2 / R1")
ax.set_title("같은 자료, 분자만 바꾼 K", fontweight=600, fontsize=11); ax.legend(loc="lower right", fontsize=9)
ax.text(.03, .96, "두 후보 양자 비율이라 R_이 = 1 - R_김 이므로\n한 후보가 재확인표에서 늘면 다른 후보는 줄어듦", transform=ax.transAxes, va="top", fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
for a in A: a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("K21_당선인분자_FitPlot.png", dpi=150)
diagnostics(m, o, k.R_2, "Fit Diagnostics for R_2  (21대, 이재명 분자)", "K21_당선인분자_Diagnostics.png")
