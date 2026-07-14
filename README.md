# Thesis Writer

Thesis Writer is a dual-vendor plugin for plan-driven doctoral thesis authoring with Zotero-grounded citations and IEEE-style LaTeX output. One shared source produces complete Claude Code and Codex plugins; vendor mechanics are kept in small, explicit overlays.

## What it provides

```text
document-planner ⇄ zotero-research → writer → figure-generator → formatter → reviewer
       │                                                              ⇄ zotero-research
       └─ corpus gap → zotero-source-acquisition → user-approved import ┘
```

The plugin also includes authorship-session logging and a vendor-specific project initializer. Claude Code initializes `CLAUDE.md`; Codex initializes `AGENTS.md`. Both use the same canonical thesis-instruction template.

## Prerequisites

- Zotero with a populated research library
- The [Deep Zotero MCP server](https://github.com/ccam80/zotero-citation-mcp) in a Python virtual environment
- Claude Code and/or Codex
- A LaTeX distribution for compilation
- Python 3.10 or newer; matplotlib for figure generation
- For corpus-gap acquisition: installed Google Chrome, a dedicated persistent SSO profile, and a Zotero API key with library write and file access

The local scripts default to `C:\local_working_projects\zotero_citation_mcp`. Pass `--mcp-root` on another machine. The generated MCP configuration contains only the resolved virtual-environment interpreter and `-m deep_zotero.server`; it never copies or prints API keys.

## Install or update locally

Build and validate both plugins first:

```powershell
python scripts\build_plugin.py --vendor all
python scripts\validate_all.py --mcp-root C:\path\to\zotero_citation_mcp
```

Install or update Codex:

```powershell
python scripts\install_plugin.py --vendor codex --mcp-root C:\path\to\zotero_citation_mcp --execute
```

This copies the disposable generated plugin to `~/plugins/thesis-writer`, creates the standard personal marketplace entry only when needed, applies Codex's required local cachebuster, and runs `codex plugin add thesis-writer@personal`. Start a new Codex task after installation so skills and MCP tools are reloaded.

The installer stages and fully configures the replacement before swapping it into place, so a missing MCP interpreter, failed server import, or missing cachebuster cannot destroy a working installation. A custom `--marketplace` is supported when it follows `<root>/.agents/plugins/marketplace.json` and `--plugin-home` is `<root>/plugins`; the installer reads and uses that marketplace's actual top-level name in the Codex command.

Install or update Claude Code:

```powershell
python scripts\install_plugin.py --vendor claude --mcp-root C:\path\to\zotero_citation_mcp --execute
```

The script builds the Claude distribution, updates or registers this repository as the `thesis-writer-marketplace`, and updates or installs `thesis-writer@thesis-writer-marketplace`. Restart Claude Code after installation. From the Claude Code interface, published updates can also be applied with `/plugin marketplace update thesis-writer-marketplace` followed by `/plugin update thesis-writer@thesis-writer-marketplace`.

Omit `--execute` to build and show the vendor commands without running them. Codex's plugin files and marketplace entry are still prepared locally so their paths and MCP import can be verified.

## Initialize a thesis project

- Claude Code: run `/thesis-writer:init`.
- Codex: ask to use the `thesis-writer-init` skill.

If project instructions already exist, the initializer asks before backing up/replacing or merging them. It never silently overwrites an existing backup or produces a reduced fallback template.

## Source and build architecture

Repository-root `AGENTS.md` contains plugin-maintainer instructions, and root `CLAUDE.md` is a relative symlink to it. These files govern work on this repository; they are not thesis-project templates and are not consumed by the builder. End-user instructions come only from `src/templates/thesis-instructions.md`.

```text
metadata.json                         shared plugin identity and release version
src/
  skills/<name>/skill.yaml           shared name and description
  skills/<name>/body.md               shared workflow with explicit vendor markers
  skills/<name>/references|scripts/  shared companion files
  templates/thesis-instructions.md   shared project instructions
vendors/
  claude/skills.json                 Claude allowed-tools frontmatter overlay
  claude/fragments/                  Claude tool/delegation wording
  claude/commands/                   Claude initializer command
  codex/skills.json                  intentionally empty frontmatter overlay
  codex/fragments/                   Codex tool/delegation wording
  codex/init-skill/                  Codex initializer skill
scripts/                              build, install, validate, and release tooling
dist/claude/thesis-writer/           generated Claude plugin
dist/codex/thesis-writer/            generated Codex plugin
```

The committed Codex distribution contains `.mcp.json.example`, not a machine-specific path. During installation, the installer verifies `deep_zotero.server`, writes the installed plugin's `.mcp.json` with the selected virtual-environment interpreter, and adds `mcpServers` to that installed manifest. The committed source and distribution therefore remain portable.

Each generated `SKILL.md` is compiled as:

```text
shared skill.yaml
  + vendor frontmatter overlay
  + shared body.md with vendor fragments inserted
  = dist/<vendor>/thesis-writer/skills/<name>/SKILL.md
```

Claude output contains shared `name` and `description` plus its skill-specific `allowed-tools`. Codex output contains exactly `name` and `description`. Fragment markers use `<!-- vendor:fragment-name -->`. The build fails when a referenced fragment is missing, a supplied fragment is unused, or any marker remains unresolved.

Do not edit `dist/`, installed plugin caches, root marketplace JSON, or generated `SKILL.md` files. Edit `metadata.json`, `src/`, or `vendors/`, then rebuild. Generated Markdown files carry a notice pointing back to these authoritative sources. JSON cannot carry comments, so its generated status is documented here and enforced by rebuild validation.

## Contributor workflow

1. Edit shared behavior under `src/`. Put host tool names, delegation syntax, initialization semantics, and attribution under the appropriate `vendors/` tree.
2. Run `python scripts\build_plugin.py --vendor all`.
3. Run `python -m pytest tests`.
4. Run `python scripts\validate_all.py` for deterministic-build checks, vendor-leakage checks, every Codex skill's `quick_validate.py`, Codex `validate_plugin.py`, Claude plugin validation, and a Deep Zotero import check.
5. Inspect `git diff -- dist` and commit shared source and both generated distributions together.

The vendor-leakage validator rejects Claude-only concepts in Codex output and Codex-only concepts in Claude output. The builder also adapts the legacy paper-cache default to the correct vendor directory while preserving the `THESIS_PAPER_CACHE` override.

## Release workflow

```powershell
python scripts\release.py --version 0.3.0 --mcp-root C:\path\to\zotero_citation_mcp
git add metadata.json src vendors scripts dist .claude-plugin\marketplace.json README.md
git commit -m "Release thesis-writer 0.3.0"
git tag thesis-writer-v0.3.0
git push --follow-tags
```

`release.py` updates the canonical version, regenerates both distributions, and validates them. Codex cachebusters are applied only to the disposable installed copy; they never modify the shared release version or committed distribution.

## Key policies

- All substantive writing is collaborative and follows an approved plan.
- All citations come from the user's Zotero library through the isolated `zotero-research` worker.
- External discovery is isolated in `zotero-source-acquisition`; candidate tabs remain open for review and exact candidate IDs require approval before Zotero metadata/PDF import.
- Every literature claim card carries the supporting, qualifying, and contradicting passages found within its declared search boundary.
- Technical prose maps every sentence to stable grounded point IDs; narrative `LINK` and `PURPOSE` points cannot hide factual premises.
- No placeholder or invented citations are permitted.
- The generated distributions retain the complete planning, writing, figure, formatting, review, and logging behavior from the original Claude plugin.

## License

MIT
