# Vercel deploy & test guide (new project slug)

This guide shows how to run, validate, and deploy the dashboard to a **new Vercel project** under:
- Team scope: `tcgyvers-projects`
- Team URL: https://vercel.com/tcgyvers-projects
- Suggested project slug: `k18to21-election-dashboard-v2`

## 0) Prerequisites
1. Install Node.js 20 LTS (or newer LTS) and npm.
2. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```
3. Login to Vercel:
   ```bash
   vercel login
   ```

## 1) Pin stable framework/runtime versions
The project is pinned to a stable combo in `package.json`:
- `next`: `14.2.33`
- `react`: `18.3.1`
- `react-dom`: `18.3.1`
- `eslint-config-next`: `14.2.33`

## 2) Regenerate lockfile (run in a network-enabled environment)
```bash
rm -rf node_modules package-lock.json
npm install
```
Then verify lockfile was recreated:
```bash
test -f package-lock.json && echo "lockfile ready"
```

## 3) Local validation (step-by-step)
Run each command and confirm it passes:
```bash
npm run lint
npx tsc --noEmit
npm run build
npm run dev
```
Open the app at:
- http://localhost:3000

## 4) Manual feature checks in browser
Use this checklist:
1. **Language persistence**: switch EN/KO, refresh page, ensure language stays.
2. **Share URL state**: change election/view/lang and confirm querystring updates.
3. **CSV export**: click export and verify downloaded file values.
4. **Accessibility nav**: tab into candidate navigator, use left/right arrows, verify live updates.
5. **Narrative insights**: verify auto insight cards populate for selected election.
6. **Audit scorecards**: confirm completeness/freshness/schema drift/validation counters render.
7. **SEO metadata**: inspect page source for OpenGraph/Twitter tags and JSON-LD script.

## 5) Link to a new Vercel project slug
From repo root:
```bash
vercel link --scope tcgyvers-projects --project k18to21-election-dashboard-v2
```

If project does not exist yet, create in dashboard first with the same slug:
- https://vercel.com/new
- Team: `tcgyvers-projects`
- Project Name: `k18to21-election-dashboard-v2`

## 6) Deploy preview and production
Preview deploy:
```bash
vercel --scope tcgyvers-projects
```

Production deploy:
```bash
vercel --prod --scope tcgyvers-projects
```

## 7) Post-deploy checks
1. Open deployed URL.
2. Re-run feature checklist from section 4.
3. Check Lighthouse for performance/accessibility/SEO baseline.
4. Save deployment URL in project docs.

## Troubleshooting
- If npm install fails due registry restrictions, run steps in CI or a machine with npm registry access.
- If Vercel scope mismatch occurs, run `vercel teams ls` and verify active team is `tcgyvers-projects`.

## PR #4 conflict resolution helper
If GitHub shows merge conflicts on PR #4, run:

```bash
./scripts/resolve_pr4_conflict.sh origin main
```

This helper uses a deterministic strategy:
- keeps PR UI/feature files (`ElectionDashboard.tsx`, `layout.tsx`, deploy guide),
- keeps `main` for `package.json` (to avoid dependency-policy merges),
- keeps `main` for `app/page.tsx` if it conflicts.

Then push the branch:

```bash
git push
```
