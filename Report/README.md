# Report — IEEE Research Paper (HF-Digital Twin Platform)

This folder contains the LaTeX source for the project research paper in **IEEE conference format**.

## Files

- **`main.tex`** — Main document (abstract, introduction, related work, methodology, implementation, evaluation, discussion, conclusion).
- **`references.bib`** — Bibliography in IEEE-style (BibTeX).
- **`figures/`** — Standalone TikZ figure sources (optional; figures are also defined inline in `main.tex`).

## Build

From this directory (`Report/`):

```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

Or use your editor/IDE LaTeX build (e.g. LaTeX Workshop in VS Code).

## Requirements

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX).
- Packages used: `IEEEtran`, `amsmath`, `amssymb`, `cite`, `url`, `booktabs`, `graphicx`, `float`, `tikz`, `subcaption`, `multirow`, `array`, `xcolor`, `inputenc`.

## Output

- **`main.pdf`** — Compiled paper with tables and figures (architecture, flowchart, data pipeline).
