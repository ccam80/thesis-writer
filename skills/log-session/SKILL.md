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

### Step 2: Analyse and Categorise

From checkpoints and context, identify:

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

---

[Session entries in reverse chronological order]
```

## What This Skill Does NOT Do

- Does not modify any thesis content (plans, .tex files, figures)
- Does not assess quality or correctness of the work
- Does not fabricate or embellish the author's contributions
- Does not include full conversation transcripts (too verbose, out of context)

## Honesty Policy

The log must be **accurate, not flattering**. If the agent originated a structural idea that the author accepted without modification, record it as an agent contribution. If the author rejected most agent suggestions and rebuilt from scratch, record that too. The value of this log is its credibility — an honest record protects the author far better than a sanitised one.

## Edge Cases

- **No checkpoints exist**: Analyse conversation context only. Note in the entry that no mid-session checkpoints were captured (less detail available).
- **Session was purely formatting/review**: Note that no authorship-relevant decisions were made — formatting and review are mechanical.
- **Very short session**: Still log it. A 10-minute correction session is worth recording.
- **Context heavily compacted**: Rely primarily on checkpoint notes. Note that context was compacted and detail may be limited.
