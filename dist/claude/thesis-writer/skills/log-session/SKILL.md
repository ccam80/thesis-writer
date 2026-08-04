---
name: log-session
description: "Derives the session's authorship tally from the conversation and the plan diff at session end. Presents draft for author approval before appending to the project's authorship_log.md, the only place authorship is recorded."
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion]
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Log Session

## Overview

This skill produces an auditable record of authorship for AI-assisted thesis writing sessions. At session end it derives the session's authorship tally from the conversation and the plan diff, presents an entry for author review, and appends the approved entry to the project's `authorship_log.md`.

The log records the author's decisions, rejections, and domain contributions. It is not a transcript.

`authorship_log.md` is the only place authorship is recorded. `plan.md`, `evidence.md`, and drafted `.tex` files carry no authorship or approval-stage field. Write no authorship file during the session.

## Inputs

1. **Conversation context**: the session's exchanges. Gives who proposed, challenged, or edited each point.
2. **Plan diff**: `git diff` over the project's `plan.md` and `evidence.md` files. Gives the structural counts.
3. **Existing log**: `authorship_log.md` in the thesis project root, for the cumulative summary

## Process

### Step 1: Establish the diff baseline

Determine the project root and confirm it is a git repository. Establish the session's baseline commit: the most recent commit made before this session's first edit, found with `git log` over the plan files. State the baseline explicitly in the entry.

Collect the structural change with `git diff <baseline> -- '*plan.md' '*evidence.md'`. If the project is not a git repository, or the working tree was already dirty at session start so no clean baseline exists, say so in the entry and derive every count from conversation alone.

### Step 2: Derive the session tally

Count sentence points across the session's scope:

| Count | Definition |
|---|---|
| Points recorded | Sentence points written or rewritten in the scope this session |
| Adjusted by grounding | Points whose text changed as a result of the grounding pass |
| Agent-suggested, unchallenged | Points the agent proposed that entered the plan with no author edit or objection |
| Edited or added by the author | Points the author dictated, added, reworded, or altered after an agent proposal |

The last two partition the recorded total. Grounding adjustments are orthogonal and overlap both.

Take points recorded and the added or changed subtotals from the diff. Take the split between the last two rows from the conversation; the diff cannot separate them.

The tally is a session aggregate. Do not track authorship per point, do not enumerate point IDs, and do not reconstruct a per-point history.

### Step 3: Identify the decision record

From the conversation, identify:

**Author direction** — where the author introduced a technical point, claim, or structural choice; rejected an agent suggestion, with brief reason if apparent; modified an agent suggestion before accepting; supplied domain knowledge not available in the literature; or redirected emphasis, ordering, or scope.

**Agent contributions** — where the agent proposed structure or content accepted without significant modification, suggested Zotero references that were accepted, or performed organisational work such as sequencing, grouping, or formatting.

**Iteration indicators** — scopes that required multiple revision cycles before approval, and the approximate exchange count.

### Step 4: Draft the session entry

```markdown
## Session [DATE] — [Scope Description]

**Exchanges**: ~[N] | **Skills used**: [list]
**Diff baseline**: [commit | none, stated reason]

### Scope
[1-2 sentences: what was worked on this session]

### Authorship Tally

| Count | Value |
|--------|-------|
| Points recorded | [N] |
| Adjusted by grounding | [N] |
| Agent-suggested, unchallenged | [N] |
| Edited or added by the author | [N] |

**Summary**: [1-2 sentence plain-language interpretation of the session's authorship balance]

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

### Step 5: Present for author approval

Present the draft entry as a complete block. The author will approve as-is, request specific corrections (misattributed decisions, missing context, inaccurate characterisation), or add points the log missed.

Handle corrections conversationally — update the draft and re-present until approved.

**Do NOT**:
- Ask open-ended questions ("anything else to add?")
- Present the entry piecemeal
- Skip this approval step

### Step 6: Append to log

Once approved:

1. **Append** the entry to `authorship_log.md` in the thesis project root
2. **Update the cumulative summary** at the top of the file, creating it if this is the first entry

### Cumulative summary format

The top of `authorship_log.md` contains a running summary updated each session:

```markdown
# Authorship Log

## Cumulative Summary
- **Sessions logged**: [N]
- **Chapters/sections covered**: [list]
- **Total exchanges**: ~[N]
- **Tool**: Claude [model/version], thesis-writer plugin v[version]
- **Process**: All content planned collaboratively via document-planner,
  prose drafted via writer skill from approved plans. All citations from
  author's Zotero library. Author reviewed and approved all output.

### Cumulative Authorship Tally
| Count | Total |
|--------|-------|
| Points recorded | [N] |
| Agent-suggested, unchallenged | [N] |
| Edited or added by the author | [N] |

---

[Session entries in reverse chronological order]
```

## What This Skill Does NOT Do

- Does not modify any thesis content (plans, `.tex` files, figures)
- Does not write authorship, origin, or approval-stage fields into any plan, ledger, or `.tex` file
- Does not assess quality or correctness of the work
- Does not fabricate or embellish the author's contributions
- Does not include full conversation transcripts

## Honesty Policy

The log must be **accurate, not flattering**. Report the session as it happened, not as the agent wishes it had.

- If the author rejected most agent suggestions, report the rejections honestly.
- If the agent's main contribution was organisational rather than substantive, say so.
- If the author dictated nearly all content and the agent transcribed, record it as author content.
- Attribute each point's substance to whoever introduced it. Content generated from the author's stated narrative goal is the author's; content the agent proposed unprompted is the agent's.
- Mark any count the session cannot support as an estimate. Do not compute ratios or percentages the counts do not contain.
- Report the agent-suggested-unchallenged count even when it is unflattering.

## Edge Cases

- **No git baseline**: Derive all counts from conversation and state that the diff was unavailable.
- **Session was purely formatting or review**: State that no authorship-relevant decisions were made. Omit the Authorship Tally.
- **Session was purely writing, not planning**: State "Writing session — authorship established during planning." Do not tally the points again.
- **Very short session**: Still log it.
- **Mixed session, planning and writing**: Tally the planning scope only.
