---
name: log-session
description: "Derives the session's authorship tally from the conversation and the plan diff at session end. Presents draft for author approval before appending to the project's authorship_log.md, the only place authorship is recorded."
allowed-tools: [Read, Write, Edit, Bash, AskUserQuestion]
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Log Session

## Overview

This skill produces an auditable record of authorship for AI-assisted thesis writing sessions. At session end it derives the session's authorship tally from the conversation and the plan diff, presents an entry for author review, and appends the approved entry to the project's `authorship_log.md`.

The log is a **defensible paper trail** demonstrating the author's intellectual direction of the work: a record of decisions, rejections, and domain contributions, not a mechanical transcript.

`authorship_log.md` is the only place authorship is recorded. `plan.md`, `evidence.md`, and drafted `.tex` files carry no authorship or approval-stage field, and no mid-session scratch file exists. Do not read, write, or restore `authorship_log_draft.md`; if one is present it is a stale artifact of a retired format, and its contents are plan bookkeeping rather than authorship evidence.

## Inputs

1. **Conversation context**: the session's exchanges, the primary source for who proposed, challenged, or edited each point
2. **Plan diff**: `git diff` over the project's `plan.md` and `evidence.md` files, bounding the structural counts independently of recall
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

The diff bounds points recorded and the added or changed subtotals. The attribution split between the last two rows comes from the conversation, because a point the author accepted verbatim and a point the author dictated are identical in the file and differ only in the exchange.

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
- If the author dictated nearly all content and the agent transcribed, that is valuable work but not agent authorship — characterise it accurately.
- Attribute each point's substance to whoever introduced it: content generated from the author's stated narrative goal is the author's intellectual contribution; content the agent proposed unprompted is the agent's.
- A count the session cannot support is reported as an estimate and marked as one. Do not compute ratios or percentages the counts do not contain.
- Report the agent-suggested-unchallenged count even when it is unflattering. A point that reached the plan without author scrutiny is the single most important number in this log.

The value of this log is its credibility — an honest record protects the author far better than a sanitised one.

## Edge Cases

- **No git baseline**: Derive all counts from conversation and state that the diff was unavailable.
- **Session was purely formatting or review**: Note that no authorship-relevant decisions were made; formatting and review are mechanical. Omit the Authorship Tally.
- **Session was purely writing, not planning**: Writing converts existing plans to prose. Note "Writing session — authorship established during planning." Do not double-count content.
- **Very short session**: Still log it. A 10-minute correction session is worth recording.
- **Mixed session, planning and writing**: Tally the planning scope only. Writing is mechanical conversion of already-attributed content.
- **A stale `authorship_log_draft.md` exists**: Do not merge it into the entry. Report its presence to the author and let them decide whether to delete it.
