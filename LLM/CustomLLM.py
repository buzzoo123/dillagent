from LLM.LLMConfig import LLMConfig
from LLM.LLM import LLM
from openai import OpenAI


class CustomLLM(LLM):
    def __init__(self, config: LLMConfig, api_call: function):
        super.__init__(config)
        self.api_call = api_call

    def run(self, prompt, system_prompt):
        if self.config.type == 'API':
            response = self._call_api(prompt, system_prompt)
            return response

        else:
            raise NotImplementedError(
                "Still working on this feature... Sorry!")

    def _call_api(self, prompt, system_prompt):
        return self.api_call(prompt, system_prompt)
