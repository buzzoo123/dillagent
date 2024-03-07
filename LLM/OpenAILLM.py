from LLM.LLMConfig import LLMConfig
from LLM.LLM import LLM
from openai import OpenAI


class OpenAILLM(LLM):
    def __init__(self, config: LLMConfig, messages=[]):
        super().__init__(config, messages)

    def run(self, prompt):
        if self.config.type == 'API':
            response = self._call_api(prompt)
            return response

        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases.")

    def _call_api(self, prompt):
        self.add_messages([{"role": "user", "content": prompt}])
        client = OpenAI(base_url=self.config.path, api_key=self.config.api_key)
        completion = client.chat.completions.create(
            model=self.config.model,
            messages=self.messages
        )
        return completion

    def add_messages(self, messages):
        self.messages.extend(messages)
