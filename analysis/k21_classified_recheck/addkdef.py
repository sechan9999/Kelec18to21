"""k18to21_수정본.xlsx 에 K정의_비교 탭 추가 (정의·집계 방식별 K 는 수식, 18대 부족분 분해는 값)"""
import shutil, openpyxl, pandas as pd, numpy as np
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
F = "k18to21_수정본.xlsx"; shutil.copy(F, "k18to21_수정본_before_kdef.xlsx")
wb = openpyxl.load_workbook(F)
if "K정의_비교" in wb.sheetnames: del wb["K정의_비교"]
ws = wb.create_sheet("K정의_비교", 1)                       # 점검_수정내역 바로 뒤
B = Font(bold=True); H = PatternFill("solid", fgColor="DDEBF7"); Y = PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
def hdr(r, vals, c0=1):
    for j, v in enumerate(vals):
        c = ws.cell(r, c0 + j, v); c.font = B; c.fill = H; c.border = BOX; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
def row(r, vals, fmt=None, c0=1):
    for j, v in enumerate(vals):
        c = ws.cell(r, c0 + j, v); c.border = BOX
        if fmt and j > 0: c.number_format = fmt
r = 1
ws.cell(r, 1, "K 정의와 집계 방식 (18–21대)").font = Font(bold=True, size=14); r += 1
ws.cell(r, 1, "K 와 OR 은 같은 식이다. 값이 달라지는 것은 집계 방식(구·시·군 평균 / 전국 합산) 때문이다. 아래 표 2 는 각 data 탭을 참조하는 수식이다."); r += 2

# 1. 정의
ws.cell(r, 1, "1. 정의").font = B; r += 1
hdr(r, ["기호", "정의", "비고"]); r += 1
for v in [["P1, M1", "분류표의 보수 후보, 민주 후보 득표", "18대 박근혜·문재인, 19대 홍준표·문재인, 20대 윤석열·이재명, 21대 김문수·이재명"],
          ["P2, M2", "미분류(재확인)표의 보수 후보, 민주 후보 득표", ""],
          ["K", "(P2/M2) ÷ (P1/M1)", "엑셀 data 탭 K 열 (data18 T, data19 AB, data20 T, data21 T). OR 과 같은 식"],
          ["비율의 비", "[P2/(P2+M2)] ÷ [P1/(P1+M1)] = R_2 / R_1", "data18 AD(K18), data19 AF(K19), data20 X(K20_2), data21 X(K21_2). 회귀 R_2 ~ R_1 과 같은 척도"],
          ["구·시·군 평균", "구·시·군마다 K 를 구한 뒤 평균", "시트·SAS 방식. 작은 군과 큰 구를 똑같이 센다"],
          ["전국 합산", "전국의 P1·M1·P2·M2 를 먼저 더한 뒤 한 번 계산", "표 수로 가중된다"]]:
    row(r, v); r += 1
r += 1

# 2. 선거별 표 (수식)
ws.cell(r, 1, "2. 선거별 K (수식, data 탭 참조)").font = B; r += 1
hdr(r, ["선거", "탭", "n", "K 구·시·군 평균", "K 중앙값", "K 전국 합산", "비율의 비 평균", "비율의 비 전국 합산", "K 평균 (반올림 전 값)"]); r += 1
#        탭, P1, M1, P2, M2, K열, 비율의비열
S = [("18대", "data18", "H", "I", "J", "K", "T", "AD"), ("19대", "data19", "I", "H", "L", "K", "AB", "AF"),
     ("20대", "data20", "I", "H", "K", "J", "T", "X"), ("21대", "data21", "I", "H", "K", "J", "T", "X")]
top = r
for e, sh, p1, m1, p2, m2, kc, sc in S:
    rg = lambda c: f"{sh}!${c}$2:${c}$250"
    exact = f"=SUMPRODUCT(({rg(p2)}/{rg(m2)})/({rg(p1)}/{rg(m1)}))/COUNT({rg(p1)})" if sh != "data21" else f"=AVERAGE({rg(kc)})"
    row(r, [e, sh, f"=COUNT({rg(p1)})", f"=AVERAGE({rg(kc)})", f"=MEDIAN({rg(kc)})",
            f"=(SUM({rg(p2)})/SUM({rg(m2)}))/(SUM({rg(p1)})/SUM({rg(m1)}))", f"=AVERAGE({rg(sc)})",
            f"=(SUM({rg(p2)})/(SUM({rg(p2)})+SUM({rg(m2)})))/(SUM({rg(p1)})/(SUM({rg(p1)})+SUM({rg(m1)})))", exact], "0.0000")
    ws.cell(r, 3).number_format = "0"; ws.cell(r, 4).fill = Y; r += 1
