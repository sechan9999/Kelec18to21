"""18·19대 K 정규성 검토 + 사용자 결과 파일 QC(봉화군) 확인"""
import pandas as pd, numpy as np
from scipy import stats
x = pd.read_excel("k1819res.xlsx", sheet_name=None)
A, B = x["18대_구시군"], x["19대_구시군"]

# QC: 19대 사용자 집계 vs 선관위 구시군 소계(nec19)
g = pd.read_pickle("nec19.pkl")
q = B.merge(g, left_on=["시도", "구시군"], right_on=["시도", "구"], how="left", indicator=True)
print("19대 매칭", q._merge.value_counts().to_dict())
cm = [("분류_문", "C문"), ("분류_홍", "C홍"), ("분류_안", "C안"), ("분류_유", "C유"), ("분류_심", "C심"), ("미분류_문", "U문"), ("미분류_홍", "U홍"), ("미분류_안", "U안"), ("미분류_유", "U유"), ("미분류_심", "U심"), ("통과_계", "T계"), ("미분류계", "U계")]
d = pd.DataFrame({a: q[a] - q[b] for a, b in cm}); d["구시군"] = q.구시군
bad = d[(d.drop(columns="구시군") != 0).any(axis=1)]
print("선관위 소계와 다른 곳:", len(bad)); print(bad.to_string())
bh = q[q.구시군 == "봉화군"]
print("봉화 사용자 K홍", round(float(bh.K_홍준표.iloc[0]), 4), "| 소계 기준 K홍", round(float(((bh.U홍 / bh.U문) / (bh.C홍 / bh.C문)).iloc[0]), 4))
# 18대: 사용자 파일 vs nec18
n18 = pd.read_pickle("nec18.pkl")
m18 = A.merge(n18, left_on=["시도", "구시군"], right_on=["시도명", "구시군명"])
print("18대 매칭", len(m18), "| 분류·미분류 박·문 모두 일치", int(((m18.분류_박근혜_x == m18.분류_박근혜_y) & (m18.미분류_문재인_x == m18.미분류_문재인_y) & (m18.분류_문재인_x == m18.분류_문재인_y) & (m18.미분류_박근혜_x == m18.미분류_박근혜_y)).sum()))

# 정규성
def norm(v, name):
    v = pd.Series(v).dropna().astype(float)
    sw = stats.shapiro(v); dag = stats.normaltest(v); jb = stats.jarque_bera(v); ad = stats.anderson(v)
    ks = stats.kstest((v - v.mean()) / v.std(ddof=1), "norm")
    return dict(K=name, n=len(v), 평균=v.mean(), 중앙값=v.median(), SD=v.std(ddof=1), 왜도=stats.skew(v), 첨도=stats.kurtosis(v),
                SW_p=sw.pvalue, DAgostino_p=dag.pvalue, JB_p=jb.pvalue, AD_stat=ad.statistic, AD_5pct=ad.critical_values[2], KS_p=ks.pvalue,
                최소=v.min(), 최대=v.max())
rows = []
for nm, v in [("18대 박/문", A.K_박근혜_문재인), ("19대 홍/문", B.K_홍준표), ("19대 안/문", B.K_안철수), ("19대 유/문", B.K_유승민), ("19대 심/문", B.K_심상정)]:
    rows.append(norm(v, nm)); rows.append(norm(np.log(v), "log " + nm))
T = pd.DataFrame(rows).set_index("K"); pd.set_option("display.width", 250); print(T.round(4).to_string())

# 이질성: log K 의 표본오차로 표준화한 z 가 N(0,1) 인지 (모든 구시군 K 가 같은 값이면 z ~ N(0,1))
def hetero(a, b, c, dd, name):
    lk = np.log((c / dd) / (a / b)); se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / dd); w = 1 / se ** 2
    mu = np.sum(w * lk) / w.sum(); z = (lk - mu) / se; Q = np.sum(z ** 2); df = len(z) - 1
    tau2 = max(0, (Q - df) / (w.sum() - (w ** 2).sum() / w.sum()))
    return dict(K=name, n=len(z), 표본오차_중앙값=float(np.median(se)), z_SD=float(z.std(ddof=1)), Q=float(Q), df=df, I2=max(0, (Q - df) / Q), tau=np.sqrt(tau2),
                z_SW_p=stats.shapiro(z).pvalue)
H = pd.DataFrame([hetero(A.분류_박근혜, A.분류_문재인, A.미분류_박근혜, A.미분류_문재인, "18대 박/문"),
                  hetero(B.분류_홍, B.분류_문, B.미분류_홍, B.미분류_문, "19대 홍/문")]).set_index("K")
print(H.round(4).to_string())
# 이질성을 설명하는 변수: R1(분류표 보수 비율)과 상관
A["R1"] = A.분류_박근혜 / (A.분류_박근혜 + A.분류_문재인); B["R1"] = B.분류_홍 / (B.분류_홍 + B.분류_문)
print("log K ~ R1 상관: 18대", round(np.corrcoef(np.log(A.K_박근혜_문재인), A.R1)[0, 1], 3), "19대", round(np.corrcoef(np.log(B.K_홍준표), B.R1)[0, 1], 3))
pd.to_pickle(dict(T=T, H=H, A=A, B=B), "knorm.pkl")
