"""
LLM Client Abstraction
=======================

Swappable LLM client for AI analysis.
Supports OpenAI (GPT-4 Turbo, GPT-4o-mini) and Anthropic (Claude).

Usage:
    from backend.services.llm_client import get_llm
    
    llm = get_llm()
    result = llm.chat_json(messages, ResponseSchema)
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from pydantic import BaseModel


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        schema: Type[BaseModel],
        max_tokens: int = 1800
    ) -> Dict[str, Any]:
        """
        Send chat messages and get structured JSON response.
        
        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
            schema: Pydantic model class for response validation
            max_tokens: Maximum tokens in response
        
        Returns:
            Dict matching the schema
        
        Raises:
            ValidationError: If response doesn't match schema
            Exception: If API call fails
        """
        pass
    
    @abstractmethod
    def chat_text(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000
    ) -> str:
        """
        Send chat messages and get plain text response.
        
        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."}
            max_tokens: Maximum tokens in response
        
        Returns:
            Plain text response
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI client using instructor for structured outputs."""
    
    def __init__(self, model: str, api_key: str):
        """
        Initialize OpenAI client.
        
        Args:
            model: Model name (e.g., "gpt-4o-mini", "gpt-4-turbo")
            api_key: OpenAI API key
        """
        from instructor import from_openai
        from openai import OpenAI
        
        self.model = model
        self.api_key = api_key
        
        # Create instructor-wrapped client for structured outputs
        base_client = OpenAI(api_key=api_key)
        self.client = from_openai(base_client)
        
        # Separate client for text-only responses
        self.text_client = base_client
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        schema: Type[BaseModel],
        max_tokens: int = 1800
    ) -> Dict[str, Any]:
        """
        Get structured JSON response using instructor.
        
        Automatically validates against schema and retries once on error.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=schema,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent outputs
            )
            return response.model_dump()
        except Exception as e:
            # Log the error
            print(f"[LLM ERROR] First attempt failed: {e}")
            
            # Retry once with error feedback
            retry_messages = messages + [
                {
                    "role": "user",
                    "content": f"The previous response had validation errors: {str(e)}. "
                               f"Please return ONLY valid JSON matching the exact schema."
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                response_model=schema,
                messages=retry_messages,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return response.model_dump()
    
    def chat_text(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000
    ) -> str:
        """Get plain text response (for Markdown generation)."""
        response = self.text_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.5,
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """
    Anthropic Claude client (stub for future implementation).
    
    TODO: Implement when multi-agent consensus is added.
    """
    
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        raise NotImplementedError("Anthropic client not yet implemented")
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        schema: Type[BaseModel],
        max_tokens: int = 1800
    ) -> Dict[str, Any]:
        raise NotImplementedError("Anthropic client not yet implemented")
    
    def chat_text(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000
    ) -> str:
        raise NotImplementedError("Anthropic client not yet implemented")


def get_llm() -> LLMClient:
    """
    Factory function to get LLM client based on environment variables.
    
    Environment Variables:
        LLM_PROVIDER: "openai" or "anthropic"
        LLM_MODEL: Model name (e.g., "gpt-4o-mini", "claude-3-5-sonnet-20241022")
        OPENAI_API_KEY: OpenAI API key (if provider=openai)
        ANTHROPIC_API_KEY: Anthropic API key (if provider=anthropic)
    
    Returns:
        LLMClient instance
    
    Raises:
        ValueError: If provider is unsupported or credentials missing
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIClient(model=model, api_key=api_key)
    
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return AnthropicClient(model=model, api_key=api_key)
    
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. "
            f"Must be 'openai' or 'anthropic'."
        )

