from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from release import (
    INPUT_PATHS,
    RELEASE_PATHS,
    SEMANTIC_VERSION,
    TAG_PREFIX,
    assert_committable,
    assert_nothing_uncommitted,
    assert_tag_is_available,
    commit_and_tag,
    git,
)

INPUT_REASON = "commit these build inputs first"
RELEASE_REASON = "commit or revert these release paths first"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def make_repository(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    git(directory, "init", "-b", "main")
    git(directory, "config", "user.name", "Release Test")
    git(directory, "config", "user.email", "release@example.com")
    write(directory / ".gitattributes", "* text=auto eol=lf\n")
    write(directory / "metadata.json", '{\n  "version": "0.1.0"\n}\n')
    write(directory / ".claude-plugin" / "marketplace.json", '{\n  "version": "0.1.0"\n}\n')
    write(directory / "dist" / "claude" / "plugin.json", '{\n  "version": "0.1.0"\n}\n')
    for input_path in INPUT_PATHS:
        write(directory / input_path / "kept.md", "content\n")
    git(directory, "add", "--all")
    git(directory, "commit", "-m", "initial")
    return directory


def bump(repository: Path, version: str) -> None:
    write(repository / "metadata.json", f'{{\n  "version": "{version}"\n}}\n')


def test_semantic_version_accepts_releases_and_rejects_malformed_input() -> None:
    for accepted in ("0.4.0", "1.0.0", "0.4.0-rc.1"):
        assert SEMANTIC_VERSION.fullmatch(accepted)
    for rejected in ("0.4", "v0.4.0", "00.4.0", "0.4.0.1", ""):
        assert not SEMANTIC_VERSION.fullmatch(rejected)


def test_commit_and_tag_makes_a_release_commit_with_an_annotated_tag(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    bump(repository, "0.4.0")

    tag = commit_and_tag(repository, "0.4.0")

    assert tag == f"{TAG_PREFIX}0.4.0"
    assert git(repository, "cat-file", "-t", tag) == "tag"
    assert git(repository, "tag", "--points-at", "HEAD") == tag
    assert git(repository, "for-each-ref", "--format=%(contents:subject)", f"refs/tags/{tag}") == (
        "thesis-writer 0.4.0"
    )
    assert git(repository, "log", "-1", "--format=%s") == (
        "chore: release version 0.4.0 across metadata, marketplace, and both distributions"
    )
    assert git(repository, "status", "--porcelain") == ""


def test_commit_and_tag_stages_only_release_paths(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    bump(repository, "0.4.0")
    write(repository / "src" / "kept.md", "edited after the guards ran\n")

    commit_and_tag(repository, "0.4.0")

    assert git(repository, "show", "--name-only", "--format=", "HEAD") == "metadata.json"
    assert git(repository, "status", "--porcelain") == "M src/kept.md"


def test_commit_and_tag_refuses_an_already_released_version(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")

    with pytest.raises(SystemExit, match="nothing to release"):
        commit_and_tag(repository, "0.1.0")


def test_existing_tag_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    tag = f"{TAG_PREFIX}0.4.0"
    git(repository, "tag", "-a", tag, "-m", "thesis-writer 0.4.0")

    with pytest.raises(SystemExit, match="tag already exists"):
        assert_tag_is_available(repository, tag)


def test_absent_tag_is_available(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")

    assert_tag_is_available(repository, f"{TAG_PREFIX}0.4.0")


def test_modified_build_input_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    write(repository / "src" / "kept.md", "edited\n")

    with pytest.raises(SystemExit, match=INPUT_REASON):
        assert_nothing_uncommitted(repository, INPUT_PATHS, INPUT_REASON, include_untracked=True)


def test_staged_build_input_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    write(repository / "vendors" / "kept.md", "edited\n")
    git(repository, "add", "--", "vendors/kept.md")

    with pytest.raises(SystemExit, match="vendors/kept.md"):
        assert_nothing_uncommitted(repository, INPUT_PATHS, INPUT_REASON, include_untracked=True)


def test_untracked_build_input_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    write(repository / "src" / "new-skill.md", "new\n")

    with pytest.raises(SystemExit, match="new-skill.md"):
        assert_nothing_uncommitted(repository, INPUT_PATHS, INPUT_REASON, include_untracked=True)


def test_committed_build_inputs_pass_the_guard(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")

    assert_nothing_uncommitted(repository, INPUT_PATHS, INPUT_REASON, include_untracked=True)


def test_modified_release_path_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    write(repository / "dist" / "claude" / "plugin.json", '{\n  "version": "9.9.9"\n}\n')

    with pytest.raises(SystemExit, match=RELEASE_REASON):
        assert_nothing_uncommitted(repository, RELEASE_PATHS, RELEASE_REASON)


def test_untracked_generated_output_does_not_block_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    write(repository / "dist" / "claude" / "stale.md", "regenerated away by the build\n")

    assert_nothing_uncommitted(repository, RELEASE_PATHS, RELEASE_REASON)


def test_line_ending_difference_is_not_an_uncommitted_change(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    (repository / "src" / "kept.md").write_bytes(b"content\r\n")

    assert_nothing_uncommitted(repository, INPUT_PATHS, INPUT_REASON, include_untracked=True)


def test_detached_head_blocks_the_release(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")
    git(repository, "checkout", "--detach")

    with pytest.raises(SystemExit, match="detached"):
        assert_committable(repository)


def test_branch_checkout_is_committable(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "repo")

    assert_committable(repository)


def test_non_repository_is_not_committable(tmp_path: Path) -> None:
    directory = tmp_path / "plain"
    directory.mkdir()

    with pytest.raises(SystemExit, match="not a git repository"):
        assert_committable(directory)
