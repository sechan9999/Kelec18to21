"""20대 pe20 보정(오산 복원, 제천 제외) 후 Fit Diagnostics / Fit Plot 다시 그리기"""
import pandas as pd, numpy as np
# k21reg.py 의 그림 함수(reg, stat_box, diagnostics, fitplot)를 그대로 가져온다
src = open("k21reg.py").read()
exec(src[:src.index("# Step 1.")])                                # import·스타일
exec(src[src.index("def reg("):src.index("m21, o21 = reg(")])      # reg()
exec(src[src.index("def stat_box("):src.index("diagnostics(m21,")])  # stat_box, diagnostics, fitplot

# Step 1. 원본 20대 (SAS k20elec 와 같은 249)
p0 = pd.read_pickle("pe20.pkl").copy()
chk = pd.read_pickle("pe20_check.pkl").set_index("district")[["윤석열", "이재명"]]   # 공개 최종득표

# Step 2. 오산: 분류 열(Y1·L1) = 공개 최종득표 → 분류 = 최종 − 재확인 으로 복원
p = p0.copy(); o = p.district == "오산시"
assert (p.loc[o, "Y1"].values == chk.loc["오산시", "윤석열"]) and (p.loc[o, "L1"].values == chk.loc["오산시", "이재명"])
p.loc[o, "Y1"] = p.loc[o, "Y1"] - p.loc[o, "Y2"]; p.loc[o, "L1"] = p.loc[o, "L1"] - p.loc[o, "L2"]
# Step 3. 제천: Y1+L1 = 총투표수, 분류·재확인 모두 공개값과 불일치 → 복원 불가, 제외
pj = p.copy()                                                      # 민감도용: 제천도 최종−재확인으로 넣은 판
j = pj.district == "제천시"; pj.loc[j, "Y1"] = chk.loc["제천시", "윤석열"] - pj.loc[j, "Y2"]; pj.loc[j, "L1"] = chk.loc["제천시", "이재명"] - pj.loc[j, "L2"]
p = p[p.district != "제천시"].reset_index(drop=True)

def prep(df):
    df = df.copy(); df["R_1"] = df.Y1 / (df.Y1 + df.L1); df["R_2"] = df.Y2 / (df.Y2 + df.L2)
    df["R_1sq"] = df.R_1 ** 2; df["K"] = df.R_2 / df.R_1; return df.reset_index(drop=True)
p0, p, pj = prep(p0), prep(p), prep(pj)
print("오산 보정:", p[p.district == "오산시"][["Y1", "L1", "Y2", "L2", "R_1", "R_2", "K"]].round(3).to_string(index=False))

# Step 4. 회귀 (원본 / 보정 / 민감도) + 21대
m0, o0 = reg(p0, "R_2 ~ R_1"); m1, o1 = reg(p, "R_2 ~ R_1"); mj, oj = reg(pj, "R_2 ~ R_1")
q1, _ = reg(p, "R_2 ~ R_1sq + R_1")
k = pd.read_pickle("k21reg_out.pkl")["k"]; m21, o21 = reg(k, "R_2 ~ R_1"); q21, _ = reg(k, "R_2 ~ R_1sq + R_1")

# Step 5. 그림
diagnostics(m1, o1, p.R_2, "Fit Diagnostics for R_2  (20대 보정: 오산 복원, 제천 제외)", "K20_FitDiagnostics_보정.png")
fig, A = plt.subplots(1, 2, figsize=(15, 6.2))
fitplot(A[0], p, m1, "Fit Plot for R_2  (20대 보정)", box=False); fitplot(A[1], k, m21, "Fit Plot for R_2  (21대)", box=False)
for ax, m in zip(A, [m1, m21]): stat_box(ax, m, .03, .97)
A[0].legend(loc="upper center", bbox_to_anchor=(1.05, -.1), ncol=3); fig.tight_layout(); fig.savefig("K20보정_K21_FitPlot.png", dpi=150); plt.close(fig)

# Step 6. 비교표
def summ(nm, m, o, df, q=None):
    r = o.Residual; from scipy import stats as st
    d = dict(자료=nm, N=int(m.nobs), 절편=m.params.Intercept, 기울기=m.params.R_1, 기울기SE=m.bse.R_1, R2=m.rsquared, MSE=m.mse_resid,
             잔차SD=r.std(), 왜도=st.skew(r), 첨도=st.kurtosis(r), SW_p=st.shapiro(r).pvalue,
             RStudent_위2=int((o.RStudent > 2).sum()), RStudent_아래2=int((o.RStudent < -2).sum()), CookD_최대=o.CooksD.max(),
             CookD_최대단위=df.district[o.CooksD.idxmax()], 평균K=df.K.mean())
    if q is not None: d.update(R1sq계수=q.params.R_1sq, R1sq_t=q.tvalues.R_1sq)
    return d
T = pd.DataFrame([summ("20대 원본 (SAS)", m0, o0, p0, reg(p0, "R_2 ~ R_1sq + R_1")[0]),
                  summ("20대 보정 (오산 복원·제천 제외)", m1, o1, p, q1),
                  summ("20대 민감도 (제천 = 최종−재확인)", mj, oj, pj, reg(pj, "R_2 ~ R_1sq + R_1")[0]),
                  summ("21대", m21, o21, k, q21)])
top = lambda df, o, n=5: df.join(o)[["region", "district", "R_1", "R_2", "K", "RStudent", "CooksD"]].reindex(o.RStudent.abs().sort_values(ascending=False).index[:n])
with pd.ExcelWriter("K20_보정_진단.xlsx") as w:
    T.to_excel(w, sheet_name="원본_보정_21대_비교", index=False)
    p0[p0.district.isin(["오산시", "제천시"])][["region", "district", "Y1", "L1", "Y2", "L2", "R_1", "R_2", "K"]].assign(판=["원본"] * 2).to_excel(w, sheet_name="보정내역", index=False)
    pd.concat([p[p.district == "오산시"].assign(판="보정(최종−재확인)"), pj[pj.district == "제천시"].assign(판="민감도만")])[["region", "district", "Y1", "L1", "Y2", "L2", "R_1", "R_2", "K", "판"]].to_excel(w, sheet_name="보정내역", index=False, startrow=4)
    top(p, o1, 10).to_excel(w, sheet_name="20대보정_이상점", index=False)
    p.join(o1).to_excel(w, sheet_name="20대보정_관측별", index=False)
pd.set_option("display.width", 250)
print(T.round(4).T.to_string())
print("\n20대 보정 이상점"); print(top(p, o1, 8).round(3).to_string(index=False))
print("\n제천 민감도:", pj[pj.district == "제천시"][["R_1", "R_2", "K"]].round(3).to_string(index=False), "RStudent", round(oj.RStudent[pj.district == "제천시"].iloc[0], 2))
