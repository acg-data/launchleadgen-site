#!/usr/bin/env bash
set -euo pipefail
source "$CI_PROJECT_DIR/.gitlab/scripts/common.sh"
cd "$CI_PROJECT_DIR"/.
python src/build.py
