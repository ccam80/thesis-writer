# Thesis Writer Plugin Repository Instructions

## Repository role

This repository develops and publishes the dual-vendor `thesis-writer` plugin for Claude Code and Codex. Work here changes plugin source, generated distributions, installers, validators, or maintainer documentation.

This repository is not a thesis project. Do not follow the end-user thesis-authoring workflow against this checkout, create thesis plans here, or replace these maintainer instructions with the generated thesis-project template.

`AGENTS.md` is the canonical repository-maintainer instruction file. Root `CLAUDE.md` must remain a relative symbolic link to `AGENTS.md` so both hosts receive the same maintainer contract.

## Sources of truth

Edit authoritative inputs, then regenerate outputs:

| Path | Authority |
|---|---|
| `metadata.json` | Shared plugin identity, version, description, and release metadata |
| `src/skills/<name>/skill.yaml` | Shared skill name and description |
| `src/skills/<name>/body.md` | Shared skill behavior |
| `src/skills/<name>/references/` and `scripts/` | Shared skill companions |
| `src/templates/thesis-instructions.md` | End-user thesis-project instructions generated into installed plugins |
| `vendors/claude/` | Claude-only tools, commands, fragments, and frontmatter |
| `vendors/codex/` | Codex-only fragments and initializer skill |
| `scripts/` | Build, installation, validation, and release tooling |
| `dist/claude/thesis-writer/` | Generated and committed Claude distribution |
| `dist/codex/thesis-writer/` | Generated and committed Codex distribution |

Never edit `dist/`, installed plugin directories, plugin caches, or generated `SKILL.md` files directly. A generated-output defect must be fixed in `src/`, `vendors/`, `metadata.json`, or the builder, then rebuilt.

Root `AGENTS.md` is not an input to the plugin builder. The end-user templates are generated only from `src/templates/thesis-instructions.md` plus vendor fragments. Keep maintainer instructions and thesis-project instructions separate.

## Build architecture

Each vendor skill is compiled from:

```text
src/skills/<name>/skill.yaml
  + vendor frontmatter from vendors/<vendor>/skills.json
  + src/skills/<name>/body.md
  + referenced vendors/<vendor>/fragments/*.md
  + shared references and scripts
  = dist/<vendor>/thesis-writer/skills/<name>/SKILL.md
```

Claude skills require an `allowed-tools` entry in `vendors/claude/skills.json`. Codex skills contain only `name` and `description` frontmatter. Vendor markers use `<!-- vendor:fragment-name -->`; the build must fail on missing, unused, or unresolved fragments.

Claude's initializer is maintained under `vendors/claude/commands/`. Codex's initializer is maintained under `vendors/codex/init-skill/`. These initialize thesis projects from generated templates inside the installed plugin; they do not use the repository-root instruction files.

Generated distributions are committed because remote marketplaces install them directly. Commit authoritative source and both regenerated vendor distributions together.

## Maintainer workflow

1. Inspect the working tree and preserve unrelated changes.
2. Change shared behavior in `src/`; isolate host-specific syntax and capabilities in `vendors/`.
3. Build both distributions:

   ```powershell
   python scripts\build_plugin.py --vendor all
   ```

4. Run the test suite:

   ```powershell
   python -m pytest tests
   ```

   If the active interpreter does not provide pytest, use the repository's established ephemeral runner:

   ```powershell
   uv run --with pytest pytest -q
   ```

5. Run complete validation:

   ```powershell
   python scripts\validate_all.py --mcp-root C:\path\to\zotero_citation_mcp
   ```

6. Inspect source and generated diffs together. Confirm no vendor leakage, unresolved markers, machine-specific MCP paths, secrets, `__pycache__`, or `.pyc` files entered the distributions.

Do not report success from tests alone. `validate_all.py` also checks deterministic regeneration, stale distribution files, skill frontmatter, vendor leakage, Codex skill/plugin validity, Claude plugin/marketplace validity, configured Codex MCP output, and the Deep Zotero server import.

## Skill changes

When adding or changing a skill:

- Use the `skill-creator` guidance and retain the shared-source layout.
- Put reusable behavior in `src/skills/<name>/body.md`.
- Put executable helpers and references beside that skill under `scripts/` and `references/`.
- Add every Claude skill to `vendors/claude/skills.json` with the minimum required tools.
- Keep host tool names, delegation language, and user-interaction mechanisms in vendor fragments when they differ.
- Add contract tests for fail-closed behavior, not only successful examples.
- Rebuild and validate both vendors even when a change appears host-specific.

Use `plugin-creator` guidance for manifest, marketplace, cachebuster, or local-installation changes. Do not hand-edit an installed Codex marketplace or plugin cache.

## Grounding contracts that must be preserved

The plugin organizes the author's knowledge; it does not invent research. Changes must preserve these boundaries:

- Top-down narrowing from thesis to chapter, section, paragraph, and sentence remains author-controlled.
- Technical plan points use stable typed provenance. Narrative `LINK` and `PURPOSE` points cannot conceal factual premises.
- Unsupported propositions remain inline `OPEN` points and never become writer input. Do not create a separate reference-debt authority.
- `zotero-research` is read-only and isolated. It reports claim-centred evidence cards with immediate passages and all material supporting, qualifying, and contradicting sources found within the declared boundary.
- External discovery and Zotero mutation belong only to `zotero-source-acquisition`.
- Source acquisition requires visible user review, exact candidate-ID approval, matching metadata and PDF identity, access preflight, atomic journalling, verified Zotero fetchback, and attachment-first rollback.
- Imported items are not evidence until indexing completes and a new Zotero research pass verifies them.
- Writer output maps technical sentences to grounded point IDs, preserves epistemic scope, calibrates to author prose, and passes deterministic prose linting.
- Reviewer coverage is exhaustive rather than sampled.

Any relaxation of these contracts is an architectural change and requires explicit author approval plus adversarial tests.

## Installation and release

Building and validating do not authorize modifying installed plugins. Install only when the user explicitly requests it.

Codex installation or update:

```powershell
python scripts\install_plugin.py --vendor codex --mcp-root C:\path\to\zotero_citation_mcp --execute
```

Claude installation or update:

```powershell
python scripts\install_plugin.py --vendor claude --mcp-root C:\path\to\zotero_citation_mcp --execute
```

Omit `--execute` only when a dry run is intended. After Codex installation, start a new Codex task. After Claude installation, restart Claude Code.

For a release, use `scripts/release.py`; do not update generated versions independently. Verify the release diff, commit source and distributions, create the requested tag, and push tags only when explicitly authorized.

## Security and portability

- Never commit Zotero API keys, browser cookies, SSO state, `.env` files, machine-specific `.mcp.json`, or local interpreter paths.
- The committed Codex distribution contains `.mcp.json.example`; installation writes the real `.mcp.json` only into the installed copy.
- Keep Zotero imports fail-closed. HTTP success without the exact expected payload is failure.
- Keep source-acquisition review tabs under user control; authentication, 2FA, and CAPTCHA remain user actions.
- Preserve portable relative paths and LF-generated output. A committed symlink must use a relative target.

## Completion evidence

Before considering repository work complete, report:

- the authoritative files changed;
- the generated distributions rebuilt;
- test totals and failures;
- complete validator outcome;
- any installation or release action actually performed;
- a point-by-point check against the requested behavior for workflow-contract changes.

Do not claim that a plugin was installed, a distribution is current, or a citation path works without the corresponding command receipt from the current session.
