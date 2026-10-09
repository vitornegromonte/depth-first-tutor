#!/usr/bin/env python3
"""Structural checks for the depth-first-tutor repository.

Run from the repository root:  python3 scripts/check.py
Prints one PASS/FAIL line per check and exits 1 if any check fails.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "depth-first-tutor"
SKILL_DIR = PLUGIN / "skills" / "learn"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFS = SKILL_DIR / "references"
EXPECTED_REFS = ["tree.md", "grounding.md", "visuals.md", "code-practice.md"]
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

# Leftovers from the private version this skill was forked from.
FORBIDDEN = ["lucas", "vault", "wiki/", "mcp__", "show_widget", "senduserfile", "$arguments"]
PORTUGUESE = re.compile(r"[áàâãéêíóôõúç]|\b(?:você|não|que|para|uma|isso|pelo|pela|então|também)\b", re.IGNORECASE)
CHECKBOX = re.compile(r"^\s*[-*] \[[ xX]\]", re.MULTILINE)
NODE = re.compile(
    r"^(?P<indent>(?:    )*)- \[(?P<state>OPEN|FOCUS|CLOSED|DEFERRED)\]"
    r"(?: \((?P<type>practice|decision|black-box)\))?"
    r"(?: \((?P<mark>K|U|N|\?)\))?"
    r" (?P<rest>\S.*)$"
)
DATE = re.compile(r"\(\d{4}-\d{2}-\d{2}\)")
LINK = re.compile(r"\]\(([^)#\s]+)\)")

results = []


def check(name, ok, detail=""):
    ok = bool(ok)
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))


def read(path):
    return path.read_text(encoding="utf-8") if path.is_file() else None


def load_json(path, name):
    """Load and validate a JSON file. Returns (data, ok) where ok is True if valid."""
    text = read(path)
    if text is None:
        return None, True  # File doesn't exist, not a JSON error
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            check(f"{name} parses as a JSON object", False)
            return None, False
        return data, True
    except json.JSONDecodeError:
        check(f"{name} parses as a JSON object", False)
        return None, False


def check_manifests():
    market = read(ROOT / ".claude-plugin" / "marketplace.json")
    plugin = read(PLUGIN / ".claude-plugin" / "plugin.json")
    check("marketplace.json exists", market is not None)
    check("plugin.json exists", plugin is not None)
    if market is None or plugin is None:
        return

    market_data, market_ok = load_json(ROOT / ".claude-plugin" / "marketplace.json", "marketplace.json")
    if not market_ok:
        return
    plugin_data, plugin_ok = load_json(PLUGIN / ".claude-plugin" / "plugin.json", "plugin.json")
    if not plugin_ok:
        return

    entries = market_data.get("plugins", [])
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        check("marketplace.json parses as a JSON object", False)
        return

    entry = entries[0] if entries else {}
    check("marketplace entry name == plugin.json name == depth-first-tutor",
          entry.get("name") == plugin_data.get("name") == "depth-first-tutor",
          f"{entry.get('name')!r} / {plugin_data.get('name')!r}")
    check("marketplace source points at the plugin", entry.get("source") == "./plugins/depth-first-tutor")
    check("plugin.json license is Apache-2.0", plugin_data.get("license") == "Apache-2.0")


def check_license():
    lic = read(ROOT / "LICENSE") or ""
    notice = read(ROOT / "NOTICE") or ""
    adapted = read(REFS / "code-practice.md") or ""
    check("LICENSE is the Apache License 2.0",
          "Apache License" in lic and "Version 2.0" in lic and
          "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in lic and
          "END OF TERMS AND CONDITIONS" in lic)
    check("NOTICE credits learning-output-style", "learning-output-style" in notice)
    check("code-practice.md carries the adaptation notice",
          "learning-output-style" in adapted and "Apache License, Version 2.0" in adapted)


def check_skill_files():
    check("SKILL.md exists", SKILL_MD.is_file())
    for name in EXPECTED_REFS:
        check(f"references/{name} exists", (REFS / name).is_file())

    # Check skill files under skills/learn/
    for path in sorted(SKILL_DIR.rglob("*.md")) if SKILL_DIR.is_dir() else []:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(SKILL_DIR)
        hits = [w for w in FORBIDDEN if w in text.lower()]
        check(f"{rel}: no leftovers from the private version", not hits, ", ".join(hits))
        check(f"{rel}: no checkbox syntax", CHECKBOX.search(text) is None)
        pt = sorted(set(PORTUGUESE.findall(text)))
        check(f"{rel}: English only", not pt, ", ".join(pt))

    # Check README.md
    readme_path = ROOT / "README.md"
    if readme_path.is_file():
        text = readme_path.read_text(encoding="utf-8")
        hits = [w for w in FORBIDDEN if w in text.lower()]
        check("README.md: no leftovers from the private version", not hits, ", ".join(hits))
        pt = sorted(set(PORTUGUESE.findall(text)))
        check("README.md: English only", not pt, ", ".join(pt))

    # Check examples/*.md
    for path in sorted((ROOT / "examples").glob("*.md")) if (ROOT / "examples").is_dir() else []:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        hits = [w for w in FORBIDDEN if w in text.lower()]
        check(f"{rel}: no leftovers from the private version", not hits, ", ".join(hits))
        pt = sorted(set(PORTUGUESE.findall(text)))
        check(f"{rel}: English only", not pt, ", ".join(pt))


def check_skill_frontmatter():
    text = read(SKILL_MD)
    if text is None:
        return
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    check("SKILL.md has frontmatter", fm is not None)
    if fm is None:
        return
    fm = fm.group(1)
    name = re.search(r"^name:\s*['\"]?(\S+?)['\"]?\s*$", fm, re.MULTILINE)
    name = name.group(1) if name else ""
    check("name matches its folder and the spec",
          name == SKILL_DIR.name and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64, name)
    desc = re.search(r'^description:\s*"(.*)"\s*$', fm, re.MULTILINE)
    desc = desc.group(1) if desc else ""
    has_unescaped_quote = re.search(r'(?<!\\)"', desc) is not None if desc else False
    check("description is quoted, non-empty and at most 1024 characters",
          0 < len(desc) <= 1024 and not has_unescaped_quote, f"{len(desc)}")
    keys = set(re.findall(r"^([A-Za-z0-9_-]+):", fm, re.MULTILINE))
    check("frontmatter uses only Agent Skills fields", keys <= SPEC_FIELDS, ", ".join(sorted(keys - SPEC_FIELDS)))
    lines = len(text.splitlines())
    check("SKILL.md is under 200 lines", lines < 200, f"{lines} lines")
    mentioned = set(re.findall(r"references/([a-z-]+\.md)", text))
    present = {p.name for p in REFS.glob("*.md")} if REFS.is_dir() else set()
    check("every reference SKILL.md mentions exists", mentioned <= present, ", ".join(sorted(mentioned - present)))
    check("every reference file is mentioned in SKILL.md", present <= mentioned, ", ".join(sorted(present - mentioned)))


def check_trees():
    trees = sorted((ROOT / "examples").glob("*.md"))
    check("examples/ has a tree", trees)
    for path in trees:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        check(f"{rel}: no checkbox syntax", CHECKBOX.search(text) is None)
        tree = text.split("## Tree", 1)[1] if "## Tree" in text else ""
        lines = [l for l in tree.splitlines() if l.lstrip().startswith("- ")]
        bad = [l.strip() for l in lines if not NODE.match(l)]
        check(f"{rel}: every node follows the grammar", lines and not bad, bad[0] if bad else "no nodes")
        nodes = [NODE.match(l) for l in lines if NODE.match(l)]
        focus = sum(m["state"] == "FOCUS" for m in nodes)
        check(f"{rel}: at most one FOCUS", focus <= 1, f"{focus}")
        closed = [m["rest"] for m in nodes if m["state"] == "CLOSED" and not ("→" in m["rest"] and DATE.search(m["rest"]))]
        check(f"{rel}: CLOSED nodes carry '→ answer (date)'", not closed, closed[0] if closed else "")
        deferred = [m["rest"] for m in nodes if m["state"] == "DEFERRED" and "— reason:" not in m["rest"]]
        check(f"{rel}: DEFERRED nodes carry a reason", not deferred, deferred[0] if deferred else "")
        aliases = set(re.findall(r"— alias: ([a-z0-9-]+)", tree))
        depends = set(re.findall(r"— depends: ([a-z0-9-]+)", tree))
        check(f"{rel}: every depends: has an alias", depends <= aliases, ", ".join(sorted(depends - aliases)))
        depths = [len(m["indent"]) // 4 for m in nodes]
        check(f"{rel}: indentation grows one level at a time",
              all(b <= a + 1 for a, b in zip([-1] + depths, depths)))


def check_readme():
    text = read(ROOT / "README.md")
    check("README.md exists", text is not None)
    if text is None:
        return
    targets = LINK.findall(text)
    # Filter: skip external links (contain ://), skip mailto:, strip fragments and titles
    relative_targets = []
    for t in targets:
        if "://" in t or t.startswith("mailto:"):
            continue
        # Strip #fragment and optional " title"
        t = re.sub(r'#.*$', '', t)  # Remove #fragment
        t = re.sub(r'\s+"[^"]*"$', '', t)  # Remove optional " title"
        t = t.strip()
        if t:  # Skip empty targets
            relative_targets.append(t)

    missing = [t for t in relative_targets if not (ROOT / t).exists()]
    check("README's relative links point at files that exist", not missing, ", ".join(missing))


def main():
    check_manifests()
    check_license()
    check_skill_files()
    check_skill_frontmatter()
    check_trees()
    check_readme()
    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
