#!/usr/bin/env python3
"""Emit the plugins whose plugin.json version changed in this push.

Written as `releases=<json>` on stdout, for $GITHUB_OUTPUT. A plugin whose manifest is
new, or whose version differs from the one in the previous commit, is released; anything
else -- a docs-only change, a description edit, a version left alone -- is not.
"""

import json
import os
import subprocess
import sys

MARKETPLACE = os.path.join(".claude-plugin", "marketplace.json")
NULL_SHA = "0" * 40


def version_at(ref: str, path: str) -> str | None:
    """The version recorded in `path` at `ref`, or None when it did not exist there."""

    try:
        blob = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None

    try:
        return json.loads(blob).get("version")
    except json.JSONDecodeError:
        return None


def main() -> int:
    before = os.environ.get("BEFORE", "")

    with open(MARKETPLACE, encoding="utf-8") as handle:
        marketplace = json.load(handle)

    releases = []

    for entry in marketplace.get("plugins", []):
        name = entry.get("name")
        source = entry.get("source")

        if not name or not isinstance(source, str):
            continue

        manifest = os.path.join(source.lstrip("./"), ".claude-plugin", "plugin.json")

        if not os.path.exists(manifest):
            continue

        with open(manifest, encoding="utf-8") as handle:
            current = json.load(handle).get("version")

        if not current:
            continue

        # A first push, a force push onto a new history, or a branch created here all
        # arrive with no usable "before" -- release nothing rather than re-tagging
        # every plugin in the repository.
        previous = None if not before or before == NULL_SHA else version_at(before, manifest)

        if previous != current:
            print(f"{name}: {previous} -> {current}", file=sys.stderr)
            releases.append({"name": name, "version": current})
        else:
            print(f"{name}: unchanged at {current}", file=sys.stderr)

    print(f"releases={json.dumps(releases)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
