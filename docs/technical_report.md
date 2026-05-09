# Technical Report: AI Legal Assistant for SMEs

## 1. Executive Summary

### What This Project Is

This project is a full-stack prototype for an AI-first startup called **AI Legal Assistant for SMEs**.

The app helps small and medium-sized companies in Portugal and the EU understand legal and compliance documents using a Retrieval-Augmented Generation (RAG) system.

In simple terms:

- The user uploads a legal or compliance document.
- The system reads and stores the document.
- The user asks questions in a chat interface.
- The system retrieves the most relevant parts of the uploaded documents.
- A local AI model answers using those retrieved sources.
- The app shows the answer, the retrieved sources, and safety warnings where needed.

### What Problem It Solves

SMEs often need legal help but cannot afford constant legal support. They may need to:

- Understand supplier/client contracts.
- Check GDPR obligations.
- Review employment-related documents.
- Identify risky clauses.
- Know when to contact a lawyer.
- Prepare questions before sending a document to a lawyer.

The app gives SMEs a first layer of legal triage and document understanding.

It is **not a replacement for a lawyer**. It is designed to help users understand documents and decide when professional legal review is needed.

### What the App Currently Does

The current app can:

- Upload `.txt`, `.md`, `.pdf`, and `.docx` documents.
- Extract text from those documents.
- Split the text into smaller chunks.
- Create embeddings using a local Ollama embedding model.
- Store the chunks in a persistent ChromaDB vector store.
- Let users ask questions in a Streamlit chat interface.
- Retrieve relevant chunks from the vector store.
- Send those chunks to a local Ollama LLM.
- Generate source-grounded answers.
- Display retrieved sources to the user.
- Store conversation history.
- Show a legal disclaimer.
- Recommend human legal review for higher-risk topics.
- Suggest a legal service route, such as GDPR review, employment law review, or contract review.

### What Was Adapted From the Previous RAG Project

The following core technical foundation was reused:

- Streamlit frontend structure.
- Document upload workflow.
- Document loader.
- Text chunking logic.
- Ollama LLM integration.
- Ollama embedding integration.
- ChromaDB vector store.
- Persistent vector storage.
- Conversation history.
- Config-based model and prompt settings.

### What Is New in This Legal Services Version

The new project adds:

- Legal services branding.
- SME and Portugal/EU positioning.
- Legal disclaimer.
- Legal/compliance prompt rules.
- Source-labelled retrieved context.
- Retrieved source display in the UI.
- Human legal review recommendation logic.
- Legal service routing logic.
- Business plan documentation.
- AI unit economics documentation.
- Safety/privacy documentation.
- GenAI transparency log.
- Evaluation files for hallucination and retrieval testing.
- Group PowerPoint business plan file in `docs/`.

## 2. Repository Status

### Current Project Folder Name

The current repository folder is:

```text
Advanced-Topics-In-Machine-Learning
```

Full local path:

```text
/home/tiagoveri/NovaSBE/2ºSemester/AdvancedProgrammingforDataScience/Project/Advanced-Topics-In-Machine-Learning
```

### Current Git Branch

The current branch is:

```text
main
```

### Is the Repo Connected to GitHub?

No.

At the time of this report, `git remote -v` returns no remote URLs. That means this local repository is not connected to a GitHub repository yet.

### Has It Been Pushed or Published?

No evidence of a GitHub push exists because there is no configured remote.

The project has been committed locally, but it has not been published to GitHub from this repository.

### Latest Commit

Latest commit:

```text
9471ff4 Initial AI legal assistant prototype
```

### Files Changed in the Latest Commit

The first commit added 25 files:

- `.gitignore`
- `LICENSE`
- `README.md`
- `config/config.yaml`
- `data/raw/.gitkeep`
- `data/vector_store/.gitkeep`
- `docs/LexAI_Portugal_Business_Plan.pptx`
- `docs/ai_unit_economics.md`
- `docs/business_plan.md`
- `docs/evaluation_plan.md`
- `docs/genai_transparency_log.md`
- `docs/safety_and_privacy.md`
- `evaluation/hallucination_tests.md`
- `evaluation/retrieval_tests.md`
- `evaluation/sample_questions.md`
- `frontend/app.py`
- `requirements.txt`
- `src/ingestion/document_loader.py`
- `src/memory/conversation_history.py`
- `src/memory/vector_store.py`
- `src/models/llm.py`
- `src/utils/chunker.py`
- `src/utils/config_loader.py`
- `src/utils/legal_safety.py`
- `tests/test_rag_pipeline.py`

### Files Still Uncommitted

Before this report was created, the working tree was clean.

This report file itself is now a new uncommitted file:

```text
docs/technical_report.md
```

It should only be committed when you decide to commit it.

### Commands to Publish to GitHub

