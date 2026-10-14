#!/usr/bin/env python3
"""Inventory an explicitly scoped author's reachable local Git history as JSON."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys


STASH_LIKE = re.compile(r"^(?:WIP on |index on |untracked files on |On [^:]+: )")
REPOSITORY_ENV = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_PREFIX", "GIT_INTERNAL_SUPER_PREFIX", "GIT_IMPLICIT_WORK_TREE",
    "GIT_GRAFT_FILE", "GIT_REPLACE_REF_BASE", "GIT_SHALLOW_FILE",
}


def git(path, *arguments, input_text=None, optional=False):
    result = subprocess.run(
        ["git", "-c", "color.ui=false", "-C", str(path), *arguments], input=input_text,
        text=True, encoding="utf-8", errors="surrogateescape",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**{key: value for key, value in os.environ.items() if key not in REPOSITORY_ENV},
             "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode and not optional:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip() if optional else result.stdout


def discover(roots, max_depth, errors):
    found = set()
    for root in roots:
        root = root.resolve()
        if not root.is_dir():
            errors.append({"path": str(root), "error": "Root is not a directory"})
            continue
        for directory, children, _ in os.walk(root, onerror=lambda e: errors.append(
            {"path": str(e.filename), "error": str(e)}
        )):
            path = Path(directory)
            depth = len(path.relative_to(root).parts)
            bare = (path / "HEAD").is_file() and (path / "objects").is_dir()
            if (path / ".git").exists() or bare:
                found.add(path.resolve())
                children[:] = []
            elif max_depth is not None and depth >= max_depth:
                children[:] = []
            else:
                children[:] = [child for child in children if child != ".git"]
    return sorted(found)


def metadata(path):
    common = Path(git(path, "rev-parse", "--git-common-dir").strip())
    if not common.is_absolute():
        common = path / common
    return {
        "path": str(path), "common_git_dir": str(common.resolve()),
        "head": git(path, "rev-parse", "--verify", "--quiet", "HEAD", optional=True) or None,
        "refs": [line.split(" ", 1) for line in git(
            path, "for-each-ref", "--format=%(refname) %(objectname)"
        ).splitlines()],
        "shallow": git(path, "rev-parse", "--is-shallow-repository").strip() == "true",
    }


def commits(path, revisions, authors):
    raw = git(path, "log", "--no-color", "--no-show-signature", "--all", "--stdin", "-z",
              "--format=%H%x00%P%x00%aI%x00%an%x00%ae%x00%s",
              input_text="".join(revision + "\n" for revision in sorted(revisions)))
    fields = raw.split("\0")
    if fields[-1] == "":
        fields.pop()
    if len(fields) % 6:
        raise RuntimeError("Unexpected Git log record format")
    result = {}
    for offset in range(0, len(fields), 6):
        commit, parents, date, name, email, subject = fields[offset:offset + 6]
        if any(author.search(f"{name} <{email}>") for author in authors):
            result[commit] = {
                "hash": commit, "date": date, "merge": len(parents.split()) > 1,
                "stash_like": bool(STASH_LIKE.match(subject)),
            }
    return result


def counts(values, include_patches=False):
    values = list(values)
    dates = [value["date"] for value in values]
    candidates = [value for value in values if not value["merge"] and not value["stash_like"]]
    result = {
        "authored_hashes": len(values),
        "merge_hashes": sum(value["merge"] for value in values),
        "nonmerge_hashes": sum(not value["merge"] for value in values),
        "stash_like_hashes": sum(value["stash_like"] for value in values),
        "nonmerge_nonstash_hashes": len(candidates),
        "authored_date_from": min(dates, key=parse_date) if dates else None,
        "authored_date_to": max(dates, key=parse_date) if dates else None,
    }
    if include_patches:
        result["unique_nonempty_stable_patch_ids"] = len({
            value["patch_id"] for value in candidates if value.get("patch_id")
        })
        result["empty_patch_hashes"] = sum(not value.get("patch_id") for value in candidates)
    return result


def parse_date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def inventory(roots, authors, max_depth=None, patch_ids=False, manifest=False):
    errors, groups, all_commits, reports = [], {}, {}, []
    paths = discover(roots, max_depth, errors)
    for path in paths:
        try:
            info = metadata(path)
            groups.setdefault(info["common_git_dir"], []).append(info)
        except (OSError, RuntimeError) as error:
            errors.append({"path": str(path), "error": str(error)})
    for common, copies in sorted(groups.items()):
        path = Path(copies[0]["path"])
        refs = {tuple(ref) for copy in copies for ref in copy["refs"]}
        heads = {copy["head"] for copy in copies if copy["head"]}
        try:
            found = commits(path, {ref[1] for ref in refs} | heads, authors)
            if patch_ids:
                for commit in found.values():
                    if commit["merge"] or commit["stash_like"]:
                        continue
                    if commit["hash"] in all_commits:
                        commit["patch_id"] = all_commits[commit["hash"]].get("patch_id")
                    else:
                        patch = git(
                            path, "show", "--root", "--patch", "--no-color", "--no-show-signature",
                            "--no-ext-diff", "--no-textconv", "--format=", "--binary", commit["hash"],
                        )
                        stable = git(path, "patch-id", "--stable", input_text=patch).split()
                        commit["patch_id"] = stable[0] if stable else None
            all_commits.update(found)
            report = {
                "paths": [copy["path"] for copy in copies], "common_git_dir": common,
                "heads": sorted(heads), "ref_count": len(refs),
                "shallow": any(copy["shallow"] for copy in copies),
                **counts(found.values(), patch_ids),
            }
            if manifest:
                report["refs"] = sorted(refs)
                report["commits"] = sorted(found.values(), key=lambda value: value["hash"])
            reports.append(report)
        except (OSError, RuntimeError) as error:
            errors.append({"path": str(path), "error": str(error)})
    return {
        "scope": {"roots": [str(root.resolve()) for root in roots],
                  "author_patterns": [author.pattern for author in authors], "max_depth": max_depth},
        "limits": ["Reachable local refs and scanned checkout HEADs; no fetch or reflog.",
                   "Discovery stops at a repository; supply nested repositories as additional roots.",
                   "Author filtering is regex search against Name <email>, without mailmap rewriting.",
                   "Stash-like subjects are heuristic and overlap the merge count.",
                   "Commit and patch counts are not defect or independent incident counts."],
        "summary": {"repository_directories": len(paths), "common_git_directories": len(groups),
                    "inventoried_repositories": len(reports),
                    "shallow_repositories": sum(report["shallow"] for report in reports),
                    **counts(all_commits.values(), patch_ids)},
        "repositories": reports, "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", required=True,
                        help="Checkout or directory of checkouts; repeat for multiple roots")
    parser.add_argument("--author", action="append", required=True,
                        help="Regex searched against 'Name <email>'; repeat for alternate identities")
    parser.add_argument("--max-depth", type=int, help="Discovery depth below each root (root is depth zero)")
    parser.add_argument("--patch-ids", action="store_true", help="Compute stable patch IDs for nonmerge, nonstash commits")
    parser.add_argument("--manifest", action="store_true", help="Include raw hashes, refs and classification, without commit messages")
    args = parser.parse_args()
    if args.max_depth is not None and args.max_depth < 0:
        parser.error("--max-depth must be nonnegative")
    try:
        authors = [re.compile(pattern) for pattern in args.author]
    except re.error as error:
        parser.error(str(error))
    result = inventory(args.root, authors, args.max_depth, args.patch_ids, args.manifest)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
