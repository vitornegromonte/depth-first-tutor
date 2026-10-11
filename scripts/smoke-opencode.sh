#!/usr/bin/env bash
# One-turn smoke test for OpenCode. Mirrors scripts/smoke-headless.sh:
# stages the skill in a throwaway folder, tutors headlessly, and checks
# that the first turn creates a tree file and asks for the K/U/N marks.
# Uses your OpenCode login and spends usage. Run `opencode providers list` first.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
mkdir -p "$work/.opencode/skills" "$work/.opencode/commands"
cp -r "$root/plugins/depth-first-tutor/skills/learn" "$work/.opencode/skills/"
cp "$root/.opencode/commands/learn.md" "$work/.opencode/commands/"
cd "$work"
echo "workdir: $work"

status=0
opencode run "Use the learn skill to tutor me on binary search" > transcript.txt 2>&1 || status=$?
if [ "$status" -ne 0 ]; then
  echo "FAIL opencode run exited with status $status (read transcript.txt; check \`opencode providers list\`)"
fi

checks=0
python3 - "$work" <<'PY' || checks=$?
import re
import sys
from pathlib import Path

work = Path(sys.argv[1])
ok = True


def report(name, cond, detail=""):
    global ok
    ok = ok and bool(cond)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  ({detail})"))


trees = sorted((work / "learning-trees").glob("*.md"))
report("tree file created in learning-trees/", trees, "no file")
if trees:
    text = trees[0].read_text()
    report("tree has a Goal: line", re.search(r"^Goal: .+", text, re.M))
    report("tree has a source under Sources:", re.search(r"^Sources:\n- .+", text, re.M))
    nodes = [l for l in text.split("## Tree", 1)[-1].splitlines() if l.lstrip().startswith("- ")]
    grammar = re.compile(r"^(    )*- \[(OPEN|FOCUS|CLOSED|DEFERRED)\]"
                         r"( \((practice|decision|black-box)\))?( \((K|U|N|\?)\))? \S")
    report("tree nodes follow the grammar", nodes and all(grammar.match(l) for l in nodes), nodes[:3])

reply = (work / "transcript.txt").read_text()
report("reply tells the learner to flag what stops them", re.search(r"branch|stops you|stuck", reply, re.I), reply[:300])
report("reply asks for the (K)/(U)/(N) marks", all(m in reply for m in ("(K)", "(U)", "(N)")), reply[:300])
report("reply renders the tree", "├──" in reply or "└──" in reply, reply[:300])
sys.exit(0 if ok else 1)
PY
[ "$status" -eq 0 ] && [ "$checks" -eq 0 ]
