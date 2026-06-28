# Overleaf Build Notes

Use `main_fast.tex` on Overleaf free plan when the full thesis build times out.

- `main.tex` or `thesis.tex`: full build, uses BibTeX and includes list of figures/tables.
- `main_fast.tex`: lighter build, uses inline bibliography and skips list of figures/tables.

Recommended main file on Overleaf:

- Set the main file to `main_fast.tex` first.
- Once the document is stable and you want the final polished PDF, switch back to `thesis.tex` or `main.tex`.
