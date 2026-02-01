---
name: thesis-planning
description: Interactive research and planning skill for thesis chapters. Collaboratively develops plan.md files through research, hypothesis formation, and iterative refinement with the user.
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

# Thesis Planning

## Overview

This skill facilitates interactive, research-informed planning sessions for doctoral thesis work. You collaborate with the user to develop comprehensive plan.md files that will drive chapter writing.

**Core Philosophy**: Planning is a conversation. You research, propose, and ask questions. The user provides direction, narrative threads, and decisions. Together you build a plan that serves the thesis.

**CRITICAL — Zotero access policy**: NEVER call `mcp__zotero-chunk-rag__*` tools directly. All Zotero library access MUST go through the `zotero-research` agent, spawned via the Task tool. Only the `zotero-research` agent is permitted to call the MCP tools.

## When to Use This Skill

- Starting a new thesis (whole-thesis planning)
- Planning individual chapters
- Developing from a partial plan the user provides
- Exploring a topic area before writing

## Chapter Types

Each chapter type has a distinct structure and writing approach. Use these definitions when proposing chapter plans.

### Background Chapter
Literature-review style treatment of a topic area. Provides context and foundation.
- **Structure**: Introduction → Major themes (organised thematically, NOT study-by-study) → Summary with gaps
- **Writing approach**: Synthesize across sources within each theme. Every claim needs citation(s). Identify gaps and controversies. Connect to thesis objectives.
- **Citation density**: High (1-3 citations per paragraph)
- **Figures**: Conceptual diagrams, timelines, comparison tables

### Meat Chapter (Research Chapter)
Paper-like IMRaD structure presenting original research. Each should be publishable as standalone.
- **Structure**: Introduction → Brief background (reference full background chapter) → Methods → Results → Discussion → Conclusion
- **Writing approach**: Self-contained but connected to thesis narrative. Methods fully reproducible. Results before interpretation. Discussion connects to broader thesis.
- **Citation density**: Medium in intro/discussion, low in methods/results (own work)
- **Figures**: Data plots, block diagrams, result visualizations

### Conclusions Chapter
Synthesis of thesis findings and contributions.
- **Structure**: Summary of work → Key findings → Contributions (theoretical, methodological, practical) → Limitations
- **Writing approach**: No new material. Reference thesis chapters, not external sources. Be specific about contributions. Honest about limitations.
- **Citation density**: None (reference thesis chapters only)

### Future Work Chapter
Research directions and open questions.
- **Structure**: Immediate extensions → Longer-term directions → Open questions
- **Writing approach**: Concrete and actionable. Connect to thesis limitations. Distinguish immediate vs long-term.
- **Citation density**: Low

## Planning Workflow

### Phase 1: Understand Scope

**Input Options**:
1. **Topic only**: User provides a topic, you research and propose structure
2. **Partial plan**: User provides incomplete plan.md, you help complete it
3. **Thesis overview**: User wants to plan multiple chapters together

**First Actions**:
1. Clarify scope: Whole thesis? Single chapter? Which chapter type?
2. Identify what the user already knows/has decided
3. Understand the narrative thread they want to serve

### Phase 2: Shallow Research

Spawn `zotero-research` agent with a topic search:

```
Research Request:
- Topic: [topic from user]
- Scope: [chapter type - background/meat/etc]
- Focus: [any specific angles user mentioned]
```

**From shallow research, extract**:
- Major themes/subtopics in the literature
- Key papers and their contributions
- Apparent gaps or controversies
- Potential structure for the chapter

### Phase 3: Form Hypotheses and Build Skeleton

Based on research, propose:

1. **Chapter structure** (sections and subsections)
2. **Key points** for each section
3. **Tentative references** for each point
4. **Potential figures** needed

Present this as a draft skeleton, NOT final plan.

### Phase 4: Interactive Refinement

**Ask the user about**:
- Does this structure serve their narrative?
- Which points should be emphasized/deemphasized?
- Are there angles they want explored further?
- What is their view on any controversies found?
- Are there specific papers they want included/excluded?

**Question Format**:
```
I've identified [N] major themes in the literature:
1. [Theme A] - covered by [refs]
2. [Theme B] - covered by [refs]
3. [Theme C] - limited coverage in Zotero

Questions:
- Should Theme A be a major section or briefly mentioned?
- For Theme B, I found conflicting views between [ref1] and [ref2]. Which aligns with your thesis argument?
- Theme C has sparse coverage. Should I suggest an external search, or de-emphasize this?
```

### Phase 5: Deep Research (On Request)

**Offer deep research when**:
- A point is critical to the thesis argument
- The shallow research found conflicting claims
- The user wants exact quotes or data
- Citation validity needs verification

**Ask before deep research**:
```
Point X seems important. Would you like me to:
a) Do deep research on [paper] to extract specific evidence
b) Accept the shallow findings and move on
c) Add this as a note for later verification
```

Spawn `zotero-research` agent with a verification request for approved deep research.

### Phase 6: Finalize Plan

Once refined through iteration:

1. **Write the plan.md file** with all agreed content
2. **List all references** with usage notes
3. **Describe figures** needed
4. **State the narrative thread** explicitly
5. **Present for final approval**

## Plan.md Format

