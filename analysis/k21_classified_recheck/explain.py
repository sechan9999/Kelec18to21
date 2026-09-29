"""설명력 있는 지표 계산
A. 후보 지지의 고령 기울기(구·시·군 득표율 ~ 60대 이상 비율의 표준화 상관) vs 후보 log K
B. 구·시·군 미분류율 ~ 60대 이상 비율 (선거별)
C. 후보별 미분류율 ~ 60대 이상 (주 후보 둘 다 오르는가)"""
import pandas as pd, numpy as np, openpyxl
rows, dist = [], {}
def cand_rows(e, C, U, age, ref, names):
    tot = C.sum(axis=1) + U.sum(axis=1)
    for a in names:
        share = (C[a] + U[a]) / tot
        k = (U[a].sum() / U[ref].sum()) / (C[a].sum() / C[ref].sum())
        rows.append(dict(선거=e, 후보=a, 기준=ref, 고령상관=np.corrcoef(share, age)[0, 1], logK=np.log(k), K=k,
                         미분류율=U[a].sum() / (C[a].sum() + U[a].sum())))
# 18대
N = pd.read_pickle("nec18.pkl"); nm = ["박근혜", "문재인", "기타"]
C = N[["분류_박근혜", "분류_문재인", "분류_기타후보"]].set_axis(nm, axis=1); U = N[["미분류_박근혜", "미분류_문재인", "미분류_기타후보"]].set_axis(nm, axis=1)
age = N["60대이상"] / 100; cand_rows("18대", C, U, age, "문재인", ["박근혜", "기타"])
dist["18대"] = pd.DataFrame({"age": age, "urate": N.미분류_계 / N.분류기개표_계, **{f"u_{a}": U[a] / (C[a] + U[a]) for a in nm}})
# 19대
m = pd.read_pickle("nec19_merge.pkl"); c19 = ["문", "홍", "안", "유", "심", "기타"]; n19 = ["문재인", "홍준표", "안철수", "유승민", "심상정", "기타"]
C = pd.DataFrame({n: m[f"C{c}"] for c, n in zip(c19, n19)}); U = pd.DataFrame({n: m[f"U{c}"] for c, n in zip(c19, n19)}); age = m.over60.astype(float)
cand_rows("19대", C, U, age, "문재인", n19[1:])
dist["19대"] = pd.DataFrame({"age": age, "urate": m.U계 / m.T계, **{f"u_{a}": U[a] / (C[a] + U[a]) for a in n19}})
# 20대 (윤·이만)
p = pd.read_pickle("pe20.pkl").dropna(subset=["Y1", "L1", "Y2", "L2", "over60"])
dist["20대"] = pd.DataFrame({"age": p.over60.astype(float), "urate": p.U_all / p.vote_all, "u_윤석열": p.Y2 / (p.Y1 + p.Y2), "u_이재명": p.L2 / (p.L1 + p.L2)})
# 21대
P = pd.read_csv("bundle/corrected_data/k21_precinct_classified_recheck.csv"); P = P[P["제외 사유"].isna()]
cand = ["이재명", "김문수", "이준석", "권영국", "송진호"]
g = P.groupby(["시도명", "구시군명"])[[f"분류_{c}" for c in cand] + [f"재확인_{c}" for c in cand]].sum().reset_index()
wv = openpyxl.load_workbook("k18to21_수정본.xlsx", data_only=True)["data21"]; h = [c.value for c in wv[1]]
D = pd.DataFrame([[c.value for c in wv[r]] for r in range(2, 251)], columns=h)
g = g.merge(D[["district21", "over60"]].drop_duplicates("district21"), left_on="구시군명", right_on="district21").dropna(subset=["over60"])
C = pd.DataFrame({c: g[f"분류_{c}"] for c in cand}); U = pd.DataFrame({c: g[f"재확인_{c}"] for c in cand}); age = g.over60.astype(float)
cand_rows("21대", C, U, age, "이재명", cand[1:])
dist["21대"] = pd.DataFrame({"age": age, "urate": U.sum(axis=1) / (C.sum(axis=1) + U.sum(axis=1)), **{f"u_{a}": U[a] / (C[a] + U[a]) for a in cand}})
# 기준 후보(민주)도 고령상관 기록
for e, (C_, ref) in {"18대": (None, "문재인"), "19대": (None, "문재인"), "21대": (None, "이재명")}.items(): pass
R = pd.DataFrame(rows); pd.set_option("display.width", 200); print(R.round(3).to_string(index=False))
print("고령상관 vs logK 상관 (군소 제외):", round(np.corrcoef(R[~R.후보.isin(["기타", "송진호"])].고령상관, R[~R.후보.isin(["기타", "송진호"])].logK)[0, 1], 3),
      "| 전체:", round(np.corrcoef(R.고령상관, R.logK)[0, 1], 3))
for e, d in dist.items():
    s = np.polyfit(d.age, d.urate, 1)
    print(e, "미분류율 ~ 60대이상 상관", round(np.corrcoef(d.age, d.urate)[0, 1], 3), "기울기(10%p)", round(s[0] * .1 * 100, 2), "%p",
          "| 후보별 미분류율 상관:", {c[2:]: round(np.corrcoef(d.age, d[c])[0, 1], 2) for c in d.columns if c.startswith("u_")})
pd.to_pickle(dict(R=R, dist=dist), "explain.pkl")
