#!/usr/bin/env bash
# Usage: check.sh <release.json> [--ref REF] [--upstream DIR] [--assets DIR] -> rebuild REF in a temp dir, compare.
set -euo pipefail

usage='usage: check.sh <release.json> [--ref REF] [--upstream DIR] [--assets DIR]'
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
config="${1:?$usage}"
shift
ref="HEAD"
upstream=""
published=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --ref) ref="${2:?$usage}" ;;
    --upstream) upstream="${2:?$usage}" ;;
    --assets) published="${2:?$usage}" ;;
    *) echo "$usage" >&2; exit 2 ;;
  esac
  shift 2
done

# Everything is written under a fresh temp dir; the checkout is only read.
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir "$work/expected" "$work/tree"
git -C "$repo" archive "$ref" | tar -x -C "$work/expected"
git -C "$repo" archive "$ref" | tar -x -C "$work/tree"

python3 "$here/release.py" reset --config "$config" --repo "$work/tree" --git "$repo"
options=("$config" --repo "$work/tree" --git "$repo")
if [ -n "$upstream" ]; then options+=(--upstream "$upstream"); fi
bash "$here/generate.sh" "${options[@]}"

diff -r "$work/expected" "$work/tree"
echo "TREE $(find "$work/tree" -type f | wc -l | tr -d ' ') files, regenerated tree equals $ref"

python3 "$here/release.py" assets --ref "$ref" --git "$repo" --out "$work/assets"
(cd "$work/assets" && shasum -a 256 -c SHASUMS256.txt)
if [ -n "$published" ]; then
  diff -r "$published" "$work/assets"
  echo "ASSETS $(find "$work/assets" -type f | wc -l | tr -d ' ') files equal to $published"
fi
echo "OK $ref reproduces from $config"
