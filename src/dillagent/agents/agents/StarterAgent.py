from ...tools import Tool
from .BaseAgent import BaseAgent
from ...dependencies.prompts.BaseSysPrompt import BaseSysPrompt
from typing import List, Optional
from ...llm.LLM import LLM

class StarterAgent(BaseAgent):
    def __init__(self, llm: LLM, tools: List, sys_prompt: BaseSysPrompt, name: str = "Starter Agent"):
        """
        Initialize the BaseAgent with a list of tools and an optional initial prompt.

        Parameters:
        - tools: A list of Tool instances representing the available tools for the agent.
        - initial_prompt: An optional initial prompt for the agent. If not provided, a prompt will be generated.

        Returns:
        None
        """
        super().__init__(llm, tools, sys_prompt, name)

    async def run(self, *, prompt: Optional[str] = None, inputs: Optional[dict] = None):
        """
        Runs the agent with either a direct prompt or structured inputs.
        
        Parameters:
        - prompt: An optional string prompt to pass directly to the LLM
        - inputs: An optional dictionary of structured inputs
        
        Returns:
        The response from the LLM
        """
        # If inputs are provided, construct a prompt from them
        if inputs:
            # Convert inputs to a formatted string that the agent can understand
            formatted_prompt = f"Input: {inputs.get('input', '')}"
            return self.llm.run(formatted_prompt)
        
        # Otherwise, use the direct prompt
        elif prompt:
            return self.llm.run(prompt)
        
        # Handle the case where neither is provided
        else:
            raise ValueError("Either prompt or inputs must be provided")
