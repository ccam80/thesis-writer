from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src" / "skills"


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_planner_grounds_in_a_batch_pass_and_fails_closed() -> None:
    planner = text("src/skills/document-planner/body.md")
    assert "Every grounded sentence point takes exactly one type from the shared vocabulary" in planner
    assert "Nothing above sentence level is typed, and nothing is typed before grounding" in planner
    assert "Two statuses exist, recorded only in the point's ledger entry: `open` and `write-ready`" in planner
    assert "Mint IDs at grounding, never earlier" in planner
    assert "Phases 1–4 are ungrounded" in planner
    assert "grounding verifies every sentence point regardless of origin" in planner
    assert "Run grounding as a batch pass over the settled sentence plan" in planner
    assert "an `open` point gets no marker in `plan.md`" in planner
    assert "Do not create or append to `reference_debt.md`" in planner
    assert "No point below `write-ready` is included in writer input" in planner
    assert "generate from whole cloth" not in planner.lower()
    assert "citation marking (after author approval)" not in planner.lower()


def test_ungrounded_phases_carry_no_machine_fields_and_drift_is_not_blocking() -> None:
    planner = text("src/skills/document-planner/body.md")
    style = text("src/output-styles/writing-planner.md")
    template = text("src/templates/thesis-instructions.md")

    assert "They carry no IDs, no types, no statuses, and no ledger writes" in planner
    assert "divergence from the thesis plan is normal work product, not a conflict" in planner
    assert "update the thesis plan in a single approval batch" in planner
    assert "no sibling `evidence.md`" in planner
    assert "Planning is ungrounded until the grounding phase" in style
    assert "is normal work product" in style
    assert "permanently ungrounded" in template
    assert "Divergence is noted, never blocking" in template


def test_grounding_verifies_at_stated_precision_without_point_inflation() -> None:
    planner = text("src/skills/document-planner/body.md")
    research = text("src/skills/zotero-research/body.md")

    assert "Verify each point at the precision the plan states" in planner
    assert "A point is supported when its wording is entailed" in planner
    assert "Do not add, split, or widen points during grounding" in planner
    assert "Verify the proposition at the precision it states" in research
    assert "it is supported when its wording is entailed" in research
    assert "Never add, split, or widen propositions" in research


def test_point_vocabulary_is_shared_and_retired_names_are_gone() -> None:
    template = text("src/templates/thesis-instructions.md")
    style_guide = text("src/skills/writer/references/thesis-style-guide.md")

    for point_type in (
        "`CLAIM`",
        "`PROJECT_FACT`",
        "`DERIVATION`",
        "`AUTHOR_ASSERTION`",
        "`INFERENCE`",
    ):
        assert point_type in template
        assert point_type in style_guide
    assert "This vocabulary is shared by every skill" in template
    assert "Two statuses exist, recorded only in `evidence.md`" in template
    assert "Only `write-ready` reaches the writer" in template
    assert "Only a grounded sentence point carries an ID" in template

    contracts = (
        "src/skills/document-planner/body.md",
        "src/skills/writer/body.md",
        "src/skills/reviewer/body.md",
        "src/skills/zotero-research/body.md",
        "src/skills/zotero-source-acquisition/body.md",
        "src/skills/writer/references/thesis-style-guide.md",
        "src/templates/thesis-instructions.md",
        "src/output-styles/writing-planner.md",
    )
    for retired in (
        "`LINK`",
        "`PURPOSE`",
        "`OPEN`",
        "agent-proposed",
        "author-proposed",
        "`accepted`",
        "| write-ready]",
        "| accepted]",
        "PHYS-S0",
    ):
        for contract in contracts:
            assert retired not in text(contract), f"{retired!r} found in {contract}"


def test_research_contract_keeps_passages_with_multisource_claims() -> None:
    research = text("src/skills/zotero-research/body.md")
    assert "Never search the web" in research
    assert "#### Supporting evidence" in research
    assert "#### Qualifying evidence" in research
    assert "#### Contradicting evidence" in research
    assert "Every synthesis must be followed immediately by the passages" in research
    assert "Do not stop after finding one convenient citation" in research
    assert "Context-only" in research


def test_writer_and_reviewer_require_complete_traceability() -> None:
    writer = text("src/skills/writer/body.md")
    reviewer = text("src/skills/reviewer/body.md")
    assert "<target-stem>.claim-map.md" in writer
    assert "scripts/lint_prose.py" in writer
    assert "three to five nearby author-written paragraphs" in writer
    assert "Review every sentence and every plan point" in reviewer
    assert 'Sampling "critical" claims is prohibited' in reviewer
    assert "never `chapter_plan.md`" in writer
    assert "Never request `chapter_plan.md`" in reviewer
    assert "TODO" not in reviewer


