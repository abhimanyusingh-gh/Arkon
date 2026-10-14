#!/usr/bin/env python3
"""Test that all rule IDs referenced in rationalization tables are defined in references."""

import re
import unittest
from pathlib import Path


class TestRuleIds(unittest.TestCase):
    """Verify rule IDs in rationalization tables exist in references."""

    def setUp(self):
        """Set up paths."""
        self.craft_dir = Path(__file__).parent.parent
        self.references_dir = self.craft_dir / "references"
        self.verification_file = self.references_dir / "verification.md"
        self.review_file = self.references_dir / "review.md"

    def extract_rule_ids_from_file(self, filepath):
        """Extract all backticked rule IDs from a file."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all backticked IDs: `ID` where ID is uppercase letters/hyphens
        pattern = r"`([A-Z][A-Z\-]*)`"
        matches = re.findall(pattern, content)
        return set(matches)

    def rule_exists_in_references(self, rule_id):
        """Check if a rule ID is defined in any reference file."""
        try:
            # Search in all .md files in references directory
            for md_file in self.references_dir.glob("*.md"):
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for **ID — pattern (bold with em dash or hyphen)
                if re.search(rf"\*\*{re.escape(rule_id)}\s+[—-]", content):
                    return True

                # Check for ## ID — pattern (section heading)
                if re.search(rf"^## {re.escape(rule_id)}\s+[—-]", content, re.MULTILINE):
                    return True

                # Check for # ID pattern (top-level heading)
                if re.search(rf"^# {re.escape(rule_id)}\s", content, re.MULTILINE):
                    return True

            return False
        except Exception as e:
            print(f"Error checking rule {rule_id}: {e}")
            return False

    def test_verification_rule_ids_exist(self):
        """All rule IDs in verification.md table must be defined."""
        rule_ids = self.extract_rule_ids_from_file(self.verification_file)
        missing = []
        for rule_id in rule_ids:
            if not self.rule_exists_in_references(rule_id):
                missing.append(rule_id)

        self.assertEqual(
            missing,
            [],
            f"Rule IDs referenced in verification.md but not defined: {missing}"
        )

    def test_review_rule_ids_exist(self):
        """All rule IDs in review.md table must be defined."""
        rule_ids = self.extract_rule_ids_from_file(self.review_file)
        missing = []
        for rule_id in rule_ids:
            if not self.rule_exists_in_references(rule_id):
                missing.append(rule_id)

        self.assertEqual(
            missing,
            [],
            f"Rule IDs referenced in review.md but not defined: {missing}"
        )

    def test_rule_ids_extracted_from_tables(self):
        """Verify we can extract rule IDs from the rationalization tables."""
        verification_ids = self.extract_rule_ids_from_file(self.verification_file)
        review_ids = self.extract_rule_ids_from_file(self.review_file)

        # Should have extracted some IDs
        self.assertGreater(len(verification_ids), 0,
                          "Failed to extract rule IDs from verification.md")
        self.assertGreater(len(review_ids), 0,
                          "Failed to extract rule IDs from review.md")


if __name__ == "__main__":
    unittest.main()
