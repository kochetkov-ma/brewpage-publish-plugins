#!/usr/bin/env bash
# Usage: generate.sh <release.json> [--repo DIR] [--git DIR] [--upstream DIR] -> vendor, npm pack, build.
set -euo pipefail

usage='usage: generate.sh <release.json> [--repo DIR] [--git DIR] [--upstream DIR]'
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
config="${1:?$usage}"
shift
git_dir=""
upstream=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo) repo="${2:?$usage}" ;;
    --git) git_dir="${2:?$usage}" ;;
    --upstream) upstream="${2:?$usage}" ;;
    *) echo "$usage" >&2; exit 2 ;;
  esac
  shift 2
done

options=(--config "$config" --repo "$repo")
if [ -n "$git_dir" ]; then options+=(--git "$git_dir"); fi
if [ -n "$upstream" ]; then options+=(--upstream "$upstream"); fi

python3 "$here/release.py" vendor "${options[@]}"
# npm writes deepseek/dsh-brewpage-<version>.tgz from package.json "files"; no lifecycle scripts, no network.
(cd "$repo/deepseek" && npm pack --ignore-scripts > /dev/null)
python3 "$here/release.py" build "${options[@]}"
