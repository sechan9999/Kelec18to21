"""20대선(pe20res) 구·시·군 분류/미분류 + 연령 구성  ×  21대선 판독 결과(구·시·군 합산) 결합 -> age_units.pkl"""
import pandas as pd, numpy as np

# Step 1. 20대: 이름을 21대 기준 단위로 맞춘다
p = pd.read_pickle("pe20.pkl").copy()
ren = {("부산광역시", "진구"): ("부산광역시", "부산진구"), ("인천광역시", "남구"): ("인천광역시", "미추홀구"),
       ("경기도", "여주군"): ("경기도", "여주시"), ("경상북도", "군위군"): ("대구광역시", "군위군"),
       }                                   # 세종은 20대 자료대로 충청남도 '세종시' 단위로 둔다
def unit20(r):
    s, g = ren.get((r.시도, r.district), (r.시도, r.district))
    if s == "울산광역시": g = g.replace("울산", "")
    if s == "충청북도" and (g.startswith("청주시") or g == "청원군"): g = "청주시"
    return pd.Series({"시도": s, "단위": g})
p[["시도", "단위"]] = p.apply(unit20, axis=1)
p = p[~((p.시도 == "경상북도") & (p.단위 == "울릉군"))]
# 연령은 투표수 가중 평균으로, 표는 합산 (청주 4→1)
p["w"] = p.vote_all
agg20 = p.groupby(["시도", "단위"]).apply(lambda z: pd.Series({
    "Y1": z.Y1.sum(), "L1": z.L1.sum(), "Y2": z.Y2.sum(), "L2": z.L2.sum(), "vote20": z.vote_all.sum(),
    "under50": np.average(z.under50, weights=z.w), "r50s": np.average(z.r50s, weights=z.w), "over60": np.average(z.over60, weights=z.w)})).reset_index()

# Step 2. 21대: 투표구별 판독 결과를 같은 단위로 합산 (제외 행 빼고, 모든 투표구분)
d = pd.read_excel("ALL17.xlsx", "투표구별"); d = d[d.판독방식 != "제외"].copy()
def unit21(s, g):
    if s == "세종특별자치시": return "세종시"
    if s == "경기도" and g.startswith("부천시"): return "부천시"
    if s == "경기도" and g.startswith("화성시"): return "화성시"
    if s == "충청북도" and g.startswith("청주시"): return "청주시"
    return g
d["단위"] = [unit21(s, g) for s, g in zip(d.시도명, d.구시군명)]
d["시도명"] = d.시도명.replace({"세종특별자치시": "충청남도"})
agg21 = d.groupby(["시도명", "단위"])[["분류_김문수", "분류_이재명", "재확인_김문수", "재확인_이재명"]].sum().reset_index().rename(columns={"시도명": "시도"})
# 투표구분별 R1도 (관내사전/선거일) 보관
for g in ["관내사전", "선거일"]:
    x = d[d.구분 == g].groupby(["시도명", "단위"])[["분류_김문수", "분류_이재명", "재확인_김문수", "재확인_이재명"]].sum()
    x.columns = [f"{c}_{g}" for c in x.columns]; agg21 = agg21.merge(x.reset_index().rename(columns={"시도명": "시도"}), on=["시도", "단위"], how="left")

# Step 3. 결합
U = agg20.merge(agg21, on=["시도", "단위"], how="outer", indicator=True)
print(U._merge.value_counts().to_dict())
print("한쪽만:", U[U._merge != "both"][["시도", "단위", "_merge"]].to_string(index=False))
U = U[U._merge == "both"].drop(columns="_merge")
lg = lambda a, b: np.log(a / b)
U["lr1_20"] = lg(U.Y1, U.L1); U["lr2_20"] = lg(U.Y2, U.L2); U["lor20"] = U.lr2_20 - U.lr1_20
U["lr1_21"] = lg(U.분류_김문수, U.분류_이재명); U["lr2_21"] = lg(U.재확인_김문수, U.재확인_이재명); U["lor21"] = U.lr2_21 - U.lr1_21
U["n20"] = U.Y2 + U.L2; U["n21"] = U.재확인_김문수 + U.재확인_이재명
U.to_pickle("age_units.pkl")
print(len(U), "단위 결합")
print("전국 20대 OR", round(np.exp(lg(U.Y2.sum(), U.L2.sum()) - lg(U.Y1.sum(), U.L1.sum())), 3),
      "| 21대 OR", round(np.exp(lg(U.재확인_김문수.sum(), U.재확인_이재명.sum()) - lg(U.분류_김문수.sum(), U.분류_이재명.sum())), 3))
