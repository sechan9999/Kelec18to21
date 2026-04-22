# Election Dashboard

A modern, interactive dashboard for analyzing South Korean presidential elections from the 18th to 21st elections (2012-2025).

## Features

- **Key Metrics Overview**: Display of total votes, eligible voters, turnout rate, number of regions, and winner margin
- **Candidate Results**: Ranked candidate results with vote counts and percentages for the 21st election
- **Historical Trends**: Line charts showing voter turnout rates and major party vote shares across elections 18-21
- **Regional Analysis**: Horizontal bar chart comparing Democratic vs. Conservative vote shares across all 17 regions

## Tech Stack

- **Frontend**: React 19 + TypeScript
- **Styling**: Tailwind CSS 4
- **Charts**: Recharts
- **UI Components**: shadcn/ui
- **Build Tool**: Vite
- **Icons**: Lucide React

## Project Structure

```
dashboard/
├── client/
│   ├── public/           # Static assets
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # Utility functions and data
│   │   ├── contexts/     # React contexts
│   │   ├── App.tsx       # Main app component
│   │   ├── main.tsx      # React entry point
│   │   └── index.css     # Global styles
│   └── index.html        # HTML template
├── server/               # Server configuration (static deployment)
├── shared/               # Shared types and constants
├── package.json          # Dependencies
├── vite.config.ts        # Vite configuration
└── tsconfig.json         # TypeScript configuration
```

## Getting Started

### Prerequisites
- Node.js 18+ or pnpm 10+

### Installation

```bash
cd dashboard
pnpm install
```

### Development

```bash
pnpm dev
```

The development server will start at `http://localhost:3000`

### Build

```bash
pnpm build
```

### Preview

```bash
pnpm preview
```

## Data

Election data is sourced from the Korean Central Election Management Committee (중앙선거관리위원회) and includes:

- **18th Election (2012)**: Park Geun-hye vs. Moon Jae-in
- **19th Election (2017)**: Moon Jae-in vs. Hong Jun-pyo
- **20th Election (2022)**: Yoon Suk-yeol vs. Lee Jae-myung
- **21st Election (2025)**: Lee Jae-myung vs. Kim Moon-soo

Data files are located in `client/src/lib/electionData.ts`

## Components

### MetricCard
Displays key statistics with icons and color-coded backgrounds.

### TrendChart
Interactive line chart for displaying trends over multiple elections.

### RegionalChart
Horizontal bar chart for regional vote share comparison.

### CandidateResults
Ranked list of candidates with vote counts and percentages.

## Deployment

The dashboard is deployed and publicly accessible at:
https://electiondash-ji2brbpu.manus.space

## License

MIT

## Author

Created with Manus AI
