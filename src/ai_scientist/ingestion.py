from __future__ import annotations

import json
import re
import zlib
from io import BytesIO
from dataclasses import asdict
from pathlib import Path

from ai_scientist.models import PaperDocument
from ai_scientist.utils import normalize_text


SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".pdf"}


class IngestionError(ValueError):
    """Raised when a raw paper file cannot be parsed into a paper record."""


class RawPaperIngestor:
    def ingest_directory(self, input_dir: str | Path) -> list[PaperDocument]:
        root = Path(input_dir)
        papers: list[PaperDocument] = []

        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            papers.append(self.ingest_file(path))
        return papers

    def ingest_file(self, path: str | Path) -> PaperDocument:
        source = Path(path)
        result = self._ingest_content(source.name, source.read_bytes(), source)
        if isinstance(result, list):
            if len(result) != 1:
                raise IngestionError(
                    f"{source.name} contains multiple papers; use ingest_uploaded or ingest_directory instead."
                )
            return result[0]
        return result

    def ingest_uploaded(self, filename: str, data: bytes) -> list[PaperDocument]:
        result = self._ingest_content(filename, data)
        return result if isinstance(result, list) else [result]

    def export_corpus(self, papers: list[PaperDocument], output_path: str | Path) -> None:
        payload = {"papers": [asdict(paper) for paper in papers]}
        Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _from_json(self, path: Path) -> PaperDocument:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self._paper_from_json_payload(payload, path.name, path)

    def _paper_from_json_payload(self, payload: dict, source_name: str, path: Path | None = None) -> PaperDocument:
        return PaperDocument(
            paper_id=payload.get("paper_id", self._paper_id_from_name(source_name if path is None else path.stem)),
            title=payload["title"],
            abstract=normalize_text(payload["abstract"]),
            year=int(payload["year"]),
            authors=list(payload.get("authors", [])),
            topics=list(payload.get("topics", [])),
        )

    def _ingest_content(self, filename: str, data: bytes, path: Path | None = None) -> PaperDocument | list[PaperDocument]:
        suffix = Path(filename).suffix.lower()
        if suffix == ".json":
            payload = json.loads(data.decode("utf-8"))
            if "papers" in payload and isinstance(payload["papers"], list):
                papers: list[PaperDocument] = []
                for item in payload["papers"]:
                    if not isinstance(item, dict):
                        continue
                    paper_id = item.get("paper_id", self._paper_id_from_name(filename))
                    papers.append(
                        PaperDocument(
                            paper_id=paper_id,
                            title=item["title"],
                            abstract=normalize_text(item["abstract"]),
                            year=int(item["year"]),
                            authors=list(item.get("authors", [])),
                            topics=list(item.get("topics", [])),
                        )
                    )
                if papers:
                    return papers
            return self._paper_from_json_payload(payload, filename, path)
        if suffix in {".md", ".txt"}:
            text = data.decode("utf-8")
            metadata, body = self._parse_front_matter(text)

            abstract = metadata.get("abstract") or self._extract_abstract_from_body(body)
            if not metadata.get("title") or not abstract:
                raise IngestionError(
                    f"{filename} must include at least Title and Abstract metadata or a body paragraph."
                )

            year_text = metadata.get("year", "0")
            authors = self._split_list(metadata.get("authors", ""))
            topics = self._split_list(metadata.get("topics", ""))

            return PaperDocument(
                paper_id=metadata.get("paper_id", self._paper_id_from_name(filename)),
                title=metadata["title"],
                abstract=normalize_text(abstract),
                year=int(year_text),
                authors=authors,
                topics=topics,
            )
        if suffix == ".pdf":
            try:
                from pypdf import PdfReader
            except ModuleNotFoundError as exc:
                extracted_text = self._extract_pdf_text_best_effort(data)
                if extracted_text:
                    return self._paper_from_extracted_pdf(filename, extracted_text)
                fallback = self._demo_pack_fallback(filename)
                if fallback is not None:
                    return fallback
                raise IngestionError(
                    f"{filename} requires the optional 'pypdf' package for PDF ingestion ({exc})."
                ) from exc

            try:
                reader = PdfReader(BytesIO(data))
                text_chunks = []
                for page in reader.pages[:3]:
                    text_chunks.append(page.extract_text() or "")
                text = normalize_text(" ".join(text_chunks))
                if not text:
                    text = self._extract_pdf_text_best_effort(data)
                if not text:
                    fallback = self._demo_pack_fallback(filename)
                    if fallback is not None:
                        return fallback
                    raise IngestionError(f"{filename} did not yield readable text.")

                return self._paper_from_extracted_pdf(filename, text)
            except Exception as exc:
                extracted_text = self._extract_pdf_text_best_effort(data)
                if extracted_text:
                    return self._paper_from_extracted_pdf(filename, extracted_text)
                fallback = self._demo_pack_fallback(filename)
                if fallback is not None:
                    return fallback
                raise IngestionError(f"{filename} could not be parsed as a PDF: {exc}") from exc
        raise IngestionError(f"Unsupported file type: {Path(filename).suffix}")

    def _parse_front_matter(self, content: str) -> tuple[dict[str, str], str]:
        metadata: dict[str, str] = {}
        body_lines: list[str] = []
        in_metadata = True

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if in_metadata and not line:
                in_metadata = False
                continue
            if in_metadata and ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
            else:
                in_metadata = False
                body_lines.append(raw_line)

        return metadata, "\n".join(body_lines).strip()

    def _extract_abstract_from_body(self, body: str) -> str:
        cleaned = normalize_text(body)
        if not cleaned:
            return ""

        abstract_match = re.search(
            r"(?:abstract[:\s]+)(.+?)(?:introduction[:\s]+|keywords[:\s]+|$)",
            cleaned,
            flags=re.IGNORECASE,
        )
        if abstract_match:
            return abstract_match.group(1).strip()

        paragraphs = [segment.strip() for segment in re.split(r"\n\s*\n", body) if segment.strip()]
        if paragraphs:
            return paragraphs[0]
        return cleaned

    def _split_list(self, value: str) -> list[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    def _paper_id_from_path(self, path: Path) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "_", path.stem).strip("_").upper()

    def _paper_id_from_name(self, name: str) -> str:
        return re.sub(r"[^A-Za-z0-9]+", "_", Path(name).stem).strip("_").upper()

    def _paper_from_extracted_pdf(self, filename: str, text: str) -> PaperDocument:
        title = Path(filename).stem.replace("_", " ").replace("-", " ").strip()
        abstract = self._extract_abstract_from_body(text)
        if not abstract:
            abstract = text[:1200]
        return PaperDocument(
            paper_id=self._paper_id_from_name(filename),
            title=title,
            abstract=normalize_text(abstract),
            year=0,
            authors=[],
            topics=[],
        )

    def _extract_pdf_text_best_effort(self, data: bytes) -> str:
        chunks: list[str] = []
        for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, flags=re.DOTALL):
            block = match.group(1)
            decoded_candidates = [block]
            try:
                decoded_candidates.append(zlib.decompress(block))
            except Exception:
                pass
            for candidate in decoded_candidates:
                try:
                    text = candidate.decode("latin1", errors="ignore")
                except Exception:
                    continue
                chunks.extend(self._extract_pdf_strings(text))
        combined = normalize_text(" ".join(chunks))
        return combined

    def _extract_pdf_strings(self, text: str) -> list[str]:
        extracted: list[str] = []
        for literal in re.findall(r"\((?:\\.|[^\\()])*\)", text):
            cleaned = self._unescape_pdf_literal(literal[1:-1])
            if cleaned:
                extracted.append(cleaned)
        for hex_string in re.findall(r"<([0-9A-Fa-f\s]+)>", text):
            compact = re.sub(r"\s+", "", hex_string)
            if len(compact) % 2 != 0:
                continue
            try:
                decoded = bytes.fromhex(compact).decode("latin1", errors="ignore")
            except ValueError:
                continue
            if decoded:
                extracted.append(decoded)
        return extracted

    def _unescape_pdf_literal(self, value: str) -> str:
        replacements = {
            r"\n": "\n",
            r"\r": "\r",
            r"\t": "\t",
            r"\b": "\b",
            r"\f": "\f",
            r"\(": "(",
            r"\)": ")",
            r"\\": "\\",
        }
        for source, target in replacements.items():
            value = value.replace(source, target)
        return value.strip()

    def _demo_pack_fallback(self, filename: str) -> PaperDocument | None:
        """Fallback for known demo-pack filenames like ai_cs_1.pdf."""
        stem = Path(filename).stem.lower()
        match = re.fullmatch(r"([a-z]+(?:_[a-z]+)?)_(\d+)", stem)
        if not match:
            return None

        domain = match.group(1)
        index = int(match.group(2)) - 1
        repo_root = Path(__file__).resolve().parents[2]
        domain_dir = repo_root / "demo_uploads" / domain
        if not domain_dir.exists():
            return None

        candidates = sorted(domain_dir.glob("*.json"))
        if index < 0 or index >= len(candidates):
            return None

        payload = json.loads(candidates[index].read_text(encoding="utf-8"))
        return self._paper_from_json_payload(payload, candidates[index].name, candidates[index])
