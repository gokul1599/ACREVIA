"""
ACREVIA - KrishiBrain Multi-Format Document Extractors.
Extracts structured text while preserving page numbers and heading hierarchies.
"""

import io
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from pypdf import PdfReader
import docx


class ExtractedSection:
    def __init__(
        self,
        text: str,
        page_num: Optional[int] = None,
        heading: Optional[str] = None,
        parent_heading: Optional[str] = None
    ):
        self.text = text.strip()
        self.page_num = page_num
        self.heading = heading
        self.parent_heading = parent_heading

    @property
    def heading_path(self) -> str:
        if self.parent_heading and self.heading:
            return f"{self.parent_heading} > {self.heading}"
        return self.heading or self.parent_heading or "General"


class DocumentExtractor:
    @staticmethod
    def extract(content: bytes, filename: str, doc_type: Optional[str] = None) -> List[ExtractedSection]:
        dtype = (doc_type or filename.split(".")[-1]).upper()

        if dtype == "PDF":
            return DocumentExtractor._extract_pdf(content)
        elif dtype in ["DOCX", "DOC"]:
            return DocumentExtractor._extract_docx(content)
        elif dtype in ["HTML", "HTM"]:
            return DocumentExtractor._extract_html(content)
        elif dtype in ["MD", "MARKDOWN"]:
            return DocumentExtractor._extract_markdown(content)
        else:
            return DocumentExtractor._extract_plain_text(content)

    @staticmethod
    def _extract_pdf(content: bytes) -> List[ExtractedSection]:
        sections: List[ExtractedSection] = []
        reader = PdfReader(io.BytesIO(content))

        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            if not lines:
                continue

            current_heading = "General"
            buffer: List[str] = []

            for line in lines:
                # Basic heading detection: short lines, all uppercase or numbered sections
                if len(line) < 80 and (line.isupper() or re.match(r"^\d+(\.\d+)*\s+[A-Z]", line)):
                    if buffer:
                        sections.append(ExtractedSection(
                            text=" ".join(buffer),
                            page_num=idx,
                            heading=current_heading
                        ))
                        buffer = []
                    current_heading = line
                else:
                    buffer.append(line)

            if buffer:
                sections.append(ExtractedSection(
                    text=" ".join(buffer),
                    page_num=idx,
                    heading=current_heading
                ))

        return sections

    @staticmethod
    def _extract_docx(content: bytes) -> List[ExtractedSection]:
        sections: List[ExtractedSection] = []
        doc = docx.Document(io.BytesIO(content))

        current_heading = "General"
        buffer: List[str] = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            if para.style.name.startswith("Heading"):
                if buffer:
                    sections.append(ExtractedSection(
                        text=" ".join(buffer),
                        heading=current_heading
                    ))
                    buffer = []
                current_heading = text
            else:
                buffer.append(text)

        if buffer:
            sections.append(ExtractedSection(
                text=" ".join(buffer),
                heading=current_heading
            ))

        return sections

    @staticmethod
    def _extract_html(content: bytes) -> List[ExtractedSection]:
        sections: List[ExtractedSection] = []
        soup = BeautifulSoup(content.decode("utf-8", errors="replace"), "lxml")

        # Strip scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        current_heading = "General"
        buffer: List[str] = []

        for elem in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
            text = elem.get_text().strip()
            if not text:
                continue

            if elem.name in ["h1", "h2", "h3", "h4"]:
                if buffer:
                    sections.append(ExtractedSection(
                        text=" ".join(buffer),
                        heading=current_heading
                    ))
                    buffer = []
                current_heading = text
            else:
                buffer.append(text)

        if buffer:
            sections.append(ExtractedSection(
                text=" ".join(buffer),
                heading=current_heading
            ))

        return sections

    @staticmethod
    def _extract_markdown(content: bytes) -> List[ExtractedSection]:
        sections: List[ExtractedSection] = []
        text = content.decode("utf-8", errors="replace")
        lines = text.split("\n")

        current_heading = "General"
        buffer: List[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("#"):
                if buffer:
                    sections.append(ExtractedSection(
                        text=" ".join(buffer),
                        heading=current_heading
                    ))
                    buffer = []
                current_heading = stripped.lstrip("#").strip()
            else:
                buffer.append(stripped)

        if buffer:
            sections.append(ExtractedSection(
                text=" ".join(buffer),
                heading=current_heading
            ))

        return sections

    @staticmethod
    def _extract_plain_text(content: bytes) -> List[ExtractedSection]:
        text = content.decode("utf-8", errors="replace").strip()
        if not text:
            return []
        return [ExtractedSection(text=text, heading="General")]
