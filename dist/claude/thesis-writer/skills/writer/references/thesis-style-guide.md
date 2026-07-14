# Thesis Style Guide

Reference document for the `writer` skill. Contains IEEE style conventions, equation formatting, citation guidelines, figure placeholders, table formatting, field-specific terminology, and common pitfalls.

## Plan Authority

Every chapter MUST be written from an approved plan.md file.

1. If a point is in the plan, it MUST appear in the document
2. If a reference is in the plan, it MUST be cited
3. Do not add content beyond the plan without explicit approval
4. Do not omit planned content without explicit approval

### Plan Structure

```markdown
# Chapter: [Title]
Type: [background|meat|conclusions|future-work]

## Narrative Thread
[1-2 sentences describing the story this chapter tells]

## Sections

### Section 1: [Title]
Points:
- Point A \cite{ref1, ref2}
- Point B \cite{ref3}

### Section 2: [Title]
Points:
- Point C \cite{ref4}
...

## Figures
- Figure 1: [Description of what it shows]
- Figure 2: [Description]

## Key References
- ref1: [Brief note on how it's used]
- ref2: [Brief note]
```

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

## Citation Requirements

**STRICT**: All citations must come from Zotero library.

### Before Writing
1. Verify all plan references exist in Zotero
2. Use zotero-research agent to validate citations
3. Flag any missing references to user

### During Writing
1. Every factual claim needs citation
2. Use Zotero item keys for \cite{}
3. Do not fabricate or placeholder citations

### Citation Density Guidelines
- Background chapters: High (1-3 citations per paragraph)
- Meat chapter intro: Medium
- Meat chapter methods: Low (cite established methods)
- Meat chapter results: Low (own work)
- Meat chapter discussion: Medium (comparison to literature)

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
- **Verify terminology**: Consult field-specific style guides and recent papers from the target journal

## Common Writing Pitfalls

- Mixing tenses inappropriately (use past tense for methods/results, present for established facts)
- Excessive jargon or undefined acronyms
- Paragraph breaks that disrupt logical flow
- Missing transitions between sections
- Inconsistent notation or terminology
