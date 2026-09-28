"""투표구 단위 R1 통제 회귀
결과: r1reg_out.pkl (계수표들), 콘솔 요약"""
import pandas as pd, numpy as np, statsmodels.api as sm, statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")

# Step 1. 데이터: 투표구별 분류표·재확인표 (제외 행, 재외, 재확인 0인 곳 제외)
d = pd.read_pickle("prec.pkl")
d = d[d.구분.isin(["선거일", "관내사전", "관외사전"])].copy()
d["k"] = d.재확인_김문수; d["n"] = d.재확인_이재명 + d.재확인_김문수
d = d[d.n > 0].copy()
# R1 로짓 (0 대비 0.5 보정)
d["lr1"] = np.log((d.분류_김문수 + .5) / (d.분류_이재명 + .5))
d["lr2"] = np.log((d.k + .5) / (d.n - d.k + .5))
d["gu"] = d.시도명 + " " + d.구시군명
d["구분"] = pd.Categorical(d.구분, ["선거일", "관내사전", "관외사전"])
d["시도"] = pd.Categorical(d.시도명, ["서울특별시"] + sorted(set(d.시도명) - {"서울특별시"}))
print("투표구", len(d), "구·시·군", d.gu.nunique())

def fit(formula, offset=None):
    """이항 GLM (재확인표 중 김문수 표 / 재확인 양자 표), 구·시·군 군집 강건 SE"""
    m = smf.glm(formula, d, family=sm.families.Binomial(), var_weights=None,
                freq_weights=None, offset=offset,
                exposure=None).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.gu)[0]})
    return m
d["prop"] = d.k / d.n
GLM = lambda f, off=None: smf.glm(f, d, family=sm.families.Binomial(), var_weights=d.n, offset=off).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(d.gu)[0]})

# Step 2. M0: 기울기 1 고정 (offset) -> 전국 공통 OR
M0 = GLM("prop ~ 1", d.lr1)
# Step 3. M1: 기울기 자유 -> b = 1 검정
M1 = GLM("prop ~ lr1")
# Step 4. M2: + 투표구분
M2 = GLM("prop ~ lr1 + C(구분)")
# Step 5. M3: + 시도 고정효과
M3 = GLM("prop ~ lr1 + C(구분) + C(시도)")
# Step 6. M4: 투표구분별 기울기
M4 = GLM("prop ~ lr1 * C(구분) + C(시도)")
# 비교용: R1 통제 없이 시도 효과 (기울기 1 고정 = 원래 OR 비교와 같은 척도)
M3o = GLM("prop ~ C(구분) + C(시도)", d.lr1)

def row(m, name, lab=None):
    b, se = m.params[name], m.bse[name]
    return dict(항=lab or name, 계수=b, SE=se, z=b / se, p=m.pvalues[name], OR=np.exp(b), OR_lo=np.exp(b - 1.96 * se), OR_hi=np.exp(b + 1.96 * se))

out = {}
print("\n[M0] 기울기 1 고정: 공통 log OR", round(M0.params["Intercept"], 4), "OR", round(np.exp(M0.params["Intercept"]), 3))
b, se = M1.params["lr1"], M1.bse["lr1"]
print(f"[M1] 기울기 b = {b:.4f} (SE {se:.4f}), b=1 검정 z = {(b-1)/se:.2f}; 절편 {M1.params['Intercept']:.4f}")
for m, nm in [(M2, "M2"), (M3, "M3")]:
    b, se = m.params["lr1"], m.bse["lr1"]
    print(f"[{nm}] b = {b:.4f} (SE {se:.4f}), b=1 z = {(b-1)/se:.2f}")
    for g in ["관내사전", "관외사전"]:
        r = row(m, f"C(구분)[T.{g}]"); print(f"     {g} vs 선거일: OR비 {r['OR']:.3f} [{r['OR_lo']:.3f}, {r['OR_hi']:.3f}] p={r['p']:.2g}")
print("[M4] 투표구분별 기울기:", {g: round(M4.params["lr1"] + (M4.params.get(f"lr1:C(구분)[T.{g}]", 0)), 3) for g in ["선거일", "관내사전", "관외사전"]})

# Step 7. 시도 효과: R1 통제 전(기울기 1 고정) vs 후(기울기 자유)
S = [s for s in d.시도.cat.categories if s != "서울특별시"]
T = pd.DataFrame([dict(시도=s, 통제전_OR비=np.exp(M3o.params[f"C(시도)[T.{s}]"]), 통제후_OR비=np.exp(M3.params[f"C(시도)[T.{s}]"]),
                       통제후_lo=np.exp(M3.params[f"C(시도)[T.{s}]"] - 1.96 * M3.bse[f"C(시도)[T.{s}]"]),
                       통제후_hi=np.exp(M3.params[f"C(시도)[T.{s}]"] + 1.96 * M3.bse[f"C(시도)[T.{s}]"]),
                       p=M3.pvalues[f"C(시도)[T.{s}]"]) for s in S])
R1m = d.groupby("시도명").apply(lambda x: x.분류_김문수.sum() / (x.분류_김문수 + x.분류_이재명).sum())
T["R1"] = T.시도.map(R1m); T = T.sort_values("R1")
print("\n시도 효과 (서울 대비 OR비) — 통제 전 vs R1 통제 후"); print(T.round(3).to_string(index=False))
sd_before, sd_after = np.log(T.통제전_OR비).std(), np.log(T.통제후_OR비).std()
print(f"시도 간 log OR비 표준편차: 통제 전 {sd_before:.3f} → 통제 후 {sd_after:.3f} ({(1-sd_after/sd_before)*100:.0f}% 감소)")
print("통제 후 5% 유의 시도:", list(T[T.p < .05].시도))

# Step 8. 과대산포 확인 (피어슨 카이제곱/자유도)
print("\n과대산포 φ (M3):", round(M3.pearson_chi2 / M3.df_resid, 2))

# Step 9. 결과 표 저장
coef = lambda m: pd.DataFrame([row(m, k) for k in m.params.index])
out = dict(d=d, M0=M0, M1=M1, M2=M2, M3=M3, M4=M4, T=T,
           coef={n: coef(m) for n, m in [("M1", M1), ("M2", M2), ("M3", M3), ("M4", M4)]})
pd.to_pickle({k: v for k, v in out.items() if k in ("T", "coef")}, "r1reg_out.pkl")
d[["시도명", "구시군명", "읍면동명", "투표구명", "구분", "분류_이재명", "분류_김문수", "재확인_이재명", "재확인_김문수", "lr1", "lr2", "n"]].to_pickle("r1reg_d.pkl")
