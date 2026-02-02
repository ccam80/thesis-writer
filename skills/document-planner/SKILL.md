---
name: document-planner
description: Interactive planning at any scope — whole thesis, chapter, section, or subsection. Invoke with a prompt specifying the working level. Collaboratively builds writing plans from cold start through to claim-level outlines with verified Zotero citations.
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

# Document Planner

## Overview

This skill collaboratively builds writing plans at any scope — from whole-thesis chapter maps down to claim-level paragraph outlines with verified citations. It is the single planning skill for all document types and hierarchy levels.

The process is **fundamentally collaborative**. The author is a subject-matter expert who knows what points are needed to communicate clearly. You are a writing expert who structures documents logically, divides responsibilities into sections, and maintains narrative coherence across the wider document. Neither party works autonomously — every structural decision is discussed.

**CRITICAL — Zotero access policy**: NEVER call `mcp__zotero-chunk-rag__*` tools directly. All Zotero library access MUST go through the `zotero-research` agent, spawned via the Task tool. Only the `zotero-research` agent is permitted to call the MCP tools.

## When to Use This Skill

- Planning a new thesis from scratch (whole-thesis scope)
- Planning individual chapters from a thesis-level plan
- Building paragraph-level or claim-level plans for sections
- Revising the structure of an already-planned section
- Planning a standalone paper or report

## Chapter Types

Each chapter type has a distinct structure and writing approach. Use these when proposing chapter plans.

### Background Chapter
Literature-review style treatment. Provides context and foundation.
- **Structure**: Introduction → Major themes (organised thematically, NOT study-by-study) → Summary with gaps
- **Writing approach**: Synthesize across sources. Every claim needs citation(s). Identify gaps and controversies. Connect to thesis objectives.
- **Citation density**: High (1-3 citations per paragraph)
- **Figures**: Conceptual diagrams, timelines, comparison tables

### Meat Chapter (Research Chapter)
Paper-like IMRaD structure presenting original research. Each should be publishable as standalone.
- **Structure**: Introduction → Brief background (reference full background chapter) → Methods → Results → Discussion → Conclusion
- **Writing approach**: Self-contained but connected to thesis narrative. Methods fully reproducible. Results before interpretation.
- **Citation density**: Medium in intro/discussion, low in methods/results (own work)
- **Figures**: Data plots, block diagrams, result visualizations

### Conclusions Chapter
Synthesis of thesis findings and contributions.
- **Structure**: Summary of work → Key findings → Contributions → Limitations
- **Writing approach**: No new material. Reference thesis chapters, not external sources. Specific about contributions. Honest about limitations.
- **Citation density**: None (reference thesis chapters only)

### Future Work Chapter
Research directions and open questions.
- **Structure**: Immediate extensions → Longer-term directions → Open questions
- **Writing approach**: Concrete and actionable. Connect to thesis limitations.
- **Citation density**: Low

## Inputs

1. **Target scope**: Whole thesis, chapter, section, or subsection
2. **Document directory**: The directory containing the `.tex` file and (optionally) a `plan.md`

## Document Hierarchy

Three documents form an authority hierarchy for content. Higher-level documents set narrative and structure; lower-level documents add detail:

1. **`.tex` file** (most detailed, authoritative for existing prose)
2. **Directory-level `plan.md`** (paragraph/claim-level plan, created/maintained by this skill)
3. **Parent-level `plan.md`** (chapter-level or thesis-level plan, sets narrative goals)

If there is a `plan.md` one directory above the document directory, treat it as the hierarchical master plan for this document.

**Parent plan detail level:** The thesis-level plan should contain section purposes, high-level bullet points, and key reference tables. The document-planner may update it to reflect structural changes (section reordering, new/removed sections, cross-chapter scope changes, corrected references) but must NOT inflate it with paragraph-level detail, figure descriptions, or expanded sub-points. Those belong in the directory-level plan only.

### Startup: Read and Reconcile

1. **Read the `.tex` file first.** Existing content is authoritative — it must not be removed without explicit user discussion. The user edits this file between sessions.
2. **Read the directory-level `plan.md`** if it exists. This is the detailed plan from previous sessions. The user may have modified it between sessions.
3. **Read the parent-level `plan.md`** (e.g., `thesis/plan.md`). This contains the high-level narrative and key points.

