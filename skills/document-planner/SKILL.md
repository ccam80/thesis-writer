---
name: document-planner
description: Interactive planning at any scope — whole thesis, chapter, section, or subsection. Invoke with a prompt specifying the working level. Collaboratively builds writing plans from cold start through to statement-level outlines with verified Zotero citations.
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

# Document Planner

## Overview

This skill collaboratively builds writing plans at any scope — from whole-thesis chapter maps down to statement-level paragraph outlines with verified citations. It is the single planning skill for all document types and hierarchy levels.

The process is **fundamentally collaborative**. The author is a subject-matter expert who knows what points are needed to communicate clearly. You are a writing expert who structures documents logically, divides responsibilities into sections, and maintains narrative coherence across the wider document. Neither party works autonomously — every structural decision is discussed.

**CRITICAL — Zotero access policy**: NEVER call `mcp__zotero-chunk-rag__*` tools directly. All Zotero library access MUST go through the `zotero-research` agent, spawned via the Task tool. Only the `zotero-research` agent is permitted to call the MCP tools.

## When to Use This Skill

- Planning a new thesis from scratch (whole-thesis scope)
- Planning individual chapters from a thesis-level plan
- Building paragraph-level or statement-level plans for sections
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
2. **Directory-level `plan.md`** (paragraph/statement-level plan, created/maintained by this skill)
3. **Parent-level `plan.md`** (chapter-level or thesis-level plan, sets narrative goals)

If there is a `plan.md` one directory above the document directory, treat it as the hierarchical master plan for this document.

**Parent plan detail level:** The thesis-level plan should contain section purposes, high-level bullet points, and narrative goals. It does not contain references — those are resolved at the directory-level plan during Phase 3. The document-planner may update the parent plan to reflect structural changes (section reordering, new/removed sections, cross-chapter scope changes) but must NOT inflate it with paragraph-level detail, figure descriptions, or expanded sub-points. Those belong in the directory-level plan only.

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

The parent-level plan is a **thin outline** — a best attempt at a high-level overview of points that will meet narrative goals. It was typically built collaboratively with the author, so it **lacks specific detail**. Treat it as a structural starting point, not a content-complete source.

### Cold Start (No Higher-Level Plan)

When there is no parent-level `plan.md`, build the thin starting plan collaboratively:

1. Ask the author what this document needs to achieve and who the audience is
2. Propose a section structure with narrative bullet points based on the author's input
3. Iterate with the author until the high-level structure is agreed
4. Write this as the directory-level `plan.md` and proceed to Phase 2

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

The structural planning phase and the research fill phase are very different interaction modes. **Make the transition explicit**: "Structure is agreed. Moving to statement expansion and research."

### Phase 3: Statement Expansion and Research

Once the narrative structure is agreed, expand paragraph stubs into statement-level outlines with verified citations. This phase operates at **section scope** — complete one section fully (expansion, author review, research, triage) before moving to the next.

#### Step 1: Iterative statement expansion (per section)

This step builds the complete skeleton of every paragraph in a section. The goal is a sequence of statements that a writer agent can convert to flowing prose by adding only wording, transitions, and joins — no new content.

**Statement style — terse, not prose.** Write statements as compressed note-form: noun phrases, arrows for causation, semicolons for related points. The writer skill converts these to prose — full sentences in the plan over-constrain wording and are harder to review.

Good: `Concentration gradient → electrochemical driving force → membrane voltage`
Bad: `The concentration gradient creates an electrochemical driving force which produces a voltage across the membrane.`

Good: `Neuron anatomy: soma (nucleus), dendrites (receive), axon (transmit), synaptic terminals (output)`
Bad: `A neuron consists of a cell body (soma) containing the nucleus, branching dendrites that receive input from other neurons, a long axon that carries signals away from the soma, and synaptic terminals that transmit signals to the next cell.`

The test: if a statement reads as a finished sentence that could appear verbatim in the thesis, it is too detailed. Compress it.

##### Expansion mode choice

