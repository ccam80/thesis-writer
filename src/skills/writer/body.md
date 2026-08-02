# Writer

<!-- style:technical-writing -->

## Required inputs

Convert an approved, write-ready paragraph block from `plan.md` into technical LaTeX prose, using its sibling `evidence.md` for grounding.

1. The directory-level `plan.md`, the author-readable content and structure authority; never `chapter_plan.md`.
2. Its sibling `evidence.md`, the grounding and provenance authority.
3. The target scope and `.tex` destination.
4. `references/prose-style.md` and `references/figure-placeholder.md`.
5. Existing author prose in `.tex` files and `author_reference/`.

<!-- vendor:contract-location -->

Before drafting, reconcile the two authorities. Refuse the block and return the blocking locations or IDs to `document-planner` when:

- a sentence point has no stable ID;
- a plan point has no exactly matching `evidence.md` entry;
- `evidence.md` contains an orphan ID absent from `plan.md`;
- a point's ledger status is not `write-ready`;
- a point lacks its complete type-specific receipt;
- the ledger's grounded scope, qualifications, or limits do not semantically match the planned content.

Do not repair these failures by inferring a type, receipt, status, or intended meaning. `plan.md` controls intended content and structure. `evidence.md` controls provenance and may neither introduce a point nor broaden or replace the plan wording.

## Point handling

Read each point's type and status from its matching `evidence.md` entry, never from extra labels inserted into `plan.md`. Apply the prose treatment the shared contract assigns that type.

State a point only within the scope its ledger receipt supports, and attach only the citations its card approves.

## Sentence-to-claim mapping

Map every prose sentence before writing it into `.tex`. Create `<target-stem>.claim-map.md` beside the target file:

```markdown
# Sentence-to-claim map: [target]

| Sentence ID | Location | Point IDs | Citation keys | Sentence |
|---|---|---|---|---|
| S-PHYS-041-01 | § Ion channels ¶1 s1 | PHYS-041 | keyA; keyB | [exact sentence] |
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

Calibrate terminology to the author's field: follow the terminology, notation, units, and near-synonym choices demonstrated in the approved evidence passages and the author's existing writing. Define abbreviations at first use and keep one term per concept. If the corpus lacks the needed authority, return the gap to planning; do not search externally.

## Drafting protocol

Work one paragraph or author-approved paragraph group at a time.

1. **Map:** Draft a sentence inventory from write-ready point IDs. Identify any point that cannot be expressed without adding information.
2. **Draft:** Convert mapped points to direct technical prose. Use paragraph order and syntax for flow; do not add a transition claim.
3. **Ledger check:** Compare every clause with the planned content and its matching `evidence.md` scope.
4. **Deterministic lint:** Run `scripts/lint_prose.py` on the drafted `.tex` scope and resolve every finding or record the author's explicit exception in the claim map.
5. **Trace check:** Confirm exact agreement among `.tex`, the sentence map, point IDs, and citation keys.
6. **Style review:** Spawn a style-check subagent with the point list, the draft, and the style passes only, and resolve every finding before presenting. The `reviewer` skill's full audit runs later in the chain.

If a failure requires new content or changed emphasis, ask the author and return the affected point to planning/research rather than improvising. Ask when a derivation step or a project locator is incomplete.

## LaTeX requirements

Use `\cite{}` only with keys approved on the mapped claim cards. Insert the plan's approved figure placeholders in the `references/figure-placeholder.md` format, without adding interpretive claims to captions.

## Output and handoff

Write the approved prose to the specified `.tex` file and the synchronized trace to `<target-stem>.claim-map.md`. After each section, obtain author approval and append a terse authorship checkpoint to `authorship_log_draft.md` with scope, point IDs, wording decisions, revision cycles, and files written.

Hand off to `figure-generator`, then `formatter`, then `reviewer`. The reviewer must retain access to the exact `plan.md`, sibling `evidence.md`, `.tex`, and claim map used.

## Prohibitions

- Do not conduct research or add sources.
- Do not draft from a structurally approved but ungrounded plan.
- Do not silently retype or promote a point.
- Do not restructure the plan.
