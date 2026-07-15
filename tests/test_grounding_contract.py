from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src" / "skills"


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_planner_is_research_interleaved_and_fail_closed() -> None:
    planner = text("src/skills/document-planner/body.md")
    for point_type in (
        "`CLAIM`",
        "`PROJECT_FACT`",
        "`DERIVATION`",
        "`AUTHOR_ASSERTION`",
        "`INFERENCE`",
        "`LINK`",
        "`PURPOSE`",
        "`OPEN`",
    ):
        assert point_type in planner
    assert "generate from whole cloth" not in planner.lower()
    assert "citation marking (after author approval)" not in planner.lower()
    assert "Do not create or append to `reference_debt.md`" in planner
    assert "No `OPEN` point is included in writer input" in planner
    assert "Do not generate a section's factual skeleton before research" in planner


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

    plan_format = planner.split("## Plan format", 1)[1].split("## Citation density", 1)[0]
    evidence_format = planner.split("## Evidence-ledger format", 1)[1].split("## Corpus gaps", 1)[0]
    assert "only a stable point ID plus status as machine metadata" in planner
    assert "Status: [draft|approved]" in plan_format
    for forbidden_header in (
        "Type: [background|research|conclusions|future-work]",
        "Structural status:",
        "Grounding status:",
        "Date: [YYYY-MM-DD]",
        "Parent: [parent plan path]",
    ):
        assert forbidden_header not in plan_format
    assert "Document type: [background|research|conclusions|future-work]" in evidence_format
    assert "Recorded: [YYYY-MM-DD]" in evidence_format
    assert "Parent plan: [parent plan path]" in evidence_format
    assert "[C03-S02-P01-CL01 | write-ready]" in plan_format
    assert "[embedded evidence card]" not in plan_format
    assert "Evidence: [file/data/code locator]" not in plan_format
    assert "Premises: [IDs]" not in plan_format

    for contract in (planner, writer, reviewer, style_guide, template):
        assert "`evidence.md`" in contract

    assert "`plan.md` is authoritative for what the thesis should say" in planner
    assert "`evidence.md` is authoritative for whether each planned point is grounded" in planner
    assert "The ledger may not add a point that is absent from its sibling plan" in planner
    assert "full gap record in the matching `evidence.md` entry" in planner


def test_writer_and_reviewer_fail_closed_on_plan_ledger_divergence() -> None:
    writer = text("src/skills/writer/body.md")
    reviewer = text("src/skills/reviewer/body.md")

    for failure in (
        "plan's author-visible `Status` is not `approved`",
        "no stable ID or status",
        "no exactly matching `evidence.md` entry",
        "orphan ID absent from `plan.md`",
        "status is not `write-ready`",
        "lacks its complete type-specific receipt",
        "do not semantically match the planned content",
    ):
        assert failure in writer
    assert "block-level `Grounding status`" not in writer

    for failure in (
        "without an ID or status",
        "missing ledger entry",
        "orphan ledger ID",
        "non-ready technical status",
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
