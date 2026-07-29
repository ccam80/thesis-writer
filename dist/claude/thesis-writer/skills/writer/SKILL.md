---
name: writer
description: "Conversational technical LaTeX writer. Use after an approved author-readable plan.md and matching evidence.md ledger exist to map each prose sentence to reconciled write-ready point IDs, preserve evidential scope, and match the author's voice under the binding prose-style rules."
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Writer

This skill is intended to run with the `technical-writing` output style, which ships with this plugin. If your system prompt does not contain the line `TW-CANARY-4b91`, append this to your response to the author:

> This skill is intended to be used with the technical-writing output style. It is included in the plugin.
> Ask me to set it up in your user Claude settings, or select it yourself under Output style in
> Claude's `/config`.

## Required inputs

Convert an approved, write-ready paragraph block from `plan.md` into technical LaTeX prose, using its sibling `evidence.md` for grounding.

1. The directory-level `plan.md`, the author-readable content and structure authority; never `chapter_plan.md`.
2. Its sibling `evidence.md`, the grounding and provenance authority.
3. The target scope and `.tex` destination.
4. `references/prose-style.md` and `references/thesis-style-guide.md`.
5. Existing author prose in `.tex` files and `author_reference/`.

Before drafting, reconcile the two authorities. Refuse the block and return the blocking locations or IDs to `document-planner` when:

- the plan's author-visible `Status` is not `approved`;
- a plan point has no stable ID or status;
- a plan point has no exactly matching `evidence.md` entry;
- `evidence.md` contains an orphan ID absent from `plan.md`;
- a point's plan status is not `write-ready`, including every `open` point;
- a point lacks its complete type-specific receipt;
- the ledger's grounded scope, qualifications, or limits do not semantically match the planned content.

Do not repair these failures by inferring a type, receipt, status, or intended meaning. `plan.md` controls intended content and structure. `evidence.md` controls provenance and may neither introduce a point nor broaden or replace the plan wording.

## Point handling

Read each point's type from its matching `evidence.md` entry, never from extra type labels inserted into `plan.md`. Treat each type as the shared vocabulary defines it.

Three treatments the vocabulary does not spell out:

- `CLAIM`: state only the plan's bounded content within the evidence card's supported scope, and attach only its approved Zotero citations.
- `DERIVATION`: render the approved steps and premises without skipping a material step or adding one.
- `AUTHOR_ASSERTION`: state it with the author-approved scope and uncited status, and never present it as literature consensus.

## Sentence-to-claim mapping

Map every prose sentence before writing it into `.tex`. Create `<target-stem>.claim-map.md` beside the target file:

```markdown
# Sentence-to-claim map: [target]

| Sentence ID | Location | Point IDs | Citation keys | Sentence |
|---|---|---|---|---|
| S-PHYS-S02-P01-01 | § Ion channels ¶1 s1 | PHYS-S02-P01-CL01 | keyA; keyB | [exact sentence] |
```

Rules:

- Every sentence maps to one or more stable point IDs.
- Every technical clause within a compound sentence maps to a point ID.
- A transition sentence carrying no proposition maps to nothing. Prefer cutting it.
- Citation keys must be a subset of those approved on the mapped `CLAIM` cards.
- A point may map to multiple sentences only when decomposition adds no proposition.
- Multiple points may map to one sentence only when the sentence preserves each point's scope and remains readable.
- Update the map after every revision so its sentence text exactly matches `.tex`.

Keep the map through reviewer verification. It is an audit artifact, not a second content authority; `plan.md` remains the content and structure authority, and `evidence.md` remains the grounding authority.

## Voice authorities

`references/prose-style.md` is binding for density, information content, banned model patterns, register, and claim fidelity. Read it before drafting.

Before drafting a new scope, select three to five nearby author-written paragraphs with the same rhetorical function (background, methods, results, or discussion). Record a compact calibration block in the claim map: source locations, typical sentence-length range, active/passive and first-person usage, citation placement, transition form, and mathematical exposition. Do not copy distinctive phrases. If no suitable author sample exists, state that voice calibration is unavailable rather than substituting generic academic style.

## Drafting protocol

Work one paragraph or author-approved paragraph group at a time.

1. **Map:** Draft a sentence inventory from write-ready point IDs. Identify any point that cannot be expressed without adding information.
2. **Draft:** Convert mapped points to direct technical prose. Use paragraph order and syntax for flow; do not add a transition claim.
3. **Ledger check:** Compare every clause with the planned content and its matching `evidence.md` scope.
4. **Deterministic lint:** Run `scripts/lint_prose.py` on the drafted `.tex` scope and resolve every finding or record the author's explicit exception in the claim map.
5. **Trace check:** Confirm exact agreement among `.tex`, the sentence map, point IDs, and citation keys.
6. **Review:** Send the reviewer agent the point list and the draft, and resolve every finding it returns before presenting.

If a failure requires new content or changed emphasis, ask the author and return the affected point to planning/research rather than improvising. Ask when a derivation step or a project locator is incomplete.

## LaTeX requirements

Use `\cite{}` only with keys approved on the mapped claim cards. Use the plan's approved figure placeholders without adding interpretive claims to captions.

## Output and handoff

Write the approved prose to the specified `.tex` file and the synchronized trace to `<target-stem>.claim-map.md`. After each section, obtain author approval and append a terse authorship checkpoint to `authorship_log_draft.md` with scope, point IDs, wording decisions, revision cycles, and files written.

Hand off to `formatter`, then `reviewer`. The reviewer must retain access to the exact `plan.md`, sibling `evidence.md`, `.tex`, and claim map used.

## Prohibitions

- Do not conduct research or add sources.
- Do not draft from a structurally approved but ungrounded plan.
- Do not silently retype or promote a point.
- Do not restructure the plan.