**If the directory-level `plan.md` does not exist**, create one by copying in the parent plan's content for this document as a starting point.

### Reconciliation Rules

Compare the three documents and resolve discrepancies before proceeding:

- **Content in a higher-level doc missing from a lower-level doc**: Ask the user whether to (a) remove it from the higher-level doc, or (b) add it to the lower-level doc(s) in this or a future round.
- **Content in a lower-level doc that diverges from or modifies the narrative/key points in a higher-level doc**: Ask the user whether to (a) update the higher-level doc to match the new narrative, or (b) modify the lower-level doc to fit the existing narrative.

This hierarchy applies outside thesis structures too. Any document directory should have a `plan.md` and a `.tex` file; create them if missing.

### Structural Mismatches

When section headings, ordering, or structure differ between documents (e.g., `.tex` has different subsection titles than `plan.md`), **ask the user for guidance** — do not silently pick one. Present the mismatch and ask which version to follow, then update the other document(s) to match.

### Understanding the Parent Plan

The parent-level plan is a **thin outline** — a best attempt at a high-level overview of points that will meet narrative goals. It was typically built from abstracts and metadata alone, so it **lacks specific detail**. The key references listed are "likely" references, not confirmed ones. Treat it as a structural starting point, not a content-complete source.

### Cold Start (No Higher-Level Plan)

When there is no parent-level `plan.md`, build the thin starting plan collaboratively:

1. Ask the author what this document needs to achieve and who the audience is
2. Spawn `zotero-research` agent: "Find top 20 papers on [topic]" to survey Zotero coverage
3. Propose a section structure with narrative bullet points
4. Iterate with the author until the high-level structure is agreed
5. Write this as the directory-level `plan.md` and proceed to Phase 2

For whole-thesis cold starts, first establish the overall narrative (what is the thesis about, what is the contribution, what story does it tell), then map chapters (background, meat, conclusions) with their connections before planning individual chapters.

## Workflow

### Phase 1: Read and Reconcile

Follow the Startup procedure above. Report what was found in each document and any discrepancies requiring user input.

### Phase 2: Narrative Structure and Paragraph Flow

**This is the core collaborative phase.** Before touching references or detailed points, establish the narrative arc and paragraph flow for each section.

#### Top-Down Planning Across Hierarchy Levels

Documents have multiple levels of hierarchy (thesis → chapter → section → subsection → paragraph). **Plan top-down**: complete the narrative arc and prerequisite check at the highest level before descending to plan individual children at the next level. Then work through children sequentially, planning each one at its own level before descending further.

**Procedure:**

1. **Plan the highest level first.** For a thesis, this means chapter ordering. For a chapter, section-level narrative arc.
2. **Get author agreement** on this level before proceeding.
3. **Descend one level.** Work through children **sequentially** — finish one child's plan before starting the next.
4. **Repeat** at each level until you reach paragraph granularity.

#### Structural Critique Pass

Before descending to the next level, perform a **structural critique** of the current level's ordering. This is a distinct analytical step — not paragraph planning, not research, just examining whether the sequence forms coherent topic threads.

**Thread analysis:** Label each child with the domain or topic thread it belongs to (e.g., "cells," "control systems," "anatomy," "clinical"). Then read the sequence of labels. If the sequence zigzags between domains, propose a reordering that groups related threads into contiguous runs. Two clean threads that converge at a defined point read better than interleaved fragments.

**Monotonic knowledge test:** For each child, ask: "Does the reader's knowledge in this domain build monotonically, or do we introduce a concept, leave it, and return later?" If knowledge in a domain is interrupted, the reader must mentally context-switch. Reorder to minimise switches.

**Cross-chapter thread analysis:** When working at thesis scope, apply thread and monotonic analysis across the full chapter sequence. Chapters should also avoid zigzagging between domains.

**Present reorderings proactively.** If thread analysis reveals a zigzag, propose the alternative ordering and explain the narrative improvement. Don't wait for the author to spot it — this structural analysis is the planner's core value-add.

