# Prose Sweep

<!-- style:writing-planner -->

## Purpose

Tighten the author's prose without changing what it says. The sweep removes weasel words, vague quantities, and redundancy, and brings the text into line with the report guidelines. It does not review technical content; that happens during drafting rounds and in `reviewer`.

<!-- vendor:contract-location -->

## Scope and authorities

Sweep the scope the author names: a file, a section, or the paragraphs written this round. With no scope named, sweep the paragraphs changed since the last sweep.

Read before sweeping:

1. `references/report-guidelines.md`, which takes precedence;
2. `references/prose-style.md`;
3. nearby paragraphs the author wrote, for voice.

## Passes

Run `scripts/lint_prose.py` on each file in scope. Its findings point at candidates; judge each one in context, because a flagged word is sometimes the right word.

Then read every sentence in scope and check it for:

1. **Weasel words and vagueness.** Replace each vague quantity, unnamed authority, intensifier, and weakening adverb with the number, the source, or nothing. Where the replacement needs a value or a source you do not have, propose a placeholder: `[[the value needed]]` or `[[cite: what the source must show]]`.
2. **Redundancy.** Delete each word whose removal leaves the meaning unchanged, and replace each gaucherie.
3. **Sentence rules.** One idea per sentence, no comma splices, no contractions, acronyms defined at first use, apostrophes for possession only, a consistent comma style.
4. **Person, voice, and tense,** as the report guidelines set them.
5. **Paragraph rules.** No paragraph opens on a connective such as "However"; no single-sentence paragraph; no "above", "below", or "the figure below" in place of a numbered reference.
6. **Floats and mathematics.** Captions end with a full stop and describe their figure; every figure and table is referenced by number; equations are punctuated as part of the sentence; every variable is defined at first use; units use `\SI{}{}`.
7. **Generated-prose patterns** from `prose-style.md`: contrast scaffolds, em-dash pairs, meta-narration, sentence-adverb openers, and framing that says nothing.

## Applying fixes

Apply a fix directly when it leaves the claim exactly as it was: deleting an intensifier or a redundant phrase, replacing a gaucherie, expanding a contraction, splitting a comma splice, defining an acronym, correcting a caption's punctuation, or formatting a unit. Re-read each file immediately before editing it. Afterwards, list the applied fixes compactly, one line each, as location, old text, new text, and rule ID.

Propose any fix that needs knowledge the author holds or that shifts emphasis, such as replacing "often" with a frequency, naming the authority behind "it is well known", or rewording a long sentence. Put every such fix in one batch, each with its location, current text, proposed text, and rule ID. One approval applies the batch.

No fix may change negation, modality, a condition, a quantity, the comparison class, the population, or a causal claim. If tightening a sentence would do any of those, propose it instead of applying it, and say what would change.

## Output

Report the applied fixes, then the proposed batch, then any rule the author's prose breaks deliberately and consistently, so the author can confirm it as house style. Record no authorship.
