from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_DIR = ROOT / "summaries"
REPORT_DIR = ROOT / "reports"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pct(value: float, digits: int = 2) -> str:
    return f"{value * 100:.{digits}f}%"


def main() -> None:
    election_summary = load_json(SUMMARY_DIR / "election_summary.json")
    regional_summary = load_json(SUMMARY_DIR / "regional_summary.json")
    recount_summary = load_json(SUMMARY_DIR / "k21_recount_summary.json")
    recount_rows = load_json(SUMMARY_DIR / "k21_recount.json")

    e21 = next(item for item in election_summary if item["Election"] == "21st")
    candidates = e21["Candidates"]
    total_votes = e21["Total Votes"]
    voters = e21["Voters"]
    turnout_votes = e21["Turnout"]

    sorted_candidates = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)
    winner, winner_votes = sorted_candidates[0]
    runner_up, runner_up_votes = sorted_candidates[1]
    margin_votes = winner_votes - runner_up_votes
    margin_pct = margin_votes / total_votes

    candidate_shares = [
        {
            "candidate": name,
            "votes": votes,
            "vote_share": votes / total_votes,
        }
        for name, votes in sorted_candidates
    ]

    provinces = regional_summary["21st"]
    province_rows = []
    for province, val in provinces.items():
        dem = val["Democratic"]
        cons = val["Conservative"]
        diff = dem - cons
        label = "swing" if abs(diff) < 0.05 else ("dem_lead" if diff > 0 else "cons_lead")
        province_rows.append(
            {
                "province": province,
                "democratic": dem,
                "conservative": cons,
                "diff": diff,
                "label": label,
            }
        )

    province_rows.sort(key=lambda x: x["diff"], reverse=True)
    strongest_dem = province_rows[:5]
    strongest_cons = sorted(province_rows, key=lambda x: x["diff"])[:5]
    swing_regions = sorted([r for r in province_rows if r["label"] == "swing"], key=lambda x: abs(x["diff"]))

    ratio_rows = recount_summary["candidateRatios"]
    by_k_desc = sorted(ratio_rows, key=lambda x: x["k"], reverse=True)
    by_k_asc = sorted(ratio_rows, key=lambda x: x["k"])

    province_k = recount_summary["provinceRows"]
    province_k_sorted = sorted(province_k, key=lambda x: x["k_lee"], reverse=True)

    outliers_high = [r for r in recount_rows if r["r2"] > r["upper_95_pi"]]
    outliers_low = [r for r in recount_rows if r["r2"] < r["lower_95_pi"]]
    residual_sorted = sorted(recount_rows, key=lambda x: abs(x["residual"]), reverse=True)

    r1_vals = [r["r1"] for r in recount_rows]
    r2_vals = [r["r2"] for r in recount_rows]
    mean_r1 = mean(r1_vals)
    mean_r2 = mean(r2_vals)
    cov = mean([(x - mean_r1) * (y - mean_r2) for x, y in zip(r1_vals, r2_vals)])
    var_r1 = mean([(x - mean_r1) ** 2 for x in r1_vals])
    var_r2 = mean([(y - mean_r2) ** 2 for y in r2_vals])
    corr = cov / ((var_r1 ** 0.5) * (var_r2 ** 0.5))

    output = {
        "election_overview": {
            "total_votes": total_votes,
            "voters": voters,
            "turnout_votes": turnout_votes,
            "turnout_rate": turnout_votes / voters,
            "winner": winner,
            "winner_votes": winner_votes,
            "winner_share": winner_votes / total_votes,
            "runner_up": runner_up,
            "runner_up_votes": runner_up_votes,
            "runner_up_share": runner_up_votes / total_votes,
            "margin_votes": margin_votes,
            "margin_share_of_valid_votes": margin_pct,
        },
        "candidate_shares": candidate_shares,
        "regional_split": {
            "province_count": len(province_rows),
            "dem_lead_count": sum(1 for r in province_rows if r["diff"] > 0),
            "cons_lead_count": sum(1 for r in province_rows if r["diff"] < 0),
            "swing_count": len(swing_regions),
            "strongest_democratic_regions": strongest_dem,
            "strongest_conservative_regions": strongest_cons,
            "swing_regions": swing_regions,
        },
        "k_ratio_summary": {
            "candidate_ratios": ratio_rows,
            "highest_k_candidate": by_k_desc[0],
            "lowest_k_candidate": by_k_asc[0],
            "province_k_top5": province_k_sorted[:5],
            "province_k_bottom5": list(reversed(province_k_sorted[-5:])),
        },
        "district_fit": {
            "n_districts": len(recount_rows),
            "mean_r1": mean_r1,
            "mean_r2": mean_r2,
            "median_residual": median([r["residual"] for r in recount_rows]),
            "correlation_r1_r2": corr,
            "above_upper_95_pi": len(outliers_high),
            "below_lower_95_pi": len(outliers_low),
            "largest_abs_residual_top10": residual_sorted[:10],
        },
    }

    out_json = SUMMARY_DIR / "k21_statistical_analysis.json"
    out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# 21대 대선 데이터 분석 (Velog 시리즈 방식 반영)\n")
    lines.append("## 1) 선거 개요")
    lines.append(f"- 총 유효표: **{total_votes:,}표**, 총 투표수: **{turnout_votes:,}표**, 선거인수: **{voters:,}명**")
    lines.append(f"- 투표율: **{pct(turnout_votes / voters)}**")
    lines.append(f"- 1위: **{winner}** ({winner_votes:,}표, {pct(winner_votes / total_votes)})")
    lines.append(f"- 2위: **{runner_up}** ({runner_up_votes:,}표, {pct(runner_up_votes / total_votes)})")
    lines.append(f"- 격차: **{margin_votes:,}표 ({pct(margin_pct)})**\n")

    lines.append("## 2) 후보별 득표 점유율")
    for row in candidate_shares:
        lines.append(f"- {row['candidate']}: {row['votes']:,}표 ({pct(row['vote_share'])})")
    lines.append("")

    lines.append("## 3) 지역 양강구도 (민주-보수) 분해")
    rs = output["regional_split"]
    lines.append(
        f"- 지역 수: {rs['province_count']}개 (민주 우세 {rs['dem_lead_count']} / 보수 우세 {rs['cons_lead_count']} / 경합 {rs['swing_count']})"
    )
    lines.append("- 민주 우세 상위 5개 지역 (민주-보수 격차):")
    for r in strongest_dem:
        lines.append(f"  - {r['province']}: {pct(r['diff'])}p")
    lines.append("- 보수 우세 상위 5개 지역 (보수-민주 격차):")
    for r in strongest_cons:
        lines.append(f"  - {r['province']}: {pct(-r['diff'])}p")
    if swing_regions:
        lines.append("- 경합 지역 (절대 격차 < 5%p):")
        for r in swing_regions:
            lines.append(f"  - {r['province']}: {'민주' if r['diff'] > 0 else '보수'} {pct(abs(r['diff']))}p")
    lines.append("")

    lines.append("## 4) Velog 계열 지표(R1/R2/K) 요약")
    lines.append("- 후보별 K = R2 / R1")
    for r in ratio_rows:
        lines.append(f"  - {r['name']}({r['party']}): R1={r['r1']:.2f}, R2={r['r2']:.2f}, K={r['k']:.4f}")
    lines.append(f"- 최고 K 후보: {by_k_desc[0]['name']} (K={by_k_desc[0]['k']:.4f})")
    lines.append(f"- 최저 K 후보: {by_k_asc[0]['name']} (K={by_k_asc[0]['k']:.4f})")
    lines.append("- 이재명 후보 기준 지역별 K 상위 5개:")
    for r in province_k_sorted[:5]:
        lines.append(f"  - {r['province']}: K={r['k_lee']:.4f} (R1={r['r1_lee']:.2f}, R2={r['r2_lee']:.2f})")
    lines.append("")

    df = output["district_fit"]
    lines.append("## 5) 기초 적합도 점검 (구/시군 단위)")
    lines.append(f"- 분석 단위: {df['n_districts']}개")
    lines.append(f"- 평균 R1={df['mean_r1']:.4f}, 평균 R2={df['mean_r2']:.4f}, 상관계수={df['correlation_r1_r2']:.4f}")
    lines.append(f"- 95% 예측구간 상회: {df['above_upper_95_pi']}개, 하회: {df['below_lower_95_pi']}개")
    lines.append("- |잔차| 상위 10개 지역:")
    for r in df["largest_abs_residual_top10"]:
        direction = "상회" if r["residual"] > 0 else "하회"
        lines.append(
            f"  - {r['province']} {r['district']}: residual={r['residual']:+.4f} ({direction}), K={r['k_value']:.4f}"
        )

    lines.append("")
    lines.append("## 6) 해석")
    lines.append("- 전국 단위에서는 1·2위 격차가 두 자릿수에 가까운 %p로 나타나 '박빙'보다는 '명확한 우세'에 가깝습니다.")
    lines.append("- 지역 구도는 전통적 영호남 분화가 유지되지만, 수도권/충청권/강원의 일부에서 격차가 상대적으로 축소되어 경합 성격이 강화됩니다.")
    lines.append("- K 지표는 후보별로 비대칭적이며, 특히 3위 후보에서 K가 높게 관측되어 미분류표 분배 구조가 양당 중심과 다르게 작동했을 가능성을 시사합니다.")
    lines.append("- 다만 일부 지역의 큰 잔차는 데이터 생성/집계 과정 또는 지역 특수성의 영향을 받을 수 있으므로, 원자료(개표구 단위) 재검증이 필요합니다.")

    out_md = REPORT_DIR / "k21_election_analysis.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
