# Thesis Prose Style — Binding

This file is the prose voice authority for all generated thesis text. The
`writer` skill reads it before drafting and runs an explicit pass against it
before presenting any prose. The `reviewer` skill audits against it. Plan
files are exempt (plan statements are terse notes, not prose), but plan stub
*labels* follow the vocabulary rules.

The author's own writing is the ultimate voice reference: existing chapter
`.tex` files and papers in `author_reference/`. Where this file and the
author's demonstrated style differ, the author's style wins — flag the
difference rather than silently choosing.

Rules cannot fully specify voice. An agent can obey every rule below and
still produce prose that reads as machine-generated. The failure is always
the same: writing *about* the content (framing, emphasising, dramatising)
instead of *stating* the content. When in doubt, state the fact and stop.

Groundedness precedes style. Every technical sentence maps to stable point
IDs in the approved `plan.md`. No improvement in rhythm, flow, or elegance
permits a new premise, stronger causal relation, broader population, removed
qualification, or unapproved citation.

---

## 1. Density and concision

First drafts run about twice as long as needed. Cut before presenting, not
after feedback.

- **One fact per sentence. One claim per sentence.** Fewest words that carry
  the claim.
- **Cut framing clauses; state the claim directly.** Bad: "When considering
  the effect of noise on the measurement, it becomes apparent that..." Good:
  "Noise limits the measurement to..."
- **Stop at the number.** When a number carries the claim, end the sentence
  on it: "The filter settles within \SI{40}{\milli\second}." No trailing
  "which means..." gloss re-explaining a fact already complete.
- **No verb-jargon.** "responds to", "exhibits", "is characterised by", "is
  concerned with", "serves as", "acts as", "plays a role in" — use a plain
  verb. A sensor does not "exhibit drift"; it drifts.
- **Never walk the reader through an observation.** State the property; the
  figure or table shows it. Bad: "Examining the plot, one can observe that
  the amplitude decreases..." Good: "Amplitude decreases with distance
  (\cref{fig:x})."
- **Axe a whole paragraph that does not land.** A formal definition or
  notation aside included only to look complete gets trimmed out, not down.
- **Motivate a method with the problem it solves**, stated immediately
  before it — not with a survey of everything it could do.

Deletion test: reread the sentence with a word or clause deleted. If the
claim is unchanged, the words were decorative — leave them out.

## 2. Banned modifiers — cut on sight

Delete the modifier unless it changes the claim:

- **Empty intensifiers:** very, quite, rather, fairly, really, particularly,
  highly, extremely, remarkably, notably, significantly (unless statistical,
  with the test named).
- **Importance-claiming adjectives:** key, important, crucial, essential,
  critical, significant, fundamental, vital, pivotal. If it matters, the
  sentence must show why; the adjective is an unsupported claim.
- **Filler qualifiers:** "a certain amount", "a given value", "the
  appropriate X", "a particular case", "in general", "overall", "in terms
  of", "with respect to" (where a plain preposition works).
- **Vague plurals:** various, several, numerous, myriad, "a number of",
  "a range of", "multiple" — give the count, or nothing.
- **Stative padding:** actual, specific, respective, associated, underlying,
  corresponding, overall — bolted onto a noun that is already definite.
- **Hedging stacks:** "may potentially", "could possibly suggest", "it is
  perhaps likely that". Where uncertainty is real, one hedge, chosen
  precisely ("suggests", "is consistent with", "cannot be excluded"). Where
  it is not, none.

## 3. Banned AI sentence patterns

These are the tics that mark generated prose. They are banned as *patterns*,
not word lists — rephrasing the same move is the same violation.

- **Contrast scaffolds:** "It's not X, it's Y", "not just X but Y", "X isn't
  merely Y — it's Z", "rather than X, this represents Y". State Y directly;
  X was never on the table.
- **Dramatic staccato.** No breaking content into short decisive fragments
  for weight ("One sensor. One signal. No calibration."). Punctuation
  reflects sentence structure, not emphasis.
- **Over-compression into punchiness.** "so this solves nothing" reads as
  pretentious, not plain. Say the claim in full: "so this does not solve the
  problem."
- **Rhetorical questions.** Never. State the question's answer.
- **Tricolon flourishes:** "faster, simpler, and more robust" — three
  parallel adjectives ending a sentence for rhythm. Keep the one that is
  measured; cut the rest.
- **Sentence-adverb openers:** Crucially, Importantly, Interestingly,
  Notably, Essentially, Fundamentally, Ultimately, Arguably, "Of course,".
  Delete the adverb; if the sentence loses force, the sentence was weak.
- **Filler moves:** "it is important to note that", "it is worth
  mentioning", "the reality is", "at its core", "in essence", "when it
  comes to", "a testament to", "underscores the importance of".
- **Vocabulary kill list:** delve, leverage (verb), harness, unlock,
  showcase, seamless, holistic, comprehensive (as praise), robust (as
  praise without a metric), landscape, realm, paradigm, journey, tapestry,
  "state-of-the-art" (unless citing a benchmark), "cutting-edge".
- **Anthropomorphic or dramatic colour.** Methods do not "struggle",
  results do not "tell a story", data does not "reveal a surprising truth".
