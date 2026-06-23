import unittest
from pathlib import Path
from types import SimpleNamespace

from app import load_systems


ROOT = Path(__file__).resolve().parents[1]


class StreamlitAppTests(unittest.TestCase):
    def test_load_systems_uses_frozen_corpus(self) -> None:
        system, single_agent, rag, corpus, uploaded_papers, upload_errors = load_systems(
            ROOT / "data" / "final_demo_corpus.json"
        )
        self.assertIsNotNone(system)
        self.assertIsNotNone(single_agent)
        self.assertIsNotNone(rag)
        self.assertEqual(len(corpus.all_papers()), 6)
        self.assertFalse(uploaded_papers)
        self.assertFalse(upload_errors)

    def test_load_systems_merges_uploaded_paper(self) -> None:
        upload = SimpleNamespace(
            name="my_ai_paper.md",
            getvalue=lambda: (
                "title: Upload Test Paper\n"
                "year: 2026\n"
                "authors: A. Student\n"
                "topics: ai, verification\n\n"
                "Abstract: This uploaded paper evaluates claim verification in AI systems.\n"
            ).encode("utf-8"),
        )
        system, single_agent, rag, corpus, uploaded_papers, upload_errors = load_systems(
            ROOT / "data" / "final_demo_corpus.json",
            uploaded_files=[upload],
        )
        self.assertIsNotNone(system)
        self.assertIsNotNone(single_agent)
        self.assertIsNotNone(rag)
        self.assertEqual(len(uploaded_papers), 1)
        self.assertFalse(upload_errors)
        self.assertEqual(len(corpus.all_papers()), 7)


if __name__ == "__main__":
    unittest.main()
