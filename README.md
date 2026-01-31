# Claude Thesis Writer

A Claude Code plugin for plan-driven doctoral thesis writing with Zotero-sourced citations and IEEE-style LaTeX output.

## What It Does

Provides a structured skill chain for thesis writing:

```
thesis-planning → document-planner → writer → figure-generator → formatter → reviewer
                        ↕                                                       ↕
                  zotero-research                                         zotero-research
```

All citations come from your Zotero library. All writing follows collaboratively approved plans. Output is publication-ready LaTeX.

## Prerequisites

- **Claude Code** (or compatible IDE with Claude Code plugin support)
- **Zotero** with a populated library for your research area
- **Zotero MCP server** configured in Claude Code (provides `semantic_search`, `search_items`, `get_item`, `get_fulltext`, `get_annotations`)
- **LaTeX distribution** (TeX Live, MiKTeX, or similar) for compilation
- **Python 3.10+** with matplotlib (for figure generation)

## Installation

1. Add the plugin marketplace in Claude Code:
   ```
   /plugin marketplace add https://github.com/K-Dense-AI/claude-scientific-writer
   ```

2. Install the plugin:
   ```
   /plugin install claude-thesis-writer
   ```

3. Restart Claude Code when prompted.

4. Initialise in your thesis project:
   ```
   /thesis-writer:init
   ```
   This creates a `CLAUDE.md` with thesis writing instructions and makes all skills available.

## Skills

### Core Workflow

| Skill | Role |
|-------|------|
| `zotero-research` | Spawnable research agent — topic search, claim support, citation verification |
| `thesis-planning` | Chapter-level interactive planning (includes chapter type definitions) |
| `document-planner` | Paragraph-level planning with verified references and figure stubs |
| `writer` | LaTeX prose from plans (conversational, checks wording with user) |
| `figure-generator` | Generates matplotlib plots and schematics from figure placeholders |
| `formatter` | LaTeX formatting checker (packages, placement, units, cross-refs) |
| `reviewer` | Plan compliance and reference verification |

### Support

| Skill | Role |
|-------|------|
| `peer-review` | Academic review methodology |
| `markitdown` | File conversion (PDF → Markdown) |
| `latex-posters` | Conference poster creation |

## Quick Start

```
> I need to plan my background chapter on HRV physiology

[thesis-planning runs: searches Zotero, proposes structure, iterates with you]

> Approved. Now let's do detailed planning for section 2.

[document-planner runs: paragraph-level planning with verified references]

> Plan looks good, write it up.

[writer runs: produces LaTeX prose from the approved plan]
[figure-generator runs: creates plots from placeholders]
[formatter runs: checks LaTeX compliance]
[reviewer runs: verifies plan coverage and citation accuracy]
```

## Key Principles

- **Collaborative**: You are the domain expert. The agent organises your knowledge, never invents content.
- **Plan-driven**: All writing follows approved plan.md files with explicit authority hierarchy.
- **Zotero-first**: Every citation comes from your Zotero library. No external API searches.
- **IEEE style**: Concise technical prose, numeric citations, equations with defined variables.

## License

MIT
