from __future__ import annotations

from pathlib import Path

from ai_scientist.thesis_support import ThesisSupport


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    support = ThesisSupport()
    support.export(
        summary_path=root / "results" / "latest" / "summary.json",
        output_dir=root / "results" / "latest",
    )
    print("Thesis assets written to results/latest/")


if __name__ == "__main__":
    main()
