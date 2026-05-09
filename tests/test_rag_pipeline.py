"""
Smoke tests for local RAG components that do not require a running Ollama server.
"""

from src.utils.chunker import TextChunker
from src.utils.legal_safety import requires_human_review, route_legal_service
from src.utils.query_guard import classify_query_intent, filter_relevant_items, insufficient_context_answer


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


def test_out_of_scope_question_does_not_use_supplier_contract():
    question = "Do you think Portugal will ever get in a war with Spain?"
    retrieved_items = [
        {
            "text": "This supplier agreement is governed by Portuguese law.",
            "source": "supplier_contract_test.md",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert filter_relevant_items(question, retrieved_items) == []


def test_insufficient_context_answer_redirects_to_supported_scope():
    answer = insufficient_context_answer("Do you think Portugal will ever get in a war with Spain?")

    assert "do not have enough relevant information" in answer
    assert "contracts" in answer
    assert "GDPR" in answer


def test_general_gdpr_question_does_not_use_uploaded_supplier_contract():
    question = "What GDPR documents should a small company in Portugal prepare?"
    retrieved_items = [
        {
            "text": "This supplier agreement mentions delivery, payment, termination, and Portuguese law.",
            "source": "supplier_contract_test.md",
            "source_type": "uploaded",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert classify_query_intent(question) == "gdpr_general_guidance"
    assert filter_relevant_items(question, retrieved_items) == []


def test_general_gdpr_question_can_use_knowledge_base_source():
    question = "What GDPR documents should a small company in Portugal prepare?"
    retrieved_items = [
        {
            "text": "SMEs should prepare a privacy notice, records of processing, data processing agreements, retention policy, breach response procedure, data subject rights procedure, lawful basis documentation, employee privacy notice, cookie policy where applicable, and DPIA where high-risk processing applies.",
            "source": "gdpr_summary.md",
            "source_type": "knowledge_base",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert filter_relevant_items(question, retrieved_items) == retrieved_items
