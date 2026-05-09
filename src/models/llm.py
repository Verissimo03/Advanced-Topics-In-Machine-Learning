"""
LLM Module

Handles interaction with the local language model via Ollama.
"""

import json

import ollama


class LLM:
    """
    Wrapper for the local Ollama language model.
    """

    def __init__(
        self,
        model_name: str,
        system_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 450,
        history_turns: int = 2,
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history_turns = history_turns

    def generate(self, question: str, context: list[str], history: list = None) -> str:
        """
        Generate an answer using retrieved context and conversation history.
        """

        context_text = "\n\n".join(context)

        messages = []

        # system prompt from config.yaml
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })

        # conversation history
        if history:
            for turn in history[-self.history_turns:]:
                messages.append({"role": "user", "content": turn["question"]})
                answer = turn["answer"]
                if len(answer) > 700:
                    answer = f"{answer[:700]}..."
                messages.append({"role": "assistant", "content": answer})

        # user query with context ONLY (no extra rules here)
        messages.append({
            "role": "user",
            "content": f"""
Context:
{context_text}

Question:
{question}
"""
        })

        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            options={
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        )

        return response["message"]["content"]

    def assess_context(self, question: str, retrieved_items: list[dict]) -> dict:
        """
        Assess whether retrieved chunks are relevant and sufficient.

        This step prevents the assistant from answering unsupported questions
        just because the vector store returned weakly related chunks.
        """

        source_blocks = []
        for index, item in enumerate(retrieved_items, start=1):
            source_type = item.get("source_type_label", "Uploaded document")
            source = item.get("source", "Unknown source")
            chunk = item.get("chunk", index)
            text = item.get("text", "")
            source_blocks.append(
                f"Source [{index}] - {source_type}: {source} | chunk {chunk}\n{text}"
            )

        prompt = f"""
You are a strict relevance and safety classifier for an SME legal/compliance RAG assistant.

Supported domain:
- contract analysis
- GDPR/data protection
- employment-law document triage
- SME compliance
- legal risk identification
- missing information in legal/business documents
- lawyer handoff recommendations
- general legal services triage for SMEs in Portugal/EU

Unsupported domain:
- geopolitics
- medical advice
- sports
- general trivia
- questions unrelated to the retrieved legal/compliance documents or legal knowledge base

Decision rules:
- Judge semantic relevance, not only keyword overlap.
- Broad contract-review questions can be relevant to an uploaded contract even if the exact words are not in the document.
- A general legal/GDPR guidance question requires a relevant Legal knowledge base source. Do not use an unrelated uploaded contract as general legal guidance.
- If sources are partially relevant, allow a limited answer only for what the sources support.
- Do not rely on the model's internal legal knowledge.

Return only valid JSON with this schema:
{{
  "domain_relevance": "supported" or "unsupported",
  "source_relevance": "relevant" or "partially_relevant" or "not_relevant",
  "context_sufficiency": "sufficient" or "insufficient",
  "answer_mode": "summarize_document" or "identify_risks" or "gdpr_data_protection_review" or "missing_information_scan" or "lawyer_handoff_recommendation" or "general_sme_compliance_guidance" or "refuse",
  "usable_source_numbers": [1, 2],
  "human_review_recommended": true or false,
  "reason": "short explanation"
}}

User question:
{question}

Retrieved sources:
{chr(10).join(source_blocks)}
"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format="json",
                options={
                    "temperature": 0,
                    "num_predict": 220,
                },
            )
            assessment = json.loads(response["message"]["content"])
        except Exception:
            return {
                "domain_relevance": "unsupported",
                "source_relevance": "not_relevant",
                "context_sufficiency": "insufficient",
                "answer_mode": "refuse",
                "usable_source_numbers": [],
                "human_review_recommended": True,
                "reason": "The relevance assessment could not be completed safely.",
            }

        assessment.setdefault("domain_relevance", "unsupported")
        assessment.setdefault("source_relevance", "not_relevant")
        assessment.setdefault("context_sufficiency", "insufficient")
        assessment.setdefault("answer_mode", "refuse")
        assessment.setdefault("usable_source_numbers", [])
        assessment.setdefault("human_review_recommended", False)
        assessment.setdefault("reason", "")

        return assessment
