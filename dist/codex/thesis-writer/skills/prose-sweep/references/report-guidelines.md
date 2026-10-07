# Report Guidelines

These rules restate M. P. Hayes, *A guide to writing technical reports* (version 4.4, Department of Electrical and Computer Engineering, University of Canterbury). The rule IDs follow the guide, so a finding can cite one, for example `W-8`. Where these rules and `prose-style.md` disagree, these rules win.

## Structure

- **S-1** Number every section from the introduction onward.
- **S-2** Refer to sections by number (`\cref`), never as "the section above" or "below".
- **S-3** Use at most three heading levels.
- **A-1, A-2** The abstract is unnumbered and states the key findings, not only the topics covered.
- **I-1, I-2** The introduction is the first numbered section.
- **I-3** The introduction describes the top-level concepts before the detail; a simplified system diagram helps.
- **I-4** The introduction ends with a roadmap of how the material is organised.
- **C-1** There is a conclusion.
- **R-1** There is a numbered references section with full details for every source.
- **R-2** A web reference carries the date the page was last updated. Prefer books, papers, and patents to URLs.
- **R-3** Every reference is cited in the text.
- **R-4** Use the specified reference style consistently.
- **X-1** Software listings go in an appendix; short code fragments may illustrate a point in the body.
- **X-2** Detailed tables of results go in an appendix; the body shows the general results.
- **X-3** Full schematics go in an appendix; the body uses block diagrams or simple circuits.

## Tense, person, and voice

- **W-1** Write in the present tense, except for the results of experiments, which take the past tense.
- **W-2** Avoid the future tense. Write "referencing is considered in Section 2", not "will be considered".
- **W-3** Prefer the third person. The first person is acceptable in places, especially the introduction.
- **W-4** Use "we" only when there are several authors. A thesis has one author.
- **W-5** Avoid the passive voice except when describing experimental procedure.

## Sentences

- **W-6** Keep sentences short; long sentences are hard to parse and invite ambiguity.
- **W-7** Put one idea in each sentence.
- **W-8** Do not join independent clauses with a comma. Start a new sentence.
- **W-9** Remove every word whose deletion leaves the meaning unchanged. See the gaucheries below.
- **W-10** Remove weasel words. See the list below.

## Paragraphs

- **W-11** Keep paragraphs short.
- **W-12** Avoid single-sentence paragraphs.
- **W-13** Do not open a paragraph with "However", "Furthermore", "Moreover", "Hence", or a similar connective.

## Punctuation and spelling

- **W-14** Use one comma style throughout. The serial comma is preferred.
- **W-15** Do not link sentences with a comma. A semicolon is acceptable where the two clauses are a genuine pair.
- **W-16** No contractions: "have not", not "haven't".
- **W-17** The apostrophe marks possession only: "two UAVs", "the UAV's propeller".
- **W-18** Define every initialism or acronym at first use.
- **W-19** Follow "i.e." and "e.g." with a comma.
- **W-20** Spell consistently, in New Zealand English.
- **W-21** Spelling errors are defects, not style choices.
- **§3.6** Use "however", "furthermore", "hence", "thus", and "nevertheless" only to join two sides of an argument. At the start of a sentence they take a comma.

## Presentation

- **P-3** Put text between a heading and its first subheading, explaining what the subsections contain.
- **P-4** Emphasise with italic or bold, never underline.
- **P-5** Set program identifiers in a fixed-width font.
- **P-7** Capitalise consistently.

## Figures, tables, and listings

- **F-2** Text in figures must not be too small. When a figure is scaled down, regenerate it with larger text.
- **F-3** Avoid bitmaps that contain text; if unavoidable, use at least 300 dpi.
- **F-4** Every figure and table has a caption that describes it.
- **F-5** Captions end with a full stop.
- **F-6** Every figure and table is referred to in the text.
- **F-7** Refer to a figure or table by its number, never as "the figure below".
- **F-8** Capitalise "Figure" and "Table" when referring to them.
- **F-9** Set listings in a fixed-width font.

## Mathematics

- **M-1** Display equations apart from the text.
- **M-2** Punctuate equations as part of the sentence that contains them.
- **M-3** Define every variable at first use, usually immediately after the equation.
- **M-4** Number equations that are referred to; numbering all of them is acceptable.
- **M-5** Refer to an equation by name as well as number: "Ohm's law (1)".
- **M-6** Refer to an equation by its number in parentheses.
- **M-7** Never use `*` for multiplication; use `\times` or juxtaposition.
- **M-8** Set operators and words upright: `\cos`, `\mathrm{d}x`.
- **M-9** Set words in subscripts and superscripts upright: `V_\mathrm{rms}`.

## Units

- **U-1** Use SI units. A unit named after a person is lower case when written out and capitalised when abbreviated: "5 joules", "5 J".
- **U-2** Never change the case of a prefix: m is milli and M is mega.
- **U-3** Separate a value from its unit with a non-breaking thin space, which `\SI{}{}` provides.
- **U-4** Set units upright.

## Weasel words

Weasel words sound informative and carry no information. Replace each with the quantity, the source, or nothing.

- **Vague expressions:** some people, experts, it is well known, many, somewhat, in most respects, various, fairly, several, extremely, exceedingly, quite, remarkably, few, mostly, largely, huge, tiny, a number of, excellent, significantly, substantially, incredibly, clearly, vast, relatively, completely, very.
- **Passive voice that hides an authority:** "it is said", "it is believed", "it has been shown". Name who, and cite them.
- **Weakening adverbs:** often, probably, possibly, truly, actually, basically, interestingly, surprisingly.

"Significantly" is acceptable only for a statistical result with its test named. "Often" and "probably" are acceptable where a cited source supports the frequency or likelihood, and then a number is better.

## Gaucheries

Redundant phrases and their replacements:

| Write | Not |
|---|---|
| a variety of | a variety of different |
| fact | actual fact |
| adept in | adept at |
| approximation to | approximation of |
| after | at the conclusion of |
| at present, today | at the present time |
| now | at this point in time |
| is found | can be found |
| compensate | compensate for |
| connect | connect up |
| correct | correct for |
| doubt | doubt but |
| because | due to the fact that |
| during | during the course of, in the course of |
| while | during the time that |
| often | frequently |
| help | help but |
| to | in order to |
| about | in the vicinity of |
| near | in the neighbourhood of |
| today | in this day and age |
| instant | instant of time, instant in time |
| if | in the event that |
| regardless | irregardless |
| join | join together |
| called | known as |
| unique | most unique, very unique |
| innovative | new and innovative |
| no | not got any |
| before | prior to |
| because | the reason why |
| to begin | to begin with |
| whether | whether or not |
| (delete) | quite, very |
