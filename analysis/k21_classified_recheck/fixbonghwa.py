"""19대 봉화군: 선관위 구·시·군 소계 행에서 개표단위 일부(2,159표)가 빠짐 → 개표단위 합계(K18_K19_results.xlsx)로 교체
data19 표 수·비율, data20·Kcomparison 의 19대 값, nec19 원자료 행 표시"""
import shutil, openpyxl, pandas as pd
from openpyxl.styles import PatternFill
from openpyxl.comments import Comment
F = "k18to21_수정본.xlsx"; shutil.copy(F, "k18to21_수정본_before_bonghwa.xlsx")
YEL = PatternFill("solid", fgColor="FFFF00"); ORG = PatternFill("solid", fgColor="FFC000"); AUTH = "점검"
B = pd.read_excel("k1819res.xlsx", "19대_구시군"); b = B[B.구시군 == "봉화군"].iloc[0]
wb = openpyxl.load_workbook(F); log = []
def hmap(ws): return {(c.value.strip() if isinstance(c.value, str) else c.value): c.column for c in ws[1]}
def setc(ws, r, col, new, why, fill=YEL):
    c = ws.cell(r, col); old = c.value; c.value = new; c.fill = fill
    c.comment = Comment(f"[수정] 봉화군 개표단위 합계로 교체\n이전: {old}\n{why}", AUTH, width=330, height=110); log.append((ws.title, c.coordinate, old, new))
WHY = "선관위 구·시·군 소계 행에서 개표단위 일부가 빠짐(분류기 통과 2,159표). 개표단위 합계 22,808 이 공개 투표수 22,947 에 맞음"

# 1) data19
d = wb["data19"]; H = hmap(d); r = next(i for i in range(2, 251) if d.cell(i, H["district"]).value == "봉화군")
new = dict(vote_all=int(b.통과_계), U_all=int(b.미분류계), M1=int(b.분류_문), H1=int(b.분류_홍), D1=int(b.분류_안), M2=int(b.미분류_문), H2=int(b.미분류_홍), D2=int(b.미분류_안))
for k, v in new.items(): setc(d, r, H[k], v, WHY)
v = {k: d.cell(r, H[k]).value for k in ["vote_all", "U_all", "M1", "H1", "D1", "M2", "H2", "D2", "U2"]}
exp = {"U_rate2": (v["U_all"] - v["U2"]) / (v["vote_all"] - v["U2"]), "C_rate": (v["vote_all"] - v["U_all"]) / v["vote_all"], "U_rate": v["U_all"] / v["vote_all"],
       "UM_rate": v["M2"] / (v["M1"] + v["M2"]), "UH_rate": v["H2"] / (v["H1"] + v["H2"]), "UD_rate": v["D2"] / (v["D1"] + v["D2"]), "K_DM": (v["D2"] / v["D1"]) / (v["M2"] / v["M1"])}
for k, e in exp.items(): setc(d, r, H[k], e, "바뀐 표 수로 다시 계산")
for k, why in [("U2", "미분류 중 무효표. 결과 파일에 무효·기타 후보 열이 없어 그대로 둠 (늘어난 미분류 140표 중 5명 후보 외 19표가 무효·기타)"),
               ("Pr_total", "정의를 확인하지 못해 그대로 둠 (vote_all 이 바뀌었으므로 확인 필요)")]:
    c = d.cell(r, H[k]); c.fill = ORG; c.comment = Comment(f"[확인 필요] {why}", AUTH, width=330, height=100)
R1 = new["H1"] / new["M1"]; R2 = new["H2"] / new["M2"]; r1 = new["H1"] / (new["H1"] + new["M1"]); r2 = new["H2"] / (new["H2"] + new["M2"])
vals = {"R19_1": r1, "R19_2": r2, "K19_2": r2 / r1, "K19": R2 / R1}
print("봉화 새 값", {k: round(x, 4) for k, x in vals.items()})

# 2) data20·Kcomparison 의 19대 값 (값으로 들어 있음)
for s in ["data20", "Kcomparison"]:
    ws = wb[s]; hdr = [c.value for c in ws[1]]; ic = hdr.index("index") + 1
    rr = next(i for i in range(2, ws.max_row + 1) if ws.cell(i, ic).value == 92)
    for j, h in enumerate(hdr, 1):
        if h in vals and not (isinstance(ws.cell(rr, j).value, str) and ws.cell(rr, j).value.startswith("=")): setc(ws, rr, j, vals[h], "data19 봉화군 수정에 맞춰 갱신")

# 3) nec19 원자료 봉화 행 표시
n = wb["nec19"]
for row in n.iter_rows():
    if row[1].value == "봉화군":
        row[1].fill = ORG; row[1].comment = Comment("[확인 필요] 선관위 원자료의 구·시·군 소계. 개표단위 일부(분류기 통과 2,159표)가 빠진 값이라 data19 는 개표단위 합계(22,808)로 고침", AUTH, width=330, height=100)

lg = wb["점검_수정내역"]; k = lg.max_row + 1
lg.cell(k, 1, f"봉화군(19대): 선관위 구·시·군 소계 행에 개표단위 일부가 빠져 있어(분류기 통과 20,649 → 개표단위 합계 22,808, 공개 투표수 22,947) data19 표 수 8칸·비율 7칸과 data20·Kcomparison 의 19대 값을 고침. K19 {vals['K19']:.4f} (이전 1.5327). U2·Pr_total 은 근거가 없어 그대로 두고 주황색 표시.")
wb.save(F); print("수정 셀", len(log))
