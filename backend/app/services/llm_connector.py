"""
LLM Connector Service
Provides unified interface for multiple AI models with caching and error handling
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiofiles
import httpx
from pydantic import BaseModel

from app.services.error_handling import call_api_with_retry, APIError
from app.services.cache_service import cache_result

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"
    GOOGLE = "google"

@dataclass
class ModelConfig:
    provider: ModelProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30

@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0
    cached: bool = False

class LLMConnector:
    def __init__(self):
        self.clients = {}
        self.model_configs = {}
        self.cache_ttl = 3600  # 1 hour
        self.rate_limits = {}
        
    async def initialize_client(self, config: ModelConfig):
        """Initialize client for a specific model provider"""
        if config.provider == ModelProvider.OPENAI:
            await self._init_openai_client(config)
        elif config.provider == ModelProvider.ANTHROPIC:
            await self._init_anthropic_client(config)
        elif config.provider == ModelProvider.LOCAL:
            await self._init_local_client(config)
        elif config.provider == ModelProvider.AZURE:
            await self._init_azure_client(config)
        elif config.provider == ModelProvider.GOOGLE:
            await self._init_google_client(config)
        
        self.model_configs[config.model_name] = config

    async def _init_openai_client(self, config: ModelConfig):
        """Initialize OpenAI client"""
        try:
            import openai
            client = openai.AsyncOpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
            self.clients[config.model_name] = {
                "client": client,
                "provider": ModelProvider.OPENAI
            }
            logger.info(f"OpenAI client initialized for model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def _init_anthropic_client(self, config: ModelConfig):
        """Initialize Anthropic client"""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(
                api_key=config.api_key,
                base_url=config.base_url
            )
            self.clients[config.model_name] = {
                "client": client,
                "provider": ModelProvider.ANTHROPIC
            }
            logger.info(f"Anthropic client initialized for model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise

    async def _init_local_client(self, config: ModelConfig):
        """Initialize local model client"""
        try:
            # This would connect to a local model server (e.g., Ollama, vLLM)
            client = httpx.AsyncClient(
                base_url=config.base_url or "http://localhost:11434",
                timeout=config.timeout
            )
            self.clients[config.model_name] = {
                "client": client,
                "provider": ModelProvider.LOCAL
            }
            logger.info(f"Local client initialized for model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize local client: {e}")
            raise

    async def _init_azure_client(self, config: ModelConfig):
        """Initialize Azure OpenAI client"""
        try:
            import openai
            client = openai.AsyncAzureOpenAI(
                api_key=config.api_key,
                azure_endpoint=config.base_url,
                api_version="2024-02-15-preview"
            )
            self.clients[config.model_name] = {
                "client": client,
                "provider": ModelProvider.AZURE
            }
            logger.info(f"Azure client initialized for model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure client: {e}")
            raise

    async def _init_google_client(self, config: ModelConfig):
        """Initialize Google AI client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config.api_key)
            client = genai.GenerativeModel(config.model_name)
            self.clients[config.model_name] = {
                "client": client,
                "provider": ModelProvider.GOOGLE
            }
            logger.info(f"Google client initialized for model: {config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Google client: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True
    ) -> LLMResponse:
        """Generate text using specified model"""
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(prompt, model_name, system_prompt, temperature, max_tokens)
            cached_response = await cache_result.get(cache_key)
            if cached_response:
                return LLMResponse(
                    content=cached_response["content"],
                    model=model_name,
                    usage=cached_response.get("usage"),
                    finish_reason=cached_response.get("finish_reason"),
                    response_time=time.time() - start_time,
                    cached=True
                )
        
        # Get model config
        config = self.model_configs.get(model_name)
        if not config:
            raise ValueError(f"Model {model_name} not configured")
        
        # Use provided parameters or defaults
        temp = temperature or config.temperature
        tokens = max_tokens or config.max_tokens
        
        try:
            # Generate response based on provider
            if config.provider == ModelProvider.OPENAI:
                response = await self._generate_openai_text(prompt, model_name, system_prompt, temp, tokens)
            elif config.provider == ModelProvider.ANTHROPIC:
                response = await self._generate_anthropic_text(prompt, model_name, system_prompt, temp, tokens)
            elif config.provider == ModelProvider.LOCAL:
                response = await self._generate_local_text(prompt, model_name, system_prompt, temp, tokens)
            elif config.provider == ModelProvider.AZURE:
                response = await self._generate_azure_text(prompt, model_name, system_prompt, temp, tokens)
            elif config.provider == ModelProvider.GOOGLE:
                response = await self._generate_google_text(prompt, model_name, system_prompt, temp, tokens)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
            
            # Cache response
            if use_cache:
                cache_key = self._generate_cache_key(prompt, model_name, system_prompt, temperature, max_tokens)
                await cache_result.set(
                    cache_key,
                    {
                        "content": response.content,
                        "usage": response.usage,
                        "finish_reason": response.finish_reason
                    },
                    ttl=self.cache_ttl
                )
            
            response.response_time = time.time() - start_time
            return response
            
        except Exception as e:
            logger.error(f"Text generation failed for model {model_name}: {e}")
            raise APIError(f"Text generation failed: {str(e)}")

    async def _generate_openai_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate text using OpenAI"""
        client_info = self.clients[model_name]
        client = client_info["client"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await call_api_with_retry(
            client.chat.completions.create,
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model_name,
            usage=response.usage.dict() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )

    async def _generate_anthropic_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate text using Anthropic"""
        client_info = self.clients[model_name]
        client = client_info["client"]
        
        response = await call_api_with_retry(
            client.messages.create,
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return LLMResponse(
            content=response.content[0].text,
            model=model_name,
            usage=response.usage.dict() if response.usage else None,
            finish_reason=response.stop_reason
        )

    async def _generate_local_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate text using local model"""
        client_info = self.clients[model_name]
        client = client_info["client"]
        
        # Format for Ollama API
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = await call_api_with_retry(
            client.post,
            "/api/generate",
            json=payload
        )
        
        response_data = response.json()
        
        return LLMResponse(
            content=response_data["response"],
            model=model_name,
            usage={
                "prompt_tokens": response_data.get("prompt_eval_count", 0),
                "completion_tokens": response_data.get("eval_count", 0),
                "total_tokens": response_data.get("prompt_eval_count", 0) + response_data.get("eval_count", 0)
            }
        )

    async def _generate_azure_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate text using Azure OpenAI"""
        client_info = self.clients[model_name]
        client = client_info["client"]
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await call_api_with_retry(
            client.chat.completions.create,
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model_name,
            usage=response.usage.dict() if response.usage else None,
            finish_reason=response.choices[0].finish_reason
        )

    async def _generate_google_text(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate text using Google AI"""
        client_info = self.clients[model_name]
        client = client_info["client"]
        
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await call_api_with_retry(
            client.generate_content,
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        
        return LLMResponse(
            content=response.text,
            model=model_name,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0
            }
        )

    def _generate_cache_key(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> str:
        """Generate cache key for the request"""
        import hashlib
        
        key_data = {
            "prompt": prompt,
            "model": model_name,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"llm:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        models = []
        
        for model_name, config in self.model_configs.items():
            models.append({
                "name": model_name,
                "provider": config.provider.value,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            })
        
        return models

    async def test_connection(self, model_name: str) -> bool:
        """Test connection to a specific model"""
        try:
            response = await self.generate_text(
                prompt="Hello, this is a test message.",
                model_name=model_name,
                max_tokens=10,
                use_cache=False
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed for {model_name}: {e}")
            return False

    def get_rate_limit_info(self, model_name: str) -> Dict[str, Any]:
        """Get rate limit information for a model"""
        return self.rate_limits.get(model_name, {})

    async def close_connections(self):
        """Close all client connections"""
        for model_name, client_info in self.clients.items():
            try:
                if hasattr(client_info["client"], "close"):
                    await client_info["client"].close()
                elif hasattr(client_info["client"], "aclose"):
                    await client_info["client"].aclose()
            except Exception as e:
                logger.error(f"Error closing connection for {model_name}: {e}")

# Global instance
llm_connector = LLMConnector()