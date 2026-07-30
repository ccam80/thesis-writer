---
name: document-planner
description: "Interactive top-down planning at thesis, chapter, section, paragraph, and sentence scope. Use to draft author-readable plan.md files narratively down to sentence points, then ground the settled sentence plan in a batch Zotero research pass that builds the chapter's claim-addressable evidence.md ledger for author haggling."
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Document Planner

This skill is intended to run with the `writing-planner` output style, which ships with this plugin. If your system prompt does not contain the line `WP-CANARY-2c7d`, append this to your response to the author:

> This skill is intended to be used with the writing-planner output style. It is included in the plugin.
> Ask me to set it up in your user Claude settings, or select it yourself under Output style in
> Claude's `/config`.

## Inputs and authority

Plan thesis documents from thesis scope down to sentence scope, keeping every `plan.md` readable and editable as a document. Structure, reader-state transitions, purposes, research questions, and placement are yours to propose. The facts are the author's or the corpus's.

**CRITICAL — Zotero access policy**: NEVER call `mcp__deep-zotero__*` tools directly. All Zotero library access MUST go through the `zotero-research` agent, spawned via the Task tool. Only the `zotero-research` agent is permitted to call the MCP tools.

Read, in this order:

1. The target `.tex` file. Existing prose is authoritative for existing content.
2. The chapter `plan.md`. This is the author-readable content and structure authority.
3. The sibling `evidence.md`, once grounding has begun. This is the grounding and provenance authority for the point IDs in the chapter plan.
4. The thesis `plan.md`. It sets narrative goals and scope.
5. Existing project evidence named by the author: data, code, laboratory notes, methods records, figures, or calculations.

Existing `.tex` content cannot be removed without explicit discussion.

On entering an existing chapter, report what `.tex`, the chapter plan, and the thesis plan already contain and where they disagree. Treat plan-to-plan disagreements as divergence-list items for the session-close sync, not as blockers.

## Plan tiers

Exactly two plan tiers exist.

The thesis `plan.md` holds each chapter, its content in a few sentences, and its section breakdown, with subsections where useful. It is narratively haggled and permanently ungrounded: no IDs, no statuses, no types, and no sibling `evidence.md`. A number or claim in it is assumed-to-be-grounded and is verified only when the owning chapter reaches its grounding pass.

Each chapter directory holds one `plan.md` carrying the chapter down to sentence points and, once grounding begins, one sibling `evidence.md` ledger. There are no deeper plan files.

## Plan grammar

Stage is encoded by shape, not labels. In a chapter `plan.md`:

- Prose under a heading is summary and purpose. It is never grounded and emits no sentence.
- A bold `**¶ [label]** — [paragraph point]` line is a paragraph point.
- A bullet nested under a `¶` line is a sentence point. Only sentence points are ever grounded.
- A loose bullet under a heading, outside any `¶` line, is a candidate point not yet sorted into a paragraph.

Read a half-done chapter's state from shape alone: a section with only prose has not been pointed; loose bullets are mid-sorting; a `¶` line without bullets is not yet expanded; a `¶` line with bullets has its sentence plan; a bullet ending in a bracketed ID has entered grounding.

```markdown
# Plan: [Title]

## Narrative thread
[Author-approved narrative]

## [Section title]
[One or two prose sentences: what the section covers and does.]

**¶ [label]** — [paragraph point]
- [sentence point]
- [sentence point] [PHYS-041] \cite{keyA,keyB}

**¶ [label]** — [paragraph point, not yet expanded]

- [candidate point not yet sorted into a paragraph]

→ **Figure:** [descriptive label and specification]

## Unresolved points
[Optional readable index of open point IDs and their bounded questions; full gap records live only in `evidence.md`]
```

Number no heading; refer to a unit by directory and heading. The plan header carries the title only. Keep document type, recording date, parent path, and grounding bookkeeping in `evidence.md`. Add no block-level or file-level status field; readiness reconciles each grounded point with its ledger receipt.

## Phases

Phases 1–4 are ungrounded. They carry no IDs, no types, no statuses, and no ledger writes. Their points are narrative drafts: propose candidate facts from the discussion or from general knowledge freely; grounding verifies every sentence point regardless of origin. Say in chat when a specific number or result came from you rather than the author, then continue. Do not run research, police provenance, or raise grounding vocabulary during these phases. The factual skeleton is haggled with the author, not generated by research.

Settle one phase at a time; advance on the author's request.

### Phase 1: Thesis plan

Haggle the chapter list, each chapter's content in a few sentences, and its section breakdown. Present a compact visual chain for narrative order, for example:

