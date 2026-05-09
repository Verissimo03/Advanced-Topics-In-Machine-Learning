"""
Text Chunking Module

Splits large documents into smaller chunks suitable for embedding.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """
    Splits text into overlapping chunks.
    """

    def __init__(self, chunk_size: int = 150, chunk_overlap: int = 20):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split(self, text: str):
        """
        Split text into chunks.

        Parameters
        ----------
        text : str

        Returns
        -------
        list[str]
        """

        return self.splitter.split_text(text)