Because no remote is configured, you need to create a GitHub repository first. You can do this manually on GitHub, then run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/Advanced-Topics-In-Machine-Learning.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

If you use SSH instead of HTTPS, use:

```bash
git remote add origin git@github.com:YOUR_USERNAME/Advanced-Topics-In-Machine-Learning.git
git push -u origin main
```

Do not use `--force` unless you intentionally want to overwrite history on GitHub. There is no reason to force-push for the normal first publish.

## 3. Project Architecture

### High-Level Architecture

The project has these main layers:

1. **Frontend**
   - Built with Streamlit.
   - Gives the user a web interface.
   - Handles document upload, chat, conversation selection, and source display.

2. **Backend / AI Logic**
   - Python modules inside `src/`.
   - Handles document loading, chunking, vector storage, retrieval, LLM calls, safety logic, and conversation memory.

3. **RAG Pipeline**
   - Reads uploaded documents.
   - Splits them into chunks.
   - Embeds the chunks.
   - Stores them in ChromaDB.
   - Retrieves relevant chunks when the user asks a question.
   - Sends retrieved context to the LLM.
   - Produces an answer grounded in the retrieved documents.

4. **Document Ingestion**
   - Supports TXT, Markdown, PDF, and DOCX.
   - Converts files into plain text.

5. **Vector Store / Memory Store**
   - Uses ChromaDB.
   - Stores embedded chunks.
   - Persists data locally in `data/vector_store/`.

6. **Conversation History**
   - Stores chat interactions in `data/chat_history.json`.
   - Lets the user select previous conversations.

7. **Configuration**
   - Stored in `config/config.yaml`.
   - Controls model names, chunk size, chunk overlap, vector store path, legal disclaimer, and legal prompt.

8. **Documentation**
   - Stored in `docs/`.
   - Explains business plan, AI costs, safety, privacy, evaluation, transparency, and this technical report.

9. **Evaluation**
   - Stored in `evaluation/`.
   - Contains sample questions, hallucination tests, and retrieval tests.

### How the Parts Connect

The main Streamlit app imports all backend components:

- `DocumentLoader` reads uploaded files.
- `TextChunker` splits extracted text.
- `VectorStore` stores and retrieves chunks.
- `LLM` sends the prompt to Ollama.
- `ConversationHistory` saves chat turns.
- `load_config` reads settings from YAML.
- `legal_safety` functions add legal escalation and service-routing logic.

The user only interacts with Streamlit, but Streamlit calls the full RAG pipeline behind the scenes.

## 4. File-by-File Explanation

### `frontend/app.py`

Purpose:

- Main Streamlit application.
- Controls the website interface.
- Connects frontend actions to backend RAG logic.

Reused or new:

- Reused the old Streamlit structure.
- Heavily modified for the legal assistant.

Main changes:

- Rebranded the app to "AI Legal Assistant for SMEs".
- Added legal disclaimer.
- Added SME legal workflow suggestions.
- Added source-aware context formatting.
- Added legal service routing.
- Added human-review recommendation logic.
- Added retrieved source display.
- Updated chat placeholder and UI text.

Why this was necessary:

- The previous app was a generic document Q&A RAG app.
- This project needs to look and behave like a legal services startup prototype.

### `src/ingestion/document_loader.py`

Purpose:

- Loads documents from different file types.
- Converts them into plain text.

Reused or new:

- Mostly reused from the previous project.

Supported formats:

- `.txt`
- `.md`
- `.pdf`
- `.docx`

Why it matters:

- Legal documents often come as PDFs and DOCX files.
- The RAG system needs plain text before it can chunk and embed documents.

### `src/utils/chunker.py`

Purpose:

- Splits long text into smaller chunks.

Reused or new:

- Reused from the previous project.

Main logic:

- Uses `RecursiveCharacterTextSplitter`.
- Chunk size and overlap come from `config/config.yaml`.

Why it matters:

- LLMs cannot process very long documents all at once.
- Retrieval works better when documents are split into manageable pieces.

### `src/memory/vector_store.py`

Purpose:

- Manages ChromaDB.
- Stores document chunks as embeddings.
- Retrieves relevant chunks for user questions.

Reused or new:

- Reused, but modified.

Main changes:

- Added optional metadata when storing chunks.
- Added `query_with_sources`, which returns chunk text plus source information.

Why this was necessary:

- Legal answers must be source-grounded.
- The app needs to show which document/chunk was used.

### `src/models/llm.py`

Purpose:

- Wrapper around Ollama chat model.
- Sends system prompt, conversation history, retrieved context, and user question to the model.

Reused or new:

- Reused, but modified.

Main changes:

- Added temperature configuration.

Why this was necessary:

- Lower temperature makes legal answers more stable and less creative.

### `src/memory/conversation_history.py`

Purpose:

- Stores and loads chat history.

Reused or new:

- Reused from the previous project.

Why it matters:

