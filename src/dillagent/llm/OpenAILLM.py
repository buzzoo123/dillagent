import json
from .LLMConfig import LLMConfig
from .LLM import LLM
from openai import AsyncOpenAI
from .StandardizedLLMResponse import StandardizedLLMResponse
from typing import Dict, List, Optional
from ..tools.Tool import Tool


class OpenAILLM(LLM):
    def __init__(self, config: LLMConfig, messages: Optional[List[Dict[str, str]]] = None, tools: Optional[List[Tool]] = None):
        if messages is None:
            messages = []
        self._tools = tools if tools is not None else []
        super().__init__(config, messages)


    async def run(self, prompt: str) -> str:
        if self.config.type == 'API':
            response = await self._call_api(prompt)
            return response
        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases."
            )

    async def _call_api(self, prompt: str) -> str:
        self.add_messages([{"role": "user", "content": prompt}])
        client = AsyncOpenAI(base_url=self.config.path, api_key=self.config.api_key)

        openai_tools_config = []
        if self._tools:
            for tool in self._tools:
                openai_tools_config.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.schema()
                    }
                })

        completion = await client.chat.completions.create(
            model=self.config.model,
            messages=self.messages,
            tools=openai_tools_config if openai_tools_config else None,
            tool_choice="auto"
        )

        formatted_completion = self.format_completion(completion)
        return formatted_completion

    def add_messages(self, messages: List[Dict[str, str]]) -> None:
        self.messages.extend(messages)

    def add_sys_prompt(self, sys_prompt: str) -> None:
        self.messages.append({"role": "system", "content": sys_prompt})

    def clear_messages(self) -> None:
        self.messages = []

    def format_completion(self, completion) -> str:
        message = completion.choices[0].message
        if message.tool_calls:
            serialized_calls = []
            for call in message.tool_calls:
                serialized_calls.append(
                    StandardizedLLMResponse(
                        type="function",
                        name=call.function.name,
                        arguments=call.function.arguments
                    )
                )
            return serialized_calls
        elif message.content:
            return StandardizedLLMResponse(
                type="natural language",
                content=message.content
            )
        else:
            return StandardizedLLMResponse(
                type="unknown",
                content=""
            )