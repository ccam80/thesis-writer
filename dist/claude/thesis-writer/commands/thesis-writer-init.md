---
description: Initialize the current project with Thesis Writer and its Zotero-integrated workflow.
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Thesis Writer Project Setup

When the user runs `/thesis-writer:init`, initialize the current project from the generated `templates/CLAUDE.thesis-writer.md` file in this plugin.

1. Check whether `CLAUDE.md` exists in the current working directory.
2. If it exists, ask the user whether to back it up and replace it, merge the Thesis Writer instructions at the end, or cancel. Wait for the response before writing.
3. Locate `templates/CLAUDE.thesis-writer.md` within this installed plugin. Do not recreate or paraphrase it.
4. For replacement, preserve the existing file as `CLAUDE.md.bak`, then copy the template to `CLAUDE.md`. Do not overwrite an existing backup without explicit approval.
5. For merge, append a horizontal rule, a `# Thesis Writer Configuration (Added by Plugin)` heading, and the complete template. Do not append a duplicate configuration.
6. For a new project, copy the complete template to `CLAUDE.md`.
7. Report the action taken and remind the user that the `deep-zotero` MCP server must be available for research features.

Use the host's native file tools so the workflow is portable across Windows, macOS, and Linux. If the template cannot be found, report the missing installed artifact and stop; do not create a reduced substitute.

After initialization, recommend starting with the `document-planner` skill and an explicit scope such as a chapter or section.
