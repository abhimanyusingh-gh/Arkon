#!/usr/bin/env python3
"""Discover bounded, reproducible project context for the craft skill as JSON."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from xml.etree import ElementTree


BUILD_MANIFESTS = ("pom.xml", "package.json", "build.gradle", "build.gradle.kts", "go.mod",
                   "pyproject.toml")
INSTRUCTIONS = ("CLAUDE.md", ".claude/CLAUDE.md")
SOURCE_SUFFIXES = (".java", ".kt", ".ts", ".tsx", ".js", ".py", ".go")
SKIP_DIRECTORIES = {".git", "node_modules", "target", "build", "dist", ".venv", "venv",
                    "__pycache__", ".idea"}
SOURCE_FILE_CAP = 200
READ_CAP = 256 * 1024
BINDING_CAP = 30
BRANDED_CAP = 20
VALUE_CAP = 200
SCHEMA_VERSION = 1
NPM_TABLES = (
    ("framework", {"express": "express", "next": "next", "react": "react", "@nestjs/core": "nestjs"}),
    ("orm", {"prisma": "prisma", "typeorm": "typeorm", "sequelize": "sequelize"}),
    ("database", {"mysql": "mysql", "mysql2": "mysql", "mariadb": "mariadb", "pg": "postgresql",
                  "mongodb": "mongodb", "sqlite3": "sqlite", "better-sqlite3": "sqlite"}),
    ("test_framework", {"jest": "jest", "vitest": "vitest", "cypress": "cypress"}),
)
PYTHON_TABLES = (
    ("framework", {"django": "django", "fastapi": "fastapi", "flask": "flask"}),
    ("orm", {"sqlalchemy": "sqlalchemy"}),
    ("database", {"psycopg": "postgresql", "psycopg2": "postgresql", "pymysql": "mysql",
                  "mysqlclient": "mysql", "pymongo": "mongodb"}),
    ("test_framework", {"pytest": "pytest"}),
)
MAVEN_DATABASES = ("mysql", "mariadb", "postgresql", "mongodb", "sqlite")
BRANDED = {
    ".java": re.compile(r"record (\w+)\(\s*String\s+\w+\s*\)"),
    ".ts": re.compile(r"type (\w+) = string & \{\s*readonly __brand"),
    ".tsx": re.compile(r"type (\w+) = string & \{\s*readonly __brand"),
}
MARKERS = {
    "async_patterns": ("@Scheduled", "@Async", "@Incoming", "setInterval", "cron"),
    "authorization": ("@RolesAllowed", "@PreAuthorize", "@Authenticated", "@PermitAll", "requireAuth"),
}
ROW = re.compile(r"^\|\s*`<([\w.-]+)>`\s*\|\s*(.*?)\s*\|", re.M)


def word(name):
    return re.compile(rf"(?<!\w){re.escape(name)}(?!\w)")


def field(value, confidence, source):
    return {"value": value, "confidence": confidence, "source": source}


def single(found, category, confidence):
    if not found.get(category):
        return None
    value, source = next(iter(found[category].items()))
    return field(value, confidence, source)


def multiple(found, category, confidence, cap=None):
    if not found.get(category):
        return None
    return field(sorted(found[category])[:cap], confidence, next(iter(found[category].values())))


def inside(path, base):
    try:
        return path.is_file() and path.resolve().is_relative_to(base)
    except (OSError, RuntimeError):
        return False


def manifest_names(root):
    """Build manifests at the root and one directory down (multi-module repositories)."""
    names = [*BUILD_MANIFESTS, *INSTRUCTIONS]
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.is_symlink() and not child.name.startswith(".") \
                and child.name not in SKIP_DIRECTORIES:
            names += [f"{child.name}/{name}" for name in BUILD_MANIFESTS]
    return names


def manifest_bytes(root):
    return {name: (root / name).read_bytes() for name in manifest_names(root)
            if inside(root / name, root)}


def basename(name):
    return name.rsplit("/", 1)[-1]


def hash_manifests(manifests):
    digest = hashlib.sha256()
    for name in sorted(manifests):
        digest.update(f"{name}\0{hashlib.sha256(manifests[name]).hexdigest()}\n".encode())
    return digest.hexdigest()


def root_hash(root):
    return hash_manifests(manifest_bytes(Path(root).resolve()))


def decode(data):
    return data[:READ_CAP].decode("utf-8", errors="replace")


def maven_artifacts(data):
    try:
        tree = ElementTree.fromstring(data[:READ_CAP])
    except ElementTree.ParseError:
        return []
    artifacts = []
    for element in tree.iter():
        if element.tag.rsplit("}", 1)[-1] == "dependency":
            values = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in element}
            artifacts.append((values.get("groupId", ""), values.get("artifactId", "")))
    return artifacts


def npm_dependencies(text):
    try:
        manifest = json.loads(text)
    except ValueError:
        return set()
    if not isinstance(manifest, dict):
        return set()
    names = set()
    for key in ("dependencies", "devDependencies"):
        if isinstance(manifest.get(key), dict):
            names.update(manifest[key])
    return names


def detect_manifests(manifests, texts):
    found = {}

    def add(category, value, source):
        found.setdefault(category, {}).setdefault(value, source)

    systems = {"pom.xml": "maven", "build.gradle": "gradle", "build.gradle.kts": "gradle",
               "package.json": "npm", "go.mod": "go", "pyproject.toml": "python"}
    for name, text in texts.items():
        kind = basename(name)
        if kind not in systems or name in INSTRUCTIONS:
            continue
        add("build_system", systems[kind], name)
        if kind in ("pom.xml", "build.gradle", "build.gradle.kts"):
            kotlin = any(marker in text for marker in
                         ("kotlin-maven-plugin", "org.jetbrains.kotlin", 'kotlin("jvm")'))
            add("language", "kotlin" if kotlin else "java", name)
        elif kind == "package.json":
            npm = npm_dependencies(text)
            add("language", "typescript" if "typescript" in npm else "javascript", name)
            for category, table in NPM_TABLES:
                for dependency, value in table.items():
                    if dependency in npm:
                        add(category, value, name)
        elif kind == "go.mod":
            add("language", "go", name)
        elif kind == "pyproject.toml":
            add("language", "python", name)
            for category, table in PYTHON_TABLES:
                for dependency, value in table.items():
                    if word(dependency).search(text):
                        add(category, value, name)
        if kind == "pom.xml":
            detect_maven(maven_artifacts(manifests[name]), name, add)
    return found


def detect_maven(artifacts, source, add):
    for group, artifact in artifacts:
        if group == "io.quarkus":
            add("framework", "quarkus", source)
        if group == "org.springframework.boot":
            add("framework", "spring-boot", source)
        if artifact.startswith("quarkus-hibernate-orm") or artifact in (
                "hibernate-core", "spring-boot-starter-data-jpa"):
            add("orm", "hibernate", source)
        if group.startswith("org.testcontainers") or "testcontainers" in artifact:
            add("test_framework", "testcontainers", source)
        elif artifact.startswith("junit-jupiter") or artifact == "quarkus-junit5":
            add("test_framework", "junit5", source)
        else:
            for keyword in MAVEN_DATABASES:
                if keyword in artifact:
                    add("database", keyword, source)
            for keyword in ("flyway", "liquibase"):
                if keyword in artifact:
                    add("migrations", keyword, source)


def scan_sources(root, base):
    candidates = []
    for directory, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRECTORIES)
        candidates.extend(Path(directory, name) for name in filenames
                          if name.endswith(SOURCE_SUFFIXES))
    paths = []
    for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
        if len(paths) == SOURCE_FILE_CAP:
            break
        if inside(path, base):
            paths.append(path)

    hits = {"branded_types": {}, "async_patterns": {}, "authorization": {}}
    for path in paths:
        try:
            with path.open("rb") as handle:
                text = handle.read(READ_CAP).decode("utf-8", errors="replace")
        except OSError:
            continue
        relative = path.relative_to(root).as_posix()
        branded = BRANDED.get(path.suffix)
        for name in branded.findall(text) if branded else []:
            hits["branded_types"].setdefault(name, relative)
        for group, names in MARKERS.items():
            for name in names:
                if word(name).search(text):
                    hits[group].setdefault(name, relative)
    return len(paths), hits


def bindings(texts):
    values, first = {}, None
    for name in ("CLAUDE.md", ".claude/CLAUDE.md"):
        for key, raw in ROW.findall(texts.get(name, "")):
            value = raw.replace("`", "").strip()[:VALUE_CAP]
            if key in values or not value or len(values) >= BINDING_CAP:
                continue
            values[key] = value
            first = first or name
    return field(values, "declared", first) if values else None


def discover(root):
    root = Path(root).resolve()
    manifests = manifest_bytes(root)
    texts = {name: decode(data) for name, data in manifests.items()}
    found = detect_manifests(manifests, texts)
    scanned, hits = scan_sources(root, root)
    found.update(hits)
    fields = {
        "build_system": single(found, "build_system", "detected"),
        "language": single(found, "language", "inferred"),
        "framework": multiple(found, "framework", "detected"),
        "orm": single(found, "orm", "detected"),
        "database": single(found, "database", "detected"),
        "migrations": single(found, "migrations", "detected"),
        "test_framework": multiple(found, "test_framework", "detected"),
        "branded_types": multiple(found, "branded_types", "detected", BRANDED_CAP),
        "async_patterns": multiple(found, "async_patterns", "detected"),
        "authorization": multiple(found, "authorization", "detected"),
        "bindings": bindings(texts),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root_hash": hash_manifests(manifests),
        "sources": sorted(manifests),
        "fields": fields,
        "limits": {"source_files_scanned": scanned, "source_file_cap": SOURCE_FILE_CAP},
    }


def write_atomically(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         delete=False) as handle:
            temporary = handle.name
            handle.write(json.dumps(document, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, path)
    except BaseException:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
        raise


def stale_reason(out, root):
    if not out.is_file():
        return f"missing {out}"
    try:
        saved = json.loads(out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return f"unreadable {out}: {error}"
    if not isinstance(saved, dict) or saved.get("schema_version") != SCHEMA_VERSION:
        return "schema_version is not 1"
    if saved.get("root_hash") != root_hash(root):
        return "root_hash differs from current build and instruction files"
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Discover project context for the craft skill.")
    parser.add_argument("root", help="repository root to inspect")
    parser.add_argument("--out", type=Path,
                        help="output JSON path (default: ROOT/.claude/craft-context.json)")
    parser.add_argument("--check", action="store_true",
                        help="verify the existing output is current without writing")
    arguments = parser.parse_args(argv)
    root = Path(arguments.root)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    root = root.resolve()
    out = arguments.out or root / ".claude" / "craft-context.json"
    if arguments.check:
        reason = stale_reason(out, root)
        if reason:
            print(f"stale: {reason}", file=sys.stderr)
            return 1
        return 0
    try:
        write_atomically(out, discover(root))
    except OSError as error:
        print(f"error: cannot write {out}: {error}", file=sys.stderr)
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
