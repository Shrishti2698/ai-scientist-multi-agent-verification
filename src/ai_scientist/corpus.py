from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ai_scientist.models import BenchmarkCase, PaperDocument


class CorpusRepository:
    def __init__(self, papers: list[PaperDocument]):
        self._papers = papers
        self._paper_index = {paper.paper_id: paper for paper in papers}

    @classmethod
    def from_path(cls, path: str | Path) -> "CorpusRepository":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        papers = [PaperDocument(**paper) for paper in payload["papers"]]
        return cls(papers)

    def all_papers(self) -> list[PaperDocument]:
        return list(self._papers)

    def get(self, paper_id: str) -> PaperDocument:
        return self._paper_index[paper_id]

    def to_dict(self) -> list[dict]:
        return [asdict(paper) for paper in self._papers]


def load_benchmark_cases(path: str | Path) -> list[BenchmarkCase]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [BenchmarkCase(**item) for item in payload["benchmark_cases"]]

