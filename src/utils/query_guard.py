"""
Query scope and retrieval relevance checks for the legal RAG assistant.
"""

from __future__ import annotations

import re


SUPPORTED_SCOPE_TERMS = {
    "agreement",
    "clause",
    "clauses",
    "client",
    "compliance",
    "confidentiality",
    "contract",
    "data",
    "document",
    "employment",
    "gdpr",
    "invoice",
    "jurisdiction",
    "law",
    "lawful",
    "legal",
    "lawyer",
    "liability",
    "non-compete",
    "payment",
    "personal",
    "policy",
    "privacy",
    "processor",
    "risk",
    "risks",
    "service",
    "sign",
    "signing",
    "supplier",
    "termination",
    "terms",
}

SUPPORTED_ACTION_TERMS = {
    "analyze",
    "check",
    "clarified",
    "compare",
    "explain",
    "find",
    "identify",
    "missing",
    "negotiate",
    "negotiated",
    "review",
    "reviewed",
    "summarize",
    "summary",
}

LAWYER_HANDOFF_TERMS = {
    "before signing",
    "clarified",
    "legal review",
    "lawyer",
    "negotiate",
    "negotiated",
    "reviewed",
    "signing",
}

DOCUMENT_REFERENCE_TERMS = {
    "agreement",
    "clause",
    "contract",
    "document",
    "file",
    "policy",
    "this",
    "uploaded",
}

GENERAL_GUIDANCE_TERMS = {
    "checklist",
    "documents",
    "prepare",
    "required",
    "requirements",
    "should",
    "small company",
    "sme",
}

OUT_OF_SCOPE_TERMS = {
    "army",
    "battle",
    "election",
    "football",
    "geopolitical",
    "invasion",
    "military",
    "politics",
    "war",
    "weather",
}

STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "have",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "whether",
    "will",
    "with",
    "you",
}


def tokenize(text: str) -> set[str]:
    """Return simple lowercase word tokens for transparent relevance checks."""

    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z-]{2,}", text.lower())
        if token not in STOPWORDS
    }


def classify_query_intent(question: str) -> str:
    """Classify the requested answer shape for prompt conditioning."""

    question_lower = question.lower()

    if any(term in question_lower for term in ["summarize", "summary", "plain language"]):
        return "summary"
    if any(term in question_lower for term in LAWYER_HANDOFF_TERMS):
        return "lawyer_handoff"
    if any(term in question_lower for term in ["risk", "risky", "red flag", "before signing"]):
        return "risk"
    if any(term in question_lower for term in ["gdpr", "data protection", "privacy", "personal data"]):
        if is_general_guidance_question(question):
            return "gdpr_general_guidance"
        return "gdpr"
    if any(term in question_lower for term in ["missing", "not include", "does it contain", "non-compete"]):
        return "missing_information"
    return "general_legal_triage"


def is_general_guidance_question(question: str) -> bool:
    """
    Return True when a GDPR/legal question asks for general guidance rather than
    analysis of a specific uploaded document.
    """

    question_lower = question.lower()
    tokens = tokenize(question)

    has_general_guidance = bool(tokens & GENERAL_GUIDANCE_TERMS) or any(
        phrase in question_lower for phrase in GENERAL_GUIDANCE_TERMS if " " in phrase
    )
    has_document_reference = bool(tokens & DOCUMENT_REFERENCE_TERMS)

    if "gdpr" in question_lower and has_general_guidance and not has_document_reference:
        return True

    if "what" in tokens and {"documents", "prepare"} & tokens and not has_document_reference:
        return True

    return False


def is_supported_scope(question: str) -> bool:
    """
    Return True when the question is inside the product scope.

    The product scope is SME legal/compliance document analysis. Broad
    geopolitical, medical, financial-market, or unrelated questions should not
    be answered from weakly related contract chunks.
    """

    tokens = tokenize(question)
    question_lower = question.lower()

    has_supported_term = bool(tokens & SUPPORTED_SCOPE_TERMS)
    has_supported_action = bool(tokens & SUPPORTED_ACTION_TERMS)
    has_out_of_scope_term = bool(tokens & OUT_OF_SCOPE_TERMS)

    if has_out_of_scope_term and not has_supported_term:
        return False

    return has_supported_term or has_supported_action


def filter_relevant_items(question: str, retrieved_items: list[dict], max_distance: float | None = None) -> list[dict]:
    """
    Filter retrieved chunks using distance and transparent lexical overlap.

    This is intentionally conservative. It blocks obviously irrelevant chunks,
    but keeps legal document chunks for summary/review questions where the user
    refers to "this document" without repeating exact terms from the chunk.
    """

    if not is_supported_scope(question):
        return []

    question_tokens = tokenize(question)
    intent = classify_query_intent(question)
    filtered = []

    if intent == "gdpr_general_guidance":
        return [
            item
            for item in retrieved_items
            if item.get("source_type") == "knowledge_base" and _passes_distance(item, max_distance)
        ]

    for item in retrieved_items:
        if not _passes_distance(item, max_distance):
            continue

        item_tokens = tokenize(item.get("text", ""))
        overlap = question_tokens & item_tokens
        legal_overlap = question_tokens & SUPPORTED_SCOPE_TERMS

        if overlap or legal_overlap:
            filtered.append(item)
            continue

        if intent in {"summary", "risk", "lawyer_handoff", "missing_information", "general_legal_triage"}:
            if item_tokens & SUPPORTED_SCOPE_TERMS:
                filtered.append(item)

    return filtered


def select_assessed_sources(retrieved_items: list[dict], usable_source_numbers: list) -> list[dict]:
    """Select retrieved items by 1-based source numbers returned by the assessor."""

    selected = []
    for source_number in usable_source_numbers:
        if not isinstance(source_number, int):
            continue

        index = source_number - 1
        if 0 <= index < len(retrieved_items):
            selected.append(retrieved_items[index])

    return selected


def should_refuse_assessment(assessment: dict) -> bool:
    """Return True when the structured assessment says not to answer."""

    return (
        assessment.get("domain_relevance") != "supported"
        or assessment.get("source_relevance") == "not_relevant"
        or assessment.get("context_sufficiency") == "insufficient"
        or assessment.get("answer_mode") == "refuse"
    )


def _passes_distance(item: dict, max_distance: float | None) -> bool:
    """Return True if a retrieved item passes the configured distance threshold."""

    distance = item.get("distance")
    return not (max_distance is not None and distance is not None and distance > max_distance)


def insufficient_context_answer(question: str, retrieved_items: list[dict] | None = None) -> str:
    """Return a safe answer when the retrieved context is missing or irrelevant."""

    available_sources = []
    for item in retrieved_items or []:
        source = item.get("source")
        if source and source not in available_sources:
            available_sources.append(source)

    source_text = ""
    if available_sources:
        source_text = f" The available retrieved source appears to be: {', '.join(available_sources)}."

    return (
        "I do not have enough relevant information in the uploaded or indexed documents to answer this question."
        f"{source_text} I can help analyze contracts, GDPR/data protection materials, employment-law documents, "
        "SME compliance documents, and lawyer handoff questions. For unrelated or high-risk matters, please use an "
        "appropriate professional source."
    )
