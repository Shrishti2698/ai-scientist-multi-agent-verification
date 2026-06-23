# Final Demo Procedure

## Recommended approach

Use the frozen offline workflow for the actual presentation. Do not depend on live APIs during the defense.

## One-command demo refresh

From the project root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo_day_run.ps1
```

This refreshes:

- `results/latest/report.md`
- `results/latest/failure_analysis.md`
- `results/latest/thesis_tables.md`
- `results/latest/thesis_narrative.md`
- `results/latest/demo_report.html`

## Files to show in the demo

1. `results/latest/report.md`
2. `results/latest/thesis_tables.md`
3. `results/latest/failure_analysis.md`
4. `results/latest/demo_report.html`

## Suggested demo flow

1. Briefly introduce the problem and baselines.
2. Show the benchmark result table.
3. Highlight the critic-loop ablation gain.
4. Open the HTML demo report and walk through:
   - question,
   - orchestration trace,
   - verified claims,
   - critique notes.
5. Close with failure analysis and future work.

## If someone asks about live APIs

Explain:

- live literature retrieval is implemented,
- but the official demo uses a frozen corpus for reproducibility,
- and this is deliberate to avoid network and API instability during evaluation and defense.

## Official frozen inputs

- `data/final_demo_corpus.json`
- `data/final_benchmark_claims.json`
