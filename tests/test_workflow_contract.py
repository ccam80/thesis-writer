from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src" / "skills"
STYLED_SKILLS = ("document-planner", "prose-sweep")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def shipped_sources() -> list[Path]:
    """Every Markdown source that reaches a distribution."""
    paths = [
        *(ROOT / "src").rglob("*.md"),
        *(ROOT / "vendors").rglob("*.md"),
    ]
    return sorted(paths)


def test_no_source_still_routes_work_through_the_retired_ledger() -> None:
    retired = (
        "evidence.md",
        "write-ready",
        "claim-map",
        "PROJECT_FACT",
        "Unresolved points",
        "point ID",
        "`writer`",
        "technical-writing",
    )
    for path in shipped_sources():
        source = text(path)
        for term in retired:
            assert term not in source, f"{term!r} found in {path.relative_to(ROOT)}"


def test_every_companion_file_a_skill_names_exists() -> None:
    reference = re.compile(r"(?:\.\./(?P<skill>[a-z-]+)/)?(?P<path>(?:references|scripts)/[A-Za-z0-9_.-]+\.(?:md|py))")
    checked = 0
    for skill in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
        for match in reference.finditer(text(skill / "body.md")):
            owner = SKILLS / match.group("skill") if match.group("skill") else skill
            assert (owner / match.group("path")).is_file(), f"{skill.name} names missing {match.group(0)}"
            checked += 1
    assert checked


def test_skills_that_need_the_contract_fail_closed_without_it() -> None:
    for name in ("document-planner", "prose-sweep", "reviewer"):
        assert "<!-- vendor:contract-location -->" in text(SKILLS / name / "body.md")
    for vendor in ("claude", "codex"):
        fragment = text(ROOT / "vendors" / vendor / "fragments" / "contract-location.md")
        assert "stop and ask the author to run the initializer" in fragment


def test_research_worker_uses_only_current_deep_zotero_tools() -> None:
    research = text(SKILLS / "zotero-research" / "body.md")
    for retired_tool in ("search_boolean", "search_tables", "search_figures"):
        assert retired_tool not in research
    assert "required_terms" in research
    assert "chunk_types" in research


def test_figure_placeholder_format_has_one_owner() -> None:
    owners = [
        path for path in SKILLS.rglob("*.md")
        if "FIGURE PLACEHOLDER" in text(path)
    ]
    assert owners == [SKILLS / "figure-generator" / "references" / "figure-placeholder.md"]


def sentences(path: Path) -> set[str]:
    collapsed = " ".join(text(path).split())
    return {s.strip() for s in re.split(r"(?<=[.:])\s+", collapsed) if len(s.strip()) > 25}


@pytest.mark.parametrize("skill", STYLED_SKILLS)
def test_a_styled_skill_does_not_restate_its_style(skill: str) -> None:
    # Codex inlines the style into the skill, so a shared sentence would appear twice.
    style = ROOT / "src" / "output-styles" / "writing-planner.md"
    assert sentences(style) & sentences(SKILLS / skill / "body.md") == set()


@pytest.mark.parametrize("skill", STYLED_SKILLS)
def test_the_codex_build_does_not_repeat_a_section_heading(skill: str) -> None:
    built = ROOT / "dist" / "codex" / "thesis-writer" / "skills" / skill / "SKILL.md"
    headings = [
        line.strip()
        for line in text(built).splitlines()
        if line.startswith("## ") or line.startswith("### ")
    ]
    assert {h for h in headings if headings.count(h) > 1} == set()


def load_linter():
    path = SKILLS / "prose-sweep" / "scripts" / "lint_prose.py"
    spec = importlib.util.spec_from_file_location("lint_prose", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rules(findings: list[dict[str, object]]) -> set[object]:
    return {finding["rule"] for finding in findings}


def test_linter_leaves_clean_prose_alone() -> None:
    linter = load_linter()
    assert linter.lint_text("The filter settles within \\SI{40}{\\milli\\second}.") == []
    assert linter.lint_text("A many-core device runs 5\\% faster.") == []


@pytest.mark.parametrize(
    "prose,rule",
    [
        ("Crucially, the method works.", "sentence-adverb"),
        ("This section discusses the method.", "meta-narration"),
        ("The method --- in brief --- works.", "em-dash"),
        ("The cache is very small.", "weasel"),
        ("Several studies agree.", "weasel"),
        ("The kernel probably stalls.", "weakening-adverb"),
        ("It is believed that caches help.", "hidden-authority"),
        ("The kernel waits in order to sync.", "gaucherie"),
        ("The kernel doesn't stall.", "contraction"),
        ("The figure below shows the layout.", "relative-reference"),
        ("Occupancy will be discussed later.", "future-tense"),
        ("The latency is [[value]] cycles.", "placeholder"),
        ("Caches help [cite].", "placeholder"),
        ("The product is $a * b$.", "star-multiplication"),
        ("Why does it stall?", "rhetorical-question"),
    ],
)
def test_linter_flags_each_banned_pattern(prose: str, rule: str) -> None:
    assert rule in rules(load_linter().lint_text(prose))


def test_linter_suggests_the_replacement_for_a_gaucherie() -> None:
    findings = load_linter().lint_text("The kernel waits prior to the barrier.")
    assert [f["suggestion"] for f in findings if f["rule"] == "gaucherie"] == ["before"]


def test_linter_flags_a_connective_only_where_a_paragraph_opens() -> None:
    linter = load_linter()
    opening = "\\section{Memory}\nHowever, the cache is small.\n\nThe cache is small.\nHowever, it is fast.\n"
    findings = [f for f in linter.lint_text(opening) if f["rule"] == "paragraph-opener"]
    assert [f["line"] for f in findings] == [2]


def test_linter_treats_a_line_opening_with_a_reference_as_prose() -> None:
    findings = load_linter().lint_text("\\Cref{fig:x} shows a very small cache.")
    assert "weasel" in rules(findings)


def test_linter_ignores_comments_but_not_escaped_percent_signs() -> None:
    linter = load_linter()
    assert linter.lint_text("The cache is small. % very small") == []
    assert "weasel" in rules(linter.lint_text("A 5\\% drop is very small."))
