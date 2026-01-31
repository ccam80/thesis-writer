---
name: document-planner
description: Interactive paragraph-level planning for chapters, papers, or subsections. Collaboratively builds detailed writing plans from thin high-level outlines through narrative structuring and Zotero research.
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

# Document Planner

## Overview

This skill takes a thin high-level plan (section headings, narrative bullet points, a few likely references) and collaboratively turns it into a detailed paragraph-level writing plan with concrete references and specific points. It works at any scope: full chapter, single section, or single subsection.

The process is **fundamentally collaborative**. The author is a subject-matter expert who knows what points are needed to communicate clearly. You are a writing expert who structures documents logically, divides responsibilities into sections, and maintains narrative coherence across the wider document. Neither party works autonomously — every structural decision is discussed.

**Key difference from thesis-planning**: `thesis-planning` produces a chapter-level plan with section headings and key points derived from abstracts/metadata. `document-planner` takes that thin outline and builds it into paragraph-granularity plans with specific, verified references.

## When to Use This Skill

- After `thesis-planning` has produced an approved high-level plan
- Before invoking the `writer` skill to produce LaTeX prose
- When revising the structure of an already-planned section
- When planning a standalone paper or report section
- When starting a new document with no existing plan (see "Cold Start" below)

## Inputs

1. **Target scope**: Chapter number/section, or a specific subsection
2. **Document directory**: The directory containing the `.tex` file and (optionally) a `plan.md`

## Document Hierarchy

Three documents form an authority hierarchy for content. Higher-level documents set narrative and structure; lower-level documents add detail:

1. **`.tex` file** (most detailed, authoritative for existing prose)
2. **Directory-level `plan.md`** (paragraph-level plan, created/maintained by this skill)
3. **Parent-level `plan.md`** (chapter-level or thesis-level plan, sets narrative goals)

If there is a `plan.md` one directory above the document directory, treat it as the hierarchical master plan for this document.

**Parent plan detail level:** The thesis-level plan should contain section purposes, high-level bullet points, and key reference tables — roughly the level of detail produced by the `thesis-planning` skill. The document-planner may update it to reflect structural changes (section reordering, new/removed sections, cross-chapter scope changes, corrected references) but must NOT inflate it with paragraph-level detail, figure descriptions, or expanded sub-points. Those belong in the directory-level plan only.

### Startup: Read and Reconcile

1. **Read the `.tex` file first.** Existing content is authoritative — it must not be removed without explicit user discussion. The user edits this file between sessions.
2. **Read the directory-level `plan.md`** if it exists. This is the detailed plan from previous sessions. The user may have modified it between sessions.
3. **Read the parent-level `plan.md`** (e.g., `thesis/plan.md`). This contains the high-level narrative and key points, typically derived from abstracts and metadata alone — it will lack the specific detail found in lower-level documents.

**If the directory-level `plan.md` does not exist**, create one by copying in the parent plan's content for this document as a starting point.

### Reconciliation Rules

Compare the three documents and resolve discrepancies before proceeding:

- **Content in a higher-level doc missing from a lower-level doc**: Ask the user whether to (a) remove it from the higher-level doc, or (b) add it to the lower-level doc(s) in this or a future round.
- **Content in a lower-level doc that diverges from or modifies the narrative/key points in a higher-level doc**: Ask the user whether to (a) update the higher-level doc to match the new narrative, or (b) modify the lower-level doc to fit the existing narrative.

This hierarchy applies outside thesis structures too. Any document directory should have a `plan.md` and a `.tex` file; create them if missing.

### Structural Mismatches

When section headings, ordering, or structure differ between documents (e.g., `.tex` has different subsection titles than `plan.md`), **ask the user for guidance** — do not silently pick one. Present the mismatch and ask which version to follow, then update the other document(s) to match.

### Understanding the Parent Plan

The parent-level plan is a **thin outline** — a best attempt at a high-level overview of points that will meet narrative goals. It was typically built from abstracts and metadata alone, so it **lacks specific detail**. The key references listed are "likely" references, not confirmed ones. The bullet points sketch what the section might contain, not what it will contain. Treat it as a structural starting point, not a content-complete source.

### Cold Start (No Higher-Level Plan)

When there is no parent-level `plan.md`, build the thin starting plan collaboratively:

1. Ask the author what this document needs to achieve and who the audience is
2. Spawn `zotero-research` agent: "Find top 20 papers on [topic]" to survey Zotero coverage
3. Propose a section structure with narrative bullet points
4. Iterate with the author until the high-level structure is agreed
5. Write this as the directory-level `plan.md` and proceed to Phase 2

## Workflow

### Phase 1: Read and Reconcile

Follow the Startup procedure above. Report what was found in each document and any discrepancies requiring user input.

### Phase 2: Narrative Structure and Paragraph Flow

**This is the core collaborative phase.** Before touching references or detailed points, establish the narrative arc and paragraph flow for each section.

