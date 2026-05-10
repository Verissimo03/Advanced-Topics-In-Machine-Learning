# AI Legal Assistant for SMEs

AI Legal Assistant for SMEs is an AI-first startup prototype for small and medium-sized enterprises in Portugal and the EU. It helps SMEs understand legal documents, identify contract and compliance risks, prepare lawyer handoff checklists, and decide when professional legal review is needed.

This is not a replacement for a lawyer. It is a legal triage, compliance support, and document-understanding assistant powered by retrieval-augmented generation (RAG).

## Startup Concept

SMEs often cannot afford constant legal support, but they still need fast and understandable help with contracts, GDPR, employment documents, service terms, supplier agreements, and internal policies. This prototype gives them a first legal read grounded in uploaded or previously indexed documents, instead of relying on the model as a legal authority.

## Problem

Legal and compliance work is expensive, slow, and difficult for SMEs to interpret. Common problems include:
- Reviewing supplier and client contracts.
- Understanding GDPR obligations.
- Preparing basic employment-law documents.
- Identifying risky or missing clauses.
- Knowing when a lawyer is required.
- Organizing internal legal templates and policies.

## Solution

The app lets users upload documents, ask legal/compliance questions, and receive source-grounded answers. It separates information found in documents from practical interpretation, cites retrieved sources, flags uncertainty, and recommends human legal review for higher-risk issues.

Current scope: the prototype answers from retrieved document chunks stored in the local vector database. These chunks come from documents uploaded through the app. A curated fixed Portugal/EU legal knowledge base is a future improvement, not part of the current core implementation.

## Target Market

Primary users:
- Portuguese and EU SMEs.
- Founders and operations teams.
- Accounting firms and consultants serving SMEs.
- Small law firms seeking AI-supported client intake.

## Features

- Streamlit frontend.
- Document upload for TXT, Markdown, PDF, and DOCX.
- Local Ollama LLM and embeddings.
- ChromaDB persistent vector store.
- Conversation history.
- Source-grounded answers.
- Retrieved source display.
- Legal disclaimer.
- Portugal/EU SME legal triage prompt.
- Human-review recommendation logic.
- Legal service routing.
- Investor and academic documentation.

## Technical Architecture

Pipeline:

1. Document ingestion.
2. Text extraction.
3. Chunking.
4. Embedding generation.
5. Persistent vector storage in ChromaDB.
6. Semantic retrieval.
7. Source-labelled prompt construction.
8. Ollama LLM answer generation.
9. Source-grounded response with safety footer.
10. Conversation history storage.

Core files:
- `frontend/app.py`: Streamlit user interface and legal workflow logic.
- `src/ingestion/document_loader.py`: TXT, Markdown, PDF, DOCX parsing.
- `src/utils/chunker.py`: recursive text splitting.
- `src/memory/vector_store.py`: ChromaDB storage and source-aware retrieval.
- `src/models/llm.py`: Ollama chat wrapper.
- `src/memory/conversation_history.py`: persistent chat history.
- `config/config.yaml`: model, chunking, vector store, prompt, and disclaimer settings.

## Tech Stack

- Python
- Streamlit
- Ollama
- ChromaDB
- LangChain text splitters
- pypdf
- python-docx

## How to Run Locally

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install and run Ollama, then pull the local models:

```bash
ollama pull phi3:mini
ollama pull nomic-embed-text
```

4. Start the app:

```bash
streamlit run frontend/app.py
```

## How to Deploy

The prototype can be deployed as a Streamlit app with a persistent storage volume for:
- `data/raw/`
- `data/vector_store/`
- `data/chat_history.json`

For privacy-focused deployments, run Ollama and ChromaDB inside the same private environment as the Streamlit backend.

## Supported File Types

- `.txt`
- `.md`
- `.pdf`
- `.docx`

## Example Use Cases

- "What are the main risks in this contract?"
- "Does this document mention GDPR obligations?"
- "What should I check before hiring an employee in Portugal?"
- "Which legal service do I need for this issue?"
- "What clauses are missing from this supplier agreement?"
- "Can you summarize this contract in simple language?"
- "What should I ask a lawyer before signing this?"

## Demo Preparation

Use your own class demo contract or a non-confidential sample document. Upload it through the Streamlit sidebar before asking questions. The app supports fictional or test contracts for prototype evaluation, but outputs remain legal information and triage support only.

## AI Unit Economics

The prototype uses local Ollama models, so marginal inference cost is low after hosting costs. A cloud API version can still be viable with usage limits by tier. See `docs/ai_unit_economics.md` for assumptions and pricing coverage.

## Revenue Model

Suggested SaaS tiers:
- Free/basic: limited document checks.
- Starter: monthly subscription for small SMEs.
- Professional: higher usage, contract analysis, checklists, history.
- Premium/human-in-the-loop: legal review credits or partner lawyer referral.

Additional models:
- Pay-per-contract review.
- Monthly compliance monitoring.
- Law firm referral partnerships.
- White-label version for accounting firms, consultants, and law firms.

## Moat and Defensibility

This is designed as more than a generic chatbot wrapper:
- SME-specific legal workflows.
- Portugal/EU-focused legal workflow strategy.
- RAG grounded in uploaded/indexed documents and visible retrieved sources.
- Source audit trail.
- Human-in-the-loop escalation.
- Structured risk/service routing.
- Clause extraction and categorization roadmap.
- Domain-specific manual evaluation scenarios.
- Privacy-focused local model option.
- Conversation and document history for each SME client.

## Safety and Legal Disclaimer

The assistant provides legal information and triage support, not definitive legal advice. It is not a substitute for a licensed lawyer. Users should request professional legal review for high-risk, ambiguous, jurisdiction-specific, employment, GDPR, tax, litigation, or contract-signing decisions.

See `docs/safety_and_privacy.md`.

## GenAI Transparency

The course transparency appendix is available at `docs/genai_transparency_log.md`. It records AI assistance during ideation, coding, debugging, prompt engineering, writing, and business-plan development.

## Evaluation

The current project is tested manually through the Streamlit interface using uploaded contracts and legal/compliance questions. Recommended checks include source grounding, refusal of unrelated questions, contract summary quality, clause presence/absence, GDPR/data-protection analysis, and human-review recommendations.

## Limitations

- The prototype does not provide binding legal advice.
- Retrieved chunks may omit relevant context from long documents.
- The current prototype does not include a fixed curated legal knowledge base.
- Production deployment needs tenant isolation, authentication, encryption, and stronger audit logging.
- Human lawyers are required for definitive legal conclusions.

## Future Improvements

- Multi-tenant workspaces.
- Clause extraction and risk scoring.
- Portuguese/English legal synonym expansion.
- Document comparison.
- Lawyer review dashboard.
- Admin analytics and audit exports.
- Optional curated Portugal/EU legal knowledge base.
- Production authentication and encryption.
