"""
LLM Module

Handles interaction with the local language model via Ollama.
"""

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
