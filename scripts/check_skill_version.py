#!/usr/bin/env python3
"""Load craft at session start and remind the user when a newer release exists. Never blocks: always exits 0.

Usage: check_skill_version.py [--check | --hook] [--timeout SECONDS]
  --check  (default) print the update notice to stderr when an update exists
  --hook   print one Claude Code SessionStart JSON object: the autoload context
           (unless CRAFT_AUTOLOAD=0|false) and a systemMessage when an update exists
Environment:
  CRAFT_AUTOLOAD=0|false   omit the autoload context
  CRAFT_UPDATE_CHECK=0     skip the network release check
  DISABLE_UPDATES, DISABLE_AUTOUPDATER, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
                           a non-empty value skips the network release check
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
UPDATE_COMMAND = "claude plugin update craft@Arkon"
AUTOLOAD = "craft is installed: for code, review, ticket or doc work, load Skill(craft:craft) before starting."
NETWORK_OFF_VARIABLES = ("DISABLE_UPDATES", "DISABLE_AUTOUPDATER", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC")
PLUGIN_JSON = Path(__file__).resolve().parents[1] / ".claude-plugin/plugin.json"
CACHE_TTL_SECONDS = 24 * 60 * 60


def parse_version(text):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", (text or "").strip())
    return tuple(int(part) for part in match.groups()) if match else None


def installed_version(plugin_json=PLUGIN_JSON):
    return json.loads(plugin_json.read_text()).get("version", "")


def cache_path(environ=None):
    environ = os.environ if environ is None else environ
    root = environ.get("CLAUDE_PLUGIN_DATA") or tempfile.gettempdir()
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
    latest = parse_version((release or {}).get("tag_name"))
    if not latest or not parse_version(current) or latest <= parse_version(current):
        return None
    shown = ".".join(map(str, latest))
    return (f"craft {shown} is available (you have {current}). "
            f"Update: {UPDATE_COMMAND}, then /reload-plugins. "
            "To get updates automatically: /plugin → Marketplaces → Arkon → enable auto-update.")


def autoload_enabled(environ):
    return environ.get("CRAFT_AUTOLOAD", "").strip().lower() not in ("0", "false")


def network_allowed(environ):
    if any(environ.get(name) for name in NETWORK_OFF_VARIABLES):
        return False
    return environ.get("CRAFT_UPDATE_CHECK", "").strip() != "0"


def hook_source(stream):
    """Return (parsed, source) from the hook's stdin JSON; parsed is False when stdin is absent or unparseable."""
    try:
        if stream is None or stream.isatty():
            return False, None
        data = json.loads(stream.read())
    except (OSError, ValueError):
        return False, None
    if not isinstance(data, dict):
        return False, None
    return True, data.get("source")


def update_message(args, environ, stdin):
    """Return the update notice, or None when there is no newer release or the check is skipped."""
    current = installed_version()
    if args.hook:
        parsed, source = hook_source(stdin)
        if parsed and source != "startup":
            return None
    if not network_allowed(environ):
        return None
    release = latest_release(args.timeout, cache=cache_path(environ))
    return reminder(current, release)


def main(argv=None, environ=None, stdin=None):
    environ = os.environ if environ is None else environ
    stdin = sys.stdin if stdin is None else stdin
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--hook", action="store_true")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        message = update_message(args, environ, stdin)
    except Exception as error:  # noqa: BLE001 - a version check must never block the skill
        print(f"craft version check skipped: {type(error).__name__}", file=sys.stderr)
        message = None
    if not args.hook:
        if message:
            print(message, file=sys.stderr)
        return 0
    payload = {}
    if autoload_enabled(environ):
        payload["hookSpecificOutput"] = {"hookEventName": "SessionStart", "additionalContext": AUTOLOAD}
    if message:
        payload["systemMessage"] = message
    if payload:
        print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
