"""연령 가설 검정: 구·시·군 단위 이항 GLM (20대, 21대 각각)"""
import pandas as pd, numpy as np, statsmodels.api as sm, statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")
U = pd.read_pickle("age_units.pkl").reset_index(drop=True)
U["시도c"] = pd.Categorical(U.시도, ["서울특별시"] + sorted(set(U.시도) - {"서울특별시"}))
U["o60"] = U.over60 * 10            # 계수 = 60세 이상 비율 10%p당
U["o50"] = U.r50s * 10
cl = pd.factorize(U.시도)[0]

# Step 1. 20대와 21대 OR의 일치도
w = np.sqrt(U.n20 * U.n21)
print(f"[1] 구·시·군 log OR 상관 (20대 vs 21대): {np.corrcoef(U.lor20, U.lor21)[0,1]:.2f}")
dm = lambda s: s - U.groupby("시도")[s.name].transform("mean")
print(f"    시도 평균을 뺀 뒤(시도 안) 상관: {np.corrcoef(dm(U.lor20), dm(U.lor21))[0,1]:.2f}")
print(f"    60세 이상 비율과의 상관: 20대 {np.corrcoef(U.over60, U.lor20)[0,1]:.2f}, 21대 {np.corrcoef(U.over60, U.lor21)[0,1]:.2f}; R1(로짓)과 60세+ 상관: {np.corrcoef(U.over60, U.lr1_21)[0,1]:.2f}")

def glm(y, n, f):
    U["_p"] = U[y] / U[n]
    return smf.glm("_p ~ " + f, U, family=sm.families.Binomial(), var_weights=U[n]).fit(cov_type="cluster", cov_kwds={"groups": cl})
res = {}
for e, k, n, lr1 in [(20, "Y2", "n20", "lr1_20"), (21, "재확인_김문수", "n21", "lr1_21")]:
    print(f"\n===== 제{e}대 =====")
    M = {"A: R1": f"{lr1}", "B: R1+60세+": f"{lr1} + o60", "C: R1+60세++50대": f"{lr1} + o60 + o50",
         "D: R1+시도": f"{lr1} + C(시도c)", "E: R1+60세++시도": f"{lr1} + o60 + C(시도c)"}
    out = {}
    for nm, f in M.items():
        m = glm(k, n, f); out[nm] = m
        s = f"  {nm:18s} R1기울기 {m.params[lr1]:.3f} (SE {m.bse[lr1]:.3f})"
        if "o60" in f: s += f" | 60세+ 10%p당 OR×{np.exp(m.params['o60']):.3f} [{np.exp(m.params['o60']-1.96*m.bse['o60']):.3f}, {np.exp(m.params['o60']+1.96*m.bse['o60']):.3f}]"
        if "o50" in f: s += f" | 50대 10%p당 ×{np.exp(m.params['o50']):.3f} [{np.exp(m.params['o50']-1.96*m.bse['o50']):.3f}, {np.exp(m.params['o50']+1.96*m.bse['o50']):.3f}]"
        s += f" | 편차 {m.deviance:,.0f}"
        print(s)
    fe = lambda m: np.array([m.params[c] for c in m.params.index if c.startswith("C(시도c)")])
    sdD, sdE = fe(out["D: R1+시도"]).std(), fe(out["E: R1+60세++시도"]).std()
    print(f"  시도 효과 표준편차: 연령 통제 전 {sdD:.3f} → 후 {sdE:.3f} ({(1 - sdE / sdD) * 100:.0f}% 감소)")
    # 연령 통제 전후 시도 효과 (서울 대비 OR비)
    T = pd.DataFrame({"시도": [c[len("C(시도c)[T."):-1] for c in out["D: R1+시도"].params.index if c.startswith("C(시도c)")],
                      "통제전": np.exp(fe(out["D: R1+시도"])), "연령통제후": np.exp(fe(out["E: R1+60세++시도"]))})
    res[e] = dict(models={k2: (v.params, v.bse, v.deviance) for k2, v in out.items()}, T=T)
    print(T.round(3).sort_values("통제전").to_string(index=False))
pd.to_pickle(res, "age_reg_out.pkl")
