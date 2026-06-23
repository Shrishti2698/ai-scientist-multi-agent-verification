from __future__ import annotations

from pathlib import Path

from ai_scientist.failure_analysis import FailureAnalysis


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    analyzer = FailureAnalysis()
    analyzer.export(
        summary_path=root / "results" / "latest" / "summary.json",
        benchmark_path=root / "data" / "benchmark_claims.json",
        output_path=root / "results" / "latest" / "failure_analysis.md",
    )
    print("Failure analysis written to results/latest/failure_analysis.md")


if __name__ == "__main__":
    main()
