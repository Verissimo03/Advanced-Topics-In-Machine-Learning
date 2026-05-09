# Retrieval Tests

## Test Setup

Upload the controlled demo SME legal documents from `demo_documents/`:
- Supplier agreement.
- GDPR checklist.
- Incomplete contract draft.

## Test Cases

| Test | Query | Expected Retrieval |
| --- | --- | --- |
| Contract summary | "Summarize this supplier agreement" | Supplier agreement chunks with parties, scope, payment, liability, termination |
| GDPR obligations | "Does this mention GDPR obligations?" | GDPR checklist chunks |
| Missing clauses | "What clauses are missing?" | Incomplete contract chunks and clause list if available |
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
- Add a curated legal glossary or fixed legal knowledge base as future work.
- Use query rewriting for Portuguese/English legal synonyms.
- Add clause extraction before embedding.
