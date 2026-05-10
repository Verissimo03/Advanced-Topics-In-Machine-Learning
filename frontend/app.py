"""
Streamlit frontend for AI Legal Assistant for SMEs.

The app reuses the original RAG pipeline and adds legal-focused UX,
source grounding, safety notices, and human-review routing.
"""

import hashlib
import json
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from src.ingestion.document_loader import DocumentLoader
from src.memory.conversation_history import ConversationHistory
from src.memory.vector_store import VectorStore
from src.models.llm import LLM
from src.utils.chunker import TextChunker
from src.utils.config_loader import load_config
from src.utils.legal_safety import requires_human_review, route_legal_service
from src.utils.query_guard import (
    can_use_fast_document_path,
    classify_query_intent,
    can_use_document_fallback,
    get_document_fallback_sources,
    insufficient_context_answer,
    is_supported_scope,
    normalize_answer_mode,
    select_assessed_sources,
    service_route_for_mode,
    should_refuse_assessment,
)


config = load_config()

MODEL_NAME = config["model"]["name"]
TEMPERATURE = config["model"]["temperature"]
MAX_TOKENS = config["model"]["max_tokens"]
HISTORY_TURNS = config["model"]["history_turns"]
EMBEDDING_MODEL = config["embedding"]["model"]
CHUNK_SIZE = config["chunking"]["chunk_size"]
CHUNK_OVERLAP = config["chunking"]["chunk_overlap"]
VECTOR_STORE_PATH = config["vector_store"]["path"]
SYSTEM_PROMPT = config["prompts"]["system"]
LEGAL_DISCLAIMER = config["legal"]["disclaimer"]
N_RESULTS = config["retrieval"]["n_results"]
MAX_DISTANCE = config["retrieval"].get("max_distance")
SUMMARY_CONTEXT_MAX_CHARS = config["retrieval"].get("summary_context_max_chars", 9000)
SUMMARY_CONTEXT_MAX_CHUNKS = config["retrieval"].get("summary_context_max_chunks", 18)
SUMMARY_ANSWER_MAX_TOKENS = config["retrieval"].get("summary_answer_max_tokens", MAX_TOKENS)

CLAUSE_SECTION_TERMS = {
    "non-solicitation": ["non-solicitation", "non solicitation", "restrictive covenant"],
    "restrictive covenant": ["restrictive covenant", "non-solicitation", "non solicitation"],
    "non-compete": ["non-compete", "non compete", "restrictive covenant"],
    "confidentiality": ["confidentiality", "confidential"],
    "liability": ["liability", "limitation of liability", "indemnity"],
    "termination": ["termination", "cancel", "end"],
    "data protection": ["data protection", "gdpr", "privacy", "personal data"],
    "gdpr": [
        "gdpr",
        "data protection",
        "article 28",
        "dpa",
        "data processing agreement",
        "scc",
        "standard contractual clauses",
        "tia",
        "transfer impact assessment",
        "breach",
        "lawful basis",
        "data subject",
        "retention",
        "processor",
        "subprocessor",
        "sub-processor",
        "ai training",
        "international transfer",
    ],
    "payment": ["payment", "fees", "invoice", "price"],
    "governing law": ["governing law", "jurisdiction", "dispute", "court"],
    "assignment": ["assignment", "assign", "subcontract", "subcontracting"],
    "intellectual property": ["intellectual property", "ip", "ownership", "ai outputs", "output"],
    "notices": ["notice", "notices", "online terms"],
}


