# Document Planner

<!-- style:writing-planner -->

## Contract and inputs

The files, plan grammar, approval rules, placeholders, and citation rules are the shared contract's. <!-- vendor:contract-location -->

<!-- vendor:zotero-delegation -->

When you enter a chapter or section, read:

1. the target `.tex` file, which is the authority for everything already written;
2. the chapter `plan.md`;
3. the thesis `plan.md`;
4. any project evidence the author names: data, code, notes, figures, or calculations.

Say in a few lines what already exists and where the plan and the `.tex` disagree. Where the `.tex` has moved on from the plan, bring the plan into line with the prose as a mechanical fix and report it. Where the plan holds material the `.tex` lacks, that material is simply not written yet.

## Levels

The thesis plan lists the chapters, what each is for, and each chapter's sections. A chapter plan lists its sections and subsections, each section's paragraph labels, and each paragraph's points. Nest below subsection level only when the author asks.

Each level refines the one above: a section's paragraph labels stay as they are while points collect beneath them, and a coarse point splits into finer ones until the paragraph reads one point per sentence. The author moves between levels whenever the work calls for it; follow them there and keep every level consistent with the prose.

## Ordering

Apply these rules at the thesis level and again inside every chapter and section, and check each new ordering against them:

- Go top-down and outside-in: the system before its components, the interface before its internals, the top-level concepts before the detail.
- Where a topic has an abstract model and a physical realisation, such as a programming model and the hardware that runs it, give each its own subsection and put the model first.
- Background chapters explain mechanisms. The choice between mechanisms, and its trade-offs, belongs in the method chapter. Material about the author's own design moves out of the background and into the chapter that presents the design.
- Present each fact where the reader first needs it. Define scope terms when they first appear; for example, state what "modern" covers before using it.
- Reference detail goes at the end of the chapter or in an appendix: tables of generations or parameters, detailed results, software listings, and full schematics.
- A worked example is minimal and figure-led, and sits where its concept is introduced rather than at the end of the chapter.
- The introduction ends with a roadmap of the chapters. Use no more than three heading levels, and put text between every heading and its first subheading.

## Moves and reorders

When a point belongs elsewhere, propose the move as one batch item that names the source and the destination. On approval:

1. Move the bullet to the destination plan, and move the written sentence with it if one exists.
2. If the destination paragraph is already written and the moved sentence does not fit it as it stands, place the sentence where it belongs and tell the author it needs joining in.
3. Repair the `\cref` targets, labels, and roadmap sentences that the move breaks, and update the thesis plan when a chapter's content or order changes.

Swapping chapters or sections follows the same steps: reorder the `\include` or `\subfile` lines, the thesis plan, and the roadmap, then check that every term each moved unit uses is still defined before it.

## Checking facts

Check a fact whenever it is uncertain, as the work reaches it. Do not wait for a section to settle. Send `zotero-research` a quick-check batch: each item is one fact as the plan or prose states it. Each answer returns a verdict, the value at the source's precision, the citation key, the locator, and the passage.

Report the answers as a batch of corrections. Where a fact is confirmed, propose replacing its citation placeholder with `\cite{key}`. Where the source says something different, propose the corrected wording. Where research finds nothing, say what was searched and leave the placeholder.

## Resolving citations

When the author asks, resolve the citation placeholders in a scope. Collect every `[[cite: ...]]` and informal citation marker, send them to `zotero-research` as one quick-check batch, and present one proposed key per placeholder. On approval, replace each placeholder with `\cite{key}`. Report any placeholder with no supporting source, any item that came back without a Better BibTeX key, and any key absent from `references.bib`.

## Missing sources

When research reports that the library has no source for a fact, offer the author three options: hand it to `zotero-source-acquisition`, supply the value from the author's own work, or rephrase the sentence so it needs no source. For acquisition, pass a short description of what the source must show, along with every item research has already found, so acquisition does not propose items the library already holds.

A candidate the acquisition agent finds is not evidence. Use it only after it is imported, indexed, and confirmed by a new quick check.

## Integration

- Uses `zotero-research` for every library search, at any stage.
- Hands sources the library lacks to `zotero-source-acquisition`.
- The author runs `prose-sweep` when a section is ready for a style pass, and `reviewer` before submission.
- Records no authorship; `log-session` does that at session end.
