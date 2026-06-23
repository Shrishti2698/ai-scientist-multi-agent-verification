from __future__ import annotations

import argparse
from pathlib import Path

from ai_scientist.demo_assets import DemoAssetBuilder


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a lightweight HTML demo report.")
    parser.add_argument("--question", required=True, help="Research question for the demo.")
    parser.add_argument("--corpus", default=None, help="Corpus JSON path.")
    parser.add_argument("--output", default=None, help="Output HTML path.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    corpus = Path(args.corpus) if args.corpus else root / "data" / "sample_corpus.json"
    output = Path(args.output) if args.output else root / "results" / "latest" / "demo_report.html"

    builder = DemoAssetBuilder()
    builder.export_html_report(corpus, args.question, output)
    print(f"Demo HTML written to {output}")


if __name__ == "__main__":
    main()
