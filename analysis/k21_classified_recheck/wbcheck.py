"""k18to20_08FEB23.xlsx 숫자 대조: 원자료(pe18/19/20), 공개 최종득표, 시트 내 계산값, 시트 간 복사값
출력: wbcheck.pkl (불일치 목록), 콘솔 요약"""
import pandas as pd, numpy as np, openpyxl
from openpyxl.utils import get_column_letter as L
U = "/root/.claude/uploads/b16eee4c-f64b-565c-be43-dea7f56709b5/"
wv = openpyxl.load_workbook("k18to20.xlsx", data_only=True)

def sheet(name, nrow):
    ws = wv[name]; hdr = [c.value.strip() if isinstance(c.value, str) else c.value for c in ws[1]]
    seen = {}
    for i, h in enumerate(hdr):                      # 같은 이름이 두 번 나오면 두 번째부터 '_2', '_3'
        if h is None: hdr[i] = f"_blank{i}"; continue
        seen[h] = seen.get(h, 0) + 1
        if seen[h] > 1: hdr[i] = f"{h}__{seen[h]}"
    rows = [[c.value for c in ws[r]] for r in range(2, nrow + 1)]
    d = pd.DataFrame(rows, columns=hdr); d["_row"] = range(2, nrow + 1); return d, hdr
d18, h18 = sheet("data18", 250); d19, h19 = sheet("data19", 250); d20, h20 = sheet("data20", 250); kc, hk = sheet("Kcomparison", 250)
for d in (d18, d19, d20, kc): d.dropna(subset=["index"], inplace=True)
col = lambda hdr, name: L(hdr.index(name) + 1)
issues = []   # (시트, 셀, 구시군, 항목, 현재값, 기준값, 근거)
def add(sh, hdr, r, name, dist, cur, ref, why): issues.append(dict(시트=sh, 셀=f"{col(hdr, name)}{int(r._row)}", 구시군=dist, 항목=name, 현재값=cur, 기준값=ref, 근거=why))

# Step 1. 원자료 대조 (index 기준)
src = {"data18": (pd.read_csv(U + "825374fd-pe18res2.csv"), d18, h18, ["vote_all", "U_all", "P1", "M1", "P2", "M2", "U2"]),
       "data19": (pd.read_excel(U + "50c14bcc-pe19res.xlsx").rename(columns=lambda c: c.strip()), d19, h19, ["vote_all", "U_all", "M1", "H1", "M2", "H2", "U2"]),
       "data20": (pd.read_excel(U + "a5105d22-pe20res.xlsx").rename(columns={"Y1 윤석열(분류)": "Y1", "L1 이재명(분류)": "L1", "Y2 윤석열(미분류)": "Y2", "L2 이재명 (미분류)": "L2", "U2 무효": "U2"}),
                  d20, h20, ["vote_all", "U_all", "L1", "Y1", "L2", "Y2", "U2"])}
for sh, (s, d, hdr, cols) in src.items():
    m = d.merge(s, on="index", suffixes=("", "_src"), how="left")
    n = 0
    for c in cols:
        bad = m[(m[c] - m[c + "_src"]).abs() > 0]
        for _, r in bad.iterrows(): add(sh, hdr, r, c, r.district, r[c], r[c + "_src"], "원자료(pe 파일)와 다름"); n += 1
    print(f"{sh}: 원자료 대조 {len(m)}행 × {len(cols)}열, 불일치 {n}")

# Step 2. 시트 안의 숫자로 박힌 계산값 재계산
# data18: R1 = P1/M1, R2 = P2/M2, K = R2/R1 (소수 둘째 자리 반올림), C_rate, U_rate, vote_all2, U_all2, U_rate2, UP_rate, UM_rate
n = 0
for _, r in d18.iterrows():
    exp = {"R1": round(r.P1 / r.M1, 2), "R2": round(r.P2 / r.M2, 2), "C_rate": round((r.vote_all - r.U_all) / r.vote_all, 4), "U_rate": round(r.U_all / r.vote_all, 4),
           "vote_all2": r.vote_all - r.U2, "U_all2": r.U_all - r.U2, "U_rate2": round((r.U_all - r.U2) / (r.vote_all - r.U2), 4)}
    exp["K"] = round(exp["R2"] / exp["R1"], 2)
    for c, e in exp.items():
        tol = 0.011 if c in ("R1", "R2", "K") else (0.00011 if "rate" in c else 0)
        if r[c] is None or abs(r[c] - e) > tol: add("data18", h18, r, c, r.district, r[c], e, "원자료로 다시 계산한 값과 다름"); n += 1