Before generating any content, present the section's paragraph stubs and ask the author how they want to proceed:

**Presentation format:**

```
## Section X.Y: [Title]

This section has [N] paragraphs:

1. **[Topic Label]** — [1-sentence stub from Phase 2]
2. **[Topic Label]** — [1-sentence stub from Phase 2]
...

**Expansion mode:** For each paragraph, would you like to:
(a) **Provide the initial points yourself** — you dictate the key facts and logical steps; I refine and structure
(b) **Have me generate from whole cloth** — I propose the initial expansion; you review and modify
(c) **Mixed** — specify which paragraphs you'll seed vs which I should generate

If you choose (a) or (c), provide your points in any format — bullet lists, prose notes, keywords. I'll convert to terse statement form and run the refinement cycles. Points you provide are tagged as "user-dictated" in provenance tracking.
```

**Author-seeded expansion:** When the author provides initial points:
1. Convert their input to terse statement form (noun phrases, arrows, semicolons)
2. Number and tag by topic domain
3. Note which points came directly from author input in the scratch file
4. Proceed to refinement cycles — prerequisite check, topic coherence, etc.

**Agent-generated expansion:** When the author requests generation from whole cloth, proceed directly to the initial expansion procedure below.

**Mixed mode:** Track each paragraph's provenance mode separately in the scratch file.

##### Iterative refinement process

Expansion is not a single pass. Perform multiple refinement cycles, writing working state to a scratch file at `<document_directory>/scratch_<section_number>.md`. This file is deleted after the section is approved.

**Initial expansion:** For each paragraph stub, list every point needed to tell that stub's story:
- Factual claims (the core content)
- Framing or setup notes
- Logical steps connecting one fact to the next
- Links to other paragraphs/sections where narrative requires

Number all points. Tag each point by topic domain (e.g., `[anatomy]`, `[math]`, `[mechanism]`).

**Provenance baseline:** After initial expansion and before presenting to the author, record the baseline state in the scratch file:

```markdown
## Provenance Baseline
**Paragraphs**: [N]
**Points**: [N]
**Figures proposed**: [N]
**Point IDs**: 1.1, 1.2, 1.3, 2.1, 2.2, ... [full list]
```

This baseline is compared against the final approved state to compute provenance statistics.

**Paragraph numbering:** Use sequential integers (1, 2, 3...), not sublabels (5a, 5b). When splitting a paragraph, the resulting paragraphs become new sequential numbers — renumber all subsequent paragraphs and update cross-references accordingly.

**Refinement cycles:** After initial expansion, run the following passes. Record each cycle in the scratch file:

```markdown
## Cycle N

### Current point list
[numbered, tagged points for each paragraph]

### Pass results
**Prerequisite check:** [reorders made, or "none"]
**Topic coherence:** [merge/split decisions, or "none"]
**Gap check:** [bridges added or gaps flagged, or "none"]
**Framing check:** [framing added, or "none"]
**Quantitative check:** [quantities flagged for "derivation needed?" question, or "none"]

### Questions for author
[list of domain-specific questions identified this cycle]
```

**Pass descriptions:**

1. **Prerequisite check:** For each point, verify the reader has the necessary background from earlier points. If not, reorder. If prerequisite is missing entirely, add a bridge point or flag for author.

2. **Topic coherence:** Read the topic tags in sequence. If a paragraph interleaves topics (e.g., `[anatomy]` → `[math]` → `[anatomy]`), consider reordering. If adjacent paragraphs share significant topic overlap, merge their points into one list, reorder by topic, then re-split at natural boundaries.

3. **Gap check:** Look for logical jumps — places where the reader must infer a step. Either insert an explicit bridge point or flag as "needs author input: [what's missing]."

4. **Framing check:** Each paragraph should begin with context before detail. If a paragraph launches into specifics without setup, add a framing point at the start.

5. **Quantitative check:** Flag any point that asserts a specific value, describes a quantity, or implies a mathematical relationship. Add to questions: "Should [X] include a derivation?"

