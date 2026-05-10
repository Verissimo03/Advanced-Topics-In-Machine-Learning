"""
Legal-document-aware text chunking.

The chunker tries to keep legal sections and clause headings together before
falling back to overlapping character chunks for long sections.
"""

from __future__ import annotations

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


SECTION_HEADING_RE = re.compile(
    r"""
    ^\s*(
        \#{1,6}\s+.+ |
        (?:clause|section|article)\s+\d+[\.:)]?\s+.+ |
        \d+(?:\.\d+)*[\.:)]\s+.+ |
        [A-Z][A-Za-z /&,-]{2,80}
    )\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


KNOWN_LEGAL_HEADINGS = {
    "parties",
    "scope",
    "scope of services",
    "services",
    "payment terms",
    "fees",
    "term and termination",
    "termination",
    "confidentiality",
    "data protection",
    "gdpr",
    "liability",
    "limitation of liability",
    "governing law",
    "jurisdiction",
    "intellectual property",
    "client responsibilities",
    "supplier responsibilities",
}


class TextChunker:
    """
    Splits legal and business documents into section-preserving chunks.
    """

    def __init__(self, chunk_size: int = 450, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "; ", ", ", " "],
        )

    def split(self, text: str):
        """
        Return chunk texts only.

        Kept for compatibility with existing tests and callers.
        """

        return [chunk["text"] for chunk in self.split_with_metadata(text)]

    def split_with_metadata(self, text: str):
        """
        Split text into chunks with section metadata.

        Returns
        -------
        list[dict]
            Each dict contains text, section_title, section_index,
            chunk_in_section, and chunk_chars.
        """

        sections = self._split_into_sections(text)
        chunks = []

        for section_index, section in enumerate(sections, start=1):
            section_text = section["text"].strip()
            if not section_text:
                continue

            if len(section_text) <= self.chunk_size:
                section_chunks = [section_text]
            else:
                section_chunks = self.splitter.split_text(section_text)

            for chunk_index, chunk_text in enumerate(section_chunks, start=1):
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue

                chunks.append({
                    "text": chunk_text,
                    "section_title": section["title"],
                    "section_index": section_index,
                    "chunk_in_section": chunk_index,
                    "chunk_chars": len(chunk_text),
                })

        return chunks

    def _split_into_sections(self, text: str):
        """Split text by detected headings while keeping headings with content."""

        normalized = self._normalize_text(text)
        blocks = [block.strip() for block in re.split(r"\n\s*\n", normalized) if block.strip()]

        sections = []
        current_title = "Document start"
        current_parts = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            first_line = lines[0]
            if self._looks_like_heading(first_line):
                if current_parts:
                    sections.append({
                        "title": current_title,
                        "text": "\n\n".join(current_parts),
                    })

                current_title = self._clean_heading(first_line)
                current_parts = [block]
            else:
                current_parts.append(block)

        if current_parts:
            sections.append({
                "title": current_title,
                "text": "\n\n".join(current_parts),
            })

        if not sections and normalized.strip():
            sections.append({
                "title": "Document",
                "text": normalized.strip(),
            })

        return sections

    def _looks_like_heading(self, line: str) -> bool:
        """Detect common legal/contract section headings."""

        cleaned = self._clean_heading(line)
        if cleaned.lower() in KNOWN_LEGAL_HEADINGS:
            return True

        if len(cleaned.split()) > 10:
            return False

        return bool(SECTION_HEADING_RE.match(line))

    @staticmethod
    def _clean_heading(line: str) -> str:
        """Normalize heading text for metadata."""

        cleaned = re.sub(r"^\s*\#{1,6}\s+", "", line.strip())
        cleaned = re.sub(r"^\s*(?:clause|section|article)\s+", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"^\s*\d+(?:\.\d+)*[\.:)]\s*", "", cleaned)
        return cleaned.strip(" :-")

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize line endings and whitespace while preserving paragraphs."""

        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
