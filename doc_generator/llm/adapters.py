"""Model-agnostic LLM adapter layer.

Design decision: Each LLM provider is wrapped in a thin adapter that
implements a common interface. The factory reads the provider name and
model from project_config.yml (via ConfigLoader) and all runtime
parameters (max_tokens, temperature) from the same config. No model
names, tokens, or temperatures are hardcoded in this module.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from ..config import ConfigLoader

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """Abstract interface for all LLM adapters."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send a prompt and return the generated text.

        Args:
            prompt: User / task prompt.
            system_prompt: Optional system-level instruction.

        Returns:
            Generated text string.
        """

    @abstractmethod
    def get_model_name(self) -> str:
        """Return a human-readable model identifier."""


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for the OpenAI Chat Completions API.

    Design decision: The ``openai`` library is imported inside __init__
    so it is only required when this adapter is actually selected.
    """

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"OpenAI {self._model}"


class ClaudeAdapter(BaseLLMAdapter):
    """Adapter for the Anthropic Messages API."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def get_model_name(self) -> str:
        return f"Claude {self._model}"


class AzureOpenAIAdapter(BaseLLMAdapter):
    """Adapter for Azure OpenAI Service."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment: str,
        api_version: str,
        max_tokens: int,
        temperature: float,
    ):
        from openai import AzureOpenAI

        self._client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        self._deployment = deployment
        self._max_tokens = max_tokens
        self._temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content

    def get_model_name(self) -> str:
        return f"Azure OpenAI {self._deployment}"


class LLMFactory:
    """Create an LLM adapter from configuration.

    Design decision: The factory reads provider, model, max_tokens, and
    temperature from ConfigLoader (which reads project_config.yml), and
    API keys from environment variables (loaded from .env). This keeps
    all tuning knobs in the YAML and all secrets in the env file.
    """

    @staticmethod
    def create(config: ConfigLoader) -> BaseLLMAdapter:
        """Instantiate the appropriate adapter.

        Args:
            config: Validated ConfigLoader instance.

        Returns:
            A concrete BaseLLMAdapter.

        Raises:
            ValueError: If the configured provider is not supported.
        """
        provider = config.llm_provider
        model = config.llm_model
        max_tokens = config.llm_max_tokens
        temperature = config.llm_temperature

        if provider == "openai":
            return OpenAIAdapter(
                api_key=config.openai_api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        elif provider == "claude":
            return ClaudeAdapter(
                api_key=config.anthropic_api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        elif provider == "azure":
            return AzureOpenAIAdapter(
                api_key=config.azure_openai_key,
                endpoint=config.azure_openai_endpoint,
                deployment=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
