# Safety and Privacy Strategy

## Positioning

AI Legal Assistant for SMEs is a legal information, compliance support, and triage tool. It is not a law firm, lawyer, or substitute for licensed legal advice.

## Hallucination Mitigation

The prototype reduces hallucination risk through:
- Retrieval-augmented generation from uploaded documents.
- A system prompt that forbids inventing legal rules outside retrieved context.
- Source-labelled context injected into the prompt.
- Explicit insufficient-context behavior.
- Retrieved source display in the UI.
- Low model temperature.
- Evaluation tests for unsupported claims.

## Human Review Triggers

The assistant recommends human legal review for:
- Contract signing decisions.
- Litigation, court, or penalty exposure.
- GDPR incidents or possible data breaches.
- Employment dismissal or disciplinary issues.
- Tax, shareholder, IP, merger, or acquisition matters.
- Ambiguous or missing source material.
- Jurisdiction-specific questions not answered by retrieved documents.

## Privacy Model

The prototype uses local Ollama models and a local ChromaDB store. In a production SaaS version:
- Each SME should have tenant-isolated storage.
- Documents should be encrypted at rest.
- Access should be role-based.
- Audit logs should record uploads, retrievals, and generated answers.
- Documents should not be used for model training without explicit consent.
- Retention and deletion policies should be clear to customers.

## Liability Mitigation

Risk is reduced through:
- Clear UI disclaimer.
- Source-grounded answers.
- Professional-review recommendations.
- Audit trail of retrieved sources.
- Escalation to licensed lawyers for high-risk cases.
- Avoiding final binding legal drafting unless based on a supplied template.

## Remaining Limitations

The system can retrieve irrelevant chunks, miss context in long documents, or fail to reflect current law if the knowledge base is outdated. It should be evaluated with legal professionals before production use.
