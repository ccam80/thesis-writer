---
name: log-session
description: "Synthesises an authorship log entry from session checkpoints and conversation context. Presents draft for author approval before appending to the project's authorship_log.md."
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Log Session

## Overview

This skill produces an auditable record of authorship for AI-assisted thesis writing sessions. It synthesises checkpoint notes (written silently by content-creating skills during the session) and any remaining conversation context into a structured log entry, then presents it for author review and approval before appending to the project's `authorship_log.md`.

The log is a **defensible paper trail** demonstrating the author's intellectual direction of the work: a record of decisions, rejections, and domain contributions, not a mechanical transcript.

## Inputs

1. **Checkpoint scratch file**: `authorship_log_draft.md` in the thesis project root, written incrementally by `document-planner` and `writer` during the session
2. **Conversation context**: whatever remains in the context window at invocation time
3. **Existing log**: `authorship_log.md` in the thesis project root, for the cumulative summary

## Process

### Step 1: Gather Material

1. Read `authorship_log_draft.md` if it exists
2. Scan current conversation context for work done since the last checkpoint
3. Read the current `authorship_log.md` cumulative summary, if it exists, to update running totals

### Step 2: Analyse Checkpoints

Each checkpoint records scope and phase, author decisions and rejections, files written, and a revision-cycle count. Grounded-scope checkpoints add point IDs added, changed, removed, or retyped; provenance counts by point type; research request IDs; and corpus gaps. Ungrounded-phase checkpoints carry no per-type provenance.

Aggregate across checkpoints:

- author decisions and rejections, kept concrete;
- point IDs touched and per-type provenance counts for grounded scopes;
- research request IDs and corpus gaps;
- files written and revision cycles.

From checkpoint notes and conversation context, identify:

**Author direction** — instances where the author introduced a technical point, claim, or structural choice; rejected an agent suggestion (with brief reason if apparent); modified an agent suggestion before accepting; provided domain knowledge not available in the literature; or redirected emphasis, ordering, or scope.

**Agent contributions** — instances where the agent proposed structure or content that was accepted without significant modification, suggested references from Zotero that were accepted, or performed organisational work (sequencing, grouping, formatting).

**Iteration indicators** — scopes that required multiple revision cycles before approval, and the approximate exchange count.

### Step 3: Draft Session Entry

```markdown
## Session [DATE] — [Scope Description]

**Exchanges**: ~[N] | **Skills used**: [list]
**Checkpoints captured**: [N]

### Scope
[1-2 sentences: what was worked on this session]

### Content Provenance (grounded scopes only)

| Metric | Value |
|--------|-------|
| Grounded points in scope | [N] |
| By type | CLAIM [N], PROJECT_FACT [N], DERIVATION [N], AUTHOR_ASSERTION [N], INFERENCE [N] |
| Points added / changed / removed / retyped | [N] / [N] / [N] / [N] |
| Research requests | [N] |
| Corpus gaps | [N] |
| Revision cycles | [N] |

**Summary**: [1-2 sentence plain-language interpretation of the session's authorship balance, grounded in the decision record]

### Author Direction
- [Concrete decisions, rejections, and domain contributions — 3-8 bullet points]
- [Each bullet specific enough to demonstrate intellectual control]
- [Include section/paragraph references where possible]

### Agent Contributions
- [What the agent provided — structural organisation, reference suggestions, prose drafting]
- [Be honest about agent-originated content that was accepted]

### Iteration & Negotiation
- [Scopes that required significant back-and-forth]
- [Key points of disagreement and how they were resolved]

### Files Modified
- [Files written or edited during the session]
```

### Step 4: Present for Author Approval

Present the draft entry as a complete block. The author will approve as-is, request specific corrections (misattributed decisions, missing context, inaccurate characterisation), or add points the log missed.

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
- **Tool**: Codex [model/version], thesis-writer plugin v[version]
- **Process**: All content planned collaboratively via document-planner,
  prose drafted via writer skill from approved plans. All citations from
  author's Zotero library. Author reviewed and approved all output.

### Cumulative Provenance (grounded scopes only)
| Metric | Total |
|--------|-------|
| Grounded points | [N] |
| By type | CLAIM [N], PROJECT_FACT [N], DERIVATION [N], AUTHOR_ASSERTION [N], INFERENCE [N] |
| Corpus gaps open / resolved | [N] / [N] |

---

[Session entries in reverse chronological order]
```

## What This Skill Does NOT Do

- Does not modify any thesis content (plans, .tex files, figures)
- Does not assess quality or correctness of the work
- Does not fabricate or embellish the author's contributions
- Does not include full conversation transcripts

## Honesty Policy

The log must be **accurate, not flattering**. Report the checkpoint record as captured, not as the agent wishes it were.

- If the author rejected most agent suggestions, report the rejections honestly.
- If the agent's main contribution was organisational (sequencing, formatting) rather than substantive content, say so.
- If the author dictated nearly all content and the agent transcribed, that is valuable work but not agent authorship — characterise it accurately.
- Attribute each point's substance to whoever introduced it: content generated from the author's stated narrative goal is the author's intellectual contribution; content the agent proposed unprompted is the agent's.
- Report only counts the checkpoints actually recorded. Do not compute ratios or percentages from data the checkpoints do not contain.

The value of this log is its credibility — an honest record protects the author far better than a sanitised one.

## Edge Cases

- **No checkpoints exist**: Analyse conversation context only. Note in the entry that no mid-session checkpoints were captured, and omit the Content Provenance table.
- **Session was purely formatting/review**: Note that no authorship-relevant decisions were made — formatting and review are mechanical. Omit the Content Provenance section.
- **Session was purely writing (not planning)**: Writing sessions convert existing plans to prose. Note "Writing session — provenance established during planning." Do not double-count content.
- **Very short session**: Still log it. A 10-minute correction session is worth recording.
- **Context heavily compacted**: Rely primarily on checkpoint notes. Note that context was compacted and detail may be limited.
- **Mixed session (planning + writing)**: Count provenance only for the grounded planning scopes. Writing is mechanical conversion of already-attributed content.
- **Only ungrounded-phase checkpoints (structure, paragraph, or sentence phases)**: Omit the Content Provenance table; the decision record still fills Author Direction and Agent Contributions.
