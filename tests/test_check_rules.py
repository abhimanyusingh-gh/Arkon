import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/craft/scripts/check_rules.py"
SPEC = importlib.util.spec_from_file_location("check_rules", SCRIPT)
check_rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_rules)


class CheckRulesTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.repo = Path(self.scratch.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test Author")
        self.git("config", "user.email", "author@example.com")
        self.git("config", "commit.gpgsign", "false")
        self.write("README.md", "base\n")
        self.commit("initial")

    def git(self, *arguments):
        return subprocess.check_output(["git", "-C", str(self.repo), *arguments], text=True).strip()

    def write(self, path, text):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, subject):
        self.git("add", "-A")
        self.git("commit", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def scan(self, base, head="HEAD"):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = check_rules.main(["--repo", str(self.repo), base, head])
        return code, output.getvalue().splitlines()

    def test_deleted_test_file_is_reported_and_deleted_source_is_not(self):
        self.write("tests/test_parser.py", "def test_parse():\n    assert parse('a') == 1\n")
        self.write("src/old_helper.py", "VALUE = 1\n")
        base = self.commit("base")
        (self.repo / "tests/test_parser.py").unlink()
        (self.repo / "src/old_helper.py").unlink()
        code, lines = self.scan(base, self.commit("delete"))
        self.assertIn("TEST-NODELETE tests/test_parser.py:0 test file deleted", lines)
        self.assertFalse(any("old_helper" in line for line in lines))
        self.assertEqual(1, code)

    def test_renamed_test_file_is_reported_and_renamed_source_is_not(self):
        self.write("spec/login.spec.ts", "it('logs in', () => expect(true).toBe(true));\n")
        self.write("src/login.ts", "export const login = 1;\n")
        base = self.commit("base")
        self.git("mv", "spec/login.spec.ts", "spec/signin.spec.ts")
        self.git("mv", "src/login.ts", "src/signin.ts")
        code, lines = self.scan(base, self.commit("rename"))
        self.assertEqual(["TEST-NODELETE spec/login.spec.ts:0 test file renamed to spec/signin.spec.ts"], lines)
        self.assertEqual(1, code)

    def test_net_removed_assertions_are_reported_and_moved_assertions_are_not(self):
        self.write("tests/test_math.py", "def test_add():\n    assert add(1, 2) == 3\n    assert add(0, 0) == 0\n")
        self.write("tests/test_moved.py", "def test_moved():\n    assert True\n    value = 1\n")
        base = self.commit("base")
        self.write("tests/test_math.py", "def test_add():\n    pass\n")
        self.write("tests/test_moved.py", "def test_moved():\n    value = 1\n    assert True\n")
        code, lines = self.scan(base, self.commit("weaken"))
        self.assertEqual(["TEST-NODELETE tests/test_math.py:0 net assertions removed (2 removed, 0 added)"], lines)
        self.assertEqual(1, code)

    def test_added_skip_and_focus_markers_are_reported(self):
        self.write("src/FooTest.java", "class FooTest {\n    @Test void a() {}\n}\n")
        self.write("web/app.spec.ts", "describe('app', () => {});\n")
        base = self.commit("base")
        self.write("src/FooTest.java", "class FooTest {\n    @Disabled\n    @Test void a() {}\n}\n")  # check-rules: ignore
        self.write("web/app.spec.ts", "it.skip('a', () => {});\nit.only('b', () => {});\nit('c', () => {});\n")  # check-rules: ignore
        code, lines = self.scan(base, self.commit("skip"))
        self.assertIn("TEST-SKIP src/FooTest.java:2 added skip", lines)
        self.assertIn("TEST-SKIP web/app.spec.ts:1 added skip", lines)
        self.assertIn("TEST-SKIP web/app.spec.ts:2 added focus", lines)
        self.assertFalse(any("web/app.spec.ts:3 " in line for line in lines))
        self.assertEqual(1, code)

    def test_skip_outside_tests_and_ignore_marker_are_not_reported(self):
        self.write("src/Rules.java", "class Rules {}\n")
        base = self.commit("base")
        self.write("src/Rules.java", "class Rules {\n    String p = \"@Disabled\";\n}\n")  # check-rules: ignore
        self.write("tests/test_fixture.py", "FIXTURE = 'it.skip('  # check-rules: ignore\n")
        code, lines = self.scan(base, self.commit("literals"))
        self.assertEqual([], lines)
        self.assertEqual(0, code)

    def test_findings_sort_by_numeric_line(self):
        self.write("tests/test_a.py", "x = 1\n")
        base = self.commit("base")
        self.write("tests/test_a.py", "\n".join(["@unittest.skip('a')"] + ["x = 1"] * 9 + ["@unittest.skip('b')"]) + "\n")  # check-rules: ignore
        _, lines = self.scan(base, self.commit("two skips"))
        self.assertEqual(["TEST-SKIP tests/test_a.py:1 added skip", "TEST-SKIP tests/test_a.py:11 added skip"], lines)

    def test_added_empty_catch_blocks_are_reported_and_handled_catches_are_not(self):
        self.write("src/Reader.java", "class Reader {\n    void read() {\n        load();\n    }\n}\n")
        self.write("src/reader.py", "def read():\n    load()\n")
        base = self.commit("base")
        self.write("src/Reader.java",
                   "class Reader {\n    void read() {\n        try { load(); } catch (IOException e) {}\n    }\n}\n")  # check-rules: ignore
        self.write("src/reader.py", "def read():\n    try:\n        load()\n    except OSError: pass\n")
        self.write("src/Safe.java", "class Safe {\n    void read() {\n        try { load(); } catch (IOException e) "
                                    "{ throw new IllegalStateException(\"load failed\", e); }\n    }\n}\n")
        code, lines = self.scan(base, self.commit("swallow"))
        self.assertIn("CATCH-EMPTY src/Reader.java:3 added empty catch block", lines)
        self.assertIn("CATCH-EMPTY src/reader.py:4 added empty catch block", lines)
        self.assertFalse(any("src/Safe.java" in line for line in lines))
        self.assertEqual(1, code)

    def test_clean_diff_exits_zero_without_output(self):
        self.write("src/service.py", "def run():\n    return 1\n")
        base = self.commit("base")
        self.write("src/service.py", "def run():\n    return 2\n")
        self.assertEqual((0, []), self.scan(base, self.commit("change")))

    def test_unknown_revision_exits_two_with_no_findings(self):
        self.assertEqual((2, []), self.scan("no-such-revision", "HEAD"))


if __name__ == "__main__":
    unittest.main()
