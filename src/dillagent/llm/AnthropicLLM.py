from .LLMConfig import LLMConfig
from .LLM import LLM
import anthropic


class AnthropicLLM(LLM):
    def __init__(self, config: LLMConfig, messages=None):
        super().__init__(config, messages)
        self.sys_prompt = None

    async def run(self, prompt):
        if self.config.type == 'API':
            response = self._call_api(prompt)
            return response

        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases.")

    def _call_api(self, prompt):
        self.add_messages([{"role": "user", "content": prompt}])
        client = anthropic.Anthropic(
            api_key=self.config.api_key,
        )
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=self.messages,
            temperature=0,
            system=self.sys_prompt
        )
        return message

    def add_messages(self, messages):
        self.messages.extend(messages)

    def add_sys_prompt(self, sys_prompt):
        self.sys_prompt = sys_prompt
