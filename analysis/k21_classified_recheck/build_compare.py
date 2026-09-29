"""18–21대 비교 묶음: 보수 후보 분자 통일
출력: bundle/summaries/k18_21_comparison.json, bundle/corrected_data/pe18res_corrected.csv, pe19res_corrected.csv, bundle/public/analysis/k18_*·k19_*.png"""
import json, shutil, pandas as pd, numpy as np, statsmodels.formula.api as smf
from pathlib import Path
from scipy import stats
OUT = Path("bundle"); R = lambda v, n=4: None if v is None or not np.isfinite(float(v)) else round(float(v), n)
O3 = pd.read_pickle("overlay4_out.pkl"); D, P, N = O3["D"], O3["P"], O3["N"]
S19 = pd.read_pickle("pe19_out.pkl"); x19 = S19["x"]
S18 = pd.read_pickle("pe18_out.pkl"); x18 = S18["x"]

META = {"18대": dict(year=2012, conservative="박근혜", democratic="문재인", winner="박근혜", winner_is_conservative=True),
        "19대": dict(year=2017, conservative="홍준표", democratic="문재인", winner="문재인", winner_is_conservative=False),
        "20대": dict(year=2022, conservative="윤석열", democratic="이재명", winner="윤석열", winner_is_conservative=True),
        "21대": dict(year=2025, conservative="김문수", democratic="이재명", winner="이재명", winner_is_conservative=False)}
SRC = {"18대": "pe18res2.csv (구·시·군 분류/미분류), 이름은 같은 index 의 19대에서 복원", "19대": "pe19res.xlsx (구·시·군 분류/미분류), 이름 5곳 보정", "20대": "pe20res.xlsx, 오산 복원·제천 제외",
       "21대": "개표상황표 판독(17개 시도, 18,847행)"}

# Step 1. 선거별 적합(선형·2차)·전국 OR·잔차 요약
elections = []
for e in ["18대", "19대", "20대", "21대"]:
    d = D[D.선거 == e].copy(); d["R_1sq"] = d.R_1 ** 2
    m = smf.ols("R_2 ~ R_1", d).fit(); q = smf.ols("R_2 ~ R_1sq + R_1", d).fit(); r = m.resid
    inf = m.get_influence(); rs = inf.resid_studentized_external
    out = d.assign(rs=rs).iloc[np.argsort(-np.abs(rs))[:6]]
    elections.append(dict(id=e, **META[e], available=True, source=SRC[e],
        fit=dict(n=int(m.nobs), intercept=R(m.params.Intercept), slope=R(m.params.R_1), slope_se=R(m.bse.R_1), r2=R(m.rsquared), mse=R(m.mse_resid, 6),
                 at_half=R(m.params.Intercept + .5 * m.params.R_1), quad=R(q.params.R_1sq, 3), quad_t=R(q.tvalues.R_1sq, 2), quad_r2=R(q.rsquared),
                 resid_sd=R(r.std()), skew=R(stats.skew(r), 3), kurt=R(stats.kurtosis(r), 3), shapiro_p=R(stats.shapiro(r).pvalue)),
        national=dict(OR=R(N.loc[e, "OR"]), lo=R(N.loc[e, "lo"]), hi=R(N.loc[e, "hi"]), K=R(N.loc[e, "K"]),
                      R1=R(d.Y1.sum() / (d.Y1 + d.L1).sum()), R2=R(d.Y2.sum() / (d.Y2 + d.L2).sum())),
        outliers=[dict(province=r.시도, district=r.단위, R1=R(r.R_1), R2=R(r.R_2), K=R(r.R_2 / r.R_1), rstudent=R(r.rs, 2)) for _, r in out.iterrows()],
        points=[[R(a, 4), R(b, 4), s, u] for a, b, s, u in zip(d.R_1, d.R_2, d.시도, d.단위)]))

# Step 2. 20대 기준 차이 검정 (HC3)
Mp, Mv = O3["M"]
tests = []
for e in ["18대", "19대", "21대"]:
    tests.append(dict(election=e, vs="20대", slope_diff=R(Mp[f"c:C(선거, Treatment('20대'))[T.{e}]"]), slope_p=R(Mv[f"c:C(선거, Treatment('20대'))[T.{e}]"], 4),
                      level_diff_at_half=R(Mp[f"C(선거, Treatment('20대'))[T.{e}]"]), level_p=R(Mv[f"C(선거, Treatment('20대'))[T.{e}]"], 6)))

# Step 3. 시도별 OR (세종은 충남)
provs = []
W = P.pivot(index="시도", columns="선거", values="OR")
for s in W.sort_values("21대").index:
    row = dict(province=s)
    for e in ["18대", "19대", "20대", "21대"]:
        z = P[(P.선거 == e) & (P.시도 == s)]
        if len(z): z = z.iloc[0]; row[e] = dict(OR=R(z.OR), lo=R(z.lo), hi=R(z.hi), K=R(z.K), n=int(z.n))
    provs.append(row)
C = np.corrcoef(np.log(W.dropna().values.T))

