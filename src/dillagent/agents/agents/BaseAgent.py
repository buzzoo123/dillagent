from ...dependencies.prompts.BaseSysPrompt import BaseSysPrompt
from ...dependencies.parsers.intermediate.BaseIntermediateParser import BaseIntermediateParser
from typing import List, Optional
from ...llm.LLM import LLM
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, llm: LLM, tools: List, intermediate_parser: BaseIntermediateParser, sys_prompt: BaseSysPrompt = None, name: str = "Generic Agent"):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        self.llm = llm
        self.tools = tools
        self.sys_prompt = sys_prompt
        self.sys_prompt.generate_prompt(tools)
        self.llm.add_sys_prompt(self.sys_prompt.prompt_str)
        self.name = name
        self.intermediate_parser = intermediate_parser

    @abstractmethod
    async def run(self, *, prompt: Optional[str] = None, inputs: Optional[dict] = None) -> dict:
        """
        Runs the agent using the underlying LLM. You may call this:

            return values parsed via an intermediate parser as a dict for best use in ecosystem 
        """
        pass
