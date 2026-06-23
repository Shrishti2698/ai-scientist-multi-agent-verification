import json
import unittest
from pathlib import Path

from ai_scientist.literature import LiteratureCollectionService
from ai_scientist.models import PaperDocument


ROOT = Path(__file__).resolve().parents[1]


class StubFetcher:
    def __init__(self, papers: list[PaperDocument]):
        self.papers = papers

    def search(self, query: str, limit: int = 5) -> list[PaperDocument]:
        return self.papers[:limit]


class LiteratureTests(unittest.TestCase):
    def test_collection_merges_duplicate_titles(self) -> None:
        shared = PaperDocument(
            paper_id="X1",
            title="Shared Paper",
            abstract="A shared abstract.",
            year=2024,
            authors=["A"],
            topics=["ai"],
        )
        unique = PaperDocument(
            paper_id="X2",
            title="Unique Paper",
            abstract="A unique abstract.",
            year=2025,
            authors=["B"],
            topics=["ml"],
        )
        service = LiteratureCollectionService(
            semantic_scholar=StubFetcher([shared]),
            arxiv=StubFetcher([shared, unique]),
        )

        papers = service.collect("agents", limit_per_source=5)
        self.assertEqual(len(papers), 2)
        self.assertEqual(papers[0].title, "Shared Paper")
        self.assertEqual(papers[1].title, "Unique Paper")

    def test_export_writes_corpus_json(self) -> None:
        service = LiteratureCollectionService(
            semantic_scholar=StubFetcher(
                [
                    PaperDocument(
                        paper_id="X1",
                        title="Exported Paper",
                        abstract="Export abstract.",
                        year=2024,
                        authors=["A"],
                        topics=["topic"],
                    )
                ]
            ),
            arxiv=StubFetcher([]),
        )

        output_path = ROOT / "data" / "tmp_literature_export.json"
        service.export(service.collect("verification"), output_path)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["papers"][0]["title"], "Exported Paper")
        output_path.unlink()


if __name__ == "__main__":
    unittest.main()
