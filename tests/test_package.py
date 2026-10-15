import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = (ROOT / "pyproject.toml").read_text()


def setting(name):
    match = re.search(rf'^{re.escape(name)}\s*=\s*(.+)$', PYPROJECT, re.M)
    return match.group(1).strip() if match else None


class PackageTest(unittest.TestCase):
    def test_entry_point_resolves_to_the_skill_script(self):
        module, function = setting("arkon-discover").strip('"').split(":")
        package_dir = re.search(r'package-dir = \{"" = "([^"]+)"\}', PYPROJECT).group(1)
        script = ROOT / package_dir / f"{module}.py"
        self.assertTrue(script.is_file(), script)
        spec = importlib.util.spec_from_file_location(module, script)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as exit_:
            getattr(loaded, function)(["--help"])
        self.assertEqual(0, exit_.exception.code)
        self.assertIn("--check", out.getvalue())

    def test_package_version_matches_plugin(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(f'"{plugin["version"]}"', setting("version"))

    def test_package_has_no_runtime_dependencies(self):
        self.assertEqual("[]", setting("dependencies"))
        self.assertTrue((ROOT / setting("readme").strip('"')).is_file())

    @unittest.skipUnless(os.environ.get("ARKON_PACKAGE_INSTALL_TEST") == "1",
                         "set ARKON_PACKAGE_INSTALL_TEST=1 to build and install into a fresh venv (needs network)")
    def test_installs_into_a_fresh_venv_and_runs(self):
        with tempfile.TemporaryDirectory() as scratch:
            venv = Path(scratch) / "venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
            pip = [str(venv / "bin/python"), "-m", "pip", "-q"]
            subprocess.run(pip + ["install", "--upgrade", "pip"], check=True)
            subprocess.run(pip + ["install", str(ROOT)], check=True)
            command = venv / "bin/arkon-discover"
            help_text = subprocess.run([str(command), "--help"], check=True,
                                       capture_output=True, text=True).stdout
            self.assertIn("--check", help_text)
            out = Path(scratch) / "ctx.json"
            subprocess.run([str(command), str(ROOT), "--out", str(out)], check=True)
            self.assertEqual(1, json.loads(out.read_text())["schema_version"])


if __name__ == "__main__":
    unittest.main()
