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
AUTOLOAD = version_check.AUTOLOAD
NETWORK_SWITCHES = ("DISABLE_UPDATES", "DISABLE_AUTOUPDATER", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
                    "CRAFT_UPDATE_CHECK", "CRAFT_AUTOLOAD")
STARTUP = '{"source": "startup"}'


class CheckSkillVersionTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.cache = self.scratch / "cache.json"

    def env(self, **overrides):
        """Every switch blank (unset) unless overridden; the release cache stays in the scratch directory."""
        environ = {name: "" for name in NETWORK_SWITCHES}
        environ["CLAUDE_PLUGIN_DATA"] = str(self.scratch)
        environ.update(overrides)
        return environ

    def run_hook(self, environ, stdin_text=STARTUP):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = version_check.main(["--hook"], environ=environ, stdin=io.StringIO(stdin_text))
        return code, out.getvalue()

    def test_newer_release_produces_reminder_with_update_and_auto_update_steps(self):
        message = version_check.reminder("1.3.0", RELEASE)
        self.assertEqual(
            "craft 9.0.0 is available (you have 1.3.0). Update: claude plugin update craft@Arkon, "
            "then /reload-plugins. To get updates automatically: /plugin → Marketplaces → Arkon → "
            "enable auto-update.",
            message)

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
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="1.3.0"):
            code, out = self.run_hook(self.env())
        self.assertEqual(code, 0)
        self.assertIn("9.0.0", json.loads(out)["systemMessage"])

    def test_network_failure_never_blocks(self):
        err = io.StringIO()
        with patch.object(version_check, "latest_release", side_effect=OSError("offline")), \
                contextlib.redirect_stderr(err):
            code, out = self.run_hook(self.env())
        self.assertEqual(code, 0)
        self.assertIn("skipped: OSError", err.getvalue())
        self.assertEqual(AUTOLOAD, json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_installed_version_reads_plugin_manifest(self):
        self.assertIsNotNone(version_check.parse_version(version_check.installed_version()))

    def test_autoload_is_on_by_default(self):
        with patch.object(version_check, "fetch_release") as fetch:
            code, out = self.run_hook(self.env(CRAFT_UPDATE_CHECK="0"))
        self.assertEqual(code, 0)
        self.assertEqual({"hookEventName": "SessionStart", "additionalContext": AUTOLOAD},
                         json.loads(out)["hookSpecificOutput"])
        fetch.assert_not_called()

    def test_autoload_is_absent_when_disabled_and_nothing_is_printed_without_update(self):
        for value in ("0", "false", "FALSE"):
            with self.subTest(CRAFT_AUTOLOAD=value):
                code, out = self.run_hook(self.env(CRAFT_AUTOLOAD=value, CRAFT_UPDATE_CHECK="0"))
                self.assertEqual(code, 0)
                self.assertEqual("", out)

    def test_autoload_off_still_reports_an_update_without_autoload_context(self):
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="1.3.0"):
            _, out = self.run_hook(self.env(CRAFT_AUTOLOAD="0"))
        payload = json.loads(out)
        self.assertEqual({"systemMessage"}, set(payload))
        self.assertIn("craft 9.0.0 is available", payload["systemMessage"])

    def test_hook_output_is_one_json_object_with_both_keys_when_update_exists(self):
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="1.3.0"):
            code, out = self.run_hook(self.env())
        self.assertEqual(code, 0)
        self.assertEqual(1, len(out.splitlines()))
        payload = json.loads(out)
        self.assertEqual({"hookSpecificOutput", "systemMessage"}, set(payload))
        self.assertEqual(AUTOLOAD, payload["hookSpecificOutput"]["additionalContext"])

    def test_system_message_only_when_a_newer_release_exists(self):
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="9.0.0"):
            _, out = self.run_hook(self.env())
        self.assertEqual({"hookSpecificOutput"}, set(json.loads(out)))

    def test_no_network_check_when_a_disable_switch_is_set(self):
        switches = [{"DISABLE_UPDATES": "1"}, {"DISABLE_AUTOUPDATER": "1"},
                    {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}, {"CRAFT_UPDATE_CHECK": "0"}]
        for switch in switches:
            with self.subTest(switch=switch), patch.object(version_check, "fetch_release") as fetch:
                code, out = self.run_hook(self.env(**switch))
                self.assertEqual(code, 0)
                self.assertEqual({"hookSpecificOutput"}, set(json.loads(out)))
                fetch.assert_not_called()

    def test_network_check_runs_on_startup_when_no_switch_is_set(self):
        with patch.object(version_check, "fetch_release", return_value=RELEASE) as fetch:
            _, out = self.run_hook(self.env())
        fetch.assert_called_once()
        self.assertIn("systemMessage", json.loads(out))

    def test_network_check_runs_only_on_startup_or_unreadable_stdin(self):
        cache_file = self.scratch / "craft-latest-release.json"
        with patch.object(version_check, "fetch_release", return_value=RELEASE) as fetch:
            for stdin_text in ('{"source": "resume"}', '{"source": "clear"}', '{"source": "compact"}', "{}"):
                with self.subTest(stdin=stdin_text):
                    cache_file.unlink(missing_ok=True)
                    fetch.reset_mock()
                    self.run_hook(self.env(), stdin_text=stdin_text)
                    fetch.assert_not_called()
            for stdin_text in (STARTUP, "not json", ""):
                with self.subTest(stdin=stdin_text):
                    cache_file.unlink(missing_ok=True)
                    fetch.reset_mock()
                    self.run_hook(self.env(), stdin_text=stdin_text)
                    fetch.assert_called_once()

    def test_check_mode_prints_the_notice_to_stderr_only(self):
        err, out = io.StringIO(), io.StringIO()
        with patch.object(version_check, "latest_release", return_value=RELEASE), \
                patch.object(version_check, "installed_version", return_value="1.3.0"), \
                contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            self.assertEqual(0, version_check.main(["--check"], environ=self.env(), stdin=io.StringIO("")))
        self.assertIn("craft 9.0.0 is available (you have 1.3.0)", err.getvalue())
        self.assertEqual("", out.getvalue())


if __name__ == "__main__":
    unittest.main()
