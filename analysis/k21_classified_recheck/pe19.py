"""19대(2017) 분류/미분류 분석 — 보수 후보(홍준표) 분자
R1 = H1/(H1+M1) 분류표, R2 = H2/(H2+M2) 미분류(재확인)표, K = R2/R1
출력: pe19_out.pkl, K19_FitPlot.png, K19_FitDiagnostics.png"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
src = open("k21reg.py").read()
exec(src[:src.index("# Step 1.")])
exec(src[src.index("def reg("):src.index("m21, o21 = reg(")])
exec(src[src.index("def stat_box("):src.index("diagnostics(m21,")])
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")

# Step 1. 자료 읽기 (M2 열 이름 뒤 공백 정리), 시도 이름은 20대 코드표 사용
p = pd.read_excel("/root/.claude/uploads/b16eee4c-f64b-565c-be43-dea7f56709b5/50c14bcc-pe19res.xlsx")
p.columns = [c.strip() for c in p.columns]
# 이름 보정: 빈 이름(index 31) = 부천시(가나다순 위치·규모), 여주군 -> 여주시, 진구 -> 부산진구, 청원군 -> 청주시청원구
p.loc[p.district.isna(), "district"] = "부천시"
p["district"] = p.district.replace({"여주군": "여주시", "진구": "부산진구", "청원군": "청주시청원구"})
# 봉화군: 선관위 구·시·군 소계 행에 개표단위 일부(분류기 통과 2,159표)가 빠짐 → 개표단위 합계로 교체 (K18_K19_results.xlsx, 공개 투표수 22,947 에 맞음)
_b = pd.read_excel("k1819res.xlsx", "19대_구시군").set_index("구시군").loc["봉화군"]
p.loc[p.district == "봉화군", ["vote_all", "U_all", "M1", "H1", "M2", "H2"]] = [_b.통과_계, _b.미분류계, _b.분류_문, _b.분류_홍, _b.미분류_문, _b.미분류_홍]
code = pd.read_pickle("pe20.pkl").groupby("region").시도.first()
p["시도"] = p.region.map(code)
p["R_1"] = p.H1 / (p.H1 + p.M1); p["R_2"] = p.H2 / (p.H2 + p.M2); p["K"] = p.R_2 / p.R_1; p["R_1sq"] = p.R_1 ** 2
print("행", len(p), "| 전국 분류 홍/(문+홍)", round(p.H1.sum() / (p.H1 + p.M1).sum(), 4), "미분류", round(p.H2.sum() / (p.H2 + p.M2).sum(), 4),
      "| K", round((p.H2.sum() / (p.H2 + p.M2).sum()) / (p.H1.sum() / (p.H1 + p.M1).sum()), 4),
      "| OR", round((p.H2.sum() / p.M2.sum()) / (p.H1.sum() / p.M1.sum()), 4))

# Step 2. 공개 19Data 구·시·군 합계와 대조 (문재인 = M1+M2, 홍준표 = H1+H2)
D = pd.read_excel("Kelec18to21/corrected_data/K18to21charts_corrected.xlsx", "19Data", header=None).iloc[3:]
D = D[(D[2] == "합계") & (D[1] != "합계")]
SIDO = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도", "세종특별자치시": "충청남도"}
pub = pd.DataFrame({"시도": D[0].replace(SIDO).values, "구": D[1].values, "투표수": num(D[5]).values, "문재인": num(D[6]).values, "홍준표": num(D[7]).values})
pub.loc[pub.구 == "세종특별자치시", "구"] = "세종시"
# 청주 서원구는 pe19res 에서 흥덕구 행에 합쳐져 있음 -> 공개자료도 합침
pub.loc[pub.구 == "청주시서원구", "구"] = "청주시흥덕구"
pub = pub.groupby(["시도", "구"], as_index=False)[["투표수", "문재인", "홍준표"]].sum()
def key(s, g):
    g = str(g)
    if s == "울산광역시": g = g.replace("울산", "")
    return g
p["구"] = [key(s, g) for s, g in zip(p.시도, p.district)]
x = p.merge(pub, on=["시도", "구"], how="left", indicator=True)
print("공개자료 결합:", x._merge.value_counts().to_dict())
if (x._merge != "both").any(): print(x[x._merge != "both"][["시도", "district"]].to_string(index=False))
x["d문"] = x.M1 + x.M2 - x.문재인; x["d홍"] = x.H1 + x.H2 - x.홍준표; x["d투표"] = x.vote_all - x.투표수
x["rel"] = (x.d문.abs() + x.d홍.abs()) / (x.문재인 + x.홍준표)
m_ = x._merge == "both"
print(f"정확히 일치 {int(((x.d문 == 0) & (x.d홍 == 0))[m_].sum())} | 차이 2% 미만 {int((x.rel < .02)[m_].sum())} | 2% 이상 {int((x.rel >= .02)[m_].sum())} | 투표수 일치 {int((x.d투표 == 0)[m_].sum())}")
print("차이 큰 단위:"); print(x[m_ & (x.rel >= .02)].sort_values("rel", ascending=False)[["시도", "district", "M1", "M2", "문재인", "d문", "H1", "H2", "홍준표", "d홍", "rel", "K"]].round(3).to_string(index=False))
# 분류 합이 총투표수와 같은 행 (20대 제천 유형)
print("M1+H1 >= 투표수 행:", x[(x.M1 + x.H1 >= x.vote_all)][["district"]].values.ravel().tolist())

# Step 3. 회귀 (SAS 재현) 선형 / 2차
m, o = reg(p, "R_2 ~ R_1"); q, _ = reg(p, "R_2 ~ R_1sq + R_1")
print(f"\n선형: R_2 = {m.params.Intercept:.4f} + {m.params.R_1:.4f} R_1 | R2 {m.rsquared:.4f} MSE {m.mse_resid:.5f} n {int(m.nobs)} | 기울기=1 z {(m.params.R_1 - 1) / m.bse.R_1:.2f}")
print(f"2차: R_1sq {q.params.R_1sq:.3f} (t {q.tvalues.R_1sq:.2f}) R2 {q.rsquared:.4f}")
r = m.resid; print(f"잔차: sd {r.std():.4f} 왜도 {stats.skew(r):.2f} 첨도 {stats.kurtosis(r):.2f} Shapiro p {stats.shapiro(r).pvalue:.4f}")
po = p.join(o)
print("\n|RStudent| 상위:"); print(po.reindex(o.RStudent.abs().sort_values(ascending=False).index[:10])[["시도", "district", "R_1", "R_2", "K", "RStudent", "CooksD"]].round(3).to_string(index=False))

# Step 4. 시도별 OR (구·시·군 군집 델타법)
def lor_ci(df, y2="H2", l2="M2", y1="H1", l1="M1"):
    A, B, C, Dd = (df[c].astype(float) for c in (y2, l2, y1, l1))
    lor = np.log(A.sum()) - np.log(B.sum()) - np.log(C.sum()) + np.log(Dd.sum()); n = len(df)
    z = A / A.sum() - B / B.sum() - C / C.sum() + Dd / Dd.sum()
    se = np.sqrt(n / (n - 1) * (z ** 2).sum()) if n > 1 else np.nan; t = stats.t.ppf(.975, max(n - 1, 1))
    return pd.Series(dict(OR=np.exp(lor), lo=np.exp(lor - t * se), hi=np.exp(lor + t * se), n=n))
P = p.groupby("시도").apply(lor_ci).sort_values("OR"); P.loc["전국"] = lor_ci(p)
print("\n시도별 OR (19대, 홍준표 분자)"); print(P.round(3).to_string())

# Step 5. 그림 (21대와 같은 형식)
diagnostics(m, o, p.R_2, "Fit Diagnostics for R_2  (19대, 홍준표 분자)", "K19_FitDiagnostics.png")
fig, ax = plt.subplots(figsize=(9.6, 6.2)); fitplot(ax, p, m, "Fit Plot for R_2  (19대, 홍준표 분자)")
ax.set(xlabel="R_1 = 홍준표 / (문재인+홍준표), 분류된 투표지", ylabel="R_2 = 같은 비율, 미분류(재확인) 투표지")
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.1), ncol=3, frameon=True)
fig.subplots_adjust(left=.07, right=.74, bottom=.17, top=.93); fig.savefig("K19_FitPlot.png", dpi=150)
pd.to_pickle(dict(p=p, x=x, o=o, P=P, m=(m.params, m.bse, m.rsquared, m.mse_resid), q=(q.params, q.tvalues)), "pe19_out.pkl")
