---
name: log-session
description: "Derives the session's authorship tally from the conversation and the diff of plans and prose at session end. Presents a draft for author approval before appending to the project's authorship_log.md, the only place authorship is recorded."
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Log Session

## Overview

This skill produces an auditable record of authorship for AI-assisted thesis writing sessions. At session end it derives the session's authorship tally from the conversation and the diff of the plans and prose, presents an entry for author review, and appends the approved entry to the project's `authorship_log.md`.

The log records the author's decisions, rejections, and domain contributions. It is not a transcript.

`authorship_log.md` is the only place authorship is recorded. `plan.md` and `.tex` files carry no authorship field. Write no authorship file during the session.

## Inputs

1. **Conversation context**: the session's exchanges. Gives who proposed, challenged, wrote, or edited each point and paragraph.
2. **Diff**: `git diff` over the project's `plan.md` and `.tex` files. Gives the structural counts.
3. **Existing log**: `authorship_log.md` in the thesis project root, for the cumulative summary.

## Process

### Step 1: Establish the diff baseline

Determine the project root and confirm it is a git repository. Establish the session's baseline commit: the most recent commit made before this session's first edit, found with `git log` over the plan and prose files. State the baseline explicitly in the entry.

Collect the change with `git diff <baseline> -- '*plan.md' '*.tex'`. If the project is not a git repository, or the working tree was already dirty at session start so no clean baseline exists, say so in the entry and derive every count from conversation alone.

### Step 2: Derive the session tally

| Count | Definition |
|---|---|
| Points recorded | Plan points written or rewritten this session |
| Agent-suggested, unchallenged | Points the agent proposed that entered the plan with no author edit or objection |
| Edited or added by the author | Points the author dictated, added, reworded, or altered after an agent proposal |
| Paragraphs written by the author | Prose paragraphs the author wrote or substantially rewrote |
| Paragraphs drafted by the agent | Prose paragraphs the agent drafted at the author's request, whether or not the author then edited them |
| Agent edits to author prose | Corrections the agent applied to the author's prose: mechanical fixes, sweep fixes, and approved rewordings |

The second and third rows partition the first. Take points recorded and paragraph counts from the diff where it can separate them, and the split between agent and author from the conversation.

The tally is a session aggregate. Do not track authorship per point or per sentence, and do not reconstruct a per-item history.

### Step 3: Identify the decision record

From the conversation, identify:

**Author direction**: where the author introduced a technical point, claim, or structural choice; rejected an agent suggestion, with brief reason if apparent; modified an agent suggestion before accepting; supplied domain knowledge not available in the literature; or redirected emphasis, ordering, or scope.

**Agent contributions**: where the agent proposed structure or content accepted without significant modification, caught a technical error, suggested Zotero references that were accepted, drafted prose on request, or performed organisational work such as sequencing, grouping, or formatting.

**Iteration indicators**: scopes that required several revision rounds, and the approximate exchange count.

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
| Agent-suggested, unchallenged | [N] |
| Edited or added by the author | [N] |
| Paragraphs written by the author | [N] |
| Paragraphs drafted by the agent | [N] |
| Agent edits to author prose | [N] |

**Summary**: [1-2 sentence plain-language interpretation of the session's authorship balance]

### Author Direction
- [Concrete decisions, rejections, and domain contributions — 3-8 bullet points]
- [Each bullet specific enough to demonstrate intellectual control]
- [Include section/paragraph references where possible]

### Agent Contributions
- [What the agent provided — structure, error catches, reference suggestions, drafted paragraphs]
- [Be honest about agent-originated content that was accepted]

### Iteration & Negotiation
- [Scopes that required significant back-and-forth]
- [Key points of disagreement and how they were resolved]

### Files Modified
- [Files written or edited during the session]
```

### Step 5: Present for author approval

Present the draft entry as a complete block. The author will approve it as it stands, request specific corrections, or add points the log missed. Apply corrections and present the entry again until approved.

Do not ask open-ended questions such as "anything else to add?", present the entry piecemeal, or skip this approval step.

### Step 6: Append to log

Once approved:

1. **Append** the entry to `authorship_log.md` in the thesis project root.
2. **Update the cumulative summary** at the top of the file, creating it if this is the first entry.

### Cumulative summary format

```markdown
# Authorship Log

## Cumulative Summary
- **Sessions logged**: [N]
- **Chapters/sections covered**: [list]
- **Total exchanges**: ~[N]
- **Tool**: Codex [model/version], thesis-writer plugin v[version]
- **Process**: Prose written by the author, with structure, review, and
  occasional drafting by the agent. All citations from the author's Zotero
  library. Author reviewed and approved all agent output.

### Cumulative Authorship Tally
| Count | Total |
|--------|-------|
| Points recorded | [N] |
| Agent-suggested, unchallenged | [N] |
| Edited or added by the author | [N] |
| Paragraphs written by the author | [N] |
| Paragraphs drafted by the agent | [N] |
| Agent edits to author prose | [N] |

---

[Session entries in reverse chronological order]
```

## What This Skill Does Not Do

- Does not modify any thesis content (plans, `.tex` files, figures).
- Does not write authorship fields into any plan or `.tex` file.
- Does not assess the quality or correctness of the work.
- Does not fabricate or embellish the author's contributions.
- Does not include full conversation transcripts.

## Honesty Policy

The log must be accurate, not flattering. Report the session as it happened.

- If the author rejected most agent suggestions, report the rejections.
- If the agent's main contribution was organisational rather than substantive, say so.
- If the author dictated nearly all content and the agent transcribed, record it as author content.
- Attribute each point's substance to whoever introduced it. Content generated from the author's stated narrative goal is the author's; content the agent proposed unprompted is the agent's.
- Count every paragraph the agent drafted, including ones the author later edited.
- Mark any count the session cannot support as an estimate. Do not compute ratios or percentages the counts do not contain.
- Report the agent-suggested-unchallenged count even when it is unflattering.

## Edge Cases

- **No git baseline**: derive all counts from conversation and state that the diff was unavailable.
- **Formatting or review only**: state that no authorship-relevant decisions were made and omit the tally.
- **Very short session**: still log it.
