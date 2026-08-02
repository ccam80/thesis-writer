# Figure Placeholder Format

Shared interface: `writer` creates placeholders in this format; `figure-generator` finds and replaces them.

```latex
\begin{figure}[tb]
\centering
\fbox{\parbox{0.8\textwidth}{
\textbf{FIGURE PLACEHOLDER}\\[1em]
\textit{Description:} [What this figure shows]\\[0.5em]
\textit{Type:} [Data plot / Block diagram / Schematic / Photo]\\[0.5em]
\textit{Data source:} [Path to data file or source code, if applicable]\\[0.5em]
\textit{Axes/Labels:} [X-axis: time (s), Y-axis: amplitude (mV)]\\[0.5em]
\textit{Key features:} [What the reader should observe]
}}
\caption{[Caption text]}
\label{fig:label}
\end{figure}
```

Common thesis figure types: time series, scatter with regression, bar chart with error bars, box plot, Bland-Altman, block diagram, signal-processing pipeline, sensor placement diagram, circuit schematic.
