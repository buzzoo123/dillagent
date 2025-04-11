from ...tools import Tool
from .BaseAgent import BaseAgent
from ...dependencies.prompts.SysPrompt import SysPrompt
from typing import List
from ...llm.LLM import LLM


class StarterAgent(BaseAgent):
    def __init__(self, llm: LLM, tools: List, sys_prompt: SysPrompt, name: str = "Starter Agent"):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        super().__init__()

    def run(self, prompt):
        return self.llm.run(prompt)
