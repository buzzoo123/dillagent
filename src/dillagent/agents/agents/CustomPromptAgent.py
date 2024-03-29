from .BaseAgent import BaseAgent
from ...dependencies.prompts.Prompt import Prompt


class CustomPromptAgent(BaseAgent):
    def __init__(llm, tools, customPrompt: Prompt):
        super().__init__(llm, tools, initial_prompt=customPrompt)
