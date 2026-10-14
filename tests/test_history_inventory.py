import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/craft/scripts/history_inventory.py"
SPEC = importlib.util.spec_from_file_location("history_inventory", SCRIPT)
history = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(history)
AUTHOR = re.compile(r"^Target Person <target@example\.com>$")


class HistoryInventoryTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Target Person")
        self.git("config", "user.email", "target@example.com")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *arguments, repo=None, env=None):
        return subprocess.check_output(
            ["git", "-C", str(repo or self.repo), *arguments],
            text=True, stderr=subprocess.PIPE, env={**os.environ, **(env or {})},
        ).strip()

    def commit(self, filename, text, subject="change", author=None, env=None):
        (self.repo / filename).write_text(text)
        self.git("add", filename)
        arguments = ["commit", "-m", subject]
        if author:
            arguments += ["--author", author]
        self.git(*arguments, env=env)
        return self.git("rev-parse", "HEAD")

    def scan(self, **options):
        return history.inventory([self.root], [AUTHOR], **options)

    def test_exact_identity_and_duplicate_refs_clones(self):
        wanted = self.commit("one", "one")
        other = self.commit("two", "two", author="Target Colleague <colleague@example.com>")
        self.git("branch", "duplicate-ref", wanted)
        clone = self.root / "clone"
        subprocess.check_call(["git", "clone", "--quiet", str(self.repo), str(clone)])
        result = self.scan(manifest=True)
        self.assertEqual([], result["errors"])
        self.assertEqual(2, result["summary"]["common_git_directories"])
        self.assertEqual(1, result["summary"]["authored_hashes"])
        hashes = {commit["hash"] for report in result["repositories"] for commit in report["commits"]}
        self.assertEqual({wanted}, hashes)
        self.assertNotIn(other, hashes)
        self.assertNotIn('"subject"', json.dumps(result))

    def test_empty_working_and_bare_repositories_have_complete_zero_counts(self):
        bare = self.root / "empty.git"
        subprocess.check_call(["git", "init", "--quiet", "--bare", str(bare)])
        result = self.scan(patch_ids=True, manifest=True)
        self.assertEqual([], result["errors"])
        self.assertEqual(2, result["summary"]["inventoried_repositories"])
        self.assertEqual(0, result["summary"]["authored_hashes"])
        self.assertEqual(0, result["summary"]["unique_nonempty_stable_patch_ids"])
        for report in result["repositories"]:
            self.assertEqual([], report["heads"])
            self.assertEqual([], report["refs"])
            self.assertEqual([], report["commits"])
            self.assertIsNone(report["authored_date_from"])
            self.assertIsNone(report["authored_date_to"])
        output = subprocess.check_output([
            "python3", str(SCRIPT), "--root", str(self.root), "--author", AUTHOR.pattern,
        ], text=True)
        self.assertEqual([], json.loads(output)["errors"])

    def test_bare_clone_discovery_counts_shared_hashes_once(self):
        self.commit("base", "base")
        bare = self.root / "populated.git"
        subprocess.check_call(["git", "clone", "--quiet", "--bare", str(self.repo), str(bare)])
        result = self.scan(manifest=True)
        self.assertEqual([], result["errors"])
        self.assertEqual(2, result["summary"]["inventoried_repositories"])
        self.assertEqual(1, result["summary"]["authored_hashes"])
        self.assertTrue(all(report["ref_count"] == 1 for report in result["repositories"]))

    def test_merge_and_stash_are_transparent_not_analysis_candidates(self):
        self.commit("base", "base")
        self.git("checkout", "-b", "feature")
        self.commit("feature", "feature")
        self.git("checkout", "main")
        self.commit("main", "main")
        self.git("merge", "--no-ff", "feature", "-m", "merge feature")
        (self.repo / "base").write_text("stash contents")
        self.git("stash", "push", "-m", "custom stash")
        result = self.scan(manifest=True)
        summary = result["summary"]
        self.assertEqual(6, summary["authored_hashes"])
        self.assertEqual(2, summary["merge_hashes"])
        self.assertEqual(2, summary["stash_like_hashes"])
        self.assertEqual(3, summary["nonmerge_nonstash_hashes"])

    def test_common_dir_dedup_preserves_detached_worktree_head(self):
        self.commit("base", "base")
        worktree = self.root / "worktree"
        self.git("worktree", "add", "--detach", str(worktree), "HEAD")
        (worktree / "detached").write_text("detached")
        self.git("add", "detached", repo=worktree)
        self.git("commit", "-m", "detached work", repo=worktree)
        result = self.scan(manifest=True)
        self.assertEqual(2, result["summary"]["repository_directories"])
        self.assertEqual(1, result["summary"]["common_git_directories"])
        self.assertEqual(2, result["summary"]["authored_hashes"])
        self.assertEqual(2, len(result["repositories"][0]["heads"]))

    def test_patch_ids_distinguish_hashes_from_replayed_changes(self):
        base = self.commit("base", "base")
        original = self.commit("change", "change")
        self.git("checkout", "-b", "replay", base)
        self.git("cherry-pick", original, env={"GIT_COMMITTER_DATE": "2030-01-01T00:00:00Z"})
        result = self.scan(patch_ids=True)
        self.assertEqual(3, result["summary"]["authored_hashes"])
        self.assertEqual(2, result["summary"]["unique_nonempty_stable_patch_ids"])

    def test_color_config_cannot_corrupt_patch_ids(self):
        self.commit("base", "base")
        self.commit("change", "change")
        plain = self.scan(patch_ids=True, manifest=True)
        self.git("config", "color.ui", "always")
        self.git("config", "color.diff", "always")
        colored = self.scan(patch_ids=True, manifest=True)
        self.assertEqual([], colored["errors"])
        self.assertEqual(0, colored["summary"]["empty_patch_hashes"])
        self.assertEqual(2, colored["summary"]["unique_nonempty_stable_patch_ids"])
        self.assertEqual(plain["repositories"][0]["commits"], colored["repositories"][0]["commits"])

    def test_log_show_root_config_cannot_hide_a_real_root_patch(self):
        self.commit("base", "base")
        self.git("config", "log.showRoot", "false")
        result = self.scan(patch_ids=True)
        self.assertEqual([], result["errors"])
        self.assertEqual(1, result["summary"]["unique_nonempty_stable_patch_ids"])
        self.assertEqual(0, result["summary"]["empty_patch_hashes"])

    def test_ambient_git_directory_cannot_replace_the_requested_repository(self):
        wanted = self.commit("base", "base")
        other = self.root / "unrequested"
        other.mkdir()
        self.git("init", "-b", "main", repo=other)
        self.git("config", "user.name", "Target Person", repo=other)
        self.git("config", "user.email", "target@example.com", repo=other)
        self.git("config", "commit.gpgsign", "false", repo=other)
        self.git("commit", "--allow-empty", "-m", "unrequested commit", repo=other)
        with patch.dict(os.environ, {"GIT_DIR": str(other / ".git"), "GIT_WORK_TREE": str(other)}):
            result = history.inventory([self.repo], [AUTHOR], manifest=True)
        self.assertEqual([], result["errors"])
        self.assertEqual({wanted}, {commit["hash"] for commit in result["repositories"][0]["commits"]})

    def test_utc_git_commit_date_works_with_python_39(self):
        self.commit("utc", "utc", env={
            "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
        })
        result = self.scan()
        self.assertEqual([], result["errors"])
        self.assertEqual("2026-01-01T00:00:00+00:00",
                         result["summary"]["authored_date_from"].replace("Z", "+00:00"))

    def test_cli_depth_and_missing_root_report_incomplete_scope(self):
        self.commit("base", "base")
        output = subprocess.check_output([
            "python3", str(SCRIPT), "--root", str(self.root), "--author", AUTHOR.pattern,
            "--max-depth", "0",
        ], text=True)
        self.assertEqual(0, json.loads(output)["summary"]["authored_hashes"])
        result = history.inventory([self.root / "missing"], [AUTHOR])
        self.assertEqual(1, len(result["errors"]))

    def test_shallow_repository_reports_missing_ancestry(self):
        self.commit("base", "base")
        latest = self.commit("latest", "latest")
        (self.repo / ".git/shallow").write_text(latest + "\n")
        result = self.scan()
        self.assertEqual(1, result["summary"]["shallow_repositories"])
        self.assertEqual(1, result["summary"]["authored_hashes"])

    def test_date_coverage_compares_instants_across_offsets(self):
        values = [
            {"date": "2026-01-01T01:00:00+02:00", "merge": False, "stash_like": False},
            {"date": "2025-12-31T23:30:00+00:00", "merge": False, "stash_like": False},
            {"date": "2025-12-31T23:15:00Z", "merge": False, "stash_like": False},
        ]
        result = history.counts(values)
        self.assertEqual("2026-01-01T01:00:00+02:00", result["authored_date_from"])
        self.assertEqual("2025-12-31T23:30:00+00:00", result["authored_date_to"])


if __name__ == "__main__":
    unittest.main()
