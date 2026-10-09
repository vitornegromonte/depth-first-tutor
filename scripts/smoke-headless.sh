#!/usr/bin/env bash
# One-turn smoke test. Loads the plugin in a throwaway folder, invokes the skill headlessly and checks
# that the first turn fetches a source, creates a tree file and asks for the K/U/N marks.
# Uses your Claude Code login and spends usage (one short session).
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
plugin="$root/plugins/depth-first-tutor"
work="$(mktemp -d)"
cd "$work"

claude -p \
  --setting-sources project \
  --plugin-dir "$plugin" \
  --add-dir "$plugin" \
  --allowedTools "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch" \
  --max-turns 25 \
  --output-format stream-json --verbose \
  "/depth-first-tutor:learn binary search" > transcript.jsonl

echo "workdir: $work"
python3 - "$work" <<'PY'
import json
import re
import sys
from pathlib import Path

work = Path(sys.argv[1])
events = [json.loads(l) for l in (work / "transcript.jsonl").read_text().splitlines() if l.strip()]
ok = True


def report(name, cond, detail=""):
    global ok
    ok = ok and bool(cond)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  ({detail})"))


init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
report("plugin loaded", "depth-first-tutor" in json.dumps(init), "not in the init event")
print("plugins in the session:", [p.get("name") for p in init.get("plugins", [])])

tools = [b.get("name") for e in events if e.get("type") == "assistant"
         for b in e.get("message", {}).get("content", []) if b.get("type") == "tool_use"]
report("a source was fetched", any(t in ("WebSearch", "WebFetch") for t in tools), tools)

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

texts = [b.get("text", "") for e in events if e.get("type") == "assistant"
         for b in e.get("message", {}).get("content", []) if b.get("type") == "text"]
result = next((e for e in reversed(events) if e.get("type") == "result"), {})
reply = "\n".join(texts + [result.get("result", "")])
report("reply tells the learner to flag what stops them", re.search(r"branch|stops you|stuck", reply, re.I), reply[:300])
report("reply asks for the (K)/(U)/(N) marks", all(m in reply for m in ("(K)", "(U)", "(N)")), reply[:300])
report("reply renders the tree", "├──" in reply or "└──" in reply, reply[:300])
sys.exit(0 if ok else 1)
PY
