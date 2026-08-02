---
name: thesis-writer-init
description: "Initialize a project with the Thesis Writer contract block in AGENTS.md, appending beside existing instructions and updating the block in place when the plugin version changes."
---

<!-- GENERATED FILE — edit src/ or vendors/, then run scripts/build_plugin.py -->

# Thesis Writer Project Setup

Initialize the current project from the generated `templates/AGENTS.thesis-writer.md` file in this installed plugin.

1. Locate `templates/AGENTS.thesis-writer.md` within this installed plugin. Do not recreate or paraphrase it.
2. Copy the contract block: `<!-- thesis-writer:contract v... -->` through `<!-- /thesis-writer:contract -->`, inclusive. Do not copy the generated-file notice above it.
3. If `AGENTS.md` has no contract markers, append a horizontal rule and the block, creating the file if it does not exist.
4. If `AGENTS.md` has a contract block at the template's version, change nothing and say so.
5. If `AGENTS.md` has a contract block at any other version, replace that marked block with the template's block. Never replace, reorder, or rewrite content outside the markers.
6. Report the action taken and remind the user that the plugin-local `deep-zotero` MCP server must be available for research features.

Use Codex filesystem tools and preserve unrelated working-tree changes. If the template cannot be found, report the missing installed artifact and stop; do not create a reduced substitute.

After initialization, recommend starting with the `document-planner` skill and an explicit scope such as a chapter or section.
