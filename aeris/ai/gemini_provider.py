from typing import AsyncGenerator
from google import genai
from google.genai import types as genai_types
from google.genai.errors import APIError
from aeris.ai.provider import AIProvider
from aeris.ai.types import AIRequest, AIResponse
from aeris.config.settings import settings
from aeris.app_logger.logger import log


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

    def _build_function_declaration(self, tool) -> genai_types.FunctionDeclaration:
        # Wrap parameters if needed (it assumes tool.parameters is a dict of properties)
        # We need a valid OpenAPI schema. Usually, it's an object with properties.
        parameters = {
            "type": "OBJECT",
            "properties": tool.parameters,
        }
        # Assuming all parameters are required for simplicity, or can be refined later.
        required = list(tool.parameters.keys()) if tool.parameters else []
        if required:
            parameters["required"] = required

        return genai_types.FunctionDeclaration(
            name=tool.name, description=tool.description, parameters=parameters
        )

    def _convert_messages(self, messages) -> list:
        # Convert our core Messages to Gemini format using genai_types.Content and Part
        formatted = []
        for msg in messages:
            if msg.role == "system":
                continue

            role = "model" if msg.role == "assistant" else "user"
            parts = []

            if msg.content:
                parts.append(genai_types.Part.from_text(text=msg.content))

            if msg.image:
                parts.append(genai_types.Part.from_image(image=msg.image))

            if getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    # Depending on how we store it, assume it's a FunctionCall object or dict
                    parts.append(
                        genai_types.Part.from_function_call(name=tc.name, args=tc.args)
                    )

            if getattr(msg, "tool_responses", None):
                for tr in msg.tool_responses:
                    parts.append(
                        genai_types.Part.from_function_response(
                            name=tr.name, response=tr.response
                        )
                    )

            if parts:
                formatted.append(genai_types.Content(role=role, parts=parts))

        return formatted

    async def send_message(self, request: AIRequest) -> AIResponse:
        if not self.client:
            return AIResponse(
                content="", error="Gemini client not initialized", is_success=False
            )

        try:
            log.debug(f"Sending request to {self.model_name}")
            contents = self._convert_messages(request.messages)

            config_kwargs = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
            }
            if request.system_instruction:
                config_kwargs["system_instruction"] = request.system_instruction

            if getattr(request, "tools", None):
                function_declarations = [
                    self._build_function_declaration(t) for t in request.tools
                ]
                if function_declarations:
                    config_kwargs["tools"] = [
                        genai_types.Tool(function_declarations=function_declarations)
                    ]

            config = genai_types.GenerateContentConfig(**config_kwargs)

            # google-genai supports async calls via client.aio
            response = await self.client.aio.models.generate_content(
                model=self.model_name, contents=contents, config=config
            )

            log.debug("Received response from Gemini")

            # Extract tool calls if any
            tool_calls = []
            content_text = ""
            if (
                response.candidates
                and response.candidates[0].content
                and response.candidates[0].content.parts
            ):
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        tool_calls.append(part.function_call)
                    elif part.text:
                        content_text += part.text

            return AIResponse(content=content_text, tool_calls=tool_calls)

        except APIError as e:
            log.error(f"Gemini API Error: {e}")
            return AIResponse(
                content="", error=f"API Error: {str(e)}", is_success=False
            )
        except Exception as e:
            log.error(f"Unexpected error in Gemini Provider: {e}")
            return AIResponse(
                content="", error=f"Unexpected error: {str(e)}", is_success=False
            )

    async def stream_message(
        self, request: AIRequest
    ) -> AsyncGenerator[AIResponse, None]:
        if not self.client:
            yield AIResponse(
                content="", error="Gemini client not initialized", is_success=False
            )
            return

        try:
            log.debug(f"Starting stream to {self.model_name}")
            contents = self._convert_messages(request.messages)

            config_kwargs = {
                "temperature": request.temperature,
                "max_output_tokens": request.max_tokens,
            }
            if request.system_instruction:
                config_kwargs["system_instruction"] = request.system_instruction

            if getattr(request, "tools", None):
                function_declarations = [
                    self._build_function_declaration(t) for t in request.tools
                ]
                if function_declarations:
                    config_kwargs["tools"] = [
                        genai_types.Tool(function_declarations=function_declarations)
                    ]

            config = genai_types.GenerateContentConfig(**config_kwargs)

            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model_name, contents=contents, config=config
            ):
                # Note: Streaming with tool calls is more complex to parse chunk-by-chunk.
                # Assuming simple text streaming for now.
                yield AIResponse(content=chunk.text or "")

        except APIError as e:
            log.error(f"Gemini API Error during stream: {e}")
            yield AIResponse(content="", error=f"API Error: {str(e)}", is_success=False)
        except Exception as e:
            log.error(f"Unexpected error in Gemini Provider stream: {e}")
            yield AIResponse(
                content="", error=f"Unexpected error: {str(e)}", is_success=False
            )

    async def validate_connection(self) -> bool:
        if not self.client:
            return False
        try:
            # A simple test request
            await self.client.aio.models.generate_content(
                model=self.model_name, contents="Test"
            )
            return True
        except Exception as e:
            log.error(f"Connection validation failed: {e}")
            return False

    def get_model_information(self) -> str:
        return f"Google Gemini ({self.model_name})"