```text
[Feedback vocabulary] → [Sensor and actuator paths] → [Controller design] → [Robustness limits]
```

Check cross-chapter duplication and record agreed ownership in the thesis plan.

### Phase 2: Chapter structure

Fix the chapter's sections and subsections, then add and sort candidate points into them to establish narrative and flow. Points move, split, merge, appear, and disappear freely. Nest below subsection level only on the author's request.

### Phase 3: Paragraph points

Organise each section's material into `¶` lines, one point per paragraph, establishing order and coverage. Keep visible, as prose or in the point itself, what each paragraph needs from its predecessors and any figure or cross-reference opportunity.

### Phase 4: Sentence points

Expand each `¶` line into bullets, one point per sentence. Terseness cuts words, not scope: a qualification that is part of the fact stays in the point. Where the author cannot supply content, put a bounded question in place of a point; do not invent a specific result to fill the gap.

### Phase 5: Grounding

Run grounding as a batch pass over the settled sentence plan, one section at a time, on the author's request.

1. Pull down into a sentence bullet any factual content in prose or a `¶` line that must survive into the written paragraph. Grounding covers only sentence bullets.
2. Mint IDs for every sentence point in scope.
3. Assign each point exactly one type from the shared vocabulary and create its ledger entry with status `open`.
4. Send the section's claims and questions to `zotero-research` in batches. Require for every claim: a claim-centred card; all materially relevant supporting, qualifying, and contradicting passages found; BetterBibTeX key, item title, page/section or chunk locator, and an immediate verbatim passage for every cited item; an entailment note; a search receipt.
5. Verify each point at the precision the plan states. A point is supported when its wording is entailed, even where the passage is more specific. Propose rewording only when the evidence contradicts or cannot support the wording as written. Do not add, split, or widen points during grounding; record the finding on the card and raise it in haggling.
6. Record verdicts and type-specific receipts in `evidence.md`.

The research worker synthesizes across retrieved passages; the planner must not strengthen that synthesis.

### Phase 6: Haggling and promotion

Present grounding results per section as a digest: points supported as written; points needing narrowing, each with a proposed rewording; contested points with both sides; refuted points; corpus gaps. The author decides wording, splits, additions, and removals. Any rewording that exceeds the passages' entailment goes back through `zotero-research`.

Where sources disagree, retain the conflict in the card and propose contested wording. Never select only the convenient side. A reworded point preserves negation, modality and uncertainty, population or system, operating conditions, quantities and units, comparison class, correlation versus causation, and temporal and spatial bounds.

Iterate until the author accepts each point's grounded wording; acceptance flips its ledger status to `write-ready`. Wording changes after promotion reopen the point.

### Session close: parent sync

Lower-level planning is expected to change content; divergence from the thesis plan is normal work product, not a conflict. During the session, keep a short running divergence list and never block on it. At session close, or when the author asks, present the list once and update the thesis plan in a single approval batch.

## Stable IDs

Mint IDs at grounding, never earlier. Use the chapter directory's slug plus an opaque serial:

- `PHYS-041`
- `CUBIE-007`

The ID encodes no section, paragraph, or type and never changes on reorder. Never reuse an ID. When one point splits, the surviving proposition keeps the ID and additional propositions get new IDs. When points merge, retain all contributing IDs as aliases. IDs persist from grounded plan through prose and review.

## Types and statuses

Every grounded sentence point takes exactly one type from the shared vocabulary. Nothing above sentence level is typed, and nothing is typed before grounding. Type lives in `evidence.md`, never in `plan.md`.

Two statuses exist, recorded only in the point's ledger entry: `open` and `write-ready`. A plan line carries only its text, its bracketed ID, and any approved `\cite{}` keys; an `open` point gets no marker in `plan.md`. The optional `## Unresolved points` index is the plan's only readable view of open points. Only `write-ready` points reach the writer.

## Write-ready invariant

A point becomes `write-ready` only when:

- Its ledger entry carries its complete type-specific receipt.
- Every `CLAIM` has an approved evidence card containing at least one supporting passage.
- Every `PROJECT_FACT` has a precise project locator.
- Every `DERIVATION` names grounded premises and has checked steps.
- Every `AUTHOR_ASSERTION` records explicit author attestation.
- Every `INFERENCE` names grounded premises and states its inferential limits.
- Contradicting and qualifying evidence remains attached and is reflected in the point wording.
- The wording does not exceed the scope its evidence supports.
- The author has accepted the grounded wording.

Fail closed. A structurally settled plan is not a grounded one. No point below `write-ready` is included in writer input.

## Evidence-ledger format

