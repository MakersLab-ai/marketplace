#!/usr/bin/env python3
"""Fail when a plugin's marketplace.json version disagrees with its own plugin.json.

Claude Code decides an installed plugin is out of date purely by comparing version
numbers, and it reads the catalog entry while the installed plugin carries its own
manifest. A disagreement between the two is silent: a release simply never reaches
the people who have it installed. This check makes it loud instead.
"""

import json
import os
import sys

MARKETPLACE = os.path.join(".claude-plugin", "marketplace.json")


def main() -> int:
    with open(MARKETPLACE, encoding="utf-8") as handle:
        marketplace = json.load(handle)

    failures = []

    for entry in marketplace.get("plugins", []):
        name = entry.get("name", "<unnamed>")
        source = entry.get("source")

        if not isinstance(source, str):
            print(f"{name}: source is not a repository path, skipped")
            continue

        manifest = os.path.join(source.lstrip("./"), ".claude-plugin", "plugin.json")

        if not os.path.exists(manifest):
            failures.append(f"{name}: {manifest} does not exist")
            continue

        with open(manifest, encoding="utf-8") as handle:
            plugin = json.load(handle)

        catalog_version = entry.get("version")
        plugin_version = plugin.get("version")

        if catalog_version is None:
            failures.append(f"{name}: the marketplace.json entry has no version")
        elif plugin_version is None:
            failures.append(f"{name}: {manifest} has no version key")
        elif catalog_version != plugin_version:
            failures.append(
                f"{name}: marketplace.json says {catalog_version}, "
                f"{manifest} says {plugin_version}"
            )
        else:
            print(f"{name}: {plugin_version} OK")

    if failures:
        print()
        for failure in failures:
            print(f"MISMATCH: {failure}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
