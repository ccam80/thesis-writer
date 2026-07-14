from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_plugin import build, ensure_all_fragments_used, render_fragments
from install_plugin import install_codex
from validate_all import assert_generated_tree_matches


def test_both_vendors_build_with_expected_frontmatter() -> None:
    claude = build("claude")
    codex = build("codex")
    claude_skill = (claude / "skills" / "writer" / "SKILL.md").read_text(encoding="utf-8")
    codex_skill = (codex / "skills" / "writer" / "SKILL.md").read_text(encoding="utf-8")
    assert "allowed-tools:" in claude_skill
    assert "allowed-tools:" not in codex_skill
    assert "AskUserQuestion" not in codex_skill


def test_vendor_fragments_are_resolved() -> None:
    for vendor in ("claude", "codex"):
        output = build(vendor)
        text = "\n".join(path.read_text(encoding="utf-8") for path in output.rglob("*.md"))
        assert "<!-- vendor:" not in text


def test_missing_fragment_is_an_error() -> None:
    with pytest.raises(ValueError, match="missing vendor fragment"):
        render_fragments("<!-- vendor:missing -->", {}, set(), Path("body.md"))


def test_unused_fragment_is_an_error() -> None:
    with pytest.raises(ValueError, match="unused codex vendor fragments"):
        ensure_all_fragments_used({"unexpected": "content"}, set(), "codex")


def test_committed_codex_distribution_is_machine_independent() -> None:
    output = build("codex")
    assert not (output / ".mcp.json").exists()
    assert "<generated-at-install-time>" in (output / ".mcp.json.example").read_text(encoding="utf-8")
    assert "mcpServers" not in (output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")


@pytest.mark.parametrize("stale_relative", [Path("STALE.txt"), Path("thesis-writer") / "nested" / "STALE.txt"])
def test_build_removes_stale_files_across_vendor_boundary(stale_relative: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-test-") as temporary:
        temporary_root = Path(temporary)
        dist_root = temporary_root / "dist"
        repository_root = temporary_root / "repository"
        preserved = dist_root / "codex" / "PRESERVE.txt"
        preserved.parent.mkdir(parents=True)
        preserved.write_text("other vendor", encoding="utf-8")
        stale = dist_root / "claude" / stale_relative
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("stale", encoding="utf-8")

        build("claude", dist_root, repository_root)

        assert not stale.exists()
        assert preserved.read_text(encoding="utf-8") == "other vendor"


@pytest.mark.parametrize("stale_relative", [Path("STALE.txt"), Path("thesis-writer") / "nested" / "STALE.txt"])
def test_validation_rejects_stale_generated_files(stale_relative: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-validation-test-") as temporary:
        temporary_root = Path(temporary)
        actual = temporary_root / "actual"
        expected = temporary_root / "expected"
        actual.mkdir()
        expected.mkdir()
        stale = actual / stale_relative
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("stale", encoding="utf-8")

        with pytest.raises(AssertionError, match="generated output is stale"):
            assert_generated_tree_matches(actual, expected, "Test")


def test_codex_installer_uses_custom_marketplace_name(capsys: pytest.CaptureFixture[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-marketplace-test-") as temporary:
        root = Path(temporary)
        marketplace = root / ".agents" / "plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text(
            '{"name":"research","interface":{"displayName":"Research"},"plugins":[]}\n',
            encoding="utf-8",
        )
        install_codex(
            Path(r"C:\local_working_projects\zotero_citation_mcp"),
            False,
            root / "plugins",
            marketplace,
        )
        assert "thesis-writer@research" in capsys.readouterr().out


def test_codex_installer_preserves_existing_install_when_mcp_preflight_fails() -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-preflight-test-") as temporary:
        root = Path(temporary)
        plugin_home = root / "plugins"
        existing = plugin_home / "thesis-writer"
        existing.mkdir(parents=True)
        marker = existing / "WORKING_INSTALL.txt"
        marker.write_text("preserve me", encoding="utf-8")
        marketplace = root / ".agents" / "plugins" / "marketplace.json"

        with pytest.raises(FileNotFoundError, match="Deep Zotero interpreter not found"):
            install_codex(root / "missing-mcp", False, plugin_home, marketplace)

        assert marker.read_text(encoding="utf-8") == "preserve me"
