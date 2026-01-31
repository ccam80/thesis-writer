---
name: formatter
description: LaTeX formatting checker and corrector. Ensures figure placement, equation alignment, table formatting, cross-references, and units comply with thesis conventions.
allowed-tools: [Read, Write, Edit, Bash]
---

# Formatter

## Overview

This skill checks and corrects LaTeX formatting in thesis documents. It applies the formatting rules defined in the thesis conventions without changing the content or meaning of the text.

## When to Use This Skill

- After the `writer` skill has produced LaTeX prose
- When reviewing existing chapter files for formatting compliance
- Before compilation to catch formatting issues early

## Formatting Rules

### Figure and Table Placement

1. Use `[tb]` placement specifiers (never `[h!]` or `[H]`)
2. Floats should appear immediately after their first reference where possible
3. Related figures may use `subcaption` for subfigures

```latex
\begin{figure}[tb]
    \centering
    \includegraphics[width=\columnwidth]{graphics/example}
    \caption{Descriptive caption.}
    \label{fig:example}
\end{figure>
```

### Equation Alignment

Multi-line equations must align on the equals sign using `align` (never `eqnarray`):

```latex
\begin{align}
    y &= mx + b \\
    z &= ax^2 + bx + c
\end{align}
```

Use `\left` and `\right` for scalable delimiters:

```latex
\left( \frac{a}{b} \right)
```

### Units with siunitx

All units must use siunitx:

```latex
\SI{5}{\kilo\hertz}
\SI{3.2}{\milli\volt}
\si{\meter\per\second}
\num{1.23e-4}
```

### Cross-References with cleveref

All cross-references must use cleveref:

```latex
\cref{fig:example}      % figure 1
\Cref{fig:example}      % Figure 1 (sentence start)
\cref{eq:rmssd}          % equation (1)
\cref{tab:results}       % table 1
\cref{sec:methods}       % section 2.3
```

### Tables with booktabs

Use `\toprule`, `\midrule`, `\bottomrule` (never `\hline`):

```latex
\begin{table}[tb]
    \centering
    \caption{Caption above table.}
    \label{tab:example}
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

### Font Size

- Never reduce font size in tables or figures (`\small`, `\footnotesize` etc.)
- Let LaTeX handle equation sizing automatically
- Follow document class defaults for captions

### Subfigures

```latex
\begin{figure}[tb]
    \centering
    \begin{subfigure}[b]{0.48\columnwidth}
        \centering
        \includegraphics[width=\textwidth]{graphics/fig_a}
        \caption{First subfigure.}
        \label{fig:sub_a}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\columnwidth}
        \centering
        \includegraphics[width=\textwidth]{graphics/fig_b}
        \caption{Second subfigure.}
        \label{fig:sub_b}
    \end{subfigure}
    \caption{Main figure caption.}
    \label{fig:main}
\end{figure}
```

## Formatting Checklist

Before completing:

- [ ] All figures use `[tb]` placement
- [ ] All floats appear near their first reference
- [ ] Multi-line equations use `align` and align on `=`
- [ ] Delimiters use `\left` and `\right` where appropriate
- [ ] No font size reductions in tables or figures
- [ ] All units use `\SI{}{}` or `\si{}`
- [ ] All cross-references use `\cref{}` / `\Cref{}`
- [ ] Tables use `booktabs` rules
- [ ] No `eqnarray` environments
- [ ] No `[h!]` or `[H]` float specifiers
- [ ] Consistent styling throughout document

## Workflow

1. Read the target `.tex` file(s)
2. Scan for each formatting rule violation
3. Make corrections directly to the LaTeX source
4. Add `% TODO:` comments for issues requiring author decision (e.g., ambiguous figure sizing)
5. Report a summary of changes made

## What This Skill Does NOT Do

- Does not change content, wording, or meaning
- Does not restructure sections
- Does not add or remove citations
- Does not verify reference accuracy (that's `reviewer`)
- Does not compile the document (user handles this)

## LaTeX Style and Packages

### Document Class

The thesis uses a custom or institutional document class. Chapter files use `subfiles` for standalone compilation:

```latex
\documentclass[../main.tex]{subfiles}
\begin{document}
% chapter content
\end{document}
```

### Required Packages

| Package | Options | Purpose |
|---------|---------|---------|
| `graphicx` | | Figure inclusion |
| `tikz` | | Figure markup and overlays |
| `overpic` | `percent` | LaTeX annotations on figures |
| `amsmath` | | Mathematics environments |
| `amsfonts` | | Mathematical fonts |
| `amssymb` | | Mathematical symbols |
| `upgreek` | | Upright Greek letters (e.g., `\upmu`) |
| `siunitx` | | Units and numbers |
| `hyperref` | | Hyperlinks and PDF metadata |
| `cleveref` | `capitalise` | Smart cross-references |
| `subfiles` | | Standalone chapter compilation |
| `booktabs` | | Professional table rules |
| `subcaption` | | Subfigures |
| `multirow` | | Table multirow cells |
| `placeins` | | Float barriers (`\FloatBarrier`) |
| `float` | | Float placement control |

### Package Usage Notes

- **cleveref must be loaded last** (after hyperref)
- **hyperref** should be loaded near-last, before cleveref
- **siunitx**: Use `\SI{value}{unit}` for all quantities, `\si{unit}` for standalone units
- **overpic**: Use `percent` option so coordinates are 0–100 regardless of image size
- **upgreek**: Use `\upmu` not `\mu` for unit prefixes (micro)
- **placeins**: Insert `\FloatBarrier` before new sections to prevent floats drifting past section boundaries
- **subfiles**: Each chapter `.tex` can compile standalone with `\documentclass[../main.tex]{subfiles}`

## Integration

- **Receives from**: `writer` skill (LaTeX prose)
- **Produces**: Formatted LaTeX files
- **Hands off to**: `reviewer` skill for content and reference verification
