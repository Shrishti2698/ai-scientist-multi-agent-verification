# PatchOps Thesis Build Notes

If you upload only this `Actual_Thesis` folder, compile `thesis.tex` or `main.tex`.

If you upload the whole PatchOps repository, compile the root-level `main.tex`.

If Overleaf's free plan times out, compile `main_fast.tex` instead:

- Upload only `Actual_Thesis`: set the main document to `main_fast.tex` inside this folder.
- Upload the whole repository: set the main document to the root-level `main_fast.tex`.

The fast entrypoint keeps all chapter text, tables, and citations visible, but it
uses draft image boxes, skips the list of figures/tables, and uses an inline
bibliography so Overleaf does not need the expensive BibTeX + multipass cycle.
Use the normal `thesis.tex`/`main.tex` build for final PDF generation.

The active template now follows the inspiration structure more closely:

- `book` layout with double-sided chapter openings
- Times-like academic serif fonts
- formal front matter pages with placeholders
- roman-numbered preliminary pages and styled headers in the main matter

`patchops_thesis.tex` is only a compatibility wrapper that delegates to `thesis.tex`.
The old `chapters/` directory is a stale skeleton and is not used by the active build.

Files/folders to upload to Overleaf if you upload only the thesis folder:

- `main.tex`
- `main_fast.tex`
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

If Overleaf uses Latexmk, it will usually perform this sequence automatically.

If the project previously failed with an error like `I can't write on file
Chapter9/chapter9.aux`, use Overleaf's "Recompile from scratch" option after
uploading the latest files. The thesis now uses `\input` instead of `\include`
for chapters, so it should no longer create per-chapter `.aux` files.
