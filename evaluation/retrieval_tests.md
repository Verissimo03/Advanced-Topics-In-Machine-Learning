# Retrieval Tests

## Test Setup

Upload a controlled set of SME legal documents:
- Supplier agreement.
- GDPR checklist.
- Privacy policy template.
- Employment onboarding checklist.
- Incomplete contract draft.

## Test Cases

| Test | Query | Expected Retrieval |
| --- | --- | --- |
| Contract summary | "Summarize this supplier agreement" | Supplier agreement chunks with parties, scope, payment, liability, termination |
| GDPR obligations | "Does this mention GDPR obligations?" | GDPR checklist or privacy policy chunks |
| Missing clauses | "What clauses are missing?" | Incomplete contract chunks and clause list if available |
| Employment triage | "What should I check before hiring?" | Employment onboarding chunks |
| Lawyer checklist | "What should I ask a lawyer?" | Contract risk and missing-information chunks |

## Pass Criteria

- Retrieved chunks are visibly related to the query.
- The answer cites retrieved source labels.
- The assistant does not rely on unsupported legal claims.
- High-risk questions trigger human review language.

## Notes for Improvement

If retrieval is weak:
- Increase chunk size for legal documents.
- Add metadata filters by document type.
- Add a curated legal glossary.
- Use query rewriting for Portuguese/English legal synonyms.
- Add clause extraction before embedding.
