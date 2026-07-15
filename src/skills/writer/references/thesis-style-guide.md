# Thesis Style Guide

Reference document for the `writer` skill. Contains IEEE style conventions, equation formatting, citation guidelines, figure placeholders, table formatting, field-specific terminology, and common pitfalls.

## Plan and Evidence Authority

Every chapter MUST be written from an approved `plan.md` and its sibling `evidence.md`.

1. `plan.md` is the author-readable content and structure authority.
2. `evidence.md` is the grounding and provenance authority and cannot introduce or alter planned content.
3. Every point ID must occur exactly once in each file; missing or orphan IDs block writing.
4. If a point is in the plan, it MUST appear in the document unless it is `structure-only` or `open`.
5. If a reference is in the plan, it MUST be cited only when the matching ledger card approves it.
6. Do not add content beyond the plan or omit planned content without explicit approval.

### Author-readable plan structure

```markdown
# Plan: [Title]
Status: approved

## Narrative Thread
[1-2 sentences describing the story this chapter tells]

## Sections

### Section 1: [Title]
**Purpose:** [C01-S01-PU01 | structure-only] [narrative function]

#### Paragraph 1
- [C01-S01-P01-CL01 | write-ready] [bounded proposition] \cite{ref1,ref2}
- [C01-S01-P01-PF01 | write-ready] [project-specific proposition]
- [C01-S01-P01-LK01 | structure-only] [ordering instruction; no thesis sentence]

### Section 2: [Title]
[continue with stable typed point IDs]

## Figures
- Figure 1: [Description of what it shows]
- Figure 2: [Description]

## Unresolved points
[readable index of open IDs/questions; must be empty for writer input]
```

Plan points contain only an ID and status as machine metadata. Types, origins,
evidence cards, passages, search receipts, project locators, derivation steps,
author attestations, inference warrants, and full `OPEN` gap records belong in
the matching `evidence.md` entries. The point types are `CLAIM`, `PROJECT_FACT`,
`DERIVATION`, `AUTHOR_ASSERTION`, `INFERENCE`, `LINK`, `PURPOSE`, and `OPEN`.
The writer reads these types from the ledger and uses only `write-ready`
technical points. `structure-only` points guide structure; `open` blocks
drafting.

The plan header contains only the author-visible `Status: draft|approved` field.
Document type, recording date, parent path, and grounding bookkeeping belong in
`evidence.md`. Determine readiness from each in-scope point's status and matching
receipt; do not require or add a block-level grounding field in `plan.md`.

## Figure Placeholders

The `writer` creates figure placeholders in LaTeX. The `figure-generator` skill later replaces these with actual figures where possible.

```latex
\begin{figure}[tb]
\centering
\fbox{\parbox{0.8\textwidth}{
\textbf{FIGURE PLACEHOLDER}\\[1em]
\textit{Description:} [Detailed description of what this figure shows]\\[0.5em]
\textit{Type:} [Data plot / Block diagram / Schematic / Photo]\\[0.5em]
\textit{Data source:} [Path to data file or source code, if applicable]\\[0.5em]
\textit{Axes/Labels:} [X-axis: time (s), Y-axis: amplitude (mV)]\\[0.5em]
\textit{Key features:} [What the reader should observe]
}}
\caption{[Caption text]}
\label{fig:label}
\end{figure}
```

**Figure types for thesis:**
- Time series plots
- Scatter plots with regression
- Bar charts with error bars
- Box plots
- Bland-Altman plots
- Block diagrams of systems
- Signal processing pipelines
- Sensor placement diagrams
- Circuit schematics

## IEEE Style Guidelines

### Language

Prose voice is governed by `prose-style.md` in this directory — density rules, banned modifiers, banned AI sentence patterns, em-dash policy, and register. It is binding; read it before drafting. Headlines:

