'use client';

import React, { useMemo, useState } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Markdown } from './ClassifiedRecheckView';

// 18–21대 분류/미분류(재확인) 투표지 비교 화면. 분자는 보수 후보로 통일.
// 데이터: summaries/k18_21_comparison.json, 보고서: reports/k18_21_comparison_report.md

type Fit = { n: number; intercept?: number; slope?: number; slope_se?: number; r2: number; mse: number; at_half?: number; quad?: number; quad_t?: number };
type Election = {
  id: string; year: number; conservative: string; democratic: string; winner: string; winner_is_conservative: boolean;
  available: boolean; source: string; note?: string; fit: Fit;
  national?: { OR: number; lo: number; hi: number; K: number; R1: number; R2: number };
  outliers?: { province: string; district: string; K: number; rstudent: number }[];
  points?: [number, number, string, string][];
};
type ProvCell = { OR: number; lo: number; hi: number; K: number; n: number };
export type ComparisonData = {
  meta: { title: string; built: string; numerator: string; definitions: Record<string, string>; why_conservative: string; units: string };
  elections: Election[];
  tests_vs_20: { election: string; slope_diff: number; slope_p: number; level_diff_at_half: number; level_p: number }[];
  provinces: ({ province: string } & Partial<Record<'19대' | '20대' | '21대', ProvCell>>)[];
  province_log_or_corr: Record<string, number>;
  data_quality: { pe19: { name_fixes: string[]; within_2pct: number; over_2pct: number; over_2pct_units: string[]; sensitivity_excluding: { n: number; intercept: number; slope: number; r2: number }; sas_reported: { n: number; r2: number; mse: number } }; pe20: { fixes: string[] } };
  figures: { file: string; title: string }[];
};

const COLORS: Record<string, string> = { '18대': '#94a3b8', '19대': '#1baf7a', '20대': '#2a78d6', '21대': '#eb6834' };
const ABBR: Record<string, string> = { 경상북도: '경북', 경상남도: '경남', 충청북도: '충북', 충청남도: '충남', 전라남도: '전남', 전북특별자치도: '전북', 강원특별자치도: '강원', 제주특별자치도: '제주', 경기도: '경기' };
const short = (s: string) => ABBR[s] ?? s.replace(/특별자치시|광역시|특별시/g, '');
const pfmt = (p: number) => (p < 0.001 ? '< 0.001' : `= ${p.toFixed(p < 0.01 ? 3 : 2)}`);
// 셀 배경: OR 1 에서 멀수록 진하게
const cellBg = (v?: number) => {
  if (v == null) return 'transparent';
  const t = Math.min(1, Math.abs(Math.log(v)) / Math.log(1.8));
  return v >= 1 ? `rgba(244,63,94,${0.08 + 0.45 * t})` : `rgba(16,185,129,${0.08 + 0.45 * t})`;
};

function Card({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border border-white/5 bg-slate-900/40 p-6 shadow-xl">
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-bold text-white">{title}</h2>
        {sub && <span className="text-xs text-slate-500">{sub}</span>}
      </div>
      {children}
    </section>
  );
}

