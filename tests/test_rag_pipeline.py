"""
Smoke tests for local RAG components that do not require a running Ollama server.
"""

from src.utils.chunker import TextChunker
from src.utils.legal_safety import requires_human_review, route_legal_service


def test_chunker_splits_long_text():
    text = "This supplier agreement includes payment terms, liability, and termination. " * 20
    chunker = TextChunker(chunk_size=120, chunk_overlap=20)

    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_legal_safety_flags_high_risk_signature_question():
    question = "Can I sign this contract today without a lawyer?"

    assert requires_human_review(question)


def test_legal_service_routing_for_gdpr():
    question = "Does this privacy policy explain GDPR and personal data obligations?"

    assert route_legal_service(question) == "GDPR / data protection review"
