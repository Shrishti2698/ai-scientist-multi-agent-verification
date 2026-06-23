from __future__ import annotations

import argparse
from pathlib import Path

from ai_scientist.ingestion import IngestionError, RawPaperIngestor


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a normalized corpus from local raw paper files.")
    parser.add_argument("--input-dir", required=True, help="Directory containing raw paper files.")
    parser.add_argument("--output", required=True, help="Output JSON corpus path.")
    args = parser.parse_args()

    ingestor = RawPaperIngestor()
    try:
        papers = ingestor.ingest_directory(args.input_dir)
    except IngestionError as exc:
        raise SystemExit(str(exc)) from exc

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ingestor.export_corpus(papers, output_path)
    print(f"Built corpus with {len(papers)} papers at {output_path}")


if __name__ == "__main__":
    main()
