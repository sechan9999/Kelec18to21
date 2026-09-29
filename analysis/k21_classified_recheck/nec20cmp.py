"""20thKelection.xlsx (20elec, 20elec_old, 시도별 공개 시트) vs data20(pe20res) 대조"""
import openpyxl, pandas as pd, numpy as np
wb = openpyxl.load_workbook("nec20.xlsx", data_only=True)
def sheet(name, n=250):
    rows = list(wb[name].iter_rows(values_only=True)); h = [str(x).strip() if x is not None else f"c{i}" for i, x in enumerate(rows[0])]
    seen = {}; hh = []
    for x in h: seen[x] = seen.get(x, 0) + 1; hh.append(x if seen[x] == 1 else f"{x}_{seen[x]}")
    return pd.DataFrame(rows[1:n + 1], columns=hh)
N = sheet("20elec "); O = sheet("20elec_old")
num = lambda s: pd.to_numeric(s, errors="coerce")
for c in ["vote_all", "U_all", "L1", "Y1", "S1", "L2", "Y2", "S2", "U2"]: N[c] = num(N[c]); O[c] = num(O[c])
print("20elec 행", N.district.notna().sum(), "| L2 값 있는 행", N.L2.notna().sum(), "| old L2 값 있는 행", O.L2.notna().sum())
print("20elec: L1+Y1+S1 == vote_all − U_all ?", int(((N.L1 + N.Y1 + N.S1) == (N.vote_all - N.U_all)).sum()))
# 공개 시·도 시트 (구시군별 최종 득표)
pub = []
for sd in ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]:
    for r in wb[sd].iter_rows(min_row=5, values_only=True):
        if r[0] and isinstance(r[1], (int, float)) and r[0] != "합계":
            pub.append(dict(시도=sd, 구=str(r[0]).strip(), 선거인수=r[1], 투표수=r[2], 이재명=r[3], 윤석열=r[4], 심상정=r[5], 무효=r[16]))
Pb = pd.DataFrame(pub); print("공개 구시군 행", len(Pb))
# data20
wv = openpyxl.load_workbook("k18to21_수정본.xlsx", data_only=True)["data20"]; h = [c.value for c in wv[1]]
D = pd.DataFrame([[c.value for c in wv[r]] for r in range(2, 251)], columns=h)
for c in ["vote_all", "U_all", "L1", "Y1", "L2", "Y2", "U2"]: D[c] = num(D[c])
m = D.merge(N[["index", "district", "vote_all", "U_all", "L1", "Y1", "S1"]], on="index", how="outer", suffixes=("_d", "_n"), indicator=True)
print(m._merge.value_counts().to_dict())
m = m[m._merge == "both"].copy()
print("이름 불일치:", m[m.district_d.astype(str).str.replace(" ", "") != m.district_n.astype(str).str.replace(" ", "")][["index", "district_d", "district_n"]].head(12).to_string())
for a, b in [("vote_all_d", "vote_all_n"), ("U_all_d", "U_all_n")]:
    d = m[a] - m[b]; print(a, "일치", int((d == 0).sum()), "/", len(m))
m["dL"] = (m.L1_d + m.L2) - m.L1_n; m["dY"] = (m.Y1_d + m.Y2) - m.Y1_n
print("data20 분류+미분류 == 20elec L1 (이재명):", int((m.dL == 0).sum()), "| 윤석열:", int((m.dY == 0).sum()), "/", len(m))
print(m.loc[(m.dL != 0) | (m.dY != 0), ["index", "district_d", "L1_d", "L2", "L1_n", "dL", "Y1_d", "Y2", "Y1_n", "dY"]].to_string())
print(N[N.district.astype(str).str.contains("오산|제천")][["index", "district", "vote_all", "U_all", "L1", "Y1", "S1"]].to_string())
print(D[D.district.astype(str).str.contains("오산|제천")][["index", "district", "vote_all", "U_all", "L1", "Y1", "L2", "Y2", "U2"]].to_string())
print(Pb[Pb.구.str.contains("오산|제천|강릉")].to_string())
# old L2.. vs data19
w19 = openpyxl.load_workbook("k18to21_수정본.xlsx", data_only=True)["data19"]; h = [c.value.strip() if isinstance(c.value, str) else c.value for c in w19[1]]
D19 = pd.DataFrame([[c.value for c in w19[r]] for r in range(2, 251)], columns=h)
q = O.merge(D19[["index", "M2", "H2", "D2", "U2"]], on="index", suffixes=("", "_19"))
print("20elec_old L2,Y2,S2,U2 == data19 M2,H2,D2,U2:", int(((q.L2 == q.M2) & (q.Y2 == q.H2) & (q.S2 == q.D2) & (q.U2 == q.U2_19)).sum()), "/", len(q))
pd.to_pickle(dict(N=N, O=O, Pb=Pb, m=m), "nec20.pkl")
