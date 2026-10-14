import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_skill.py"
SPEC = importlib.util.spec_from_file_location("validate_skill", SCRIPT)
validate_skill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_skill)


class RuleIdTest(unittest.TestCase):
    def test_rationalization_tables_reference_only_defined_rules(self):
        for name in validate_skill.RULE_ID_SOURCES:
            rule_ids = validate_skill.referenced_rule_ids(validate_skill.REFERENCES / name)
            self.assertTrue(rule_ids, f"no rule IDs extracted from {name}")
            undefined = sorted(r for r in rule_ids if not validate_skill.rule_is_defined(r))
            self.assertEqual(undefined, [], f"{name} references undefined rule IDs")

    def test_rule_definition_forms_are_recognised(self):
        with tempfile.TemporaryDirectory() as scratch:
            references = Path(scratch)
            (references / "a.md").write_text("**BOLD-RULE — text**\n## HEADING-RULE — text\n")
            self.assertTrue(validate_skill.rule_is_defined("BOLD-RULE", references))
            self.assertTrue(validate_skill.rule_is_defined("HEADING-RULE", references))
            self.assertFalse(validate_skill.rule_is_defined("MISSING-RULE", references))

    def test_capped_references_stay_within_their_caps(self):
        for name, cap in validate_skill.LINE_CAPS.items():
            lines = len((validate_skill.REFERENCES / name).read_text().splitlines())
            self.assertLessEqual(lines, cap, f"{name} exceeds its cap")


if __name__ == "__main__":
    unittest.main()