st.set_page_config(
    page_title="AI Legal Assistant for SMEs",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def format_context(retrieved_items, query_intent):
    """Build source-labelled context for the LLM."""

    formatted = [f"Query intent: {query_intent}"]
    if query_intent == "summary":
        formatted.append(
            "Summary output guide: write a concise plain-language contract summary, not a risk review. "
            "Use one short opening sentence, then a 'Key points' section with 5-8 bullets, then an optional "
            "'Notable unclear points' section with at most 2-3 bullets only if clearly supported. Cover the "
            "main contract topics broadly and do not over-focus on GDPR unless the user asks specifically about GDPR. "
            "If the source appears fictional, sample, demo, or test material, do not refuse; summarize the uploaded "
            "content and add at most one short prototype-testing note."
        )
    for index, item in enumerate(retrieved_items, start=1):
        source_type_label = item.get("source_type_label", "Uploaded document")
        section_title = item.get("section_title") or "Unknown section"
        formatted.append(
            f"Source [{index}] - {source_type_label}: {item['source']} | section: {section_title} | chunk {item['chunk']}:\n{item['text']}"
        )
    return formatted


def merge_retrieved_items(*item_groups):
    """Merge retrieved chunks while preserving order and removing duplicates."""

    merged = []
    seen = set()
    for group in item_groups:
        for item in group or []:
            key = (item.get("source"), item.get("chunk"))
            if key in seen:
                continue
            merged.append(item)
            seen.add(key)
    return merged


def is_party_identity_question(query):
    """Return True for questions asking who the contract parties are."""

    query_lower = query.lower()
    return (
        "parties" in query_lower
        or "party" in query_lower
        or "who is the customer" in query_lower
        or "who is the supplier" in query_lower
        or "who are the parties" in query_lower
    )


def extract_section_terms(query):
    """Extract general legal section terms that can be matched to section titles."""

    query_lower = query.lower()
    terms = set()

    for canonical_term, synonyms in CLAUSE_SECTION_TERMS.items():
        if canonical_term in query_lower or any(synonym in query_lower for synonym in synonyms):
            terms.update(synonyms)

    for token in query_lower.replace("/", " ").replace("-", " ").split():
        clean_token = "".join(character for character in token if character.isalnum())
        if len(clean_token) >= 4:
            terms.add(clean_token)

    return terms


def section_title_matches(item, terms):
    """Return True when a chunk section title matches extracted query terms."""

    section_title = (item.get("section_title") or "").lower()
    if not section_title:
        return False

    compact_title = section_title.replace("-", " ")
    return any(term in compact_title for term in terms)


def get_section_matched_chunks(active_sources, query, limit=6):
    """Retrieve chunks whose section titles match the clause/legal topic."""

    terms = extract_section_terms(query)
    if not terms:
        return []

    matches = []
    for source in active_sources:
        for item in vector_store.get_source_chunks(source):
            if section_title_matches(item, terms):
                matches.append(item)
                if len(matches) >= limit:
                    return matches

    return matches


def build_summary_context(active_sources, semantic_items):
    """
    Build broader document context for contract summaries.

    Small/medium documents are included fully within a character budget. Larger
    documents use the first chunk, semantically retrieved chunks, and a diverse
    one-chunk-per-section sample guided by common contract section titles.
    """

    all_chunks = []
    for source in active_sources:
        all_chunks.extend(vector_store.get_source_chunks(source))

    if not all_chunks:
        return semantic_items

    total_chars = sum(len(item.get("text", "")) for item in all_chunks)
    if total_chars <= SUMMARY_CONTEXT_MAX_CHARS and len(all_chunks) <= SUMMARY_CONTEXT_MAX_CHUNKS:
        return all_chunks

    summary_items = []
    used_titles = set()
    used_keys = set()
    current_chars = 0

    def add_item(item):
        nonlocal current_chars
        key = (item.get("source"), item.get("chunk"))
        if key in used_keys:
            return False
        if len(summary_items) >= SUMMARY_CONTEXT_MAX_CHUNKS:
            return False
        item_chars = len(item.get("text", ""))
        if summary_items and current_chars + item_chars > SUMMARY_CONTEXT_MAX_CHARS:
            return False
        summary_items.append(item)
        used_keys.add(key)
        current_chars += item_chars
        return True

    if all_chunks:
        add_item(all_chunks[0])

    # Prefer broad coverage in original document order: one representative chunk
    # per section title before adding semantic matches.
    for item in all_chunks:
        section_title = (item.get("section_title") or "").lower()
        if not section_title or section_title in used_titles:
            continue
        if add_item(item):
            used_titles.add(section_title)
        if len(summary_items) >= SUMMARY_CONTEXT_MAX_CHUNKS:
            break

    for item in semantic_items:
        add_item(item)

    return summary_items


def build_retrieval_context(query, active_sources, semantic_items):
    """Combine semantic retrieval with metadata-aware legal document retrieval."""

    query_intent = classify_query_intent(query)
    intro_items = []
    if query_intent == "summary":
        return build_summary_context(active_sources, semantic_items)

    if is_party_identity_question(query):
        for source in active_sources:
            intro_items.extend(vector_store.get_source_chunks(source, limit=1))

    section_matches = get_section_matched_chunks(active_sources, query)

    return merge_retrieved_items(intro_items, section_matches, semantic_items)


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


@st.cache_resource
def get_loader():
    return DocumentLoader()


@st.cache_resource
def get_chunker(chunk_size, chunk_overlap):
    return TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


@st.cache_resource
def get_vector_store(persist_directory, embedding_model):
    return VectorStore(
        persist_directory=persist_directory,
        embedding_model=embedding_model,
    )


@st.cache_resource
def get_llm(model_name, system_prompt, temperature, max_tokens, history_turns):
    return LLM(
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        history_turns=history_turns,
    )


loader = get_loader()
chunker = get_chunker(CHUNK_SIZE, CHUNK_OVERLAP)

if "vector_store" not in st.session_state:
    st.session_state.vector_store = get_vector_store(VECTOR_STORE_PATH, EMBEDDING_MODEL)

vector_store = st.session_state.vector_store
llm = get_llm(MODEL_NAME, SYSTEM_PROMPT, TEMPERATURE, MAX_TOKENS, HISTORY_TURNS)
history_manager = ConversationHistory()


with st.sidebar:
    st.title("Legal Workspace")

    st.caption("Upload SME legal documents, templates, policies, or compliance notes.")
    uploaded_file = st.file_uploader(
        "Upload document",
        type=["txt", "pdf", "md", "docx"],
        help="Supported formats: TXT, Markdown, PDF, DOCX.",
    )

    if uploaded_file:
        st.session_state.active_uploaded_sources = [os.path.basename(uploaded_file.name)]
    else:
        st.session_state.active_uploaded_sources = []

    active_sources = st.session_state.get("active_uploaded_sources", [])
    if active_sources:
        st.caption("Active indexed document:")
        for source in active_sources:
            st.write(f"- {source}")
    else:
        st.caption("No active uploaded document for this session.")

    if st.button("Reset document index"):
        vector_store.delete_uploaded_documents()
        st.session_state.active_uploaded_sources = []
        st.session_state.last_file_digest = None
        st.session_state.last_chunk_debug = []
        st.session_state.last_ingest_timings = None
        st.success("Uploaded document chunks cleared from the active index.")
        st.rerun()

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
    file_bytes = uploaded_file.getvalue()
    file_digest = hashlib.sha256(file_bytes).hexdigest()
    active_source = os.path.basename(uploaded_file.name)
    st.session_state.active_uploaded_sources = [active_source]

    if st.session_state.get("last_file_digest") != file_digest:
        st.session_state.last_file_digest = file_digest
        ingest_start = time.perf_counter()

        with st.spinner("Reading, chunking, embedding, and indexing the document..."):
            file_path = os.path.join("data/raw", active_source)
            os.makedirs("data/raw", exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(file_bytes)

            load_start = time.perf_counter()
            text = loader.load(file_path)
            load_seconds = time.perf_counter() - load_start

            chunk_start = time.perf_counter()
            chunk_records = chunker.split_with_metadata(text)
            chunks = [chunk["text"] for chunk in chunk_records]
            chunk_seconds = time.perf_counter() - chunk_start

            file_hash = hashlib.sha256(f"{active_source}:{file_digest}".encode("utf-8")).hexdigest()[:10]
            ids = [f"{file_hash}_chunk_{index}" for index in range(len(chunks))]
            metadatas = [
                {
                    "source": active_source,
                    "source_type": "uploaded",
                    "chunk": index + 1,
                    "section_title": chunk["section_title"],
                    "section_index": chunk["section_index"],
                    "chunk_in_section": chunk["chunk_in_section"],
                    "chunk_chars": chunk["chunk_chars"],
                    "document_type": os.path.splitext(uploaded_file.name)[1].lower(),
                }
                for index, chunk in enumerate(chunk_records)
            ]

            index_start = time.perf_counter()
            vector_store.delete_by_source(active_source)
            vector_store.add_documents(documents=chunks, ids=ids, metadatas=metadatas)
            index_seconds = time.perf_counter() - index_start
            total_ingest_seconds = time.perf_counter() - ingest_start

        st.success(
            f"Document indexed successfully: {len(chunks)} chunks stored "
            f"({total_ingest_seconds:.2f}s total)."
        )
        st.session_state.last_ingest_timings = {
            "document_loading": round(load_seconds, 3),
            "chunking": round(chunk_seconds, 3),
            "embedding_and_indexing": round(index_seconds, 3),
            "total_ingestion": round(total_ingest_seconds, 3),
        }
        st.session_state.last_chunk_debug = [
            {
                "chunk": index + 1,
                "section_title": chunk["section_title"],
                "section_index": chunk["section_index"],
                "chunk_in_section": chunk["chunk_in_section"],
                "chunk_chars": chunk["chunk_chars"],
                "preview": chunk["text"][:100],
                "source": active_source,
                "source_type": "uploaded",
                "document_type": os.path.splitext(uploaded_file.name)[1].lower(),
            }
            for index, chunk in enumerate(chunk_records)
        ]

    if st.session_state.get("last_chunk_debug"):
        with st.expander("Debug: uploaded document chunks"):
            st.write(f"Total chunks created: {len(st.session_state.last_chunk_debug)}")
            st.dataframe(st.session_state.last_chunk_debug, use_container_width=True)


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
    total_start = time.perf_counter()
    timings = {}

    with st.chat_message("user"):
        st.write(query)

    retrieval_start = time.perf_counter()
    active_sources = st.session_state.get("active_uploaded_sources", [])
    semantic_items = vector_store.query_with_sources(
        query,
        n_results=N_RESULTS,
        source_filter=active_sources,
    )
    retrieved_items = build_retrieval_context(
        query,
        active_sources,
        semantic_items,
    )
    timings["retrieval"] = round(time.perf_counter() - retrieval_start, 3)
    relevant_items = []
    assessment = None
    refusal_reason = ""
    used_fast_path = False

    if not retrieved_items:
        refusal_reason = "No chunks were retrieved from the vector store."
        answer = insufficient_context_answer(query, retrieved_items)
    elif not is_supported_scope(query):
        refusal_reason = "Question is outside the supported SME legal/compliance scope."
        answer = insufficient_context_answer(query, retrieved_items)
    elif (
        classify_query_intent(query) == "gdpr_general_guidance"
        and not any(item.get("source_type") == "knowledge_base" for item in retrieved_items)
    ):
        refusal_reason = "General GDPR guidance requires a legal knowledge base source, not only uploaded documents."
        answer = insufficient_context_answer(query, retrieved_items)
    elif can_use_fast_document_path(query, retrieved_items):
        used_fast_path = True
        relevant_items = get_document_fallback_sources(query, retrieved_items)
        assessment = {
            "domain_relevance": "supported",
            "source_relevance": "relevant",
            "context_sufficiency": "sufficient",
            "answer_mode": classify_query_intent(query),
            "usable_source_numbers": [retrieved_items.index(item) + 1 for item in relevant_items],
            "human_review_recommended": requires_human_review(
                query,
                "\n\n".join(item["text"] for item in relevant_items),
            ),
            "reason": "Fast path: supported document-analysis query with uploaded legal-document chunks.",
            "parse_error": False,
        }
    else:
        assessment_start = time.perf_counter()
        with st.spinner("Checking whether the retrieved sources can answer safely..."):
            assessment = llm.assess_context(query, retrieved_items)
        timings["relevance_assessment"] = round(time.perf_counter() - assessment_start, 3)

        relevant_items = select_assessed_sources(
            retrieved_items,
            assessment.get("usable_source_numbers", []),
        )

        if should_refuse_assessment(assessment) or not relevant_items:
            if can_use_document_fallback(query, retrieved_items):
                used_fast_path = True
                relevant_items = get_document_fallback_sources(query, retrieved_items)
                assessment["domain_relevance"] = "supported"
                assessment["source_relevance"] = "partially_relevant"
                assessment["context_sufficiency"] = "sufficient"
                assessment["answer_mode"] = normalize_answer_mode(assessment.get("answer_mode"), query)
                assessment["usable_source_numbers"] = [
                    retrieved_items.index(item) + 1 for item in relevant_items
                ]
                assessment["reason"] = (
                    "Used deterministic document-analysis fallback because the question is a supported "
                    "legal-document task and uploaded contract-like chunks were retrieved."
                )
            else:
                refusal_reason = assessment.get("reason", "The retrieved context was not relevant or sufficient.")
                answer = insufficient_context_answer(query, retrieved_items)

        if relevant_items:
            assessment["answer_mode"] = normalize_answer_mode(assessment.get("answer_mode"), query)

            query_intent = assessment["answer_mode"]
            context_items = format_context(relevant_items, query_intent)
            retrieved_text = "\n\n".join(item["text"] for item in relevant_items)
            recommended_service = service_route_for_mode(query_intent, query)
            human_review_needed = assessment.get("human_review_recommended") or requires_human_review(
                query,
                retrieved_text,
            )

            generation_start = time.perf_counter()
            with st.spinner("Analyzing the retrieved document context..."):
                answer = llm.generate(
                    query,
                    context_items,
                    history,
                    max_tokens=SUMMARY_ANSWER_MAX_TOKENS if query_intent == "summary" else None,
                )
            timings["answer_generation"] = round(time.perf_counter() - generation_start, 3)

            safety_footer = [
                "",
                "---",
                f"Service route: {recommended_service}.",
            ]

            if human_review_needed:
                safety_footer.append(
                    "Human review recommended for this issue."
                )

            safety_footer.append(
                "Note: legal information and triage support only, not definitive legal advice."
            )

            answer = f"{answer}\n" + "\n".join(safety_footer)

    if relevant_items and "answer_generation" not in timings:
        query_intent = normalize_answer_mode(assessment.get("answer_mode"), query)
        context_items = format_context(relevant_items, query_intent)
        retrieved_text = "\n\n".join(item["text"] for item in relevant_items)
        recommended_service = service_route_for_mode(query_intent, query)
        human_review_needed = assessment.get("human_review_recommended") or requires_human_review(
            query,
            retrieved_text,
        )

        generation_start = time.perf_counter()
        with st.spinner("Analyzing the retrieved document context..."):
            answer = llm.generate(
                query,
                context_items,
                history,
                max_tokens=SUMMARY_ANSWER_MAX_TOKENS if query_intent == "summary" else None,
            )
        timings["answer_generation"] = round(time.perf_counter() - generation_start, 3)

        safety_footer = [
            "",
            "---",
            f"Service route: {recommended_service}.",
        ]

        if human_review_needed:
            safety_footer.append("Human review recommended for this issue.")

        safety_footer.append(
            "Note: legal information and triage support only, not definitive legal advice."
        )

        answer = f"{answer}\n" + "\n".join(safety_footer)

    timings["total_response"] = round(time.perf_counter() - total_start, 3)
    with st.chat_message("assistant"):
        st.write(answer)

    history_manager.save_interaction(chat_id, query, answer)

    with st.expander("Retrieved sources"):
        if not relevant_items:
            st.write("No directly relevant sources found for this question.")
        for index, item in enumerate(relevant_items, start=1):
            source_type_label = item.get("source_type_label", "Uploaded document")
            section_title = item.get("section_title") or "Unknown section"
            st.markdown(
                f"**Source [{index}] - {source_type_label}: {item['source']} | section: {section_title} | chunk {item['chunk']}**"
            )
            st.write(item["text"])
            if item["distance"] is not None:
                st.caption(f"Retrieval distance: {item['distance']:.4f}")
            st.markdown("---")

    with st.expander("Debug: relevance decision"):
        st.write(f"Retrieved chunk count: {len(retrieved_items)}")
        st.write(f"Accepted source count: {len(relevant_items)}")
        st.write(f"Active uploaded sources: {active_sources}")
        st.write(f"Fast document path used: {used_fast_path}")
        if refusal_reason:
            st.write(f"Refusal reason: {refusal_reason}")
        if st.session_state.get("last_ingest_timings"):
            st.write("Last ingestion timings")
            st.json(st.session_state.last_ingest_timings)
        st.write("Current query timings")
        st.json(timings)
        if assessment:
            st.json(assessment)
