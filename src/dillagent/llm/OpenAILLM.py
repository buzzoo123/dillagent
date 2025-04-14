from .LLMConfig import LLMConfig
from .LLM import LLM
from openai import AsyncOpenAI


class OpenAILLM(LLM):
    def __init__(self, config: LLMConfig, messages=None):
        if messages is None:
            messages = []
        super().__init__(config, messages)

    async def run(self, prompt):
        if self.config.type == 'API':
            response = await self._call_api(prompt)
            return response
        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases."
            )

    async def _call_api(self, prompt):
        self.add_messages([{"role": "user", "content": prompt}])
        client = AsyncOpenAI(base_url=self.config.path, api_key=self.config.api_key)
        completion = await client.chat.completions.create(
            model=self.config.model,
            messages=self.messages
        )
        return completion.choices[0].message.content

    def add_messages(self, messages):
        self.messages.extend(messages)

    def add_sys_prompt(self, sys_prompt):
        self.messages.append({"role": "system", "content": sys_prompt})

    def clear_messages(self):
        self.messages = []
