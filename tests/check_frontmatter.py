#!/usr/bin/env python3
"""Strict front-matter check: every SKILL.md and rules/*.mdc must start with a
YAML front-matter block that a strict YAML parser (PyYAML safe_load) accepts,
and must contain a non-empty string `description`. Also checks that
.cursor-plugin/plugin.json is valid JSON. Run from the repo root:
    python3 tests/check_frontmatter.py
Exit code 0 = all pass, 1 = at least one failure."""
import json, pathlib, sys
import yaml

root = pathlib.Path(__file__).resolve().parent.parent
fail = 0
files = sorted(list(root.glob("skills/**/SKILL.md")) + list(root.glob("rules/**/*.mdc")))
for f in files:
    rel = f.relative_to(root)
    text = f.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        print(f"FAIL {rel}: no opening ---"); fail = 1; continue
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        print(f"FAIL {rel}: no closing ---"); fail = 1; continue
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as e:
        print(f"FAIL {rel}: YAML error: {str(e).splitlines()[0]}"); fail = 1; continue
    if not isinstance(data, dict) or not isinstance(data.get("description"), str) or not data["description"].strip():
        print(f"FAIL {rel}: missing or empty description"); fail = 1; continue
    print(f"ok   {rel}")
try:
    json.loads((root / ".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
    print("ok   .cursor-plugin/plugin.json")
except Exception as e:
    print(f"FAIL .cursor-plugin/plugin.json: {e}"); fail = 1
print(f"{len(files)} front-matter files checked: {'ALL PASS' if not fail else 'FAILURES'}")
sys.exit(fail)
