#!/usr/bin/env bash
set -euo pipefail

# Resolve common merge conflicts for PR #4 against main.
# Strategy:
# - Keep PR feature work for dashboard/layout/docs
# - Keep main's package.json to avoid dependency-policy conflicts

TARGET_MAIN_REMOTE="${1:-origin}"
TARGET_MAIN_BRANCH="${2:-main}"

echo "Fetching ${TARGET_MAIN_REMOTE}/${TARGET_MAIN_BRANCH}..."
git fetch "${TARGET_MAIN_REMOTE}" "${TARGET_MAIN_BRANCH}"

echo "Merging ${TARGET_MAIN_REMOTE}/${TARGET_MAIN_BRANCH} into $(git branch --show-current)..."
set +e
git merge "${TARGET_MAIN_REMOTE}/${TARGET_MAIN_BRANCH}"
MERGE_EXIT=$?
set -e

if [[ ${MERGE_EXIT} -eq 0 ]]; then
  echo "No conflicts found. Merge completed."
  exit 0
fi

echo "Conflicts detected. Applying resolution strategy..."

# Keep feature/UI files from current PR branch
for file in \
  app/components/ElectionDashboard.tsx \
  app/layout.tsx \
  docs/05-vercel-deploy-and-test.md
do
  if git ls-files -u -- "${file}" >/dev/null 2>&1 && [[ -n "$(git ls-files -u -- "${file}")" ]]; then
    git checkout --ours "${file}"
    git add "${file}"
  fi
done

# Keep package configuration from main branch
if git ls-files -u -- package.json >/dev/null 2>&1 && [[ -n "$(git ls-files -u -- package.json)" ]]; then
  git checkout --theirs package.json
  git add package.json
fi

# Optional: page.tsx should generally follow main if conflict appears
if git ls-files -u -- app/page.tsx >/dev/null 2>&1 && [[ -n "$(git ls-files -u -- app/page.tsx)" ]]; then
  git checkout --theirs app/page.tsx
  git add app/page.tsx
fi

if [[ -n "$(git ls-files -u)" ]]; then
  echo "Unresolved conflict(s) remain:"
  git ls-files -u
  echo "Please resolve remaining files manually."
  exit 1
fi

git commit -m "Resolve PR #4 merge conflicts with main (feature-first UI + main package config)"
echo "Conflict resolution commit created successfully."
