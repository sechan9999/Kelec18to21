"""k18to21_수정본.xlsx 에 K정의_비교 탭 추가 (정의·집계 방식별 K 는 수식, 18대 부족분 분해는 값)"""
import shutil, openpyxl, pandas as pd, numpy as np
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
F = "k18to21_수정본.xlsx"; shutil.copy(F, "k18to21_수정본_before_kdef2.xlsx")
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

# 4. 18대 공개값과 차이 — 뉴스타파(선관위) 분류기 운영결과로 확인 (값)
m = pd.read_pickle("nec18_merge.pkl")
ws.cell(r, 1, "4. 18대 data18 과 뉴스타파 분류기 운영결과(선관위) 대조 — 공개값 = 수개표 + 분류기 개표 (값)").font = B; r += 1
hdr(r, ["구분", "곳 수", "K 구·시·군 평균 (data18)", "K 구·시·군 평균 (뉴스타파)", "내용"]); r += 1
def kk(d, a, b, c, e): return ((d[c] / d[e]) / (d[a] / d[b])).mean()
G = [("전체", m, "공개 득표 = 뉴스타파 '계' (249곳 모두 확인). 공개값보다 적은 몫은 모두 수개표(부재자 등)"),
     ("완전 일치", m[m.cat.str.startswith("A")], "data18 = 분류기 개표분"),
     ("분류·미분류 사이 소수 표 차이", m[m.cat.str.startswith("B")], "후보별 합은 같고 분류↔미분류로 최대 54표 옮겨짐 (입력 차이)"),
     ("수개표 일부·전부 포함", m[m.cat.str.startswith("C")], "data18 이 수개표(부재자 등) 득표를 분류·미분류에 더함 (중앙값 92%)"),
     ("기타 소수 차이", m[m.cat.str.startswith("D")], "최대 56표")]
for g, d, t in G:
    row(r, [g, len(d), kk(d, "P1", "M1", "P2", "M2"), kk(d, "분류_박근혜", "분류_문재인", "미분류_박근혜", "미분류_문재인"), t], "0.0000"); ws.cell(r, 2).number_format = "0"; r += 1
ws.cell(r, 1, "앞서 '투표구 일부 누락'으로 본 9곳(연천·거창·경산·연제·인천 동구·옹진·완도·무주·임실)은 누락이 아니라 수개표 비중이 큰 곳이다."); r += 2
ws.cell(r, 1, "5. 수개표 비중이 큰 곳 (뉴스타파 자료, 상위 12곳)").font = B; r += 1
hdr(r, ["시도", "구·시·군", "총투표", "수개표", "분류기 개표", "수개표 비중"]); r += 1
m["hand"] = m.수개표_계 / m.계_총투표수
for _, x in m.sort_values("hand", ascending=False).head(12).iterrows():
    row(r, [x.시도, x.district, int(x.계_총투표수), int(x.수개표_계), int(x.분류기개표_계), float(x.hand)], "#,##0"); ws.cell(r, 6).number_format = "0.0%"; r += 1
for c, w in zip("ABCDEFGHI", [34, 44, 60, 16, 14, 14, 16, 18, 20]): ws.column_dimensions[c].width = w
for rr in ws.iter_rows():
    for c in rr:
        if isinstance(c.value, str) and len(c.value) > 40: c.alignment = Alignment(wrap_text=True, vertical="top")

# 점검_수정내역에 기록
lg = wb["점검_수정내역"]; n = next((c.row for c in lg["A"] if isinstance(c.value, str) and c.value.startswith("K정의_비교:")), lg.max_row + 1)
lg.cell(n, 1, "K정의_비교: K = (P2/M2)÷(P1/M1) 의 구·시·군 평균·중앙값·전국 합산과 비율의 비를 선거별로 비교 (data 탭 참조 수식). 18대 평균 1.48 과 합산 1.38 의 차이 분해, 18대 data18 과 뉴스타파 분류기 운영결과 대조 (일치 158, 소수 표 차이 40, 수개표 포함 51곳).")
wb.save(F); print("saved", r)
