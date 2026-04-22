// Election data for 18th to 21st elections
export const turnoutTrend = [
  { election: "18th", rate: 59.8 },
  { election: "19th", rate: 77.2 },
  { election: "20th", rate: 77.1 },
  { election: "21st", rate: 79.3 }
];

export const partyVoteShare = [
  { election: "18th", democratic: 48.0, conservative: 51.6 },
  { election: "19th", democratic: 41.1, conservative: 24.0 },
  { election: "20th", democratic: 48.6, conservative: 49.2 },
  { election: "21st", democratic: 49.4, conservative: 41.2 }
];

export const electionSummary = [
  {
    election: "18th",
    totalVotes: 30594621,
    voters: 40507842,
    winner: "박근혜 (새누리당)",
    winnerVotes: 15773128,
    runnerUp: "문재인 (민주통합당)",
    runnerUpVotes: 14692632,
    margin: 1080496
  },
  {
    election: "19th",
    totalVotes: 32672175,
    voters: 42479710,
    winner: "문재인 (더불어민주당)",
    winnerVotes: 13423800,
    runnerUp: "홍준표 (자유한국당)",
    runnerUpVotes: 7852849,
    margin: 5570951
  },
  {
    election: "20th",
    totalVotes: 33760311,
    voters: 44197692,
    winner: "윤석열 (국민의힘)",
    winnerVotes: 16394815,
    runnerUp: "이재명 (더불어민주당)",
    runnerUpVotes: 16147738,
    margin: 247077
  },
  {
    election: "21st",
    totalVotes: 34980616,
    voters: 44391871,
    winner: "이재명 (더불어민주당)",
    winnerVotes: 17287513,
    runnerUp: "김문수 (국민의힘)",
    runnerUpVotes: 14395639,
    margin: 2891874
  }
];

export const regionalData21 = {
  "강원특별자치도": { democratic: 48.2, conservative: 51.8 },
  "경기도": { democratic: 57.9, conservative: 42.1 },
  "경상남도": { democratic: 43.1, conservative: 56.9 },
  "경상북도": { democratic: 27.6, conservative: 72.4 },
  "광주광역시": { democratic: 91.4, conservative: 8.6 },
  "대구광역시": { democratic: 25.6, conservative: 74.4 },
  "대전광역시": { democratic: 54.4, conservative: 45.6 },
  "부산광역시": { democratic: 43.9, conservative: 56.1 },
  "서울특별시": { democratic: 53.1, conservative: 46.9 },
  "세종특별자치시": { democratic: 62.6, conservative: 37.4 },
  "울산광역시": { democratic: 47.2, conservative: 52.8 },
  "인천광역시": { democratic: 57.3, conservative: 42.7 },
  "전라남도": { democratic: 91.0, conservative: 9.0 },
  "전북특별자치도": { democratic: 88.3, conservative: 11.7 },
  "제주특별자치도": { democratic: 61.2, conservative: 38.8 },
  "충청남도": { democratic: 52.4, conservative: 47.6 },
  "충청북도": { democratic: 52.3, conservative: 47.7 }
};

export const candidates21 = [
  { rank: 1, name: "이재명", party: "더불어민주당", votes: 17287513, percentage: 49.42 },
  { rank: 2, name: "김문수", party: "국민의힘", votes: 14395639, percentage: 41.15 },
  { rank: 3, name: "이준석", party: "개혁신당", votes: 2917523, percentage: 8.34 },
  { rank: 4, name: "권영국", party: "민주노동당", votes: 344150, percentage: 0.98 },
  { rank: 5, name: "송진호", party: "무소속", votes: 35791, percentage: 0.10 }
];

export const keyMetrics21 = {
  totalVotes: 34980616,
  eligibleVoters: 44391871,
  turnout: 79.38,
  regions: 17,
  winner: "이재명",
  winnerParty: "더불어민주당",
  margin: 2891874,
  marginPercentage: 8.27
};
