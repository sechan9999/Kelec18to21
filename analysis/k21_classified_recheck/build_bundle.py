"""대시보드용 묶음 생성: 21대 분류/재확인(개표상황표 판독) 분석
출력: bundle/summaries/k21_classified_recheck.json, bundle/corrected_data/*.csv, bundle/public/analysis/*.png"""
import json, shutil, pandas as pd, numpy as np, statsmodels.formula.api as smf
from pathlib import Path
from scipy import stats
OUT = Path("bundle"); [ (OUT / p).mkdir(parents=True, exist_ok=True) for p in ["summaries", "corrected_data", "public/analysis", "analysis/k21_classified_recheck"] ]
R = lambda v, n=4: None if v is None or (isinstance(v, float) and not np.isfinite(v)) else round(float(v), n)

# Step 1. 21대 투표구 판독 자료 (제외 행 표시 유지)
d = pd.read_excel("ALL17.xlsx", "투표구별")
d.to_csv(OUT / "corrected_data/k21_precinct_classified_recheck.csv", index=False, encoding="utf-8")
ok = d[d.판독방식 != "제외"].copy()
C5 = ["이재명", "김문수", "이준석", "권영국", "송진호"]

def lor_ci(df, y2="재확인_김문수", l2="재확인_이재명", y1="분류_김문수", l1="분류_이재명"):
    """OR 과 군집(행 단위) 델타법 95% 구간"""
    A, B, Cc, D = (df[c].astype(float) for c in (y2, l2, y1, l1))
    lor = np.log(A.sum()) - np.log(B.sum()) - np.log(Cc.sum()) + np.log(D.sum()); n = len(df)
    z = A / A.sum() - B / B.sum() - Cc / Cc.sum() + D / D.sum()
    se = np.sqrt(n / (n - 1) * (z ** 2).sum()) if n > 1 else np.nan; t = stats.t.ppf(.975, max(n - 1, 1))
    return dict(OR=R(np.exp(lor)), lo=R(np.exp(lor - t * se)), hi=R(np.exp(lor + t * se)), n=int(n))

def block(z):
    y1, l1, y2, l2 = (float(z[c].sum()) for c in ["분류_김문수", "분류_이재명", "재확인_김문수", "재확인_이재명"])
    r1, r2 = y1 / (y1 + l1), y2 / (y2 + l2)
    return dict(classified_kim=int(y1), classified_lee=int(l1), recheck_kim=int(y2), recheck_lee=int(l2),
                R1=R(r1), R2=R(r2), K=R(r2 / r1), **lor_ci(z[(z.재확인_김문수 + z.재확인_이재명) > 0]))

TYPES = ["관내사전", "선거일", "관외사전"]
nat = {"전체": block(ok[ok.구분.isin(TYPES + ["재외"])])}
for g in TYPES: nat[g] = block(ok[ok.구분 == g])
a5, b5 = ok[[f"분류_{c}" for c in C5]].sum(), ok[[f"재확인_{c}" for c in C5]].sum()
cand = [dict(name=c, classified_pct=R(a5[f"분류_{c}"] / a5.sum() * 100, 2), recheck_pct=R(b5[f"재확인_{c}"] / b5.sum() * 100, 2),
             K=R((b5[f"재확인_{c}"] / b5.sum()) / (a5[f"분류_{c}"] / a5.sum()))) for c in C5]

# Step 2. 시도별 (17개, 세종 따로) + 20대 보정 OR
p20 = pd.read_pickle("pe20.pkl").copy(); o = p20.district == "오산시"
p20.loc[o, "Y1"] -= p20.loc[o, "Y2"]; p20.loc[o, "L1"] -= p20.loc[o, "L2"]; p20 = p20[p20.district != "제천시"]
prov = []
for s, z in ok.groupby("시도명", sort=False):
    row = dict(province=s, 전체=block(z[z.구분.isin(TYPES + ["재외"])]), **{g: block(z[z.구분 == g]) for g in ["관내사전", "선거일"] if (z.구분 == g).any()})
    zz = p20[p20.시도 == s]
    if len(zz): row["OR20"] = lor_ci(zz, "Y2", "L2", "Y1", "L1")
    prov.append(row)