#### Top-Down Planning Across Hierarchy Levels

Documents have multiple levels of hierarchy (chapter → section → subsection → subsubsection). **Plan top-down**: complete the narrative arc and prerequisite check at the highest level before descending to plan individual children at the next level. Then work through children sequentially, planning each one at its own level before descending further.

**Procedure:**

1. **Plan the highest level first.** For a chapter, this means proposing the section-level narrative arc before touching any individual section's paragraph flow.
2. **Get author agreement** on this level before proceeding.
3. **Descend one level.** For each child (e.g., each section within the chapter), propose its narrative arc at the next level down (e.g., subsection flow within a section). Work through children **sequentially** — finish one section's plan before starting the next.
4. **Repeat** at each level until you reach paragraph granularity.

This means a chapter with sections and subsections gets three planning passes:
- **Pass 1 (chapter):** Section-level arc and prerequisites → author agreement
- **Pass 2 (per section):** Subsection-level arc and prerequisites → author agreement, sequentially through all sections
- **Pass 3 (per subsection):** Paragraph-level flow → author agreement, sequentially through all subsections

#### Narrative Arc and Prerequisite Check (at each level)

At every level of hierarchy, before drilling into children, propose:

1. **What does the reader know** at the start of this unit?
2. **What must they know** by the end, and why?
3. **In what order do concepts build on each other?** Identify prerequisite knowledge chains — if child N assumes the reader understands concept X, verify that a prior child introduces it.
4. **Present this as a visual summary** — a short, plain-language flow showing the narrative blocks and how they connect:

```
[General ANS] → [SNS & PNS branches] → [Neural anatomy] → [Tonic control & modulation]
```

This bird's-eye view lets the author spot structural gaps (e.g., "we're discussing neurotransmitters but haven't explained action potentials") before time is spent on detail below.

**Prerequisite check**: For each child in the arc, explicitly identify what the reader must already understand to follow it. If a prerequisite isn't covered by a prior child or a prior chapter/section, flag it — this may require adding a new child or restructuring. Iterate this with the author until resolved.

**Cross-document duplication check**: At each level, check whether any planned content overlaps with or pre-empts topics in other chapters/sections of the parent plan. Common cases:
- A background chapter introducing a concept that a later chapter covers in depth (e.g., coupled-clock mechanism in physiology vs. detailed cell models in computational electrophysiology)
- Two sections covering the same topic from different angles without clear delineation

When overlap is found, present the conflict to the author with concrete options for how to divide responsibility between the sections. For example: "Section 2.4 covers the SAN coupled-clock, but Chapter 4 also covers cell models. Should §2.4 cover channel types and their functional roles (what they do and why), while Ch4 covers the modelling perspective (how many subtypes exist, experimental identification, model complexity over time)?"

Upon author approval, **update the parent-level plan** to reflect the agreed division of responsibility, so that future planning sessions for the other chapter start from the correct scope.

#### Paragraph-Level Flow (lowest level)

At the lowest level of hierarchy (the level where children are paragraphs rather than sections), propose:

1. **A summary narrative arc** — a few plain-language sentences describing the flow of ideas without specific detail:

> "I propose we cover the autonomic system generally: it controls many unconscious systems, it has a complex job, it has to keep them balanced. Then the split into SNS and PNS: two halves, each branch alone, then how they interact. Then the actual neural anatomy. Finally tonic control, and how that control is modulated and in response to what."

2. **The detailed paragraph-flow outline** where each line represents 1–3 paragraphs, described as a topic stub with a brief note on what it achieves in the narrative:
   - Use descriptive labels like `(Intro)`, `(Anatomy)`, `(Control)`, `(New topic intro)` to show the narrative role
   - Note where figures or diagrams belong
   - Note where cross-references to other sections/chapters are needed

3. **Present both levels to the author and ask for feedback** — specifically:
   - Does this sequence tell the right story?
   - Are there points that need adding for the audience to follow?
   - Does any content belong in a different section?
   - Is the level of detail right, or should we expand/compress areas?

**The author will suggest changes.** They know what foundational knowledge the audience needs, what points require more setup, and where the narrative breaks down. Engage critically with their suggestions:

- If a suggestion would improve the narrative, adopt it
- If a suggestion creates structural problems (e.g., duplicating content covered elsewhere, breaking logical flow), explain the concern and propose alternatives
- If content could live in multiple sections, discuss the trade-offs of each placement
- When restructuring, consider the impact on other sections in the document — if moving content changes dependencies, flag this

**Iterate until the paragraph-flow outline is agreed.** This may take several rounds. Do not rush to references.

### Phase 3: Research Fill

Once the narrative structure is agreed, populate it with concrete references and specific points. The parent plan's references are almost never sufficient — they were derived from abstracts and metadata. **Expect to add 2–3 references per paragraph.**

