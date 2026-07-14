from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_claude_instructions_are_a_portable_link_to_agents() -> None:
    claude = ROOT / "CLAUDE.md"
    agents = ROOT / "AGENTS.md"

    assert claude.is_symlink()
    assert os.readlink(claude) == "AGENTS.md"
    assert claude.resolve() == agents.resolve()


def test_build_and_install_do_not_consume_root_agent_instructions() -> None:
    scripts = list((ROOT / "scripts").glob("*.py"))
    assert scripts

    for script in scripts:
        text = script.read_text(encoding="utf-8")
        assert 'ROOT / "AGENTS.md"' not in text
        assert 'ROOT / "CLAUDE.md"' not in text

    build = (ROOT / "scripts" / "build_plugin.py").read_text(encoding="utf-8")
    assert 'ROOT / "src" / "templates" / "thesis-instructions.md"' in build


def test_maintainer_and_thesis_project_instructions_are_separate() -> None:
    maintainers = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    thesis_projects = (ROOT / "src" / "templates" / "thesis-instructions.md").read_text(encoding="utf-8")

    assert "This repository is not a thesis project." in maintainers
    assert "Root `AGENTS.md` is not an input to the plugin builder." in maintainers
    assert "doctoral thesis writing assistant" not in maintainers
    assert "doctoral thesis writing assistant" in thesis_projects