- One fact per sentence; fewest words that carry the claim
- Technical terms fully defined on first use
- No intensifiers, importance-claiming adjectives, or hedging stacks
- No contrast scaffolds, staccato drama, or em-dash interpolation pairs
- Active voice preferred; plain verbs over verb-jargon

### Equations
- Number all equations
- Define all variables immediately after
- Use consistent notation throughout

```latex
\begin{equation}
x_{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}
\label{eq:rms}
\end{equation}
where $x_i$ is the $i$th sample of the signal and $N$ is the total number of samples.
```

### Citations
- IEEE numeric style: [1], [2], [1]-[3]
- Multiple citations: [1], [4], [7]
- Citation with author: Smith et al. [5] showed...

### Tables
```latex
\begin{table}[tb]
\centering
\caption{[Table caption above table]}
\label{tab:label}
\begin{tabular}{lcc}
\toprule
Parameter & Group A & Group B \\
\midrule
Mean & 0.42 & 0.38 \\
SD & 0.05 & 0.07 \\
\bottomrule
\end{tabular}
\end{table}
```

## Evidence and Citation Requirements

**STRICT**: All citations must come from Zotero library.

### Before Writing
1. Confirm the plan is `approved` and every in-scope point has a stable ID and status.
2. Confirm every ID has exactly one matching ledger entry and no orphan entry exists.
3. Confirm the ledger scope semantically matches the planned content.
4. Confirm every literature `CLAIM` has an approved Zotero evidence card in `evidence.md`.
5. Confirm project facts, derivations, author assertions, and inferences have
   their type-specific receipts.
6. Stop on any non-ready point, missing receipt, or mismatch and return its ID to planning.

### During Writing
1. Map every technical sentence to stable plan point IDs.
2. Cite `CLAIM` sentences with only the matching ledger card's approved Zotero item keys.
3. Keep citations adjacent to the supported sentence or clause.
4. Do not add, fabricate, or substitute citations.
5. Do not force citations onto `LINK` or `PURPOSE` metadata.
6. Preserve the approved provenance for `PROJECT_FACT`, `DERIVATION`,
   `AUTHOR_ASSERTION`, and `INFERENCE` points.

### Citation scope

Citation need follows point type, not a density target. Background prose often
contains more literature `CLAIM` points; methods and results often contain more
`PROJECT_FACT` and `DERIVATION` points. Never use a paragraph-level citation to
cover several propositions with different evidence.

## Field-Specific Language and Terminology

Adapt language, terminology, and conventions to match the target discipline. Every field has established vocabulary, preferred phrasings, and notation conventions that signal expertise and ensure clarity for the intended audience. Rather than prescribing conventions for any one field, calibrate to the author's field by observing how its literature is written.

**Identify the field's conventions from its literature:**
- Review terminology used in recent high-impact papers in the target journal
- Note field-specific abbreviations, units, and notation systems
- Identify preferred terms where the field distinguishes near-synonyms (e.g., "participants" vs. "subjects," "specimens" vs. "samples")
- Observe how methods, apparatus, and techniques are conventionally described
- Follow the field's authoritative nomenclature and standardized naming schemes where they exist

**General Principles:**

- **Match audience expertise**: Define terms appropriate to the audience's level
- **Define abbreviations at first use**: introduce the full term, then the abbreviation in parentheses
- **Maintain consistency**: Use the same term for the same concept throughout
- **Use precise, formal terminology**: prefer the exact technical term over an informal paraphrase
- **Report quantities with standard units and notation**: follow SI conventions unless the field dictates otherwise
- **Verify terminology**: Use approved Zotero evidence and the author's existing
  writing. If the corpus lacks the needed authority, return the gap to planning;
  do not search externally from the writer.

## Common Writing Pitfalls

- Mixing tenses inappropriately (use past tense for methods/results, present for established facts)
- Excessive jargon or undefined acronyms
- Paragraph breaks that disrupt logical flow
- Missing transitions between sections
- Inconsistent notation or terminology