print("data18 계산값 불일치", n)
n = 0
for _, r in d19.iterrows():
    exp = {"U_rate2": (r.U_all - r.U2) / (r.vote_all - r.U2), "C_rate": (r.vote_all - r.U_all) / r.vote_all, "U_rate": r.U_all / r.vote_all,
           "UM_rate": r.M2 / (r.M1 + r.M2), "UH_rate": r.H2 / (r.H1 + r.H2), "UD_rate": r.D2 / (r.D1 + r.D2), "K_DM": (r.D2 / r.D1) / (r.M2 / r.M1)}
    for c, e in exp.items():
        if r[c] is None or abs(r[c] - e) > 1e-6 * max(1, abs(e)): add("data19", h19, r, c, r.district, r[c], e, "원자료로 다시 계산한 값과 다름"); n += 1
print("data19 계산값 불일치", n)

# Step 3. data20 에 복사된 18·19대 값 (R19_1..K18) vs data19·data18 (index 기준)
x = d20.merge(d19[["index", "district", "R_1", "R_2", "K19", "K"]].rename(columns={"district": "d19", "R_1": "a", "R_2": "b", "K19": "c", "K": "k19"}), on="index", how="left") \
       .merge(d18[["index", "district", "R_1", "R_2", "K18", "K"]].rename(columns={"district": "d18", "R_1": "e", "R_2": "f", "K18": "g", "K": "k18"}), on="index", how="left")
n = 0
for _, r in x.iterrows():
    for c, e, why in [("R19_1", r.a, "data19 R_1"), ("R19_2", r.b, "data19 R_2"), ("K19_2", r.c, "data19 K19"), ("K19", r.k19, "data19 K"),
                      ("R18_1", r.e, "data18 R_1"), ("R18_2", r.f, "data18 R_2"), ("K18_2", r.g, "data18 K18"), ("K18", r.k18, "data18 K")]:
        if e is None or pd.isna(e) or r[c] is None or abs(r[c] - e) > 1e-9: add("data20", h20, r, c, r.district, r[c], e, f"{why} (같은 index {int(r['index'])})와 다름"); n += 1
print("data20 ← data18/19 복사값 불일치", n)

# Step 4. Kcomparison vs data20 (index 기준)
y = kc.merge(d20[["index", "district", "R1", "R2", "T" if "T" in d20 else "K", "U" if False else "over60", "R_1", "R_2", "K20_2", "R19_1", "R19_2", "K19_2", "K19", "R18_1", "R18_2", "K18_2", "K18"]]
             .rename(columns=lambda c: c if c == "index" else "s_" + c), on="index", how="left")
n = 0
kcols = [("R1", "s_R1"), ("R2", "s_R2"), ("over60", "s_over60"), ("R_1", "s_R_1"), ("R_2", "s_R_2"), ("K20_2", "s_K20_2"), ("R19_1", "s_R19_1"), ("R19_2", "s_R19_2"),
         ("K19_2", "s_K19_2"), ("K19", "s_K19"), ("R18_1", "s_R18_1"), ("R18_2", "s_R18_2"), ("K18_2", "s_K18_2"), ("K18", "s_K18")]
for _, r in y.iterrows():
    if r.district != r.s_district: add("Kcomparison", hk, r, "district", r.district, r.district, r.s_district, "data20 이름과 다름"); n += 1
    for c, s in kcols:
        if r[c] is None or r[s] is None or abs(r[c] - r[s]) > 1e-9: add("Kcomparison", hk, r, c, r.district, r[c], r[s], "data20 값과 다름"); n += 1
print("Kcomparison ← data20 불일치", n)

I = pd.DataFrame(issues); pd.to_pickle(dict(I=I, d18=d18, d19=d19, d20=d20, kc=kc), "wbcheck.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 40)
print(I.groupby(["시트", "근거"]).size().to_string())
print(I.head(60).to_string(index=False))