**Stopping condition:** Continue cycles until a full cycle produces "none" for all five passes. Minimum 2 cycles required.

##### Post-author-feedback cycles

After presenting to the author and receiving feedback (answers to questions, corrections, additions, removals), incorporate the changes and run **at least 2 more refinement cycles**. Author input often changes structure — reordering, new points, removed points — which may introduce new prerequisite issues or gaps.

Record these as continuing cycle numbers (e.g., if initial refinement ended at Cycle 2, post-feedback cycles are Cycle 3, Cycle 4, etc.).

##### Provenance tracking during feedback

After each round of author feedback, update the provenance tracking in the scratch file:

```markdown
## Feedback Round [N]

### Changes from author feedback
**Points kept verbatim**: [list of point IDs unchanged from baseline]
**Points modified**: [list of point IDs that were changed, with brief note]
**Points deleted**: [list of point IDs removed]
**Points added by user**: [new point IDs with brief description]
**Points added by agent (user-directed)**: [points agent extracted from user's narrative direction]
**Points added by agent (independent)**: [points agent suggested without user prompting]
**Figures added**: [figure descriptions with attribution: "user-suggested" or "agent-suggested"]
**Structural changes**: [paragraph splits, merges, reorders — who initiated]
```

**Attribution rules:**
- **User-dictated**: The user stated the point, the agent transcribed it (possibly rephrasing)
- **User-directed**: The user described a narrative goal or gap; the agent generated specific points to fill it
- **Agent-suggested**: The agent proposed the point without user prompting; user accepted/modified
- **Agent-suggested, rejected**: The agent proposed; user rejected (track for honesty)

The test for "user-dictated" vs "user-directed": Could a diligent transcriptionist have produced this point from the user's words alone? If yes, it's user-dictated. If the agent had to infer, synthesize, or generate substantive content, it's user-directed or agent-suggested.

##### Questions for author

During refinement, compile questions in these categories:

- **Relevance:** "Does [specific detail] get used later in the thesis?"
- **Correctness:** "Is [factual claim] accurate?"
- **Scope:** "What level of detail is needed for [topic]?"
- **Gaps:** "What connects [X] to [Y]? I see a logical jump."
- **Derivations:** "Should [quantity/equation] be presented as a derivation?"

Do not ask questions with obvious answers. Do ask when uncertain — the author may say "don't know," which flags a point for reference checking.

##### Presentation to author

After refinement stabilizes, present to the author:

1. **Final point list** — clean, numbered, without topic tags or working annotations
2. **Compiled questions** — grouped by category
3. **Proposed paragraph splits** — if any paragraph exceeds 6 points, propose split locations

Do NOT show the scratch file contents. The author reviews the clean output.

**CHECKPOINT REMINDER:** When the author approves the point list (signals like "ok", "approved", "let's continue"), write a checkpoint entry before proceeding to citation marking.

##### Citation marking (after author approval)

Only after the author approves the point list, add citation annotations:

- **Paragraph-level** `(cite whole para: [topic area])` when all points draw from standard textbook material
- **Point-level** `(citable)` only for: specific measured values, contested claims, specific study findings, non-obvious facts

Do not pre-assign specific references — the research agent finds appropriate sources.

#### Step 2: Research (per section)

After the author approves a section's point list with citation annotations, collect all statements marked `(citable)` or paragraphs marked `(cite whole para)`. Compile into a numbered list:

    ## Section X.Y: [Title]
    1. [statement text]
    2. [statement text]
    ...

Spawn the `zotero-research` agent with this list as a Claim Research request (see zotero-research skill §1). The agent processes statements sequentially and returns supporting, contradicting, and qualifying citations for each. If the agent does not complete the full list, it reports where it stopped — spawn a follow-up agent for the remaining statements.

#### Step 3: Triage and present

