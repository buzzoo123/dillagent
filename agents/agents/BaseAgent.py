from dependencies.prompts.Prompt import Prompt
from dependencies.prompts.StructuredPrompt import StructuredPrompt
from typing import List
from llm.LLM import LLM


class BaseAgent:
    def __init__(self, llm: LLM, tools: List, initial_prompt: Prompt = None):
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
        if initial_prompt is None:
            initial_prompt = self._generate_initial_prompt()
        elif isinstance(initial_prompt, StructuredPrompt):
            initial_prompt = self._generate_from_structured_prompt(
                initial_prompt)
        self.initial_prompt = initial_prompt.get_prompt_str()
        self.llm.add_messages([
            {"role": "system", "content": self.initial_prompt},
        ])

    def _generate_initial_prompt(self):
        """
        Generate the initial prompt for the agent.

        The prompt includes descriptions for each tool, along with instructions for interacting with the agent.

        Returns:
        str: The generated initial prompt.
        """

        prompt = """
    You are an intelligent and helpful AI Assistant.
    
    Answer the following questions and obey the following commands as best you can. 

    You have access to the following tools:

    """
        # Add descriptions for each tool
        for tool in self.tools:
            prompt += f"\n\t{tool.describe_tool()}\n"

        prompt += """
    You will receive a message from the human, then you should start a loop and do one of two things

    Option 1: You use a tool to answer the question.
    For this, you should use the following format:

    Thought: Your thought process to assist the user.
    Action: The action to take, should be one of 
    """
        prompt += "[ "
        for i in range(len(self.tools)):
            if i != len(self.tools)-1:
                prompt += f"""{self.tools[i].name}, """
            else:
                prompt += f"""{self.tools[i].name} """
        prompt += """]
    Action Input: the input to the action, to be sent to the tool

    After this, the human will respond with an observation that reflects the output from the tool, and you will continue.

    Always trust the output from the tool.

    Option 2: You respond to the human with your final response.
    For this, you should use the following format:
    Action: Response To Human
    Action Input: your response to the human, summarizing what you did and what you learned

    Begin!
    """
        return Prompt(prompt)

    def _generate_from_structured_prompt(self, structured_prompt):
        prompt = structured_prompt.header
        if not structured_prompt.tool_section:
            # Add descriptions for each tool
            prompt += f"""You have access to the following tools:\n"""
            for tool in self.tools:
                prompt += f"\n{tool.describe_tool()}\n"
        else:
            prompt += structured_prompt.tool_section
        prompt += structured_prompt.loop_condition
        if structured_prompt.footer:
            prompt += structured_prompt.footer
        return Prompt(prompt)

    def run(self, prompt):
        return self.llm.run(prompt)
