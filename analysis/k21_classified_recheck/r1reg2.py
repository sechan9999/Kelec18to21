"""R1 효과를 구·시·군 안(within)과 사이(between)로 분해 + 같은 읍면동 안 투표구분 비교"""
import pandas as pd, numpy as np, statsmodels.api as sm, statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")
d = pd.read_pickle("r1reg_d.pkl").reset_index(drop=True)
d["k"] = d.재확인_김문수; d["prop"] = d.k / d.n
d["gu"] = d.시도명 + " " + d.구시군명
d["dong"] = d.gu + " " + d.읍면동명.astype(str)
d["구분"] = pd.Categorical(d.구분.astype(str), ["선거일", "관내사전", "관외사전"])
g = pd.factorize(d.gu)[0]
GLM = lambda f: smf.glm(f, d, family=sm.families.Binomial(), var_weights=d.n).fit(cov_type="cluster", cov_kwds={"groups": g})

# Step 1. 구·시·군 평균 R1 로짓 (분류표 가중) 과 편차
w = d.분류_이재명 + d.분류_김문수
d["lr1_b"] = d.groupby("gu").lr1.transform(lambda s: np.average(s, weights=w[s.index]))
d["lr1_w"] = d.lr1 - d.lr1_b
d["sido_b"] = d.groupby("시도명").lr1.transform(lambda s: np.average(s, weights=w[s.index]))
d["gu_dev"] = d.lr1_b - d.sido_b

# Step 2. within-between 모형 (투표구분 통제)
WB = GLM("prop ~ lr1_w + lr1_b + C(구분)")
# Step 3. 세 수준: 투표구(구 안) / 구(시도 안) / 시도
W3 = GLM("prop ~ lr1_w + gu_dev + sido_b + C(구분)")
# Step 4. 구·시·군 고정효과 모형 (구 안 비교만)
FE = GLM("prop ~ lr1 + C(구분) + C(gu)")

def show(m, keys, title):
    print(f"\n[{title}]")
    for k in keys:
        b, se = m.params[k], m.bse[k]
        print(f"  {k:22s} {b:7.3f} (SE {se:.3f})  95% [{b-1.96*se:.3f}, {b+1.96*se:.3f}]")
show(WB, ["lr1_w", "lr1_b", "C(구분)[T.관내사전]", "C(구분)[T.관외사전]"], "within-between")
show(W3, ["lr1_w", "gu_dev", "sido_b", "C(구분)[T.관내사전]", "C(구분)[T.관외사전]"], "투표구 / 구 / 시도 세 수준")
show(FE, ["lr1", "C(구분)[T.관내사전]", "C(구분)[T.관외사전]"], "구·시·군 고정효과")

# Step 5. 같은 읍면동 안 비교: 선형 근사(WLS), 종속 = 투표구 log OR = lr2 - lr1, 읍면동 고정효과 흡수
#   관내사전 투표구와 같은 동의 선거일 투표구만 있는 동으로 한정
d["lor"] = d.lr2 - d.lr1
has = d.groupby("dong").구분.transform(lambda s: s.astype(str).isin(["관내사전"]).any() and s.astype(str).isin(["선거일"]).any())
x = d[has & d.구분.isin(["관내사전", "선거일"])].copy()
x["wt"] = 1 / (1 / (x.k + .5) + 1 / (x.n - x.k + .5))            # log OR 분산의 역수 (재확인 쪽)
x["pre"] = (x.구분 == "관내사전").astype(float)
for c in ["lor", "pre", "lr1"]:
    x[c + "_d"] = x[c] - x.groupby("dong")[c].transform(lambda s: np.average(s, weights=x.wt[s.index]))
m = sm.WLS(x.lor_d, x[["pre_d", "lr1_d"]], weights=x.wt).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(x.gu)[0]})
print(f"\n[같은 읍면동 안, 선형 근사] 읍면동 {x.dong.nunique()}개, 투표구 {len(x)}")
for k in ["pre_d", "lr1_d"]:
    b, se = m.params[k], m.bse[k]; print(f"  {k:8s} {b:7.3f} (SE {se:.3f})  → exp {np.exp(b):.3f} [{np.exp(b-1.96*se):.3f}, {np.exp(b+1.96*se):.3f}]")
m0 = sm.WLS(x.lor_d, x[["pre_d"]], weights=x.wt).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(x.gu)[0]})
b, se = m0.params["pre_d"], m0.bse["pre_d"]
print(f"  (R1 통제 없이) 관내사전 효과 exp {np.exp(b):.3f} [{np.exp(b-1.96*se):.3f}, {np.exp(b+1.96*se):.3f}]")

# Step 6. 그림용 구간 평균: 투표구분별 R1 로짓 20분위
d["bin"] = d.groupby("구분", observed=True).lr1.transform(lambda s: pd.qcut(s, 20, labels=False, duplicates="drop"))
B = d.groupby(["구분", "bin"], observed=True).apply(lambda z: pd.Series(dict(
    lr1=np.average(z.lr1, weights=z.n), lr2=np.log(z.k.sum() / (z.n.sum() - z.k.sum())), n=z.n.sum(), m=len(z)))).reset_index()
S = d.groupby("시도명").apply(lambda z: pd.Series(dict(
    lr1=np.log(z.분류_김문수.sum() / z.분류_이재명.sum()), lr2=np.log(z.k.sum() / (z.n.sum() - z.k.sum())), n=z.n.sum()))).reset_index()
pd.to_pickle(dict(B=B, S=S, WB=WB.params, W3=(W3.params, W3.bse), FE=(FE.params[["lr1", "C(구분)[T.관내사전]", "C(구분)[T.관외사전]"]], FE.bse[["lr1", "C(구분)[T.관내사전]", "C(구분)[T.관외사전]"]]),
               dong=(m.params, m.bse, m0.params, m0.bse, x.dong.nunique(), len(x))), "r1reg2_out.pkl")
print("\n시도 수준 (그림용):"); print(S.assign(OR=lambda s: np.exp(s.lr2 - s.lr1)).round(3).sort_values("lr1").to_string(index=False))
