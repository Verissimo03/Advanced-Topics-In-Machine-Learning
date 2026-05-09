"""
Lightweight legal safety helpers for the SME legal assistant.
"""

HIGH_RISK_KEYWORDS = [
    "lawsuit",
    "court",
    "tribunal",
    "fine",
    "penalty",
    "dismissal",
    "termination",
    "data breach",
    "breach",
    "criminal",
    "tax",
    "shareholder",
    "merger",
    "acquisition",
    "intellectual property",
    "gdpr violation",
    "sign",
    "signature",
]

SERVICE_ROUTES = {
    "GDPR / data protection review": ["gdpr", "data protection", "privacy", "personal data", "breach"],
    "Employment law review": ["employee", "employment", "worker", "dismissal", "salary", "contract of employment"],
    "Commercial contract review": ["supplier", "client", "service agreement", "payment", "liability", "termination"],
    "Corporate legal review": ["shareholder", "company incorporation", "equity", "board", "merger"],
    "IP / technology legal review": ["copyright", "trademark", "software", "license", "intellectual property"],
}


def requires_human_review(question: str, retrieved_text: str = "") -> bool:
    """Return True when the issue should be escalated to a lawyer."""

    combined_text = f"{question} {retrieved_text}".lower()
    return any(keyword in combined_text for keyword in HIGH_RISK_KEYWORDS)


def route_legal_service(question: str, retrieved_text: str = "") -> str:
    """Suggest the most likely legal service category using transparent rules."""

    combined_text = f"{question} {retrieved_text}".lower()

    for service, keywords in SERVICE_ROUTES.items():
        if any(keyword in combined_text for keyword in keywords):
            return service

    return "General SME legal triage"
