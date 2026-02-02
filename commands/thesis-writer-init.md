---
description: Initialize the current project with Thesis Writer - a Zotero-integrated doctoral thesis writing tool.
---

# Thesis Writer Project Setup

When the user runs `/thesis-writer:init`, do the following:

## Step 1: Check for Existing CLAUDE.md

1. Check if a `CLAUDE.md` file exists in the current working directory.

2. If it exists:
   - Ask the user whether to:
     - a) **Back up** the existing file as `CLAUDE.md.bak` and replace it with the Thesis Writer configuration, or
     - b) **Merge** the Thesis Writer settings into the existing file (append to end), or
     - c) **Cancel** the operation.

3. Wait for user response before proceeding.

## Step 2: Locate the Template File Path

**CRITICAL: Do NOT use the read_file tool. Only locate the file path.**

Find the path to the Thesis Writer template file using glob or list_dir:
- Look for `CLAUDE.thesis-writer.md` in the templates directory
- Try known plugin installation paths

Once you have the path, immediately proceed to Step 3.

## Step 3: Create or Update CLAUDE.md

Based on the user's choice (or create new if no existing file):

### Option A: Replace (with backup)
```bash
mv CLAUDE.md CLAUDE.md.bak
cp {template_path} CLAUDE.md
```

### Option B: Merge
```bash
echo -e "\n\n---\n\n# Thesis Writer Configuration (Added by Plugin)\n" >> CLAUDE.md
cat {template_path} >> CLAUDE.md
```

### Option C: Create New (Default)
```bash
cp {template_path} CLAUDE.md
```

## Step 4: Summarize What Was Installed

```
Thesis Writer has been initialized in this project!

What's Included:
- Zotero-integrated research and citation management
- Plan-driven thesis writing workflow
- IEEE-style formatting default

Core Workflow:
  - document-planner: Multi-scope interactive planning (thesis, chapter, section, subsection)
  - writer: LaTeX prose from plans (conversational)
  - figure-generator: Matplotlib plots and schematics from placeholders
  - formatter: LaTeX formatting checker
  - reviewer: Plan compliance and reference verification
  - zotero-research: Spawnable research agent (Zotero library)

Support Skills:
  - peer-review: Academic review methodology
  - markitdown: File conversion (PDF → Markdown)
  - latex-posters: Conference poster creation

Thesis Chapter Types:
- Background chapters: Literature-review style treatment
- Meat chapters: Paper-like IMRaD structure
- Conclusions: Synthesis and summary
- Future Work: Research directions

Getting Started:
1. Your CLAUDE.md file is now configured
2. Ensure the zotero-chunk-rag MCP server is enabled in Claude settings
3. Start with: "/document-planner" to begin planning a chapter

Plan.md Workflow:
- All writing starts from a plan.md file
- Points in the plan MUST appear in the document
- References in the plan MUST be cited in the document
- Use document-planner skill to develop plans interactively
```

## Step 5: Verify zotero-chunk-rag MCP

Remind the user:
- The zotero-chunk-rag MCP server must be enabled for research features
- Run a test query to verify: "Search my Zotero library for [topic]"
- If not working, see next_steps.md for setup instructions

## Error Handling

If template can't be found:
- Report the error
- Suggest checking plugin installation
- Offer to create minimal CLAUDE.md with thesis writing instructions
