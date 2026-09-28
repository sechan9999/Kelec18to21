"""시도별 재확인 OR 신뢰구간(20대·21대) + 구·시·군 20→21 변화 분석 -> ci_out.pkl"""
import pandas as pd, numpy as np
from scipy import stats
U = pd.read_pickle("age_units.pkl").reset_index(drop=True)

# Step 1. 군집 선형화(델타법) 분산: log OR = log ΣY2 − log ΣL2 − log ΣY1 + log ΣL1
def lor_ci(df, y2, l2, y1, l1, level=.95):
    A, B, C, D = (df[c].astype(float) for c in (y2, l2, y1, l1))
    lor = np.log(A.sum()) - np.log(B.sum()) - np.log(C.sum()) + np.log(D.sum())
    woolf = np.sqrt(1 / A.sum() + 1 / B.sum() + 1 / C.sum() + 1 / D.sum())
    n = len(df)
    z = A / A.sum() - B / B.sum() - C / C.sum() + D / D.sum()          # 군집별 영향값 (합 0)
    se_cl = np.sqrt(n / (n - 1) * (z ** 2).sum()) if n > 1 else np.nan
    t = stats.t.ppf(.5 + level / 2, max(n - 1, 1))
    return dict(OR=np.exp(lor), 군집수=n, SE_woolf=woolf, W_lo=np.exp(lor - 1.96 * woolf), W_hi=np.exp(lor + 1.96 * woolf),
                SE_군집=se_cl, C_lo=np.exp(lor - t * se_cl), C_hi=np.exp(lor + t * se_cl))

rows = []
for s, z in list(U.groupby("시도")) + [("전국", U)]:
    a = lor_ci(z, "Y2", "L2", "Y1", "L1"); b = lor_ci(z, "재확인_김문수", "재확인_이재명", "분류_김문수", "분류_이재명")
    rows.append({"시도": s, **{f"20_{k}": v for k, v in a.items()}, **{f"21_{k}": v for k, v in b.items()}})
P = pd.DataFrame(rows)

# Step 2. 21대는 투표구를 군집으로 한 구간도 (세종 → 충남)
d = pd.read_excel("ALL17.xlsx", "투표구별"); d = d[d.판독방식 != "제외"].copy()
d["시도명"] = d.시도명.replace({"세종특별자치시": "충청남도"})
d = d[(d.재확인_김문수 + d.재확인_이재명) > 0]
pp = {s: lor_ci(z, "재확인_김문수", "재확인_이재명", "분류_김문수", "분류_이재명") for s, z in list(d.groupby("시도명")) + [("전국", d)]}
P["21_투표구수"] = P.시도.map(lambda s: pp[s]["군집수"]); P["21_P_lo"] = P.시도.map(lambda s: pp[s]["C_lo"]); P["21_P_hi"] = P.시도.map(lambda s: pp[s]["C_hi"])
# 21대 투표구분별(관내사전·선거일) 투표구 군집 구간
for g in ["관내사전", "선거일"]:
    q = {s: lor_ci(z, "재확인_김문수", "재확인_이재명", "분류_김문수", "분류_이재명") for s, z in list(d[d.구분 == g].groupby("시도명")) + [("전국", d[d.구분 == g])]}
    P[f"21{g}_OR"] = P.시도.map(lambda s: q[s]["OR"]); P[f"21{g}_lo"] = P.시도.map(lambda s: q[s]["C_lo"]); P[f"21{g}_hi"] = P.시도.map(lambda s: q[s]["C_hi"])
# 20→21 시도 변화의 유의성 (구·시·군 군집, 두 선거 독립 가정)
P["Δlog"] = np.log(P["21_OR"]) - np.log(P["20_OR"]); P["Δ_SE"] = np.sqrt(P["20_SE_군집"] ** 2 + P["21_SE_군집"] ** 2)
P["Δ_z"] = P.Δlog / P.Δ_SE