ws.cell(r, 1, "노란색 = 시트 K 열의 구·시·군 평균 (18대 1.479). data18 T 열은 소수 둘째 자리로 반올림된 값이라 마지막 열(반올림 전 P·M 으로 계산)과 약간 다르다. data21 은 울릉군이 비어 있어 n 248."); r += 2

# 3. 18대 평균과 합산 차이 분해 (수식)
ws.cell(r, 1, "3. 18대 K 구·시·군 평균(1.48)과 전국 합산(1.38)이 다른 이유").font = B; r += 1
hdr(r, ["계산", "값", "설명"]); r += 1
K18 = "(data18!$J$2:$J$250/data18!$K$2:$K$250)/(data18!$H$2:$H$250/data18!$I$2:$I$250)"
for v in [["단순 평균", f"=SUMPRODUCT({K18})/COUNT(data18!$H$2:$H$250)", "249곳을 똑같이 센다"],
          ["재확인표 수 가중 평균", f"=SUMPRODUCT({K18},data18!$J$2:$J$250+data18!$K$2:$K$250)/SUM(data18!$J$2:$J$250,data18!$K$2:$K$250)", "재확인표가 많은 곳을 크게 센다"],
          ["전국 합산", "=(SUM(data18!$J$2:$J$250)/SUM(data18!$K$2:$K$250))/(SUM(data18!$H$2:$H$250)/SUM(data18!$I$2:$I$250))", "R1 이 다른 지역을 합치면 OR 이 더 작아진다 (합산 효과)"],
          ["K 와 R_1 상관", "=CORREL(data18!$T$2:$T$250,data18!$AB$2:$AB$250)", "R_1 이 높은 곳일수록 K 가 크다"]]:
    row(r, v, "0.0000"); r += 1
r += 1

# 4. 18대 공개값 부족분 분해 (값)
m = pd.read_pickle("pe18_shortfall.pkl")
ws.cell(r, 1, "4. 18대 자료가 공개값(18Data)보다 적은 부분 — 구·시·군별 대조 (값)").font = B; r += 1
hdr(r, ["구분", "곳 수", "K 구·시·군 평균", "K 전국 합산", "내용"]); r += 1
def st(d): return [len(d), ((d.P2 / d.M2) / (d.P1 / d.M1)).mean(), (d.P2.sum() / d.M2.sum()) / (d.P1.sum() / d.M1.sum())]
G = [("전체", m, ""), ("부재자·재외 투표만 빠짐", m[m.grp.str.startswith("A")], "부족분 = 그 구·시·군의 국내부재자·재외 득표 (차이 50표 이내). 투표소 개표분은 빠짐없음"),
     ("부재자·재외 투표 일부 또는 전부 포함", m[m.grp.str.startswith("C")], "서초구·제주시·평창군은 부족분 0"),
     ("투표구 일부 누락", m[m.grp.str.startswith("D")], ", ".join(f"{a} {b}" for a, b in m[m.grp.str.startswith("D")][["시도", "district"]].values)),
     ("투표구 누락 9곳 제외", m[~m.grp.str.startswith("D")], "영향이 작다")]
for g, d, t in G:
    row(r, [g, *st(d), t], "0.0000"); ws.cell(r, 2).number_format = "0"; r += 1
r += 1
ws.cell(r, 1, "5. 9곳 상세 (부족분 − 부재자·재외 득표 = 투표구 누락분)").font = B; r += 1
hdr(r, ["시도", "구·시·군", "공개 박근혜", "공개 문재인", "누락 박근혜", "누락 문재인", "누락 비율(박+문)"]); r += 1
for _, x in m[m.grp.str.startswith("D")].iterrows():
    row(r, [x.시도, x.district, int(x.박근혜), int(x.문재인), int(x.잔여_박), int(x.잔여_문), (x.잔여_박 + x.잔여_문) / (x.박근혜 + x.문재인)], "#,##0")
    ws.cell(r, 7).number_format = "0.0%"; r += 1
for c, w in zip("ABCDEFGHI", [34, 44, 60, 16, 14, 14, 16, 18, 20]): ws.column_dimensions[c].width = w
for rr in ws.iter_rows():
    for c in rr:
        if isinstance(c.value, str) and len(c.value) > 40: c.alignment = Alignment(wrap_text=True, vertical="top")

# 점검_수정내역에 기록
lg = wb["점검_수정내역"]; n = lg.max_row + 1
lg.cell(n, 1, "K정의_비교: K = (P2/M2)÷(P1/M1) 의 구·시·군 평균·중앙값·전국 합산과 비율의 비를 선거별로 비교 (data 탭 참조 수식). 18대 평균 1.48 과 합산 1.38 의 차이 분해, 18대 공개값 부족분(부재자·재외 191곳, 일부 포함 49곳, 투표구 누락 9곳) 정리.")
wb.save(F); print("saved", r)
