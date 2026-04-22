import fs from 'fs';
import path from 'path';
import rawElectionData from '../summaries/election_summary.json';
import rawRegionalData from '../summaries/regional_summary.json';
import k21RecountData from '../summaries/k21_recount.json';
import k21RecountSummary from '../summaries/k21_recount_summary.json';
import electionReports from '../summaries/election_reports.json';
import ElectionDashboard from './components/ElectionDashboard';
import type { ElectionRecord, RegionalRecord } from './types/election';

export default async function Home() {
  const reportsDir = path.join(process.cwd(), 'reports');
  
  const analysisReport = fs.readFileSync(path.join(reportsDir, 'election_analysis_report.md'), 'utf-8');
  const excelAudit = fs.readFileSync(path.join(reportsDir, 'excel_audit_report.md'), 'utf-8');
  const presentationAudit = fs.readFileSync(path.join(reportsDir, 'presentation_audit_report.md'), 'utf-8');

  return (
    <ElectionDashboard
      electionData={rawElectionData as unknown as ElectionRecord[]}
      regionalData={rawRegionalData as unknown as Record<string, RegionalRecord>}
      recountData={k21RecountData}
      recountSummary={k21RecountSummary as any}
      electionReports={electionReports as any}
      reports={{
        analysis: analysisReport,
        excelAudit: excelAudit,
        presentationAudit: presentationAudit,
      }}
    />
  );
}
