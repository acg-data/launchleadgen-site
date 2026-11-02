#!/usr/bin/env bash
set -euo pipefail
source "$CI_PROJECT_DIR/.gitlab/scripts/common.sh"
cd "$CI_PROJECT_DIR"/.
git diff --quiet -- site || echo "::warning::Committed site/ differs from a fresh build. Run python3 src/build.py and commit. Deploying the fresh build."
