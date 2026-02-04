"""
LLM Adapter

Provides a model-agnostic interface for interacting with different
LLM providers (OpenAI, Claude, Azure OpenAI).
"""

from abc import ABC, abstractmethod
from typing import Optional
from .config_loader import ConfigLoader


class BaseLLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt/question.
            system_prompt: Optional system prompt for context.
            
        Returns:
            Generated text response.
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        pass


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        """
        Initialize OpenAI adapter.
        
        Args:
            api_key: OpenAI API key.
            model: Model name to use.
        """
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    def get_model_name(self) -> str:
        return f"OpenAI {self.model}"


class ClaudeAdapter(BaseLLMAdapter):
    """Adapter for Anthropic Claude API."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Claude adapter.
        
        Args:
            api_key: Anthropic API key.
            model: Model name to use.
        """
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Claude."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt or "You are a helpful documentation generator.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def get_model_name(self) -> str:
        return f"Claude {self.model}"


class AzureOpenAIAdapter(BaseLLMAdapter):
    """Adapter for Azure OpenAI API."""
    
    def __init__(
        self, 
        api_key: str, 
        endpoint: str, 
        deployment: str,
        api_version: str = "2024-02-15-preview"
    ):
        """
        Initialize Azure OpenAI adapter.
        
        Args:
            api_key: Azure OpenAI API key.
            endpoint: Azure OpenAI endpoint URL.
            deployment: Deployment name.
            api_version: API version.
        """
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment = deployment
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Azure OpenAI."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    def get_model_name(self) -> str:
        return f"Azure OpenAI {self.deployment}"


class LLMFactory:
    """Factory for creating LLM adapters based on configuration."""
    
    @staticmethod
    def create(config: ConfigLoader) -> BaseLLMAdapter:
        """
        Create an LLM adapter based on configuration.
        
        Args:
            config: Configuration loader with LLM settings.
            
        Returns:
            Appropriate LLM adapter instance.
            
        Raises:
            ValueError: If provider is unknown or not configured.
        """
        provider = config.llm_provider
        
        if provider == "openai":
            return OpenAIAdapter(
                api_key=config.openai_api_key,
                model=config.openai_model
            )
        
        elif provider == "claude":
            return ClaudeAdapter(
                api_key=config.claude_api_key,
                model=config.claude_model
            )
        
        elif provider == "azure":
            return AzureOpenAIAdapter(
                api_key=config.azure_openai_api_key,
                endpoint=config.azure_openai_endpoint,
                deployment=config.azure_openai_deployment,
                api_version=config.azure_openai_api_version
            )
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