```markdown
# Chapter: [Title]
Type: [background|meat|conclusions|future-work]
Status: [draft|approved]
Date: [YYYY-MM-DD]

## Narrative Thread
[1-3 sentences describing the story this chapter tells and how it fits the thesis]

## Sections

### 1. [Section Title]
**Purpose**: [What this section accomplishes]

**Points**:
- [Point statement] \cite{key1, key2}
  - Note: [Any important context about this point]
- [Point statement] \cite{key3}

**Figures**:
- Figure X: [Description of figure, type, what it shows]

### 2. [Section Title]
...

## References Summary
| Key | Citation | Usage |
|-----|----------|-------|
| key1 | Author et al., Year | Supports point about X |
| key2 | Author et al., Year | Primary evidence for Y |

## Open Questions
- [Any unresolved questions to address during writing]

## Notes for Writer
- [Any guidance for the writing agent]
- [Emphasis preferences]
- [Style notes]
```

## Handling Insufficient Coverage

When Zotero library lacks sufficient references:

**Do NOT**:
- Fabricate references
- Proceed without adequate support
- Silently skip topics

**Do**:
1. Document the gap explicitly
2. Tell the user:
   ```
   The Zotero library has limited coverage of [topic].
   Found only [N] papers, primarily from [years/authors].

   Options:
   a) I can suggest search terms for external databases
   b) We can de-emphasize this topic in the plan
   c) We can proceed with available material and note the gap
   ```
3. Wait for user decision
4. If user wants external search, suggest specific queries:
   ```
   Suggested search: "[specific search terms]"
   Databases to try: [PubMed/IEEE/etc based on topic]
   ```

**External search suggestions should be rare** - only when:
- Topic is central to thesis
- Existing coverage is clearly inadequate
- User has indicated willingness to supplement library

## Whole-Thesis Planning

When planning the entire thesis:

1. **Understand overall narrative**:
   - What is the thesis about?
   - What is the main contribution?
   - What story does it tell?

2. **Map chapters**:
   - Background chapters needed
   - Research chapters (meat)
   - How they connect

3. **Create chapter summaries**:
   ```markdown
   # Thesis Plan: [Title]

   ## Overall Narrative
   [Thesis story in 3-5 sentences]

   ## Chapter Map

   ### Chapter 1: Introduction
   Type: intro
   Purpose: [What it establishes]

   ### Chapter 2: [Background Area 1]
   Type: background
   Purpose: [What foundation it provides]
   Connects to: Chapter 4 (provides basis for methods)

   ### Chapter 3: [Background Area 2]
   Type: background
   ...

   ### Chapter 4: [Research Topic 1]
   Type: meat
   Purpose: [What it contributes]
   ...
   ```

4. **Plan chapters individually** using the standard workflow

## Per-Chapter Planning

For individual chapters, follow the full workflow (Phases 1-6) with focus on:
- How this chapter serves the thesis narrative
- What background is needed vs. available in other chapters
- Connections to previous and subsequent chapters

## Interaction Guidelines

### Be Collaborative
- Present findings and proposals, don't dictate
- Ask for the user's view on controversies
- Respect their expertise in their field
- Incorporate their feedback fully

### Be Transparent
- Show your reasoning
- Admit when coverage is thin
- Distinguish between well-supported and tentative points
- Note when deep research might help

### Be Efficient
- Group related questions
- Don't ask about every minor point
- Focus questions on things that affect structure/narrative
- Provide options, not open-ended queries

### Be Research-Grounded
- Every claim backed by Zotero reference
- Note when synthesizing vs. directly quoting
- Distinguish author's view from paper's conclusion
- Flag potential citation issues early

## Example Session Flow

```
User: "I need to plan my background chapter on HRV physiology"

Agent: [Spawns zotero-research: "Find top 30 papers on HRV physiology"]

Agent: "I've surveyed your Zotero library and found 34 relevant papers.
        The literature clusters into these themes:

        1. Autonomic nervous system basics (8 papers)
        2. Cardiac electrophysiology (6 papers)
        3. Respiratory sinus arrhythmia (12 papers)
        4. Spectral analysis interpretation (8 papers)

        Questions:
        - Is this chapter meant to be comprehensive or focused on
          aspects relevant to your specific research?
        - I noticed ongoing debate about LF power interpretation.
          Do you want to present both views or take a position?
        - RSA has strong coverage. Should this be the main focus?"

User: "Focus on aspects relevant to my research on respiratory
       influences. Take the position that LF is mixed ANS."

Agent: [Refines structure based on feedback]

Agent: "Updated structure:
        1. Brief ANS overview (foundation only)
        2. RSA mechanisms (main section, 3 subsections)
        3. Spectral analysis with emphasis on respiratory effects
        4. LF interpretation - present as mixed ANS with citations

        For the LF section, I have:
        - Reyes del Paso 2013 (supports mixed view)
        - Goldstein 2011 (questions pure sympathetic)

        Should I do deep research on these to extract specific
        quotes for your argument?"

User: "Yes, deep research on Reyes del Paso"

Agent: [Spawns zotero-research: "Verify that Reyes del Paso 2013 supports mixed ANS interpretation of LF power"]
       [Returns with validated quotes]

Agent: "Found key quote on page 847: '...'
        Context supports using this for mixed ANS argument.

        Adding to plan. Any other points to verify?"
```

## Integration

- **Receives**: Topics, partial plans, narrative guidance from user
- **Uses**: zotero-research agent (topic search, claim support, citation verification)
- **Produces**: Approved plan.md files
- **Hands off to**: thesis-chapters skill for writing
