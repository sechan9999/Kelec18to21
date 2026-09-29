"""18·21대 후보별 K (민주 후보 대비). 20대는 후보별 자료가 없음(pe20res 는 윤·이만)"""
import pandas as pd, numpy as np
out = []
def kk(C, U, a, ref, unit):
    """C, U: 분류·미분류 표 수 DataFrame (열=후보). unit: 구시군 열"""
    tot = dict(분류득표율=C[a].sum() / C.sum(axis=1).sum(), 미분류득표율=U[a].sum() / U.sum(axis=1).sum(),
               K_전국=(U[a].sum() / U[ref].sum()) / (C[a].sum() / C[ref].sum()))
    g = pd.concat([C.add_prefix("C_"), U.add_prefix("U_"), unit.rename("unit")], axis=1).groupby("unit").sum()
    k = (g["U_" + a] / g["U_" + ref]) / (g["C_" + a] / g["C_" + ref]); k = k.replace([np.inf, -np.inf], np.nan).dropna()
    tot.update(K_구시군평균=k.mean(), K_중앙값=k.median(), K_1초과=int((k > 1).sum()), n=len(k))
    return tot

# 18대 (뉴스타파 251곳): 박근혜, 기타 후보 vs 문재인
N = pd.read_pickle("nec18.pkl")
C = N[["분류_박근혜", "분류_문재인", "분류_기타후보"]].set_axis(["박근혜", "문재인", "기타"], axis=1)
U = N[["미분류_박근혜", "미분류_문재인", "미분류_기타후보"]].set_axis(["박근혜", "문재인", "기타"], axis=1)
for a in ["박근혜", "기타"]: out.append(dict(선거="18대", 후보=a, 기준="문재인", **kk(C, U, a, "문재인", N.시도명 + " " + N.구시군명)))

# 19대 (선관위 250곳, 봉화 개표단위 합계): 홍·안·유·심·기타 vs 문재인
G = pd.read_pickle("nec19.pkl"); c19 = ["문", "홍", "안", "유", "심", "기타"]; nm19 = dict(zip(c19, ["문재인", "홍준표", "안철수", "유승민", "심상정", "기타"]))
C = G[[f"C{c}" for c in c19]].set_axis([nm19[c] for c in c19], axis=1); U = G[[f"U{c}" for c in c19]].set_axis([nm19[c] for c in c19], axis=1)
for a in ["홍준표", "안철수", "유승민", "심상정", "기타"]: out.append(dict(선거="19대", 후보=a, 기준="문재인", **kk(C, U, a, "문재인", G.시도 + " " + G.구)))

# 21대 (개표상황표 판독, 투표구·유형 단위): 김문수, 이준석, 권영국, 송진호 vs 이재명
P = pd.read_csv("bundle/corrected_data/k21_precinct_classified_recheck.csv")
P = P[P["제외 사유"].isna()].copy(); cand = ["이재명", "김문수", "이준석", "권영국", "송진호"]
P = P.dropna(subset=[f"분류_{c}" for c in cand] + [f"재확인_{c}" for c in cand])
C = P[[f"분류_{c}" for c in cand]].set_axis(cand, axis=1); U = P[[f"재확인_{c}" for c in cand]].set_axis(cand, axis=1)
unit = P.시도명 + " " + P.구시군명
for a in cand[1:]: out.append(dict(선거="21대", 후보=a, 기준="이재명", **kk(C, U, a, "이재명", unit)))
T = pd.DataFrame(out); pd.set_option("display.width", 220); print(T.round(4).to_string(index=False))
print("21대 행 수", len(P), "구시군", unit.nunique())
# 21대 유형별 전국 K
rows = []
for t, d in P.groupby("구분"):
    Cd, Ud = C.loc[d.index], U.loc[d.index]
    rows.append({"유형": t, **{a: round((Ud[a].sum() / Ud["이재명"].sum()) / (Cd[a].sum() / Cd["이재명"].sum()), 3) for a in cand[1:]}})
print(pd.DataFrame(rows).to_string(index=False))
T.to_pickle("candk.pkl"); pd.DataFrame(rows).to_pickle("candk21_type.pkl")
