import asyncio
from typing import AsyncGenerator
from google import genai
from google.genai import types as genai_types
from google.genai.errors import APIError

from aeris.ai.provider import AIProvider
from aeris.ai.types import AIRequest, AIResponse
from aeris.config.settings import settings
from aeris.logging.logger import log
from aeris.core.exceptions import ProviderError

class GeminiProvider(AIProvider):
    def __init__(self):
        self.model_name = settings.model_name
        # Initialize client. It will automatically use GEMINI_API_KEY if present in env, 
        # or we can pass it explicitly. We pass it explicitly from our validated settings.
        try:
            self.client = genai.Client(api_key=settings.api_key)
        except Exception as e:
            log.error(f"Failed to initialize Gemini Client: {e}")
            self.client = None

    def _convert_messages(self, messages) -> list:
        # Convert our core Messages to Gemini format
        formatted = []
        for msg in messages:
            # map 'system' to system instruction (usually handled separately in google-genai)
            # map 'assistant' to 'model'
            role = 'model' if msg.role == 'assistant' else 'user'
            if msg.role != 'system':
                formatted.append(
                    {"role": role, "parts": [{"text": msg.content}]}
                )
        return formatted

    async def send_message(self, request: AIRequest) -> AIResponse:
        if not self.client:
            return AIResponse(content="", error="Gemini client not initialized", is_success=False)
            
        try:
            log.debug(f"Sending request to {self.model_name}")
            contents = self._convert_messages(request.messages)
            
            config = genai_types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )
            
            if request.system_instruction:
                config.system_instruction = request.system_instruction
                
            # google-genai supports async calls via client.aio
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            
            log.debug("Received response from Gemini")
            return AIResponse(content=response.text)
            
        except APIError as e:
            log.error(f"Gemini API Error: {e}")
            return AIResponse(content="", error=f"API Error: {str(e)}", is_success=False)
        except Exception as e:
            log.error(f"Unexpected error in Gemini Provider: {e}")
            return AIResponse(content="", error=f"Unexpected error: {str(e)}", is_success=False)

    async def stream_message(self, request: AIRequest) -> AsyncGenerator[AIResponse, None]:
        if not self.client:
            yield AIResponse(content="", error="Gemini client not initialized", is_success=False)
            return

        try:
            log.debug(f"Starting stream to {self.model_name}")
            contents = self._convert_messages(request.messages)
            
            config = genai_types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )
            
            if request.system_instruction:
                config.system_instruction = request.system_instruction
                
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config
            ):
                yield AIResponse(content=chunk.text)
                
        except APIError as e:
            log.error(f"Gemini API Error during stream: {e}")
            yield AIResponse(content="", error=f"API Error: {str(e)}", is_success=False)
        except Exception as e:
            log.error(f"Unexpected error in Gemini Provider stream: {e}")
            yield AIResponse(content="", error=f"Unexpected error: {str(e)}", is_success=False)

    async def validate_connection(self) -> bool:
        if not self.client:
            return False
        try:
            # A simple test request
            await self.client.aio.models.generate_content(
                model=self.model_name,
                contents="Test"
            )
            return True
        except Exception as e:
            log.error(f"Connection validation failed: {e}")
            return False

    def get_model_information(self) -> str:
        return f"Google Gemini ({self.model_name})"
