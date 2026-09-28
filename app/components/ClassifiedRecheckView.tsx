'use client';

import React, { useMemo, useState } from 'react';

// 21대 분류/재확인 투표지 분석 (개표상황표 판독) 화면.
// 데이터: summaries/k21_classified_recheck.json, 보고서: reports/k21_classified_recheck_report.md

type Block = {
  classified_kim: number; classified_lee: number; recheck_kim: number; recheck_lee: number;
  R1: number; R2: number; K: number; OR: number; lo: number; hi: number; n: number;
};
type Province = { province: string; 전체: Block; 관내사전?: Block; 선거일?: Block; OR20?: { OR: number; lo: number; hi: number; n: number } };
type District = {
  province: string; district: string; R1: number; R2: number; K: number; OR: number;
  pred: number; pi_lo: number; pi_hi: number; rstudent: number; cooksD: number; OR_pre?: number; OR_day?: number;
};
export type ClassifiedRecheckData = {
  meta: { title: string; built: string; definitions: Record<string, string>; rows_total: number; rows_used: number; rows_excluded: number; checks: string[]; not_same_as: string };
  candidates: { name: string; classified_pct: number; recheck_pct: number; K: number }[];
  national: Record<string, Block>;
  provinces: Province[];
  districts: District[];
  regression: Record<string, any>;
  invalid_and_age: Record<string, any>;
  pre_vs_day: Record<string, any>;
  figures: { file: string; title: string }[];
};

const short = (s: string) => s.replace(/특별자치시|특별자치도|광역시|특별시|도$/g, '');
const f3 = (v?: number) => (v == null ? '–' : v.toFixed(3));
const orColor = (v: number) => {
  const d = Math.abs(Math.log(v));
  return d >= Math.log(1.4) ? 'text-rose-400' : d >= Math.log(1.2) ? 'text-amber-300' : d > Math.log(1.05) ? 'text-yellow-200' : 'text-emerald-400';
};

// 분자 전환: 두 후보 양자 비율이므로 R_이 = 1 - R_김, OR_이 = 1 / OR_김
type Num = 'kim' | 'lee';
const flipBlock = (b: Block | undefined, num: Num): Block | undefined =>
  !b || num === 'kim' ? b : { ...b, R1: 1 - b.R1, R2: 1 - b.R2, K: (1 - b.R2) / (1 - b.R1), OR: 1 / b.OR, lo: 1 / b.hi, hi: 1 / b.lo };
const flipDistrict = (d: District, num: Num): District =>
  num === 'kim' ? d : {
    ...d, R1: 1 - d.R1, R2: 1 - d.R2, K: (1 - d.R2) / (1 - d.R1), OR: 1 / d.OR,
    OR_pre: d.OR_pre != null ? 1 / d.OR_pre : undefined, OR_day: d.OR_day != null ? 1 / d.OR_day : undefined,
    pred: 1 - d.pred, pi_lo: 1 - d.pi_hi, pi_hi: 1 - d.pi_lo, rstudent: -d.rstudent,
  };

