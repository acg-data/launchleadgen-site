#!/usr/bin/env bash
set -euo pipefail
source "$CI_PROJECT_DIR/.gitlab/scripts/common.sh"
cd "$CI_PROJECT_DIR"/.
ci_require CLOUDFLARE_API_TOKEN
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-}"
[[ -n "$CLOUDFLARE_ACCOUNT_ID" ]] || unset CLOUDFLARE_ACCOUNT_ID
cd .
npx --yes wrangler@4.150.0 deploy
