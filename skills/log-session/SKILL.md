---
name: log-session
description: Synthesises an authorship log entry from session checkpoints and conversation context. Presents draft for author approval before appending to the project's authorship_log.md.
allowed-tools: [Read, Write, Edit, AskUserQuestion]
---

# Log Session

## Overview

This skill produces an auditable record of authorship for AI-assisted thesis writing sessions. It synthesises checkpoint notes (written silently by content-creating skills during the session) and any remaining conversation context into a structured log entry, then presents it for author review and approval before appending to the project's `authorship_log.md`.

The log serves as a **defensible paper trail** demonstrating the author's intellectual direction of the work — not a mechanical transcript, but a record of decisions, rejections, and domain contributions.

## When to Use This Skill

- At the end of a thesis writing session (planning, writing, or revision)
- When the context window is approaching capacity (10% remaining warning)
- The user invokes `/log-session`

## Inputs

1. **Checkpoint scratch file**: `authorship_log_draft.md` in the thesis project root, written incrementally by `document-planner` and `writer` during the session
2. **Conversation context**: Whatever remains in the context window at invocation time
3. **Existing log**: `authorship_log.md` in the thesis project root (to read cumulative summary)

## Process

### Step 1: Gather Material

1. Read `authorship_log_draft.md` if it exists — these are the mid-session checkpoints captured while context was fresh
2. Scan current conversation context for any work done since the last checkpoint
3. Read the current `authorship_log.md` cumulative summary (if it exists) to update running totals

### Step 2: Analyse Provenance Data

Checkpoints from `document-planner` contain structured provenance tables. Extract and aggregate these.

#### 2a: Extract Quantitative Provenance

For each checkpoint with a Provenance Summary table, extract:
- Initial AI proposal counts (points, paragraphs)
- Final approved counts
- Surviving verbatim from initial
- AI points modified/deleted
- User-dictated points
- User-directed points
- Agent-suggested accepted/rejected
- Figure attribution

**Aggregate across all checkpoints** to produce session totals.

#### 2b: Compute Provenance Metrics

From the aggregated data, compute:

| Metric | Formula |
|--------|---------|
| **AI survival rate** | (surviving verbatim) / (initial AI points) |
| **User content ratio** | (user-dictated + user-directed) / (final points) |
| **Agent acceptance rate** | (agent-suggested accepted) / (agent-suggested total) |
| **Figure attribution** | user-suggested / total figures |

#### 2c: Categorise Qualitative Contributions

From checkpoint qualitative notes and conversation context, identify:

**Author direction** — instances where the author:
- Introduced a technical point, claim, or structural choice
- Rejected an agent suggestion (with brief reason if apparent)
- Modified an agent suggestion before accepting
- Provided domain knowledge not available in the literature
- Redirected emphasis, ordering, or scope

**Agent contributions** — instances where the agent:
- Proposed structure or content that was accepted without significant modification
- Suggested references from Zotero that were accepted
- Performed organisational work (sequencing, grouping, formatting)

**Iteration indicators**:
- Sections/blocks that required multiple revision cycles before approval
- Total exchange count (approximate if context has been compacted)

### Step 3: Draft Session Entry

Produce a structured entry in this format:

```markdown
## Session [DATE] — [Scope Description]

**Exchanges**: ~[N] | **Skills used**: [list]
**Checkpoints captured**: [N]

### Scope
[1-2 sentences: what was worked on this session]

### Content Provenance

| Metric | Value |
|--------|-------|
| Initial AI generation | [N] points in [M] paragraphs |
| Final approved | [N] points in [M] paragraphs |
| Surviving verbatim from AI | [N] ([X]%) |
| User-dictated content | [N] points ([X]%) |
| User-directed content | [N] points ([X]%) |
| Agent-suggested, accepted | [N] points ([X]%) |
| Agent-suggested, rejected | [N] points |
| Figures — user | [N] |
| Figures — agent | [N] |

**Summary**: [1-2 sentence plain-language interpretation, e.g., "The author extensively restructured and expanded the initial AI proposal. Of 120 final points, 108 were user-contributed; all 12 figures were user-suggested."]

### Author Direction
- [Concrete decisions, rejections, and domain contributions — 3-8 bullet points]
- [Each bullet should be specific enough to demonstrate intellectual control]
- [Include section/paragraph references where possible]

### Agent Contributions
- [What the agent provided — structural organisation, reference suggestions, prose drafting]
- [Be honest about agent-originated content that was accepted]

### Iteration & Negotiation
- [Sections that required significant back-and-forth]
- [Key points of disagreement and how they were resolved]

### Files Modified
- [List of files written or edited during the session]
```