// 아주 작은 마크다운 렌더러: 제목, 목록, 표, 이미지, 굵게, 코드
function inline(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((p, i) =>
    p.startsWith('**') ? <strong key={i} className="text-white">{p.slice(2, -2)}</strong>
    : p.startsWith('`') ? <code key={i} className="rounded bg-white/10 px-1 text-[0.85em] text-sky-200">{p.slice(1, -1)}</code>
    : <React.Fragment key={i}>{p}</React.Fragment>);
}
export function Markdown({ md }: { md: string }) {
  const lines = md.split('\n'); const out: React.ReactNode[] = []; let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (l.startsWith('|')) {
      const rows: string[][] = [];
      while (i < lines.length && lines[i].startsWith('|')) { rows.push(lines[i].split('|').slice(1, -1).map((c) => c.trim())); i++; }
      const [head, , ...body] = rows;
      out.push(
        <div key={i} className="my-4 overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full text-sm">
            <thead className="bg-white/5 text-slate-300"><tr>{head.map((h, j) => <th key={j} className="px-3 py-2 text-left font-semibold">{inline(h)}</th>)}</tr></thead>
            <tbody>{body.map((r, k) => <tr key={k} className="border-t border-white/5">{r.map((c, j) => <td key={j} className="px-3 py-2 text-slate-300">{inline(c)}</td>)}</tr>)}</tbody>
          </table>
        </div>);
      continue;
    }
    const img = l.match(/^!\[(.*?)\]\((.*?)\)/);
    if (img) out.push(<figure key={i} className="my-4"><img src={img[2]} alt={img[1]} className="w-full rounded-xl bg-white" loading="lazy" /><figcaption className="mt-1 text-xs text-slate-500">{img[1]}</figcaption></figure>);
    else if (l.startsWith('# ')) out.push(<h1 key={i} className="mb-3 mt-2 text-2xl font-bold text-white">{l.slice(2)}</h1>);
    else if (l.startsWith('## ')) out.push(<h2 key={i} className="mb-2 mt-8 text-xl font-bold text-white">{l.slice(3)}</h2>);
    else if (l.startsWith('### ')) out.push(<h3 key={i} className="mb-2 mt-6 text-lg font-semibold text-white">{l.slice(4)}</h3>);
    else if (/^\s*- /.test(l)) {
      const items: string[] = [];
      while (i < lines.length && /^\s*- /.test(lines[i])) { items.push(lines[i]); i++; }
      out.push(<ul key={i} className="my-2 space-y-1 text-slate-300">{items.map((it, j) =>
        <li key={j} className={`list-disc ${it.startsWith('  ') ? 'ml-10' : 'ml-5'}`}>{inline(it.replace(/^\s*- /, ''))}</li>)}</ul>);
      continue;
    } else if (l.trim()) out.push(<p key={i} className="my-2 leading-relaxed text-slate-300">{inline(l)}</p>);
    i++;
  }
  return <div>{out}</div>;
}

