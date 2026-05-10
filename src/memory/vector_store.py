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

    def __init__(
        self,
        persist_directory: str,
        embedding_model: str,
        embedding_provider: str = "ollama",
        openai_api_key: str | None = None,
    ):
        """
        Initialize the vector store.

        Parameters
        ----------
        persist_directory : str
            Directory where the vector database will be stored.

        embedding_model : str
            Name of the embedding model used for generating embeddings.

        embedding_provider : str
            Provider used for embeddings. Supported values: ollama, openai.

        openai_api_key : str | None
            API key used when embedding_provider is openai.
        """

        self.persist_directory = persist_directory
        self.embedding_provider = embedding_provider.lower()
        self.embedding_model = embedding_model

        if self.embedding_provider == "ollama":
            self.embedding_function = embedding_functions.OllamaEmbeddingFunction(
                model_name=embedding_model
            )
        elif self.embedding_provider == "openai":
            if not openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required when embedding provider is openai."
                )
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name=embedding_model,
            )
        else:
            raise ValueError(
                f"Unsupported embedding provider: {embedding_provider}. "
                "Use 'ollama' or 'openai'."
            )

        # Client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Keep provider/model collections separate to avoid embedding dimension
        # conflicts when switching between Ollama and OpenAI.
        safe_model = (
            embedding_model.replace(":", "_")
            .replace("-", "_")
            .replace(".", "_")
            .lower()
        )
        self.collection_name = f"documents_{self.embedding_provider}_{safe_model}"

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

    def query_with_sources(self, query_text: str, n_results: int = 4):
        """
        Retrieve relevant chunks with source metadata for grounded answers.

        Returns
        -------
        list[dict]
            Each item contains text, source, chunk index, and distance.
        """

        query_text = query_text.lower()

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

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
