from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_plugin import (
    build,
    ensure_all_fragments_used,
    ensure_all_styles_used,
    load_output_styles,
    render_fragments,
    render_styles,
)
from install_plugin import install_codex
from validate_all import assert_generated_tree_matches

STYLED_SKILLS = {
    "document-planner": "writing-planner",
    "writer": "technical-writing",
    "figure-generator": "image-output",
}


def write_style(directory: Path, name: str, token: str, body: str = "# Role\n\nBe terse.") -> Path:
    path = directory / f"{name}.md"
    path.write_text(
        f"---\nname: {name}\ndescription: test\nkeep-coding-instructions: false\n---\n\n"
        f"Canary: {name} output style active. {token}.\n\n{body}\n",
        encoding="utf-8",
    )
    return path


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


def test_claude_ships_output_styles_and_codex_does_not() -> None:
    claude = build("claude")
    codex = build("codex")
    shipped = {path.name for path in (claude / "output-styles").glob("*.md")}
    assert shipped == {f"{name}.md" for name in STYLED_SKILLS.values()}
    assert not (codex / "output-styles").exists()


@pytest.mark.parametrize("skill,style", sorted(STYLED_SKILLS.items()))
def test_claude_gets_the_canary_and_codex_gets_the_style_body(skill: str, style: str) -> None:
    styles = load_output_styles()
    token = styles[style]["token"]
    marker = styles[style]["body"].splitlines()[0]

    claude_skill = (build("claude") / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    codex_skill = (build("codex") / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")

    assert token in claude_skill
    assert f"intended to run with the `{style}` output style" in claude_skill
    assert marker not in claude_skill

    assert token not in codex_skill
    assert "Canary:" not in codex_skill
    assert f"#{marker}" in codex_skill


def test_no_canary_token_reaches_the_codex_distribution() -> None:
    codex = build("codex")
    text = "\n".join(path.read_text(encoding="utf-8") for path in codex.rglob("*.md"))
    for style in load_output_styles().values():
        assert style["token"] not in text


def test_output_style_markers_are_all_resolved() -> None:
    for vendor in ("claude", "codex"):
        output = build(vendor)
        text = "\n".join(path.read_text(encoding="utf-8") for path in output.rglob("*.md"))
        assert "<!-- style:" not in text


def test_shared_block_markers_do_not_reach_either_distribution() -> None:
    for vendor in ("claude", "codex"):
        output = build(vendor)
        text = "\n".join(path.read_text(encoding="utf-8") for path in output.rglob("*.md"))
        assert "<!-- shared:" not in text


def test_shared_block_body_survives_marker_stripping() -> None:
    for name, style in load_output_styles().items():
        assert "Laconic mode governs chat." in style["body"], name


def test_every_shipped_style_declares_a_unique_canary() -> None:
    styles = load_output_styles()
    tokens = [style["token"] for style in styles.values()]
    assert len(set(tokens)) == len(tokens)
    for style in styles.values():
        assert "name:" in style["frontmatter"]
        assert "description:" in style["frontmatter"]
        assert "keep-coding-instructions:" in style["frontmatter"]


def test_missing_style_is_an_error() -> None:
    with pytest.raises(ValueError, match="missing output style 'absent'"):
        render_styles("<!-- style:absent -->", "codex", {}, set(), Path("body.md"))


def test_unused_style_is_an_error() -> None:
    with pytest.raises(ValueError, match="unused output styles"):
        ensure_all_styles_used({"orphan": {"token": "XX-CANARY-0000"}}, set())


@pytest.mark.parametrize(
    "content,expected",
    [
        ("---\nname: broken\n---\n\n# Role\n", "missing canary line"),
        ("no frontmatter at all\n", "missing frontmatter"),
        (
            "---\nname: broken\n---\n\nCanary: other output style active. XX-CANARY-0001.\n",
            "does not match filename",
        ),
    ],
)
def test_malformed_style_is_an_error(content: str, expected: str) -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-style-test-") as temporary:
        directory = Path(temporary)
        (directory / "broken.md").write_text(content, encoding="utf-8")
        with pytest.raises(ValueError, match=expected):
            load_output_styles(directory)


def test_duplicate_canary_tokens_are_an_error() -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-style-test-") as temporary:
        directory = Path(temporary)
        write_style(directory, "first", "AA-CANARY-1111")
        write_style(directory, "second", "AA-CANARY-1111")
        with pytest.raises(ValueError, match="duplicate output-style canary tokens"):
            load_output_styles(directory)


def test_empty_style_directory_is_an_error() -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-style-test-") as temporary:
        with pytest.raises(ValueError, match="no output styles found"):
            load_output_styles(Path(temporary))


def test_codex_style_headings_are_demoted_under_the_skill_title() -> None:
    with tempfile.TemporaryDirectory(prefix="thesis-writer-style-test-") as temporary:
        directory = Path(temporary)
        write_style(directory, "demo", "ZZ-CANARY-9999", "# Role\n\ntext\n\n## Banned patterns\n\nmore")
        styles = load_output_styles(directory)
        rendered = render_styles("<!-- style:demo -->", "codex", styles, set(), Path("body.md"))
        assert "## Role" in rendered
        assert "### Banned patterns" in rendered
        assert "\n# Role" not in rendered


def test_zotero_research_cannot_delegate() -> None:
    allowed = json.loads((ROOT / "vendors" / "claude" / "skills.json").read_text(encoding="utf-8"))
    assert "Task" not in allowed["zotero-research"]


def test_template_contract_block_is_version_marked() -> None:
    version = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))["version"]
    for vendor, name in (("claude", "CLAUDE.thesis-writer.md"), ("codex", "AGENTS.thesis-writer.md")):
        template = (build(vendor) / "templates" / name).read_text(encoding="utf-8")
        begin = f"<!-- thesis-writer:contract v{version} -->"
        assert begin in template
        assert template.rstrip().endswith("<!-- /thesis-writer:contract -->")
        assert template.index("GENERATED FILE") < template.index(begin)


def test_initializers_update_only_the_versioned_contract_block() -> None:
    for relative in ("vendors/claude/commands/thesis-writer-init.md", "vendors/codex/init-skill/body.md"):
        init = (ROOT / relative).read_text(encoding="utf-8")
        assert "<!-- thesis-writer:contract v... -->" in init
        assert "<!-- /thesis-writer:contract -->" in init
        assert "Do not copy the generated-file notice" in init
        assert "change nothing and say so" in init
        assert "Never replace, reorder, or rewrite content outside the markers" in init


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
