# AI Unit Economics

## Model Choice

The prototype uses local Ollama models:
- LLM: `phi3:mini`
- Embeddings: `nomic-embed-text`
- Vector database: local ChromaDB

This choice fits the project because SME legal documents are sensitive. Local models reduce data exposure, remove per-token API dependency during prototyping, and support privacy-focused deployments for law firms, consultants, or regulated SMEs.

## Baseline Interaction Assumptions

Typical SME query:
- Retrieved context: 1,500-2,500 tokens.
- User question: 20-80 tokens.
- Conversation history: 300-800 tokens.
- Answer: 300-700 tokens.
- Total LLM tokens per query: about 2,500-4,000.

Typical document ingestion:
- 10-page contract: 4,000-7,000 words.
- Chunks: about 20-40.
- Embedding calls: one per chunk.

## Local Ollama Cost Logic

With local models, marginal token cost is close to zero after hardware or server hosting is paid. The main costs become:
- Compute server or developer machine.
- Storage for documents and ChromaDB.
- Backups and monitoring.
- Human review costs when escalated.

Example monthly hosted prototype:
- Small VM/app host: EUR 10-30.
- Larger CPU/GPU server for local inference: EUR 80-300+ depending on speed and concurrency.
- Storage/vector DB: EUR 5-25 for early-stage usage.
- Total early infrastructure range: EUR 95-355/month.

If 100 SMEs pay EUR 49/month, revenue is EUR 4,900/month. Even with EUR 500-1,000/month infrastructure and support tooling, software gross margin can remain high before human-review costs.

## API Model Scenario

If API models are used later, assume:
- 3,000-4,000 tokens per query.
- 50-150 questions per SME per month.
- Embeddings mainly at upload time.

Illustrative cost formula:

`monthly AI cost per SME = query_count * cost_per_query + document_upload_count * embedding_cost_per_document`

If cost per query is EUR 0.002-0.02 depending on model choice, 100 monthly queries cost EUR 0.20-2.00 per SME. If document embeddings cost EUR 0.01-0.10 per document and an SME uploads 20 documents, embeddings cost EUR 0.20-2.00. This supports SaaS pricing if heavy usage is limited by plan.

## Pricing Coverage

Suggested tiers:
- Free: 5 questions/month, 1-2 documents, no human review.
- Starter at EUR 29-49/month: 100 questions/month, 20 documents.
- Professional at EUR 99-199/month: 500+ questions/month, more storage, checklists, exports.
- Premium at EUR 299+/month: includes legal review credits or partner lawyer escalation.

Gross margin controls:
- Usage caps by tier.
- Larger document limits only on paid plans.
- Local embeddings for uploaded files.
- Queueing/batching for heavy ingestion.
- Human review priced separately or included as limited credits.

## Scaling Sustainably

The business scales by separating automated triage from human review:
- AI handles summaries, checklists, source lookup, and risk flags.
- Lawyers handle binding legal advice and high-risk decisions.
- The product captures structured intake data before escalation, making lawyer time more efficient.

This keeps AI costs predictable while creating a premium service path that SMEs can trust.