prov.sort(key=lambda r: r["전체"]["OR"])

# Step 3. 구·시·군 (k21reg 결과: 선형 적합, 예측구간, RStudent, Cook's D) + 투표구분별 OR
k = pd.read_pickle("k21reg_out.pkl")["k"]; o21 = pd.read_pickle("k21reg_out.pkl")["o21"]
kk = k.join(o21)
t = pd.read_pickle("k21reg_out.pkl")["t"]
tt = {(r.region, r.district, r["class"]): r for _, r in t.iterrows()}
dist = []
for _, r in kk.iterrows():
    row = dict(province=r.region, district=r.district, classified_kim=int(r.Y1), classified_lee=int(r.L1), recheck_kim=int(r.Y2), recheck_lee=int(r.L2),
               R1=R(r.R1), R2=R(r.R2), K=R(r.K), OR=R((r.Y2 / r.L2) / (r.Y1 / r.L1)), pred=R(r.Predicted), pi_lo=R(r.CLI_lo), pi_hi=R(r.CLI_hi),
               rstudent=R(r.RStudent, 3), cooksD=R(r.CooksD))
    for g, key in [("관내사전", "OR_pre"), ("선거일", "OR_day")]:
        q = tt.get((r.region, r.district, g))
        if q is not None and q.Y2 > 0 and q.L2 > 0: row[key] = R((q.Y2 / q.L2) / (q.Y1 / q.L1))
    dist.append(row)

# Step 4. 회귀 요약 (20대 보정 / 21대 / 2차 / 투표구분별 / 두 선 비교)
p20["R_1"] = p20.Y1 / (p20.Y1 + p20.L1); p20["R_2"] = p20.Y2 / (p20.Y2 + p20.L2)
def fit(df, f="R_2 ~ R_1"):
    m = smf.ols(f, df).fit(); r = m.resid
    return dict(n=int(m.nobs), params={k2: R(v) for k2, v in m.params.items()}, se={k2: R(v) for k2, v in m.bse.items()}, r2=R(m.rsquared), mse=R(m.mse_resid, 6),
                resid_sd=R(r.std()), skew=R(stats.skew(r), 3), kurt=R(stats.kurtosis(r), 3), shapiro_p=R(stats.shapiro(r).pvalue))
t2 = t.assign(R_1=t.R1, R_2=t.R2)
D = pd.concat([pd.DataFrame({"R_1": p20.R_1.values, "R_2": p20.R_2.values, "e": "20대"}), pd.DataFrame({"R_1": k.R1.values, "R_2": k.R2.values, "e": "21대"})])
D["c"] = D.R_1 - .5; MI = smf.ols("R_2 ~ c * C(e)", D).fit(cov_type="HC3")
reg = {"20대_보정_선형": fit(p20), "21대_선형": fit(k.assign(R_1=k.R1, R_2=k.R2)), "21대_2차": fit(k.assign(R_1=k.R1, R_2=k.R2, R_1sq=k.R1 ** 2), "R_2 ~ R_1sq + R_1"),
       "21대_당선인분자_선형": fit(k.assign(R_1=k.L1 / (k.L1 + k.Y1), R_2=k.L2 / (k.L2 + k.Y2))),
       "21대_관내사전_선형": fit(t2[t2["class"] == "관내사전"]), "21대_선거일_선형": fit(t2[t2["class"] == "선거일"]),
       "20대21대_비교": dict(slope_diff=R(MI.params["c:C(e)[T.21대]"]), slope_p=R(MI.pvalues["c:C(e)[T.21대]"]),
                          level_diff_at_R1_0_5=R(MI.params["C(e)[T.21대]"]), level_p=R(MI.pvalues["C(e)[T.21대]"], 6))}

