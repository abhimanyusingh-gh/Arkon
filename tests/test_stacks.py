import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_skill.py"
SPEC = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
validate_skill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_skill)

PROFILE = "# Stack\n\n## Match signals\n\n- `pom.xml`\n"
INDEX = "# Stacks\n\n- [Stack](stack.md) matches `pom.xml`\n"
ROUTE = "`references/stacks/README.md`"


def make_tree(files):
    scratch = tempfile.TemporaryDirectory()
    references = Path(scratch.name)
    for name, text in files.items():
        path = references / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return scratch, references


class StacksTest(unittest.TestCase):
    def test_routed_subdirectory_with_linked_profile_passes(self):
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/stack.md": PROFILE})
        self.addCleanup(scratch.cleanup)
        self.assertEqual(validate_skill.routing_errors(ROUTE, references), [])
        self.assertEqual(validate_skill.stack_profile_errors(references), [])

    def test_unlinked_profile_fails(self):
        scratch, references = make_tree({"stacks/README.md": "# Stacks\n", "stacks/stack.md": PROFILE})
        self.addCleanup(scratch.cleanup)
        errors = validate_skill.routing_errors(ROUTE, references)
        self.assertEqual(len(errors), 1)
        self.assertIn("unlinked reference stack.md", errors[0])

    def test_profile_without_match_signals_fails(self):
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/stack.md": "# Stack\n"})
        self.addCleanup(scratch.cleanup)
        errors = validate_skill.stack_profile_errors(references)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing ## Match signals section", errors[0])

    def test_profile_over_seventy_lines_fails(self):
        long_profile = PROFILE + "- signal\n" * 70
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/stack.md": long_profile})
        self.addCleanup(scratch.cleanup)
        errors = validate_skill.stack_profile_errors(references)
        self.assertEqual(len(errors), 1)
        self.assertIn("exceeds the 70-line cap", errors[0])

    def test_profile_with_empty_match_signals_fails(self):
        empty = "# Stack\n\n## Match signals\n\n## Rules\n\n- `x`\n"
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/stack.md": empty})
        self.addCleanup(scratch.cleanup)
        errors = validate_skill.stack_profile_errors(references)
        self.assertEqual(len(errors), 1)
        self.assertIn("empty ## Match signals section", errors[0])

    def test_anchor_link_counts_as_linked(self):
        self.assertTrue(validate_skill.is_linked("x.md", "[X](x.md#y)"))
        self.assertTrue(validate_skill.is_linked("x.md", "[X](stacks/x.md#y)"))
        self.assertTrue(validate_skill.is_linked("x.md", "[X](x.md)"))
        self.assertTrue(validate_skill.is_linked("x.md", "`x.md`"))
        self.assertFalse(validate_skill.is_linked("x.md", "[X](other.md#x.md)"))

    def test_profile_at_seventy_lines_passes_and_seventy_one_fails(self):
        at_cap = PROFILE + "- signal\n" * 65
        over_cap = PROFILE + "- signal\n" * 66
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/at.md": at_cap, "stacks/over.md": over_cap})
        self.addCleanup(scratch.cleanup)
        self.assertEqual(len(at_cap.splitlines()), 70)
        self.assertEqual(len(over_cap.splitlines()), 71)
        errors = validate_skill.stack_profile_errors(references)
        self.assertEqual(len(errors), 1)
        self.assertIn("over.md: 71 lines exceeds the 70-line cap", errors[0])

    def test_routed_but_missing_stacks_directory_is_reported(self):
        scratch, references = make_tree({"verification.md": "# Verification\n"})
        self.addCleanup(scratch.cleanup)
        errors = validate_skill.routing_errors(ROUTE, references)
        self.assertIn("SKILL.md: missing reference stacks/README.md", errors)

    def test_rule_defined_only_in_subdirectory_counts_as_defined(self):
        scratch, references = make_tree({"stacks/stack.md": "**SUB-RULE — text**\n"})
        self.addCleanup(scratch.cleanup)
        self.assertTrue(validate_skill.rule_is_defined("SUB-RULE", references))
        self.assertFalse(validate_skill.rule_is_defined("MISSING-RULE", references))

    def test_route_to_missing_stack_profile_fails(self):
        scratch, references = make_tree({"stacks/README.md": INDEX, "stacks/stack.md": PROFILE})
        self.addCleanup(scratch.cleanup)
        entry = "`references/stacks/x.md`"
        errors = validate_skill.routing_errors(entry, references)
        self.assertIn("SKILL.md: missing reference stacks/x.md", errors)

    def test_real_stack_profiles_are_linked_and_have_match_signals(self):
        stacks = validate_skill.REFERENCES / validate_skill.STACKS
        entry = (validate_skill.SKILL / "SKILL.md").read_text()
        if not stacks.is_dir():
            self.assertNotIn(ROUTE, entry, "SKILL.md routes stacks/README.md but references/stacks/ is missing")
            self.skipTest("references/stacks/ is absent and not routed")
        index = (stacks / "README.md").read_text()
        profiles = sorted(path for path in stacks.glob("*.md") if path.name != "README.md")
        self.assertTrue(profiles, "stacks/ has no profiles")
        for profile in profiles:
            with self.subTest(profile=profile.name):
                self.assertTrue(validate_skill.is_linked(profile.name, index), f"{profile.name} not linked from README.md")
                self.assertRegex(profile.read_text(), r"(?m)^## Match signals\s*$")


if __name__ == "__main__":
    unittest.main()
