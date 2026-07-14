#!/usr/bin/env python3
"""Build and validate both vendor distributions and the Deep Zotero binding."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

from build_plugin import DEFAULT_MCP_ROOT, DIST, ROOT, build
from install_plugin import configure_codex_mcp


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def file_manifest(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise AssertionError(f"generated output is missing: {root}")
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


def assert_generated_tree_matches(actual: Path, expected: Path, label: str) -> None:
    actual_files = file_manifest(actual)
    expected_files = file_manifest(expected)
    extra = sorted(set(actual_files) - set(expected_files))
    missing = sorted(set(expected_files) - set(actual_files))
    changed = sorted(
        path for path in set(actual_files) & set(expected_files)
        if actual_files[path] != expected_files[path]
    )
    if extra or missing or changed:
        raise AssertionError(
            f"{label} generated output is stale; run scripts/build_plugin.py. "
            f"extra={extra}, missing={missing}, changed={changed}"
        )


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError(f"missing frontmatter: {path}")
    end = lines.index("---", 1)
    result = {}
    for line in lines[1:end]:
        key, value = line.split(":", 1)
        result[key] = value.strip()
    return result


def run_optional(command: list[str], label: str) -> None:
    print(f"[{label}] {subprocess.list2cmdline(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcp-root", type=Path, default=DEFAULT_MCP_ROOT)
    parser.add_argument("--skip-claude-cli", action="store_true")
    args = parser.parse_args()
    mcp_root = args.mcp_root.resolve()

    claude = DIST / "claude" / "thesis-writer"
    codex = DIST / "codex" / "thesis-writer"
    with tempfile.TemporaryDirectory(prefix="thesis-writer-build-") as temporary:
        temporary_root = Path(temporary)
        expected_dist = temporary_root / "dist"
        expected_repository = temporary_root / "repository"
        build("claude", expected_dist, expected_repository)
        build("codex", expected_dist, expected_repository)
        first = tree_digest(expected_dist)
        build("claude", expected_dist, expected_repository)
        build("codex", expected_dist, expected_repository)
        if tree_digest(expected_dist) != first:
            raise AssertionError("fresh build is not deterministic")
        assert_generated_tree_matches(DIST / "claude", expected_dist / "claude", "Claude")
        assert_generated_tree_matches(DIST / "codex", expected_dist / "codex", "Codex")
        actual_marketplace = ROOT / ".claude-plugin" / "marketplace.json"
        expected_marketplace = expected_repository / ".claude-plugin" / "marketplace.json"
        if not actual_marketplace.is_file() or actual_marketplace.read_bytes() != expected_marketplace.read_bytes():
            raise AssertionError(
                "Claude marketplace output is stale; run scripts/build_plugin.py --vendor claude"
            )

    for path in sorted((claude / "skills").glob("*/SKILL.md")):
        keys = set(frontmatter(path))
        if keys != {"name", "description", "allowed-tools"}:
            raise AssertionError(f"invalid Claude frontmatter keys {keys}: {path}")
    for path in sorted((codex / "skills").glob("*/SKILL.md")):
        keys = set(frontmatter(path))
        if keys != {"name", "description"}:
            raise AssertionError(f"invalid Codex frontmatter keys {keys}: {path}")

    codex_text = "\n".join(path.read_text(encoding="utf-8") for path in codex.rglob("*") if path.is_file() and path.suffix in {".md", ".py"})
    claude_text = "\n".join(path.read_text(encoding="utf-8") for path in claude.rglob("*") if path.is_file() and path.suffix in {".md", ".py"})
    for forbidden in ("AskUserQuestion", "Task tool", "via Task", ".claude", "CLAUDE.md", "Claude Agent"):
        if forbidden in codex_text:
            raise AssertionError(f"Claude-only term leaked into Codex output: {forbidden}")
    for forbidden in ("AGENTS.md", ".codex", "Codex Agent"):
        if forbidden in claude_text:
            raise AssertionError(f"Codex-only term leaked into Claude output: {forbidden}")
    if "<!-- vendor:" in codex_text or "<!-- vendor:" in claude_text:
        raise AssertionError("unresolved vendor marker in generated output")

    skill_creator = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    plugin_creator = Path.home() / ".codex" / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
    for skill in sorted(path.parent for path in (codex / "skills").glob("*/SKILL.md")):
        run_optional([sys.executable, str(skill_creator), str(skill)], f"Codex quick_validate {skill.name}")
    run_optional([sys.executable, str(plugin_creator), str(codex)], "Codex validate_plugin")

    if (codex / ".mcp.json").exists() or not (codex / ".mcp.json.example").is_file():
        raise AssertionError("committed Codex dist must contain only the install-time MCP example")
    with tempfile.TemporaryDirectory(prefix="thesis-writer-codex-") as temporary:
        configured = Path(temporary) / "thesis-writer"
        shutil.copytree(codex, configured)
        configure_codex_mcp(configured, mcp_root)
        run_optional([sys.executable, str(plugin_creator), str(configured)], "Configured Codex validate_plugin")

    if not args.skip_claude_cli:
        run_optional(["claude", "plugin", "validate", str(claude)], "Claude plugin validate")
        run_optional(["claude", "plugin", "validate", str(ROOT)], "Claude marketplace validate")

    interpreter = mcp_root / ".venv" / "Scripts" / "python.exe"
    run_optional([str(interpreter), "-c", "import deep_zotero.server; print('deep_zotero.server import OK')"], "Deep Zotero import")
    print("All validations passed.")


if __name__ == "__main__":
    main()