# Step 5. 무효표·연령 (invalid.py 결과), 관내사전 쌍 비교 (pre_decomp)
inv = pd.read_pickle("inv_out.pkl"); w = pd.read_pickle("prewide.pkl")
w["d"] = (w.lR2_pre - w.lR1_pre) - (w.lR2_day - w.lR1_day)
ma_p, ma_b, ma_pv = inv["ma"]
invalid = dict(precincts=int(len(inv["x"])), invalid_rate=R(inv["x"].무효.sum() / inv["x"].투표수.sum()),
               OR_if_invalid_doubles=0.989, OR_if_invalid_doubles_ci=[0.976, 1.002], OR_if_recheck_doubles=0.918, OR_if_recheck_doubles_ci=[0.902, 0.935],
               over60_per10pp_OR=R(np.exp(ma_p["over60"] / 10), 3), over60_per10pp_ci=[R(np.exp((ma_p["over60"] - 1.96 * ma_b["over60"]) / 10), 3), R(np.exp((ma_p["over60"] + 1.96 * ma_b["over60"]) / 10), 3)],
               corr_over60_recheck=R(np.corrcoef(inv["A"].over60, inv["A"].rv)[0, 1], 3), corr_over60_invalid=R(np.corrcoef(inv["A"].over60, inv["A"].u)[0, 1], 3),
               by_invalid_quintile=[dict(type=r.구분, q=int(r.u5) + 1, OR=R(r.OR), invalid_rate=R(r.u), precincts=int(r.투표구)) for _, r in inv["BU"].iterrows()],
               by_recheck_quintile=[dict(type=r.구분, q=int(r.r5) + 1, OR=R(r.OR), recheck_rate=R(r.rv), precincts=int(r.투표구)) for _, r in inv["BR"].iterrows()])
pre_vs_day = dict(districts=int(len(w)), OR_ratio_pre_over_day=R(np.exp(w.d.mean()), 3), log_se=R(w.d.std() / np.sqrt(len(w)), 4), districts_pre_higher=int((w.d > 0).sum()),
                  precinct_model_pre_effect_log=0.189, precinct_model_pre_effect_log_with_district_FE=0.019,
                  note="구·시·군 쌍 비교에서는 관내사전 OR이 약 1.19배 높지만, 투표구 모형에 구·시·군 고정효과를 넣으면 관내사전 효과가 0.019(유의하지 않음)로 줄어 두 수준의 결과가 엇갈린다.")

# Step 6. 20대 자료 보정 내역
pe20_fix = [dict(unit="경기도 오산시", issue="분류 열(Y1·L1)에 공개 최종득표가 들어 있음", action="분류 = 최종 − 재확인으로 복원", note="재확인 열도 U_all과 950표 불일치 — 복원 후에도 신뢰도 낮음"),
            dict(unit="충청북도 제천시", issue="Y1+L1 = 총투표수(87,091), 분류·재확인 모두 공개값과 불일치", action="제외", note="복원 근거 없음")]
flag11 = ["오산시", "제천시", "영덕군", "포항시남구", "광산구", "도봉구", "영암군", "아산시", "태안군", "청주시흥덕구", "충주시"]
pc = pd.read_pickle("pe20.pkl").copy(); pc["보정"] = ""; pc.loc[pc.district == "오산시", "보정"] = "분류=최종-재확인 복원"
pc.loc[pc.district == "오산시", "Y1"] -= pc.loc[pc.district == "오산시", "Y2"]; pc.loc[pc.district == "오산시", "L1"] -= pc.loc[pc.district == "오산시", "L2"]
pc.loc[pc.district == "제천시", "보정"] = "제외 권고(복원 불가)"; pc["점검표시"] = pc.district.isin(flag11)
pc.to_csv(OUT / "corrected_data/pe20res_corrected.csv", index=False, encoding="utf-8")

