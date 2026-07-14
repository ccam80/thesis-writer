# Thesis Writer Project Setup

Initialize the current project from the generated `templates/AGENTS.thesis-writer.md` file in this installed plugin.

1. Check whether `AGENTS.md` exists in the current working directory.
2. If it exists, present the existing-file situation and ask the user in free text whether to back it up and replace it, merge the Thesis Writer instructions at the end, or cancel. Wait for approval before writing.
3. Locate `templates/AGENTS.thesis-writer.md` within this installed plugin. Do not recreate or paraphrase it.
4. For replacement, preserve the existing file as `AGENTS.md.bak`, then copy the template to `AGENTS.md`. Do not overwrite an existing backup without explicit approval.
5. For merge, append a horizontal rule, a `# Thesis Writer Configuration (Added by Plugin)` heading, and the complete template. Do not append a duplicate configuration.
6. For a new project, copy the complete template to `AGENTS.md`.
7. Report the action taken and remind the user that the plugin-local `deep-zotero` MCP server must be available for research features.

Use Codex filesystem tools and preserve unrelated working-tree changes. If the template cannot be found, report the missing installed artifact and stop; do not create a reduced substitute.

After initialization, recommend starting with the `document-planner` skill and an explicit scope such as a chapter or section.
