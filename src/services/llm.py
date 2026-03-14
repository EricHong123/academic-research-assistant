"""LLM service for text generation and embeddings."""
import os
from typing import Optional


class LLMService:
    """Service for LLM interactions."""

    def __init__(self, provider: str = None):
        # Auto-detect provider based on available API keys
        if provider is None:
            if os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            elif os.getenv("MINIMAX_API_KEY"):
                provider = "minimax"
            else:
                provider = "openai"  # default

        self.provider = provider
        self._client = None

        # MiniMax specific settings
        self.minimax_base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        self.minimax_group_id = os.getenv("MINIMAX_GROUP_ID", "")

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
            # Use OpenAI compatible API base
            base_url = os.getenv("OPENAI_BASE_URL", None)
            self._client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=base_url,
            )
        elif self.provider == "minimax":
            import openai
            # MiniMax uses OpenAI compatible API
            self._client = openai.OpenAI(
                api_key=os.getenv("MINIMAX_API_KEY"),
                base_url=self.minimax_base_url,
            )

        return self._client

    async def generate(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        response_format: dict = None,
    ) -> str:
        """Generate text using LLM."""
        client = self._get_client()

        # Map model names
        if model is None:
            model = self._get_default_model()

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
            # OpenAI compatible (including MiniMax)
            if self.provider == "minimax" and self.minimax_group_id:
                # MiniMax requires group_id in extra body
                kwargs["extra_body"] = {
                    "group_id": self.minimax_group_id
                }

            kwargs["model"] = model
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        models = {
            "anthropic": "claude-sonnet-4-20250514",
            "openai": "gpt-4o",
            "minimax": "MiniMax-M2.5",
        }
        return models.get(self.provider, "gpt-4o")

    async def get_embedding(self, text: str, model: str = None) -> list[float]:
        """Get embedding for text."""
        client = self._get_client()

        # Use a compatible embedding model
        embedding_model = "text-embedding-3-large"

        if self.provider == "openai" or self.provider == "minimax":
            # Check if using a custom endpoint that might not support embeddings
            if self.provider == "minimax":
                # MiniMax might not have embeddings, fallback to OpenAI or skip
                # For now, try with OpenAI
                import openai
                openai_client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY") or os.getenv("MINIMAX_API_KEY"),
                )
                response = openai_client.embeddings.create(
                    model=embedding_model,
                    input=text,
                )
                return response.data[0].embedding
            else:
                response = client.embeddings.create(
                    model=embedding_model,
                    input=text,
                )
                return response.data[0].embedding
        else:
            # Anthropic doesn't have embeddings, use OpenAI
            import openai
            openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = openai_client.embeddings.create(
                model=embedding_model,
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


def get_llm_service(provider: str = None) -> LLMService:
    """Get singleton LLM service."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(provider)
    return _llm_service