export default function CompareElectionsView({ data, report }: { data: ComparisonData; report?: string }) {
  const [tab, setTab] = useState<'overview' | 'provinces' | 'figures' | 'report'>('overview');
  const avail = data.elections.filter((e) => e.available);
  const [shown, setShown] = useState<Record<string, boolean>>(Object.fromEntries(avail.map((e) => [e.id, true])));

  const series = useMemo(() => avail.map((e) => ({
    id: e.id,
    pts: (e.points ?? []).map(([x, y, s, d]) => ({ x, y, s, d, e: e.id })),
    line: [0.02, 0.9].map((x) => ({ x, y: (e.fit.intercept ?? 0) + (e.fit.slope ?? 1) * x })),
  })), [avail]);

  const TabBtn = ({ id, label }: { id: typeof tab; label: string }) => (
    <button onClick={() => setTab(id)} className={`rounded-xl px-4 py-2 text-sm font-semibold transition-all ${tab === id ? 'bg-teal-600 text-white shadow-lg' : 'bg-white/5 text-slate-400 hover:text-white'}`}>{label}</button>
  );

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-teal-500/20 bg-teal-500/5 p-6">
        <h1 className="text-2xl font-bold text-white">{data.meta.title}</h1>
        <p className="mt-2 text-sm text-slate-400">
          분자: {data.meta.numerator}. R1 = {data.meta.definitions.R1} · R2 = {data.meta.definitions.R2} · K = R2/R1 · OR = {data.meta.definitions.OR}. 단위: {data.meta.units}.
        </p>
        <p className="mt-2 text-xs text-teal-200/80">{data.meta.why_conservative}</p>
      </div>

      {/* 선거별 카드 */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data.elections.map((e) => (
          <div key={e.id} className={`rounded-2xl border p-5 ${e.available ? 'border-white/5 bg-slate-900/40' : 'border-dashed border-white/10 bg-slate-900/20'}`}>
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold" style={{ color: COLORS[e.id] }}>{e.id} <span className="text-xs font-normal text-slate-500">{e.year}</span></span>
              <span className={`rounded-md px-2 py-0.5 text-[10px] font-semibold ${e.winner_is_conservative ? 'bg-rose-500/20 text-rose-300' : 'bg-blue-500/20 text-blue-300'}`}>
                당선 {e.winner}
              </span>
            </div>
            <div className="mt-1 text-xs text-slate-400">분자 {e.conservative} · 상대 {e.democratic}</div>
            {e.national ? (
              <>
                <div className="mt-3 text-2xl font-bold text-white">OR {e.national.OR.toFixed(2)}</div>
                <div className="text-xs text-slate-500">95% [{e.national.lo.toFixed(2)}, {e.national.hi.toFixed(2)}] · K {e.national.K.toFixed(3)}</div>
                <div className="mt-2 text-xs text-slate-400">R2 = {e.fit.intercept!.toFixed(3)} + {e.fit.slope!.toFixed(3)}·R1 · R² {e.fit.r2.toFixed(4)} · n {e.fit.n}</div>
              </>
            ) : (
              <>
                <div className="mt-3 text-2xl font-bold text-slate-400">K &gt; 1</div>
                <div className="text-xs text-slate-500">SAS 결과: n {e.fit.n} · R² {e.fit.r2} · MSE {e.fit.mse}</div>
                <div className="mt-2 text-xs text-amber-300/80">{e.note}</div>
              </>
            )}
            <div className="mt-2 text-[10px] text-slate-600">{e.source}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <TabBtn id="overview" label="적합선 비교" /><TabBtn id="provinces" label="시도별 OR" /><TabBtn id="figures" label="그림" /><TabBtn id="report" label="비교 보고서" />
      </div>

      {tab === 'overview' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Card title="R1 대 R2 (구·시·군)" sub="점 = 구·시·군, 선 = 선거별 OLS 적합선, 점선 = K = 1">
              <div className="mb-3 flex flex-wrap gap-3 text-xs">
                {avail.map((e) => (
                  <label key={e.id} className="flex cursor-pointer items-center gap-1.5 text-slate-300">
                    <input type="checkbox" checked={!!shown[e.id]} onChange={() => setShown((s) => ({ ...s, [e.id]: !s[e.id] }))} />
                    <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: COLORS[e.id] }} />{e.id} ({e.conservative})
                  </label>
                ))}
              </div>
              <div className="h-[460px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis type="number" dataKey="x" domain={[0, 1]} ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]} stroke="#64748b" fontSize={11}
                      label={{ value: 'R1 = 보수/(보수+민주), 분류표', position: 'insideBottom', offset: -15, fill: '#64748b', fontSize: 11 }} />
                    <YAxis type="number" dataKey="y" domain={[0, 1]} ticks={[0, 0.2, 0.4, 0.6, 0.8, 1]} stroke="#64748b" fontSize={11}
                      label={{ value: 'R2 (미분류표)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
                    <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]} stroke="#64748b" strokeDasharray="4 4" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ payload }) => {
                      const p = payload?.[0]?.payload as any;
                      if (!p || !p.d) return null;
                      return (
                        <div className="rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-xs text-slate-200 shadow-xl">
                          <div className="font-bold" style={{ color: COLORS[p.e] }}>{p.e} · {short(p.s)} {p.d}</div>
                          <div>R1 {p.x.toFixed(3)} · R2 {p.y.toFixed(3)} · K {(p.y / p.x).toFixed(3)}</div>
                        </div>
                      );
                    }} />
                    {series.filter((s) => shown[s.id]).map((s) => (
                      <Scatter key={s.id} data={s.pts} fill={COLORS[s.id]} fillOpacity={0.55} shape="circle" isAnimationActive={false} />
                    ))}
                    {series.filter((s) => shown[s.id]).map((s) => (
                      <Scatter key={s.id + 'l'} data={s.line} line={{ stroke: COLORS[s.id], strokeWidth: 2.5 }} shape={() => <g />} isAnimationActive={false} />
                    ))}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card title="20대 대비 차이 (HC3)">
              <table className="w-full text-sm">
                <thead className="text-slate-400"><tr><th className="py-1 text-left">선거</th><th className="text-right">기울기 차이</th><th className="text-right">R1=0.5 높이 차이</th></tr></thead>
                <tbody>{data.tests_vs_20.map((t) => (
                  <tr key={t.election} className="border-t border-white/5 text-slate-300">
                    <td className="py-2" style={{ color: COLORS[t.election] }}>{t.election}</td>
                    <td className="text-right">{t.slope_diff >= 0 ? '+' : ''}{t.slope_diff.toFixed(3)} <span className="text-xs text-slate-500">p {pfmt(t.slope_p)}</span></td>
                    <td className="text-right font-semibold text-white">{t.level_diff_at_half >= 0 ? '+' : ''}{t.level_diff_at_half.toFixed(3)} <span className="text-xs font-normal text-slate-500">p {pfmt(t.level_p)}</span></td>
                  </tr>))}</tbody>
              </table>
              <p className="mt-3 text-xs text-slate-500">기울기는 세 선거가 같고(약 1.11), 높이만 다릅니다. 19대 선이 약 6%p 위에 있습니다.</p>
            </Card>
            <Card title="곡선성 (2차항)">
              <ul className="space-y-1 text-sm text-slate-300">
                {avail.map((e) => <li key={e.id}><span style={{ color: COLORS[e.id] }}>{e.id}</span>: R1² 계수 {e.fit.quad?.toFixed(3)} (t {e.fit.quad_t?.toFixed(1)})</li>)}
              </ul>
              <p className="mt-2 text-xs text-slate-500">비율이 0–1에 갇혀 생기는 곡선. 19대가 가장 강합니다.</p>
            </Card>
            <Card title="이상점 (|RStudent| 상위)">
              {avail.map((e) => (
                <div key={e.id} className="mb-2 text-xs text-slate-400">
                  <span className="font-semibold" style={{ color: COLORS[e.id] }}>{e.id}</span>{' '}
                  {e.outliers?.slice(0, 4).map((o) => `${o.district}(${o.rstudent > 0 ? '+' : ''}${o.rstudent})`).join(' · ')}
                </div>
              ))}
            </Card>
          </div>
        </div>
      )}

      {tab === 'provinces' && (
        <Card title="시도별 OR (보수 후보 분자, 95% 구간)" sub={`log OR 상관: ${Object.entries(data.province_log_or_corr).map(([k, v]) => `${k} ${v}`).join(' · ')}`}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-slate-400"><tr><th className="py-2 text-left">시도</th>{['19대', '20대', '21대'].map((e) => <th key={e} className="text-right" style={{ color: COLORS[e] }}>{e} OR [95%]</th>)}</tr></thead>
              <tbody>{data.provinces.map((p) => (
                <tr key={p.province} className="border-t border-white/5 text-slate-300">
                  <td className="py-2">{short(p.province)}</td>
                  {(['19대', '20대', '21대'] as const).map((e) => {
                    const c = p[e];
                    return <td key={e} className="px-2 text-right" style={{ background: cellBg(c?.OR) }}>
                      {c ? <><b className="text-white">{c.OR.toFixed(2)}</b> <span className="text-xs text-slate-400">[{c.lo.toFixed(2)}, {c.hi > 9 ? '…' : c.hi.toFixed(2)}]</span></> : '–'}
                    </td>;
                  })}
                </tr>))}</tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-slate-500">세종은 충남에 포함. 제주는 구·시·군이 2곳뿐이라 구간이 넓습니다.</p>
          <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 text-xs text-slate-400">
            <div>
              <h3 className="mb-1 font-semibold text-slate-300">19대 자료 점검</h3>
              <ul className="list-disc space-y-0.5 pl-4">
                {data.data_quality.pe19.name_fixes.map((f) => <li key={f}>{f}</li>)}
                <li>공개 최종득표 대조: 2% 미만 {data.data_quality.pe19.within_2pct}곳, 2% 이상 {data.data_quality.pe19.over_2pct}곳</li>
                <li>2% 이상 {data.data_quality.pe19.over_2pct}곳 제외 시 {data.data_quality.pe19.sensitivity_excluding.intercept.toFixed(3)} + {data.data_quality.pe19.sensitivity_excluding.slope.toFixed(3)}·R1, R² {data.data_quality.pe19.sensitivity_excluding.r2.toFixed(3)}</li>
                <li>SAS 보고값: n {data.data_quality.pe19.sas_reported.n}, R² {data.data_quality.pe19.sas_reported.r2}, MSE {data.data_quality.pe19.sas_reported.mse}</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-1 font-semibold text-slate-300">20대 자료 보정</h3>
              <ul className="list-disc space-y-0.5 pl-4">{data.data_quality.pe20.fixes.map((f) => <li key={f}>{f}</li>)}</ul>
            </div>
          </div>
        </Card>
      )}

      {tab === 'figures' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {data.figures.map((f) => (
            <figure key={f.file} className="rounded-3xl border border-white/5 bg-slate-900/40 p-4">
              <a href={f.file} target="_blank" rel="noreferrer"><img src={f.file} alt={f.title} loading="lazy" className="w-full rounded-xl bg-white" /></a>
              <figcaption className="mt-2 text-sm text-slate-400">{f.title}</figcaption>
            </figure>
          ))}
        </div>
      )}

      {tab === 'report' && (
        <section className="rounded-3xl border border-white/5 bg-slate-900/40 p-8">
          {report ? <Markdown md={report} /> : <p className="text-sm text-slate-500">보고서가 없습니다.</p>}
        </section>
      )}
    </div>
  );
}
