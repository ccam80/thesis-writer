from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLANNER = ROOT / "src" / "skills" / "document-planner" / "body.md"
STYLE = ROOT / "src" / "output-styles" / "writing-planner.md"
TEMPLATE = ROOT / "src" / "templates" / "thesis-instructions.md"
REVIEWER = ROOT / "src" / "skills" / "reviewer" / "body.md"
DIST_PLANNERS = (
    ROOT / "dist" / "claude" / "thesis-writer" / "skills" / "document-planner" / "SKILL.md",
    ROOT / "dist" / "codex" / "thesis-writer" / "skills" / "document-planner" / "SKILL.md",
)


def text(path: Path) -> str:
    """Read a source file with every whitespace run collapsed to one space."""

    return " ".join(path.read_text(encoding="utf-8").split())


def test_the_style_owns_the_approval_cycle() -> None:
    style = text(STYLE)

    assert "There is no autonomous editing at any level" in style
    assert "Present the complete list for the unit in hand, as a list." in style
    assert "Present the complete amended list again, in full." in style
    assert "Write exactly that list." in style
    assert (
        "An instruction to amend is an instruction to re-present, never an "
        "instruction to write." in style
    )
    assert "Your rendering of instructed changes is not approved content." in style
    assert "Never modify a plan file unprompted, and never offer to." in style


def test_the_skill_owns_what_reaches_the_artefacts() -> None:
    planner = text(PLANNER)

    assert (
        "`plan.md` holds only what the author approved in chat, in the form they "
        "approved, at every level and in every stage." in planner
    )
    assert "the file is never the working surface for an unsettled one" in planner
    assert "nothing undecided enters it" in planner
    assert "`evidence.md` is the exception, as a receipt store" in planner
    assert "Promotion to `write-ready` still requires author acceptance in chat." in planner


def test_the_style_and_the_skill_do_not_restate_each_other() -> None:
    import re

    def sentences(path: Path) -> set[str]:
        return {
            s.strip()
            for s in re.split(r"(?<=[.:])\s+", text(path))
            if len(s.strip()) > 25
        }

    assert sentences(STYLE) & sentences(PLANNER) == set()


def test_nothing_undecided_reaches_the_plan_file() -> None:
    style = text(STYLE)
    template = text(TEMPLATE)

    assert "Nothing undecided enters a plan file" in style
    assert "`plan.md` holds only content the author approved in chat" in template
    for source in (style, template):
        assert "no placeholders" in source
        assert "TODO" in source
        assert "TBD" in source


def test_an_unavailable_value_becomes_an_unvalued_point_not_a_question() -> None:
    planner = text(PLANNER)
    style = text(STYLE)
    template = text(TEMPLATE)

    assert (
        "Where the specific value or mechanics a point needs are not available, "
        "propose the point stating what it describes, without the value." in style
    )
    assert "carrying no question mark, no marker, and no invented value" in style
    assert "This holds at every level up to grounding." in style
    assert (
        "An unvalued point is approved content: it states what it describes, and "
        "enters the file as an ordinary point line that grounding later resolves."
        in planner
    )
    assert (
        "A point whose value is not yet available states what it describes, without "
        "the value, and is approved like any other point." in template
    )


def test_planner_never_hands_back_an_empty_list_for_the_author_to_fill() -> None:
    style = text(STYLE)

    assert "You always bring a candidate list." in style
    assert "empty list for the author to fill" in style
    assert "press the author for the material to cover it" in style
    assert (
        "A unit with no approved points carries its heading and its purpose line and "
        "nothing else." in style
    )


def test_stages_carry_semantic_names_and_level_correspondence() -> None:
    planner = text(PLANNER)
    style = text(STYLE)

    for heading in (
        "### Document planning",
        "### Section planning",
        "### Paragraph planning",
        "### Grounding",
        "### Grounded review",
        "### Parent sync",
    ):
        assert heading in planner
    for retired in (
        "### Phase 1",
        "### Phase 2",
        "### Phase 3",
        "### Phase 4",
        "### Phase 5",
        "### Phase 6",
        "Haggling and promotion",
        "Session close: parent sync",
    ):
        assert retired not in planner
    assert "haggl" not in planner.lower()
    assert "haggl" not in style.lower()

    assert "Each point is one child unit" in planner
    assert "Each point is one paragraph of the section or subsection in hand" in planner
    assert "Each point is one sentence of the paragraph in hand" in planner
    assert "Section and subsection are equivalent levels." in planner
    assert (
        "| Section/subsection [equivalent] | one paragraph of that section or "
        "subsection | paragraph order |" in style
    )
    assert "| Paragraph | one sentence of that paragraph | sentence order |" in style


def test_review_happens_on_every_presentation_rather_than_as_a_later_stage() -> None:
    style = text(STYLE)

    assert "Every presentation carries its review with it." in style
    assert "Reviewing is not a later stage" in style


def test_provenance_narration_is_not_required_during_planning() -> None:
    planner = text(PLANNER)
    style = text(STYLE)

    for source in (planner, style):
        assert "came from you rather than the author" not in source
        assert "verifies every sentence point regardless of origin" in source


def test_unresolved_points_index_is_generated_only_by_grounding() -> None:
    planner = text(PLANNER)
    template = text(TEMPLATE)
    reviewer = text(REVIEWER)

    assert "The grounding pass is its only author" in planner
    assert "It is not a route into the document" in planner
    assert (
        "every ID in it has both an approved point line in `plan.md` and a matching "
        "ledger entry" in planner
    )
    assert (
        "`## Unresolved points` is written only by the grounding pass, generated from "
        "the `evidence.md` entries at status `open`." in template
    )
    assert (
        "Every ID in it has both an approved point line in `plan.md` and a matching "
        "ledger entry." in template
    )
    assert "Check that index in both directions." in reviewer
    assert (
        "the index is generated from the ledger and introduces no content of its own"
        in reviewer
    )


def test_unsorted_candidate_bullets_are_no_longer_a_plan_shape() -> None:
    planner = text(PLANNER)
    template = text(TEMPLATE)

    assert "Loose bullet under a heading" not in template
    assert "candidate point not yet sorted into a paragraph" not in template
    assert "loose bullets are mid-sorting" not in planner
    assert (
        "Every shape in the file is approved content; unsorted or provisional material "
        "never appears there." in planner
    )


def test_both_distributions_carry_the_write_protocol() -> None:
    for built in DIST_PLANNERS:
        assert built.exists(), built
        content = text(built)
        assert "## What reaches a plan file" in content
        assert "nothing undecided enters it" in content
        assert "### Grounded review" in content
        assert "haggl" not in content.lower()


def test_the_codex_build_does_not_repeat_a_section_heading() -> None:
    """The inlined output style and the skill body must not share a heading."""

    built = ROOT / "dist" / "codex" / "thesis-writer" / "skills" / "document-planner" / "SKILL.md"
    headings = [
        line.strip()
        for line in built.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ") or line.startswith("### ")
    ]
    duplicates = {h for h in headings if headings.count(h) > 1}
    assert duplicates == set(), duplicates