- Users can continue previous conversations.
- It creates a basic audit trail of questions and answers.

### `src/utils/config_loader.py`

Purpose:

- Loads YAML config from `config/config.yaml`.

Reused or new:

- Reused from the previous project.

Why it matters:

- Keeps model names, prompts, chunking, and legal disclaimer separate from code.

### `src/utils/legal_safety.py`

Purpose:

- Adds simple legal triage logic.

Reused or new:

- New file.

Main features:

- Detects high-risk keywords.
- Suggests human legal review.
- Routes questions to likely legal service categories.

Why it matters:

- The startup concept is not only Q&A.
- It includes legal triage and escalation logic.

### `config/config.yaml`

Purpose:

- Stores model, embedding, chunking, vector store, disclaimer, and prompt configuration.

Reused or new:

- Reused, but heavily modified.

Main changes:

- Rebranded prompt for legal assistant.
- Added legal disclaimer.
- Added safety rules.
- Increased chunk size from the old generic setup.
- Lowered temperature.

Why it matters:

- The prompt controls how the assistant behaves.
- For legal use, the model must avoid unsupported legal advice.

### `README.md`

Purpose:

- Main project explanation.
- Explains startup concept, problem, solution, architecture, run instructions, moat, safety, and limitations.

Reused or new:

- Rewritten from the previous generic RAG README.

Why it matters:

- The README is often the first thing professors or judges read.
- It must show this is an AI-first startup prototype, not just a coding exercise.

### `docs/`

Purpose:

- Contains business and technical documentation.

Files:

- `business_plan.md`: startup concept, revenue model, moat, GTM, risks.
- `ai_unit_economics.md`: AI cost assumptions and pricing logic.
- `safety_and_privacy.md`: legal safety and privacy controls.
- `genai_transparency_log.md`: AI tool usage log template.
- `evaluation_plan.md`: how to evaluate the system.
- `LexAI_Portugal_Business_Plan.pptx`: group business plan presentation.
- `technical_report.md`: this report.

### `evaluation/`

Purpose:

- Contains evaluation examples and tests for the AI Judge.

Files:

- `sample_questions.md`: realistic demo questions.
- `hallucination_tests.md`: prompts designed to test refusal and safety.
- `retrieval_tests.md`: tests to check whether retrieval returns relevant chunks.

### `tests/test_rag_pipeline.py`

Purpose:

- Simple smoke tests for local logic.

Reused or new:

- Rewritten from the previous full RAG script.

Why it changed:

- The old test depended on live documents and outdated method calls.
- The new tests focus on local functions that can run without Ollama.

### `requirements.txt`

Purpose:

- Lists Python dependencies.

Important dependencies:

- `streamlit`
- `chromadb`
- `ollama`
- `langchain-text-splitters`
- `pypdf`
- `python-docx`
- `PyYAML`

### `.gitignore`

Purpose:

- Prevents virtual environments, caches, runtime data, chat history, and generated files from being committed.

Important for this project:

- Avoids committing private uploaded legal documents.
- Avoids committing local vector database binaries.

## 5. Function-by-Function Explanation

### `format_context(retrieved_items)`

File:

```text
frontend/app.py
```

What it does:

- Converts retrieved chunks into text labels like `Source [1] - filename | chunk 3`.

Inputs:

- `retrieved_items`: a list of retrieved chunks with metadata.

Returns:

- A list of formatted strings.

Where used:

- Used before calling the LLM.

How it contributes:

- Makes source citations possible in the answer.

### `save_uploaded_file(uploaded_file)`

File:

```text
frontend/app.py
```

What it does:

- Saves the uploaded Streamlit file into `data/raw/`.

Inputs:

- `uploaded_file`: the file object from Streamlit.

Returns:

- The local file path.

Where used:

- Used when a user uploads a document.

How it contributes:

- Creates a local copy so the document loader can read it.

### `DocumentLoader.load(file_path)`

File:

```text
src/ingestion/document_loader.py
```

What it does:

- Checks the file extension.
- Calls the correct loader for TXT/MD, PDF, or DOCX.

Inputs:

- `file_path`: path to uploaded document.

Returns:

- Extracted plain text.

Where used:

- In `frontend/app.py` during document ingestion.

How it contributes:

- Converts legal files into text for the RAG pipeline.

### `DocumentLoader._load_text(file_path)`

File:

```text
src/ingestion/document_loader.py
```

What it does:

- Reads TXT or Markdown files.

Inputs:

- `file_path`.

Returns:

- Text content.

### `DocumentLoader._load_pdf(file_path)`

File:

```text
src/ingestion/document_loader.py
```

What it does:

- Uses `pypdf` to extract text from each PDF page.

Inputs:

- `file_path`.

Returns:

- Combined text from all pages.

### `DocumentLoader._load_docx(file_path)`

File:

```text
src/ingestion/document_loader.py
```

