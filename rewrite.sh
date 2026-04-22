#!/bin/sh
git filter-branch -f --env-filter '
if [ "$GIT_AUTHOR_EMAIL" = "manus@manus.im" ] || [ "$GIT_AUTHOR_EMAIL" = "manus@ai.dev" ]; then
    export GIT_AUTHOR_NAME="Gyver"
    export GIT_AUTHOR_EMAIL="sechan9999@me.com"
fi
if [ "$GIT_COMMITTER_EMAIL" = "manus@manus.im" ] || [ "$GIT_COMMITTER_EMAIL" = "manus@ai.dev" ]; then
    export GIT_COMMITTER_NAME="Gyver"
    export GIT_COMMITTER_EMAIL="sechan9999@me.com"
fi
' --tag-name-filter cat -- --all
