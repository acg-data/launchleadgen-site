#!/usr/bin/env bash
set -euo pipefail
source "$CI_PROJECT_DIR/.gitlab/scripts/common.sh"
cd "$CI_PROJECT_DIR"/.
echo "::notice::CLOUDFLARE_API_TOKEN is not set, so the site was built but not deployed. See README."