What it does:

- Uses `python-docx` to extract non-empty paragraphs from DOCX files.

Inputs:

- `file_path`.

Returns:

- Text joined with line breaks.

### `TextChunker.__init__(chunk_size, chunk_overlap)`

File:

```text
src/utils/chunker.py
```

What it does:

- Creates a text splitter with a configured chunk size and overlap.

Inputs:

- `chunk_size`
- `chunk_overlap`

Returns:

- Nothing directly; it prepares the splitter.

Where used:

- In `frontend/app.py`.

### `TextChunker.split(text)`

File:

```text
src/utils/chunker.py
```

What it does:

- Splits long text into chunks.

Inputs:

- `text`: extracted document text.

Returns:

- List of text chunks.

How it contributes:

- Makes documents searchable by smaller sections.

### `VectorStore.__init__(persist_directory, embedding_model)`

File:

```text
src/memory/vector_store.py
```

What it does:

- Connects to ChromaDB.
- Configures Ollama embeddings.
- Creates or loads the `documents` collection.

Inputs:

- `persist_directory`: where ChromaDB data is stored.
- `embedding_model`: model name for embeddings.

Returns:

- Nothing directly; creates a vector store object.

### `VectorStore.add_documents(documents, ids, metadatas=None)`

File:

```text
src/memory/vector_store.py
```

What it does:

- Adds chunks to ChromaDB.
- Optionally stores metadata such as source filename and chunk number.

Inputs:

- `documents`: list of chunk texts.
- `ids`: unique chunk IDs.
- `metadatas`: optional metadata list.

Returns:

- Nothing.

Where used:

- In `frontend/app.py` after chunking an uploaded document.

How it contributes:

- Builds the searchable document index used by the RAG pipeline.

### `VectorStore.query(query_text, n_results=3)`

File:

```text
src/memory/vector_store.py
```

What it does:

- Retrieves relevant document chunks.

Inputs:

- `query_text`: user question.
- `n_results`: number of chunks to retrieve.

Returns:

- List of chunk texts.

Notes:

- This is the original simpler retrieval method.
- It is kept for compatibility.

### `VectorStore.query_with_sources(query_text, n_results=4)`

File:

```text
src/memory/vector_store.py
```

What it does:

- Retrieves relevant chunks plus metadata.

Inputs:

- `query_text`: user question.
- `n_results`: number of chunks to retrieve.

Returns:

- List of dictionaries with:
  - `text`
  - `source`
  - `chunk`
  - `distance`

Where used:

- In `frontend/app.py` when the user asks a question.

How it contributes:

- Enables source-grounded legal answers.

### `LLM.__init__(model_name, system_prompt, temperature)`

File:

```text
src/models/llm.py
```

What it does:

- Stores the model name, system prompt, and temperature.

Inputs:

- `model_name`
- `system_prompt`
- `temperature`

### `LLM.generate(question, context, history=None)`

File:

```text
src/models/llm.py
```

What it does:

- Builds a message list for Ollama.
- Includes system prompt.
- Includes recent conversation history.
- Includes retrieved context.
- Sends everything to Ollama.
- Returns the model answer.

Inputs:

- `question`: user question.
- `context`: retrieved source-labelled chunks.
- `history`: previous conversation turns.

Returns:

- Assistant answer as text.

Where used:

- In `frontend/app.py`.

How it contributes:

- This is the final generation step of the RAG pipeline.

### `ConversationHistory.__init__(path)`

File:

```text
src/memory/conversation_history.py
```

What it does:

- Sets the chat history path.
- Creates an empty JSON file if it does not exist.

Inputs:

- Optional path, default `data/chat_history.json`.

### `ConversationHistory.load_all()`

What it does:

- Loads all chat data from JSON.

Returns:

- Dictionary of all chats.

### `ConversationHistory.get_chat_ids()`

What it does:

- Returns all conversation IDs.

Used in:

- Sidebar conversation selector.

### `ConversationHistory.load_history(chat_id)`

What it does:

- Loads the message history for one conversation.

Inputs:

- `chat_id`

Returns:

- List of previous question/answer turns.

### `ConversationHistory.save_interaction(chat_id, question, answer)`

What it does:

- Saves one user question and assistant answer.

Inputs:

- `chat_id`
- `question`
- `answer`

### `ConversationHistory.create_new_chat()`

What it does:

- Creates a new chat ID such as `chat_1`, `chat_2`, etc.

Returns:

- New chat ID.

### `load_config(path="config/config.yaml")`

File:

```text
src/utils/config_loader.py
```

What it does:

- Reads the YAML config file.

Returns:

- A Python dictionary with config settings.

### `requires_human_review(question, retrieved_text="")`

File:

```text
src/utils/legal_safety.py
```

What it does:

- Checks whether the question or retrieved text contains high-risk legal keywords.

Inputs:

