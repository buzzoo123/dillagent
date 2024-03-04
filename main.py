from agents.BaseAgent import BaseAgent
from tools.Tool import tool
from models.DescribedModel import DescribedModel, Field
from Dependencies.Prompts.StructuredPrompt import StructuredPrompt
from LLM.OpenAILLM import OpenAILLM
from LLM.LLMConfig import LLMConfig


class SearchSchema(DescribedModel):
    query: str = Field(...,
                       description="Query to be searched in the form of a string.")


@tool(name="Search", description="Useful for searching for information", schema=SearchSchema)
def search(query: str):
    return "The president is Joe Biden."


header = """You are an intelligent and helpful AI Assistant.

Answer the following questions and obey the following commands as best you can."""

loop_conditions = """You will receive a message from the human, then you must do one of two things

Option 1: You use a tool to answer the question.
For this, you must use the following format:

Thought: Your thought process to assist the user.
Action: The action to take, should be one of [ Search ]
Action Input: the input to the action, to be sent to the tool
 
After this, the human will respond with an observation, and you will continue. 
 
Option 2: You respond to the human.
For this, you must use the following format:

Action: 'Response To Human'
Action Input: the response to the human's initial question, summarizing what you did and what you learned.

Begin"""

initial_prompt = StructuredPrompt(header, loop_conditions)

llm = OpenAILLM(LLMConfig(
    model="gpt-3.5-turbo", api_key="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", path="https://api.openai.com/v1/"),)

agent = BaseAgent(llm, [search], initial_prompt)

agent.run_loop("Who is the president in 2025?")
