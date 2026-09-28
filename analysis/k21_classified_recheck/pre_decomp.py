"""관내사전 초과분 분해: 지역 성향(같은 구·시·군 선거일 R1) 통제 전후"""
import pandas as pd, numpy as np, statsmodels.formula.api as smf

# Step 1. 구·시·군마다 관내사전·선거일을 한 줄로
t = pd.read_pickle("k21reg_out.pkl")["t"]
w = t[t["class"].isin(["관내사전", "선거일"])].pivot_table(index=["region", "district"], columns="class", values=["R1", "R2"])
w.columns = [f"{a}_{'pre' if b == '관내사전' else 'day'}" for a, b in w.columns]; w = w.dropna().reset_index()
lg = lambda x: np.log(x / (1 - x))
for c in ["R1_pre", "R1_day", "R2_pre", "R2_day"]: w["l" + c] = lg(w[c])
print("구·시·군", len(w))

# Step 2. 비율 척도 회귀: 관내사전 R2 를 자기 R1 + 지역 성향(선거일 R1)으로
for f in ["R2_pre ~ R1_pre", "R2_pre ~ R1_pre + R1_day", "R2_day ~ R1_day", "R2_day ~ R1_day + R1_pre"]:
    m = smf.ols(f, w).fit(cov_type="HC3")
    print(f"{f:28s} 계수 {m.params.round(3).to_dict()}  SE {m.bse.round(3).to_dict()}  R2 {m.rsquared:.4f}")

# Step 3. 같은 구·시·군 안 비교 (로짓): log(OR_관내사전 / OR_선거일)
w["d"] = (w.lR2_pre - w.lR1_pre) - (w.lR2_day - w.lR1_day)
print(f"구·시·군 안 log OR 차이 평균 {w.d.mean():.3f} (SE {w.d.std() / np.sqrt(len(w)):.3f}) -> OR비 {np.exp(w.d.mean()):.3f}, "
      f"관내사전 OR 이 더 큰 구·시·군 {int((w.d > 0).sum())}/{len(w)}")
m = smf.ols("lR2_pre ~ lR1_pre + lR1_day", w).fit(cov_type="HC3")
print("로짓: lR2_pre ~ lR1_pre + lR1_day", m.params.round(3).to_dict(), m.bse.round(3).to_dict(), round(m.rsquared, 4))

# Step 4. 그림의 7.7%p 격차 분해
mp = smf.ols("R2_pre ~ R1_pre + R1_day", w).fit(); md = smf.ols("R2_day ~ R1_day", w).fit()
b = smf.ols("R1_day ~ R1_pre", w).fit(); print("관내사전 R1 -> 그 지역 선거일 R1:", b.params.round(3).to_dict())
rows = []
for r in [.3, .4, .5]:
    typ = b.predict(pd.DataFrame({"R1_pre": [r]}))[0]
    a = mp.predict(pd.DataFrame({"R1_pre": [r], "R1_day": [typ]}))[0]      # 보통 지역의 관내사전
    s = mp.predict(pd.DataFrame({"R1_pre": [r], "R1_day": [r]}))[0]        # 지역 성향도 r 인 경우
    d = md.predict(pd.DataFrame({"R1_day": [r]}))[0]
    rows.append(dict(R1=r, 그지역선거일R1=typ, 관내사전R2=a, 성향맞춘관내사전R2=s, 선거일R2=d, 원격차=a - d, 성향맞춘격차=s - d))
print(pd.DataFrame(rows).round(3).to_string(index=False))
w.to_pickle("prewide.pkl")
