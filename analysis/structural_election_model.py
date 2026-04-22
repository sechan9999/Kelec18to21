"""18~21대 대선 구조적(Structural) 득표율 모델."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


REGION_NORMALIZATION = {
    "강원도": "강원특별자치도",
    "전라북도": "전북특별자치도",
}


@dataclass
class PanelRow:
    election: int
    region: str
    dem_share: float
    lag_dem_share: float
    national_dem_share: float
    turnout_rate: float


def normalize_region(region: str) -> str:
    return REGION_NORMALIZATION.get(region, region)


def parse_election_number(label: str) -> int:
    digits = "".join(ch for ch in label if ch.isdigit())
    if not digits:
        raise ValueError(f"선거 차수를 해석할 수 없습니다: {label}")
    return int(digits)


def mean(values: List[float]) -> float:
    return sum(values) / len(values)


def dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def solve_linear_system(a: List[List[float]], b: List[float]) -> List[float]:
    """가우스-조던 소거법."""
    n = len(a)
    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("선형시스템이 특이(singular)합니다.")
        aug[col], aug[pivot] = aug[pivot], aug[col]

        pivot_val = aug[col][col]
        aug[col] = [v / pivot_val for v in aug[col]]

        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            aug[r] = [rv - factor * cv for rv, cv in zip(aug[r], aug[col])]

    return [aug[i][-1] for i in range(n)]


def ols_least_squares(x: List[List[float]], y: List[float]) -> List[float]:
    k = len(x[0])
    xtx = [[0.0 for _ in range(k)] for _ in range(k)]
    xty = [0.0 for _ in range(k)]

    for row, target in zip(x, y):
        for i in range(k):
            xty[i] += row[i] * target
            for j in range(k):
                xtx[i][j] += row[i] * row[j]

    return solve_linear_system(xtx, xty)


def infer_democratic_share(candidates: Dict[str, float], total_votes: float) -> float:
    dem_keywords = ("민주", "더불어민주", "민주통합")
    dem_votes = 0.0
    for name, votes in candidates.items():
        if any(keyword in name for keyword in dem_keywords):
            dem_votes += float(votes)

    if dem_votes == 0:
        raise ValueError("민주 계열 후보 득표를 찾지 못했습니다. 후보명 규칙을 확인하세요.")

    return dem_votes / float(total_votes)


def load_national_features(election_path: Path) -> Dict[int, Dict[str, float]]:
    raw = json.loads(election_path.read_text(encoding="utf-8"))

    features: Dict[int, Dict[str, float]] = {}
    for row in raw:
        election = parse_election_number(row["Election"])
        total_votes = float(row["Total Votes"])
        voters = float(row["Voters"])
        turnout = float(row["Turnout"])
        dem_share = infer_democratic_share(row["Candidates"], total_votes)

        features[election] = {
            "national_dem_share": dem_share,
            "turnout_rate": turnout / voters,
        }

    return features


def load_panel(regional_path: Path, national_features: Dict[int, Dict[str, float]]) -> List[PanelRow]:
    regional_raw = json.loads(regional_path.read_text(encoding="utf-8"))

    by_election: Dict[int, Dict[str, float]] = {}
    for election_label, region_map in regional_raw.items():
        election = parse_election_number(election_label)
        by_election[election] = {
            normalize_region(region): float(values["Democratic"])
            for region, values in region_map.items()
        }

    panel: List[PanelRow] = []
    for election in sorted(by_election.keys()):
        prev = election - 1
        if prev not in by_election:
            continue

        regions = sorted(set(by_election[election]).intersection(by_election[prev]))
        for region in regions:
            panel.append(
                PanelRow(
                    election=election,
                    region=region,
                    dem_share=by_election[election][region],
                    lag_dem_share=by_election[prev][region],
                    national_dem_share=national_features[election]["national_dem_share"],
                    turnout_rate=national_features[election]["turnout_rate"],
                )
            )

    return panel


def within_transform(panel: List[PanelRow], feature_names: List[str]):
    region_to_rows: Dict[str, List[PanelRow]] = {}
    for row in panel:
        region_to_rows.setdefault(row.region, []).append(row)

    y_tilde: List[float] = []
    x_tilde: List[List[float]] = []

    for rows in region_to_rows.values():
        y_vals = [r.dem_share for r in rows]
        y_mean = mean(y_vals)

        x_vals = [[getattr(r, f) for f in feature_names] for r in rows]
        x_means = [mean([row[i] for row in x_vals]) for i in range(len(feature_names))]

        for y, x in zip(y_vals, x_vals):
            y_tilde.append(y - y_mean)
            x_tilde.append([xi - x_means[i] for i, xi in enumerate(x)])

    return y_tilde, x_tilde


def fit_fixed_effect_model(panel: List[PanelRow]):
    features = ["lag_dem_share", "national_dem_share", "turnout_rate"]
    y_tilde, x_tilde = within_transform(panel, features)
    beta = ols_least_squares(x_tilde, y_tilde)

    region_to_rows: Dict[str, List[PanelRow]] = {}
    for row in panel:
        region_to_rows.setdefault(row.region, []).append(row)

    alphas: Dict[str, float] = {}
    for region, rows in region_to_rows.items():
        y_bar = mean([r.dem_share for r in rows])
        x_bar = [
            mean([r.lag_dem_share for r in rows]),
            mean([r.national_dem_share for r in rows]),
            mean([r.turnout_rate for r in rows]),
        ]
        alphas[region] = y_bar - dot(x_bar, beta)

    return {
        "coefficients": {
            "lag_dem_share": beta[0],
            "national_dem_share": beta[1],
            "turnout_rate": beta[2],
        },
        "region_fixed_effects": dict(sorted(alphas.items())),
    }


def build_diagnostics(panel: List[PanelRow], model: Dict[str, Dict[str, float]]):
    b = model["coefficients"]
    alphas = model["region_fixed_effects"]

    rows = []
    errors = []
    for row in panel:
        pred = (
            alphas[row.region]
            + b["lag_dem_share"] * row.lag_dem_share
            + b["national_dem_share"] * row.national_dem_share
            + b["turnout_rate"] * row.turnout_rate
        )
        err = row.dem_share - pred
        errors.append(err)
        rows.append(
            {
                "election": row.election,
                "region": row.region,
                "actual_dem_share": row.dem_share,
                "predicted_dem_share": pred,
                "residual": err,
                "structural_components": {
                    "region_baseline": alphas[row.region],
                    "inertia": b["lag_dem_share"] * row.lag_dem_share,
                    "national_cycle": b["national_dem_share"] * row.national_dem_share,
                    "turnout_channel": b["turnout_rate"] * row.turnout_rate,
                },
            }
        )

    mse = mean([e * e for e in errors])
    mae = mean([abs(e) for e in errors])

    return {
        "panel_size": len(panel),
        "rmse": mse ** 0.5,
        "mae": mae,
        "fitted_rows": rows,
    }


def run_model(election_json: Path, regional_json: Path, output: Path) -> None:
    national = load_national_features(election_json)
    panel = load_panel(regional_json, national)
    if not panel:
        raise ValueError("패널 데이터가 비어 있습니다. 입력 파일을 확인하세요.")

    model = fit_fixed_effect_model(panel)
    diagnostics = build_diagnostics(panel, model)

    result = {
        "model_spec": "dem_share_rt = alpha_r + b1*lag_dem_share_rt + b2*national_dem_share_t + b3*turnout_rate_t + e_rt",
        "elections_used": sorted({r.election for r in panel}),
        "regions_used": sorted({r.region for r in panel}),
        "model": model,
        "diagnostics": diagnostics,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="18~21대 대선 구조적 패널모델 추정")
    parser.add_argument("--election-json", type=Path, default=Path("summaries/election_summary.json"))
    parser.add_argument("--regional-json", type=Path, default=Path("summaries/regional_summary.json"))
    parser.add_argument("--output", type=Path, default=Path("analysis/structural_model_results.json"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_model(args.election_json, args.regional_json, args.output)
    print(f"[완료] 구조적 모델 결과 저장: {args.output}")


if __name__ == "__main__":
    main()
