"""Export API routes for citation formats."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


router = APIRouter()


class ExportRequest(BaseModel):
    """Export request model."""

    papers: list[dict]
    format: str = "bibtex"


@router.post("/bibtex", response_model=dict)
async def export_bibtex(request: ExportRequest):
    """Export papers to BibTeX format."""
    bibtex_entries = []

    for paper in request.papers:
        # Generate citation key
        first_author = paper.get("authors", ["Unknown"])[0].split()[-1] if paper.get("authors") else "Unknown"
        year = paper.get("year", "0000")
        title_words = paper.get("title", "").split()[:3]
        key = f"{first_author}{year}{''.join(title_words)}"

        # Build BibTeX entry
        entry = f"""@article{{{key},
  author = {{{' and '.join(paper.get('authors', []))}}},
  title = {{{paper.get('title', '')}}},
  journal = {{{paper.get('journal', '')}}},
  year = {{{year}}},
"""
        if paper.get("doi"):
            entry += f"  doi = {{{paper.get('doi')}}},\n"
        if paper.get("volume"):
            entry += f"  volume = {{{paper.get('volume')}}},\n"
        if paper.get("issue"):
            entry += f"  number = {{{paper.get('issue')}}},\n"
        if paper.get("pages"):
            entry += f"  pages = {{{paper.get('pages')}}},\n"

        entry += "}"
        bibtex_entries.append(entry)

    return {
        "success": True,
        "data": {
            "format": "bibtex",
            "content": "\n\n".join(bibtex_entries),
        },
    }


@router.post("/ris", response_model=dict)
async def export_ris(request: ExportRequest):
    """Export papers to RIS format."""
    ris_entries = []

    for paper in request.papers:
        lines = []
        lines.append("TY  - JOUR")
        lines.append("TI  - " + paper.get("title", ""))

        for author in paper.get("authors", []):
            lines.append(f"AU  - {author}")

        lines.append("PY  - " + str(paper.get("year", "")))
        lines.append("JO  - " + paper.get("journal", ""))

        if paper.get("doi"):
            lines.append("DO  - " + paper.get("doi"))
        if paper.get("volume"):
            lines.append("VL  - " + paper.get("volume"))
        if paper.get("issue"):
            lines.append("IS  - " + paper.get("issue"))
        if paper.get("pages"):
            lines.append("SP  - " + paper.get("pages"))

        lines.append("ER  - ")
        ris_entries.append("\n".join(lines))

    return {
        "success": True,
        "data": {
            "format": "ris",
            "content": "\n\n".join(ris_entries),
        },
    }


@router.post("/csv", response_model=dict)
async def export_csv(request: ExportRequest):
    """Export papers to CSV format."""
    import csv
    import io

    if not request.papers:
        return {
            "success": True,
            "data": {
                "format": "csv",
                "content": "",
            },
        }

    output = io.StringIO()
    fieldnames = ["title", "authors", "year", "journal", "doi", "abstract"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for paper in request.papers:
        writer.writerow({
            "title": paper.get("title", ""),
            "authors": "; ".join(paper.get("authors", [])),
            "year": paper.get("year", ""),
            "journal": paper.get("journal", ""),
            "doi": paper.get("doi", ""),
            "abstract": paper.get("abstract", ""),
        })

    return {
        "success": True,
        "data": {
            "format": "csv",
            "content": output.getvalue(),
        },
    }
