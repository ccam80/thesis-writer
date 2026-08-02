# Thesis Writing Contract

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

## Plan grammar

| Shape | Meaning |
|---|---|
| Prose under a heading | Summary and purpose. Emits no sentence. |
| `**¶ [label]** — [text]` | Paragraph point. |
| Bullet nested under a `¶` line | Sentence point. The only groundable line. |
| Loose bullet under a heading | Candidate point, not yet sorted into a paragraph. |
| Sentence point with a bracketed ID | Grounded. |

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
[Readable index of open point IDs and their bounded questions]
```

A grounded point line carries only its text, bracketed ID, and approved citation keys. The plan header carries the title only. Add no block-level or file-level status field.

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

## Status

Two statuses exist, recorded only in `evidence.md`.

| Status | Meaning |
|---|---|
| `open` | Grounding or wording unsettled. Blocks drafting, and an `open` point gets no marker in `plan.md`. |
| `write-ready` | Receipt complete and grounded wording author-accepted. |

- Only `write-ready` reaches the writer.
- Rewording a promoted point returns it to `open`.
- A point's wording stays within the scope its receipt supports. Narrowing is normal; broadening is a failure.
