"""무효표와 재확인표(K, OR)의 관계 — 21대 투표구 단위
출력: inv_out.pkl, 콘솔 요약"""
import pandas as pd, numpy as np, statsmodels.api as sm, statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")
num = lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")

# Step 1. 공개 21Data: 투표구별 투표수·무효투표수
P = pd.read_excel("Kelec18to21/corrected_data/K18to21charts_corrected.xlsx", "21Data", header=None).iloc[1:]
P = pd.DataFrame({"시도명": P[0], "구시군명": P[1], "읍면동명": P[2].astype(str), "투표구명": P[3].astype(str).replace("nan", ""),
                  "투표수": num(P[5]), "무효": num(P[11])}).dropna(subset=["투표수", "무효"])

# Step 2. 판독 자료와 결합 (선거일·관내사전·관외사전)
d = pd.read_excel("ALL17.xlsx", "투표구별"); d = d[d.구분.isin(["선거일", "관내사전", "관외사전"])].copy()
d["읍면동명"] = d.읍면동명.astype(str); d["투표구명"] = d.투표구명.astype(str).replace("nan", "")
x = d.merge(P, on=["시도명", "구시군명", "읍면동명", "투표구명"], how="left", indicator=True)
print("결합:", x._merge.value_counts().to_dict())
x = x[x._merge == "both"].copy()
C5 = ["이재명", "김문수", "이준석", "권영국", "송진호"]
x["분류계"] = x[[f"분류_{c}" for c in C5]].sum(1); x["재확인유효"] = x[[f"재확인_{c}" for c in C5]].sum(1)
x["유효"] = x.분류계 + x.재확인유효
chk = (x.유효 + x.무효 - x.투표수).abs()
print("검산 (분류+재확인+무효 = 투표수) 일치 비율:", round((chk == 0).mean(), 4), " 불일치 행", int((chk > 0).sum()))
x = x[chk == 0]
x["u"] = x.무효 / x.투표수                      # 무효율
x["rv"] = x.재확인유효 / x.유효                   # 유효표 중 재확인 비율
x["k"] = x.재확인_김문수; x["n"] = x.재확인_김문수 + x.재확인_이재명
x = x[(x.n > 0) & (x.분류_김문수 > 0) & (x.분류_이재명 > 0)].copy()
x["lr1"] = np.log(x.분류_김문수 / x.분류_이재명)
x["gu"] = x.시도명 + " " + x.구시군명
x["구분"] = pd.Categorical(x.구분, ["선거일", "관내사전", "관외사전"])
x["lu"] = np.log((x.무효 + .5) / x.투표수); x["lrv"] = np.log(x.rv.clip(1e-4))
print("투표구", len(x), "| 무효율", round(x.무효.sum() / x.투표수.sum(), 4), "| 재확인 유효 비율", round(x.재확인유효.sum() / x.유효.sum(), 4))

# Step 3. 무효율과 재확인율의 관계 (투표지 표기 품질 공통 요인?)
print("\n[1] 무효율 vs 재확인율 (로그, 투표구분별 상관)")
for g, z in x.groupby("구분", observed=True):
    zz = z[z.무효 > 0]
    print(f"  {g}: r = {np.corrcoef(zz.lu, zz.lrv)[0, 1]:.3f}  (n={len(zz)})  | 구·시·군 평균 뺀 뒤 r = "
          f"{np.corrcoef(zz.lu - zz.groupby('gu').lu.transform('mean'), zz.lrv - zz.groupby('gu').lrv.transform('mean'))[0, 1]:.3f}")

# Step 4. 무효율·재확인율이 재확인표의 김문수 비율(=OR)을 바꾸나: 이항 GLM, offset 없이 lr1 통제, 구·시·군 군집 SE
x["prop"] = x.k / x.n
g = pd.factorize(x.gu)[0]
GLM = lambda f: smf.glm(f, x, family=sm.families.Binomial(), var_weights=x.n).fit(cov_type="cluster", cov_kwds={"groups": g})
x["lu_c"] = x.lu - x.lu.mean(); x["lrv_c"] = x.lrv - x.lrv.mean()
x["lu_w"] = x.lu - x.groupby("gu").lu.transform("mean"); x["lu_b"] = x.groupby("gu").lu.transform("mean") - x.lu.mean()
x["lrv_w"] = x.lrv - x.groupby("gu").lrv.transform("mean"); x["lrv_b"] = x.groupby("gu").lrv.transform("mean") - x.lrv.mean()
M = {"A 기본": "prop ~ lr1 + C(구분)",
     "B +무효율": "prop ~ lr1 + C(구분) + lu_c",
     "C +재확인율": "prop ~ lr1 + C(구분) + lrv_c",
     "D +둘 다": "prop ~ lr1 + C(구분) + lu_c + lrv_c",
     "E 구 안/사이 분해": "prop ~ lr1 + C(구분) + lu_w + lu_b + lrv_w + lrv_b",
     "F 구 고정효과": "prop ~ lr1 + C(구분) + lu + lrv + C(gu)"}
