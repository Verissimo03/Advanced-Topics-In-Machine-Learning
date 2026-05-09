"""
Streamlit frontend for AI Legal Assistant for SMEs.

The app reuses the original RAG pipeline and adds legal-focused UX,
source grounding, safety notices, and human-review routing.
"""

import hashlib
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from src.ingestion.document_loader import DocumentLoader
from src.memory.conversation_history import ConversationHistory
from src.memory.vector_store import VectorStore
from src.models.llm import LLM
from src.utils.chunker import TextChunker
from src.utils.config_loader import load_config
from src.utils.legal_safety import requires_human_review, route_legal_service


config = load_config()

MODEL_NAME = config["model"]["name"]
TEMPERATURE = config["model"]["temperature"]
EMBEDDING_MODEL = config["embedding"]["model"]
CHUNK_SIZE = config["chunking"]["chunk_size"]
CHUNK_OVERLAP = config["chunking"]["chunk_overlap"]
VECTOR_STORE_PATH = config["vector_store"]["path"]
SYSTEM_PROMPT = config["prompts"]["system"]
LEGAL_DISCLAIMER = config["legal"]["disclaimer"]


st.set_page_config(
    page_title="AI Legal Assistant for SMEs",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def format_context(retrieved_items):
    """Build source-labelled context for the LLM."""

    formatted = []
    for index, item in enumerate(retrieved_items, start=1):
        formatted.append(
            f"Source [{index}] - {item['source']} | chunk {item['chunk']}:\n{item['text']}"
        )
    return formatted


def save_uploaded_file(uploaded_file):
    """Persist uploaded content in data/raw and return its path."""

    os.makedirs("data/raw", exist_ok=True)
    safe_name = os.path.basename(uploaded_file.name)
    file_path = os.path.join("data/raw", safe_name)

    with open(file_path, "wb") as file:
        file.write(uploaded_file.read())

    return file_path


st.markdown(
    """
# ⚖️ AI Legal Assistant for SMEs

Portugal/EU-focused legal triage and document-understanding assistant for small and medium-sized enterprises.
"""
)

st.info(LEGAL_DISCLAIMER)

st.markdown(
    """
Use this prototype to review contracts, explore GDPR obligations, identify missing clauses, prepare lawyer checklists, and decide when specialist legal support is needed.
"""
)


loader = DocumentLoader()
chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore(
        persist_directory=VECTOR_STORE_PATH,
        embedding_model=EMBEDDING_MODEL,
    )

vector_store = st.session_state.vector_store
llm = LLM(model_name=MODEL_NAME, system_prompt=SYSTEM_PROMPT, temperature=TEMPERATURE)
history_manager = ConversationHistory()


with st.sidebar:
    st.title("Legal Workspace")

    st.caption("Upload SME legal documents, templates, policies, or compliance notes.")
    uploaded_file = st.file_uploader(
        "Upload document",
        type=["txt", "pdf", "md", "docx"],
        help="Supported formats: TXT, Markdown, PDF, DOCX.",
    )

    st.markdown("---")
    st.subheader("Suggested workflows")
    st.markdown(
        """
- Contract summary
- Risky clause review
- GDPR checklist
- Employment-law triage
- Missing information scan
- Lawyer handoff checklist
"""
    )

    st.markdown("---")
    st.subheader("System")
    st.write(f"LLM: {MODEL_NAME}")
    st.write(f"Embeddings: {EMBEDDING_MODEL}")
    st.write("Vector DB: ChromaDB")
    st.write("Mode: Source-grounded RAG")

    st.markdown("---")
    chat_ids = history_manager.get_chat_ids()

    if not chat_ids:
        chat_ids = [history_manager.create_new_chat()]

    selected_chat = st.selectbox("Conversation", chat_ids)

    if st.button("New Chat"):
        st.session_state.chat_id = history_manager.create_new_chat()
        st.rerun()

    st.session_state.chat_id = selected_chat

    if st.button("Clear Current Chat"):
        chat_id = st.session_state.chat_id

        with open("data/chat_history.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            data = {}

        data[chat_id] = []

        with open("data/chat_history.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        st.success(f"{chat_id} cleared")
        st.rerun()

    if st.button("Delete Chat"):
        chat_id = st.session_state.chat_id

        with open("data/chat_history.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if chat_id in data:
            del data[chat_id]

        with open("data/chat_history.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        st.success(f"{chat_id} deleted")
        st.rerun()


if uploaded_file:
    if "last_file" not in st.session_state:
        st.session_state.last_file = None

    if uploaded_file.name != st.session_state.last_file:
        st.session_state.last_file = uploaded_file.name

        with st.spinner("Reading, chunking, embedding, and indexing the document..."):
            file_path = save_uploaded_file(uploaded_file)
            text = loader.load(file_path)
            chunks = chunker.split(text)

            file_hash = hashlib.sha256(uploaded_file.name.encode("utf-8")).hexdigest()[:10]
            ids = [f"{file_hash}_chunk_{index}" for index in range(len(chunks))]
            metadatas = [
                {
                    "source": uploaded_file.name,
                    "chunk": index + 1,
                    "document_type": os.path.splitext(uploaded_file.name)[1].lower(),
                }
                for index in range(len(chunks))
            ]

            vector_store.add_documents(documents=chunks, ids=ids, metadatas=metadatas)

        st.success(f"Document indexed successfully: {len(chunks)} chunks stored.")


st.markdown("## SME Legal Triage Chat")

example_questions = [
    "Can you summarize this contract in simple language?",
    "What are the main risks in this supplier agreement?",
    "Does this document mention GDPR obligations?",
    "What should I ask a lawyer before signing this?",
]

with st.expander("Example questions"):
    for question in example_questions:
        st.markdown(f"- {question}")


chat_id = st.session_state.chat_id
history = history_manager.load_history(chat_id)

for turn in history:
    with st.chat_message("user"):
        st.write(turn["question"])
    with st.chat_message("assistant"):
        st.write(turn["answer"])


query = st.chat_input("Ask about contracts, GDPR, employment, compliance, or legal risk...")

if query:
    with st.chat_message("user"):
        st.write(query)

    retrieved_items = vector_store.query_with_sources(query)
    context_items = format_context(retrieved_items)
    retrieved_text = "\n\n".join(item["text"] for item in retrieved_items)
    recommended_service = route_legal_service(query, retrieved_text)
    human_review_needed = requires_human_review(query, retrieved_text)

    if not retrieved_items:
        answer = (
            "I could not find enough relevant information in the uploaded or indexed documents to answer safely. "
            "Please upload the relevant contract, policy, guidance, or template, and consider asking a licensed lawyer "
            "for jurisdiction-specific advice."
        )
    else:
        answer = llm.generate(query, context_items, history)

        safety_footer = [
            "",
            "---",
            f"Suggested service route: {recommended_service}.",
        ]

        if human_review_needed:
            safety_footer.append(
                "Human legal review recommended: this appears to involve higher-risk legal, financial, employment, data protection, or signature-related consequences."
            )

        safety_footer.append(
            "Reminder: this is legal information and triage support, not definitive legal advice."
        )

        answer = f"{answer}\n" + "\n".join(safety_footer)

    with st.chat_message("assistant"):
        st.write(answer)

    history_manager.save_interaction(chat_id, query, answer)

    with st.expander("Retrieved sources"):
        if not retrieved_items:
            st.write("No sources retrieved.")
        for index, item in enumerate(retrieved_items, start=1):
            st.markdown(f"**Source [{index}] - {item['source']} | chunk {item['chunk']}**")
            st.write(item["text"])
            if item["distance"] is not None:
                st.caption(f"Retrieval distance: {item['distance']:.4f}")
            st.markdown("---")
