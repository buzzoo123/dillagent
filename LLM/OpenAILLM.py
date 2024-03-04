from LLM.LLMConfig import LLMConfig
from LLM.LLM import LLM
from openai import OpenAI


class OpenAILLM(LLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)

    def run(self, prompt, system_prompt):
        if self.config.type == 'API':
            response = self._call_api(prompt, system_prompt)
            return response

        else:
            raise ValueError(
                "OpenAILLM only works with type: 'API'. Consider using CustomLLM class for other use cases.")

    def _call_api(self, prompt, system_prompt):
        client = OpenAI(base_url=self.config.path, api_key="not-needed")
        completion = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "Thought: Hmm, I'm not sure who the president will be in 2024. Let me search for that information.\nAction: Search\nAction Input: \"president of the U.S. in 2024\"\n\nPlease provide the input to the action."},
            ]
        )
        return completion
