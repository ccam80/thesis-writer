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
- Electrode placement diagrams
- Circuit schematics

## IEEE Style Guidelines

### Language
- Concise, direct prose
- Technical terms fully defined on first use
- Avoid flowery language and hedging
- Active voice preferred

### Equations
- Number all equations
- Define all variables immediately after
- Use consistent notation throughout

```latex
\begin{equation}
HRV_{RMSSD} = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N-1}(RR_{i+1} - RR_i)^2}
\label{eq:rmssd}
\end{equation}
where $RR_i$ is the $i$th RR interval and $N$ is the total number of intervals.
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

Adapt language, terminology, and conventions to match the specific scientific discipline. Each field has established vocabulary, preferred phrasings, and domain-specific conventions that signal expertise and ensure clarity for the target audience.

**Identify Field-Specific Linguistic Conventions:**
- Review terminology used in recent high-impact papers in the target journal
- Note field-specific abbreviations, units, and notation systems
- Identify preferred terms (e.g., "participants" vs. "subjects," "compound" vs. "drug," "specimens" vs. "samples")
- Observe how methods, organisms, or techniques are typically described

**Biomedical and Clinical Sciences:**
- Use precise anatomical and clinical terminology (e.g., "myocardial infarction" not "heart attack" in formal writing)
- Follow standardized disease nomenclature (ICD, DSM, SNOMED-CT)
- Specify drug names using generic names first, brand names in parentheses if needed
- Use "patients" for clinical studies, "participants" for community-based research
- Follow Human Genome Variation Society (HGVS) nomenclature for genetic variants
- Report lab values with standard units (SI units in most international journals)

**Molecular Biology and Genetics:**
- Use italics for gene symbols (e.g., *TP53*), regular font for proteins (e.g., p53)
- Follow species-specific gene nomenclature (uppercase for human: *BRCA1*; sentence case for mouse: *Brca1*)
- Specify organism names in full at first mention, then use accepted abbreviations (e.g., *Escherichia coli*, then *E. coli*)
- Use standard genetic notation (e.g., +/+, +/-, -/- for genotypes)
- Employ established terminology for molecular techniques (e.g., "quantitative PCR" or "qPCR," not "real-time PCR")

**Chemistry and Pharmaceutical Sciences:**
- Follow IUPAC nomenclature for chemical compounds
- Use systematic names for novel compounds, common names for well-known substances
- Report concentrations with appropriate units (mM, μM, nM, or % w/v, v/v)
- Use terms like "bioavailability," "pharmacokinetics," "IC50" consistently with field definitions

**Physics and Engineering:**
- Follow SI units consistently unless field conventions dictate otherwise
- Use standard notation for physical quantities (scalars vs. vectors, tensors)
- Employ established terminology for phenomena (e.g., "quantum entanglement," "laminar flow")
- Specify equipment with model numbers and manufacturers when relevant
- Use mathematical notation consistent with field standards

**Neuroscience:**
- Use standardized brain region nomenclature (e.g., refer to atlases like Allen Brain Atlas)
- Follow conventions for neural terminology (e.g., "action potential" not "spike" in formal writing)
- Use "neural activity," "neuronal firing," "brain activation" appropriately based on measurement method
- Describe recording techniques with proper specificity (e.g., "whole-cell patch clamp," "extracellular recording")

**General Principles:**

- **Match audience expertise**: Define terms appropriate to audience level
- **Define abbreviations at first use**: "messenger RNA (mRNA)"
- **Maintain consistency**: Use the same term for the same concept throughout
- **Avoid field mixing**: Don't use clinical terminology for basic science
- **Verify terminology**: Consult field-specific style guides and recent papers from target journal

## Common Writing Pitfalls

- Mixing tenses inappropriately (use past tense for methods/results, present for established facts)
- Excessive jargon or undefined acronyms
- Paragraph breaks that disrupt logical flow
- Missing transitions between sections
- Inconsistent notation or terminology
