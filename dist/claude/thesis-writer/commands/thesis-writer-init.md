---
description: Initialize the current project with Thesis Writer and its Zotero-integrated workflow.
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Thesis Writer Project Setup

When the user runs `/thesis-writer:init`, initialize the current project from the generated `templates/CLAUDE.thesis-writer.md` file in this plugin.

1. Locate `templates/CLAUDE.thesis-writer.md` within this installed plugin. Do not recreate or paraphrase it.
2. Append a horizontal rule and the complete template to `CLAUDE.md`, creating the file if it does not exist. Never replace, reorder, or rewrite existing content.
3. If the contract is already present, change nothing and say so.
4. Report the action taken and remind the user that the `deep-zotero` MCP server must be available for research features.

Use the host's native file tools so the workflow is portable across Windows, macOS, and Linux. If the template cannot be found, report the missing installed artifact and stop; do not create a reduced substitute.

After initialization, recommend starting with the `document-planner` skill and an explicit scope such as a chapter or section.
