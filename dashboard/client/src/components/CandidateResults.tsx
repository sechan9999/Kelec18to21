interface Candidate {
  rank: number;
  name: string;
  party: string;
  votes: number;
  percentage: number;
}

interface CandidateResultsProps {
  candidates: Candidate[];
  title?: string;
}

export default function CandidateResults({
  candidates,
  title = "Candidate Results"
}: CandidateResultsProps) {
  const partyColors: { [key: string]: string } = {
    "더불어민주당": "bg-blue-100 text-blue-800",
    "국민의힘": "bg-red-100 text-red-800",
    "개혁신당": "bg-yellow-100 text-yellow-800",
    "민주노동당": "bg-purple-100 text-purple-800",
    "무소속": "bg-gray-100 text-gray-800"
  };

  const formatVotes = (votes: number) => {
    return votes.toLocaleString();
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="space-y-4">
        {candidates.map((candidate) => (
          <div key={candidate.rank} className="flex items-center gap-4 pb-4 border-b border-gray-100 last:border-0">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-gray-700">{candidate.rank}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-semibold text-gray-900">{candidate.name}</h4>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    partyColors[candidate.party] || "bg-gray-100 text-gray-800"
                  }`}
                >
                  {candidate.party}
                </span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2 mb-1">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full"
                  style={{ width: `${candidate.percentage}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">{formatVotes(candidate.votes)} votes</span>
                <span className="font-semibold text-gray-900">{candidate.percentage.toFixed(2)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
