import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/craft/scripts/discover_project_context.py"
SPEC = importlib.util.spec_from_file_location("discover_project_context", SCRIPT)
context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context)

POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <dependencies>
    <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-resteasy</artifactId></dependency>
    <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-hibernate-orm</artifactId></dependency>
    <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-jdbc-mysql</artifactId></dependency>
    <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-flyway</artifactId></dependency>
    <dependency><groupId>io.quarkus</groupId><artifactId>quarkus-junit5</artifactId><scope>test</scope></dependency>
  </dependencies>
</project>
"""
CLAUDE_MD = """# Project

| Key | Value |
|-----|-------|
| `<pm>` | `mvn` |
| `<scope-key>` | `RegionCode` |
"""
REGION = "package com.example;\n\npublic record RegionCode(String value) {}\n"
SCHEDULED = ("package com.example;\n\nclass Sync {\n"
             "    @Scheduled(cron = \"0 * * * * ?\")\n    void run() {}\n}\n")
REGION_PATH = "src/main/java/com/example/RegionCode.java"
SYNC_PATH = "src/main/java/com/example/Sync.java"


class DiscoverProjectContextTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name) / "repo"
        self.write("pom.xml", POM)
        self.write("CLAUDE.md", CLAUDE_MD)
        self.write(REGION_PATH, REGION)
        self.write(SYNC_PATH, SCHEDULED)

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_main(self, *arguments):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = context.main(list(arguments))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_detects_maven_java_quarkus_hibernate(self):
        fields = context.discover(self.root)["fields"]
        self.assertEqual("maven", fields["build_system"]["value"])
        self.assertEqual("detected", fields["build_system"]["confidence"])
        self.assertEqual("java", fields["language"]["value"])
        self.assertIn("quarkus", fields["framework"]["value"])
        self.assertEqual("hibernate", fields["orm"]["value"])
        self.assertEqual("mysql", fields["database"]["value"])
        self.assertEqual("flyway", fields["migrations"]["value"])
        self.assertEqual(["junit5"], fields["test_framework"]["value"])
        self.assertEqual(["@Scheduled", "cron"], fields["async_patterns"]["value"])
        self.assertEqual(SYNC_PATH, fields["async_patterns"]["source"])

    def test_reads_module_manifest_one_level_down(self):
        aggregator = POM.split("<dependencies>")[0] + "</project>\n"
        self.write("service/pom.xml", POM)
        self.write("pom.xml", aggregator)
        result = context.discover(self.root)
        self.assertIn("service/pom.xml", result["sources"])
        self.assertEqual("quarkus", result["fields"]["framework"]["value"][0])
        self.assertEqual("service/pom.xml", result["fields"]["orm"]["source"])
        out = self.root / "ctx.json"
        self.assertEqual(0, self.run_main(str(self.root), "--out", str(out))[0])
        self.write("service/pom.xml", POM.replace("quarkus-flyway", "quarkus-liquibase"))
        self.assertEqual(1, self.run_main(str(self.root), "--out", str(out), "--check")[0])

    def test_detects_branded_type(self):
        branded = context.discover(self.root)["fields"]["branded_types"]
        self.assertEqual(["RegionCode"], branded["value"])
        self.assertEqual("detected", branded["confidence"])
        self.assertEqual(REGION_PATH, branded["source"])

    def test_parses_claude_md_bindings(self):
        bindings = context.discover(self.root)["fields"]["bindings"]
        self.assertEqual("mvn", bindings["value"]["pm"])
        self.assertEqual("RegionCode", bindings["value"]["scope-key"])
        self.assertEqual("declared", bindings["confidence"])
        self.assertEqual("CLAUDE.md", bindings["source"])

    def test_missing_fields_are_null_not_guessed(self):
        self.assertIsNone(context.discover(self.root)["fields"]["authorization"])
        empty = Path(self.scratch.name) / "empty"
        empty.mkdir()
        fields = context.discover(empty)["fields"]
        self.assertEqual({}, {name: value for name, value in fields.items() if value is not None})

    def test_check_mode_detects_stale_context(self):
        out = self.root / ".claude" / "craft-context.json"
        self.assertEqual(0, self.run_main(str(self.root), "--out", str(out))[0])
        self.assertEqual(0, self.run_main(str(self.root), "--out", str(out), "--check")[0])
        self.write("pom.xml", POM + "\n")
        code, _, error = self.run_main(str(self.root), "--out", str(out), "--check")
        self.assertEqual(1, code)
        self.assertIn("stale:", error)
        out.unlink()
        self.assertEqual(1, self.run_main(str(self.root), "--out", str(out), "--check")[0])

    def test_does_not_follow_symlink_outside_root(self):
        outside = Path(self.scratch.name) / "outside"
        outside.mkdir()
        (outside / "Leaked.java").write_text("public record Leaked(String value) {}\n")
        try:
            os.symlink(outside / "Leaked.java", self.root / "src/main/java/com/example/Leaked.java")
        except OSError:
            self.skipTest("symlinks are unavailable")
        result = context.discover(self.root)
        branded = result["fields"]["branded_types"]["value"]
        self.assertNotIn("Leaked", branded)
        self.assertIn("RegionCode", branded)
        self.assertEqual(2, result["limits"]["source_files_scanned"])

    def test_output_written_atomically_and_valid_json(self):
        out = self.root / "nested" / "ctx.json"
        code, stdout, _ = self.run_main(str(self.root), "--out", str(out))
        self.assertEqual(0, code)
        self.assertEqual(str(out), stdout.strip())
        document = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(1, document["schema_version"])
        self.assertEqual(context.root_hash(self.root), document["root_hash"])
        self.assertEqual(["ctx.json"], sorted(path.name for path in out.parent.iterdir()))

    def test_invalid_root_exits_two(self):
        code, _, error = self.run_main(str(self.root / "missing"))
        self.assertEqual(2, code)
        self.assertIn("not a directory", error)


if __name__ == "__main__":
    unittest.main()
