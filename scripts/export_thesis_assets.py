from __future__ import annotations

from pathlib import Path

from ai_scientist.thesis_exports import ThesisExportBuilder


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    builder = ThesisExportBuilder()
    builder.export_all(
        summary_path=root / "results" / "latest" / "summary.json",
        output_dir=root / "results" / "latest",
    )
    print("Thesis assets exported to results/latest")


if __name__ == "__main__":
    main()
