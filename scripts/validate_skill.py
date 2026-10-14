#!/usr/bin/env python3
"""Check distributable skill structure, reference routing, examples, and manifests."""

import ast
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/craft"
REFERENCES = SKILL / "references"
LINE_CAPS = {"verification.md": 110, "review.md": 70, "security.md": 75, "testing.md": 200}
RULE_ID_SOURCES = ("verification.md", "review.md")


def referenced_rule_ids(path):
    return set(re.findall(r"`([A-Z][A-Z-]*)`", path.read_text()))


def rule_is_defined(rule_id, references=REFERENCES):
    escaped = re.escape(rule_id)
    definition = re.compile(rf"\*\*{escaped}\s+[—-]|^## {escaped}\s+[—-]|^# {escaped}\s", re.M)
    return any(definition.search(path.read_text()) for path in references.glob("*.md"))


def validate():
    errors = []
    entry = (SKILL / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", entry, re.S)
    if not frontmatter:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        fields = dict(re.findall(r"^([a-z-]+): (.+)$", frontmatter[1], re.M))
        if fields.get("name") != SKILL.name:
            errors.append("SKILL.md: name must match the skill directory")
        description = fields.get("description", "")
        if not description or len(description) > 1024:
            errors.append("SKILL.md: description must have 1–1024 characters")
        if ": " in description or description.startswith(("[", "{", "*", "&", "!")):
            errors.append("SKILL.md: quote complex YAML description syntax")

    routed = set(re.findall(r"`references/([^`]+\.md)`", entry))
    actual = {path.name for path in (SKILL / "references").glob("*.md")}
    for missing in sorted(routed - actual):
        errors.append(f"SKILL.md: missing reference {missing}")
    for orphan in sorted(actual - routed):
        errors.append(f"SKILL.md: reference has no trigger: {orphan}")
    if len(entry.splitlines()) > 110:
        errors.append("SKILL.md: exceeds the repository's 110-line entrypoint budget")
    for name, cap in LINE_CAPS.items():
        lines = len((REFERENCES / name).read_text().splitlines())
        if lines > cap:
            errors.append(f"references/{name}: {lines} lines exceeds the {cap}-line cap")
    for name in RULE_ID_SOURCES:
        for rule_id in sorted(referenced_rule_ids(REFERENCES / name)):
            if not rule_is_defined(rule_id):
                errors.append(f"references/{name}: undefined rule ID {rule_id}")

    documents = [ROOT / "README.md", ROOT / "EVIDENCE.md", *SKILL.rglob("*.md"),
                 *ROOT.glob("docs/*.md"), *ROOT.glob("evals/**/*.md")]
    for path in documents:
        content = path.read_text()
        relative = path.relative_to(ROOT)
        fence = None
        for number, line in enumerate(content.splitlines(), 1):
            match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
            if match:
                marker, suffix = match.groups()
                if fence is None:
                    fence = marker
                elif marker[0] == fence[0] and len(marker) >= len(fence) and not suffix.strip():
                    fence = None
            if fence is not None:
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                target = target.strip("<>").split("#", 1)[0]
                if not target or re.match(r"[a-z]+:", target) or "<" in target:
                    continue
                if not (path.parent / target).is_file():
                    errors.append(f"{relative}:{number}: broken link {target}")
        if fence is not None:
            errors.append(f"{relative}: unclosed fenced block")
        for block in re.findall(r"```json\s*\n(.*?)\n```", content, re.S):
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                errors.append(f"{relative}: invalid JSON example: {error}")
        if path.parent == SKILL / "references":
            for target in re.findall(r"`([a-z][a-z-]+\.md)`", content):
                if not (path.parent / target).is_file():
                    errors.append(f"{relative}: missing sibling reference {target}")

    for path in [*ROOT.glob("scripts/*.py"), *SKILL.glob("scripts/*.py"),
                 *ROOT.glob("evals/**/*.py"), *ROOT.glob("tests/*.py")]:
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            errors.append(str(error))
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    if plugin.get("name") != "craft" or marketplace["plugins"][0].get("name") != "craft":
        errors.append("Plugin and marketplace must name craft")
    if not re.fullmatch(r"\d+\.\d+\.\d+", plugin.get("version", "")):
        errors.append("Plugin version must be semantic major.minor.patch")
    return errors, len(actual), len(documents)


if __name__ == "__main__":
    failures, references, documents = validate()
    for failure in failures:
        print(f"ERROR: {failure}", file=sys.stderr)
    if failures:
        sys.exit(1)
    print(f"PASS: {references} routed references, {documents} Markdown files, Python syntax, JSON examples and plugin manifests")