#### Step 1: Generate reference lists per paragraph

For each paragraph stub in the agreed outline:

1. **Spawn `zotero-research` agent**: "Find references supporting/opposing [specific claim from paragraph]". This finds papers that support or refute those points.
2. Collect the returned references and assess coverage.

For sections where coverage is thin or the topic is broad, also spawn `zotero-research`: "Find top N papers on [broader topic]" to discover what exists in Zotero.

#### Step 2: Extract specific points from key papers

For each paragraph, identify the 2–4 most important papers from Step 1, then:

1. **Spawn `zotero-research` agent**: "Verify that [paper] supports [intended citation use]" for each key paper, asking for specific information relevant to the paragraph's topic.
2. The agent returns specific claims, quotes, figures, and page references.
3. Convert the paragraph's topic stub into a list of specific points, each with concrete citations.

For chapters with many paragraphs, spawn `zotero-research` with a combined request: "Research [section topic] and verify the key claims" — it will batch sub-agent calls internally and return consolidated results per paragraph.

#### Step 3: Present extended paragraphs to author

Present the detailed paragraphs to the author **in groups** (e.g., one section at a time):

1. For each group, explain:
   - The narrative arc the paragraphs achieve together
   - The ordering rationale
   - Key references and what they contribute
2. Ask for feedback on each group before moving to the next
3. Make changes before proceeding

Do not present the entire document at once — work through it section by section.

### Phase 4: Finalise Plan

Once all sections have been through research fill and author review:

1. Write the complete paragraph-level plan to `plan.md` in the document directory
2. Verify all parent-plan references are preserved (or removal was approved)
3. Verify all new references are real (from Zotero)
4. Present for final approval

## Output Format

Write to: `<document_directory>/plan.md`

```markdown
# Chapter Plan: [Title]
Type: [background|meat|conclusions|future-work]
Status: [draft|approved]
Date: [YYYY-MM-DD]
Source: [parent plan reference]

## Narrative Thread
[1-3 sentences: what story this chapter tells and how it fits the larger document]

## Sections

### Section X.1: [Title]
**Purpose**: What this section accomplishes in the narrative

#### Paragraph 1 — (Topic Label)
- Point: [specific claim or statement]
  - Cite: \cite{zotero_key} — [what it supports, page/figure if known]
- Point: [next claim]
  - Cite: \cite{key1, key2}
- Transition to: [next paragraph topic]

#### Paragraph 2 — (Topic Label)
- Point: [claim]
  - Cite: \cite{key}
- Point: [claim]
- Transition to: [next topic]

#### Figure X.1
- Type: [data plot / block diagram / schematic]
- Shows: [what the reader sees]
- Axes: [if applicable]
- Placement: after Paragraph N

### Section X.2: [Title]
**Purpose**: ...

[continue for all sections]

## References Summary
| Key | Citation | Zotero Key | Usage |
|-----|----------|------------|-------|
| key1 | Author et al., Year | XXXXXXXX | Supports point about X in §X.1 ¶2 |

## Open Questions
- [Unresolved items for writing phase]

## Notes for Writer
- [Style guidance, emphasis, tone]
```

## Scope Flexibility

This skill works at any granularity:

- **Full chapter**: Plan all sections to paragraph level
- **Single section**: Plan paragraphs within one section
- **Single subsection**: Detailed paragraph planning for a focused topic

When working on a subsection, still reference the broader chapter narrative to maintain coherence.

## Narrative Coherence Checks

Throughout the process, regularly verify:

1. **Does each section advance the chapter's story?** If a section feels like a detour, suggest relocation or compression.
2. **Do transitions connect logically?** Each paragraph should flow from the previous one.
3. **Is the level of detail consistent?** Don't spend 5 paragraphs on a minor point and 1 on a major one.
4. **Are we serving the larger document's narrative?** Background chapters should build toward the thesis contribution. Research chapters should be self-contained but connected.
5. **Does content belong here or elsewhere?** If a topic is covered in another section/chapter, cross-reference rather than duplicate. Discuss placement trade-offs with the author.

## Autonomy Level

**Low.** This skill operates collaboratively at every stage:

- **Phase 1** (Read/Reconcile): Report findings, ask about discrepancies
- **Phase 2** (Narrative Structure): Propose, discuss, iterate — do not finalise without author agreement
- **Phase 3** (Research Fill): Inform the author before spawning agents; present results in groups for review
- **Phase 4** (Finalise): Present complete plan for approval

The only autonomous actions are: reading files, spawning research agents (after informing the user), and writing the plan.md once approved.

## Integration

- **Reads**: `.tex` file (authoritative existing content), directory-level `plan.md`, parent-level `plan.md`
- **Uses**: `zotero-research` agent (topic discovery, claim-specific references, citation verification, batch coordination)
- **Produces**: directory-level `plan.md` files
- **Hands off to**: `writer` skill for LaTeX prose generation
