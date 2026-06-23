$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"

python scripts/run_experiments.py --corpus data/final_demo_corpus.json --benchmark data/final_benchmark_claims.json
python scripts/analyze_failures.py
python scripts/export_thesis_assets.py
python scripts/generate_thesis_assets.py
python scripts/generate_demo_html.py --question "Do critic-guided verification loops improve research claim checking?"

Write-Host ""
Write-Host "Demo-day assets refreshed in results/latest" -ForegroundColor Green
Write-Host "Open results/latest/report.md and results/latest/demo_report.html" -ForegroundColor Green
