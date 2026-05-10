"""
Vector store module.

This module manages the persistent vector database used for
document storage and retrieval in the RAG system.
"""

import chromadb
from chromadb.utils import embedding_functions


class VectorStore:
    """
    Wrapper around ChromaDB to manage persistent document embeddings.
    """

    def __init__(self, persist_directory: str, embedding_model: str):
        """
        Initialize the vector store.

        Parameters
        ----------
        persist_directory : str
            Directory where the vector database will be stored.

        embedding_model : str
            Name of the embedding model used for generating embeddings.
        """

        self.persist_directory = persist_directory

        # Embedding function
        self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
            model_name=embedding_model
        )

        # Client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Collection
        self.collection_name = "documents"

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )

    def add_documents(self, documents, ids, metadatas=None):
        """
        Add documents to the vector store.

        Parameters
        ----------
        documents : list[str]
            List of document text chunks.

        ids : list[str]
            Unique identifiers for each chunk.

        metadatas : list[dict] | None
            Optional source metadata for each chunk.
        """

        # overwrite existing documents with same ids
        try:
            self.collection.delete(ids=ids)
        except:
            pass

        add_kwargs = {
            "documents": documents,
            "ids": ids
        }

        if metadatas:
            add_kwargs["metadatas"] = metadatas

        self.collection.add(**add_kwargs)

    def delete_by_source(self, source: str):
        """Delete all chunks for a source file before re-indexing it."""

        try:
            self.collection.delete(where={"source": source})
        except Exception:
            pass

    def delete_uploaded_documents(self):
        """Delete all uploaded document chunks from the active collection."""

        try:
            self.collection.delete(where={"source_type": "uploaded"})
        except Exception:
            pass

    def get_source_chunks(self, source: str, limit: int | None = None):
        """
        Return chunks for one source ordered by their original chunk number.

        This is useful for summary-style questions, where the opening chunk
        often contains the contract title, parties, and introductory metadata
        even when semantic retrieval ranks later clauses higher.
        """

        if not source:
            return []

        results = self.collection.get(
            where={"source": source},
            include=["documents", "metadatas"],
        )

        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        chunks = []
        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) and metadatas[index] else {}
            chunks.append({
                "text": document,
                "source": metadata.get("source", source),
                "source_type": metadata.get("source_type", "uploaded"),
                "source_type_label": "Legal knowledge base"
                if metadata.get("source_type") == "knowledge_base"
                else "Uploaded document",
                "chunk": metadata.get("chunk", index + 1),
                "section_title": metadata.get("section_title", ""),
                "distance": None,
            })

        chunks.sort(key=lambda item: item.get("chunk", 0))
        return chunks[:limit] if limit else chunks

    def query(self, query_text: str, n_results: int = 3):
        """
        Retrieve relevant documents from the vector store.

        Parameters
        ----------
        query_text : str
            User query.

        n_results : int
            Number of results to retrieve.

        Returns
        -------
        list[str]
            List of retrieved document chunks.
        """

        query_text = query_text.lower()

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        documents = results.get("documents", [])

        if not documents or not documents[0]:
            return []

        return documents[0]  # return list[str]

    def query_with_sources(
        self,
        query_text: str,
        n_results: int = 4,
        source_filter: list[str] | None = None,
    ):
        """
        Retrieve relevant chunks with source metadata for grounded answers.

        Returns
        -------
        list[dict]
            Each item contains text, source, chunk index, and distance.
        """

        query_text = query_text.lower()
        where_filter = None

        if source_filter is not None:
            clean_sources = [source for source in source_filter if source]
            if not clean_sources:
                return []
            where_filter = (
                {"source": clean_sources[0]}
                if len(clean_sources) == 1
                else {"source": {"$in": clean_sources}}
            )

        query_kwargs = {
            "query_texts": [query_text],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }

        if where_filter:
            query_kwargs["where"] = where_filter

        results = self.collection.query(**query_kwargs)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved = []
        for i, document in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
            distance = distances[i] if i < len(distances) else None

            retrieved.append({
                "text": document,
                "source": metadata.get("source", "Uploaded document"),
                "source_type": metadata.get("source_type", "uploaded"),
                "source_type_label": "Legal knowledge base"
                if metadata.get("source_type") == "knowledge_base"
                else "Uploaded document",
                "chunk": metadata.get("chunk", i + 1),
                "section_title": metadata.get("section_title", ""),
                "distance": distance
            })

        return retrieved
