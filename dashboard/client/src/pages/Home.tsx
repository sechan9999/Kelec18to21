import { BarChart3, TrendingUp, MapPin, Users } from "lucide-react";
import MetricCard from "@/components/MetricCard";
import TrendChart from "@/components/TrendChart";
import RegionalChart from "@/components/RegionalChart";
import CandidateResults from "@/components/CandidateResults";
import {
  turnoutTrend,
  partyVoteShare,
  regionalData21,
  candidates21,
  keyMetrics21
} from "@/lib/electionData";

export default function Home() {
  // Prepare regional data for chart
  const regionalChartData = Object.entries(regionalData21).map(([region, data]) => ({
    region: region.replace("특별자치", "").replace("광역시", "").replace("특별시", ""),
    democratic: data.democratic,
    conservative: data.conservative
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Election Dashboard</h1>
          </div>
          <p className="text-gray-600">18th to 21st Presidential Elections Analysis</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">21st Election Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <MetricCard
              icon={<Users />}
              label="Total Votes"
              value={keyMetrics21.totalVotes.toLocaleString()}
              color="blue"
            />
            <MetricCard
              icon={<Users />}
              label="Eligible Voters"
              value={keyMetrics21.eligibleVoters.toLocaleString()}
              color="purple"
            />
            <MetricCard
              icon={<TrendingUp />}
              label="Turnout Rate"
              value={`${keyMetrics21.turnout.toFixed(2)}%`}
              color="green"
            />
            <MetricCard
              icon={<MapPin />}
              label="Regions"
              value={keyMetrics21.regions}
              color="orange"
            />
            <MetricCard
              icon={<BarChart3 />}
              label="Winner Margin"
              value={`${keyMetrics21.marginPercentage.toFixed(2)}%`}
              subtitle={`${keyMetrics21.margin.toLocaleString()} votes`}
              color="blue"
            />
          </div>
        </section>

        {/* Candidate Results */}
        <section className="mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <CandidateResults candidates={candidates21} title="21st Election Results" />
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Winner</h3>
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">{keyMetrics21.winner}</div>
                <div className="text-lg text-gray-600 mb-4">{keyMetrics21.winnerParty}</div>
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Winning Margin</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {keyMetrics21.marginPercentage.toFixed(2)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Trend Charts */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Historical Trends (18th-21st)</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <TrendChart
              data={turnoutTrend}
              title="Voter Turnout Rate"
              lines={[{ key: "rate", name: "Turnout %", color: "#3b82f6" }]}
              yAxisLabel="Turnout (%)"
            />
            <TrendChart
              data={partyVoteShare}
              title="Major Party Vote Share"
              lines={[
                { key: "democratic", name: "Democratic", color: "#3b82f6" },
                { key: "conservative", name: "Conservative", color: "#f97316" }
              ]}
              yAxisLabel="Vote Share (%)"
            />
          </div>
        </section>

        {/* Regional Analysis */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Regional Analysis - 21st Election</h2>
          <RegionalChart
            data={regionalChartData}
            title="Vote Share by Region"
          />
        </section>

        {/* Footer */}
        <footer className="border-t border-gray-200 pt-8 mt-12">
          <div className="text-center text-gray-600 text-sm">
            <p>Data source: Korean Central Election Management Committee (중앙선거관리위원회)</p>
            <p className="mt-2">Elections analyzed: 18th, 19th, 20th, 21st Presidential Elections</p>
          </div>
        </footer>
      </main>
    </div>
  );
}
