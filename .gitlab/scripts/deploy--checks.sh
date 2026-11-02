#!/usr/bin/env bash
set -euo pipefail
source .gitlab/scripts/common.sh
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--2.sh"
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--3.sh"
