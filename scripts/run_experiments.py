from __future__ import annotations

import argparse
from pathlib import Path

from ai_scientist.config import Settings
from ai_scientist.experiment_runner import ExperimentRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run benchmark experiments for AI-Scientist.")
    parser.add_argument("--corpus", default=None, help="Path to corpus JSON. Defaults to data/sample_corpus.json.")
    parser.add_argument("--benchmark", default=None, help="Path to benchmark JSON. Defaults to data/benchmark_claims.json.")
    parser.add_argument("--live-query", default=None, help="Optional live literature query to refresh the corpus before evaluation.")
    parser.add_argument("--live-limit-per-source", type=int, default=5, help="Live fetch limit per source.")
    parser.add_argument("--live-output", default=None, help="Where to save the refreshed live corpus JSON.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    runner = ExperimentRunner(
        settings=Settings(),
        corpus_path=Path(args.corpus) if args.corpus else root / "data" / "sample_corpus.json",
        benchmark_path=Path(args.benchmark) if args.benchmark else root / "data" / "benchmark_claims.json",
        live_query=args.live_query,
        live_limit_per_source=args.live_limit_per_source,
        live_output_path=Path(args.live_output) if args.live_output else None,
    )
    if args.live_query:
        refreshed, message = runner.try_refresh_corpus_from_live_sources()
        print(message if refreshed else f"Live refresh skipped: {message}")
    summaries = runner.export(root / "results" / "latest")
    for summary in summaries:
        print(
            f"{summary.system_name}: accuracy={summary.accuracy}, "
            f"avg_confidence={summary.average_confidence}, "
            f"avg_evidence={summary.average_evidence_count}"
        )


if __name__ == "__main__":
    main()
