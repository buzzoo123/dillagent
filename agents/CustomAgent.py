from BaseAgent import BaseAgent
from Dependencies.Prompts.Prompt import Prompt


class CustomPromptAgent(BaseAgent):
    def __init__(llm, tools, customPrompt):
        super().__init__(llm, tools, initial_prompt=customPrompt)