Triage the section's research results and present to the author. Show every paragraph with its statements and research outcomes:

    ### §X.Y Paragraph N — (Topic Label)

    * Statement text (citable)
        Supporting:
        - \cite{key} p. [page] — [one sentence]
        - \cite{key2} p. [page] — [one sentence]

    * Statement text (citable)
        Supporting:
        - \cite{key} p. [page] — [one sentence]
        Qualifying:
        - \cite{key3} p. [page] — [one sentence]
        ⚠ Qualification: [brief description of how the source narrows the claim]

    * Statement text (citable)
        Supporting: None
        ⚠ Gap — no source found

    * Statement text
        [no citation needed — framing/setup]

    → **Figure**: [Descriptive label — what it shows, type]

**Categorisation rules:**

- **Supported**: Attach all citations found.
- **Contradicted**: Present the counter-evidence to the author — do NOT silently drop or rewrite. This is mandatory even if the statement also has supporting citations. A statement with both supporting and contradicting evidence must be flagged. Options: rephrase the statement, remove it, or present the point as contested with both sides cited.
- **Qualified**: Present the qualification to the author. This is mandatory even if the statement also has supporting citations. A statement with both supporting and qualifying evidence may need narrowing or additional context.
- **Gap**: No relevant results found. Track as a gap — the author may have sources in mind, accept the gap for now, or decide to remove the statement.

Get author feedback per section before moving to the next. The author may:
- Overrule a contradiction ("this statement is correct, I'll find a source")
- Accept a gap and add to reference debt
- Restructure statements based on what the research revealed
- Add statements from domain knowledge

**CHECKPOINT REMINDER:** When the author approves the triaged results, write a checkpoint entry before committing the section.

#### Step 4: Commit section and continue

After the author approves a section's triaged results:

1. **Delete the scratch file** (`scratch_<section_number>.md`)
2. **Write the section** to `plan.md` in the document directory (append if other sections already written)
3. **Track gaps** in the Open Questions section
4. **Proceed to next section** — return to Step 1

#### Step 5: Chapter-level finalization

After all sections are complete:

1. **Cross-section deduplication**: Scan the full chapter for identical or near-identical statements appearing in multiple sections. For each duplicate, decide where the statement lives as the primary instance vs where it becomes a brief cross-reference. Present duplicates to the author for confirmation.
2. **Verify all citations are from Zotero** (sanity check — they came from the research agent).
3. **Update the parent plan** if structural changes occurred during any section's review.
4. **Present chapter for final approval.**

**CHECKPOINT REMINDER:** When the author gives final chapter approval, write a comprehensive checkpoint entry covering the full chapter before proceeding.

The finalised plan should be **directly prosifiable** by the writer skill — every paragraph is a list of specific, cited statements that the writer converts to flowing prose without adding content.

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
- Neuron anatomy: soma (nucleus), dendrites (receive), axon (transmit), synaptic terminals (output) `(citable)`
  - \cite{key} p. [page] — [what it supports]
  - \cite{key2} p. [page] — [what it supports]
- Myelin sheaths with nodes of Ranvier → saltatory conduction → increased velocity `(citable)`
  - \cite{key3} p. [page] — [what it supports]
- Signal flow unidirectional: dendrites → soma → axon → terminals `(citable)`

→ **Figure**: [Descriptive label — what it shows, type]

#### Paragraph 2 — (Topic Label)
- Resting membrane potential ~−70 mV; arises from ion gradients + selective permeability `(citable)`
  - \cite{key} p. [page] — [what it supports]
- Na⁺/K⁺-ATPase maintains gradients: 3 Na⁺ out, 2 K⁺ in per cycle `(citable)`
  - ⚠ Gap — no source found

[continue for all paragraphs and sections]

## Open Questions
- [Gaps awaiting sources]
- [Structural decisions deferred to writing phase]

## Notes for Writer
- [Style guidance, emphasis, tone]
- CRITICAL: Do not add statements, facts, or assertions not present in this plan.
  If a transition requires stating something not in the plan, flag it.