J = dict(meta=dict(title="21대 대선 분류/재확인 투표지 분석 (개표상황표 판독)", built="2026-09-28",
                   definitions=dict(R1="김문수/(이재명+김문수), 분류된 투표지", R2="김문수/(이재명+김문수), 재확인대상 투표지 (= 공개 최종득표 − 분류)",
                                    K="R2/R1", OR="(재확인 김/이) ÷ (분류 김/이)"),
                   numerator="보수 후보(김문수, 20대는 윤석열)", rows_total=int(len(d)), rows_used=int(len(ok)), rows_excluded=int((d.판독방식 == "제외").sum()),
                   read_method=d.판독방식.value_counts().to_dict(),
                   checks=["후보 5명 합 = 계", "계 + 재확인대상 = 공개 투표수", "분류 + 재확인 + 무효 = 투표수 (18,040개 투표구 전부 일치)"],
                   not_same_as="summaries/k21_recount*.json 의 K는 관외사전 ÷ 관내 득표율 비(이재명 기준)로, 이 분석과 다른 지표임"),
         candidates=cand, national=nat, provinces=prov, districts=dist, regression=reg, invalid_and_age=invalid, pre_vs_day=pre_vs_day,
         pe20_corrections=dict(fixed=pe20_fix, flagged_units=flag11),
         figures=[dict(file=f"/analysis/{n}.png", title=tl) for n, tl in [
             ("k20_k21_fitplot_overlay", "20대(보정)·21대 Fit Plot 겹침"), ("k21_fitplot_by_type", "21대 관내사전·선거일 Fit Plot"),
             ("k21_fitplot", "21대 Fit Plot"), ("k21_fit_diagnostics", "21대 Fit Diagnostics"), ("k20_fitplot_corrected", "20대 보정 Fit Plot"),
             ("k20_fit_diagnostics_corrected", "20대 보정 Fit Diagnostics"), ("residuals_20_vs_21", "잔차 분포 20대 vs 21대"),
             ("invalid_recheck_or", "무효표·재확인율과 OR"), ("r1_control_regression", "투표구 단위 R1 통제 회귀"),
             ("k21_winner_numerator_fitplot", "21대 당선인(이재명) 분자 Fit Plot과 K 비교"), ("k21_winner_numerator_diagnostics", "21대 당선인(이재명) 분자 Fit Diagnostics"),
             ("age_test", "연령 검정"), ("or_ci_change", "시도 OR 신뢰구간과 20→21 변화")]])
(OUT / "summaries/k21_classified_recheck.json").write_text(json.dumps(J, ensure_ascii=False, indent=1), encoding="utf-8")

# Step 7. 그림 복사 (ASCII 파일명)
FIG = {"K20_K21_FitPlot_겹침.png": "k20_k21_fitplot_overlay", "K21_투표구분별_FitPlot.png": "k21_fitplot_by_type", "K21_FitPlot.png": "k21_fitplot",
       "K21_FitDiagnostics.png": "k21_fit_diagnostics", "K20_FitPlot_보정.png": "k20_fitplot_corrected", "K20_FitDiagnostics_보정.png": "k20_fit_diagnostics_corrected",
       "잔차분포_20대_21대_비교.png": "residuals_20_vs_21", "무효표_재확인_OR.png": "invalid_recheck_or", "R1_통제_회귀_그림.png": "r1_control_regression",
       "연령_검정_그림.png": "age_test", "OR_신뢰구간_변화_그림.png": "or_ci_change",
       "K21_당선인분자_FitPlot.png": "k21_winner_numerator_fitplot", "K21_당선인분자_Diagnostics.png": "k21_winner_numerator_diagnostics"}
for a, b in FIG.items(): shutil.copy(a, OUT / "public/analysis" / f"{b}.png")
# Step 8. 분석 스크립트 사본
for f in ["k21reg.py", "k20fix.py", "k20fitplot.py", "overlay.py", "overlay_type.py", "pre_decomp.py", "pre_decomp2.py", "invalid.py", "invfig.py",
          "r1reg.py", "r1reg2.py", "k21_lee.py", "age_merge.py", "age_reg.py", "ci_change.py", "build_bundle.py", "k21elec.sas"]:
    shutil.copy(f, OUT / "analysis/k21_classified_recheck" / f)
print(json.dumps(dict(national=nat, reg20_21=reg["20대21대_비교"]), ensure_ascii=False)[:1500])
print("provinces", len(prov), "districts", len(dist)); print([(p["province"], p["전체"]["OR"], p.get("OR20", {}).get("OR")) for p in prov])
