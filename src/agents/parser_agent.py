"""Parser agent for PDF extraction and structured data mining."""
import re
from typing import Optional
from ..models.paper import ParsedPaperData


class ParserAgent:
    """Agent for parsing academic papers and extracting structured data."""

    def __init__(self):
        self.section_patterns = {
            "introduction": r"(?:^|\n)(?: INTRODUCTION|1\.\s*Introduction|背景|引言)",
            "method": r"(?:^|\n)(?: METHOD|2\.\s*Method|方法|METHODS|研究方法)",
            "result": r"(?:^|\n)(?: RESULT|3\.\s*Result|结果|RESULTS|研究发现)",
            "discussion": r"(?:^|\n)(?: DISCUSSION|4\.\s*Discussion|讨论|DISCUSSION)",
            "conclusion": r"(?:^|\n)(?: CONCLUSION|5\.\s*Conclusion|结论|CONCLUSIONS)",
        }

    async def parse(
        self,
        paper_id: Optional[str] = None,
        pdf_url: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> dict:
        """Parse a paper and extract structured data."""
        # Download PDF if URL provided
        pdf_content = None
        if pdf_url:
            pdf_content = await self._download_pdf(pdf_url)

        if not pdf_content and not pdf_url:
            raise ValueError("Either paper_id or pdf_url must be provided")

        # Extract text from PDF
        text = await self._extract_text(pdf_content or pdf_url)

        # Analyze structure
        sections = self._analyze_structure(text)

        # Extract fields
        parsed = await self._extract_fields(sections, text)

        # Generate matrix
        matrix = self._generate_matrix(parsed)

        return {
            "paper_id": paper_id,
            "parsed_data": parsed.model_dump(),
            "matrix": matrix,
            "sections": sections,
        }

    async def _download_pdf(self, url: str) -> bytes:
        """Download PDF from URL."""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.content

    async def _extract_text(self, pdf_content: bytes | str) -> str:
        """Extract text from PDF."""
        import fitz  # PyMuPDF

        if isinstance(pdf_content, str):
            # It's a URL or file path
            if pdf_content.startswith("http"):
                pdf_content = await self._download_pdf(pdf_content)
            else:
                with open(pdf_content, "rb") as f:
                    pdf_content = f.read()

        doc = fitz.open(stream=pdf_content, doc_type="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return text

    def _analyze_structure(self, text: str) -> dict[str, str]:
        """Analyze document structure and identify sections."""
        sections = {}
        text_lower = text.lower()

        # Find section boundaries
        positions = []
        for section_name, pattern in self.section_patterns.items():
            match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            if match:
                positions.append((section_name, match.start()))

        # Sort by position
        positions.sort(key=lambda x: x[1])

        # Extract sections
        for i, (section_name, start) in enumerate(positions):
            end = positions[i + 1][1] if i + 1 < len(positions) else len(text)
            sections[section_name] = text[start:end]

        return sections

    async def _extract_fields(self, sections: dict[str, str], full_text: str) -> ParsedPaperData:
        """Extract structured fields from paper sections."""
        from ..services.llm import LLMService

        llm = LLMService()

        # Extract method section for research type
        method_text = sections.get("method", "")[:3000]
        result_text = sections.get("result", "")[:3000]

        # Use LLM to extract structured data
        prompt = f"""Extract structured research data from this academic paper. Return JSON:

{{
    "research_type": "横断面/纵向/荟萃分析/实验/综述/其他",
    "independent_vars": ["list of independent variables"],
    "dependent_vars": ["list of dependent variables"],
    "mediating_vars": ["list of mediating variables if any"],
    "moderating_vars": ["list of moderating variables if any"],
    "sample_size": number or null,
    "subjects": ["study population"],
    "instruments": [{{"name": "scale name", "items": number, "alpha": number}}],
    "key_findings": "2-3 sentence summary of main findings",
    "limitations": ["list of limitations"],
    "future_directions": ["future research suggestions"]
}}

Method section:
{method_text}

Result section:
{result_text}

Return JSON only."""

        result = await llm.generate(prompt, response_format={"type": "json_object"})

        import json

        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            parsed = {}

        # Extract statistical values
        stat_values = self._extract_statistics(full_text)

        return ParsedPaperData(
            research_type=parsed.get("research_type"),
            independent_vars=parsed.get("independent_vars", []),
            dependent_vars=parsed.get("dependent_vars", []),
            mediating_vars=parsed.get("mediating_vars", []),
            moderating_vars=parsed.get("moderating_vars", []),
            sample_size=parsed.get("sample_size"),
            subjects=parsed.get("subjects", []),
            instruments=parsed.get("instruments", []),
            key_findings=parsed.get("key_findings"),
            limitations=parsed.get("limitations", []),
            future_directions=parsed.get("future_directions", []),
            statistical_values=stat_values,
            raw_json=parsed,
        )

    def _extract_statistics(self, text: str) -> list[dict[str, str]]:
        """Extract statistical values using regex."""
        import re

        stats = []

        # Common patterns
        patterns = [
            (r"r\s*=\s*([-\d.]+)", "r"),
            (r"r²\s*=\s*([-\d.]+)", "r²"),
            (r"d\s*=\s*([-\d.]+)", "d"),
            (r"F\(?\s*[\d.,]+\)?\s*=\s*([-\d.]+)", "F"),
            (r"t\(?\s*[\d.]+\)?\s*=\s*([-\d.]+)", "t"),
            (r"p\s*[=<>]\s*([.\d]+)", "p"),
            (r"χ²\s*=\s*([-\d.]+)", "χ²"),
        ]

        for pattern, stat_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:5]:  # Limit to 5 per type
                stats.append({"type": stat_type, "value": match})

        return stats

    def _generate_matrix(self, parsed: ParsedPaperData) -> dict:
        """Generate matrix data for comparison."""
        return {
            "research_type": parsed.research_type,
            "iv": parsed.independent_vars,
            "dv": parsed.dependent_vars,
            "mediators": parsed.mediating_vars,
            "moderators": parsed.moderating_vars,
            "sample_size": parsed.sample_size,
            "subjects": parsed.subjects,
            "instruments": [
                f"{inst.get('name', '')} ({inst.get('items', '?')} items, α={inst.get('alpha', '?')})"
                for inst in parsed.instruments
            ],
            "key_findings": parsed.key_findings,
        }