- `question`
- Optional `retrieved_text`

Returns:

- `True` or `False`.

Where used:

- In `frontend/app.py`.

How it contributes:

- Adds human-in-the-loop recommendation logic.

### `route_legal_service(question, retrieved_text="")`

File:

```text
src/utils/legal_safety.py
```

What it does:

- Suggests a likely legal service category.

Inputs:

- `question`
- Optional `retrieved_text`

Returns:

- A string such as:
  - `GDPR / data protection review`
  - `Employment law review`
  - `Commercial contract review`
  - `General SME legal triage`

Where used:

- In `frontend/app.py`.

How it contributes:

- Makes the app more like a legal services workflow, not only a chatbot.

## 6. Frontend / Streamlit App Explanation

### Where the App Is Created

The Streamlit app is created in:

```text
frontend/app.py
```

To run it:

```bash
streamlit run frontend/app.py
```

### Page Setup

The app page is configured with:

- Page title: `AI Legal Assistant for SMEs`
- Icon: scales symbol
- Wide layout
- Expanded sidebar

### Main Page

The main page shows:

- App title.
- Portugal/EU SME positioning.
- Legal disclaimer.
- Short explanation of what the prototype does.
- Chat area.
- Example questions.

### Sidebar

The sidebar contains:

- Document upload section.
- Suggested workflows.
- System information.
- Conversation selector.
- New chat button.
- Clear current chat button.
- Delete chat button.

### Upload Section

The upload section is created with `st.file_uploader`.

It accepts:

- TXT
- PDF
- Markdown
- DOCX

When a user uploads a file:

1. The file is saved to `data/raw/`.
2. The document loader extracts text.
3. The chunker splits the text.
4. The vector store embeds and saves the chunks.
5. The app shows a success message with the number of chunks stored.

### Legal Disclaimer

The legal disclaimer appears near the top of the main page using `st.info`.

The disclaimer text comes from:

```text
config/config.yaml
```

This makes it easy to change without editing Python code.

### Buttons

The app has these buttons:

- `New Chat`
  - Creates a new conversation ID.

- `Clear Current Chat`
  - Removes all turns from the selected conversation.

- `Delete Chat`
  - Deletes the selected conversation from chat history.

### Chat Section

The chat input uses:

```python
st.chat_input(...)
```

When the user sends a question:

1. The question appears as a user message.
2. The vector store retrieves relevant chunks.
3. The retrieved chunks are formatted as sources.
4. The LLM generates an answer.
5. Safety footer is added.
6. The answer is displayed.
7. The conversation is saved.
8. Retrieved sources are shown in an expander.

### Source Display

Sources are displayed in:

```text
Retrieved sources
```

Each source shows:

- Source number.
- File name.
- Chunk number.
- Retrieved text.
- Retrieval distance, when available.

This is important because legal answers must be auditable.

### Conversation History

Conversation history is stored using:

```text
src/memory/conversation_history.py
```

The user can select previous conversations from the sidebar.

### UI Changes From Previous Project

The previous UI was a generic RAG assistant.

The new UI:

- Uses legal assistant branding.
- Adds legal disclaimer.
- Adds SME legal workflows.
- Uses legal examples.
- Shows source grounding.
- Adds service routing.
- Adds human-review warning.

## 7. RAG Pipeline Explanation

### Step 1: User Uploads a Document

The user uploads a legal or compliance document through the Streamlit sidebar.

### Step 2: The System Reads the Document

`DocumentLoader` checks the file extension and extracts text.

### Step 3: The Document Is Chunked

`TextChunker` splits the text into smaller overlapping pieces.

Current config:

```yaml
chunk_size: 450
chunk_overlap: 80
```

### Step 4: Embeddings Are Created

The vector store uses Ollama embeddings:

```yaml
embedding model: nomic-embed-text
```

Each chunk becomes a numerical vector.

### Step 5: Chunks Are Stored

Chunks are stored in ChromaDB inside:

```text
data/vector_store/
```

Each chunk also stores metadata:

- Source file name.
- Chunk number.
- Document type.

### Step 6: User Asks a Question

The user writes a question in the chat input.

Example:

```text
What are the main risks in this contract?
```

### Step 7: Relevant Chunks Are Retrieved

The system searches ChromaDB for chunks most semantically similar to the question.

### Step 8: Prompt Is Built

The app formats retrieved chunks as labelled sources:

```text
Source [1] - supplier_contract.pdf | chunk 3:
...
```

These sources are sent to the LLM along with the user question.

### Step 9: LLM Generates an Answer

The LLM is:

```yaml
phi3:mini
```

It runs through Ollama.

Temperature:

```yaml
0.1
```

Low temperature is used because legal/compliance answers should be stable and not overly creative.

### Step 10: Answer Is Returned With Source Grounding

The answer is shown in the chat.