def test_plan_is_author_readable_and_provenance_lives_in_evidence_ledger() -> None:
    planner = text("src/skills/document-planner/body.md")
    writer = text("src/skills/writer/body.md")
    reviewer = text("src/skills/reviewer/body.md")
    style_guide = text("src/skills/writer/references/thesis-style-guide.md")
    template = text("src/templates/thesis-instructions.md")

    plan_format = planner.split("## Plan grammar", 1)[1].split("## Phases", 1)[0]
    evidence_format = planner.split("## Evidence-ledger format", 1)[1].split("## Corpus gaps", 1)[0]
    assert "Plan points carry only their text, a bracketed stable ID, and approved citation" in style_guide
    assert "A grounded point line carries only its text, bracketed ID, and approved citation keys" in template
    assert "Put document type, date, parent path, grounding bookkeeping" in template
    assert "Add no block-level or file-level status field" in plan_format
    for forbidden_header in (
        "Type: [background|research|conclusions|future-work]",
        "Status: [draft|approved]",
        "Structural status:",
        "Grounding status:",
        "Date: [YYYY-MM-DD]",
        "Parent: [parent plan path]",
    ):
        assert forbidden_header not in plan_format
    assert "Document type: [background|research|conclusions|future-work]" in evidence_format
    assert "Recorded: [YYYY-MM-DD]" in evidence_format
    assert "Parent plan: [thesis plan path]" in evidence_format
    assert "**Status:** open | write-ready" in evidence_format
    assert "[PHYS-041]" in plan_format
    assert "| write-ready]" not in plan_format
    assert "[embedded evidence card]" not in plan_format
    assert "Evidence: [file/data/code locator]" not in plan_format
    assert "Premises: [IDs]" not in plan_format

    for contract in (planner, writer, reviewer, style_guide, template):
        assert "`evidence.md`" in contract

    assert "`plan.md` is authoritative for intended content and structure" in template
    assert "`evidence.md` is authoritative for grounding" in template
    assert "may not introduce an absent point or change planned meaning" in template
    assert "the single grounding authority, not a second content plan" in planner
    assert "full gap record in the matching `evidence.md` entry" in planner


def test_writer_and_reviewer_fail_closed_on_plan_ledger_divergence() -> None:
    writer = text("src/skills/writer/body.md")
    reviewer = text("src/skills/reviewer/body.md")

    for failure in (
        "a sentence point has no stable ID",
        "a plan point has no exactly matching `evidence.md` entry",
        "orphan ID absent from `plan.md`",
        "a point's ledger status is not `write-ready`",
        "a point lacks its complete type-specific receipt",
        "do not semantically match the planned content",
    ):
        assert failure in writer
    assert "Do not repair these failures by inferring a type, receipt, status, or intended meaning" in writer
    assert "block-level `Grounding status`" not in writer

    for failure in (
        "without an ID",
        "missing ledger entry",
        "orphan ledger ID",
        "ledger status below `write-ready`",
        "incomplete type-specific receipt",
        "semantic mismatch",
    ):
        assert failure in reviewer
    assert "Reject any content introduced only by `evidence.md`" in reviewer


def test_source_acquisition_is_a_separate_exact_approval_lane() -> None:
    skill_dir = SKILLS / "zotero-source-acquisition"
    assert (skill_dir / "skill.yaml").is_file()
    assert (skill_dir / "body.md").is_file()
    assert not (skill_dir / "SKILL.md").exists()
    body = (skill_dir / "body.md").read_text(encoding="utf-8")
    assert "do not state that a candidate supports" in body
    assert "Import nothing until the user explicitly approves exact candidate IDs" in body
    assert "Leave every shortlisted candidate" in body
    assert "CAPTCHA" in body
    assert "Delete the created attachment first" in body
    assert "Then hand the claim IDs" in body


def load_linter():
    path = SKILLS / "writer" / "scripts" / "lint_prose.py"
    spec = importlib.util.spec_from_file_location("lint_prose", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_prose_linter_flags_model_voice_without_flagging_clean_prose() -> None:
    linter = load_linter()
    findings = linter.lint_text(
        "Crucially, this section discusses a very robust method --- which unlocks performance --- in practice?"
    )
    rules = {finding["rule"] for finding in findings}
    assert {"sentence-adverb", "meta-narration", "importance-modifier", "em-dash", "kill-list", "rhetorical-question"} <= rules
    assert linter.lint_text("The filter settles within \\SI{40}{\\milli\\second}.") == []