R = {}
print("\n[2] 재확인표 김문수 로짓 ~ R1 로짓 + 투표구분 + 무효율/재확인율 (로그, 계수 = log OR 변화)")
for nm, f in M.items():
    m = GLM(f); R[nm] = m
    keys = [c for c in ["lr1", "C(구분)[T.관내사전]", "lu_c", "lrv_c", "lu_w", "lu_b", "lrv_w", "lrv_b", "lu", "lrv"] if c in m.params]
    print(f"  {nm:14s} " + "  ".join(f"{k}={m.params[k]:+.3f}({m.bse[k]:.3f})" for k in keys))

# 해석용: 무효율·재확인율을 2배로 올릴 때 OR 배율
m = R["D +둘 다"]
for k, lab in [("lu_c", "무효율 2배"), ("lrv_c", "재확인율 2배")]:
    b, s = m.params[k] * np.log(2), m.bse[k] * np.log(2)
    print(f"  {lab}: OR x{np.exp(b):.3f} [{np.exp(b - 1.96 * s):.3f}, {np.exp(b + 1.96 * s):.3f}]")

# Step 5. 구간별 OR (그림용): 무효율 5분위, 재확인율 5분위 × 투표구분
def orbin(z):
    return pd.Series(dict(OR=(z.재확인_김문수.sum() / z.재확인_이재명.sum()) / (z.분류_김문수.sum() / z.분류_이재명.sum()),
                          R1=z.분류_김문수.sum() / (z.분류_김문수 + z.분류_이재명).sum(), u=z.무효.sum() / z.투표수.sum(),
                          rv=z.재확인유효.sum() / z.유효.sum(), 투표구=len(z)))
x["u5"] = x.groupby("구분", observed=True).u.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
x["r5"] = x.groupby("구분", observed=True).rv.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
BU = x.groupby(["구분", "u5"], observed=True).apply(orbin).reset_index()
BR = x.groupby(["구분", "r5"], observed=True).apply(orbin).reset_index()
print("\n[3] 무효율 5분위별 OR"); print(BU.round(4).to_string(index=False))
print("\n[4] 재확인율 5분위별 OR"); print(BR.round(4).to_string(index=False))

# Step 6. 구·시·군 단위: 무효율과 60세 이상 비율 (연령 연결)
U = pd.read_pickle("age_units.pkl")
def unit21(s, g0):
    if s == "세종특별자치시": return "세종시"
    for p in ["부천시", "화성시", "청주시"]:
        if g0.startswith(p): return p
    return g0
x["단위"] = [unit21(s, g0) for s, g0 in zip(x.시도명, x.구시군명)]
x["시도"] = x.시도명.replace({"세종특별자치시": "충청남도"})
A = x.groupby(["시도", "단위"]).agg(무효=("무효", "sum"), 투표수=("투표수", "sum"), 재확인유효=("재확인유효", "sum"), 유효=("유효", "sum"),
                                   Y1=("분류_김문수", "sum"), L1=("분류_이재명", "sum"), Y2=("재확인_김문수", "sum"), L2=("재확인_이재명", "sum")).reset_index()
A = A.merge(U[["시도", "단위", "over60", "under50"]], on=["시도", "단위"])
A["u"] = A.무효 / A.투표수; A["rv"] = A.재확인유효 / A.유효; A["lor"] = np.log(A.Y2 / A.L2) - np.log(A.Y1 / A.L1); A["lr1"] = np.log(A.Y1 / A.L1)
print(f"\n[5] 구·시·군 {len(A)}곳: 상관 (무효율, 60세+) {np.corrcoef(A.u, A.over60)[0, 1]:.3f} | (재확인율, 60세+) {np.corrcoef(A.rv, A.over60)[0, 1]:.3f} | "
      f"(무효율, 재확인율) {np.corrcoef(A.u, A.rv)[0, 1]:.3f} | (log OR, 무효율) {np.corrcoef(A.lor, A.u)[0, 1]:.3f} | (log OR, R1) {np.corrcoef(A.lor, A.lr1)[0, 1]:.3f}")
ma = smf.wls("lor ~ lr1 + np.log(u) + np.log(rv) + over60", A, weights=1 / (1 / A.Y2 + 1 / A.L2 + 1 / A.Y1 + 1 / A.L1)).fit(cov_type="HC3")
print("  구·시·군 WLS: lor ~ lr1 + log무효율 + log재확인율 + 60세+ ->", ma.params.round(3).to_dict(), "p", ma.pvalues.round(3).to_dict())
mu = smf.ols("np.log(u) ~ over60 + lr1", A).fit(cov_type="HC3")
print("  무효율(로그) ~ 60세+ + R1 ->", mu.params.round(3).to_dict(), "p", mu.pvalues.round(4).to_dict(), "R2", round(mu.rsquared, 3))
pd.to_pickle(dict(x=x[["시도명", "구시군명", "구분", "투표구명", "u", "rv", "lr1", "k", "n", "투표수", "무효"]], BU=BU, BR=BR, A=A,
                  R={k: (v.params, v.bse) for k, v in R.items()}, ma=(ma.params, ma.bse, ma.pvalues), mu=(mu.params, mu.pvalues, mu.rsquared)), "inv_out.pkl")
