"""후보별 K 와 60대 이상 비율 (구·시·군). log K_a ~ over60 (단순), log K_a ~ over60 + R1 (보수 주 후보 분류표 비율 통제), HC3"""
import pandas as pd, numpy as np, openpyxl, statsmodels.formula.api as smf
res = []
def fit(d, cand, ref, e, age_col="over60"):
    d = d.copy(); d["lk"] = np.log((d[f"U_{cand}"] / d[f"U_{ref}"]) / (d[f"C_{cand}"] / d[f"C_{ref}"]))
    d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=["lk", age_col, "R1"])
    a = smf.ols(f"lk ~ {age_col}", d).fit(cov_type="HC3"); b = smf.ols(f"lk ~ {age_col} + R1", d).fit(cov_type="HC3")
    res.append(dict(선거=e, 후보=cand, 기준=ref, n=len(d), 상관=np.corrcoef(d.lk, d[age_col])[0, 1],
                    기울기_10pt=a.params[age_col] * .1, t=a.tvalues[age_col], 기울기_R1통제_10pt=b.params[age_col] * .1, t_R1통제=b.tvalues[age_col]))

# 18대: 뉴스타파 60대이상(%) → 비율
N = pd.read_pickle("nec18.pkl")
d = pd.DataFrame({"C_박": N.분류_박근혜, "C_문": N.분류_문재인, "C_기타": N.분류_기타후보, "U_박": N.미분류_박근혜, "U_문": N.미분류_문재인, "U_기타": N.미분류_기타후보,
                  "over60": N["60대이상"] / 100}); d["R1"] = d.C_박 / (d.C_박 + d.C_문)
for c in ["박", "기타"]: fit(d, c, "문", "18대")

# 19대: nec19_merge (data19 over60)
m = pd.read_pickle("nec19_merge.pkl")
d = pd.DataFrame({f"{p}_{c}": m[f"{p}{c}"] for p in "CU" for c in ["문", "홍", "안", "유", "심", "기타"]}); d["over60"] = m.over60.astype(float); d["R1"] = d.C_홍 / (d.C_홍 + d.C_문)
for c in ["홍", "안", "유", "심", "기타"]: fit(d, c, "문", "19대")

# 21대: 판독 자료를 구·시·군으로 합산, data21 over60 (20대 기준 연령) 과 이름으로 연결
P = pd.read_csv("bundle/corrected_data/k21_precinct_classified_recheck.csv"); P = P[P["제외 사유"].isna()]
cand = ["이재명", "김문수", "이준석", "권영국", "송진호"]
g = P.groupby(["시도명", "구시군명"])[[f"분류_{c}" for c in cand] + [f"재확인_{c}" for c in cand]].sum().reset_index()
g.columns = ["시도명", "구시군명"] + [f"C_{c}" for c in cand] + [f"U_{c}" for c in cand]
wv = openpyxl.load_workbook("k18to21_수정본.xlsx", data_only=True)["data21"]; h = [c.value for c in wv[1]]
D = pd.DataFrame([[c.value for c in wv[r]] for r in range(2, 251)], columns=h)
k = pd.read_pickle("k21reg_out.pkl")["k"][["region", "district", "index"]]
SH = lambda s: {"강원특별자치도": "강원", "전북특별자치도": "전북", "제주특별자치도": "제주", "세종특별자치시": "충남"}.get(s, s[:2] if s[2:] in ("도", "시") else ({"경상북도": "경북", "경상남도": "경남", "전라남도": "전남", "충청북도": "충북", "충청남도": "충남"}.get(s, s[:2])))
g["key"] = g.구시군명; D["key"] = D.district21
x = g.merge(D[["key", "over60"]].drop_duplicates("key"), on="key", how="left")
print("21대 연령 연결", int(x.over60.notna().sum()), "/", len(x))
x = x.dropna(subset=["over60"]); x["over60"] = x.over60.astype(float); x["R1"] = x.C_김문수 / (x.C_김문수 + x.C_이재명)
for c in cand[1:]: fit(x, c, "이재명", "21대")
T = pd.DataFrame(res); pd.set_option("display.width", 220); print(T.round(3).to_string(index=False)); T.to_pickle("candage.pkl")
