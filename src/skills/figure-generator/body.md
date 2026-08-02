# Figure Generator

<!-- style:image-output -->

## Overview

This skill runs after the `writer` skill has produced LaTeX prose. It reads .tex files, finds figure placeholder blocks in the `../writer/references/figure-placeholder.md` format, and generates actual figures where possible. It replaces each placeholder with `\includegraphics{...}` pointing to generated output.

## Plot Defaults File

**Before generating any figures**, check for `plot_defaults.py` at the project root. If it does not exist, create it. This file defines all shared styling for consistency across the entire thesis.

```python
# plot_defaults.py
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
FONT_SIZE = 12
LABEL_SIZE = 12
TICK_SIZE = 11
LEGEND_SIZE = 11

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


def write_tikz_colours(path='tikz_colours.tex'):
    """Emit the shared palette as \\definecolor lines for TikZ figures."""
    with open(path, 'w', encoding='utf-8') as handle:
        for name, value in COLOURS.items():
            handle.write(f'\\definecolor{{{name}}}{{HTML}}{{{value.lstrip("#").upper()}}}\n')
```

**Every `render.py` must**:
1. `import plot_defaults; plot_defaults.apply()` at the top
2. Take its output stem as `sys.argv[1]` and export with `plot_defaults.savefig(fig, sys.argv[1])`
3. Reference `plot_defaults.COLOURS`, `plot_defaults.SINGLE_COL`, etc. for sizing and colours

Generate at the width the figure is placed at. A figure generated wider than its `\includegraphics` width is scaled down by LaTeX, which shrinks every label below the size `plot_defaults` set. No font size in this file may drop below 11.

## Figure Categories

A placeholder supplies the data source path (CSV, HDF5, or a reference to the code that produces the data), the plot type, the axes labels and units, and the features the plan requires the figure to show.

Each generated figure produces:

- a directory named for the figure, beside the `.tex` that uses it, holding one `render.py`
- `fig/<name>.pdf` and `fig/<name>.png` in that `.tex`'s own `fig/` directory
- the `.tex` placeholder replaced by `\includegraphics{fig/<name>}`

Use matplotlib, not seaborn. Schematics go through TikZ instead, with `render.tex` in place of `render.py`; see below.

## Project layout

Nothing registers a figure. Creating the directory is what adds it.

```text
plot_defaults.py            shared matplotlib styling
tikz_defaults.tex           shared TikZ preamble
tikz_colours.tex            generated from plot_defaults.COLOURS
build_figures.py            builds every figure it discovers

chapters/03-methods/
    methods.tex             \includegraphics{fig/settling_time}
    settling_time/
        render.py
    control_loop/
        render.tex
    fig/                    generated; never edited by hand
        settling_time.pdf
        settling_time.png
        control_loop.pdf
        control_loop.png
```

A figure directory holds exactly one entry point. `render.py` and `render.tex` in the same directory is an error, not a choice.

Where a figure cannot be generated, keep the placeholder and add a `% TODO: MANUAL FIGURE REQUIRED` comment naming what is needed and why.

## TikZ Figures

Schematics are standalone LaTeX documents, never inline `tikzpicture` blocks. Each compiles on its own, so there is a file to open and hand to the reviewer before it reaches the chapter.

### Shared preamble

`tikz_defaults.tex` at the project root is the preamble every schematic inputs. Create it if absent. If it exists, respect the author's choices: add missing entries, never overwrite existing ones.

```latex
% tikz_defaults.tex
\usepackage{tikz}
\usepackage{siunitx}
\usetikzlibrary{arrows.meta, positioning, calc}

\input{tikz_colours}   % generated by plot_defaults.write_tikz_colours()

\tikzset{
  every node/.style={font=\fontsize{12}{14}\selectfont},
  block/.style={draw, rectangle, minimum height=1cm, minimum width=1.5cm},
  signal/.style={-{Stealth[length=2mm]}, line width=1.5pt},
}
```

