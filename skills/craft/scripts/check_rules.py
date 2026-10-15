#!/usr/bin/env python3
"""Report mechanical review findings in a Git diff: deleted tests, weakened assertions, skips and empty catches."""

import argparse
from pathlib import PurePosixPath
import re
import subprocess
import sys


TEST_DIRECTORIES = {"test", "tests", "__tests__", "spec"}
TEST_NAME = re.compile(r"(?:^test_.*\.py|_test\.py|Tests?\.java|\.(?:test|spec)\.(?:tsx?|js))$")
ASSERTION_TOKENS = ("assert", "expect(", "assertThat", "verify(", "should")
SKIP = re.compile(r"@Disabled\b|@Ignore\b|@unittest\.skip|pytest\.mark\.skip|\.skip\(|\bxit\(|\bxdescribe\(")
FOCUS = re.compile(r"\b(?:it|describe|test)\.only\(")
EMPTY_CATCH = re.compile(r"catch\s*(\([^)]*\))?\s*\{\s*\}|except[^:]*:\s*pass\s*$")
IGNORE_MARKER = "check-rules: ignore"


def is_test_file(path):
    pure = PurePosixPath(path)
    return any(part in TEST_DIRECTORIES for part in pure.parts[:-1]) or bool(TEST_NAME.search(pure.name))


def git_diff(repo, base, head):
    result = subprocess.run(
        ["git", "-C", repo, "diff", "--no-color", "--no-ext-diff", "--no-textconv", "--find-renames",
         "--src-prefix=a/", "--dst-prefix=b/", "-U0", base, head],
        check=True, capture_output=True, text=True,
    )
    return result.stdout


def read_header(record, line):
    if line.startswith("rename from "):
        record["old"] = line[len("rename from "):]
    elif line.startswith("rename to "):
        record["new"] = line[len("rename to "):]
    elif line.startswith("deleted file mode"):
        record["deleted"] = True
    elif line.startswith("--- a/"):
        record["old"] = record["old"] or line[len("--- a/"):]
    elif line.startswith("+++ b/"):
        record["new"] = line[len("+++ b/"):]


def parse_diff(text):
    files, record, in_hunk, line_number = [], None, False, 0
    for line in text.splitlines():
        if line.startswith("diff --git "):
            record = {"old": None, "new": None, "deleted": False, "added": [], "removed": []}
            files.append(record)
            in_hunk = False
        elif record is None:
            continue
        elif line.startswith("@@"):
            in_hunk = True
            line_number = int(re.search(r"\+(\d+)", line).group(1))
        elif not in_hunk:
            read_header(record, line)
        elif line.startswith("+"):
            record["added"].append((line_number, line[1:]))
            line_number += 1
        elif line.startswith("-"):
            record["removed"].append(line[1:])
    return files


def assertion_count(lines):
    return sum(any(token in line for token in ASSERTION_TOKENS) for line in lines)


def structure_findings(record):
    old, new = record["old"], record["new"] or record["old"]
    if record["deleted"]:
        return [f"TEST-NODELETE {old}:0 test file deleted"] if is_test_file(old) else []
    findings = []
    if old and old != new and is_test_file(old):
        findings.append(f"TEST-NODELETE {old}:0 test file renamed to {new}")
    if is_test_file(new):
        removed = assertion_count(record["removed"])
        added = assertion_count(text for _, text in record["added"])
        if removed > added:
            findings.append(f"TEST-NODELETE {new}:0 net assertions removed "
                            f"({removed} removed, {added} added)")
    return findings


def line_findings(path, line_number, text):
    if IGNORE_MARKER in text:
        return []
    location = f"{path}:{line_number}"
    if is_test_file(path) and FOCUS.search(text):
        return [f"TEST-SKIP {location} added focus"]
    if is_test_file(path) and SKIP.search(text):
        return [f"TEST-SKIP {location} added skip"]
    if EMPTY_CATCH.search(text):
        return [f"CATCH-EMPTY {location} added empty catch block"]
    return []


def findings_for(records):
    findings = []
    for record in records:
        findings += structure_findings(record)
        path = record["new"] or record["old"]
        for line_number, text in record["added"]:
            findings += line_findings(path, line_number, text)
    return sorted(findings, key=sort_key)


def sort_key(finding):
    rule, location = finding.split(" ", 2)[:2]
    path, _, line = location.rpartition(":")
    return path, int(line), rule, finding


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", help="Base revision")
    parser.add_argument("head", help="Head revision")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")
    args = parser.parse_args(argv)
    try:
        findings = findings_for(parse_diff(git_diff(args.repo, args.base, args.head)))
    except subprocess.CalledProcessError as error:
        print(f"check_rules: git failed: {error.stderr.strip()}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"check_rules: {error}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