# Step 3. 구·시·군 변화: Δ = log OR21 − log OR20, 표본 분산 = Woolf 분산 합
v = lambda a, b, c, e: 1 / a + 1 / b + 1 / c + 1 / e
U["v20"] = v(U.Y2, U.L2, U.Y1, U.L1); U["v21"] = v(U.재확인_김문수, U.재확인_이재명, U.분류_김문수, U.분류_이재명)
U["Δ"] = U.lor21 - U.lor20; U["vΔ"] = U.v20 + U.v21; U["zΔ"] = U.Δ / np.sqrt(U.vΔ)
# DerSimonian–Laird: 표본 오차 이상의 실제 변화 분산 τ²
wv = 1 / U.vΔ; mu = (wv * U.Δ).sum() / wv.sum(); Q = (wv * (U.Δ - mu) ** 2).sum(); k = len(U)
tau2 = max(0, (Q - (k - 1)) / (wv.sum() - (wv ** 2).sum() / wv.sum())); I2 = max(0, (Q - (k - 1)) / Q)
# 시도 평균 변화를 뺀 뒤(구·시·군 고유 변화)도 같은 계산
U["Δw"] = U.Δ - U.groupby("시도").apply(lambda z: np.average(z.Δ, weights=1 / z.vΔ)).reindex(U.시도).values
Qw = (wv * U.Δw ** 2).sum(); tau2w = max(0, (Qw - (k - 16)) / (wv.sum() - (wv ** 2).sum() / wv.sum()))
# 신뢰도: 관측 분산 중 실제 분산 몫 (두 선거 각각)
def rel(lor, var):
    w = 1 / var; m = (w * lor).sum() / w.sum(); q = (w * (lor - m) ** 2).sum()
    t2 = max(0, (q - (len(lor) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())); return t2, t2 / (t2 + np.median(var))
t20, r20 = rel(U.lor20, U.v20); t21, r21 = rel(U.lor21, U.v21)
S = dict(k=k, mu=mu, Q=Q, tau=np.sqrt(tau2), I2=I2, tau_w=np.sqrt(tau2w), sd_obs=U.Δ.std(), se_med=np.sqrt(U.vΔ.median()),
         n_sig=int((U.zΔ.abs() > 1.96).sum()), n_sig_up=int((U.zΔ > 1.96).sum()), n_sig_dn=int((U.zΔ < -1.96).sum()),
         tau20=np.sqrt(t20), tau21=np.sqrt(t21), rel20=r20, rel21=r21,
         corr=np.corrcoef(U.lor20, U.lor21)[0, 1], corr_w=np.corrcoef(U.lor20 - U.groupby("시도").lor20.transform("mean"), U.lor21 - U.groupby("시도").lor21.transform("mean"))[0, 1])
# 변화 크기 분포 (OR 배율)
q = np.exp(U.Δ).quantile([.05, .25, .5, .75, .95])
S["ratio_q"] = q.to_dict(); S["share_within10"] = float((np.exp(U.Δ).between(1 / 1.1, 1.1)).mean()); S["share_over25"] = float(((np.exp(U.Δ) > 1.25) | (np.exp(U.Δ) < 0.8)).mean())
pd.to_pickle(dict(P=P, U=U, S=S), "ci_out.pkl")

pd.set_option("display.width", 250)
print(P[["시도", "20_OR", "20_W_lo", "20_W_hi", "20_C_lo", "20_C_hi", "20_군집수", "21_OR", "21_C_lo", "21_C_hi", "21_P_lo", "21_P_hi", "Δ_z"]].round(3).to_string(index=False))
print({k2: (round(v2, 3) if isinstance(v2, float) else v2) for k2, v2 in S.items() if k2 != "ratio_q"})
print("OR 배율 분위수(21/20):", {k2: round(v2, 3) for k2, v2 in S["ratio_q"].items()})
T = U.assign(OR20=np.exp(U.lor20), OR21=np.exp(U.lor21), 배율=np.exp(U.Δ))[["시도", "단위", "OR20", "OR21", "배율", "zΔ", "n20", "n21"]]
print("\n증가 상위"); print(T.sort_values("zΔ").tail(8).round(3).to_string(index=False))
print("감소 상위"); print(T.sort_values("zΔ").head(8).round(3).to_string(index=False))
