import random
from agents.agents.BaseAgent import BaseAgent
from tools.Tool import tool
from models.DescribedModel import DescribedModel, Field
from Dependencies.Prompts.StructuredPrompt import StructuredPrompt
from LLM.OpenAILLM import OpenAILLM
from LLM.LLMConfig import LLMConfig
from agents.Executors.AgentExecutor import AgentExecutor
import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from dotenv import load_dotenv
import os


load_dotenv()


class SearchSchema(DescribedModel):
    query: str = Field(...,
                       description="Query to be searched in the form of a string.")


class QuoteModel(DescribedModel):
    topic: str = Field(...,
                       description="Topic of motivational quote in the form of a string")


class VibeSchema(DescribedModel):
    vibe: str = Field(...,
                      description="The vibe of the music being made in the form of a String")


@tool(name="Search", description="Useful for searching for information", schema=SearchSchema)
def search(query: str):
    res = ""
    search_results = list(google_search(query, num_results=1))
    if search_results:
        # Fetch the content of the first search result page
        page_url = search_results[0]
        response = requests.get(page_url)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from the HTML content
            for data in soup.find_all("p"):
                res += "\n" + data.get_text()
            # Return the plain text
            return res
        else:
            return "Failed to retrieve page content"
    else:
        return "No search results found"


@tool(name="Quote Generator", description="Useful for generating motivational quotes", schema=QuoteModel)
def generate_quote(topic: str):
    arr = [
        "You will one day be Eric",
        "You will one day be Kieran",
        "I eat hairy assholes",
    ]
    random_element = random.choice(arr)
    return random_element


@tool(name="Make Music", description="Useful for making music", schema=VibeSchema)
def make_music(vibe: str):
    with open('example.txt', 'w') as file:
        file.write(vibe)
    return "music file generated called example.txt"


# initial_prompt = StructuredPrompt(header, loop_conditions)
# llm = OpenAILLM(LLMConfig(
#     model="gpt-3.5-turbo-0125", api_key=os.environ.get('API_KEY'), path="https://api.openai.com/v1/"),)

agent = BaseAgent(llm, [search, make_music, generate_quote])

print(agent.initial_prompt)

runner = AgentExecutor(agent)

while (True):
    print(runner.run(input("What can I help you with?\n")))


# header = """You are an intelligent and helpful AI Assistant.

# # Answer the following questions and obey the following commands as best you can."""

# loop_conditions = """You will receive a message from the human, then you must do one of two things

# Option 1: You use a tool to answer the question.
# For this, you must use the following format:

# Thought: Your thought process to assist the user.
# Action: The action to take, should be one of [ Search ]
# Action Input: the input to the action, to be sent to the tool

# After this, the human will respond with an observation, and you will continue.

# Option 2: You respond to the human.
# For this, you must use the following format:

# Action: 'Response To Human'
# Action Input: the response to the human's initial question, summarizing what you did and what you learned.

# Begin"""
