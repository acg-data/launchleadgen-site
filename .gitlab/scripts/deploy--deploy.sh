#!/usr/bin/env bash
set -euo pipefail
source .gitlab/scripts/common.sh
export HAS_TOKEN="$(if [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]]; then printf true; else printf false; fi)"
export CI_STEP_OUTPUT="$CI_TEMP_DIR/2.outputs"
: > "$CI_STEP_OUTPUT"
printf '%s\n' 'Build site'
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--2.sh"
ci_outputs "$CI_STEP_OUTPUT" CI_OUT_2_
export CI_STEP_OUTPUT="$CI_TEMP_DIR/3.outputs"
: > "$CI_STEP_OUTPUT"
printf '%s\n' 'Check committed site/ matches src/'
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--3.sh"
ci_outputs "$CI_STEP_OUTPUT" CI_OUT_3_
if [[ "${HAS_TOKEN:-}" = true ]]; then
export CI_STEP_OUTPUT="$CI_TEMP_DIR/4.outputs"
: > "$CI_STEP_OUTPUT"
printf '%s\n' 'Deploy to Cloudflare Workers'
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--4.sh"
ci_outputs "$CI_STEP_OUTPUT" CI_OUT_4_
fi
if [[ "${HAS_TOKEN:-}" != true ]]; then
export CI_STEP_OUTPUT="$CI_TEMP_DIR/5.outputs"
: > "$CI_STEP_OUTPUT"
printf '%s\n' 'Deploy skipped'
bash "$CI_PROJECT_DIR/.gitlab/scripts/deploy--deploy--5.sh"
ci_outputs "$CI_STEP_OUTPUT" CI_OUT_5_
fi
