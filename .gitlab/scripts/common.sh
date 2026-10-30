#!/usr/bin/env bash
set -euo pipefail
export CI_PROJECT_DIR="${CI_PROJECT_DIR:-$(pwd)}"
export CI_TEMP_DIR="$CI_PROJECT_DIR/.ci-results/${CI_JOB_NAME_SLUG:-local}"
mkdir -p "$CI_TEMP_DIR"
export CI_JOB_SUMMARY="$CI_TEMP_DIR/summary.md"
export CI_SOURCE_REF="refs/heads/${CI_COMMIT_BRANCH:-${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME:-local}}"
export CI_DIFF_BASE="${CI_MERGE_REQUEST_DIFF_BASE_SHA:-${CI_COMMIT_BEFORE_SHA:-}}"
case "${CI_PIPELINE_SOURCE:-push}" in
  merge_request_event) export CI_EVENT=merge_request ;;
  web|api|trigger) export CI_EVENT=web ;;
  *) export CI_EVENT="${CI_PIPELINE_SOURCE:-push}" ;;
esac
CI_JOB_FAILED=false
ci_outputs() {
  local file="$1" prefix="$2" key value
  [[ -f "$file" ]] || return 0
  while IFS='=' read -r key value; do
    [[ "$key" =~ ^[A-Za-z0-9_-]+$ ]] || continue
    key="${key//-/_}"
    printf -v "${prefix}${key}" '%s' "$value"
    export "${prefix}${key}"
  done < "$file"
}
ci_require() {
  local key missing=false
  for key in "$@"; do
    if [[ -z "${!key:-}" ]]; then printf 'Missing GitLab CI/CD variable: %s\n' "$key" >&2; missing=true; fi
  done
  [[ "$missing" = false ]]
}
