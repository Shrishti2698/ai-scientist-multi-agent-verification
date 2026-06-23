from __future__ import annotations

import argparse
from pathlib import Path

from ai_scientist.literature import LiteratureCollectionService, LiteratureFetchError


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch AI/CS papers from public literature sources.")
    parser.add_argument("--query", required=True, help="Search query for paper collection.")
    parser.add_argument("--limit-per-source", type=int, default=5, help="Number of papers per source.")
    parser.add_argument("--output", required=True, help="Path to output corpus JSON.")
    args = parser.parse_args()

    service = LiteratureCollectionService()
    try:
        papers = service.collect(query=args.query, limit_per_source=args.limit_per_source)
    except LiteratureFetchError as exc:
        raise SystemExit(str(exc)) from exc

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    service.export(papers, output_path)
    print(f"Fetched {len(papers)} papers to {output_path}")


if __name__ == "__main__":
    main()
