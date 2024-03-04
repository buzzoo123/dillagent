from LLM.LLMConfig import LLMConfig
from LLM.LLM import LLM
from openai import OpenAI


class OpenAILLM(LLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)

    def run(self, prompt, system_prompt, messages=None):
        if self.config.type == 'API':
            response = self._call_api(prompt, system_prompt, messages=messages)
            return response

        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases.")

    def _call_api(self, prompt, system_prompt, messages=None):
        if messages == None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        client = OpenAI(base_url=self.config.path, api_key=self.config.api_key)
        completion = client.chat.completions.create(
            model=self.config.model,
            messages=messages
        )
        return completion
