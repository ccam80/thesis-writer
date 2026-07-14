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

## Style Authorities

Read both before drafting anything:

1. **`references/prose-style.md`** — the binding prose voice rules: density, banned modifiers, banned AI sentence patterns, em-dash policy, register, paragraph flow. Every prose chunk is checked against its pre-presentation checklist before the author sees it.
2. **The author's own writing** — existing chapter `.tex` files and PDFs in `author_reference/`. This is the ultimate voice reference; where it and prose-style.md differ, the author's demonstrated style wins (flag the difference rather than silently choosing). Match sentence length, hedging level, how citations are introduced, and transition style.

## Writing Principles

- **Precision**: Never add meaning not present in the plan. No claims beyond what is planned. Exact technical terminology, defined on first use, used consistently.
- **Density**: One fact per sentence, fewest words that carry the claim (prose-style.md §1). First drafts run about twice as long as needed.
- **No AI prose tics**: The banned-pattern and banned-modifier lists in prose-style.md §2–§4 are hard rules, not preferences. A draft containing a contrast scaffold, staccato drama, an intensifier, or an em-dash interpolation is not ready to present.

## Drafting Protocol (per paragraph or section)

Three passes, always, before the author sees anything:

1. **Draft** from the plan's statements — wording, transitions, and joins only; no new content.
2. **Cut pass**: run the sentence-level information test (prose-style.md §8). For each sentence, name the new information it carries; cut sentences that frame, restate, or exist for rhythm. Expect to cut substantially.
3. **Style scan**: run the prose-style.md pre-presentation checklist. Scan for `---`, banned modifiers, banned patterns. Fix per instance.

Present only the post-scan version. Do not present a draft and offer to tighten it later — the tightening is part of drafting.

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
Writing §X.2 ¶3 (feedback loop stability):

The plan lists two points:
1. Loop gain determines the settling time
2. Sampling rate limits the achievable closed-loop bandwidth

Options for framing:
a) Lead with the loop-gain mechanism, then show how sampling rate constrains it
b) Lead with the bandwidth observation, then explain the loop-gain mechanism behind it

Which better serves your argument in this chapter?
```

## LaTeX Output Standards

### Equations
Include equations where the plan indicates them. Number all equations, define all variables:

```latex
\begin{equation}
    x_{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}
    \label{eq:rms}
\end{equation}
where $x_i$ is the $i$th sample of the signal and $N$ is the total number of samples.
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
\end{figure}
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
2. Read `references/prose-style.md`, then existing `.tex` prose and any `author_reference/` documents for voice calibration
3. For each paragraph in order:
   a. Review planned points and citations
   b. Run the three-pass drafting protocol (draft → cut pass → style scan)
   c. If ambiguous, ask the user (batch questions where possible)
4. Write output to the chapter's `subfiles/` directory
5. After each section, briefly confirm with the user before continuing

## Tense Conventions

- **Methods and results**: Past tense ("The signal was filtered...")
- **Established facts**: Present tense ("The output voltage is determined by...")
- **Conclusions and implications**: Present tense ("These results suggest...")
- **Literature references**: Past tense ("Smith et al. demonstrated...")

## Integration

- **Receives from**: `document-planner` (paragraph-level chapter_plan.md)
- **Uses**: `references/prose-style.md` (binding prose voice rules), `references/thesis-style-guide.md` (IEEE style, equations, citations, terminology, pitfalls)
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
