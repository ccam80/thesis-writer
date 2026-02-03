---
name: writer
description: Conversational LaTeX prose writer. Converts paragraph-level plans into flowing technical prose, asking about wording choices where ambiguous. Does not add content beyond the plan.
allowed-tools: [Read, Write, Edit, Bash, Task, AskUserQuestion]
---

# Writer

## Overview

This skill converts a paragraph-level plan (from `document-planner`) into publication-ready LaTeX prose. It is **conversational** — it asks the user about wording choices where the plan is ambiguous or multiple phrasings are defensible.

**Key principle**: The writer transforms planned content into prose. It does not add new claims, restructure sections, or make substantive decisions. Those belong in the planning phase.

## When to Use This Skill

- After `document-planner` has produced an approved `chapter_plan.md`
- When writing a specific section or set of paragraphs
- When revising prose that has already been drafted

## Inputs

1. **Paragraph-level plan**: The `chapter_plan.md` (or relevant section)
2. **Target scope**: Which paragraphs/sections to write
3. **Style reference**: Author reference documents if available (see below)

## Author Style Reference

Before writing, read these sources to calibrate tone, sentence structure, and technical vocabulary:

1. **Existing chapter .tex files** in the thesis subdirectories — these are the author's own writing and the primary style reference
2. **PDFs in `author_reference/`** — published papers or drafts by the author demonstrating their preferred prose style

Match the author's:
- Sentence length and complexity patterns
- Level of formality and hedging
- How they introduce and contextualise citations
- Paragraph structure and transition style
- Technical vocabulary choices

## Writing Principles

### Conciseness
- Every word must serve a purpose
- Remove filler phrases and redundant expressions
- Use active voice when possible
- Keep sentences focused on a single idea

### Clarity
- Avoid jargon unless essential for precision
- Define technical terms on first use
- Use consistent terminology throughout
- Structure complex ideas in digestible segments

### Precision
- Never add meaning not present in the plan
- Do not make claims beyond what is planned
- Use exact technical terminology
- Maintain scientific accuracy

### Modifiers
- Avoid adjectives unless strictly necessary to convey a concept
- Avoid adverbs unless they add essential meaning
- Let data and evidence speak for themselves
- Replace vague modifiers with specific measurements

## Conversational Behaviour

### When to Ask

Ask the user when:
- **Ambiguous emphasis**: The plan says "discuss X" but doesn't specify how much weight to give it
- **Wording choice**: Two equally valid phrasings exist and the author's preference matters
- **Technical framing**: A concept could be introduced from multiple angles
- **Transition logic**: How one paragraph connects to the next isn't obvious from the plan

### When NOT to Ask

Do not ask about:
- Standard LaTeX formatting (use conventions from `thesis-chapters` skill)
- Which citations to include (the plan specifies these)
- Section structure (the plan specifies this)
- Minor word choices that don't affect meaning

### Question Format

```
Writing §X.2 ¶3 (respiratory sinus arrhythmia mechanisms):

The plan lists two points:
1. RSA is primarily vagally mediated
2. Respiratory frequency modulates HRV spectral peaks

Options for framing:
a) Lead with the vagal mechanism, then show how respiration modulates it
b) Lead with the spectral observation, then explain the vagal mechanism behind it

Which better serves your argument in this chapter?
```

## LaTeX Output Standards

### Equations
Include equations where the plan indicates them. Number all equations, define all variables:

```latex
\begin{equation}
    HRV_{RMSSD} = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N-1}(RR_{i+1} - RR_i)^2}
    \label{eq:rmssd}
\end{equation}
where $RR_i$ is the $i$th RR interval and $N$ is the total number of intervals.
```

### Figures
Include figure placeholders where the plan specifies them:

```latex
\begin{figure}[tb]
    \centering
    \fbox{\parbox{0.8\textwidth}{
    \textbf{FIGURE PLACEHOLDER}\\[1em]
    \textit{Type:} [from plan]\\[0.5em]
    \textit{Description:} [from plan]\\[0.5em]
    \textit{Axes:} [from plan]\\[0.5em]
    \textit{Key features:} [what reader should observe]
    }}
    \caption{[Caption text]}
    \label{fig:label}
\end{figure>
```

### Cross-References
- Use `\cref{}` and `\Cref{}` for all references
- Use `\SI{}{}` for all units
- Use `align` environment for multi-line equations

### Citations
- Use `\cite{zotero_item_key}` with keys from the plan
- IEEE numeric style
- Do not add citations not in the plan without asking

## What This Skill Does NOT Do

1. **Does not create content** — only transforms planned content into prose
2. **Does not restructure** — follows the plan's paragraph order
3. **Does not format** — the `formatter` skill handles final LaTeX polish
4. **Does not verify references** — the `reviewer` skill handles verification
5. **Does not add citations** — uses only those specified in the plan

## Workflow

1. Read the `chapter_plan.md` for the target scope
2. Read any `author_reference/` documents for style guidance
3. For each paragraph in order:
   a. Review planned points and citations
   b. Draft the paragraph
   c. If ambiguous, ask the user (batch questions where possible)
4. Write output to the chapter's `subfiles/` directory
5. After each section, briefly confirm with the user before continuing

## Tense Conventions

- **Methods and results**: Past tense ("The signal was filtered...")
- **Established facts**: Present tense ("The heart rate is modulated by...")
- **Conclusions and implications**: Present tense ("These results suggest...")
- **Literature references**: Past tense ("Smith et al. demonstrated...")

## Integration

- **Receives from**: `document-planner` (paragraph-level chapter_plan.md)
- **Uses**: `references/thesis-style-guide.md` (IEEE style, equations, citations, terminology, pitfalls)
- **Produces**: LaTeX `.tex` files in `subfiles/`
- **Hands off to**: `formatter` skill for LaTeX polish, then `reviewer` skill

## Authorship Checkpointing

After each section of prose is approved by the author and written to the `.tex` file, **silently append** a checkpoint entry to `authorship_log_draft.md` in the thesis project root. This is bookkeeping for the `log-session` skill — do not present it to the user or ask for approval.

### Checkpoint Format

```markdown
### Checkpoint — [Section Reference] (prose)
- **Scope**: [Which paragraphs/section were written]
- **Wording decisions by author**: [Cases where the author chose between options or directed phrasing — 1-3 bullets]
- **Agent drafted without significant change**: [Paragraphs accepted as drafted or with minor edits]
- **Revision cycles**: [Rounds of feedback before approval]
- **Files written**: [.tex file path]
```

### When to Checkpoint

Write a checkpoint whenever the author signals agreement to move on from the current block of work. This includes but is not limited to:
- Confirming prose for a section or group of paragraphs
- Accepting a rewrite or revision
- Agreeing to a wording or framing choice after discussion
- Any "yes", "ok", "let's continue", "move on" that closes a negotiation and transitions to the next piece of work

The test: **did a decision just get made that a future reviewer would want to see attributed?** If yes, checkpoint.

Do NOT checkpoint on:
- Clarifying questions ("what do you mean by X?")
- Mid-negotiation back-and-forth before a decision is reached
- Purely mechanical actions (file reads, research spawning)

### Rules

- Keep entries terse — the `log-session` skill synthesises them later.
- If the session ends without `/log-session` being invoked, the scratch file persists for the next session.
- **Do not skip checkpoints.** Quick approvals are meaningful data.