The app also shows retrieved sources so the user can inspect what the model relied on.

## 8. Legal Services Adaptation

### Legal Services Wording

The app now uses language such as:

- Legal triage.
- Compliance support.
- Contract review.
- GDPR obligations.
- Employment-law triage.
- Lawyer handoff checklist.

### SME-Focused Use Cases

The app supports use cases such as:

- Summarizing contracts.
- Identifying risky clauses.
- Checking GDPR mentions.
- Finding missing contract information.
- Preparing questions for a lawyer.
- Understanding employment document risks.

### Legal Disclaimer

The app clearly states:

- It does not provide definitive legal advice.
- It is not a substitute for a licensed lawyer.
- It should not be the only basis for legal decisions.

### Hallucination Mitigation

The legal prompt says:

- Use only retrieved context.
- Do not invent legal rules.
- Say when context is insufficient.
- Cite source labels.
- Recommend human legal review for risky matters.

### Source-Grounded Answering

The system retrieves sources and labels them.

The LLM is instructed to cite these source labels.

### Human-In-The-Loop Recommendation

The app has simple keyword-based logic that flags high-risk topics.

Examples:

- Court.
- Fine.
- Penalty.
- Dismissal.
- GDPR violation.
- Signing.
- Tax.
- Data breach.

If these appear, the app recommends human legal review.

### Risk Identification Logic

The current risk logic is lightweight.

It is not a full legal risk scoring engine yet.

It currently:

- Detects high-risk keywords.
- Suggests a legal service route.
- Adds a human-review warning when needed.

## 9. Safety, Privacy, and Hallucination Controls

### How the System Avoids Hallucinations

The system reduces hallucinations by:

- Using RAG instead of only asking a general LLM.
- Sending retrieved document chunks to the model.
- Using a strict legal system prompt.
- Showing sources to the user.
- Using low temperature.
- Refusing when no relevant context is found.

### What Happens When Context Is Insufficient

If no relevant documents are retrieved, the app says it cannot answer safely based on the uploaded or indexed documents.

It asks the user to upload relevant documents or consult a lawyer.

### Does the Model Avoid Inventing Legal Advice?

The prompt tells the model:

- Do not invent legal rules.
- Do not provide definitive legal advice.
- Use only retrieved context.
- Recommend human legal review for high-risk cases.

This is a prompt-level control, not a perfect guarantee.

### How Legal Liability Is Reduced

The app reduces liability by:

- Showing a legal disclaimer.
- Positioning the product as triage, not legal advice.
- Recommending human review.
- Displaying retrieved sources.
- Avoiding claims of definitive compliance.

### How Private SME Documents Are Handled

Current prototype:

- Stores uploaded files locally in `data/raw/`.
- Stores embeddings locally in `data/vector_store/`.
- Uses local Ollama models.

Privacy assumption:

- Documents are processed locally, not sent to an external LLM API.

Production would need:

- Authentication.
- Tenant isolation.
- Encryption.
- Access control.
- Deletion policy.
- Audit logging.

## 10. Business Plan Connection

### Why the Business Plan Matters for the Code

The code should support the business model your group chooses.

For example, if the product is a SaaS app for SMEs, the code may eventually need:

- User accounts.
- Usage limits.
- Subscription tiers.
- Document limits.
- Customer workspaces.

If the product is a law firm partnership tool, the code may need:

- Lawyer dashboard.
- Case escalation.
- Review status.
- Notes for lawyers.

### Business Plan Items That Affect Code

The business plan affects:

- Target users.
- Main workflows.
- Pricing tiers.
- Usage limits.
- Which legal topics matter most.
- Whether lawyers are inside the product flow.
- Whether the demo should show only SME users or also lawyer users.
- Whether risk scoring should be included.
- Whether multilingual support is needed.

### Assumptions Currently in the Code

The current code assumes:

- The product is mainly for SMEs.
- The app is B2B SaaS-style.
- The main use cases are contracts, GDPR, employment, and compliance.
- The app should recommend escalation to lawyers.
- The prototype can use local models with Ollama.
- The app focuses on explanations and triage, not binding legal advice.
- Risk logic is simple and keyword-based.

### Assumptions in Docs That Should Match the Business Plan

The docs currently assume:

- Free/basic, Starter, Professional, and Premium tiers.
- Human-in-the-loop review can be a premium feature.
- Portugal/EU legal focus.
- SME target market.
- Possible partnerships with law firms, accounting firms, and consultants.
- Local/open-source models are useful for privacy.

### Checklist of Questions for the Business Plan Team

Ask your group:

