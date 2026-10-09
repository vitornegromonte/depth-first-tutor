#!/usr/bin/env bash
# Builds dist/learn.zip for claude.ai. The archive's top level must be the learn/ skill folder:
# claude.ai looks for <skill-name>/SKILL.md inside the zip. LICENSE and NOTICE are copied into it,
# because the zip is a redistribution and Apache-2.0 requires the License to travel with it.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
skills="$root/plugins/depth-first-tutor/skills"
out="$root/dist/learn.zip"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

cp -R "$skills/learn" "$stage/learn"
cp "$root/LICENSE" "$root/NOTICE" "$stage/learn/"

mkdir -p "$root/dist"
rm -f "$out"
(cd "$stage" && zip -qr "$out" learn -x '*.DS_Store')

listing="$(unzip -Z1 "$out")"
if grep -qv '^learn/' <<<"$listing"; then
  echo "FAIL: an entry is outside learn/" >&2
  exit 1
fi
for f in learn/SKILL.md learn/LICENSE learn/NOTICE; do
  if ! grep -qx "$f" <<<"$listing"; then
    echo "FAIL: $f is missing" >&2
    exit 1
  fi
done
echo "OK: $out"
echo "$listing"
