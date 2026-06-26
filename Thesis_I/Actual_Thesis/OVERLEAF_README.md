# AI-Scientist Thesis Build Notes

If you upload only this `Actual_Thesis` folder, compile `thesis.tex` or `main.tex`.

If you upload the whole repository, compile the root-level `main.tex`, which delegates to `thesis.tex`.

The template follows a formal book layout:

- `book` class with double-sided chapter openings
- Times-like academic serif fonts
- formal front-matter pages (cover, title, declaration, certificate, abstract)
- roman-numbered preliminary pages and styled headers in the main matter
- TikZ is used for the architecture and pipeline figures, so no external figure
  files are needed apart from the institute logo in `Figures/IIITLOGO.png`

Files/folders to upload to Overleaf if you upload only the thesis folder:

- `main.tex`
- `thesis.tex`
- `Thesis_Title.tex`
- `references.bib`
- `HeadTail/`
- `Symbol/`
- `Chapter1/` through `Chapter10/`
- `Appendix/`
- `Figures/`

Suggested Overleaf build sequence when using BibTeX:

1. Compile once with LaTeX.
2. Run BibTeX.
3. Compile twice more with LaTeX.

If Overleaf uses Latexmk, it will usually perform this sequence automatically. The
thesis uses `\input` instead of `\include` for chapters, so it does not create
per-chapter `.aux` files; if a stale build error appears, use "Recompile from
scratch" after uploading the latest files.
