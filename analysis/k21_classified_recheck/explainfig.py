"""설명 그림: (A) 후보 지지의 고령 상관 vs K, (B) 구·시·군 미분류율 vs 60대 이상 비율"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in fm.findSystemFonts():
    if "NanumGothic" in f and "Bold" not in f: fm.fontManager.addfont(f); plt.rcParams["font.family"] = fm.FontProperties(fname=f).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
S = pd.read_pickle("explain.pkl"); R, dist = S["R"], S["dist"]
COL = {"18대": "#9b59b6", "19대": "#1baf7a", "20대": "#2a78d6", "21대": "#eb6834"}
# 기준(민주) 후보의 고령 상관: K = 1 위치에 속 빈 점
ref = {"18대": ("문재인", dist["18대"]), "19대": ("문재인", dist["19대"]), "21대": ("이재명", dist["21대"])}
fig, ax = plt.subplots(1, 2, figsize=(16, 7.2), gridspec_kw=dict(width_ratios=[1.15, 1]))

a = ax[0]
x, y = R.고령상관.values, R.logK.values
b1, b0 = np.polyfit(x, y, 1); xs = np.linspace(-.9, .9, 50)
a.plot(xs, b0 + b1 * xs, color="#555", lw=1.5, ls="--", zorder=1)
a.axhline(0, color="#999", lw=1, zorder=0)
LAB = {"기타": "군소 후보"}
OFF = {("18대", "박근혜"): (-150, 10), ("19대", "안철수"): (9, -3), ("21대", "김문수"): (-150, -16), ("19대", "홍준표"): (9, 4), ("19대", "유승민"): (9, 8), ("21대", "권영국"): (-150, -14), ("21대", "이준석"): (9, 6)}
for _, r in R.iterrows():
    a.scatter(r.고령상관, r.logK, s=150, color=COL[r.선거], edgecolor="white", linewidth=2, zorder=3)
    a.annotate(f"{r.선거} {LAB.get(r.후보, r.후보)}  K {r.K:.2f}", (r.고령상관, r.logK), xytext=OFF.get((r.선거, r.후보), (7, 4)), textcoords="offset points", fontsize=10, color="#222")
yt = [0.7, 0.8, 1, 1.25, 1.5, 2, 3, 5]; a.set_yticks(np.log(yt)); a.set_yticklabels([str(v) for v in yt])
a.set_xlim(-.95, .95); a.set_ylim(np.log(.65), np.log(5.6))
a.set_xlabel("후보 지지가 고령 지역에서 얼마나 강한가\n(구·시·군 득표율과 60대 이상 비율의 상관)", fontsize=11)
a.set_ylabel("K (미분류표 ÷ 분류표, 민주 후보 대비, 로그 눈금)", fontsize=11)
r_all = np.corrcoef(x, y)[0, 1]; main = ~R.후보.isin(["기타", "송진호"]); r_main = np.corrcoef(x[main], y[main])[0, 1]
a.text(.02, .98, f"후보 11명 (18·19·21대)\n상관 {r_all:.2f}, 군소 후보 빼면 {r_main:.2f}", transform=a.transAxes, va="top", fontsize=11,
       bbox=dict(boxstyle="round", fc="white", ec="#ccc"))
a.text(.98, .03, "K = 1: 민주 후보와 같은 비율로 미분류", transform=a.transAxes, ha="right", fontsize=9, color="#777")
a.set_title("A. 지지층이 고령일수록 그 후보의 표가 미분류표에 많다", fontsize=13, loc="left")
for e, c in COL.items():
    if e != "20대": a.scatter([], [], s=80, color=c, label=e)
a.legend(loc="lower right", bbox_to_anchor=(1, .08), frameon=False, fontsize=10)

a = ax[1]
for e in ["18대", "19대", "20대", "21대"]:
    d = dist[e].dropna(); xx, yy = d.age * 100, d.urate * 100
    a.scatter(xx, yy, s=14, color=COL[e], alpha=.45, edgecolor="none")
    s1, s0 = np.polyfit(xx, yy, 1); xs = np.linspace(xx.min(), xx.max(), 20)
    a.plot(xs, s0 + s1 * xs, color=COL[e], lw=2.5, label=f"{e}: 60대 이상 10%p 당 +{s1 * 10:.2f}%p (상관 {np.corrcoef(xx, yy)[0, 1]:.2f})")
a.set_xlabel("구·시·군 60대 이상 비율 (%)", fontsize=11); a.set_ylabel("미분류율 (%) = 미분류표 ÷ 분류기 통과 투표지", fontsize=11)
a.set_title("B. 고령 지역일수록 분류기가 못 읽는 투표지가 많다", fontsize=13, loc="left")
a.legend(loc="upper left", frameon=False, fontsize=10)
for a in ax:
    a.grid(color="#e8e8e8", lw=.6); a.set_axisbelow(True)
    for s in ["top", "right"]: a.spines[s].set_visible(False)
fig.text(.5, .005, "두 사실이 함께 성립하면 K > 1 이 생긴다: 고령 유권자의 투표지가 더 자주 미분류되고(B), 고령 유권자가 특정 후보에 몰려 있을수록 그 후보의 K 가 커진다(A). 20대는 후보별 자료가 없어 A에서 빠짐.",
         ha="center", fontsize=10, color="#444")
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig("K_설명_고령지지.png", dpi=130); print("ok")