### Step 4: Present for Author Approval

Present the draft entry as a complete block. The author will:
- Approve as-is
- Request specific corrections (misattributed decisions, missing context, inaccurate characterisation)
- Add points the log missed

Handle corrections conversationally — update the draft and re-present until approved.

**Do NOT**:
- Ask open-ended questions ("anything else to add?")
- Present the entry piecemeal
- Skip this approval step

### Step 5: Append to Log

Once approved:

1. **Append** the entry to `authorship_log.md` in the thesis project root
2. **Update the cumulative summary** at the top of the file (create it if this is the first entry)
3. **Delete** `authorship_log_draft.md` (the scratch file is consumed)

### Cumulative Summary Format

The top of `authorship_log.md` contains a running summary updated each session:

```markdown
# Authorship Log

## Cumulative Summary
- **Sessions logged**: [N]
- **Chapters/sections covered**: [list]
- **Total exchanges**: ~[N]
- **Tool**: Claude Opus [version], thesis-writer plugin v[version]
- **Process**: All content planned collaboratively via document-planner,
  prose drafted via writer skill from approved plans. All citations from
  author's Zotero library. Author reviewed and approved all output.

### Cumulative Provenance (planning sessions only)
| Metric | Total |
|--------|-------|
| Points planned | [N] |
| User-contributed (dictated + directed) | [N] ([X]%) |
| Agent-contributed (accepted proposals) | [N] ([X]%) |
| Figures — user-suggested | [N] |
| Figures — agent-suggested | [N] |

---

[Session entries in reverse chronological order]
```

## What This Skill Does NOT Do

- Does not modify any thesis content (plans, .tex files, figures)
- Does not assess quality or correctness of the work
- Does not fabricate or embellish the author's contributions
- Does not include full conversation transcripts (too verbose, out of context)

## Honesty Policy

The log must be **accurate, not flattering**. The quantitative provenance data provides an objective foundation — report the numbers as computed, not as the agent wishes they were.

**Specific honesty requirements:**

- If the AI survival rate is 0%, say so: "No initial AI-generated points survived to the final plan."
- If the author rejected most agent suggestions, report the rejection count honestly.
- If the agent's main contribution was organisational (sequencing, formatting) rather than substantive content, say so.
- If the author dictated nearly all content and the agent transcribed, that's valuable work but not authorship — characterise it accurately.
- Do not conflate "user-directed" (agent generated points from user's narrative goal) with "agent-suggested" (agent proposed without prompting). The former is author intellectual contribution; the latter is agent intellectual contribution.

The value of this log is its credibility — an honest record protects the author far better than a sanitised one. A log showing "Author extensively restructured initial AI proposal, contributed 90% of final content" is far more defensible than vague claims of "collaborative development."

## Edge Cases

- **No checkpoints exist**: Analyse conversation context only. Note in the entry that no mid-session checkpoints were captured (less detail available). Omit the Content Provenance table or note "Provenance data not captured."
- **Checkpoints lack provenance tables**: Older checkpoints may use the qualitative-only format. Extract what information is available and note "Partial provenance data — some checkpoints predate structured tracking."
- **Session was purely formatting/review**: Note that no authorship-relevant decisions were made — formatting and review are mechanical. Omit the Content Provenance section (it doesn't apply).
- **Session was purely writing (not planning)**: Writing sessions convert existing plans to prose. Note "Writing session — provenance established during planning." Do not double-count content.
- **Very short session**: Still log it. A 10-minute correction session is worth recording. If only a few points were touched, provenance table may be trivial — include it anyway for completeness.
- **Context heavily compacted**: Rely primarily on checkpoint notes. Note that context was compacted and detail may be limited.
- **Mixed session (planning + writing)**: Only count provenance for the planning portion. Writing is mechanical conversion of already-attributed content.
