"""18대(2012) 분류/미분류 분석 — 보수 후보(박근혜, 당선인) 분자
R1 = P1/(P1+M1) 분류표, R2 = P2/(P2+M2) 미분류(재확인)표, K = R2/R1
원본 CSV의 구·시·군 이름이 '?'로 저장되어 있어, 같은 index 체계인 19대(pe19res)에서 이름을 가져와 2012년 행정구역으로 맞춘다.
출력: pe18_out.pkl, K18_FitPlot.png, K18_FitDiagnostics.png"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
src = open("k21reg.py").read()
exec(src[:src.index("# Step 1.")])
exec(src[src.index("def reg("):src.index("m21, o21 = reg(")])
exec(src[src.index("def stat_box("):src.index("diagnostics(m21,")])
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")

# Step 1. 자료 읽기, 이름 복원 (index·지역코드·글자수가 19대와 모두 같음을 확인)
p = pd.read_csv("/root/.claude/uploads/b16eee4c-f64b-565c-be43-dea7f56709b5/825374fd-pe18res2.csv")
n19 = pd.read_excel("/root/.claude/uploads/b16eee4c-f64b-565c-be43-dea7f56709b5/50c14bcc-pe19res.xlsx")[["index", "region", "district"]]
p = p.drop(columns="district").merge(n19, on=["index", "region"], how="left")
assert p.district.notna().sum() == 248 and len(p) == 249
# 2012년 이름: 빈 이름(index 31) = 부천시(당시 원미·소사·오정 3개 구), 진구 = 부산진구. 여주군·청원군·청주 상당/흥덕구는 2012년 이름 그대로
p.loc[p.district.isna(), "district"] = "부천시"
p["district"] = p.district.replace({"진구": "부산진구"})
code = pd.read_pickle("pe20.pkl").groupby("region").시도.first()
p["시도"] = p.region.map(code)
p["R_1"] = p.P1 / (p.P1 + p.M1); p["R_2"] = p.P2 / (p.P2 + p.M2); p["K"] = p.R_2 / p.R_1; p["R_1sq"] = p.R_1 ** 2
print("행", len(p), "| 전국 분류 박/(박+문)", round(p.P1.sum() / (p.P1 + p.M1).sum(), 4), "미분류", round(p.P2.sum() / (p.P2 + p.M2).sum(), 4),
      "| K", round((p.P2.sum() / (p.P2 + p.M2).sum()) / (p.P1.sum() / (p.P1 + p.M1).sum()), 4),
      "| OR", round((p.P2.sum() / p.M2.sum()) / (p.P1.sum() / p.M1.sum()), 4))

# Step 2. 공개 18Data 구·시·군 합계와 대조 (박근혜 = P1+P2, 문재인 = M1+M2)
D = pd.read_excel("Kelec18to21/corrected_data/K18to21charts_corrected.xlsx", "18Data", header=None).iloc[3:]
D = D[(D[2] == "합계") & (D[1] != "합계")]
SIDO = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도", "세종특별자치시": "충청남도"}
pub = pd.DataFrame({"시도": D[0].replace(SIDO).values, "구": D[1].values, "투표수": num(D[5]).values, "박근혜": num(D[6]).values, "문재인": num(D[7]).values})
pub.loc[pub.구 == "세종특별자치시", "구"] = "세종시"
pub.loc[pub.구.astype(str).str.startswith("부천시"), "구"] = "부천시"          # 원미·소사·오정 합산
pub = pub.groupby(["시도", "구"], as_index=False)[["투표수", "박근혜", "문재인"]].sum()
p["구"] = [g.replace("울산", "") if s == "울산광역시" else g for s, g in zip(p.시도, p.district)]
x = p.merge(pub, on=["시도", "구"], how="left", indicator=True)
print("공개자료 결합:", x._merge.value_counts().to_dict())
if (x._merge != "both").any(): print(x[x._merge != "both"][["index", "시도", "district"]].to_string(index=False))
x["d박"] = x.P1 + x.P2 - x.박근혜; x["d문"] = x.M1 + x.M2 - x.문재인; x["d투표"] = x.vote_all - x.투표수
x["rel"] = (x.d박.abs() + x.d문.abs()) / (x.박근혜 + x.문재인)
m_ = x._merge == "both"
print(f"정확히 일치 {int(((x.d박 == 0) & (x.d문 == 0))[m_].sum())} | 차이 2% 미만 {int((x.rel < .02)[m_].sum())} | 2–10% {int(((x.rel >= .02) & (x.rel < .1))[m_].sum())} | 10% 이상 {int((x.rel >= .1)[m_].sum())} | 투표수 일치 {int((x.d투표 == 0)[m_].sum())}")
print("d박·d문 중앙값", x.d박.median(), x.d문.median())
print("차이 2% 이상:"); print(x[m_ & (x.rel >= .02)].sort_values("rel", ascending=False)[["index", "시도", "district", "P1", "P2", "박근혜", "d박", "M1", "M2", "문재인", "d문", "rel", "K"]].round(3).to_string(index=False))
print("P1+M1 >= 투표수 행:", x[(x.P1 + x.M1 >= x.vote_all)][["district"]].values.ravel().tolist())

# Step 3. 회귀 (SAS 재현) 선형 / 2차
m, o = reg(p, "R_2 ~ R_1"); q, _ = reg(p, "R_2 ~ R_1sq + R_1")
print(f"\n선형: R_2 = {m.params.Intercept:.4f} + {m.params.R_1:.4f} R_1 | R2 {m.rsquared:.4f} MSE {m.mse_resid:.5f} n {int(m.nobs)} | 기울기=1 z {(m.params.R_1 - 1) / m.bse.R_1:.2f}")
print(f"2차: R_1sq {q.params.R_1sq:.3f} (t {q.tvalues.R_1sq:.2f}) R2 {q.rsquared:.4f}")
r = m.resid; print(f"잔차: sd {r.std():.4f} 왜도 {stats.skew(r):.2f} 첨도 {stats.kurtosis(r):.2f} Shapiro p {stats.shapiro(r).pvalue:.4f}")
po = p.join(o)
print("\n|RStudent| 상위:"); print(po.reindex(o.RStudent.abs().sort_values(ascending=False).index[:10])[["시도", "district", "R_1", "R_2", "K", "RStudent", "CooksD"]].round(3).to_string(index=False))

# Step 4. 그림 (다른 선거와 같은 형식)
diagnostics(m, o, p.R_2, "Fit Diagnostics for R_2  (18대, 박근혜 분자)", "K18_FitDiagnostics.png")
fig, ax = plt.subplots(figsize=(9.6, 6.2)); fitplot(ax, p, m, "Fit Plot for R_2  (18대, 박근혜 분자)")
ax.set(xlabel="R_1 = 박근혜 / (박근혜+문재인), 분류된 투표지", ylabel="R_2 = 같은 비율, 미분류(재확인) 투표지")
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, frameon=True)
fig.subplots_adjust(left=.07, right=.74, bottom=.17, top=.93); fig.savefig("K18_FitPlot.png", dpi=150)
pd.to_pickle(dict(p=p, x=x, o=o, m=(m.params, m.bse, m.rsquared, m.mse_resid), q=(q.params, q.tvalues)), "pe18_out.pkl")
