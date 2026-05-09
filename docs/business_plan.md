# Business Plan: AI Legal Assistant for SMEs

## Startup Concept

AI Legal Assistant for SMEs is a Portugal/EU-focused legal triage and compliance support platform for small and medium-sized enterprises. It helps teams understand contracts, GDPR obligations, employment-law documents, internal policies, and lawyer handoff needs through a source-grounded RAG assistant.

The product is not positioned as a replacement for lawyers. It is an AI-first workflow layer that reduces low-value legal friction, organizes company legal knowledge, and escalates higher-risk matters to human legal professionals.

## Target Market

Primary customers are Portuguese and EU SMEs with 5-250 employees that regularly handle supplier agreements, client contracts, employment documents, privacy policies, service terms, and compliance checklists but do not have full-time legal teams.

Initial beachhead:
- Portuguese SMEs in services, retail, SaaS, consulting, hospitality, and agencies.
- Accounting firms and business consultants serving SME clients.
- Small law firms that want a client-facing triage and intake tool.

## Pain Point

SMEs need legal clarity before making routine business decisions, but legal support is expensive, slow, and often inaccessible for smaller companies. They may sign contracts without understanding risk, miss GDPR obligations, use outdated templates, or contact lawyers only after a problem becomes costly.

## Value Proposition

The assistant gives SMEs a faster first legal read:
- Plain-language contract summaries.
- Risky clause identification.
- GDPR and compliance checklist support.
- Employment-law triage.
- Missing information detection.
- Lawyer handoff questions.
- Source-grounded answers using uploaded documents and trusted knowledge bases.

## Product Description

The prototype includes a Streamlit interface, document upload, persistent vector database, conversation history, local Ollama models, legal/compliance prompt rules, source display, and human-review recommendation logic.

Core workflow:
1. SME uploads a document or internal policy.
2. The system parses, chunks, embeds, and stores it in ChromaDB.
3. The SME asks a legal/compliance question.
4. The system retrieves relevant passages.
5. The LLM answers using only retrieved context and cites sources.
6. The app flags uncertainty, risky topics, and likely service routes.

## Go-To-Market Strategy

Initial GTM should focus on trust-heavy channels:
- Partner with accounting firms and SME consultants.
- Offer a free contract/GDPR health-check campaign.
- Build templates for Portuguese supplier agreements, privacy policies, employment onboarding, and service terms.
- Create white-label pilots with small law firms.
- Sell to accelerators and local business associations as a compliance enablement tool.

## Revenue Model

SaaS pricing:
- Free/basic: limited document checks per month, basic summaries.
- Starter: EUR 29-49/month for small SMEs, limited uploads and Q&A.
- Professional: EUR 99-199/month for heavier document analysis, checklists, history, and admin controls.
- Premium/human-in-the-loop: EUR 299+/month or per-review fees including lawyer referral or review credits.

Additional revenue:
- Pay-per-contract review.
- Monthly compliance monitoring.
- Referral fees from partner law firms where legally permitted.
- White-label subscriptions for accounting firms, consultants, and law firms.

## Cost Structure

Main costs:
- Model inference or local GPU/CPU hosting.
- Embedding generation.
- Streamlit/app hosting.
- Vector database storage.
- Legal knowledge-base curation.
- Human legal review partner fees.
- Security, monitoring, and support.

## AI Unit Economics

See `docs/ai_unit_economics.md` for assumptions. The prototype uses local Ollama models, which keep marginal inference costs low after hardware/hosting is paid. For cloud API deployment, the expected cost per interaction remains small enough for SaaS gross margins if usage limits and tiering are enforced.

## Competitive Landscape

Alternatives include:
- General chatbots.
- Legal document automation tools.
- Law firm consultations.
- Contract lifecycle management platforms.
- Compliance consultants.

The wedge is SME-specific legal triage for Portugal/EU, combining private document grounding, structured workflows, and human escalation.

## Moat and Defensibility

This should not be judged as a generic chatbot wrapper. Defensibility comes from:
- Portugal/EU-focused legal knowledge base and templates.
- SME workflow design around contracts, GDPR, employment, and lawyer handoff.
- RAG grounded in trusted legal materials and company documents.
- Structured risk scoring and service routing.
- Clause extraction and categorization roadmap.
- Audit trail of retrieved sources and AI responses.
- Human-in-the-loop review partnerships.
- Domain-specific prompt engineering and evaluation tests.
- Privacy-focused local/open-source deployment options.
- Conversation and document history per SME client.

## Safety and Privacy Strategy

The assistant always states that it is not a lawyer and does not provide definitive legal advice. It uses retrieved documents as the answer basis, cites sources, flags uncertainty, and recommends human review for high-risk cases.

Private documents should be stored in isolated tenant workspaces in production, encrypted at rest, and never used for model training without explicit consent.

## Human-In-The-Loop Strategy

Human review is triggered when matters involve signing contracts, employment termination, GDPR incidents, litigation, tax, penalties, ambiguity, or missing source context. The business can route these cases to partner lawyers or internal legal reviewers.

## Risks and Mitigations

- Hallucinated legal advice: strict RAG prompt, source citations, insufficient-context refusals, evaluation tests.
- Liability: legal disclaimer, triage positioning, escalation triggers, partner lawyer review.
- Data privacy: local deployment option, encryption, access control, tenant isolation.
- Weak moat critique: focus on domain workflows, curated knowledge base, audit logs, service routing, and partnerships.
- Cost overruns: usage tiers, local models, batching embeddings, limits per plan.
- Outdated law: versioned knowledge base and periodic legal review of source documents.