- What is the final product name: AI Legal Assistant for SMEs, LexAI Portugal, or another name?
- Are we targeting Portugal only, or Portugal plus the EU?
- Who is the primary buyer: SME owner, operations manager, accountant, consultant, or law firm?
- What are the top three use cases: contracts, GDPR, employment, or something else?
- What pricing model are we using: SaaS, pay-per-document, law firm referral, or white-label?
- What are the final pricing tiers?
- What limits should each tier have: documents, questions, users, storage?
- Is human lawyer review included or only recommended?
- Do we need to show a lawyer escalation workflow in the demo?
- Should the app simulate risk scoring, or only explanations and warnings?
- Should the app include Portuguese-language examples?
- Should we keep the current uploaded-document-only design, or later add official Portuguese/EU legal documents as a curated knowledge base?
- Are we claiming local/private deployment as part of the value proposition?
- How strong should the privacy promise be?
- What are the main competitors listed in the business plan?
- What moat are we emphasizing most: data, workflows, partnerships, compliance, or privacy?
- Does the PowerPoint use the same terminology as the README and app?

## 11. My Role in the Final Project

### What You Are Responsible For

You are responsible for the technical prototype:

- Streamlit app.
- Document upload.
- RAG pipeline.
- Ollama integration.
- ChromaDB vector store.
- Prompt configuration.
- Source-grounded answering.
- Conversation history.
- Legal safety logic.
- Technical README/docs.
- Demo preparation.

### Technical Components You Need to Understand

You should understand:

- How documents are loaded.
- How text is chunked.
- How embeddings are created.
- How ChromaDB stores and retrieves chunks.
- How retrieved context is sent to the LLM.
- How Ollama is used.
- How the Streamlit UI works.
- How source citations are shown.
- How human-review warnings work.
- How configuration is loaded.

### What You Should Explain in the Presentation

You should explain:

- Why the project uses RAG.
- Why this is safer than a generic chatbot.
- How documents move through the pipeline.
- How the app grounds answers in sources.
- Why local models help privacy.
- What legal safety controls exist.
- What is still prototype-level.

### What You Should Demo Live

Recommended live demo:

1. Open the Streamlit app.
2. Show the legal disclaimer.
3. Upload a sample contract or legal document.
4. Ask: "Can you summarize this contract in simple language?"
5. Show retrieved sources.
6. Ask: "What are the main risks before signing?"
7. Show human legal review recommendation.
8. Show conversation history.

### Questions the Professor or AI Judge May Ask

Possible questions:

- Why is this not just ChatGPT?
- What happens if the answer is not in the documents?
- How do you prevent hallucinations?
- Why use RAG?
- Why use local models?
- Where are documents stored?
- Is this legal advice?
- Who is liable if the model is wrong?
- How do you update legal knowledge?
- How does the app decide when to recommend a lawyer?
- What are the limitations of keyword-based risk detection?
- How would this scale to multiple SMEs?

### Technical Risks You Should Defend

Important risks:

- Retrieved context may be incomplete.
- The LLM may still hallucinate.
- Legal knowledge can become outdated.
- Keyword-based risk detection is basic.
- The prototype does not yet have authentication.
- The prototype does not yet isolate users/companies.
- The vector database is local and not production multi-tenant.

### What to Improve First If Time Is Limited

Top priorities:

1. Add a few realistic sample legal documents for demo.
2. Make sure the app runs cleanly from the new repo.
3. Align wording with the group PowerPoint.
4. Add Portuguese/EU-specific sample questions.
5. Improve source citation reliability.
6. Add a simple risk score or checklist output if the business plan promises it.

## 12. Presentation / Viva Explanation

### 30-Second Technical Explanation

This project is a Streamlit RAG application for SME legal triage. Users upload contracts or compliance documents, and the system uses local Ollama models plus ChromaDB to retrieve relevant document sections and answer questions with source grounding. The goal is not to replace lawyers, but to help SMEs understand documents, identify risks, and know when professional legal review is needed.

### 1-Minute RAG Pipeline Explanation

When a user uploads a document, the system extracts the text, splits it into smaller chunks, creates embeddings with the `nomic-embed-text` Ollama model, and stores those chunks in ChromaDB. When the user asks a question, the system embeds the question, searches for the most relevant chunks, formats them as labelled sources, and sends them to the `phi3:mini` Ollama LLM. The LLM answers using the retrieved context, and the app displays both the answer and the sources.

### 1-Minute Full-Stack Prototype Explanation

The frontend is built in Streamlit and includes document upload, chat, source display, legal disclaimer, and conversation selection. The backend is a set of Python modules for document loading, chunking, vector storage, LLM generation, conversation history, and safety logic. The app is deployable as a Streamlit prototype and uses local models, which supports privacy for sensitive SME legal documents.

### Why This Is Not Just a ChatGPT Wrapper

This is not just a generic chatbot because it has:

- Document upload and parsing.
- Persistent vector database.
- Retrieval-grounded answers.
- Source display.
- Legal-specific prompts.
- SME legal workflows.
- Human-review recommendation logic.
- Business documentation and AI unit economics.
- Evaluation tests for hallucination and retrieval.

