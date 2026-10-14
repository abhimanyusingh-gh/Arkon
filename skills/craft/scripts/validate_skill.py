#!/usr/bin/env python3
"""Validate craft skill reference files."""

import re
import sys
from pathlib import Path


def check_file_length(filepath, max_lines, name):
    """Check that a file doesn't exceed max line count."""
    with open(filepath, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)
    if line_count > max_lines:
        print(f"FAIL: {name} exceeds {max_lines} lines ({line_count} found)")
        return False
    return True


def check_no_absolute_paths(filepath, name):
    """Check that file contains no absolute file paths."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Look for lines with absolute paths (starting with /)
    # Ignore paths within words like "diff/callers" or "component/property"
    # Only flag if line starts with / or has /path/to/file pattern
    for line_num, line in enumerate(lines, 1):
        # Skip comment lines starting with #
        if line.strip().startswith("#"):
            continue
        # Skip lines that look like table cells or code
        if "|" in line or "`" in line:
            continue
        # Look for patterns like " /path/to/file" or lines starting with "/"
        if re.search(r"(?:^|\s)/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-./]+", line):
            print(f"FAIL: {name}:{line_num} contains absolute path: {line.strip()}")
            return False
    return True


def check_no_private_names(filepath, name):
    """Check for obvious private names or internal ticket IDs."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for internal ticket patterns (ME-, PROJ- followed by numbers)
    ticket_pattern = r"\b[A-Z]{2,}-\d{2,}\b"
    matches = re.findall(ticket_pattern, content)
    # Filter out false positives (common abbreviations)
    private_tickets = [m for m in matches if m.startswith(('ME-', 'PROJ-', 'JIRA-'))]

    if private_tickets:
        print(f"FAIL: {name} contains private ticket IDs: {set(private_tickets)}")
        return False

    return True


def rule_exists_in_references(rule_id, references_dir):
    """Check if a rule ID is defined in any reference file."""
    try:
        # Search in all .md files in references directory
        for md_file in references_dir.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for **ID — pattern (bold with em dash or hyphen)
            if re.search(rf"\*\*{re.escape(rule_id)}\s+[—-]", content):
                return True

            # Check for ## ID — pattern (section heading)
            if re.search(rf"^## {re.escape(rule_id)}\s+[—-]", content, re.MULTILINE):
                return True

            # Check for # ID pattern (top-level heading)
            if re.search(rf"^# {re.escape(rule_id)}\s", content, re.MULTILINE):
                return True

        return False
    except Exception as e:
        print(f"Error checking rule {rule_id}: {e}")
        return False


def check_rule_ids_exist(craft_dir):
    """Check that referenced rule IDs are defined."""
    references_dir = craft_dir / "references"
    verification_file = references_dir / "verification.md"
    review_file = references_dir / "review.md"

    errors = []

    for filepath in [verification_file, review_file]:
        if not filepath.exists():
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract backticked IDs
        pattern = r"`([A-Z][A-Z\-]*)`"
        matches = set(re.findall(pattern, content))

        for rule_id in matches:
            if not rule_exists_in_references(rule_id, references_dir):
                errors.append(f"{filepath.name}: undefined rule ID `{rule_id}`")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return False
    return True


def main():
    """Run all validation checks."""
    craft_dir = Path(__file__).parent.parent
    references_dir = craft_dir / "references"

    all_ok = True

    # Check file lengths
    checks = [
        (references_dir / "verification.md", 89, "verification.md"),
        (references_dir / "review.md", 51, "review.md"),
        (references_dir / "security.md", 60, "security.md"),
        (references_dir / "testing.md", 173, "testing.md"),
    ]

    for filepath, max_lines, name in checks:
        if filepath.exists():
            if not check_file_length(filepath, max_lines, name):
                all_ok = False
            else:
                print(f"OK: {name} length OK")

    # Check for absolute paths
    for filepath, _, name in checks:
        if filepath.exists():
            if not check_no_absolute_paths(filepath, name):
                all_ok = False

    # Check for private names
    for filepath, _, name in checks:
        if filepath.exists():
            if not check_no_private_names(filepath, name):
                all_ok = False

    # Check rule IDs
    if not check_rule_ids_exist(craft_dir):
        all_ok = False
    else:
        print("OK: All rule IDs defined")

    if all_ok:
        print("\nValidation PASSED")
        return 0
    else:
        print("\nValidation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
