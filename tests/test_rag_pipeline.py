"""
Smoke tests for local RAG components that do not require a running Ollama server.
"""

import json

from src.memory.conversation_history import ConversationHistory
from src.utils.chunker import TextChunker
from src.utils.legal_safety import requires_human_review, route_legal_service
from src.utils.query_guard import (
    can_use_document_fallback,
    classify_query_intent,
    filter_relevant_items,
    insufficient_context_answer,
    normalize_answer_mode,
    service_route_for_mode,
)


def test_chunker_splits_long_text():
    text = "This supplier agreement includes payment terms, liability, and termination. " * 20
    chunker = TextChunker(chunk_size=120, chunk_overlap=20)

    chunks = chunker.split(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_chunker_preserves_legal_section_titles():
    text = """
# Supplier Agreement

## Payment Terms

The client must pay invoices within 30 days.

## Termination

Either party may terminate with 15 days written notice.
"""
    chunker = TextChunker(chunk_size=300, chunk_overlap=40)

    chunks = chunker.split_with_metadata(text)
    titles = {chunk["section_title"] for chunk in chunks}

    assert "Payment Terms" in titles
    assert "Termination" in titles
    assert any("Payment Terms" in chunk["text"] for chunk in chunks)


def test_chunker_splits_long_section_with_overlap_metadata():
    text = "## Liability\n\n" + ("The supplier limits liability for direct damages only. " * 40)
    chunker = TextChunker(chunk_size=180, chunk_overlap=40)

    chunks = chunker.split_with_metadata(text)

    assert len(chunks) > 1
    assert all(chunk["section_title"] == "Liability" for chunk in chunks)
    assert chunks[0]["chunk_in_section"] == 1
    assert chunks[1]["chunk_in_section"] == 2


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


def test_lawyer_review_before_signing_uses_uploaded_contract():
    question = "What should be reviewed by a lawyer before signing?"
    retrieved_items = [
        {
            "text": "Payment terms require payment within 30 days. Either party may terminate with 15 days written notice. Confidentiality lasts for 2 years. Supplier liability is limited to the amount paid in the previous 3 months. The agreement is governed by Portuguese law. Customer delivery information may be processed.",
            "source": "supplier_contract_test.md",
            "source_type": "uploaded",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert classify_query_intent(question) == "lawyer_handoff"
    assert filter_relevant_items(question, retrieved_items) == retrieved_items


def test_signing_related_contract_questions_are_supported():
    questions = [
        "What should I check before signing?",
        "What clauses need legal review?",
        "What should be clarified before signing?",
        "What should be negotiated?",
    ]

    for question in questions:
        assert filter_relevant_items(
            question,
            [
                {
                    "text": "This supplier agreement includes payment terms, liability, termination, confidentiality, and governing law.",
                    "source": "supplier_contract_test.md",
                    "source_type": "uploaded",
                    "chunk": 1,
                    "distance": 0.2,
                }
            ],
        )


def test_document_fallback_allows_general_contract_review_intents():
    retrieved_items = [
        {
            "text": "This supplier agreement includes payment terms, liability, termination, confidentiality, data protection, and governing law.",
            "source": "supplier_contract_test.md",
            "source_type": "uploaded",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert can_use_document_fallback("Summarize this contract in simple terms.", retrieved_items)
    assert can_use_document_fallback("Does this contract include a non-compete clause?", retrieved_items)
    assert can_use_document_fallback("Does this contract contain GDPR-related risks?", retrieved_items)


def test_document_fallback_does_not_allow_out_of_scope_question():
    retrieved_items = [
        {
            "text": "This supplier agreement is governed by Portuguese law.",
            "source": "supplier_contract_test.md",
            "source_type": "uploaded",
            "chunk": 1,
            "distance": 0.2,
        }
    ]

    assert not can_use_document_fallback("Do you think Portugal will ever get in a war with Spain?", retrieved_items)


def test_answer_mode_normalization_and_service_routes():
    assert normalize_answer_mode("summarize_document", "Summarize this contract") == "summary"
    assert normalize_answer_mode("missing_information_scan", "Does this contract include a non-compete clause?") == "missing_information"
    assert normalize_answer_mode("gdpr_data_protection_review", "Does this contract contain GDPR risks?") == "gdpr"

    assert service_route_for_mode("summary") == "Contract summary / general contract review"
    assert service_route_for_mode("missing_information") == "Clause presence / missing clause scan"
    assert service_route_for_mode("gdpr") == "GDPR / data protection review"
    assert service_route_for_mode("lawyer_handoff") == "Lawyer handoff checklist"
    assert service_route_for_mode("risk") == "Contract risk review"


def test_create_new_chat_after_deleted_lower_number(tmp_path):
    history_path = tmp_path / "chat_history.json"
    history_path.write_text(json.dumps({"chat_2": []}))
    history = ConversationHistory(path=str(history_path))

    assert history.create_new_chat() == "chat_3"