```

## Handling Insufficient Coverage

When Zotero library lacks sufficient references:

**Do NOT**:
- Fabricate references
- Silently skip topics

**Do**:
1. Document the gap explicitly in the plan's Open Questions
2. Tell the user: "The Zotero library has limited coverage of [topic]. Options: (a) de-emphasize this topic, (b) proceed with available material and note the gap."
3. Wait for user decision

## Scope Flexibility

This skill works at any granularity:

- **Whole thesis**: Chapter map, narrative thread, cross-chapter analysis
- **Full chapter**: All sections to statement level
- **Single section**: Statement-level planning within one section
- **Single subsection**: Detailed statement planning for a focused topic

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
- Every citable statement backed by Zotero reference (or explicitly flagged as gap)
- Distinguish author's view from paper's conclusion
- Flag potential citation issues early

## Autonomy Level

**Low.** This skill operates collaboratively at every stage:

- **Phase 1** (Read/Reconcile): Report findings, ask about discrepancies
- **Phase 2** (Narrative Structure): Propose, discuss, iterate — do not finalise without author agreement
- **Phase 3** (Statement Expansion): Expand statements autonomously, research autonomously, but present all results for author review and haggling
- **Phase 3, Step 4** (Deduplicate and commit): Present complete plan for approval

The only autonomous actions are: reading files, expanding paragraph stubs (pre-review), spawning research agents, and writing the plan.md once approved.

## Integration

- **Reads**: `.tex` file (authoritative existing content), directory-level `plan.md`, parent-level `plan.md`
- **Uses**: `zotero-research` agent (claim research, citation verification)
- **Produces**: directory-level `plan.md` files (statement-level, directly prosifiable)
- **Hands off to**: `writer` skill for LaTeX prose generation (writer must not add content beyond the plan)

## Authorship Checkpointing

After each plan block is approved by the author and written to `plan.md`, **silently append** a checkpoint entry to `authorship_log_draft.md` in the thesis project root. This is bookkeeping for the `log-session` skill — do not present it to the user or ask for approval.

### Checkpoint Format

```markdown
### Checkpoint — [Section/Subsection Reference] ([Phase])
- **Scope**: [What was planned in this block]

#### Provenance Summary
| Metric | Count |
|--------|-------|
| Initial AI proposal | [N] points in [M] paragraphs |
| Final approved | [N] points in [M] paragraphs |
| Surviving verbatim from initial | [N] |
| AI points modified by user | [N] |
| AI points deleted | [N] |
| User-dictated points | [N] |
| User-directed points (agent extracted) | [N] |
| Agent-suggested, accepted | [N] |
| Agent-suggested, rejected | [N] |
| Figures — user-suggested | [N] |
| Figures — agent-suggested | [N] |

#### Qualitative Notes
- **Key author decisions**: [2-5 bullets — structural choices, emphasis, scope decisions]
- **Key rejections**: [What the author rejected and why, if apparent]
- **Revision cycles**: [How many rounds before approval]

- **Files written**: [plan.md path]
```

**Computing the summary:** At checkpoint time, read the provenance baseline and all feedback rounds from the scratch file. Sum across rounds to produce the final counts. Delete the scratch file after writing the checkpoint.

### When to Checkpoint

Write a checkpoint whenever the author signals agreement to move on from the current block of work. This includes but is not limited to:
- Approving a proposed structure or plan block
- Accepting a rearrangement or restructuring
- Agreeing to a scope change or content removal
- Any "yes", "ok", "let's continue", "move on" that closes a negotiation and transitions to the next piece of work

The test: **did a decision just get made that a future reviewer would want to see attributed?** If yes, checkpoint.

Do NOT checkpoint on:
- Clarifying questions ("what do you mean by X?")
- Mid-negotiation back-and-forth before a decision is reached
- Purely mechanical actions (file reads, research spawning)

### Rules

- Keep entries terse — the `log-session` skill synthesises them later.
- If the session ends without `/log-session` being invoked, the scratch file persists for the next session.
- **Do not skip checkpoints.** Even if a block was approved quickly, record it — quick approval is meaningful data (author agreed with the agent's proposal).
