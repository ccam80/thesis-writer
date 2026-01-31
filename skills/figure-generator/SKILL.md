---
name: figure-generator
description: "Generates figures from placeholders in .tex files. Creates Python matplotlib scripts for data figures, TikZ/Python schematics for diagrams. Maintains a shared plot_defaults.py for consistent styling. Flags complex figures for the user. Runs after the writer skill."
allowed-tools: [Read, Write, Edit, Bash, Task]
---

# Figure Generator

## Overview

This skill runs after the `writer` skill has produced LaTeX prose. It reads .tex files, finds figure placeholders, and generates actual figures where possible. It replaces `\figurePlaceholder{...}` blocks with `\includegraphics{...}` pointing to generated output.

## When to Use This Skill

- After `writer` has produced .tex files containing figure placeholders
- When updating figures after data or methods changes
- When regenerating specific figures

## Plot Defaults File

**Before generating any figures**, check for `figures/plot_defaults.py` in the document directory. If it does not exist, create it. This file defines all shared styling for consistency across the entire thesis.

```python
# figures/plot_defaults.py
# Shared matplotlib defaults for all thesis figures.
# Edit this file to change styling globally.

import matplotlib.pyplot as plt
import matplotlib as mpl

# --- Colour palette ---
COLOURS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'tertiary': '#2ca02c',
    'quaternary': '#d62728',
    'grey': '#7f7f7f',
    'light_grey': '#c7c7c7',
}
COLOUR_CYCLE = [COLOURS['primary'], COLOURS['secondary'], COLOURS['tertiary'],
                COLOURS['quaternary'], COLOURS['grey']]

# --- Figure sizes (inches) ---
SINGLE_COL = (6.5, 4.0)
DOUBLE_COL = (6.5, 3.0)    # wide but short
HALF_COL = (3.15, 3.0)     # for subfigures

# --- Font and text ---
FONT_FAMILY = 'serif'
FONT_SIZE = 10
LABEL_SIZE = 11
TICK_SIZE = 9
LEGEND_SIZE = 9

# --- Line and marker ---
LINE_WIDTH = 1.5
MARKER_SIZE = 4

# --- Export ---
DPI = 300
FORMATS = ['pdf', 'png']  # pdf for LaTeX, png for preview


def apply():
    """Apply thesis defaults to matplotlib rcParams."""
    mpl.rcParams.update({
        'font.family': FONT_FAMILY,
        'font.size': FONT_SIZE,
        'axes.labelsize': LABEL_SIZE,
        'axes.titlesize': LABEL_SIZE,
        'xtick.labelsize': TICK_SIZE,
        'ytick.labelsize': TICK_SIZE,
        'legend.fontsize': LEGEND_SIZE,
        'figure.figsize': SINGLE_COL,
        'figure.dpi': DPI,
        'savefig.dpi': DPI,
        'savefig.bbox': 'tight',
        'lines.linewidth': LINE_WIDTH,
        'lines.markersize': MARKER_SIZE,
        'axes.prop_cycle': mpl.cycler(color=COLOUR_CYCLE),
    })


def savefig(fig, path_stem):
    """Save figure in all configured formats."""
    for fmt in FORMATS:
        fig.savefig(f'{path_stem}.{fmt}', dpi=DPI, bbox_inches='tight')
```

**Every generated script must**:
1. `import plot_defaults; plot_defaults.apply()` at the top
2. Use `plot_defaults.savefig(fig, path)` to export
3. Reference `plot_defaults.COLOURS`, `plot_defaults.SINGLE_COL`, etc. for sizing and colours

**If `plot_defaults.py` already exists**, read it and respect the author's customisations. Only add missing keys — never overwrite existing choices.

## Figure Categories

### 1. Data Plots (auto-generate)

For placeholders that specify data sources, generate Python scripts using matplotlib:

**Input** (from placeholder):
- Data source path (CSV, HDF5, or reference to source code that produces data)
- Plot type (time series, scatter, bar chart, box plot, Bland-Altman, etc.)
- Axes labels and units
- Key features to highlight

**Output**:
- Python script in `figures/scripts/` that reads data and produces the plot
- Generated figure in `figures/` (PDF and PNG)
- Updated .tex with `\includegraphics` replacing the placeholder

**Script requirements**:
- Self-contained: runs independently with `python script.py`
- Imports and applies `plot_defaults` for consistent styling
- Uses matplotlib only (not seaborn)
- Outputs both PDF (for LaTeX) and PNG (for preview)

### 2. Simple Schematics (auto-generate)

For block diagrams, system architectures, signal processing pipelines:

**Approach**: Generate using TikZ directly in LaTeX, or Python (matplotlib/networkx) for more complex diagrams.

**Types**:
- Block diagrams of systems/methods
- Signal processing pipelines
- Simple circuit representations
- Algorithm flowcharts
- Data flow diagrams

### 3. Complex/Custom Figures (flag for user)

Some figures cannot be auto-generated:
- Photographs or microscopy images
- Figures requiring the author's unpublished data in inaccessible formats
- Highly specialised domain diagrams
- Figures requiring specific artistic choices

**Action**: Keep the placeholder but add a `% TODO: MANUAL FIGURE REQUIRED` comment explaining what's needed and why it couldn't be auto-generated.

## Workflow

1. **Check defaults**: Read or create `figures/plot_defaults.py`
2. **Scan**: Read .tex file(s), find all figure placeholder blocks
3. **Classify**: For each placeholder, determine category (data plot / schematic / complex)
4. **Generate**: For auto-generatable figures:
   a. Create Python script (importing plot_defaults) or TikZ code
   b. Run script to produce figure file
   c. Replace placeholder with `\includegraphics`
5. **Flag**: For complex figures, add TODO comments
6. **Report**: Summary of what was generated, what was flagged, any issues

## LaTeX Integration

Replace:
```latex
\begin{figure}[tb]
\centering
\fbox{\parbox{0.8\textwidth}{
\textbf{FIGURE PLACEHOLDER}\\[1em]
...
}}
\caption{Caption text.}
\label{fig:label}
\end{figure}
```

With:
```latex
\begin{figure}[tb]
\centering
\includegraphics[width=\columnwidth]{figures/fig_label}
\caption{Caption text.}
\label{fig:label}
\end{figure}
```

## What This Skill Does NOT Do

- Does not change prose content
- Does not add or remove figures beyond what the plan specifies
- Does not modify captions (preserves writer's captions)
- Does not change figure labels or cross-references

## Integration

- **Receives from**: `writer` skill (.tex files with figure placeholders)
- **Reads**: Data files referenced in placeholders, source code for data generation
- **Maintains**: `figures/plot_defaults.py` (shared styling for all thesis figures)
- **Produces**: Figure files in `figures/`, Python scripts in `figures/scripts/`, updated .tex files
- **Hands off to**: `formatter` skill for final LaTeX polish