Keep all provenance in the sibling `evidence.md`. This is the single grounding authority, not a second content plan and not a `reference_debt.md` replacement. Entries are keyed by IDs already present in `plan.md`.

```markdown
# Evidence: [Title]
Plan: [sibling plan path]
Document type: [background|research|conclusions|future-work]
Recorded: [YYYY-MM-DD]
Parent plan: [thesis plan path]

## PHYS-041

**Type:** CLAIM
**Status:** open | write-ready
**Research request:** [request ID]
**Grounded scope:** [single bounded synthesis matching, without broadening, the planned content]

#### Supporting evidence
- `keyA` — [item title], p. 42, [section/chunk]
  > "[shortest complete verbatim supporting passage]"
  Entailment: [supported content and limits]
- `keyB` — [item title], p. 118, [section/chunk]
  > "[verbatim passage]"
  Entailment: [supported content and limits]

#### Qualifying evidence
- `keyC` — [item title], p. 9, [section/chunk]
  > "[verbatim passage]"
  Qualification: [how the claim must be narrowed]

#### Contradicting evidence
- `keyD` — [item title], p. 27, [section/chunk]
  > "[verbatim passage]"
  Conflict: [opposing result and differing conditions]

**Search receipt:** [tools, queries, retrieval depth, results inspected]
```

List `None found` under an empty evidence class. "All" means all materially relevant results the recorded searches returned.

Use the same entry envelope for every point type. `PROJECT_FACT`, `DERIVATION`, `AUTHOR_ASSERTION`, and `INFERENCE` entries contain their type-specific locators, steps, attestations, premises, warrants, and limits. Every entry carries a receipt. Do not put these fields, evidence-card bodies, quotations, research-request details, search receipts, premise bookkeeping, or attestations in `plan.md`.

```markdown
## [point ID]
**Type:** PROJECT_FACT | DERIVATION | AUTHOR_ASSERTION | INFERENCE
**Status:** open | write-ready
**Grounded scope:** [scope that semantically matches the plan item]
**Receipt:** [exact project locator | premise IDs and checked steps | dated author attestation | premise IDs, warrant, and limits]
```

## Corpus gaps and non-Zotero facts

Keep an unresolved point visible and readable: its plan line stays in place unmarked, and its ID and bounded question appear in the `## Unresolved points` index. Keep its full gap record in the matching `evidence.md` entry:

```markdown
## PHYS-043
**Type:** CLAIM
**Status:** open
**Scope:** [scope that semantically matches the plan item]
**Zotero search receipt:** [...]
**Missing evidence:** [...]
**Resolution:** project evidence | author attestation | source acquisition | revision | removal
```

Do not create or append to `reference_debt.md`. A derived summary of unresolved IDs is allowed only as a generated view; `plan.md` remains the content authority and `evidence.md` remains the grounding authority.

Resolution lanes:

1. Attach exact project evidence and retype as `PROJECT_FACT`.
2. Obtain explicit author attestation and retype as `AUTHOR_ASSERTION`.
3. Hand off to the separate `zotero-source-acquisition` skill to locate candidate primary sources, obtain user approval, and import approved sources with PDFs into Zotero. After import and indexing, send the claim back to `zotero-research`.
4. Narrow or remove the point.

The planner and `zotero-research` must never fetch or import external sources themselves. A source-acquisition recommendation is not evidence and does not make a point write-ready.

## Citation density

Background chapters usually contain more `CLAIM` points; methods and results usually contain more `PROJECT_FACT` and `DERIVATION` points. Conclusions should derive from earlier claim and project-fact IDs rather than introduce new propositions.

## Authorship checkpoints

After the author approves a phase for a scope (structure, paragraph points, sentence points, or a grounded block), silently append a terse entry to `authorship_log_draft.md` containing:

- scope and phase;
- author decisions and rejections;
- for grounded scopes only: point IDs added, changed, removed, or retyped; provenance counts by point type; research request IDs; corpus gaps;
- files written;
- revision-cycle count.

Ungrounded-phase checkpoints carry no per-type provenance. Do not checkpoint clarification or mechanical research calls. Preserve working state until the block is committed; then remove temporary scratch files.

## Integration and autonomy

- Uses `zotero-research` only for the indexed Zotero corpus, and only in the grounding and haggling phases.
- Hands corpus gaps to `zotero-source-acquisition`; imported material returns through `zotero-research` before promotion.
- Produces the thesis `plan.md` and, per chapter, paired `plan.md` and `evidence.md` authority documents.
- Hands only write-ready points with their matching ledger entries to `writer`.

Run the grounding pass only on the author's request over an agreed scope. Do not promote a point, retype an author assertion, or write either authority document without author approval.