J = dict(meta=dict(title="18–21대 대선 분류/미분류(재확인) 투표지 비교", built="2026-09-28",
                   numerator="보수 후보 (18대 박근혜, 19대 홍준표, 20대 윤석열, 21대 김문수)",
                   definitions=dict(R1="보수/(보수+민주), 분류된 투표지", R2="보수/(보수+민주), 미분류(재확인) 투표지", K="R2/R1", OR="(미분류 보수/민주) ÷ (분류 보수/민주)"),
                   why_conservative="당선인을 분자로 두면 19·21대만 방향이 뒤집힌다. 보수 후보로 통일하면 네 선거 모두 K > 1이다. 기울기는 19·20·21대 약 1.11, 18대 1.06.",
                   units="구·시·군 (세종은 충남 '세종시')"),
         elections=elections, tests_vs_20=tests, provinces=provs,
         province_log_or_corr={"18대-19대": R(C[0, 1], 2), "19대-20대": R(C[1, 2], 2), "20대-21대": R(C[2, 3], 2), "18대-21대": R(C[0, 3], 2)},
         data_quality=dict(
             pe19=dict(name_fixes=["빈 이름(index 31) = 부천시", "여주군 → 여주시", "진구 → 부산진구", "청원군 → 청주시청원구", "청주시흥덕구 행 = 흥덕구 + 서원구"],
                       within_2pct=int((x19.rel < .02).sum()), over_2pct=int((x19.rel >= .02).sum()),
                       over_2pct_units=sorted(x19[x19.rel >= .02].district.tolist()),
                       sensitivity_excluding=dict(n=int(O3["m19s"][2]), intercept=R(O3["m19s"][0]["Intercept"]), slope=R(O3["m19s"][0]["R_1"]), r2=R(O3["m19s"][1])),
                       sas_reported=dict(n=254, r2=0.9696, mse=0.0017, note="SAS n 254 는 data19 아래 요약 통계 5행(mean·sd·median·min·max)이 섞인 값. 올바른 n 은 249")),
             pe18=dict(name_fixes=["CSV 의 구·시·군 이름이 '?' 로 저장되어 같은 index 의 19대 이름으로 복원(index·지역코드·글자수 249행 모두 일치)",
                                   "index 31 = 부천시 (2012년 원미·소사·오정 3개 구 합)", "진구 → 부산진구"],
                       within_2pct=int((x18.rel < .02).sum()), pct_2_10=int(((x18.rel >= .02) & (x18.rel < .1)).sum()), over_10pct=int((x18.rel >= .1).sum()),
                       over_10pct_units=sorted(x18[x18.rel >= .1].district.tolist()),
                       note="대부분 공개값보다 3–5% 적음(부재자투표 등 일부 제외로 보임). 부천시 vote_all 500,000 과 연령 비율은 임의값",
                       sensitivity_excluding=dict(n=int(O3["m18s"][2]), intercept=R(O3["m18s"][0]["Intercept"]), slope=R(O3["m18s"][0]["R_1"]), r2=R(O3["m18s"][1])),
                       sas_reported=dict(n=249, r2=0.9823, mse=0.001)),
             pe20=dict(fixes=["오산: 분류 = 최종 − 재확인으로 복원", "제천: 제외(복원 불가)"])),
         figures=[dict(file="/analysis/k18_k21_fitplot_sas.png", title="18–21대 Fit Plot 겹침 (SAS 스타일, Fit Statistics·20대 대비 검정)"),
                  dict(file="/analysis/k18_k21_overlay.png", title="18·19·20·21대 Fit Plot 겹침과 시도별 OR"),
                  dict(file="/analysis/k18_fitplot.png", title="18대 Fit Plot (박근혜 분자)"),
                  dict(file="/analysis/k18_fit_diagnostics.png", title="18대 Fit Diagnostics"),
                  dict(file="/analysis/k19_fitplot.png", title="19대 Fit Plot (홍준표 분자)"),
                  dict(file="/analysis/k19_fit_diagnostics.png", title="19대 Fit Diagnostics"),
                  dict(file="/analysis/k20_fitplot_corrected.png", title="20대 보정 Fit Plot"),
                  dict(file="/analysis/k21_fitplot.png", title="21대 Fit Plot")])
(OUT / "summaries/k18_21_comparison.json").write_text(json.dumps(J, ensure_ascii=False, indent=1), encoding="utf-8")

# Step 4. 파일 복사: 19대 보정본, 그림, 스크립트
p19 = S19["p"].copy(); p19["공개대조_차이비"] = x19.rel.values; p19["공개대조_2%이상"] = x19.rel.values >= .02
p19.to_csv(OUT / "corrected_data/pe19res_corrected.csv", index=False, encoding="utf-8")
p18 = S18["p"].copy(); p18["공개대조_차이비"] = x18.rel.values; p18["공개대조_10%이상"] = x18.rel.values >= .1
p18.to_csv(OUT / "corrected_data/pe18res_corrected.csv", index=False, encoding="utf-8")
for a, b in {"K18_K21_FitPlot_SAS.png": "k18_k21_fitplot_sas", "K18_K21_겹침.png": "k18_k21_overlay", "K18_FitPlot.png": "k18_fitplot", "K18_FitDiagnostics.png": "k18_fit_diagnostics", "K19_K20_K21_겹침.png": "k19_k20_k21_overlay", "K19_FitPlot.png": "k19_fitplot", "K19_FitDiagnostics.png": "k19_fit_diagnostics"}.items():
    shutil.copy(a, OUT / "public/analysis" / f"{b}.png")
for f in ["pe18.py", "pe19.py", "overlay3.py", "overlay4.py", "build_compare.py", "wbcheck.py", "fixwb.py", "sas_overlay.py", "add_data21.py"]: shutil.copy(f, OUT / "analysis/k21_classified_recheck" / f)
print(json.dumps([dict(id=e["id"], **{k: e.get(k) for k in ["national"]}, fit=e["fit"]) for e in elections], ensure_ascii=False)[:1800])
print(tests); print(J["province_log_or_corr"]); print(len(provs), "provinces", (OUT / "summaries/k18_21_comparison.json").stat().st_size // 1024, "KB")
