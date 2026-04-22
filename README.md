# K18to21 Elections Analysis

This repository contains a comprehensive analysis of the 18th to 21st Korean presidential elections. It includes original data, corrected datasets, audit reports, visualizations, and a final analysis report.

## Repository Structure

The files are organized into the following directories:

| Directory | Description |
| :--- | :--- |
| `original_data/` | Contains the initial Excel and PowerPoint files provided for analysis. |
| `corrected_data/` | Contains the audited and corrected version of the election data Excel file. |
| `reports/` | Includes audit reports for both the Excel and PowerPoint files, the final election analysis report, and the new analysis presentation (PPTX and PDF). |
| `visualizations/` | Contains PNG images of key charts: voter turnout, major party vote share, and regional party strength. |
| `summaries/` | Contains JSON files with structured data summaries of the election results and regional analysis. |

## Key Contents

### Data and Analysis
- **Original Data**: `K18to21charts.xlsx`, `18to21Kelection.pptx`
- **Corrected Data**: `K18to21charts_corrected.xlsx` (Fixed visibility issues and unhidden columns).
- **Final Report**: `election_analysis_report.md` provides a detailed breakdown of trends across the four election cycles.
- **21st Election Deep Dive**: `k21_election_analysis.md` provides a focused statistical analysis for the 21st election (vote structure, regional split, R1/R2/K indicators, district-level fit checks).
- **New Presentation**: `18__21.pptx` and `18__21.pdf` summarize the findings in a professional format.

### Audit Reports
- **Excel Audit**: `excel_audit_report.md` details the checks performed on the spreadsheet.
- **Presentation Audit**: `presentation_audit_report.md` identifies formatting and layout improvements for the original presentation.
- **21st Analysis Snapshot**: `k21_statistical_analysis.json` stores derived machine-readable metrics used in the deep-dive report.

### Visualizations
- `voter_turnout.png`: Trends in voter engagement from the 18th to 21st elections.
- `major_party_vote_share.png`: Comparison of Democratic and Conservative party performance.
- `regional_strength_21st.png`: Regional breakdown of party support in the 21st election.

## Usage
This repository is intended for researchers and analysts interested in Korean electoral trends. The data is structured to be easily accessible for further analysis or presentation.

---

## Interactive Dashboard (Next.js)

This project also includes an interactive dashboard built with [Next.js](https://nextjs.org), bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

### Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

### Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

### Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