function Card({ title, children, sub }: { title: string; sub?: string; children: React.ReactNode }) {
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

// OR 과 구간을 가로 막대로 (x 축 0.8 ~ 2.0, 1 에 기준선)
function OrBar({ v, lo, hi, color, X0 = 0.8, X1 = 2.0 }: { v?: number; lo?: number; hi?: number; color: string; X0?: number; X1?: number }) {
  if (v == null) return <div className="h-3" />;
  const pos = (x: number) => `${Math.min(100, Math.max(0, ((x - X0) / (X1 - X0)) * 100))}%`;
  return (
    <div className="relative h-3 w-full">
      <div className="absolute inset-y-0 w-px bg-slate-500" style={{ left: pos(1) }} />
      {lo != null && hi != null && <div className="absolute top-1/2 h-px -translate-y-1/2" style={{ left: pos(lo), width: `calc(${pos(hi)} - ${pos(lo)})`, background: color }} />}
      <div className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full" style={{ left: pos(v), background: color }} />
    </div>
  );
}

export default function ClassifiedRecheckView({ data, report }: { data: ClassifiedRecheckData; report?: string }) {
  const [tab, setTab] = useState<'summary' | 'districts' | 'figures' | 'report'>('summary');
  const [q, setQ] = useState('');
  const [num, setNum] = useState<Num>('kim');
  const n: Record<string, Block> = useMemo(() => Object.fromEntries(Object.entries(data.national).map(([k, b]) => [k, flipBlock(b, num)!])), [data.national, num]);
  const provinces = useMemo(() => data.provinces.map((p) => ({ ...p, 전체: flipBlock(p.전체, num)!, 관내사전: flipBlock(p.관내사전, num), 선거일: flipBlock(p.선거일, num) }))
    .sort((a, b) => a.전체.OR - b.전체.OR), [data.provinces, num]);
  const numName = num === 'kim' ? '김문수(보수 후보)' : '이재명(당선인)';
  const [AX0, AX1] = num === 'kim' ? [0.8, 2.0] : [0.5, 1.6];
  const regLine = num === 'kim' ? data.regression['21대_선형'] : data.regression['21대_당선인분자_선형'];
  const reg = data.regression;
  const cmp = reg['20대21대_비교'];
  const districts = useMemo(() => data.districts.map((d) => flipDistrict(d, num))
    .filter((d) => !q || d.province.includes(q) || d.district.includes(q))
    .sort((a, b) => a.rstudent - b.rstudent), [data.districts, q, num]);

  const kpis = [
    { label: '분석 행 (투표구)', value: data.meta.rows_used.toLocaleString(), sub: `전체 ${data.meta.rows_total.toLocaleString()}행 중 대조용 ${data.meta.rows_excluded}행 제외` },
    { label: '전국 OR', value: n['전체'].OR.toFixed(3), sub: `95% [${n['전체'].lo.toFixed(3)}, ${n['전체'].hi.toFixed(3)}] · K ${n['전체'].K.toFixed(3)}` },
    { label: '관내사전 OR', value: n['관내사전'].OR.toFixed(3), sub: `선거일 ${n['선거일'].OR.toFixed(3)} · 관외사전 ${n['관외사전'].OR.toFixed(3)}` },
    num === 'kim'
      ? { label: '기울기 20대 → 21대', value: `${reg['20대_보정_선형'].params.R_1.toFixed(3)} → ${reg['21대_선형'].params.R_1.toFixed(3)}`, sub: `차이 p = ${cmp.slope_p.toFixed(2)} · R1=0.5 높이 +${cmp.level_diff_at_R1_0_5.toFixed(3)}` }
      : { label: '21대 적합식 (이재명 분자)', value: `${regLine.params.Intercept.toFixed(3)} + ${regLine.params.R_1.toFixed(3)}·R1`, sub: `R² ${regLine.r2.toFixed(4)} · 기울기·R²는 김문수 분자와 같고 절편만 다름` },
  ];

  const TabBtn = ({ id, label }: { id: typeof tab; label: string }) => (
    <button onClick={() => setTab(id)} className={`rounded-xl px-4 py-2 text-sm font-semibold transition-all ${tab === id ? 'bg-violet-600 text-white shadow-lg' : 'bg-white/5 text-slate-400 hover:text-white'}`}>{label}</button>
  );

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-violet-500/20 bg-violet-500/5 p-6">
        <h1 className="text-2xl font-bold text-white">{data.meta.title}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">분자</span>
          {(['kim', 'lee'] as Num[]).map((v) => (
            <button key={v} onClick={() => setNum(v)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${num === v ? 'bg-violet-600 text-white' : 'bg-white/5 text-slate-400 hover:text-white'}`}>
              {v === 'kim' ? '보수 후보 (김문수)' : '당선인 (이재명)'}
            </button>
          ))}
        </div>
        <p className="mt-2 text-sm text-slate-400">
          R1 = {num === 'kim' ? '김문수' : '이재명'}/(이재명+김문수), 분류된 투표지 · R2 = 같은 비율, 재확인대상 투표지 (= 공개 최종득표 − 분류) · K = R2/R1 ·
          OR = (재확인 분자/상대) ÷ (분류 분자/상대). 분자는 {numName}이므로 K, OR &gt; 1 이면 재확인대상에서 {num === 'kim' ? '김문수' : '이재명'} 비율이 더 높습니다.
          {num === 'lee' && ' 두 후보 양자 비율이라 R_이 = 1 − R_김, OR_이 = 1/OR_김 입니다. K는 분자 후보의 기본 득표율에 따라 크기가 달라지므로 지역 비교에는 OR이 더 적합합니다.'}
        </p>
        <p className="mt-2 text-xs text-amber-300/80">※ {data.meta.not_same_as}</p>
        <p className="mt-1 text-xs text-slate-500">검산: {data.meta.checks.join(' · ')} · 작성 {data.meta.built}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((k) => (
          <div key={k.label} className="rounded-2xl border border-white/5 bg-slate-900/40 p-5">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{k.label}</div>
            <div className="mt-2 text-2xl font-bold text-white">{k.value}</div>
            <div className="mt-1 text-xs text-slate-500">{k.sub}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <TabBtn id="summary" label="요약" /><TabBtn id="districts" label="구·시·군" /><TabBtn id="figures" label="그림" /><TabBtn id="report" label="분석 보고서" />
      </div>

      {tab === 'summary' && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card title="전국: 투표구분별" sub="95% 구간은 투표구 군집 기준">
            <table className="w-full text-sm">
              <thead className="text-slate-400"><tr><th className="py-2 text-left">구분</th><th className="text-right">R1</th><th className="text-right">R2</th><th className="text-right">K</th><th className="text-right">OR [95%]</th></tr></thead>
              <tbody>{['전체', '관내사전', '선거일', '관외사전'].map((g) => (
                <tr key={g} className="border-t border-white/5 text-slate-300">
                  <td className="py-2">{g}</td><td className="text-right">{f3(n[g].R1)}</td><td className="text-right">{f3(n[g].R2)}</td><td className="text-right">{f3(n[g].K)}</td>
                  <td className={`text-right font-semibold ${orColor(n[g].OR)}`}>{f3(n[g].OR)} <span className="text-xs font-normal text-slate-500">[{f3(n[g].lo)}, {f3(n[g].hi)}]</span></td>
                </tr>))}</tbody>
            </table>
            <h3 className="mb-2 mt-6 text-sm font-semibold text-slate-300">5후보 득표 비율 (%)</h3>
            <table className="w-full text-sm">
              <thead className="text-slate-400"><tr><th className="py-1 text-left">후보</th><th className="text-right">분류표</th><th className="text-right">재확인</th><th className="text-right">K</th></tr></thead>
              <tbody>{data.candidates.map((c) => (
                <tr key={c.name} className="border-t border-white/5 text-slate-300"><td className="py-1">{c.name}</td><td className="text-right">{c.classified_pct.toFixed(2)}</td><td className="text-right">{c.recheck_pct.toFixed(2)}</td><td className="text-right">{c.K.toFixed(3)}</td></tr>))}</tbody>
            </table>
          </Card>

          <Card title={`시도별 OR (분자 ${numName})`} sub="점 = OR, 선 = 95% 구간, 세로선 = 1">
            <div className="mb-2 flex gap-4 text-xs text-slate-400">
              <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[#eb6834]" />21대 관내사전</span>
              <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[#1baf7a]" />21대 선거일</span>
              <span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[#2a78d6]" />20대 전체 (분자 윤석열: 보수 후보이자 당선인)</span>
            </div>
            <div className="space-y-2">
              {provinces.map((p) => (
                <div key={p.province} className="grid grid-cols-[4.5rem_3.5rem_1fr] items-center gap-2 text-sm">
                  <span className="text-slate-300">{short(p.province)}</span>
                  <span className={`text-right font-semibold ${orColor(p.전체.OR)}`}>{p.전체.OR.toFixed(2)}</span>
                  <div className="space-y-0.5">
                    <OrBar v={p.관내사전?.OR} lo={p.관내사전?.lo} hi={p.관내사전?.hi} color="#eb6834" X0={AX0} X1={AX1} />
                    <OrBar v={p.선거일?.OR} lo={p.선거일?.lo} hi={p.선거일?.hi} color="#1baf7a" X0={AX0} X1={AX1} />
                    <OrBar v={p.OR20?.OR} lo={p.OR20?.lo} hi={p.OR20?.hi} color="#2a78d6" X0={AX0} X1={AX1} />
                  </div>
                </div>
              ))}
              <div className="grid grid-cols-[4.5rem_3.5rem_1fr] text-[10px] text-slate-500"><span /><span className="text-right">21대 전체</span><div className="flex justify-between"><span>{AX0}</span><span>{AX1}</span></div></div>
            </div>
          </Card>

          <Card title="관내사전 vs 선거일 (같은 구·시·군 안)">
            <p className="text-sm text-slate-300">
              관내사전 OR ÷ 선거일 OR = <b className="text-white">{num === 'kim' ? data.pre_vs_day.OR_ratio_pre_over_day : (1 / data.pre_vs_day.OR_ratio_pre_over_day).toFixed(3)}</b> ·
              관내사전이 더 큰 곳 {data.pre_vs_day.districts_pre_higher}/{data.pre_vs_day.districts}
            </p>
            <p className="mt-2 text-xs text-slate-500">{data.pre_vs_day.note}</p>
          </Card>

          <Card title="무효표·재확인율·연령">
            <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
              <li>무효율 2배일 때 OR ×{data.invalid_and_age.OR_if_invalid_doubles} [{data.invalid_and_age.OR_if_invalid_doubles_ci.join(', ')}] — 관련 없음</li>
              <li>재확인율 2배일 때 OR ×{data.invalid_and_age.OR_if_recheck_doubles} [{data.invalid_and_age.OR_if_recheck_doubles_ci.join(', ')}] — 희석 효과</li>
              <li>60세 이상 10%p 높을 때 OR ×{data.invalid_and_age.over60_per10pp_OR} [{data.invalid_and_age.over60_per10pp_ci.join(', ')}]</li>
              <li>60세 이상 비율과 재확인율 상관 r = {data.invalid_and_age.corr_over60_recheck}, 무효율과 r = {data.invalid_and_age.corr_over60_invalid}</li>
            </ul>
          </Card>
        </div>
      )}

      {tab === 'districts' && (
        <Card title={`구·시·군 ${data.districts.length}곳 (분자 ${numName})`} sub="RStudent 오름차순 (적합선 아래로 크게 벗어난 곳부터)">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="시도·구시군 검색" className="mb-4 w-full rounded-xl bg-white/5 px-4 py-2 text-sm text-white ring-1 ring-white/10 placeholder:text-slate-500 sm:w-72" />
          <div className="max-h-[36rem] overflow-auto rounded-xl border border-white/5">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-slate-900 text-slate-400">
                <tr>{['시도', '구시군', 'R1', 'R2', 'K', 'OR', '관내사전 OR', '선거일 OR', '예측 R2', '95% 예측구간', 'RStudent'].map((h) => <th key={h} className="px-3 py-2 text-right first:text-left [&:nth-child(2)]:text-left">{h}</th>)}</tr>
              </thead>
              <tbody>{districts.map((d) => (
                <tr key={d.province + d.district} className="border-t border-white/5 text-slate-300">
                  <td className="px-3 py-1.5">{short(d.province)}</td><td className="px-3">{d.district}</td>
                  <td className="px-3 text-right">{f3(d.R1)}</td><td className="px-3 text-right">{f3(d.R2)}</td><td className="px-3 text-right">{f3(d.K)}</td>
                  <td className={`px-3 text-right font-semibold ${orColor(d.OR)}`}>{f3(d.OR)}</td>
                  <td className="px-3 text-right">{f3(d.OR_pre)}</td><td className="px-3 text-right">{f3(d.OR_day)}</td>
                  <td className="px-3 text-right">{f3(d.pred)}</td><td className="px-3 text-right text-xs text-slate-500">[{f3(d.pi_lo)}, {f3(d.pi_hi)}]</td>
                  <td className={`px-3 text-right ${Math.abs(d.rstudent) > 2 ? 'font-bold text-rose-400' : ''}`}>{d.rstudent.toFixed(2)}</td>
                </tr>))}</tbody>
            </table>
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
