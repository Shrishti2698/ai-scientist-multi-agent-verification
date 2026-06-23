import json
import unittest
from pathlib import Path

from ai_scientist.ingestion import RawPaperIngestor


ROOT = Path(__file__).resolve().parents[1]


class IngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ingestor = RawPaperIngestor()
        cls.raw_dir = ROOT / "data" / "raw_papers"

    def test_ingests_supported_raw_files(self) -> None:
        papers = self.ingestor.ingest_directory(self.raw_dir)
        self.assertEqual(len(papers), 3)
        titles = {paper.title for paper in papers}
        self.assertIn("Retrieval-Augmented Language Models for Factual Grounding", titles)
        self.assertIn("Multi-Agent Debate for Evidence-Sensitive Reasoning", titles)

    def test_exports_normalized_corpus_json(self) -> None:
        papers = self.ingestor.ingest_directory(self.raw_dir)
        output_path = ROOT / "data" / "tmp_ingested_test.json"
        self.ingestor.export_corpus(papers, output_path)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["papers"]), 3)
        output_path.unlink()

    def test_ingests_uploaded_text_bytes(self) -> None:
        payload = (
            "title: Uploaded Verification Paper\n"
            "year: 2026\n"
            "authors: A. Student\n"
            "topics: ai, verification\n\n"
            "Abstract: This uploaded paper studies claim verification in AI systems.\n"
        ).encode("utf-8")
        papers = self.ingestor.ingest_uploaded("uploaded_paper.md", payload)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "Uploaded Verification Paper")


if __name__ == "__main__":
    unittest.main()
