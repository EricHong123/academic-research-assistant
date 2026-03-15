"""PDF parsing service with MinerU support."""
import os
import httpx
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from ..config import get_settings


class PDFParseResult:
    """Result of PDF parsing."""

    def __init__(
        self,
        title: str = "",
        authors: List[str] = None,
        abstract: str = "",
        year: int = None,
        journal: str = "",
        doi: str = "",
        sections: List[Dict[str, str]] = None,
        tables: List[Dict] = None,
        figures: List[Dict] = None,
        references: List[str] = None,
        raw_text: str = "",
        metadata: Dict = None,
    ):
        self.title = title
        self.authors = authors or []
        self.abstract = abstract
        self.year = year
        self.journal = journal
        self.doi = doi
        self.sections = sections or []
        self.tables = tables or []
        self.figures = figures or []
        self.references = references or []
        self.raw_text = raw_text
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "sections": self.sections,
            "tables": self.tables,
            "figures": self.figures,
            "references": self.references,
            "raw_text": self.raw_text,
            "metadata": self.metadata,
        }


class PDFParserService:
    """
    PDF Parser service with MinerU support.

    MinerU is specifically designed for academic PDFs and handles:
    - Double-column layouts correctly
    - Mathematical formulas
    - Tables and figures
    - Cross-column references

    Falls back to PyMuPDF if MinerU is unavailable.
    """

    def __init__(self, parser: str = None):
        settings = get_settings()
        self.parser = parser or settings.pdf_parser
        self.mineru_host = settings.mineru_host

    async def parse_pdf(self, pdf_path: str) -> PDFParseResult:
        """
        Parse a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFParseResult with extracted content
        """
        if self.parser == "mineru":
            try:
                return await self._parse_with_mineru(pdf_path)
            except Exception as e:
                print(f"MinerU parsing failed: {e}, falling back to PyMuPDF")
                return await self._parse_with_pymupdf(pdf_path)
        else:
            return await self._parse_with_pymupdf(pdf_path)

    async def _parse_with_mineru(self, pdf_path: str) -> PDFParseResult:
        """
        Parse PDF using MinerU API.

        MinerU provides much better extraction for academic papers,
        especially for double-column layouts.
        """
        # Read PDF file
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        # Send to MinerU service
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.mineru_host}/parse_pdf",
                files={"file": ("paper.pdf", pdf_content, "application/pdf")},
            )
            response.raise_for_status()
            data = response.json()

        # Parse MinerU response
        return self._parse_mineru_response(data)

    def _parse_mineru_response(self, data: dict) -> PDFParseResult:
        """Parse MinerU API response into PDFParseResult."""
        meta = data.get("metadata", {})
        content = data.get("content", [])

        # Extract sections
        sections = []
        raw_text_parts = []

        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                section_name = item.get("section", "body")
                sections.append({
                    "section": section_name,
                    "text": text,
                    "page": item.get("page", 0),
                })
                raw_text_parts.append(text)

        # Extract tables
        tables = []
        for item in content:
            if item.get("type") == "table":
                tables.append({
                    "page": item.get("page", 0),
                    "caption": item.get("caption", ""),
                    "data": item.get("data", []),
                })

        # Extract figures
        figures = []
        for item in content:
            if item.get("type") == "figure":
                figures.append({
                    "page": item.get("page", 0),
                    "caption": item.get("caption", ""),
                    "url": item.get("url", ""),
                })

        return PDFParseResult(
            title=meta.get("title", ""),
            authors=meta.get("authors", []),
            abstract=meta.get("abstract", ""),
            year=meta.get("year"),
            journal=meta.get("journal", ""),
            doi=meta.get("doi", ""),
            sections=sections,
            tables=tables,
            figures=figures,
            references=meta.get("references", []),
            raw_text="\n\n".join(raw_text_parts),
            metadata={
                "parser": "mineru",
                "language": meta.get("language", "en"),
            },
        )

    async def _parse_with_pymupdf(self, pdf_path: str) -> PDFParseResult:
        """
        Parse PDF using PyMuPDF (fallback).

        Note: This may have issues with double-column layouts.
        """
        try:
            import pymupdf
        except ImportError:
            raise ImportError("PyMuPDF not installed. Install with: pip install pymupdf")

        doc = pymupdf.open(pdf_path)

        # Extract metadata
        meta = doc.metadata

        # Extract text by pages
        sections = []
        raw_text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            raw_text_parts.append(text)

            # Try to detect section headers
            lines = text.split("\n")
            current_section = "body"
            for line in lines:
                line = line.strip()
                if line.lower() in ["abstract", "introduction", "methods", "methodology",
                                   "results", "discussion", "conclusion", "references"]:
                    current_section = line.lower()
                if line:
                    sections.append({
                        "section": current_section,
                        "text": line,
                        "page": page_num + 1,
                    })

        doc.close()

        return PDFParseResult(
            title=meta.get("title", ""),
            abstract=meta.get("subject", ""),
            doi=meta.get("doi", ""),
            sections=sections,
            raw_text="\n\n".join(raw_text_parts),
            metadata={
                "parser": "pymupdf",
                "page_count": len(doc) if hasattr(doc, '__len__') else 0,
            },
        )

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[str]:
        """
        Split text into chunks for RAG.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < text_length:
                for punct in [". ", "! ", "? ", "\n"]:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct > start:
                        end = last_punct + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks


# Singleton instance
_pdf_parser = None


def get_pdf_parser(parser: str = None) -> PDFParserService:
    """Get singleton PDF parser service."""
    global _pdf_parser
    if _pdf_parser is None:
        _pdf_parser = PDFParserService(parser)
    return _pdf_parser
