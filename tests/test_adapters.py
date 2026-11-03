from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "adapters"
REQUIRED = [
    "README.md",
    "AGENTS.md",
    "cursor/craft.mdc",
    "copilot/copilot-instructions.md",
    "claude/CLAUDE.md",
]
BANNER_FILES = ["AGENTS.md", "cursor/craft.mdc", "copilot/copilot-instructions.md"]
CLAUDE = "claude/CLAUDE.md"
ATTRIBUTION = re.compile(r"co-authored-by|generated with", re.IGNORECASE)
PROHIBITION = re.compile(r"\b(no|never|do not)\b", re.IGNORECASE)
ABSOLUTE_PREFIXES = ("/Users/", "/home/")
README_CLAIMS = [
    "compatible with github copilot",
    "compatible with cursor",
    "works with cursor",
    "works with github copilot",
]


def read(rel):
    return (ADAPTERS / rel).read_text(encoding="utf-8")


def adapter_files():
    return sorted(path for path in ADAPTERS.rglob("*") if path.is_file())


class AdapterTest(unittest.TestCase):
    def test_required_adapter_files_exist(self):
        for rel in REQUIRED:
            with self.subTest(rel=rel):
                self.assertTrue((ADAPTERS / rel).is_file(), f"missing adapters/{rel}")

    def test_experimental_banner_is_in_first_lines(self):
        for rel in BANNER_FILES:
            with self.subTest(rel=rel):
                head = "\n".join(read(rel).splitlines()[:12]).lower()
                self.assertIn("experimental", head)
                self.assertIn("untested on this platform", head)

    def test_claude_adapter_is_marked_tested(self):
        text = read(CLAUDE)
        head = "\n".join(text.splitlines()[:8])
        self.assertIn("tested", head)
        self.assertIn("Claude Code", head)
        self.assertNotIn("untested on this platform", text.lower())

    def test_attribution_text_appears_only_as_a_prohibition(self):
        failures = []
        for path in adapter_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if ATTRIBUTION.search(line) and not PROHIBITION.search(line):
                    failures.append(f"{path.relative_to(ROOT)}:{number}")
        self.assertEqual(failures, [], "attribution text outside a prohibition")

    def test_adapters_contain_no_absolute_user_paths(self):
        failures = []
        for path in adapter_files():
            text = path.read_text(encoding="utf-8")
            for prefix in ABSOLUTE_PREFIXES:
                if prefix in text:
                    failures.append(f"{path.relative_to(ROOT)} contains {prefix}")
        self.assertEqual(failures, [])

    def test_adapter_files_are_at_most_120_lines(self):
        failures = []
        for path in adapter_files():
            count = len(path.read_text(encoding="utf-8").splitlines())
            if count > 120:
                failures.append(f"{path.relative_to(ROOT)} has {count} lines")
        self.assertEqual(failures, [])

    def test_root_readme_claims_no_untested_compatibility(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
        for phrase in README_CLAIMS:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
