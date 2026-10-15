import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_skill_version.py"
SPEC = importlib.util.spec_from_file_location("check_skill_version", SCRIPT)
version_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(version_check)
RELEASE = {"tag_name": "v9.0.0", "html_url": "https://github.com/abhimanyusingh-gh/Arkon/releases/tag/v9.0.0"}


class CheckSkillVersionTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.cache = Path(scratch.name) / "cache.json"

    def test_newer_release_produces_reminder_with_install_and_changelog(self):
        message = version_check.reminder("1.3.0", RELEASE)
        self.assertIn("1.3.0 -> 9.0.0", message)
        self.assertIn("/plugin install craft@Arkon", message)
        self.assertIn(RELEASE["html_url"], message)

    def test_same_older_or_malformed_release_produces_no_reminder(self):
        self.assertIsNone(version_check.reminder("9.0.0", RELEASE))
        self.assertIsNone(version_check.reminder("10.0.0", RELEASE))
        self.assertIsNone(version_check.reminder("1.3.0", {"tag_name": "nightly"}))
        self.assertIsNone(version_check.reminder("1.3.0", {}))

    def test_versions_compare_numerically_not_lexically(self):
        self.assertIsNotNone(version_check.reminder("1.9.0", {"tag_name": "v1.10.0"}))

    def test_release_is_cached_for_a_day(self):
        calls = []
        fetch = lambda timeout: calls.append(timeout) or RELEASE
        version_check.latest_release(1, cache=self.cache, now=1000, fetch=fetch)
        version_check.latest_release(1, cache=self.cache, now=1000 + 3600, fetch=fetch)
        self.assertEqual(len(calls), 1)
        version_check.latest_release(1, cache=self.cache, now=1000 + 2 * 86400, fetch=fetch)
        self.assertEqual(len(calls), 2)

    def test_corrupt_cache_is_refetched(self):
        self.cache.write_text("not json")
        release = version_check.latest_release(1, cache=self.cache, now=0, fetch=lambda t: RELEASE)
        self.assertEqual(release, RELEASE)

    def test_hook_mode_emits_system_message_json(self):
        out = io.StringIO()
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="1.3.0"), \
                contextlib.redirect_stdout(out):
            self.assertEqual(version_check.main(["--hook"]), 0)
        self.assertIn("9.0.0", json.loads(out.getvalue())["systemMessage"])

    def test_network_failure_never_blocks(self):
        err = io.StringIO()
        with patch.object(version_check, "latest_release", side_effect=OSError("offline")), \
                contextlib.redirect_stderr(err):
            self.assertEqual(version_check.main(["--hook"]), 0)
        self.assertIn("skipped: OSError", err.getvalue())

    def test_installed_version_reads_plugin_manifest(self):
        self.assertIsNotNone(version_check.parse_version(version_check.installed_version()))


if __name__ == "__main__":
    unittest.main()
