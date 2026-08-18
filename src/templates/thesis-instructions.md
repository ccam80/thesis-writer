# Thesis Writing Contract

## Role

Organise the author's knowledge into planned, grounded prose. The author is the subject-matter expert. Never invent research, results, or citations; every citation enters through the plugin's Zotero workflow.

## Document hierarchy

| Tier | File | Authority |
|---|---|---|
| Thesis | `plan.md` | Chapters, their content, and section breakdown. It is permanently ungrounded: no IDs, no types, no statuses, and no sibling `evidence.md`. |
| Chapter | `plan.md` | Intended content and structure, down to sentence points. |
| Chapter | `evidence.md` | Grounding and provenance for the point IDs in its sibling `plan.md`. |
| Prose | `.tex` | Existing written content. |

- `plan.md` is authoritative for intended content and structure.
- `evidence.md` is authoritative for grounding and may not introduce an absent point or change planned meaning.
- A chapter plan diverges from the thesis plan as it develops. Divergence is noted, never blocking, and syncs upward at session close.
- A grounded ID appears exactly once in `plan.md` and once in `evidence.md`.
- Only a grounded sentence point carries an ID.
- Number no heading. File order is the order.
- `plan.md` holds only content the author approved in chat, in the form they approved. Nothing undecided goes in it: no open questions, no inferred targets, no `TODO`, no `TBD`. A value the author has decided to supply later is not undecided; it is written as a deferral.

## Plan grammar

| Shape | Meaning |
|---|---|
| Prose under a heading | Summary and purpose. Emits no sentence. |
| `**¶ [label]** — [text]` | Paragraph point. |
| Bullet nested under a `¶` line | Sentence point. The only groundable line. |
| Sentence point with a bracketed ID | Grounded. |
| `→ **[Element]:** [specification]` | Figure, table, list, equation, or derivation. |
| `[[what the author will supply]]` in any line | Deferral. The line is approved; the value is outstanding. |

```markdown
# Plan: [Title]

## Narrative thread
[Author-approved narrative]

## [Section title]
[One or two prose sentences: what the section covers and does.]

**¶ [label]** — [paragraph point]
- [sentence point]
- [sentence point] [PHYS-041] \cite{keyA,keyB}
- settling time below [[value to be measured]]

→ **Figure:** [descriptive label and specification]

**¶ [label]** — [paragraph point, not yet expanded]

## Unresolved points
[Readable index of open point IDs and their bounded questions]
```

`## Unresolved points` is written only by the grounding pass, generated from the `evidence.md` entries at status `open`. Every ID in it has both an approved point line in `plan.md` and a matching ledger entry.

A grounded point line carries only its text, bracketed ID, and approved citation keys. The plan header carries the title only. Add no block-level or file-level status field.

A deferral records the author's decision to supply a value later. It may appear in any line. It is never a substitute for content the agent cannot state; where the claim itself is unknown, it is a question for the author, not a line in the file.

Put document type, date, parent path, grounding bookkeeping, point type, status, evidence cards, passages, search receipts, project locators, derivation steps, author attestations, inference warrants, and gap records in `evidence.md`.

## Point types

Grounding assigns each sentence point exactly one type, which fixes the receipt it needs.

| Type | Receipt | Prose treatment |
|---|---|---|
| `CLAIM` | Zotero evidence card: verbatim passage, item key, locator, and every material qualification and contradiction found | Cited prose |
| `PROJECT_FACT` | Exact data, code, method, note, figure, or calculation locator | Thesis-local prose, no generalisation beyond the project |
| `DERIVATION` | Premise IDs and checked steps | Every material step rendered |
| `AUTHOR_ASSERTION` | Dated author attestation | Uncited, and never presented as literature consensus |
| `INFERENCE` | Premise IDs, warrant, and limits | Inferential strength and limits preserved |

The author may retype an unsupported `CLAIM` as `AUTHOR_ASSERTION`. Approval is not evidence.

## Epistemic scope

A grounded point, and every sentence written from it, preserves:

- negation;
- modality and uncertainty;
- population or system;
- operating and experimental conditions;
- quantities, units, and uncertainty;
- comparison class and baseline;
- correlation versus causation;
- temporal and spatial bounds;
- whether the evidence is measurement, interpretation, synthesis, or hypothesis.

## Status

Two statuses exist, recorded only in `evidence.md`.

| Status | Meaning |
|---|---|
| `open` | Grounding or wording unsettled. Blocks drafting, and an `open` point gets no marker in `plan.md`. |
| `write-ready` | Receipt complete and grounded wording author-accepted. |

- Only `write-ready` reaches the writer.
- A point holding a deferral is never `write-ready`. Grounding replaces the deferral with its value, or the point stays `open`.
- Rewording a promoted point returns it to `open`.
- A point's wording stays within the scope its receipt supports. Narrowing is normal; broadening is a failure.

## Authorship

`authorship_log.md` is the only place authorship is recorded. No plan, ledger, or `.tex` file carries a field naming who proposed, edited, or accepted a point. Write no authorship file during a session.

The `log-session` skill tallies authorship once, at session end, as a session aggregate: points recorded, points adjusted by grounding, points agent-suggested and unchallenged, and points edited or added by the author. Per-point authorship is not tracked.
