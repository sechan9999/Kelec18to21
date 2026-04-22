# 구조적 선거 분석 모델 (18대~21대)

`analysis/structural_election_model.py`는 18~21대 대선을 대상으로 **지역 고정효과 패널모델**을 추정합니다.

## 모델 식

\[
\text{DemShare}_{r,t}=\alpha_r+\beta_1\text{DemShare}_{r,t-1}+\beta_2\text{NationalDem}_t+\beta_3\text{Turnout}_t+\epsilon_{r,t}
\]

- \(\alpha_r\): 지역 고정효과 (지역 고유 성향)
- \(\beta_1\): 직전 선거 득표율 관성
- \(\beta_2\): 전국 민주 진영 사이클 효과
- \(\beta_3\): 투표율 채널

## 실행

```bash
python analysis/structural_election_model.py
```

옵션 예시:

```bash
python analysis/structural_election_model.py \
  --election-json summaries/election_summary.json \
  --regional-json summaries/regional_summary.json \
  --output analysis/structural_model_results.json
```

## 출력

`analysis/structural_model_results.json`

- 추정 계수
- 지역 고정효과
- 적합값/잔차
- RMSE, MAE
