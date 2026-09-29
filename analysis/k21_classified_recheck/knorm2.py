"""18–21대 구·시·군 K 정규성 (보수 후보 분자, 비교 화면과 같은 자료) + 20·21대 그림"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy import stats
src = open("knorm.py").read(); exec(src[src.index("def norm("):src.index("rows = []")]); exec(src[src.index("def hetero("):src.index("H = pd.DataFrame")])
D = pd.read_pickle("overlay4_out.pkl")["D"]
NM = {"18대": "박근혜/문재인", "19대": "홍준표/문재인", "20대": "윤석열/이재명", "21대": "김문수/이재명"}
rows, het = [], []
for e, d in D.groupby("선거"):
    k = (d.Y2 / d.L2) / (d.Y1 / d.L1); nm = f"{e} {NM[e]}"
    rows += [norm(k, nm), norm(np.log(k), "log " + nm)]
    h = hetero(d.L1, d.Y1, d.L2, d.Y2, nm); h["K"] = nm; h["r_logK_R1"] = np.corrcoef(np.log(k), d.R_1)[0, 1]
    # 1 보다 작은 곳, 정규분포 가정 시 기대 개수
    h["K<1"] = int((k < 1).sum()); het.append(h)
T = pd.DataFrame(rows).set_index("K"); H = pd.DataFrame(het).set_index("K")
pd.set_option("display.width", 250); print(T.round(4).to_string()); print(H.round(4).to_string())
pd.to_pickle(dict(T=T, H=H), "knorm4.pkl")

for f in fm.findSystemFonts():
    if "NanumGothic" in f and "Bold" not in f: fm.fontManager.addfont(f); plt.rcParams["font.family"] = fm.FontProperties(fname=f).get_name(); break
plt.rcParams["axes.unicode_minus"] = False
COL = {"20대": "#2a78d6", "21대": "#eb6834"}
fig, ax = plt.subplots(2, 3, figsize=(15, 9))
for i, e in enumerate(["20대", "21대"]):
    d = D[D.선거 == e]; k = ((d.Y2 / d.L2) / (d.Y1 / d.L1)).astype(float); key = f"{e} {NM[e]}"; t, tl = T.loc[key], T.loc["log " + key]; col = COL[e]
    a = ax[i, 0]; a.hist(k, bins=30, density=True, color=col, alpha=.75, edgecolor="white", linewidth=1)
    xs = np.linspace(k.min(), k.max(), 200); a.plot(xs, stats.norm.pdf(xs, k.mean(), k.std(ddof=1)), color="#333", lw=2, label="정규분포")
    a.plot(xs, stats.lognorm.pdf(xs, np.log(k).std(ddof=1), scale=np.exp(np.log(k).mean())), color="#333", lw=2, ls="--", label="로그정규분포")
    a.set_title(f"{key} (n {len(k)}): K 분포", fontsize=12); a.set_xlabel("K"); a.legend(frameon=False, fontsize=9)
    a.text(.98, .6, f"평균 {t.평균:.3f}\n중앙값 {t.중앙값:.3f}\nSD {t.SD:.3f}\n왜도 {t.왜도:.2f}\n첨도 {t.첨도:.2f}", transform=a.transAxes, ha="right", va="top", fontsize=9)
    for j, (v, lab, tt) in enumerate([(k, "K", t), (np.log(k), "log K", tl)], 1):
        a = ax[i, j]; (osm, osr), (sl, ic, r) = stats.probplot(v, dist="norm")
        a.scatter(osm, osr, s=14, color=col, alpha=.8, edgecolor="white", linewidth=.5); a.plot(osm, ic + sl * osm, color="#333", lw=1.5)
        a.set_title(f"{key}: {lab} 정규 QQ", fontsize=12); a.set_xlabel("정규분포 이론 분위수"); a.set_ylabel(lab)
        verdict = "정규성 기각 안 됨" if tt.SW_p >= .05 and tt.AD_stat < tt.AD_5pct else "정규성 기각 (5%)"
        a.text(.03, .97, f"Shapiro-Wilk p = {tt.SW_p:.3g}\nD'Agostino p = {tt.DAgostino_p:.3g}\nAnderson-Darling {tt.AD_stat:.2f} (5% 기준 {tt.AD_5pct:.2f})\n{verdict}",
               transform=a.transAxes, va="top", fontsize=9, bbox=dict(boxstyle="round", fc="white", ec="#ccc"))
for a in ax.flat:
    a.grid(color="#e5e5e5", lw=.6); a.set_axisbelow(True)
    for s in ["top", "right"]: a.spines[s].set_visible(False)
fig.suptitle("20·21대 구·시·군 K 의 분포와 정규성 (K = 미분류 득표비 ÷ 분류 득표비, 보수 후보 분자)", fontsize=14, y=.995)
fig.tight_layout(); fig.savefig("K20_K21_정규성.png", dpi=130); print("ok")
