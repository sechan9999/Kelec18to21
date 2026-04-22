// app/components/Dashboard.tsx
"use client";
import React, { useEffect, useState } from "react";
import { getVersionInfo } from "../../lib/versioning";

interface ElectionSummary {
  totalVotes: number;
  turnoutRate: number;
  winner: string;
  marginVotes: number;
  lastRefresh: string;
  pipelineRunId: string;
  dedupDroppedRows: number;
}

interface CandidatePerf {
  candidate: string;
  votes: number;
  percent: number;
}

interface RegionalSupport {
  region: string;
  conservative: number;
  democratic: number;
}

export default function Dashboard() {
  const [election, setElection] = useState<ElectionSummary | null>(null);
  const [candidates, setCandidates] = useState<CandidatePerf[]>([]);
  const [regions, setRegions] = useState<RegionalSupport[]>([]);
  const [version, setVersion] = useState<any>(null);

  useEffect(() => {
    // Load summary data
    fetch("/summaries/election_summary.json")
      .then((r) => r.json())
      .then(setElection);
    fetch("/summaries/candidate_performance.json")
      .then((r) => r.json())
      .then(setCandidates);
    fetch("/summaries/regional_support.json")
      .then((r) => r.json())
      .then(setRegions);
    // Load version info for methodology panel
    getVersionInfo().then(setVersion);
  }, []);

  return (
    <section className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <header className="glass p-6 text-center">
        <h1 className="text-3xl font-bold text-primary">Electoral Insights Hub</h1>
        <p className="text-secondary">Analytics · Reports · Audits</p>
        <p className="text-sm mt-2 text-foreground">
          Last refresh {election?.lastRefresh?.replace("T", " ").replace("Z", " UTC")}
        </p>
      </header>

      {/* Summary cards */}
      {election && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Total Votes</h2>
            <p className="text-xl">{election.totalVotes.toLocaleString()}</p>
          </div>
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Turnout Rate</h2>
            <p className="text-xl">{(election.turnoutRate * 100).toFixed(1)}%</p>
          </div>
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Winner</h2>
            <p className="text-xl">{election.winner}</p>
          </div>
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Margin (votes)</h2>
            <p className="text-xl">{election.marginVotes.toLocaleString()}</p>
          </div>
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Pipeline Run ID</h2>
            <p className="text-sm break-all">{election.pipelineRunId}</p>
          </div>
          <div className="glass p-4">
            <h2 className="text-primary font-medium">Dedup Dropped Rows</h2>
            <p className="text-sm">{election.dedupDroppedRows}</p>
          </div>
        </div>
      )}

      {/* Candidate Performance */}
      {candidates.length > 0 && (
        <section className="glass p-4">
          <h2 className="text-2xl font-semibold text-primary mb-2">Candidate Performance</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b">
                <th className="pb-2">Candidate</th>
                <th className="pb-2">Votes</th>
                <th className="pb-2">% of Total</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.candidate} className="border-b">
                  <td className="py-1">{c.candidate}</td>
                  <td className="py-1">{c.votes.toLocaleString()}</td>
                  <td className="py-1">{c.percent.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* Regional Support */}
      {regions.length > 0 && (
        <section className="glass p-4">
          <h2 className="text-2xl font-semibold text-primary mb-2">Regional Support</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b">
                <th className="pb-2">Region</th>
                <th className="pb-2">Conservative</th>
                <th className="pb-2">Democratic</th>
              </tr>
            </thead>
            <tbody>
              {regions.map((r) => (
                <tr key={r.region} className="border-b">
                  <td className="py-1">{r.region}</td>
                  <td className="py-1">{r.conservative}%</td>
                  <td className="py-1">{r.democratic}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* Methodology / Trust Panel */}
      <section className="glass p-4">
        <h2 className="text-2xl font-semibold text-primary mb-2">Methodology</h2>
        <p className="text-sm text-foreground">
          Data are aggregated from official election JSON summaries located in the <code>summaries/</code> folder. Metrics such as turnout, swing, and margin are calculated from raw vote counts using standard formulas. All calculations run client‑side for reproducibility.
        </p>
        {version && (
          <ul className="mt-2 list-disc list-inside text-sm text-foreground">
            <li><strong>Data version:</strong> {version.dataVersion}</li>
            {version.commitHash && <li><strong>Commit:</strong> {version.commitHash}</li>}
            <li><strong>Generated at:</strong> {new Date(version.generatedAt).toLocaleString()}</li>
          </ul>
        )}
      </section>
    </section>
  );
}
