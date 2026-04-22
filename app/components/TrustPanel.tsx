"use client";

import React, { useEffect, useState } from 'react';
import { getVersionInfo, VersionInfo } from '../../lib/versioning';

interface Definition {
  term: string;
  description: string;
}

const definitions: Definition[] = [
  { term: 'Turnout', description: 'Percentage of eligible voters who cast a ballot.' },
  { term: 'Swing', description: 'Change in vote share between two consecutive elections.' },
  { term: 'Margin', description: 'Difference in vote share between the winner and the runner‑up.' },
  { term: 'Recount', description: 'A secondary count of ballots to verify the official result.' },
];

export default function TrustPanel() {
  const [version, setVersion] = useState<VersionInfo | null>(null);

  useEffect(() => {
    // Load version metadata once on mount.
    getVersionInfo().then(setVersion).catch(() => setVersion(null));
  }, []);

  return (
    <section className="glass p-6 md:p-8 max-w-4xl mx-auto my-8" aria-labelledby="trust-panel-title">
      <h2 id="trust-panel-title" className="text-2xl font-bold mb-4 text-primary">
        Trust &amp; Methodology
      </h2>

      {/* Definitions */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2 text-secondary">Key Definitions</h3>
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {definitions.map((def) => (
            <div key={def.term}>
              <dt className="font-medium text-primary">{def.term}</dt>
              <dd className="text-sm text-foreground">{def.description}</dd>
            </div>
          ))}
        </dl>
      </div>

      {/* Version info */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold mb-2 text-secondary">Data Version</h3>
        {version ? (
          <ul className="list-disc list-inside text-sm text-foreground">
            <li><strong>Version:</strong> {version.dataVersion}</li>
            {version.commitHash && <li><strong>Commit:</strong> {version.commitHash}</li>}
            <li><strong>Generated at:</strong> {new Date(version.generatedAt).toLocaleString()}</li>
          </ul>
        ) : (
          <p className="text-sm text-foreground">Loading version information…</p>
        )}
      </div>

      {/* Methodology */}
      <div>
        <h3 className="text-xl font-semibold mb-2 text-secondary">Methodology</h3>
        <p className="text-sm text-foreground">
          The dashboard aggregates official election JSON summaries located in the <code>summaries/</code> folder. Metrics such as turnout, swing, and margin are calculated from raw vote counts using standard formulas. All calculations are performed client‑side in a reproducible, stateless manner, ensuring that the same input data always yields identical results.
        </p>
      </div>
    </section>
  );
}
