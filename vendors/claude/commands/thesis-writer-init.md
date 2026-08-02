---
description: Initialize the current project with Thesis Writer and its Zotero-integrated workflow.
---

# Thesis Writer Project Setup

When the user runs `/thesis-writer:init`, initialize the current project from the generated `templates/CLAUDE.thesis-writer.md` file in this plugin.

1. Locate `templates/CLAUDE.thesis-writer.md` within this installed plugin. Do not recreate or paraphrase it.
2. Copy the contract block: `<!-- thesis-writer:contract v... -->` through `<!-- /thesis-writer:contract -->`, inclusive. Do not copy the generated-file notice above it.
3. If `CLAUDE.md` has no contract markers, append a horizontal rule and the block, creating the file if it does not exist.
4. If `CLAUDE.md` has a contract block at the template's version, change nothing and say so.
5. If `CLAUDE.md` has a contract block at any other version, replace that marked block with the template's block. Never replace, reorder, or rewrite content outside the markers.
6. Report the action taken and remind the user that the `deep-zotero` MCP server must be available for research features.

Use the host's native file tools so the workflow is portable across Windows, macOS, and Linux. If the template cannot be found, report the missing installed artifact and stop; do not create a reduced substitute.

After initialization, recommend starting with the `document-planner` skill and an explicit scope such as a chapter or section.
