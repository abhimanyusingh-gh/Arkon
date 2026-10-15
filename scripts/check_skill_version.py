#!/usr/bin/env python3
"""Remind the user when a newer craft release exists. Never blocks: always exits 0.

Usage: check_skill_version.py [--check | --hook] [--timeout SECONDS]
  --check  (default) print a reminder to stderr when an update exists
  --hook   print a Claude Code hook JSON object with a user-visible systemMessage
"""

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.request


RELEASES_URL = "https://api.github.com/repos/abhimanyusingh-gh/Arkon/releases/latest"
INSTALL = "/plugin install craft@Arkon"
PLUGIN_JSON = Path(__file__).resolve().parents[1] / ".claude-plugin/plugin.json"
CACHE_TTL_SECONDS = 24 * 60 * 60


def parse_version(text):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", (text or "").strip())
    return tuple(int(part) for part in match.groups()) if match else None


def installed_version(plugin_json=PLUGIN_JSON):
    return json.loads(plugin_json.read_text()).get("version", "")


def cache_path():
    root = os.environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()
    return Path(root) / "craft-latest-release.json"


def latest_release(timeout, cache=None, now=None, fetch=None):
    """Return {"tag_name", "html_url"} for the latest release, cached for a day."""
    cache = cache or cache_path()
    now = time.time() if now is None else now
    try:
        cached = json.loads(cache.read_text())
        if now - cached["checked_at"] < CACHE_TTL_SECONDS:
            return cached["release"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    release = (fetch or fetch_release)(timeout)
    try:
        cache.write_text(json.dumps({"checked_at": now, "release": release}))
    except OSError:
        pass
    return release


def fetch_release(timeout):
    request = urllib.request.Request(RELEASES_URL, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "craft-version-check"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read(64 * 1024))
    return {"tag_name": str(body.get("tag_name", "")), "html_url": str(body.get("html_url", ""))}


def reminder(current, release):
    latest = parse_version(release.get("tag_name"))
    if not latest or not parse_version(current) or latest <= parse_version(current):
        return None
    shown = ".".join(map(str, latest))
    return (f"craft skill update available: {current} -> {shown}\n"
            f"Update with: {INSTALL}\n"
            f"Changelog: {release.get('html_url', '')}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--hook", action="store_true")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        message = reminder(installed_version(), latest_release(args.timeout))
    except Exception as error:  # noqa: BLE001 - a version check must never block the skill
        print(f"craft version check skipped: {type(error).__name__}", file=sys.stderr)
        return 0
    if message and args.hook:
        print(json.dumps({"systemMessage": message}))
    elif message:
        print(message, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