- **Meta-narration.** Prose does not narrate the document: no "this section
  discusses", "having established X, we now turn to", "as will become
  clear". A section opens on its first claim. Structural cross-references
  use \cref and state the fact: "The calibration procedure is described in
  \cref{sec:cal}." No "recall that" — if the reader needs the fact, state
  it as a fact.

## 4. Em-dashes

The paired em-dash interpolation (`X --- Y --- Z` in LaTeX) is the strongest
single marker of generated prose. Scan every draft for `---` before
presenting; fix per instance, not by bulk-replace. Replacements by intent:

- Interpolated definition or example → separate sentence, or an italic noun
  phrase in place.
- Appositive ("X, the Y that does Z") → commas.
- Strong break between independent clauses → period or semicolon.
- "Namely / that is" → colon.

A single em-dash is occasionally correct; a pair almost never is.

## 5. Register

- **Active voice preferred.** "We filtered the signal at \SI{50}{\hertz}"
  over "the signal was filtered". Passive is acceptable in methods where the
  actor is obvious and the object is the topic.
- **"We" for the author's actions and decisions**; no conversational "let's",
  no imperative addressed to the reader.
- **Declarative, not narrating.** State the current claim; do not retrace
  how the chapter reached it.
- **Established results are stated as facts**, once, without re-derivation:
  "The electrode impedance dominates below \SI{1}{\kilo\hertz}."
- **Don't elevate simple claims with formal phrasing.** "constitutes",
  "represents", "reduces to", "necessitates" where a plain verb works.
  Bad: "this configuration necessitates the use of shielding." Good: "this
  configuration needs shielding."
- **Flowing sentences over chopped ones.** When clauses form one chain of
  reasoning, join with comma + "and"/"so". Reserve sentence breaks for
  independent statements. Reserve semicolons for genuinely paired claims.
- **Tense:** past for methods and results ("the signal was sampled"),
  present for established facts and interpretations ("these results
  suggest"), past for literature ("Smith et al. demonstrated").

## 6. Paragraph flow

- **Problem before anatomy.** Open a paragraph on the requirement or
  problem, not on what connects to what. Anatomy is the answer; reach the
  problem first.
- **Build from the previous paragraph's endpoint.** Reach the current claim
  by reasoning from where the reader was left, without a transition sentence
  that merely announces the topic change.
- **Mechanism before label.** State what physically happens, then attach the
  field's name for it, then use the name freely.
- **Define before use.** No technical shorthand the chapter has not built.
  Abbreviations expanded at first use, then used consistently.

## 7. Figures and captions

- **Captions identify; prose teaches.** A caption names what the figure
  shows: "Torque against rotor speed; the operating region is shaded." The
  explanation lives in the body text that references the figure. Captions
  are a recurring place verbosity creeps back in — cut them on every pass.
- Prose extends what a figure shows; it does not duplicate it in words.

## 8. Sentence-level information test

The final revision pass, run per sentence over the whole chunk before
presenting:

For each sentence ask: **what new information does this give the reader?**
New claim, new quantity, new connection → KEEP. Restates a prior sentence,
frames without adding, narrates the document, or exists for rhythm → CUT.
Apply the cuts, then present.

This pass cannot be skipped on the grounds that the rules above were
followed during drafting — density failures survive rule-following.

## 9. Claim fidelity and source voice

- Preserve negation, modality, quantities, conditions, comparison classes,
  populations, and causal status from the mapped plan point.
- Do not turn correlation into causation, a study result into field-wide
  consensus, a bounded observation into a general law, or an inference into
  an established fact.
- Citation placement defines scope. Put a citation beside the clause it
  supports; an end-of-paragraph citation does not retroactively support the
  paragraph.
- Do not imitate wording or cadence from quoted source passages. Use sources
  for evidence and field terminology; use the author's `.tex` for voice.
- A smooth transition cannot hide an ungrounded proposition. If the prose
  needs a new relationship, return it to planning.

---

## Pre-presentation checklist

Run this scan before presenting any prose chunk. The sections above are the
explanation; this is the fast pass.

- [ ] Draft is not ~2x too long; one fact / one claim per sentence.
- [ ] No banned modifiers (§2): intensifiers, importance-claimers, vague
      plurals, stative padding, hedging stacks.
- [ ] No banned patterns (§3): contrast scaffolds, staccato drama,
      rhetorical questions, tricolons, sentence-adverb openers, filler
      moves, kill-list vocabulary, anthropomorphism, meta-narration.
- [ ] No `---` em-dash pairs; each single `---` justified per §4.
- [ ] Register: active where possible, "we" not "let's", plain verbs, no
      elevated phrasing, tenses per §5.
- [ ] Paragraphs open on problem/requirement, not anatomy or announcement.
- [ ] Captions identify, they do not teach.
- [ ] Sentence-level information test run; cuts applied.
- [ ] Every sentence maps to plan point IDs; every technical clause is covered.
- [ ] Negation, modality, conditions, quantities, comparison, population,
      and causal status match the mapped points and evidence cards.
- [ ] Citations are adjacent to supported clauses and use only approved keys.
- [ ] Voice matches the author's existing .tex prose, not this file's.
