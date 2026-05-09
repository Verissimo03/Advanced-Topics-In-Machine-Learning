"""
Document Loader Module

This module loads documents of different formats and converts them
into raw text that can be processed by the RAG pipeline.
"""

from pathlib import Path
from pypdf import PdfReader
import docx


class DocumentLoader:
    """
    Loads documents from different file formats.
    """

    def load(self, file_path: str) -> str:
        """
        Load a document and return its text content.

        Parameters
        ----------
        file_path : str
            Path to the document.

        Returns
        -------
        str
            Extracted text from the document.
        """

        extension = Path(file_path).suffix.lower()

        if extension in [".txt", ".md"]:
            return self._load_text(file_path)

        elif extension == ".pdf":
            return self._load_pdf(file_path)

        elif extension == ".docx":
            return self._load_docx(file_path)

        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _load_text(self, file_path: str) -> str:
        """Load TXT or Markdown files."""

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""

        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    def _load_docx(self, file_path: str) -> str:
        """Extract text from DOCX."""

        document = docx.Document(file_path)

        text = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)

        return "\n".join(text)