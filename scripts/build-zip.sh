#!/usr/bin/env bash
# Builds dist/learn.zip for claude.ai from the committed skill (git HEAD), so uncommitted edits never
# ship. The archive's top level must be the learn/ skill folder: claude.ai looks for
# <skill-name>/SKILL.md inside the zip. LICENSE and NOTICE are copied into it, because the zip is a
# redistribution and Apache-2.0 requires the License to travel with it.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/dist/learn.zip"
rm -f "$out"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

git -C "$root" archive HEAD plugins/depth-first-tutor/skills/learn LICENSE NOTICE | tar -x -f - -C "$stage"
mv "$stage/plugins/depth-first-tutor/skills/learn" "$stage/learn"
mv "$stage/LICENSE" "$stage/NOTICE" "$stage/learn/"
(cd "$stage" && zip -qr "$stage/learn.zip" learn -x '*.DS_Store')

expected="learn/
learn/LICENSE
learn/NOTICE
learn/SKILL.md
learn/references/
learn/references/code-practice.md
learn/references/grounding.md
learn/references/tree.md
learn/references/visuals.md"
listing="$(unzip -Z1 "$stage/learn.zip" | LC_ALL=C sort)"
if [ "$listing" != "$expected" ]; then
  echo "FAIL: the zip does not hold exactly the expected files" >&2
  diff <(echo "$expected") <(echo "$listing") >&2 || true
  exit 1
fi

mkdir -p "$root/dist"
mv "$stage/learn.zip" "$out"
echo "OK: $out"
echo "$listing"
