# Phase 19: Interactive Streamlit UI

## Goal

Provide an actual interactive browser interface so the system can be explored live instead of only through generated files.

## What the UI supports

- choosing the frozen demo corpus,
- entering a research question,
- running the multi-agent pipeline live,
- viewing baseline outputs side by side,
- inspecting orchestration trace,
- reviewing verified claims and evidence snippets.

## Recommended demo mode

Use the frozen corpus in the Streamlit app during presentations. This keeps the interface interactive without introducing live API risk.

## Launch command

```powershell
$env:PYTHONPATH='src'
streamlit run app.py
```