Font family and base size here must match the thesis body text, and the node font size must match `plot_defaults.FONT_SIZE`. A standalone document inherits nothing from the thesis preamble.

Colours come from `plot_defaults.COLOURS` through `plot_defaults.write_tikz_colours()`, so one palette change reaches both pipelines. `plot_defaults.py` is canonical; `tikz_colours.tex` is generated and never hand-edited.

### Figure document

```latex
% chapters/03-methods/control_loop/render.tex
\documentclass[12pt,border=2pt]{standalone}
\input{tikz_defaults}
\begin{document}
\begin{tikzpicture}
  \node[block] (ctrl) {Controller};
  \node[block, right=2cm of ctrl] (plant) {Plant};
  \draw[signal] (ctrl) -- (plant);
\end{tikzpicture}
\end{document}
```

The `standalone` class crops to the drawing, so it is emitted at its natural size. Size the drawing to its placement width: a schematic scaled down by `\includegraphics` loses label size exactly as a plot does.

## Build

`build_figures.py` ships with this skill under `scripts/`. Copy it to the project root on first use, alongside `plot_defaults.py` and `tikz_defaults.tex`.

It walks the project, finds every directory holding a `render.py` or `render.tex`, and writes the outputs into the `fig/` directory beside that figure directory's parent. A `render.py` is run with the project root on `PYTHONPATH` and its output stem as `sys.argv[1]`, so `import plot_defaults` resolves and `plot_defaults.savefig` writes both formats. A `render.tex` is compiled with `pdflatex` with the project root on `TEXINPUTS`, so the bare `\input{tikz_defaults}` resolves, then rasterised to PNG at `plot_defaults.DPI`.

The chapter includes the PDF. The PNG exists for the render inspection and the reviewer pass.

```
python build_figures.py              build what is stale
python build_figures.py --force      rebuild everything
python build_figures.py --only NAME  build one figure
python build_figures.py --list       list what was discovered
```

A figure rebuilds when any file in its directory is newer than its PDF, or when `plot_defaults.py`, `tikz_defaults.tex`, or `tikz_colours.tex` changed. `tikz_colours.tex` is only rewritten when the palette actually changed, so an unchanged palette does not force a rebuild. Exit status is 1 if any figure failed and 2 if the layout is malformed; a failure reports the underlying traceback or LaTeX log and does not stop the other figures.

## Workflow

1. **Check defaults**: read or create `plot_defaults.py`, `tikz_defaults.tex`, and `build_figures.py` at the project root.
2. **Scan**: read the `.tex` file(s) and find every figure placeholder block.
3. **Generate**: create the figure directory, write its `render.py` or `render.tex`, run `build_figures.py --only <name>`, and open the PNG it produced.
4. **Resolve**: fix every defect visible in the render, then rebuild.
5. **Review**: send the reviewer agent the render and the placeholder's brief. Resolve its findings and rebuild until a pass returns nothing.
6. **Place**: replace the placeholder with `\includegraphics{fig/<name>}`, or add the `% TODO: MANUAL FIGURE REQUIRED` comment where the figure could not be generated.
7. **Report**: what was generated, what was flagged, what failed.

## LaTeX Integration

Replace the placeholder `\fbox{\parbox{...}}` contents of the `figure` environment, keeping its caption and label:

```latex
\begin{figure}[tb]
\centering
\includegraphics[width=\columnwidth]{fig/label}
\caption{Caption text.}
\label{fig:label}
\end{figure}
```

## What This Skill Does NOT Do

- Does not change prose content
- Does not add or remove figures beyond what the plan specifies
- Does not change figure labels or cross-references

## Integration

- **Receives from**: `writer` skill (.tex files with figure placeholders)
- **Reads**: Data files referenced in placeholders, source code for data generation
- **Maintains**: `plot_defaults.py`, `tikz_defaults.tex`, and `build_figures.py` at the project root
- **Produces**: Per-figure directories with `render.py` or `render.tex`, outputs in each chapter's `fig/` directory, updated .tex files
- **Hands off to**: `formatter` skill for final LaTeX polish