**Merge-and-resplit pattern:** When adjacent sections feel coupled, misordered, or have unclear boundaries, flatten their content into a single ordered list. Label each item by topic domain. Look for natural clusters and transitions — the split point should fall where the domain or abstraction level changes cleanly. This often reveals that the original boundaries were drawn at the wrong point. The pattern is: join → reorder → see what clusters emerge → split (or don't) at the natural boundary.

#### Narrative Arc and Prerequisite Check (at each level)

At every level of hierarchy, before drilling into children, propose:

1. **What does the reader know** at the start of this unit?
2. **What must they know** by the end, and why?
3. **In what order do concepts build on each other?** Identify prerequisite knowledge chains.
4. **Present this as a visual summary:**

```
[General ANS] → [SNS & PNS branches] → [Neural anatomy] → [Tonic control & modulation]
```

**Prerequisite check**: For each child, identify what the reader must already understand. If a prerequisite isn't covered by a prior child or chapter, flag it.

**Cross-document duplication check**: Check whether any planned content overlaps with topics in other chapters/sections of the parent plan. When overlap is found, present the conflict with concrete options for dividing responsibility. Upon agreement, **update the parent-level plan** to reflect the division.

#### Section-Purpose Revalidation

Before descending into paragraph planning for each section, explicitly answer three questions:

1. **What does this section do for the chapter?** How does it advance the chapter's narrative arc?
2. **What does this section do for the thesis?** What vocabulary, intuition, or evidence does it build for later chapters?
3. **Where did the previous section end?** What state is the reader in? What do they expect next?

If the section's planned content doesn't have a clean answer to (1), it may be a grab-bag. Look for a **unifying thread** — a single concept or framing that makes the diverse topics feel coherent. If no unifying thread exists, the content may belong in different sections or the section needs restructuring.

#### Tone Consistency Check

Background chapters describe established knowledge. Check each paragraph stub for statements that read as **thesis argument** rather than established fact. Common signs: forward references to "why this matters for our approach," evaluative claims about methodology limitations, or conclusions that presuppose the thesis contribution. Relocate these to the chapter where the argument is made. The background should build vocabulary and intuition; the reader will draw their own conclusions.

#### Content Placement Test

For each paragraph, ask: "Does this point fit the section's unifying thread?" If a point is important but doesn't fit, it belongs elsewhere — propose a specific alternative location rather than forcing it in.

#### Paragraph-Level Flow (lowest level)

At the lowest level of hierarchy (the level where children are paragraphs rather than sections), propose:

1. **A summary narrative arc** — a few plain-language sentences describing the flow of ideas without specific detail.

2. **The detailed paragraph-flow outline** where each line represents 1–3 paragraphs, described as a topic stub with a brief note on what it achieves in the narrative:
   - Use descriptive labels like `(Intro)`, `(Anatomy)`, `(Control)` to show narrative role
   - Note where figures or diagrams belong
   - Note where cross-references to other sections/chapters are needed

3. **Identify figure opportunities.** Look for high-concept-density paragraphs where spatial or structural complexity would require high word counts. Propose figures proactively. **Do NOT number figures** during planning — use descriptive labels. Numbering creates cascading changes.

4. **Before presenting, do your own prerequisite analysis silently.** Read ahead into later sections and chapters. Identify concepts that later content assumes the reader understands. Incorporate these directly — do NOT show the reasoning. If the author questions a paragraph's inclusion, *then* explain the forward dependency. Do NOT ask open-ended questions like "is anything missing?" — make specific proposals instead.

5. **Present the narrative arc and paragraph flow** as a clean proposal. Keep each paragraph stub to 2–3 sentences. No justification annotations, no forward-reference lists, no meta-commentary. Do NOT include "not covered here" or "deferred to §X" annotations — they clutter the plan without value.

6. **After presenting the detailed stubs, provide a one-clause narrative summary table** — one row per paragraph, summarising its role in a single clause. This lets the author scan flow at a glance.

**Paragraph numbering must be section-local** (¶1, ¶2, ... restarting each section), not chapter-global. Chapter-global numbering creates renumbering cascades.

**The author will suggest changes.** Engage critically:

- If a suggestion improves the narrative, adopt it
- If it creates structural problems, explain the concern and propose alternatives
- If content could live in multiple sections, discuss trade-offs
- When restructuring, consider impact on other sections

**Iterate until the paragraph-flow outline is agreed.** This may take several rounds. Do not rush to references.

### Phase Transition: Structure → Research

The structural planning phase and the research fill phase are very different interaction modes. **Make the transition explicit**: "Structure is agreed. Moving to claim expansion and research."

### Phase 3: Claim Expansion and Research

Once the narrative structure is agreed, expand paragraph stubs into claim-level outlines with verified citations. This phase operates at **chapter scope** — all sections are expanded and researched together to enable cross-section deduplication and consistency checking.

#### Step 1: Expand paragraph stubs to candidate claims (chapter-wide)

For every paragraph stub in the chapter, propose candidate claims — the specific statements each paragraph will make. Each claim should be a single assertable sentence or fact that could carry a citation. Aim for ~4–6 claims per paragraph.

Mark each claim with its citation status:
- `[restate]` — restating a point established in an earlier paragraph/section (no new citation needed)
- `[known]` — an existing reference from the parent plan covers this
- `[need]` — needs a citation from Zotero

Present the full chapter's expanded claims to the author for a **quick review pass** before researching. This catches obviously wrong directions and lets the author add claims from domain knowledge before research tokens are spent. The author is not expected to review every claim in detail — just scan for missing topics, wrong framings, or wasted effort.

#### Step 2: Research (chapter-wide batch)

Spawn `zotero-research` agent with a structured request covering all `[need]` claims across the chapter. Structure the request as a numbered list of claims grouped by section, with clear instructions on what kind of evidence is needed for each.

The agent returns passage-level results. One batch call per chapter is the target — only split into multiple calls if the claim count exceeds what the agent can handle in one request.

#### Step 3: Triage (chapter-wide)

Review all research results and categorise each claim:

- **Supported**: Attach citation (Zotero key, brief note on what it supports)
- **Refuted**: Flag with counter-evidence. Present the refutation to the author — do NOT silently drop or rewrite. Options: rephrase, remove, or present as contested.
- **Unsupported**: No relevant passages found. Track as a gap — the author may have sources in mind, accept the gap for now, or decide to remove the claim.

Also perform:
- **Cross-paragraph deduplication**: Flag identical claims appearing in multiple paragraphs. Decide where the claim lives vs where it's a brief restatement.
- **Claim density check**: If a paragraph has >8 claims, it probably needs splitting. If <3, it may be thin or should merge with an adjacent paragraph. Feed structural changes back to the author.

#### Step 4: Present (section by section)

Present the expanded, triaged claims to the author **section by section**. For each section show:

- The claim-level outline with citations attached
- Refuted claims with counter-evidence and options
- Unsupported claims as gaps
- Any structural changes suggested by claim density

Get author feedback per section before moving to the next. The author may:
- Overrule a refutation ("this claim is correct, I'll find a source")
- Accept a gap and add to reference debt
- Restructure claims based on what the research revealed
- Add domain knowledge claims the agent missed

#### Step 5: Commit

Write the full chapter's claim-level plan to `plan.md` in the document directory. Update the parent plan if structural changes occurred.

### Phase 4: Finalise Plan

Once all sections have been through claim expansion and author review:

1. Write the complete claim-level plan to `plan.md` in the document directory
2. Verify all parent-plan references are preserved (or removal was approved)
3. Verify all new references are real (from Zotero)
4. Track unsupported claims in the Open Questions or reference debt log
5. Present for final approval

The finalised plan should be **directly prosifiable** by the writer skill — every paragraph is a list of specific, cited claims that the writer converts to flowing prose without adding content.

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

## Section-Level Narrative Arc
[Visual flow diagram and prose description]

## Sections

### Section X.1: [Title]
**Purpose**: What this section accomplishes in the narrative

#### Paragraph 1 — (Topic Label)
- Claim [supported/restate/gap]
  - Cite: \cite{zotero_key} — [what it supports]
- Claim [supported]
  - Cite: \cite{key1, key2}
- Claim [restate from §X.Y ¶Z]

→ **Figure**: [Descriptive label — what it shows, type]

#### Paragraph 2 — (Topic Label)
- Claim [supported]
  - Cite: \cite{key}
- Claim [gap — needs source for X]

[continue for all paragraphs and sections]

## References Summary
| Key | Citation | Zotero Key | Usage |
|-----|----------|------------|-------|
| key1 | Author et al., Year | XXXXXXXX | Supports claim about X in §X.1 ¶2 |

## Open Questions
- [Unsupported claims awaiting sources]
- [Structural decisions deferred to writing phase]

## Notes for Writer
- [Style guidance, emphasis, tone]
- CRITICAL: Do not add claims, facts, or assertions not present in this plan.
  If a transition requires stating something not in the plan, flag it.
```

## Handling Insufficient Coverage

When Zotero library lacks sufficient references:

**Do NOT**:
- Fabricate references
- Proceed without adequate support
- Silently skip topics

**Do**:
1. Document the gap explicitly in the plan's Open Questions
2. Tell the user: "The Zotero library has limited coverage of [topic]. Found only [N] papers. Options: (a) suggest search terms for external databases, (b) de-emphasize this topic, (c) proceed with available material and note the gap."
3. Wait for user decision
4. If the user wants external search, suggest specific queries and databases

## Scope Flexibility

This skill works at any granularity:

- **Whole thesis**: Chapter map, narrative thread, cross-chapter analysis
- **Full chapter**: All sections to claim level
- **Single section**: Claim-level planning within one section
- **Single subsection**: Detailed claim planning for a focused topic

When working at a lower scope, still reference the broader document narrative to maintain coherence. When working at thesis scope, use the cold start procedure and focus on chapter ordering, narrative threads, and cross-chapter dependencies before descending.

## Cross-Reference Formatting

When referencing a later chapter or section in conversation with the author, **always include the section titles** from the parent plan so the author doesn't have to remember the document structure.

**Good:** "This fits in Ch3 §3.2 (Measuring Heart Rate), which covers R-wave detection, ECG vs PPG, artifact sources, and ectopic beat handling."

**Bad:** "This fits in Ch3 §3.2."

## Narrative Coherence Checks

Throughout the process, regularly verify:

1. **Does each section advance the chapter's story?** If a section feels like a detour, suggest relocation or compression.
2. **Do transitions connect logically?** Each paragraph should flow from the previous one.
3. **Is the level of detail consistent?** Don't spend 5 paragraphs on a minor point and 1 on a major one.
4. **Are we serving the larger document's narrative?** Background chapters should build toward the thesis contribution. Research chapters should be self-contained but connected.
5. **Does content belong here or elsewhere?** If a topic is covered in another section/chapter, cross-reference rather than duplicate.

## Interaction Guidelines

### Be Collaborative
- Present findings and proposals, don't dictate
- Ask for the author's view on controversies
- Respect their expertise in their field

### Be Transparent
- Show your reasoning for structural decisions
- Admit when coverage is thin
- Distinguish between well-supported and tentative points

### Be Efficient
- Group related questions
- Don't ask about every minor point
- Focus questions on things that affect structure/narrative
- Provide options, not open-ended queries

### Be Research-Grounded
- Every claim backed by Zotero reference (or explicitly flagged as gap)
- Distinguish author's view from paper's conclusion
- Flag potential citation issues early

## Autonomy Level

**Low.** This skill operates collaboratively at every stage:

- **Phase 1** (Read/Reconcile): Report findings, ask about discrepancies
- **Phase 2** (Narrative Structure): Propose, discuss, iterate — do not finalise without author agreement
- **Phase 3** (Claim Expansion): Expand claims autonomously, research autonomously, but present all results for author review and haggling
- **Phase 4** (Finalise): Present complete plan for approval

The only autonomous actions are: reading files, expanding candidate claims (pre-review), spawning research agents, and writing the plan.md once approved.

## Integration

- **Reads**: `.tex` file (authoritative existing content), directory-level `plan.md`, parent-level `plan.md`
- **Uses**: `zotero-research` agent (passage-level semantic search, claim verification, batch coordination)
- **Produces**: directory-level `plan.md` files (claim-level, directly prosifiable)
- **Hands off to**: `writer` skill for LaTeX prose generation (writer must not add content beyond the plan)
