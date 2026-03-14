"""LLM service for text generation and embeddings."""
import os
from typing import Optional


class LLMService:
    """Service for LLM interactions."""

    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self._client = None

    def _get_client(self):
        """Get LLM client based on provider."""
        if self._client is not None:
            return self._client

        if self.provider == "anthropic":
            import anthropic

            self._client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        elif self.provider == "openai":
            import openai

            self._client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )

        return self._client

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        response_format: dict | None = None,
    ) -> str:
        """Generate text using LLM."""
        client = self._get_client()

        # Map model names
        if model is None:
            model = "claude-sonnet-4-20250514" if self.provider == "anthropic" else "gpt-4o"

        kwargs = {
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if response_format:
            kwargs["response_format"] = response_format

        if self.provider == "anthropic":
            kwargs["model"] = model
            message = client.messages.create(
                system="You are a helpful academic research assistant.",
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return message.content[0].text
        else:
            kwargs["model"] = model
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content

    async def get_embedding(self, text: str, model: str | None = None) -> list[float]:
        """Get embedding for text."""
        client = self._get_client()

        if model is None:
            model = "text-embedding-3-large"

        if self.provider == "openai":
            response = client.embeddings.create(
                model=model,
                input=text,
            )
            return response.data[0].embedding
        else:
            # Anthropic doesn't have embeddings, use OpenAI
            import openai

            openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = openai_client.embeddings.create(
                model="text-embedding-3-large",
                input=text,
            )
            return response.data[0].embedding

    async def classify_text(self, text: str, classes: list[str]) -> str:
        """Classify text into one of the provided classes."""
        classes_str = ", ".join(classes)
        prompt = f"""Classify the following text into one of these categories: {classes_str}

Text: {text}

Return only the category name, nothing else."""

        result = await self.generate(prompt, max_tokens=50)
        return result.strip()


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get singleton LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