The value is in the legal workflow and private document grounding, not only in the LLM.

### How the System Handles Hallucinations

The system reduces hallucinations by forcing the model to answer from retrieved sources. If no relevant context is retrieved, the app says it cannot answer safely. The prompt tells the model not to invent legal rules and to recommend lawyer review for risky matters. The user can also inspect the retrieved sources.

### How the System Connects to the Business Model

The technical system supports a SaaS legal assistant for SMEs. Basic users could get limited document checks, while paid tiers could get more uploads, more questions, compliance checklists, document history, and human lawyer review. Local models and usage limits help control AI costs.

## 13. Current Weaknesses and Next Steps

### What Is Already Well Implemented

- Clean RAG pipeline.
- Streamlit frontend.
- Multi-format document upload.
- Local Ollama model usage.
- Persistent ChromaDB vector store.
- Conversation history.
- Legal prompt and disclaimer.
- Source metadata retrieval.
- Human-review warning logic.
- Strong documentation structure.
- Evaluation files.

### What Is Missing

- GitHub remote is not configured yet.
- No production authentication.
- No multi-tenant SME workspace separation.
- No fixed curated legal knowledge base included yet; the current prototype is intentionally grounded in uploaded/indexed documents.
- No advanced clause extraction.
- No structured risk score.
- No lawyer dashboard.
- No full automated test suite requiring Ollama.
- No production deployment config.

### What Is Weak

- Human-review detection is keyword-based.
- Source citation depends on LLM following instructions.
- Legal quality depends on uploaded documents.
- The app cannot guarantee current law.
- Uploaded documents are local files, not secure tenant storage.
- No user roles or permissions.

### What the AI Judge Could Attack

- "This is just a wrapper."
- "The legal risk logic is too simple."
- "Why did you choose uploaded-document RAG instead of a fixed trusted legal knowledge base?"
- "How do you prevent hallucinations?"
- "Who is liable for wrong advice?"
- "How do you handle private legal documents?"
- "How do you scale to many SMEs?"
- "What is the moat?"

### Must Fix Before Submission

- Push the repo to GitHub.
- Align the app name with the final business plan/PPT.
- Add or prepare realistic demo documents.
- Test the app live from the new repository.
- Fill in the GenAI transparency log with your real workflow.
- Make sure README and PowerPoint tell the same story.

### Should Improve If Time Allows

- Add simple structured risk score.
- Add a lawyer handoff checklist button or prompt template.
- Add Portuguese sample questions.
- Add a small curated knowledge base folder if the final business plan requires general legal guidance without uploads.
- Add more tests for safety behavior.
- Add screenshots to README.

### Nice to Have

- User authentication.
- Multi-tenant workspaces.
- Lawyer dashboard.
- Exportable PDF report.
- Clause extraction table.
- Document comparison.
- Deployment configuration.

## 14. Final Deliverable Checklist

### Code

- [ ] Run the Streamlit app from the new repo.
- [ ] Test document upload.
- [ ] Test chat questions.
- [ ] Test source display.
- [ ] Test conversation history.
- [ ] Confirm Ollama models are installed.

### UI

- [ ] Confirm final product name.
- [ ] Check legal disclaimer wording.
- [ ] Check sidebar workflows.
- [ ] Prepare a clean demo flow.

### GitHub

- [ ] Create GitHub repository.
- [ ] Add remote origin.
- [ ] Push `main`.
- [ ] Confirm repository appears on GitHub.
- [ ] Decide whether to commit this technical report.

### README

- [ ] Align README with final business plan.
- [ ] Confirm run instructions.
- [ ] Add any final screenshots if desired.

### Business Plan Alignment

- [ ] Confirm pricing tiers.
- [ ] Confirm target user.
- [ ] Confirm final use cases.
- [ ] Confirm human-in-the-loop strategy.
- [ ] Confirm moat wording.

### GenAI Transparency Logs

- [ ] Add all AI tool usage.
- [ ] Add coding prompts.
- [ ] Add debugging prompts.
- [ ] Add business/documentation prompts.
- [ ] Mark accepted/edited/rejected outputs.

### Evaluation Tests

- [ ] Prepare sample documents.
- [ ] Run sample questions.
- [ ] Run hallucination tests.
- [ ] Save observations.

### Demo Preparation

- [ ] Choose one contract document.
- [ ] Choose one GDPR/compliance document.
- [ ] Prepare 3-5 demo questions.
- [ ] Practice showing retrieved sources.
- [ ] Practice explaining human-review warning.

### Presentation Preparation

- [ ] Memorize the 30-second technical explanation.
- [ ] Memorize the 1-minute RAG explanation.
- [ ] Prepare answers for hallucination and liability questions.
- [ ] Prepare answers for "why not just ChatGPT?"
- [ ] Prepare answers for privacy and scaling questions.
