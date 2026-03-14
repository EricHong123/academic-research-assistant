"""Citation formatting utilities."""
from typing import Optional


def format_citation_apa(
    authors: list[str],
    year: int,
    title: str,
    journal: Optional[str] = None,
    volume: Optional[str] = None,
    issue: Optional[str] = None,
    pages: Optional[str] = None,
    doi: Optional[str] = None,
) -> str:
    """Format citation in APA style (7th edition)."""
    # Format authors
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    elif len(authors) <= 20:
        last_author = authors.pop()
        author_str = f"{', '.join(authors)}, & {last_author}"
    else:
        # More than 20 authors
        author_str = f"{', '.join(authors[:19])}, ... {authors[-1]}"

    # Build citation
    parts = [
        f"({year}). {title}.",
    ]

    if journal:
        parts.append(f"{journal}")

        if volume:
            parts.append(f"{volume}")
            if issue:
                parts[-1] += f"({issue})"

        if pages:
            parts[-1] += f", {pages}"

        parts[-1] += "."

    if doi:
        parts.append(f"https://doi.org/{doi}")

    return " ".join(parts)


def format_citation_mla(
    authors: list[str],
    year: int,
    title: str,
    journal: Optional[str] = None,
    volume: Optional[str] = None,
    issue: Optional[str] = None,
    pages: Optional[str] = None,
    doi: Optional[str] = None,
) -> str:
    """Format citation in MLA style (9th edition)."""
    # Format authors
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]}, and {authors[1]}"
    else:
        author_str = f"{authors[0]}, et al"

    # Build citation
    title_part = f'"{title}."' if not journal else f'"{title}."'

    parts = [
        f"{author_str}. {title_part}",
    ]

    if journal:
        journal_part = journal
        if volume:
            journal_part += f", vol. {volume}"
        if issue:
            journal_part += f", no. {issue}"
        journal_part += f", {year}"
        if pages:
            journal_part += f", pp. {pages}"
        parts.append(journal_part + ".")

    if doi:
        parts.append(f"doi:{doi}.")

    return " ".join(parts)


def format_citation_chicago(
    authors: list[str],
    year: int,
    title: str,
    journal: Optional[str] = None,
    volume: Optional[str] = None,
    issue: Optional[str] = None,
    pages: Optional[str] = None,
    doi: Optional[str] = None,
) -> str:
    """Format citation in Chicago style (17th edition)."""
    # Format authors
    if not authors:
        author_str = "Unknown Author"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} and {authors[1]}"
    elif len(authors) <= 10:
        last_author = authors.pop()
        author_str = f"{', '.join(authors)}, and {last_author}"
    else:
        author_str = f"{', '.join(authors[:7])}, et al"

    # Build citation
    parts = [
        f"{author_str}. \"{title}.\"",
    ]

    if journal:
        journal_part = journal
        if volume:
            journal_part += f" {volume}"
        if issue:
            journal_part += f", no. {issue}"
        journal_part += f" ({year})"
        if pages:
            journal_part += f": {pages}"
        parts.append(journal_part + ".")

    if doi:
        parts.append(f"https://doi.org/{doi}.")

    return " ".join(parts)


def parse_citation(citation: str, format: str = "auto") -> dict:
    """Parse a citation string into components."""
    # Simple parser - in production would use a library
    import re

    result = {
        "authors": [],
        "year": None,
        "title": "",
        "journal": None,
        "volume": None,
        "issue": None,
        "pages": None,
        "doi": None,
    }

    # Extract year
    year_match = re.search(r"\((\d{4})\)|(\d{4})", citation)
    if year_match:
        result["year"] = int(year_match.group(1) or year_match.group(2))

    # Extract DOI
    doi_match = re.search(r"10\.\d{4,}/[^\s]+", citation)
    if doi_match:
        result["doi"] = doi_match.group(0)

    return result
