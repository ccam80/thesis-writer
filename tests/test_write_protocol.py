from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PLANNER = ROOT / "src" / "skills" / "document-planner" / "body.md"
STYLE = ROOT / "src" / "output-styles" / "writing-planner.md"
TEMPLATE = ROOT / "src" / "templates" / "thesis-instructions.md"
REVIEWER = ROOT / "src" / "skills" / "reviewer" / "body.md"
WRITER = ROOT / "src" / "skills" / "writer" / "body.md"
AGENTS = ROOT / "AGENTS.md"
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
        assert "no open questions" in source.lower()
        assert "no inferred targets" in source
        assert "TODO" in source
        assert "TBD" in source


def test_a_deferred_value_has_a_grammar_shape_legal_in_any_plan_line() -> None:
    planner = text(PLANNER)
    style = text(STYLE)
    template = text(TEMPLATE)

    assert (
        "| `[[what the author will supply]]` in any line | Deferral. The line is "
        "approved; the value is outstanding. |" in template
    )
    assert "- settling time below [[value to be measured]]" in template
    assert (
        "A deferral records the author's decision to supply a value later. It may "
        "appear in any line." in template
    )
    assert (
        "A value the author has decided to supply later is not undecided; it is "
        "written as a deferral." in template
    )
    assert (
        "A value the author has decided to supply later is decided content: write it "
        "as a deferral, [[what they will supply]], where the value belongs, approved "
        "in chat like any other line." in style
    )
    assert (
        "A deferral is approved content: the author has decided the line and will "
        "supply its value later, and grounding resolves it." in planner
    )
    assert "a line holding a `[[deferral]]` awaits its value" in planner
    assert (
        "Where the author defers a value, write the point with a deferral in place "
        "of it, per the write protocol." in planner
    )
    # Nothing in the protocol bans the deferral shape or names it "unvalued".
    assert "no bracketed gap" not in style
    assert "unvalued" not in style
    assert "unvalued" not in planner


def test_a_deferral_never_reaches_prose() -> None:
    planner = text(PLANNER)
    template = text(TEMPLATE)
    writer = text(WRITER)
    reviewer = text(REVIEWER)
    style = text(STYLE)

    assert (
        "A point holding a deferral is never `write-ready`. Grounding replaces the "
        "deferral with its value, or the point stays `open`." in template
    )
    assert "Its line holds no deferral." in planner
    assert (
        "including any deferral it carries" in planner
    )
    assert "Grounding resolves it; until then no point carrying one is write-ready." in style
    assert "a sentence point or element line in the block holds a deferral;" in writer
    assert (
        "any deferral in a `write-ready` point or in `.tex`" in reviewer
    )
    assert "A deferral in an `open` point is normal." in reviewer


def test_a_missing_claim_is_a_question_not_a_deferral() -> None:
    planner = text(PLANNER)
    style = text(STYLE)
    template = text(TEMPLATE)

    assert "The deferral is the author's." in style
    assert (
        "Where you cannot state what a point asserts you have no value to defer: ask."
        in style
    )
    assert (
        "A vague line, an unsourceable attribution, or a deferral covering your own "
        "gap is not a point." in style
    )
    assert (
        "Its substance is the author's; a point you cannot state stays a chat question."
        in planner
    )
    assert (
        "It is never a substitute for content the agent cannot state; where the claim "
        "itself is unknown, it is a question for the author, not a line in the file."
        in template
    )
    assert "a deferral withholds a value, never the decision" in style
    assert "A deferred value is not a question." in style


def test_the_repository_contract_records_the_deferral_boundary() -> None:
    agents = text(AGENTS)

    assert (
        "`plan.md` carries no machine field beyond bracketed IDs, citation keys, and "
        "author deferrals" in agents
    )
    assert (
        "never originated by the agent to cover content it cannot state, and never "
        "`write-ready`" in agents
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
        assert "A deferral is approved content" in content
        assert "Its line holds no deferral." in content
        assert "unvalued" not in content


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
