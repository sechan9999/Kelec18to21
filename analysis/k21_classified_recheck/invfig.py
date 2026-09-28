"""무효표·재확인율과 OR 그림 (3 패널)"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 9})
S = pd.read_pickle("inv_out.pkl"); BU, BR, A = S["BU"], S["BR"], S["A"]
COL = {"선거일": "#1baf7a", "관내사전": "#eb6834", "관외사전": "#2a78d6"}
fig, AX = plt.subplots(1, 3, figsize=(16, 5.2))

for ax, B, xc, xl, tt in [(AX[0], BU, "u", "무효율 (%)", "① 무효율 5분위별 OR"), (AX[1], BR, "rv", "재확인율 (유효표 중 %)", "② 재확인율 5분위별 OR")]:
    for g, c in COL.items():
        z = B[B.구분 == g]
        ax.plot(z[xc] * 100, z.OR, "-o", c=c, lw=2, ms=6, label=f"{g} (투표구 {int(z.투표구.sum()):,})")
    ax.axhline(1, c="#999", ls=":", lw=1); ax.set(xlabel=xl, ylabel="OR (재확인 김/이 ÷ 분류 김/이)", ylim=(0.95, 1.5)); ax.set_title(tt, fontweight=600)
    ax.legend(frameon=False, fontsize=8.5)
AX[0].text(.03, .03, "무효율 2배일 때 OR ×0.99 [0.98, 1.00]\n(R1·투표구분 통제, 재확인율 함께 넣은 모형)", transform=AX[0].transAxes, fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
AX[1].text(.03, .03, "재확인율 2배일 때 OR ×0.92 [0.90, 0.94]\n재확인표가 많아질수록 OR이 1에 가까워짐(희석)", transform=AX[1].transAxes, fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))

ax = AX[2]
sc = ax.scatter(A.over60 * 100, A.rv * 100, c=np.exp(A.lor), cmap="YlOrRd", vmin=1.0, vmax=1.6, s=A.투표수 / A.투표수.max() * 120 + 8, edgecolors="#555", linewidths=.3)
cb = fig.colorbar(sc, ax=ax, fraction=.046, pad=.02); cb.set_label("구·시·군 OR")
r1, r2 = np.corrcoef(A.over60, A.rv)[0, 1], np.corrcoef(A.over60, A.u)[0, 1]
ax.set(xlabel="60세 이상 비율 (%, 20대선 기준)", ylabel="재확인율 (%)"); ax.set_title("③ 구·시·군: 고령 비율과 재확인율", fontweight=600)
ma = S["ma"]; b = ma[0]["over60"] / 10; s = ma[1]["over60"] / 10
ax.text(.03, .97, f"상관: 60세+ vs 재확인율 r = {r1:.2f}, vs 무효율 r = {r2:.2f}\n60세+ 10%p 높을 때 OR ×{np.exp(b):.3f} [{np.exp(b - 1.96 * s):.3f}, {np.exp(b + 1.96 * s):.3f}]\n(R1·무효율·재확인율 통제, {len(A)}곳)",
        transform=ax.transAxes, va="top", fontsize=8.5, bbox=dict(fc="white", ec="#ccc"))
for a in AX: a.spines[["top", "right"]].set_visible(False)
fig.suptitle("21대 무효표·재확인표와 OR (투표구 18,040개, 분류+재확인+무효 = 투표수 전부 일치)", fontweight=600, fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .95)); fig.savefig("무효표_재확인_OR.png", dpi=150)
