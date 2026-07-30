#!/usr/bin/env python3
"""Set a release version, rebuild both vendors, run the complete validator, then commit and tag."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from build_plugin import DEFAULT_MCP_ROOT, ROOT


SEMANTIC_VERSION = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?")
TAG_PREFIX = "thesis-writer-v"

# Paths the release commit carries.
RELEASE_PATHS = ("metadata.json", ".claude-plugin/marketplace.json", "dist")

# Build inputs the release regenerates from.
INPUT_PATHS = ("src", "vendors", "scripts")


def git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def assert_committable(repository: Path) -> None:
    try:
        git(repository, "rev-parse", "--git-dir")
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"not a git repository: {repository}") from error
    try:
        git(repository, "symbolic-ref", "--quiet", "HEAD")
    except subprocess.CalledProcessError as error:
        raise SystemExit("HEAD is detached; check out a branch before releasing") from error


def assert_nothing_uncommitted(
    repository: Path,
    paths: tuple[str, ...],
    reason: str,
    include_untracked: bool = False,
) -> None:
    """Compares filtered content; line-ending differences do not count as edits."""
    reports = [
        git(repository, "diff", "--name-only", "--", *paths),
        git(repository, "diff", "--cached", "--name-only", "--", *paths),
    ]
    if include_untracked:
        reports.append(git(repository, "ls-files", "--others", "--exclude-standard", "--", *paths))
    listed = sorted({line for report in reports for line in report.splitlines()})
    if listed:
        raise SystemExit(f"{reason}: {', '.join(listed)}")


def assert_tag_is_available(repository: Path, tag: str) -> None:
    if git(repository, "tag", "--list", tag):
        raise SystemExit(f"tag already exists: {tag}")


def commit_and_tag(repository: Path, version: str) -> str:
    tag = f"{TAG_PREFIX}{version}"
    git(repository, "add", "--", *RELEASE_PATHS)
    if not git(repository, "diff", "--cached", "--name-only", "--", *RELEASE_PATHS):
        raise SystemExit(f"nothing to release: version {version} and its distributions are already committed")
    git(
        repository,
        "commit",
        "-m",
        f"chore: release version {version} across metadata, marketplace, and both distributions",
    )
    git(repository, "tag", "-a", tag, "-m", f"thesis-writer {version}")
    return tag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--mcp-root", type=Path, default=DEFAULT_MCP_ROOT)
    parser.add_argument("--skip-claude-cli", action="store_true")
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Build and validate only, leaving the release uncommitted and untagged.",
    )
    args = parser.parse_args()
    if not SEMANTIC_VERSION.fullmatch(args.version):
        raise SystemExit(f"invalid semantic version: {args.version}")
    tag = f"{TAG_PREFIX}{args.version}"
    if not args.no_commit:
        assert_committable(ROOT)
        assert_tag_is_available(ROOT, tag)
        assert_nothing_uncommitted(ROOT, RELEASE_PATHS, "commit or revert these release paths first")
        assert_nothing_uncommitted(
            ROOT, INPUT_PATHS, "commit these build inputs first", include_untracked=True
        )
    metadata_path = ROOT / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["version"] = args.version
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_plugin.py"), "--vendor", "all"], check=True)
    command = [sys.executable, str(ROOT / "scripts" / "validate_all.py"), "--mcp-root", str(args.mcp_root.resolve())]
    if args.skip_claude_cli:
        command.append("--skip-claude-cli")
    subprocess.run(command, check=True)
    if args.no_commit:
        print(f"Release {args.version} is built and validated. Commit metadata.json and generated dist/ together, then tag the commit.")
        return
    commit_and_tag(ROOT, args.version)
    print(f"Release {args.version} is built, validated, committed, and tagged {tag}.")
    print("Push the branch and the tag only when explicitly authorized.")


if __name__ == "__main__":
    main()
