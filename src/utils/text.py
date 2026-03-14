"""Text processing utilities."""
import re
from typing import Optional


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\w\s\-.,;:'\"()\[\]]", "", text)
    return text.strip()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_doi(text: str) -> Optional[str]:
    """Extract DOI from text."""
    patterns = [
        r"10\.\d{4,}/[^\s]+",
        r"doi[:\s]+10\.\d{4,}/[^\s]+",
        r"https?://doi\.org/(10\.\d{4,}/[^\s]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(1) if match.lastindex else match.group(0)
            return doi.strip(".,;:)")

    return None


def extract_email(text: str) -> Optional[str]:
    """Extract email from text."""
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def normalize_authors(authors: list[str]) -> list[str]:
    """Normalize author names."""
    normalized = []
    for author in authors:
        # Remove extra whitespace
        author = " ".join(author.split())
        # Capitalize properly
        parts = author.split()
        normalized_parts = []
        for part in parts:
            if part.lower() in ("jr", "sr", "iii", "ii", "iv", "phd", "md"):
                normalized_parts.append(part.lower())
            else:
                normalized_parts.append(part.capitalize())
        normalized.append(" ".join(normalized_parts))
    return normalized


def format_author_list(authors: list[str], style: str = "apa") -> str:
    """Format author list for citation."""
    if not authors:
        return ""

    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return f"{authors[0]} & {authors[1]}"
    elif len(authors) <= 7:
        last = authors.pop()
        return f"{', '.join(authors)}, & {last}"
    else:
        # More than 7 authors - use et al.
        return f"{authors[0]} et al."


def parse_year(date_string: str) -> Optional[int]:
    """Extract year from various date formats."""
    # Try common formats
    patterns = [
        r"(\d{4})",  # YYYY
        r"(\d{4})-\d{2}-\d{2}",  # YYYY-MM-DD
        r"(\d{2})-(\d{4})",  # MM-YYYY
    ]

    for pattern in patterns:
        match = re.search(pattern, date_string)
        if match:
            year = int(match.group(1))
            if 1900 <= year <= 2030:
                return year

    return None


def count_words(text: str) -> int:
    """Count words in text."""
    return len(re.findall(r"\b\w+\b", text))


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract keywords from text using simple frequency."""
    # Remove stopwords
    stopwords = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "this",
        "that", "these", "those", "it", "its", "they", "them", "their",
    }

    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    freq = {}
    for word in words:
        if word not in stopwords:
            freq[word] = freq.get(word, 0) + 1

    # Sort by frequency
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]
