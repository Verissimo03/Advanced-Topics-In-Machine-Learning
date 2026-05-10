"""
LLM Module

Handles interaction with the configured chat model provider.
"""

import json

import ollama


class LLM:
    """
    Wrapper for Ollama or OpenAI chat models.
    """

    def __init__(
        self,
        model_name: str,
        system_prompt: str,
        provider: str = "ollama",
        temperature: float = 0.2,
        max_tokens: int = 450,
        history_turns: int = 2,
        openai_api_key: str | None = None,
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history_turns = history_turns
        self.openai_client = None

        if self.provider == "openai":
            if not openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required when model provider is openai."
                )
            from openai import OpenAI

            self.openai_client = OpenAI(api_key=openai_api_key)
        elif self.provider != "ollama":
            raise ValueError(
                f"Unsupported model provider: {provider}. Use 'ollama' or 'openai'."
            )

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
        if history and self.history_turns > 0:
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

        return self._chat(messages, temperature=self.temperature, max_tokens=self.max_tokens)

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
            if len(text) > 900:
                text = f"{text[:900]}..."
            source_blocks.append(
                f"Source [{index}] - {source_type}: {source} | chunk {chunk}\n{text}"
            )

        prompt = f"""
Classify whether an SME legal/compliance RAG assistant can answer.

Supported: contract review, GDPR/data protection, employment documents, SME compliance, legal risk, missing clauses, lawyer handoff.
Unsupported: geopolitics, medicine, sports, trivia, or unrelated questions.

Rules:
- Judge semantic relevance, not only word overlap.
- Uploaded contracts are relevant for summaries, risks, signing review, clause presence/absence, missing information, and lawyer handoff.
- General GDPR guidance needs a Legal knowledge base source, not an unrelated uploaded contract.
- Allow partial answers when sources support part of the question.
- Do not rely on model memory.

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
            content = self._chat(
                [{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=120,
                json_mode=True,
            )
            assessment = json.loads(content)
        except Exception:
            return {
                "domain_relevance": "unsupported",
                "source_relevance": "not_relevant",
                "context_sufficiency": "insufficient",
                "answer_mode": "refuse",
                "usable_source_numbers": [],
                "human_review_recommended": True,
                "reason": "The relevance assessment could not be completed safely.",
                "parse_error": True,
            }

        assessment.setdefault("domain_relevance", "unsupported")
        assessment.setdefault("source_relevance", "not_relevant")
        assessment.setdefault("context_sufficiency", "insufficient")
        assessment.setdefault("answer_mode", "refuse")
        assessment.setdefault("usable_source_numbers", [])
        assessment.setdefault("human_review_recommended", False)
        assessment.setdefault("reason", "")
        assessment["parse_error"] = False

        return assessment

    def _chat(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> str:
        """Call the active chat provider and return assistant text."""

        if self.provider == "ollama":
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            if json_mode:
                kwargs["format"] = "json"

            response = ollama.chat(**kwargs)
            return response["message"]["content"]

        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.openai_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
